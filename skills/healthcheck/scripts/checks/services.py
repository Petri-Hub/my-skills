"""Background services: ai-memory and Wakapi."""

from __future__ import annotations

import json
import re
from datetime import date, datetime, timedelta, timezone
from urllib.parse import quote

from lib import config as cfgmod
from lib.http import fetch, run as run_command
from lib.model import FAIL, OK, SKIP, WARN, Action, Finding
from lib.versions import latest_github, semver

AREA = "services"


def _age(seconds: float) -> str:
    seconds = max(0, seconds)
    if seconds < 120:
        return f"{int(seconds)}s ago"
    if seconds < 7200:
        return f"{int(seconds / 60)}m ago"
    if seconds < 172800:
        return f"{seconds / 3600:.1f}h ago"
    return f"{seconds / 86400:.1f}d ago"


def _duration(seconds: int) -> str:
    hours, rest = divmod(int(seconds), 3600)
    minutes = rest // 60
    if hours:
        return f"{hours}h{minutes:02d}m"
    return f"{minutes}m"


def _ai_memory(cfg, opts) -> list[Finding]:
    base = cfg.get("services", "ai_memory", "url", default="")
    if not base:
        return [
            Finding(
                AREA,
                "ai-memory",
                SKIP,
                "not configured",
                Action(
                    "manual",
                    "create ~/.config/healthcheck/config.toml from "
                    "assets/config.example.toml and set `[services.ai_memory] url`.",
                )
                if not cfg.exists
                else None,
            )
        ]

    base = base.rstrip("/")
    timeout = cfg.get("general", "timeout", default=8)
    web = fetch(f"{base}/web/login", timeout=timeout)
    mcp = fetch(f"{base}/mcp", timeout=timeout)

    cli_path = cfgmod.as_path(
        cfg.get(
            "services", "ai_memory", "cli", default="~/.local/bin/ai-memory"
        )
    )
    cli_version = None
    if cli_path.is_file():
        ok, output = run_command([str(cli_path), "--version"], timeout=10)
        if ok:
            match = re.search(r"(\d+\.\d+\.\d+)", output)
            cli_version = match.group(1) if match else None

    latest = latest_github("akitaonrails/ai-memory")

    web_ok = web.ok and web.status == 200
    # 401 is healthy here: the MCP endpoint is up and enforcing its token.
    mcp_ok = mcp.ok and mcp.status in (200, 401)

    detail = f"web {web.status or 'down'} · MCP {mcp.status or 'down'}"
    if cli_version and latest:
        detail += f" · CLI {cli_version} -> {latest}"
    elif cli_version:
        detail += f" · CLI {cli_version}"
    elif latest:
        detail += " · CLI missing"

    status = OK
    action = None

    if not web_ok:
        status = FAIL
        detail = f"web {web.status or 'down'} · {web.error or 'unreachable'}"
        action = Action(
            "investigate",
            "ai-memory web is down: check the container on the lab with "
            "`ssh lab docker ps | grep ai-memory` and its logs before restarting.",
        )
    elif not mcp_ok:
        status = WARN
        action = Action(
            "investigate",
            f"ai-memory web answers but the MCP endpoint returned "
            f"{mcp.status or 'nothing'}: check the server logs and the token.",
        )
    elif cli_version and latest and semver(latest) > semver(cli_version):
        status = WARN
        action = Action(
            "investigate",
            f"ai-memory CLI {cli_version} is behind the server's release line "
            f"{latest}: upgrade the local binary and rerun its setup check.",
        )
    elif not cli_version:
        status = WARN
        action = Action(
            "investigate",
            "the ai-memory CLI is missing at the configured path; the agent hooks "
            "call it, so capture may be silently failing.",
        )

    findings = [Finding(AREA, "ai-memory", status, detail, action)]
    return findings


def _wakatime_key(path) -> str | None:
    if not path.is_file():
        return None
    for line in path.read_text().splitlines():
        stripped = line.strip()
        if stripped.startswith("api_key"):
            _, _, value = stripped.partition("=")
            value = value.strip()
            if value:
                return value
    return None


def _wakapi(cfg, opts) -> list[Finding]:
    api = cfg.get("services", "wakapi", "api_url", default="")
    if not api:
        return [
            Finding(
                AREA,
                "Wakapi",
                SKIP,
                "not configured",
                Action(
                    "manual",
                    "create ~/.config/healthcheck/config.toml from "
                    "assets/config.example.toml and set `[services.wakapi] api_url`.",
                )
                if not cfg.exists
                else None,
            )
        ]

    api = api.rstrip("/")
    timeout = cfg.get("general", "timeout", default=8)
    max_age = cfg.get(
        "services", "wakapi", "max_heartbeat_age_min", default=180
    )
    key_path = cfgmod.as_path(
        cfg.get(
            "services",
            "wakapi",
            "api_key_file",
            default="~/.wakatime.cfg",
        )
    )
    key = _wakatime_key(key_path)
    if not key:
        return [
            Finding(
                AREA,
                "Wakapi",
                SKIP,
                "no API key found",
                Action(
                    "manual",
                    f"add `api_key` to {key_path} so the healthcheck can confirm "
                    "heartbeats are arriving.",
                ),
            )
        ]

    # Wakapi rejects Basic auth for this endpoint but accepts ?api_key=.
    # The compat endpoint's date filter is shifted by one day in practice, so
    # ask for today and tomorrow and keep the newest heartbeat from either.
    today = date.today()
    query = f"api_key={quote(key, safe='')}"
    statusbar = fetch(
        f"{api}/users/current/statusbar/today?{query}", timeout=timeout
    )

    if not statusbar.ok or statusbar.status != 200:
        return [
            Finding(
                AREA,
                "Wakapi",
                FAIL,
                f"API {statusbar.status or 'down'} · {statusbar.error or 'unreachable'}",
                Action(
                    "investigate",
                    "Wakapi API is not answering: check the container on the lab and "
                    "the public hostname. A 401 means the key was rejected, not that "
                    "the service is down.",
                ),
            )
        ]

    try:
        payload = json.loads(statusbar.body)
        categories = payload.get("data", {}).get("categories", [])
        total_seconds = sum(item.get("total_seconds", 0) for item in categories)
    except (ValueError, AttributeError):
        return [
            Finding(
                AREA,
                "Wakapi",
                WARN,
                "API 200 but the body did not parse",
                Action("investigate", "open the Wakapi API URL and inspect the body."),
            )
        ]

    heartbeats = None
    entries = []
    for offset in (0, 1):
        day = (today + timedelta(days=offset)).isoformat()
        response = fetch(
            f"{api}/compat/wakatime/v1/users/current/heartbeats"
            f"?date={day}&{query}",
            timeout=timeout,
        )
        if response.ok and response.status == 200:
            heartbeats = response
            try:
                entries.extend(json.loads(response.body).get("data", []))
            except ValueError:
                pass

    detail = f"API 200 · today {_duration(total_seconds)}"
    status = OK
    action = None

    if heartbeats is None:
        status = WARN
        detail += " · heartbeats unavailable"
        action = Action(
            "investigate",
            "Wakapi answers, but the heartbeat history did not load; check the "
            "compat API path and the user key.",
        )
    elif entries:
        latest = max(int(item.get("time", 0)) for item in entries)
        seconds = datetime.now(timezone.utc).timestamp() - latest
        detail += f" · last heartbeat {_age(seconds)}"
        if seconds > max_age * 60:
            status = WARN
            action = Action(
                "investigate",
                f"last heartbeat was {_age(seconds)}: check the WakaTime plugin in "
                "the editor you are using and `~/.wakatime/wakatime.log`.",
            )
    else:
        detail += " · no heartbeats in the last 2 days"

    return [Finding(AREA, "Wakapi", status, detail, action)]


def run(cfg, opts) -> list[Finding]:
    findings: list[Finding] = []
    findings.extend(_ai_memory(cfg, opts))
    findings.extend(_wakapi(cfg, opts))
    return findings
