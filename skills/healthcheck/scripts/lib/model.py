"""Shared data model for every healthcheck area."""

from __future__ import annotations

from dataclasses import dataclass

OK = "ok"
WARN = "warn"
FAIL = "fail"
SKIP = "skip"
INFO = "info"

# Lower sorts first, so the report opens with what needs attention.
ORDER = {FAIL: 0, WARN: 1, INFO: 2, OK: 3, SKIP: 4}

# The order areas appear in the report.
AREA_ORDER = ["setup", "agents", "lab", "web", "host", "services"]


@dataclass
class Action:
    """What the agent can do about a finding.

    kind is one of:
      command     a specific command, safe to run after approval
      investigate open a fix session and gather evidence first
      manual      a person has to do it (install, decide, reboot)
    """

    kind: str
    text: str

    def as_dict(self) -> dict:
        return {"kind": self.kind, "text": self.text}


@dataclass
class Finding:
    area: str
    title: str
    status: str
    detail: str = ""
    action: Action | None = None

    def as_dict(self) -> dict:
        data = {
            "area": self.area,
            "title": self.title,
            "status": self.status,
            "detail": self.detail,
        }
        if self.action:
            data["action"] = self.action.as_dict()
        return data
