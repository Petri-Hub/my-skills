"""Agent parity: instructions, skills and MCP servers across every CLI."""

from __future__ import annotations

import json
import re
import shutil
import tomllib
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from lib import config as cfgmod
from lib.http import run as run_command
from lib.model import WARN, Action, Finding, OK, SKIP
from lib.versions import latest_github, latest_npm, semver

AGENTS = {
    "claude": {
        "display": "Claude Code",
        "binary": "claude",
        "instructions": "~/.claude/CLAUDE.md",
        "skills": "~/.claude/skills",
        "mcp": ("~/.claude.json", "json", "mcpServers"),
        "update": ("npm", "@anthropic-ai/claude-code"),
        "command": "claude update",
    },
    "codex": {
        "display": "Codex",
        "binary": "codex",
        "instructions": "~/.codex/AGENTS.md",
        "skills": "~/.codex/skills",
        "mcp": ("~/.codex/config.toml", "toml", "mcp_servers"),
        "update": ("npm", "@openai/codex"),
        "command": "codex update",
    },
    "opencode": {
        "display": "OpenCode",
        "binary": "opencode",
        "instructions": "~/.config/opencode/AGENTS.md",
        "skills": "~/.config/opencode/skills",
        "mcp": ("~/.config/opencode/opencode.json", "json", "mcp.servers"),
        "update": ("github", "anomalyco/opencode"),
        "command": "opencode upgrade",
    },
    "kiro": {
        "display": "Kiro",
        "binary": "kiro-cli",
        "instructions": "~/.kiro/steering/AGENTS.md",
        "skills": "~/.kiro/skills",
        "mcp": ("~/.kiro/settings/mcp.json", "json", "mcpServers"),
        "update": ("command", ["kiro-cli", "update", "--check"]),
        "command": "kiro-cli update",
    },
    "antigravity": {
        "display": "Antigravity",
        "binary": None,
        "instructions": "~/.gemini/config/AGENTS.md",
        "skills": "~/.gemini/config/skills",
        "mcp": ("~/.gemini/config/mcp_config.json", "json", "mcpServers"),
        "version_log": "~/.gemini/antigravity-cli/cli.log",
        "update": None,
        "command": "",
    },
}


def _walk(data, dotted: str):
    node = data
    for key in dotted.split("."):
        if not isinstance(node, dict):
            return None
        node = node.get(key)
    return node


def _read_mcp(spec) -> dict[str, bool] | None:
    raw_path, fmt, key = spec["mcp"]
    path = cfgmod.as_path(raw_path)
    if not path.is_file():
        return None
    try:
        if fmt == "toml":
            with path.open("rb") as handle:
                data = tomllib.load(handle)
        else:
            data = json.loads(path.read_text())
    except (OSError, ValueError, tomllib.TOMLDecodeError):
        return {}
    node = _walk(data, key)
    if not isinstance(node, dict):
        return {}
    return {
        name: not (isinstance(entry, dict) and entry.get("disabled"))
        for name, entry in node.items()
    }


def _installed_version(spec) -> str | None:
    binary = spec.get("binary")
    if binary and shutil.which(binary):
        ok, output = run_command([binary, "--version"], timeout=10)
        if ok:
            match = re.search(r"\d+\.\d+\.\d+", output)
            if match:
                return match.group(0)

    log = spec.get("version_log")
    if log:
        path = cfgmod.as_path(log)
        if path.is_file():
            text = path.read_bytes()[-200_000:].decode("utf-8", "replace")
            matches = re.findall(r"Language server version:\s*([\d.]+)", text)
            if matches:
                return matches[-1]
    return None


def _latest_command(command: list[str], installed: str | None) -> str | None:
    ok, output = run_command(command, timeout=20)
    if not ok:
        return None
    lowered = output.lower()
    if "current version" in lowered:
        match = re.search(r"\(([\d.]+)\)", output)
        return match.group(1) if match else installed
    match = re.search(r"(\d+\.\d+\.\d+)", output)
    return match.group(1) if match else None


def _latest(spec, installed: str | None) -> str | None:
    update = spec.get("update")
    if not update:
        return None
    kind, value = update
    if kind == "npm":
        return latest_npm(value)
    if kind == "github":
        return latest_github(value)
    if kind == "command":
        return _latest_command(value, installed)
    return None


def _repo_skills(repo: Path) -> set[str]:
    folder = repo / "skills"
    if not folder.is_dir():
        return set()
    return {
        path.name for path in folder.iterdir() if (path / "SKILL.md").is_file()
    }


def run(cfg, opts) -> list[Finding]:
    repo = cfgmod.as_path(
        cfg.get(
            "general",
            "my_skills",
            default="~/Desktop/Personal/Projects/my-skills",
        )
    )
    enabled = cfg.get("agents", "enabled", default=list(AGENTS))
    expected_override = cfg.get("agents", "expected_mcp", default=None)
    skills = _repo_skills(repo)

    findings: list[Finding] = []
    rows: dict[str, dict] = {}
    mcp_maps: dict[str, dict[str, bool] | None] = {}

    for key in enabled:
        spec = AGENTS.get(key)
        if not spec:
            continue
        display = spec["display"]
        skills_dir = cfgmod.as_path(spec["skills"])
        instructions = cfgmod.as_path(spec["instructions"])
        binary = spec.get("binary")
        present = (
            bool(binary and shutil.which(binary))
            or skills_dir.is_dir()
            or instructions.exists()
        )
        if not present:
            findings.append(Finding("agents", display, SKIP, "not installed"))
            continue

        servers = _read_mcp(spec)
        mcp_maps[key] = servers
        rows[key] = {
            "spec": spec,
            "display": display,
            "skills_dir": skills_dir,
            "instructions": instructions,
            "version": _installed_version(spec),
            "servers": servers,
        }

    if expected_override:
        expected = list(expected_override)
    else:
        expected = sorted(
            {
                name
                for servers in mcp_maps.values()
                if servers
                for name in servers
            }
        )

    with ThreadPoolExecutor(max_workers=6) as pool:
        latest_futures = {
            key: pool.submit(_latest, row["spec"], row["version"])
            for key, row in rows.items()
        }
        latest = {key: future.result() for key, future in latest_futures.items()}

    for key, row in rows.items():
        spec = row["spec"]
        display = row["display"]
        skills_dir = row["skills_dir"]
        instructions = row["instructions"]
        version = row["version"]
        servers = row["servers"]

        missing_skills = (
            sorted(name for name in skills if not (skills_dir / name).is_dir())
            if skills_dir.is_dir()
            else sorted(skills)
        )
        dangling = (
            sorted(
                path.name
                for path in skills_dir.iterdir()
                if path.is_symlink() and not path.exists()
            )
            if skills_dir.is_dir()
            else []
        )
        extra = (
            sorted(
                path.name
                for path in skills_dir.iterdir()
                if path.name not in skills and path.is_dir()
            )
            if skills_dir.is_dir()
            else []
        )

        instructions_ok = False
        if instructions.exists():
            try:
                instructions_ok = instructions.resolve() == (repo / "AGENTS.md").resolve()
            except OSError:
                instructions_ok = False

        enabled_servers = [name for name, on in (servers or {}).items() if on]
        missing_mcp = [name for name in expected if name not in enabled_servers]

        parts = [version or "version unknown"]
        parts.append(
            f"{len(skills) - len(missing_skills)}/{len(skills)} skills"
            if skills
            else "no repo skills"
        )
        if servers is None:
            parts.append(f"MCP 0/{len(expected)}")
        else:
            parts.append(f"MCP {len(enabled_servers)}/{len(expected)}")
        if opts.verbose and extra:
            parts.append(f"+{len(extra)} extra")

        status = OK
        action = None

        if missing_skills or dangling:
            status = WARN
            missing_text = ", ".join(missing_skills[:4])
            if len(missing_skills) > 4:
                missing_text += f" and {len(missing_skills) - 4} more"
            reason = "missing " + missing_text if missing_skills else ""
            if dangling:
                reason = (
                    (reason + "; " if reason else "")
                    + "dangling "
                    + ", ".join(dangling[:4])
                )
            action = Action(
                "command",
                f"relink the skills for {display}: run `make link` in {repo}. "
                f"It refuses paths that already exist, so clear those first ({reason}).",
            )
        elif not instructions_ok:
            status = WARN
            action = Action(
                "investigate",
                f"{display} instructions are not linked to {repo}/AGENTS.md; "
                "check the path and rerun `make link`.",
            )

        if servers is None:
            status = WARN
            parts.append("no config file")
            if action is None:
                action = Action(
                    "investigate",
                    f"{display} has no MCP config at {cfgmod.as_path(spec['mcp'][0])}. "
                    f"Add {', '.join(expected)}, or accept the gap and note it as intentional.",
                )
        elif missing_mcp:
            status = WARN
            if action is None:
                action = Action(
                    "investigate",
                    f"add {', '.join(missing_mcp)} to "
                    f"{cfgmod.as_path(spec['mcp'][0])} for {display}.",
                )

        new_version = latest.get(key)
        if new_version and version and semver(new_version) > semver(version):
            status = WARN
            parts.append(f"update {new_version}")
            if action is None and spec.get("command"):
                action = Action(
                    "command",
                    f"update {display} from {version} to {new_version} "
                    f"with `{spec['command']}`.",
                )

        findings.append(Finding("agents", display, status, " · ".join(parts), action))

    return findings
