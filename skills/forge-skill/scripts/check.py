#!/usr/bin/env python3
"""Check a skill folder against the rules forge-skill can verify mechanically.

Errors break the Agent Skills specification or leave a broken link, and make
the script exit with status 1. Warnings point at guidance worth a second look,
such as length and style.

Usage: python3 check.py <skill folder> [<skill folder> ...]
"""

import re
import sys
from pathlib import Path

NAME = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
KNOWN_KEYS = {
    # Agent Skills specification
    "name", "description", "license", "compatibility", "metadata", "allowed-tools",
    # Fields some agents add, such as Claude Code
    "argument-hint", "when_to_use", "disable-model-invocation", "user-invocable",
    "model", "context", "agent", "hooks",
}
TRIGGER = re.compile(r"\b(when|use|trigger)\b", re.IGNORECASE)
EMPHASIS = re.compile(r"\b(MUST|NEVER|ALWAYS|IMPORTANT|CRITICAL)\b")
PROHIBITION_TITLE = re.compile(r"^\s*[-*]\s+\*\*(Never|Don't|Do not)\b", re.IGNORECASE)
FENCE = re.compile(r"^\s*(`{3,}|~{3,})(.*)$")
INLINE_CODE = re.compile(r"`[^`]*`")
LINK = re.compile(r"\]\(([^)\s]+)\)")
BUNDLED_PATH = re.compile(r"`((?:references|scripts|assets)/[^`\s*]+)`")
SCHEME = re.compile(r"^[a-z][a-z0-9+.-]*:", re.IGNORECASE)
BUNDLED_DIRS = ("references", "scripts", "assets")
SOFT_LIMIT, HARD_LIMIT = 150, 500


def split_frontmatter(text):
    """Return (fields, body). Reads only the flat YAML that skills use."""
    if not text.startswith("---\n"):
        return None, text
    end = text.find("\n---", 4)
    if end == -1:
        return None, text
    fields, key = {}, None
    for line in text[4:end].splitlines():
        match = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
        if match:
            key, value = match.groups()
            fields[key] = "" if value in (">", "|", ">-", "|-") else value.strip().strip("\"'")
        elif key and line.startswith((" ", "\t")):
            fields[key] = (fields[key] + " " + line.strip()).strip()
    return fields, text[end + 4:]


def check_frontmatter(fields, folder):
    errors, warnings = [], []
    name = fields.get("name", "")
    if not name:
        errors.append("frontmatter has no name")
    elif len(name) > 64 or not NAME.match(name):
        errors.append(f"name '{name}' must be 1-64 lowercase letters, digits and single hyphens")
    elif name != folder:
        errors.append(f"name '{name}' does not match the folder '{folder}'")

    description = fields.get("description", "")
    if not description:
        errors.append("frontmatter has no description")
    elif len(description) > 1024:
        errors.append(f"description is {len(description)} characters, over the 1024 limit")
    elif not TRIGGER.search(description):
        warnings.append("description never says when to use the skill")

    for key in sorted(set(fields) - KNOWN_KEYS):
        warnings.append(f"frontmatter field '{key}' is unknown to most agents")
    return errors, warnings


def closes_fence(fence, match):
    """A fence closes on the same character, at least as long, with nothing after it."""
    marker, rest = match.groups()
    return marker[0] == fence[0] and len(marker) >= len(fence) and not rest.strip()


def prose(text, first_line):
    """Return the (number, line) pairs outside fenced code, and whether a fence was left open."""
    lines, fence = [], None
    for number, line in enumerate(text.splitlines(), start=first_line):
        match = FENCE.match(line)
        if fence is None and match:
            fence = match.group(1)
        elif fence and match and closes_fence(fence, match):
            fence = None
        elif fence is None:
            lines.append((number, line))
    return lines, fence is not None


def check_markdown(path, text, first_line, skill_dir, label):
    """Check the prose of one Markdown file: links, em dashes, emphasis and headings."""
    errors, warnings = [], []
    lines, unclosed = prose(text, first_line)
    for number, line in lines:
        where = f"{label}:{number}"
        outside_code = INLINE_CODE.sub("", line)
        for target in LINK.findall(outside_code):
            target = target.split("#")[0]
            if target and not SCHEME.match(target) and not (path.parent / target).exists():
                errors.append(f"{where}: links to missing file {target}")
        for target in BUNDLED_PATH.findall(line):
            if not (skill_dir / target).exists():
                warnings.append(f"{where}: mentions {target}, which is not in the skill folder")
        if "\N{EM DASH}" in line:
            warnings.append(f"{where}: em dash")
        if match := EMPHASIS.search(outside_code):
            warnings.append(f"{where}: capitalized emphasis '{match.group()}'")
        if re.match(r"^#+\s+\*\*", line):
            warnings.append(f"{where}: bold inside a heading")
        if PROHIBITION_TITLE.match(line):
            warnings.append(f"{where}: rule title starts with a prohibition; say what to do, "
                            "or keep it for a true invariant and state the reason")
    if unclosed:
        errors.append(f"{label}: a code fence is never closed")
    return errors, warnings


def check_length(body):
    lines = len(body.strip().splitlines())
    if lines > HARD_LIMIT:
        return [], [f"SKILL.md body is {lines} lines, over the {HARD_LIMIT}-line ceiling"]
    if lines > SOFT_LIMIT:
        return [], [f"SKILL.md body is {lines} lines; aim for about {SOFT_LIMIT} by moving depth to references/"]
    return [], []


def unlinked_files(skill_dir, skill_text):
    """Warn about bundled files SKILL.md never mentions, since agents rarely find them."""
    warnings = []
    for folder in BUNDLED_DIRS:
        for path in sorted((skill_dir / folder).glob("*")):
            relative = path.relative_to(skill_dir).as_posix()
            if not path.name.startswith((".", "__")) and relative not in skill_text:
                warnings.append(f"{relative} is never mentioned in SKILL.md")
    return [], warnings


def check(skill_dir):
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        return [f"no SKILL.md in {skill_dir}"], []
    text = skill_md.read_text(encoding="utf-8")
    fields, body = split_frontmatter(text)
    if fields is None:
        return ["SKILL.md must start with a --- frontmatter block"], []

    first_body_line = text[: len(text) - len(body)].count("\n") + 1
    results = [
        check_frontmatter(fields, skill_dir.name),
        check_markdown(skill_md, body, first_body_line, skill_dir, "SKILL.md"),
        check_length(body),
        unlinked_files(skill_dir, text),
    ]
    for reference in sorted((skill_dir / "references").glob("*.md")):
        reference_text = reference.read_text(encoding="utf-8")
        results.append(check_markdown(reference, reference_text, 1, skill_dir, f"references/{reference.name}"))

    errors = [message for found, _ in results for message in found]
    warnings = [message for _, found in results for message in found]
    return errors, warnings


def main(paths):
    if not paths:
        print(__doc__.strip())
        return 2
    failed = False
    for path in map(Path, paths):
        skill_dir = (path.parent if path.name == "SKILL.md" else path).resolve()
        errors, warnings = check(skill_dir)
        print(f"{skill_dir.name}: {len(errors)} errors, {len(warnings)} warnings")
        for message in errors:
            print(f"  error: {message}")
        for message in warnings:
            print(f"  warning: {message}")
        failed = failed or bool(errors)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
