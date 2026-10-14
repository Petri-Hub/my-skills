<h1 align="center">🧩 my-skills</h1>

<br>

<h3 align="center">The context and skills I carry between coding agents.<br>Who I am, where the work lives, and how I want it done</h3>

<p align="center">
  <a href="https://github.com/Petri-Hub/my-skills/commits/main"><img alt="Last commit" src="https://img.shields.io/github/last-commit/Petri-Hub/my-skills" /></a>
</p>

<br>

## About

> **TL;DR:** My global [`AGENTS.md`](AGENTS.md) tells agents who I am, where my work lives and how I want them to work. The folders here hold skills for coding, editing prose, simplifying code and making launch videos. Each skill's original source is linked below.

## Why it exists

I use agents in different projects and want them to start with the same basic context. `AGENTS.md` carries the facts and rules that follow me between repositories. A project's own instructions can add what is specific to that project.

Skills carry the longer workflows. An agent loads the relevant skill when the request calls for it, including when I describe the work in plain language instead of typing a slash command.

## Skills

Each directory has a `SKILL.md` entry point and any files that skill needs.

| Skill | What it does | Source |
|---|---|---|
| [style](style/SKILL.md) | Applies Kent Beck's simple design principles while writing, reviewing or refactoring code. | [kent-beck-style](https://github.com/nathankim0/clean-architecture-skills/tree/main/plugins/kent-beck-style/skills/kent-beck-style) |
| [simplify](simplify/SKILL.md) | Makes working code easier to read without changing its behavior. | [Fábio Akita's adaptation](https://github.com/akitaonrails/my-skills/tree/master/simplify) of [Addy Osmani's skill](https://github.com/addyosmani/agent-skills/tree/main/skills/code-simplification) |
| [humanizer](humanizer/SKILL.md) | Revises prose that sounds generated while preserving its facts and intended voice. | [blader/humanizer](https://github.com/blader/humanizer) |
| [brag](brag/SKILL.md) | Turns a website or app into a short launch video with music, motion and share copy. | [latent-spaces/brag](https://github.com/latent-spaces/brag/tree/main/skills/brag) |

The [skill registry in `AGENTS.md`](AGENTS.md#skills-to-use) says when agents should use each one. The `SKILL.md` files hold the actual workflows.

## How it is used

On my current machine, Codex reads `AGENTS.md` through `~/.codex/AGENTS.md`, a symlink to this repository. The four skills in `~/.codex/skills` are still separate copies, so changes here need to be copied there before Codex sees them.

For a shared setup across harnesses, each harness can keep its own skills directory and link individual skill folders from this repository into it. Built-in and plugin skills can stay alongside those links. This repository does not install or update skills automatically.

## Decisions

**Keep global context short.** `AGENTS.md` covers my background, storage map, skill triggers and rules that apply across projects. Detailed procedures belong in skills or project repositories.

**Make triggers explicit.** A request to write code should pick up `style`; a request to draft prose should get a `humanizer` pass. The request does not need to name the skill.

**Keep upstream visible.** These are vendored skills. Changes from their source repositories are reviewed and copied in deliberately, with the local adaptations and credits kept in view.

## Sources and licenses

`brag`, `humanizer` and `style` include their upstream MIT notices. `style` is the Kent Beck skill renamed for this workflow, with a broader coding trigger. `simplify` comes from Akita's adaptation of Addy Osmani's skill; Addy's MIT notice is included with the original material in [`simplify/`](simplify/README.md).

The music bundled with `brag` is credited in its [music README](brag/assets/music/README.md) under CC BY 4.0. Its [audio reference](brag/references/audio.md) records the sound effect sources.
