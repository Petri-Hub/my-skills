# What each check measures

Every row is one `Finding` produced by a module in `scripts/checks/`. A finding has an area, a
title, a status (`ok`, `warn`, `fail`, `info`, `skip`), a detail string and an optional action
tagged `command`, `investigate` or `manual`.

## setup

Appears only when the inventory is missing. It names the path it looked for, skips `lab`, `web`
and `services`, and still runs `agents` and `host`, so a fresh machine still gets a useful report.

## agents

Compares each CLI against one source of truth: `my_skills` in the config.

| Row | Source | Warns when |
|---|---|---|
| `<Agent>` | `--version` (or Antigravity's language-server log) | skills missing or dangling, instructions not linked to `my-skills/AGENTS.md`, MCP servers missing, a newer release exists |
| `MCP n/m` (part of the same row) | the agent's own config file | the config is absent or a server is missing or disabled |

Version sources: npm registry for Claude and Codex, the GitHub release list for OpenCode, and
`kiro-cli update --check` for Kiro. The expected MCP set comes from `expected_mcp`, or from the
union of what the agents already have when that key is absent.

Skills parity compares the folders in `my-skills/skills/` that contain a `SKILL.md` with the
directories under each agent's skills path. Extra marketplace skills are ignored unless
`--verbose` is on.

## lab

Reads the public Gatus API, so it works with no VPN and no SSH.

| Row | Source | Notes |
|---|---|---|
| One row per endpoint | `GET /api/v1/endpoints/statuses` | `fail` when the last result failed, `warn` when any of the last 50 failed or 24h uptime is under 99% |
| `Coverage` | folder names in the lab repo | only with `--verbose`; lists services with no Gatus endpoint |

`--deep` adds an SSH pass over Tailscale:

| Row | Source | Notes |
|---|---|---|
| `Lab containers` | `docker ps -a` plus `docker inspect` | `warn` for unhealthy containers, a non-zero exit in the last 7 days, or a container stuck restarting. Older exits and clean stops are counted as parked |
| `Lab disk` | `df -P /` | `warn` at 80% |
| `Lab reboot` | `/var/run/reboot-required` | `manual` action |
| `Lab jobs` | `docker logs --since 2h ofelia` | `warn` when any scheduled run failed |
| `Backups` | the same log, `backup-*` jobs | `warn` when the last run is over an hour old or none appeared in 2h |

A failed SSH is a `skip` with an investigate action, never a `fail`: the public checks still ran.

## web

One row per `[[web.sites]]` entry.

- `fail` when the status is not 200, when `expect` is absent from the body, or when the request errors.
- `warn` when the body is under `min_bytes` (default 500), which usually means an error page served as HTML.

Content matching is case-insensitive, so `expect = "Petri"` survives a rebuild that changes markup.

## host

| Row | Source | Warns when |
|---|---|---|
| `Disk /` | `shutil.disk_usage` | `disk_warn` (80), fails at `disk_fail` (90) |
| `Memory` | `/proc/meminfo` | `mem_warn` (85), fails at `mem_fail` (95) |
| `Load` | `os.getloadavg` | 1-minute load above the core count |
| `Temperature` | thermal zones, then `sensors` | `temp_warn` (80), fails at `temp_fail` (90); absent on machines with no sensor |
| `Reboot` | `/var/run/reboot-required` | a kernel or library update is waiting |
| `Failed units` | `systemctl --failed` | any unit is failed |
| `Updates` | `apt list --upgradable`, `flatpak remote-ls --updates`, `snap refresh --list` | `warn` at `updates_warn` (10), `info` below it |

The update row only lists commands for the package managers that actually have pending updates.

## services

| Row | Source | Notes |
|---|---|---|
| `ai-memory` | `GET /web/login` and `GET /mcp`, plus `ai-memory --version` | web must be 200; `/mcp` 401 is healthy; `warn` when the CLI is behind the latest GitHub release or missing |
| `Wakapi` | `/users/current/statusbar/today` and the compat heartbeat list | `fail` when the API is unreachable; `warn` when the newest heartbeat is older than `max_heartbeat_age_min` (180) |

The Wakapi key is read from `api_key_file` (default `~/.wakatime.cfg`) and sent as `?api_key=`,
because Basic auth returns 401 on this server. It is never printed.

## Adding a check

1. Add or edit a module in `scripts/checks/`, exporting `run(cfg, opts) -> list[Finding]`.
2. Build each finding with `Finding(area, title, status, detail, action)`. Give it an `Action` when
   something can be done; otherwise leave it `None`.
3. Put any new threshold under `[thresholds]` in the config and read it through `cfg.get`, so the
   inventory stays the only place numbers live.
4. Register a new area in `AREAS` and `ORDER` in `scripts/healthcheck.py`, and give it a title in
   `AREA_TITLES` in `scripts/lib/report.py`.
5. Run the script with `--area <name> --json` before and after, and add a row to this file.
