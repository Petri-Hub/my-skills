"""Version lookups shared by the agent and service checks."""

from __future__ import annotations

import json
import re

from lib.http import fetch


def semver(value: str | None) -> tuple[int, ...]:
    parts = re.findall(r"\d+", value or "")
    return tuple(int(part) for part in parts[:3]) or (0,)


def latest_npm(package: str) -> str | None:
    response = fetch(f"https://registry.npmjs.org/{package}/latest", timeout=8)
    if response.ok and response.status == 200:
        try:
            return json.loads(response.body).get("version")
        except ValueError:
            return None
    return None


def latest_github(repo: str) -> str | None:
    """Highest non-prerelease semver release.

    releases/latest is not enough: OpenCode still marks the v1 line as latest
    while publishing v2 releases.
    """
    response = fetch(
        f"https://api.github.com/repos/{repo}/releases?per_page=30", timeout=10
    )
    if not response.ok or response.status != 200:
        return None
    try:
        releases = json.loads(response.body)
    except ValueError:
        return None
    tags = [
        release.get("tag_name", "")
        for release in releases
        if isinstance(release, dict)
        and not release.get("prerelease")
        and not release.get("draft")
        and re.match(r"^v?\d+\.\d+\.\d+$", release.get("tag_name", ""))
    ]
    if not tags:
        return None
    return max(tags, key=semver).lstrip("v")
