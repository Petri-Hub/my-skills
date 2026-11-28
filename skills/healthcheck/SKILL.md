---
name: healthcheck
description: Scans Petri's machine, agent setup, public sites and homelab, then prints one visual report with next actions. Use when he asks for a healthcheck, "how is everything", "is the lab ok", a checkup, or a status sweep before a release.
---

# Healthcheck

You are the operator on duty: the person asking wants to know what is wrong before it bites, and what to do about it. The script gathers facts and prints a dashboard; judging what those facts mean, and which of them deserve work today, is yours. Good output is a short, ordered answer that names the real problems and leaves the noise out.

## When not to use

- **One service, one question** ("is Wakapi up?", "why is Gatus red?"): curl or SSH it directly. This skill pays off on the whole sweep, not on a single probe.
- **Changing what is monitored**: that belongs in the lab repo's Gatus config, not here.
- **Upgrading a single agent**: use that agent's own updater; the report only tells you it is behind.

## Workflow

### 1. Run the scan

From the skill folder:

```bash
python3 scripts/healthcheck.py
```

Add `--deep` when the lab matters (SSH over Tailscale adds containers, disk, reboot, backups and scheduled jobs). Add `--json` when you want to filter or count instead of read. Areas are `agents`, `lab`, `web`, `host` and `services`; repeat `--area` to narrow a fix session.

You're done when you have the report or a clear error: exit 0 means no failures, 1 means at least one `fail`, 2 means a usage or config problem.

### 2. Read it like an operator

Work down the severity: `fail` first, then `warn`, then `info`. `skip` means "not configured or not reachable", never "healthy". Treat the 24h uptime beside a green lab row as the real signal: a row that says `up` but shows 97% flapped during the night deserves a sentence of its own.

If a row says `Check crashed`, that is a bug in this skill, not in the machine.

### 3. Say what matters

Lead with the worst finding and what it costs: "five flatpak updates are pending and `fwupd-refresh` has been failing since boot" beats a recital of thirty rows. Skip the healthy rows unless the person asked for the whole picture, and mention anything that is green only because a fallback worked.

### 4. Propose the next actions

The report numbers them and tags each one `command`, `investigate` or `manual`. Pass them on in that shape:

- `command`: a known fix. Say what it changes and ask before running it.
- `investigate`: the cause is unknown. Say what you would look at and why.
- `manual`: needs Petri's hands or his approval, such as a reboot or a lab restart.

Do not run updates, reboots or restarts just because they are listed.

### 5. Offer a fix session

When `investigate` or `manual` actions remain, offer to open a fix session: pick one area, rerun it with `--area <name> --json`, work one finding at a time, and rerun that area after each fix to prove it moved. Say so in one line, then stop and let the person choose. A healthcheck that ends in a wall of unowned findings is a worse outcome than one that ends with two things fixed.

## Constraints and guidelines

- **Read-only by default**: the script only reads. Every change comes from you, after the person agrees, so the report stays safe to run at any time.
- **Keep the inventory out of the repo**: real values live in `~/.config/healthcheck/config.toml`; the repo ships `assets/config.example.toml` with placeholders. The config points at key files such as `~/.wakatime.cfg` and never holds the key itself, and no key or token is printed in a report.
- **Trust the config for thresholds**: disk, memory, temperature and update counts come from the config, not from code. If a threshold feels wrong, change the config and say why.
- **One finding per check, with a next step**: a finding without an action is only worth reporting when it explains something else. Do not add checks that can only say "fine".
- **`curl` and `python3` are the only hard dependencies**: HTTP goes through `curl -4` on purpose; see the gotchas.

## Gotchas

- **The lab hostnames are IPv6-only from this network**: `lab-wakapi.petri.zip` resolves AAAA, and plain `curl` fails while Gatus reports Wakapi healthy. Every request uses `curl -4`; keep it that way.
- **Wakapi's compat heartbeat date is shifted**: `?date=<today>` returns yesterday's heartbeats here, so the check reads today and tomorrow and keeps the newest.
- **`/mcp` returning 401 is healthy**: ai-memory protects that endpoint with a token. Only a 5xx or a timeout means the server is down.
- **Kiro ships without an MCP config**: `MCP 0/3` for Kiro is a real gap, not a crash. Decide with Petri whether to add `~/.kiro/settings/mcp.json` or record it as intentional.
- **OpenCode's `releases/latest` lies**: it still points at the v1 line while v2 ships. The check takes the highest non-prerelease tag instead.
- **A container stopped months ago is parked, not broken**: game servers stopped by hand show `Exited`. The deep check warns only for an unhealthy container, a recent non-zero exit, or one stuck restarting.
- **No config, no lab**: without `~/.config/healthcheck/config.toml` the report says so and skips `lab`, `web` and `services`, still checking agents and this PC. Do not read that as a clean bill of health.
- **`make link` refuses paths that already exist**: when a row says skills are missing, clear the stale path first, then relink.

## Examples

**Bad:**

```text
Here is the full report:
<40 lines of dashboard>
Everything else looks fine. Let me know if you want me to fix anything.
```

**Good:**

```text
Two things are worth your time. `fwupd-refresh.service` has failed since boot, so firmware updates
are silently not being checked, and 5 flatpak + 7 snap updates are pending. Everything else is
healthy: all 14 Gatus endpoints at 100% for 24h, petri.zip serving 26 KB, disk at 55%, no reboot
needed.

Want me to look at the fwupd unit first (read-only, `journalctl` before touching it), then run the
flatpak and snap updates? Separately, OpenCode 2.4.1 is one patch behind and the ai-memory CLI is
on 3.2.9 against a 3.6.4 server line; I can upgrade both if you want.
```

The good one leads with impact, keeps the healthy rows to a single line, and ends with a decision the person can make in one word.

## Output

The terminal report looks like this (colors on a TTY, Unicode or `--ascii`, plain text when piped):

```text
╭──────────────────────────────────────────────────────────────────────────╮
│ HEALTHCHECK  monstrao · Ubuntu 25.10 · up 5h 40m                         │
│ Fri 27 Nov 2026 18:00 -03 · 28 checks · 5 warn · 23 ok                   │
╰──────────────────────────────────────────────────────────────────────────╯

 AGENTS ──────────────────────────────────────────── 2 warn · 3 ok
 ▲ Kiro               3.6.2 · 16/16 skills · MCP 0/3 · no config file
 ✔ Claude Code        2.1.332 · 16/16 skills · MCP 3/3

 NEXT ACTIONS
  1  command      update OpenCode from 2.4.1 to 2.4.2 with `opencode upgrade`.
  2  investigate  Kiro has no MCP config at /home/petri/.kiro/settings/mcp.json. ...
```

`--json` returns the same findings as objects with `area`, `title`, `status`, `detail` and an optional `action`, plus counts per area and a flat `actions` list.

## Checklist

Before finishing, confirm that:
- [ ] Every `fail` is named in your answer, with its next action
- [ ] Warnings are either proposed or explicitly deferred, never silently dropped
- [ ] No command that changes state ran without the person's agreement
- [ ] No key, token or secret appears in what you print
- [ ] If findings remain open, you offered a fix session and named the area to start with

## References

| File | Read it when |
|---|---|
| [references/checks.md](references/checks.md) | you need to know what a row measures, where it comes from, or how to add a check |
| [assets/config.example.toml](assets/config.example.toml) | you are creating or repairing the local inventory |

The code is one module per area: `scripts/checks/agents.py`, `scripts/checks/host.py`, `scripts/checks/lab.py`, `scripts/checks/web.py` and `scripts/checks/services.py`, with shared helpers in `scripts/lib/`.
