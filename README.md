<h1 align="center">🧩 my-skills</h1>

<br>

<h3 align="center">The context and skills I carry between coding agents.<br>Who I am, where the work lives, and how I want it done</h3>

<p align="center">
  <a href="https://github.com/Petri-Hub/my-skills/commits/main"><img alt="Last commit" src="https://img.shields.io/github/last-commit/Petri-Hub/my-skills" /></a>
</p>

<br>

## About

> **TL;DR:** Models, subscriptions and coding agents change. This repository keeps the context and skills I carry between them: who I am, how I work and the workflows I use day to day. Symlinks let different agents share the same files.

<img width="1500" height="505" alt="The my-skills repository shares AGENTS.md and skills with Claude Code, Codex, OpenCode and other AI agents through symlinks." src="https://github.com/user-attachments/assets/30fca26a-0498-44a8-ab67-0aedab6a5ae4" />

## Setup

Run `make link` once per machine, and again after adding a skill or setting up a new agent. It links this repository's files into each agent's own directories:

| Agent | Instructions | Skills |
|---|---|---|
| Claude Code | `~/.claude/CLAUDE.md` | `~/.claude/skills/` |
| Codex | `~/.codex/AGENTS.md` | `~/.codex/skills/` |
| OpenCode | `~/.config/opencode/AGENTS.md` | `~/.config/opencode/skills/` |

## Skills

Each directory has a `SKILL.md` entry point and any files that skill needs.

| Skill | What it does |
|---|---|
| [style](style/SKILL.md) | Applies Kent Beck's simple design principles while writing, reviewing or refactoring code. |
| [simplify](simplify/SKILL.md) | Makes working code easier to read without changing its behavior. |
| [humanizer](humanizer/SKILL.md) | Revises prose that sounds generated while preserving its facts and intended voice. |
| [brag](brag/SKILL.md) | Turns a website or app into a short launch video with music, motion and share copy. |
| [excalidraw](excalidraw/SKILL.md) | Guides diagram design and uses the local Excalidraw MCP server to create and render diagrams. |
| [calendar](calendar/SKILL.md) | Places each commitment on the right calendar and keeps the schedule free of duplicates. |
| [wave](wave/SKILL.md) | Opens files, folders and websites, and manages blocks, tabs and workspaces inside Wave Terminal. |

## Memory

The memory system is [ai-memory](https://github.com/akitaonrails/ai-memory), self-hosted and shared by every agent in this setup. It keeps each project's wiki, sessions and observations in one store, so a session started in Claude Code can be continued in Codex or OpenCode. Lifecycle hooks capture the session as it runs; the skills below teach an agent how to read that memory, write to it and keep it tidy.

| Skill | What it does |
|---|---|
| [ai-memory-overview](ai-memory-overview/SKILL.md) | Explains the memory system and how a memory call picks a project. |
| [ai-memory-retrieval](ai-memory-retrieval/SKILL.md) | Finds prior context, decisions, rules and recent activity. |
| [ai-memory-handoff](ai-memory-handoff/SKILL.md) | Saves and resumes work between sessions and agents. |
| [ai-memory-durable-pages](ai-memory-durable-pages/SKILL.md) | Writes durable or time-limited knowledge on request. |
| [ai-memory-messaging](ai-memory-messaging/SKILL.md) | Sends messages between projects. |
| [ai-memory-learning-maintenance](ai-memory-learning-maintenance/SKILL.md) | Consolidates, lints and prunes captured memory. |
| [ai-memory-routing-install](ai-memory-routing-install/SKILL.md) | Installs or refreshes the ai-memory routing and skills. |

## Why it exists

I moved between Claude Code, Codex and OpenCode, and I expect to keep trying other tools and models. If GLM or DeepSeek becomes a better fit, I want to switch without rebuilding the instructions and workflows I rely on each day. The model, subscription and harness are choices I can change; this repository is what I take with me.

The same context reaches Pepper, my Hermes agent. When she delegates coding work to Codex, Codex uses these standards too. A project's own instructions can still add what is specific to that project.

## Philosophy

**One source, linked where I work.**  
The files live here. `make link` creates individual symlinks for `AGENTS.md` and the skills in my local agent directories (Claude Code, Codex and OpenCode). Edits to an existing skill reach those agents through the links; when I add a skill or set up a new machine, I run the command again.

**Keep my own copies.**  
I keep the skills I use in this repository and bring in upstream changes when I choose to. I can review their instructions before they reach an agent, so an upstream prompt change never enters my setup automatically.

**Work with the model.**  
As models get better, I get more from pairing with an LLM: watching its work, interrupting when it goes off course and adjusting together. A large specification driven development (SDD) pipeline can help on some tasks, but I do not need one for every task.

## References

- [Agent Skills specification](https://agentskills.io/specification)
- [Fábio Akita's my-skills repository](https://github.com/akitaonrails/my-skills)
- [Kent Beck coding style skill](https://github.com/nathankim0/clean-architecture-skills/tree/main/plugins/kent-beck-style/skills/kent-beck-style)
- [Fábio Akita's code simplification skill](https://github.com/akitaonrails/my-skills/tree/master/simplify), adapted from [Addy Osmani's original](https://github.com/addyosmani/agent-skills/tree/main/skills/code-simplification)
- [Humanizer writing skill](https://github.com/blader/humanizer)
- [Brag launch video skill](https://github.com/latent-spaces/brag/tree/main/skills/brag)
- [Excalidraw MCP server](https://github.com/yctimlin/mcp_excalidraw)
- [Excalidraw diagram design guidance](https://github.com/coleam00/excalidraw-diagram-skill)
