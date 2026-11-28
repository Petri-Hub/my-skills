"""Render findings as a terminal dashboard or as JSON."""

from __future__ import annotations

import json
import shutil
import textwrap

from .model import AREA_ORDER, FAIL, INFO, OK, ORDER, SKIP, WARN, Finding

RESET = "\033[0m"
BOLD = "1"
DIM = "2"
TITLE = "1;36"

STATUS_COLOR = {
    OK: "32",
    WARN: "33",
    FAIL: "31",
    INFO: "36",
    SKIP: "90",
}

GLYPHS = {
    OK: "✔",
    WARN: "▲",
    FAIL: "✖",
    INFO: "·",
    SKIP: "·",
}

ASCII_GLYPHS = {
    OK: "+",
    WARN: "!",
    FAIL: "x",
    INFO: "-",
    SKIP: "-",
}

ACTION_COLOR = {
    "command": "32",
    "investigate": "33",
    "manual": "36",
}

AREA_TITLES = {
    "setup": "Setup",
    "agents": "Agents",
    "lab": "Lab",
    "web": "Public web",
    "host": "This PC",
    "services": "Background services",
}

TITLE_WIDTH = 18
KIND_WIDTH = 11


class Style:
    def __init__(self, color: bool, ascii_glyphs: bool) -> None:
        self.color = color
        self.ascii = ascii_glyphs

    def paint(self, text: str, code: str) -> str:
        if not self.color or not code:
            return text
        return f"\033[{code}m{text}{RESET}"

    def glyph(self, status: str) -> str:
        table = ASCII_GLYPHS if self.ascii else GLYPHS
        return table[status]

    def rule(self, width: int) -> str:
        return "-" * width if self.ascii else "─" * width

    def borders(self) -> tuple[str, str, str, str, str, str]:
        """top-left, top-right, bottom-left, bottom-right, horizontal, vertical."""
        if self.ascii:
            return "+", "+", "+", "+", "-", "|"
        return "╭", "╮", "╰", "╯", "─", "│"


def counts(findings: list[Finding]) -> dict[str, int]:
    result = {OK: 0, WARN: 0, FAIL: 0, SKIP: 0, INFO: 0}
    for finding in findings:
        result[finding.status] = result.get(finding.status, 0) + 1
    return result


def summary(c: dict[str, int], keys: list[str]) -> str:
    return " · ".join(f"{c.get(key, 0)} {key}" for key in keys if c.get(key))


def _truncate(text: str, width: int) -> str:
    if width <= 1 or len(text) <= width:
        return text
    return text[: width - 1] + "…"


def render(
    findings: list[Finding],
    meta: dict,
    *,
    color: bool,
    ascii_glyphs: bool,
    width: int | None = None,
    config_path: str = "",
) -> str:
    style = Style(color, ascii_glyphs)
    term = width or shutil.get_terminal_size((100, 24)).columns
    width = max(72, min(term, 96))

    totals = counts(findings)
    top_left, top_right, bottom_left, bottom_right, horizontal, vertical = style.borders()
    inner = width - 4
    lines: list[str] = []

    first = f"HEALTHCHECK  {meta.get('host', '')}"
    extras = [part for part in (meta.get("os"), meta.get("uptime")) if part]
    if extras:
        first += " · " + " · ".join(extras)

    second = f"{meta.get('date', '')} · {len(findings)} "
    second += "check" if len(findings) == 1 else "checks"
    second += " · " + summary(totals, [FAIL, WARN, INFO, OK, SKIP])

    lines.append(style.paint(top_left + horizontal * (width - 2) + top_right, DIM))
    for text, code in ((first, TITLE), (second, "")):
        plain = text[:inner]
        pad = " " * (inner - len(plain))
        lines.append(
            style.paint(vertical, DIM)
            + " "
            + style.paint(plain, code)
            + pad
            + " "
            + style.paint(vertical, DIM)
        )
    lines.append(style.paint(bottom_left + horizontal * (width - 2) + bottom_right, DIM))

    areas: dict[str, list[Finding]] = {}
    for finding in findings:
        areas.setdefault(finding.area, []).append(finding)

    for area in AREA_ORDER + sorted(set(areas) - set(AREA_ORDER)):
        group = areas.get(area)
        if not group:
            continue
        group = sorted(group, key=lambda f: (ORDER[f.status], f.title.lower()))
        right = summary(counts(group), [FAIL, WARN, INFO, OK, SKIP])
        title = f" {AREA_TITLES.get(area, area).upper()} "
        fill = width - len(title) - len(right) - 1
        lines.append("")
        lines.append(
            style.paint(title, BOLD)
            + style.paint(style.rule(max(fill, 2)), DIM)
            + " "
            + right
        )
        for finding in group:
            glyph = style.paint(style.glyph(finding.status), STATUS_COLOR[finding.status])
            title_text = _truncate(finding.title, TITLE_WIDTH)
            room = width - 4 - TITLE_WIDTH
            detail = _truncate(finding.detail, room)
            lines.append(f" {glyph} {title_text:<{TITLE_WIDTH}} {detail}")

    actionable = [f for f in findings if f.action]
    actionable.sort(key=lambda f: ORDER[f.status])

    lines.append("")
    lines.append(style.paint(" NEXT ACTIONS", BOLD))
    if not actionable:
        lines.append("   Nothing to do. Every check passed.")
    else:
        for index, finding in enumerate(actionable, start=1):
            action = finding.action
            head = f" {index:>2}  "
            tail_indent = " " * (len(head) + KIND_WIDTH + 2)
            wrapped = textwrap.wrap(
                action.text, width=max(30, width - len(tail_indent))
            ) or [""]
            kind = style.paint(action.kind, ACTION_COLOR.get(action.kind, ""))
            pad = " " * (KIND_WIDTH - len(action.kind))
            lines.append(head + kind + pad + "  " + wrapped[0])
            for extra in wrapped[1:]:
                lines.append(tail_indent + extra)

        judgement = [
            f for f in actionable if f.action.kind in ("investigate", "manual")
        ]
        if judgement:
            lines.append("")
            lines.append(
                style.paint(
                    f"  {len(judgement)} of these need a closer look or a human decision. "
                    "Open a fix session to work through them.",
                    DIM,
                )
            )

    footer = f" {meta.get('duration', 0):.1f}s"
    footer += f" · config {config_path}" if config_path else " · no config file"
    lines.append("")
    lines.append(style.paint(footer, DIM))

    output = "\n".join(lines)
    if ascii_glyphs:
        output = (
            output.replace("·", "|")
            .replace("…", "...")
            .replace("°C", " C")
            .replace("→", "->")
        )
    return output


def render_json(
    findings: list[Finding],
    meta: dict,
    *,
    config_path: str,
    configured: bool,
) -> str:
    payload = {
        "generated_at": meta.get("generated_at"),
        "host": meta.get("host"),
        "os": meta.get("os"),
        "uptime": meta.get("uptime"),
        "duration_s": round(meta.get("duration", 0), 2),
        "configured": configured,
        "config_path": config_path,
        "counts": counts(findings),
        "areas": {
            area: counts([f for f in findings if f.area == area])
            for area in sorted({f.area for f in findings})
        },
        "findings": [f.as_dict() for f in findings],
        "actions": [
            {
                "area": f.area,
                "title": f.title,
                "kind": f.action.kind,
                "text": f.action.text,
            }
            for f in sorted(findings, key=lambda f: ORDER[f.status])
            if f.action
        ],
    }
    return json.dumps(payload, indent=2)
