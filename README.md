<h1 align="center">🧩 my-skills</h1>

<br>

<h3 align="center">The context and skills I carry between coding agents.<br>Who I am, where the work lives, and how I want it done</h3>

<p align="center">
  <a href="https://github.com/Petri-Hub/my-skills/commits/main"><img alt="Last commit" src="https://img.shields.io/github/last-commit/Petri-Hub/my-skills" /></a>
</p>

<br>

## About

> **TL;DR:** Models, subscriptions and coding agents change. This repository keeps the context and skills I carry between them: who I am, how I work and the workflows I use day to day. Symlinks let different agents share the same files.

<img width="1500" height="505" alt="The my-skills repository shares AGENTS.md and skills with Claude Code, Codex and other AI agents through symlinks." src="https://github.com/user-attachments/assets/30fca26a-0498-44a8-ab67-0aedab6a5ae4" />

## Skills

Each directory has a `SKILL.md` entry point and any files that skill needs.

| Skill | What it does |
|---|---|
| [style](style/SKILL.md) | Applies Kent Beck's simple design principles while writing, reviewing or refactoring code. |
| [simplify](simplify/SKILL.md) | Makes working code easier to read without changing its behavior. |
| [humanizer](humanizer/SKILL.md) | Revises prose that sounds generated while preserving its facts and intended voice. |
| [brag](brag/SKILL.md) | Turns a website or app into a short launch video with music, motion and share copy. |

## Why it exists

I moved between Claude Code and Codex, and I expect to keep trying other tools and models. If GLM or DeepSeek becomes a better fit, I want to switch without rebuilding the instructions and workflows I rely on each day. The model, subscription and harness are choices I can change; this repository is what I take with me.

The same context reaches Pepper, my Hermes agent. When she delegates coding work to Codex, Codex uses these standards too. A project's own instructions can still add what is specific to that project.

## Philosophy

**One source, linked where I work.**  
The files live here. `make link` creates individual symlinks for `AGENTS.md` and the skills in my local agent directories. Edits to an existing skill reach those agents through the links; when I add a skill or set up a new machine, I run the command again.

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
