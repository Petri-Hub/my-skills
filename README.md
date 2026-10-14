# 🧩 my-skills

> My personal collection of skills for AI agent harnesses.

This repository holds my shared agent context and the skills I use across agent harnesses. It is public for reference; some skills may need adaptation for other setups.

## Layout

Each skill has a top-level directory with a `SKILL.md` entry point. Supporting files live beside it.

| Skill | Source | Notes |
|---|---|---|
| [brag](brag/SKILL.md) | [latent-spaces/brag](https://github.com/latent-spaces/brag/tree/main/skills/brag) | MIT; bundled audio has separate credits in [its music README](brag/assets/music/README.md). |
| [humanizer](humanizer/SKILL.md) | [blader/humanizer](https://github.com/blader/humanizer) | MIT. |
| [simplify](simplify/SKILL.md) | [Akita's adaptation](https://github.com/akitaonrails/my-skills/tree/master/simplify) of [Addy Osmani's skill](https://github.com/addyosmani/agent-skills/tree/main/skills/code-simplification) | Addy's MIT notice is included in the skill directory. |
| [style](style/SKILL.md) | [kent-beck-style](https://github.com/nathankim0/clean-architecture-skills/tree/main/plugins/kent-beck-style/skills/kent-beck-style) | Renamed for my coding workflow; MIT. |

These are local copies. Upstream changes need to be reviewed and pulled in manually.

## Global context

The root `AGENTS.md` holds my shared context and guidelines for coding agents. On this machine, Codex reads it through `~/.codex/AGENTS.md`, which points to this repository.

## Across harnesses

Each harness can link individual skill directories from this repository into its own skills directory. That lets the harness keep its own built-in and plugin skills alongside these shared ones. Codex currently has separate copies under `~/.codex/skills`; those copies do not update automatically when this repository changes.
