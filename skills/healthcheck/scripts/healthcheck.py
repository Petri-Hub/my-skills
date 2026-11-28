#!/usr/bin/env python3
"""Run every healthcheck area and render one report.

Exit codes: 0 healthy, 1 at least one failure, 2 usage or config error.
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from checks import agents, host, lab, services, web  # noqa: E402
from lib import config as cfgmod  # noqa: E402
from lib.model import AREA_ORDER, FAIL, WARN, Action, Finding  # noqa: E402
from lib.report import counts, render, render_json  # noqa: E402

AREAS = {
    "agents": agents.run,
    "lab": lab.run,
    "web": web.run,
    "host": host.run,
    "services": services.run,
}

# Areas that need the inventory; the rest still run without one.
NEEDS_CONFIG = ("lab", "web", "services")


@dataclass
class Options:
    verbose: bool = False
    deep: bool = False


def _wants_color(choice: str) -> bool:
    if choice == "yes":
        return True
    if choice == "no":
        return False
    if os.environ.get("NO_COLOR"):
        return False
    return sys.stdout.isatty()


def _wants_ascii(forced: bool) -> bool:
    if forced:
        return True
    encoding = (sys.stdout.encoding or "").lower()
    if "utf" in encoding:
        return False
    locale = os.environ.get("LC_ALL") or os.environ.get("LANG") or ""
    return "utf" not in locale.lower()


def _short(path: Path) -> str:
    try:
        home = Path.home()
        return "~/" + str(path.relative_to(home))
    except ValueError:
        return str(path)


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="healthcheck",
        description="Scan this machine, its agents and the lab, then print one report.",
    )
    parser.add_argument("--config", help="path to config.toml")
    parser.add_argument(
        "--area",
        action="append",
        metavar="NAME",
        help="run only these areas (agents, lab, web, host, services)",
    )
    parser.add_argument("--deep", action="store_true", help="add SSH checks on the lab")
    parser.add_argument("--json", action="store_true", help="print findings as JSON")
    parser.add_argument("--verbose", action="store_true", help="add coverage details")
    parser.add_argument(
        "--color",
        choices=["auto", "yes", "no"],
        default="auto",
        help="color output (default: only on a TTY)",
    )
    parser.add_argument("--no-color", action="store_true", help="disable color")
    parser.add_argument("--ascii", action="store_true", help="use ASCII glyphs")
    parser.add_argument("--width", type=int, help="report width in columns")
    args = parser.parse_args()

    selected = [name for name in AREA_ORDER if name in AREAS]
    if args.area:
        requested = [
            name.strip() for item in args.area for name in item.split(",") if name.strip()
        ]
        unknown = [name for name in requested if name not in AREAS]
        if unknown:
            parser.error(f"unknown area(s): {', '.join(unknown)}")
        selected = [name for name in AREA_ORDER if name in AREAS and name in requested]

    cfg = cfgmod.load(args.config)
    opts = Options(verbose=args.verbose, deep=args.deep)
    started = time.monotonic()

    findings: list[Finding] = []
    if not cfg.exists:
        skipped = [name for name in selected if name in NEEDS_CONFIG]
        selected = [name for name in selected if name not in NEEDS_CONFIG]
        detail = f"{cfg.path} is missing"
        if skipped:
            detail += " · skipped " + ", ".join(skipped)
        findings.append(
            Finding(
                "setup",
                "No inventory",
                WARN,
                detail,
                Action(
                    "manual",
                    "copy assets/config.example.toml to "
                    "~/.config/healthcheck/config.toml, fill in the lab, services and "
                    "sites, then rerun. Agents and this PC were checked anyway.",
                ),
            )
        )

    for area in selected:
        try:
            findings.extend(AREAS[area](cfg, opts))
        except Exception as exc:  # one broken check must not kill the report
            findings.append(
                Finding(
                    area,
                    "Check crashed",
                    FAIL,
                    f"{type(exc).__name__}: {exc}",
                    Action(
                        "investigate",
                        "this is a healthcheck bug: rerun the area with --json and "
                        "fix the check module.",
                    ),
                )
            )

    duration = time.monotonic() - started
    header = host.header_meta()
    meta = {
        "host": os.uname().nodename,
        "os": header.get("os", ""),
        "uptime": header.get("uptime", ""),
        "date": datetime.now().astimezone().strftime("%a %d %b %Y %H:%M %Z"),
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "duration": duration,
    }

    config_path = _short(cfg.path)

    if args.json:
        print(
            render_json(
                findings,
                meta,
                config_path=config_path,
                configured=cfg.exists,
            )
        )
    else:
        print(
            render(
                findings,
                meta,
                color=_wants_color("no" if args.no_color else args.color),
                ascii_glyphs=_wants_ascii(args.ascii),
                width=args.width,
                config_path=config_path if cfg.exists else "",
            )
        )

    totals = counts(findings)
    return 1 if totals[FAIL] else 0


if __name__ == "__main__":
    sys.exit(main())
