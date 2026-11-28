"""Host health: disk, memory, load, temperature, reboot, units and updates."""

from __future__ import annotations

import os
import re
import shutil
from pathlib import Path

from lib.http import run as run_command
from lib.model import INFO, OK, WARN, Action, Finding

FAILED = "fail"


def os_pretty() -> str:
    try:
        text = Path("/etc/os-release").read_text()
    except OSError:
        return ""
    match = re.search(r'^PRETTY_NAME="?(.*?)"?$', text, re.MULTILINE)
    return match.group(1) if match else ""


def uptime_text() -> str:
    try:
        seconds = float(Path("/proc/uptime").read_text().split()[0])
    except (OSError, ValueError):
        return ""
    days, rest = divmod(int(seconds), 86400)
    hours, rest = divmod(rest, 3600)
    minutes = rest // 60
    if days:
        return f"up {days}d {hours}h"
    if hours:
        return f"up {hours}h {minutes}m"
    return f"up {minutes}m"


def _memory() -> tuple[int, int]:
    info: dict[str, int] = {}
    try:
        for line in Path("/proc/meminfo").read_text().splitlines():
            key, _, value = line.partition(":")
            info[key] = int(value.split()[0])
    except (OSError, ValueError, IndexError):
        return 0, 0
    return info.get("MemTotal", 0), info.get("MemAvailable", 0)


def _temperature() -> float | None:
    candidates = sorted(Path("/sys/class/thermal").glob("thermal_zone*/temp"))
    for candidate in candidates:
        try:
            value = int(candidate.read_text().strip()) / 1000
        except (OSError, ValueError):
            continue
        if 0 < value < 120:
            return value
    ok, output = run_command(["sensors"], timeout=5)
    if ok:
        match = re.search(r"\+([\d.]+)°C", output)
        if match:
            return float(match.group(1))
    return None


def _failed_units() -> list[str]:
    ok, output = run_command(["systemctl", "--failed", "--no-legend"], timeout=8)
    if not ok:
        return []
    units = []
    for line in output.splitlines():
        text = line.replace("●", "").strip()
        if text:
            units.append(text.split()[0])
    return units


def _apt_updates() -> int | None:
    ok, output = run_command(["apt", "list", "--upgradable"], timeout=25)
    if not ok:
        return None
    lines = [
        line
        for line in output.splitlines()
        if line.strip() and not line.startswith("Listing") and "/" in line
    ]
    return len(lines)


def _flatpak_updates() -> int | None:
    if not shutil.which("flatpak"):
        return None
    ok, output = run_command(["flatpak", "remote-ls", "--updates"], timeout=20)
    if not ok:
        return None
    return len([line for line in output.splitlines() if line.strip()])


def _snap_updates() -> int | None:
    if not shutil.which("snap"):
        return None
    ok, output = run_command(["snap", "refresh", "--list"], timeout=20)
    if not ok:
        return None
    lines = [
        line
        for line in output.splitlines()
        if line.strip()
        and not line.startswith("Name")
        and "up to date" not in line.lower()
    ]
    return len(lines)


def header_meta() -> dict:
    return {"os": os_pretty(), "uptime": uptime_text()}


def run(cfg, opts) -> list[Finding]:
    disk_warn = cfg.get("thresholds", "disk_warn", default=80)
    disk_fail = cfg.get("thresholds", "disk_fail", default=90)
    mem_warn = cfg.get("thresholds", "mem_warn", default=85)
    mem_fail = cfg.get("thresholds", "mem_fail", default=95)
    temp_warn = cfg.get("thresholds", "temp_warn", default=80)
    temp_fail = cfg.get("thresholds", "temp_fail", default=90)
    updates_warn = cfg.get("thresholds", "updates_warn", default=10)

    findings: list[Finding] = []

    usage = shutil.disk_usage("/")
    disk_pct = usage.used / usage.total * 100
    disk_status = (
        FAILED if disk_pct >= disk_fail else WARN if disk_pct >= disk_warn else OK
    )
    findings.append(
        Finding(
            "host",
            "Disk /",
            disk_status,
            f"{disk_pct:.0f}% used · {usage.used / 1e9:.0f} GB of {usage.total / 1e9:.0f} GB",
            Action(
                "investigate",
                "find what filled the disk before deleting anything: "
                "`du -xh --max-depth=2 /home | sort -h | tail -20`.",
            )
            if disk_status != OK
            else None,
        )
    )

    total, available = _memory()
    if total:
        used_pct = (total - available) / total * 100
        mem_status = (
            FAILED if used_pct >= mem_fail else WARN if used_pct >= mem_warn else OK
        )
        findings.append(
            Finding(
                "host",
                "Memory",
                mem_status,
                f"{used_pct:.0f}% used · {(total - available) / 1e6:.1f} GB of {total / 1e6:.0f} GB",
                Action(
                    "investigate",
                    "list the largest processes with `ps -eo pid,comm,%mem,rss --sort=-rss | head`.",
                )
                if mem_status != OK
                else None,
            )
        )

    cores = os.cpu_count() or 1
    load = os.getloadavg()[0]
    findings.append(
        Finding(
            "host",
            "Load",
            WARN if load > cores else OK,
            f"{load:.1f} over 1 min on {cores} cores",
            Action(
                "investigate",
                "find what is competing for CPU with `top -o %CPU` and check for a runaway container.",
            )
            if load > cores
            else None,
        )
    )

    temperature = _temperature()
    if temperature is not None:
        temp_status = (
            FAILED
            if temperature >= temp_fail
            else WARN
            if temperature >= temp_warn
            else OK
        )
        findings.append(
            Finding(
                "host",
                "Temperature",
                temp_status,
                f"{temperature:.0f}°C",
                Action("investigate", "check the fans and the processes using CPU.")
                if temp_status != OK
                else None,
            )
        )

    reboot_required = Path("/var/run/reboot-required").exists()
    findings.append(
        Finding(
            "host",
            "Reboot",
            WARN if reboot_required else OK,
            "required" if reboot_required else "not required",
            Action(
                "manual",
                "reboot when convenient: a kernel or library update is waiting for it.",
            )
            if reboot_required
            else None,
        )
    )

    failed = _failed_units()
    findings.append(
        Finding(
            "host",
            "Failed units",
            WARN if failed else OK,
            "none"
            if not failed
            else f"{len(failed)}: " + ", ".join(failed[:3]),
            Action(
                "investigate",
                f"inspect `systemctl status {failed[0]}` and "
                f"`journalctl -u {failed[0]} -n 50 --no-pager` before restarting it.",
            )
            if failed
            else None,
        )
    )

    apt = _apt_updates()
    flatpak = _flatpak_updates()
    snap = _snap_updates()
    known = [value for value in (apt, flatpak, snap) if value is not None]
    pending = sum(known) if known else 0
    parts = []
    for label, value in (("apt", apt), ("flatpak", flatpak), ("snap", snap)):
        if value is not None:
            parts.append(f"{value} {label}")

    if not known:
        update_status = INFO
        detail = "update commands unavailable"
        action = None
    elif pending == 0:
        update_status = OK
        detail = "none pending"
        action = None
    else:
        update_status = WARN if pending >= updates_warn else INFO
        detail = " · ".join(parts)
        commands = []
        if apt:
            commands.append("`sudo apt upgrade`")
        if flatpak:
            commands.append("`flatpak update`")
        if snap:
            commands.append("`snap refresh`")
        action = Action(
            "command",
            "apply pending updates: " + ", ".join(commands) + " (each may ask for approval).",
        )

    findings.append(Finding("host", "Updates", update_status, detail, action))

    return findings
