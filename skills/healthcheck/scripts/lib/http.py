"""HTTP and command helpers.

Every request goes through curl so the IPv4 flag, timeouts and body limits
behave the same on every machine. The public lab hostnames resolve IPv6-only
on some networks, so IPv4 is the default.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass

META = "__HEALTHCHECK_META__"


@dataclass
class Response:
    ok: bool
    status: int
    body: str
    seconds: float
    error: str = ""


def fetch(
    url: str,
    timeout: float = 8,
    headers: dict[str, str] | None = None,
    ipv4: bool = True,
    max_bytes: int = 2_000_000,
) -> Response:
    command = [
        "curl",
        "-sS",
        "-L",
        "--max-time",
        str(int(timeout)),
        "--max-filesize",
        str(max_bytes),
        "-w",
        f"\n{META}%{{http_code}} %{{time_total}}",
    ]
    if ipv4:
        command.append("-4")
    for name, value in (headers or {}).items():
        command.extend(["-H", f"{name}: {value}"])
    command.append(url)

    try:
        proc = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout + 5,
        )
    except subprocess.TimeoutExpired:
        return Response(False, 0, "", timeout, "curl timed out")

    body, _, meta = proc.stdout.rpartition(META)
    status, seconds = 0, 0.0
    if meta:
        parts = meta.split()
        if parts:
            try:
                status = int(parts[0])
            except ValueError:
                status = 0
        if len(parts) > 1:
            try:
                seconds = float(parts[1])
            except ValueError:
                seconds = 0.0

    if proc.returncode != 0:
        message = proc.stderr.strip() or f"curl exited {proc.returncode}"
        return Response(False, status, body.strip(), seconds, message)

    return Response(True, status, body.strip(), seconds)


def run(command: list[str], timeout: float = 10) -> tuple[bool, str]:
    """Run a command and return (succeeded, combined output)."""
    try:
        proc = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except FileNotFoundError:
        return False, f"{command[0]} not found"
    except subprocess.TimeoutExpired:
        return False, f"{command[0]} timed out after {timeout:g}s"

    output = (proc.stdout + proc.stderr).strip()
    return proc.returncode == 0, output
