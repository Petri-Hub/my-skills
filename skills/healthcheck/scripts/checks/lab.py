"""Lab health from the public Gatus API, with optional SSH depth."""

from __future__ import annotations

import json
import re
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from urllib.parse import quote

from lib import config as cfgmod
from lib.http import fetch, run as run_command
from lib.model import FAIL, INFO, OK, SKIP, WARN, Action, Finding

AREA = "lab"


def _when(timestamp: str | None) -> str:
    if not timestamp:
        return ""
    try:
        moment = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    except ValueError:
        return ""
    return moment.astimezone().strftime("%H:%M")


def _uptime(base: str, key: str, timeout: float) -> float | None:
    response = fetch(
        f"{base}/api/v1/endpoints/{quote(key, safe='')}/uptimes/24h",
        timeout=timeout,
    )
    if response.ok and response.status == 200:
        try:
            return float(response.body.strip())
        except ValueError:
            return None
    return None


def _age(seconds: float) -> str:
    seconds = max(0, seconds)
    if seconds < 120:
        return f"{int(seconds)}s ago"
    if seconds < 7200:
        return f"{int(seconds / 60)}m ago"
    if seconds < 172800:
        return f"{seconds / 3600:.1f}h ago"
    return f"{seconds / 86400:.1f}d ago"


def _seconds_since(stamp: str) -> float | None:
    try:
        moment = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
    except ValueError:
        return None
    return (datetime.now(timezone.utc) - moment).total_seconds()


def _gatus(cfg, opts, findings: list[Finding]) -> None:
    base = cfg.get("lab", "gatus_url", default="")
    if not base:
        findings.append(
            Finding(
                AREA,
                "Gatus",
                SKIP,
                "not configured",
                Action(
                    "manual",
                    "create ~/.config/healthcheck/config.toml from "
                    "assets/config.example.toml and set `[lab] gatus_url` to enable "
                    "lab checks.",
                )
                if not cfg.exists
                else None,
            )
        )
        return

    base = base.rstrip("/")
    timeout = cfg.get("general", "timeout", default=8)
    response = fetch(f"{base}/api/v1/endpoints/statuses", timeout=timeout)
    if not response.ok or response.status != 200:
        findings.append(
            Finding(
                AREA,
                "Gatus",
                SKIP,
                f"unreachable: {response.error or response.status}",
                Action(
                    "investigate",
                    f"check the public status page at {base} and the Cloudflare tunnel "
                    "before trusting any lab result.",
                ),
            )
        )
        return

    try:
        endpoints = json.loads(response.body)
    except ValueError:
        findings.append(Finding(AREA, "Gatus", SKIP, "invalid JSON from status API"))
        return

    with ThreadPoolExecutor(max_workers=6) as pool:
        uptimes = {
            endpoint.get("key", endpoint.get("name", "")): pool.submit(
                _uptime, base, endpoint.get("key", endpoint.get("name", "")), timeout
            )
            for endpoint in endpoints
        }
        uptime_values = {
            key: future.result() for key, future in uptimes.items()
        }

    for endpoint in endpoints:
        name = endpoint.get("name", "unnamed")
        key = endpoint.get("key", name)
        results = endpoint.get("results") or []
        uptime = uptime_values.get(key)

        if not results:
            findings.append(Finding(AREA, name, SKIP, "no results yet"))
            continue

        last = results[-1]
        failures = [result for result in results if not result.get("success")]
        last_ok = next(
            (
                _when(result.get("timestamp"))
                for result in reversed(results)
                if result.get("success")
            ),
            "",
        )

        if not last.get("success"):
            status = FAIL
            detail = "down" + (f" · last ok {last_ok}" if last_ok else "")
            action = Action(
                "investigate",
                f"open a fix session for {name}: check the container on the lab with "
                f"`ssh {cfg.get('lab', 'ssh_host', default='lab')} docker ps -a` and its "
                f"logs, then confirm with the Gatus key `{key}`.",
            )
        elif failures or (uptime is not None and uptime < 0.99):
            status = WARN
            detail = f"{len(failures)} fail(s) in last {len(results)} checks"
            if uptime is not None:
                detail += f" · {uptime:.1%} 24h"
            action = Action(
                "investigate",
                f"look for flapping on {name}: compare its container restarts and logs "
                "over the last hour before changing anything.",
            )
        else:
            status = OK
            detail = "up"
            if uptime is not None:
                detail += f" · {uptime:.1%} 24h"
            action = None

        findings.append(Finding(AREA, name, status, detail, action))

    if opts.verbose:
        _coverage(cfg, endpoints, findings)


def _coverage(cfg, endpoints: list[dict], findings: list[Finding]) -> None:
    repo = cfg.get("general", "lab_repo", default="")
    if not repo:
        return
    root = cfgmod.as_path(repo)
    if not root.is_dir():
        return

    folders = []
    for relative in ("services/infra", "services/apps", "sandboxes"):
        folder = root / relative
        if folder.is_dir():
            folders.extend(
                path
                for path in folder.iterdir()
                if path.is_dir() and path.name != "gatus"
            )
    if not folders:
        return

    watched = " ".join(
        (endpoint.get("name", "") + " " + endpoint.get("group", ""))
        .lower()
        .replace("-", "")
        .replace("_", "")
        .replace(" ", "")
        for endpoint in endpoints
    )

    aliases = {
        "observability": ["prometheus", "nodeexporter", "cadvisor"],
        "lemon-sandbox": ["lemonsandbox"],
    }

    missing = []
    for folder in folders:
        names = [folder.name.lower().replace("-", "").replace("_", "")]
        names.extend(aliases.get(folder.name, []))
        if not any(name in watched for name in names):
            missing.append(folder.name)

    if missing:
        findings.append(
            Finding(
                AREA,
                "Coverage",
                INFO,
                f"{len(missing)} services not monitored by Gatus",
                Action(
                    "investigate",
                    "add Gatus endpoints for: " + ", ".join(missing)
                    + ". They are running but invisible to the status page.",
                ),
            )
        )


def _deep(cfg, findings: list[Finding]) -> None:
    host = cfg.get("lab", "ssh_host", default="lab")
    command = (
        "docker ps -a --format '{{.Names}}|{{.Status}}'; "
        "echo '---POLICY---'; "
        "docker inspect --format "
        "'{{.Name}}|{{.State.ExitCode}}|{{.State.FinishedAt}}' "
        "$(docker ps -aq); "
        "echo '---DISK---'; df -P / | tail -1; "
        "echo '---REBOOT---'; [ -f /var/run/reboot-required ] && echo yes || echo no; "
        "echo '---JOBS---'; docker logs --since 2h -t ofelia 2>&1 "
        "| grep -E 'Started -|Finished in' | tail -400"
    )
    ok, output = run_command(
        [
            "ssh",
            "-o",
            "BatchMode=yes",
            "-o",
            "ConnectTimeout=4",
            "-o",
            "StrictHostKeyChecking=accept-new",
            host,
            command,
        ],
        timeout=20,
    )
    if not ok:
        first = output.splitlines()[0] if output else "no output"
        findings.append(
            Finding(
                AREA,
                "SSH depth",
                SKIP,
                f"ssh {host} failed: {first[:60]}",
                Action(
                    "investigate",
                    f"check Tailscale and the SSH key for `{host}`; the public checks still ran.",
                ),
            )
        )
        return

    before_policy, _, rest = output.partition("---POLICY---")
    policy_block, _, rest = rest.partition("---DISK---")
    disk_block, _, rest = rest.partition("---REBOOT---")
    reboot_block, _, jobs_block = rest.partition("---JOBS---")

    containers = []
    for line in before_policy.splitlines():
        if "|" in line:
            name, status = line.split("|", 1)
            containers.append((name.strip(), status.strip()))

    policies: dict[str, tuple[str, str]] = {}
    for line in policy_block.splitlines():
        fields = line.strip().split("|")
        if len(fields) >= 3:
            policies[fields[0].lstrip("/")] = (fields[1], fields[2])

    # A game server stopped by hand months ago is parked, not broken. Only a
    # non-zero exit inside the last week, or an unhealthy running container,
    # deserves attention.
    parked = []
    attention = []
    for name, status in containers:
        exit_code, finished = policies.get(name, ("0", ""))
        if status.startswith("Up") and "unhealthy" not in status:
            continue
        if status.startswith("Up"):
            attention.append((name, status))
            continue
        if status.startswith("Exited"):
            age = _seconds_since(finished) if finished else None
            try:
                code = int(exit_code)
            except ValueError:
                code = 0
            if (age is not None and age > 7 * 86400) or code == 0:
                parked.append(name)
            else:
                attention.append((name, status))
            continue
        attention.append((name, status))

    running = len(containers) - len(parked) - len(attention)
    detail = (
        f"{running}/{len(containers)} running" if containers else "no containers reported"
    )
    if parked:
        detail += f" · {len(parked)} parked"
    if attention:
        detail += f" · {len(attention)} alert"

    names = ", ".join(name for name, _ in attention[:4])
    if len(attention) > 4:
        names += f" and {len(attention) - 4} more"

    findings.append(
        Finding(
            AREA,
            "Lab containers",
            WARN if attention else OK,
            detail,
            Action(
                "investigate",
                f"inspect the containers that need attention ({names}): "
                f"`ssh {host} docker logs --tail 50 <name>`, then check their exit code "
                "and restart policy.",
            )
            if attention
            else None,
        )
    )

    disk_line = disk_block.strip().splitlines()[0] if disk_block.strip() else ""
    fields = disk_line.split()
    if len(fields) >= 5:
        capacity = fields[4].rstrip("%")
        try:
            percent = int(capacity)
        except ValueError:
            percent = 0
        try:
            used_gb = int(fields[2]) / 1024 / 1024
            total_gb = int(fields[1]) / 1024 / 1024
            disk_detail = f"{percent}% used · {used_gb:.0f} GB of {total_gb:.0f} GB"
        except ValueError:
            disk_detail = f"{percent}% used"
        findings.append(
            Finding(
                AREA,
                "Lab disk",
                WARN if percent >= 80 else OK,
                disk_detail,
                Action(
                    "investigate",
                    "find the large volumes on the lab before deleting anything: "
                    f"`ssh {host} du -xh --max-depth=2 / | sort -h | tail`.",
                )
                if percent >= 80
                else None,
            )
        )

    needs_reboot = "yes" in reboot_block.strip().lower()
    findings.append(
        Finding(
            AREA,
            "Lab reboot",
            WARN if needs_reboot else OK,
            "required" if needs_reboot else "not required",
            Action(
                "manual",
                "plan a lab reboot: containers restart with the host, so do it when no game server is in use.",
            )
            if needs_reboot
            else None,
        )
    )

    last_start: dict[str, str] = {}
    failed_jobs: list[str] = []
    for line in jobs_block.splitlines():
        match = re.search(r'\[Job "([^"]+)"', line)
        if not match:
            continue
        name = match.group(1)
        stamp = line.split()[0] if line.split() else ""
        if "Started -" in line and stamp:
            last_start[name] = stamp
        if "failed: true" in line:
            failed_jobs.append(name)

    if not jobs_block.strip():
        findings.append(Finding(AREA, "Lab jobs", SKIP, "no ofelia log in 2h"))
    elif failed_jobs:
        unique = sorted(set(failed_jobs))
        findings.append(
            Finding(
                AREA,
                "Lab jobs",
                WARN,
                f"{len(failed_jobs)} failed in 2h: " + ", ".join(unique[:3]),
                Action(
                    "investigate",
                    f"inspect the failed jobs ({', '.join(unique[:4])}): "
                    f"`ssh {host} docker logs --since 2h ofelia | grep 'failed: true'`.",
                ),
            )
        )
    else:
        findings.append(Finding(AREA, "Lab jobs", OK, "all runs ok in 2h"))

    backups = {
        name: stamp for name, stamp in last_start.items() if name.startswith("backup-")
    }
    if backups:
        newest = max(backups.values())
        age = _seconds_since(newest)
        if age is not None:
            findings.append(
                Finding(
                    AREA,
                    "Backups",
                    WARN if age > 3600 else OK,
                    f"last run {_age(age)}",
                    Action(
                        "investigate",
                        "backups have not run for over an hour: check the restic "
                        f"containers and ofelia on the lab (`ssh {host} docker ps | grep restic`).",
                    )
                    if age > 3600
                    else None,
                )
            )
    elif jobs_block.strip():
        findings.append(
            Finding(
                AREA,
                "Backups",
                WARN,
                "no backup job in 2h",
                Action(
                    "investigate",
                    "no restic job appeared in the ofelia log: check the ofelia labels "
                    f"and the restic containers (`ssh {host} docker ps | grep restic`).",
                ),
            )
        )


def run(cfg, opts) -> list[Finding]:
    findings: list[Finding] = []
    _gatus(cfg, opts, findings)
    if opts.deep:
        _deep(cfg, findings)
    return findings
