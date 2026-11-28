"""Public sites: reachable, and actually serving content."""

from __future__ import annotations

from lib.http import fetch
from lib.model import FAIL, OK, SKIP, WARN, Action, Finding

AREA = "web"


def run(cfg, opts) -> list[Finding]:
    sites = cfg.get("web", "sites", default=[]) or []
    timeout = cfg.get("general", "timeout", default=8)

    if not sites:
        return [
            Finding(
                AREA,
                "Sites",
                SKIP,
                "none configured",
                Action(
                    "manual",
                    "create ~/.config/healthcheck/config.toml from "
                    "assets/config.example.toml and add `[[web.sites]]` entries to "
                    "check public pages.",
                )
                if not cfg.exists
                else None,
            )
        ]

    findings: list[Finding] = []
    for site in sites:
        name = site.get("name") or site.get("url", "site")
        url = site.get("url")
        if not url:
            findings.append(Finding(AREA, name, SKIP, "no url configured"))
            continue

        expect = site.get("expect")
        min_bytes = int(site.get("min_bytes", 500))

        response = fetch(url, timeout=timeout)
        size = len(response.body.encode("utf-8"))

        if not response.ok or response.status != 200:
            findings.append(
                Finding(
                    AREA,
                    name,
                    FAIL,
                    f"{response.status or 'no response'} · {response.error or 'request failed'}",
                    Action(
                        "investigate",
                        f"open {url} in a browser, then check the hosting project and the "
                        "Cloudflare DNS record before changing code.",
                    ),
                )
            )
            continue

        detail = f"{response.status} · {size / 1024:.0f} KB · {response.seconds:.1f}s"
        status = OK
        action = None

        if expect:
            present = expect.lower() in response.body.lower()
            detail += f" · contains '{expect}'" if present else f" · missing '{expect}'"
            if not present:
                status = FAIL
                action = Action(
                    "investigate",
                    f"{name} answers 200 but the page no longer contains '{expect}'. "
                    "Check the last deploy and the response body before touching DNS.",
                )

        if size < min_bytes and status == OK:
            status = WARN
            detail += f" · under {min_bytes} bytes"
            action = Action(
                "investigate",
                f"{name} answers 200 with only {size} bytes; it may be an error page "
                "served as HTML.",
            )

        findings.append(Finding(AREA, name, status, detail, action))

    return findings
