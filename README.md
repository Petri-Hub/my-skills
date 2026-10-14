# 🧩 my-skills

> My personal collection of skills for AI agent harnesses.

This repository is the shared home for skills I write for my own workflows. I keep each skill here once and make it available to the agent tools that can use it. The repository is public for reference, but the skills may depend on my setup and need adaptation elsewhere.

## Layout

Each skill gets a top-level directory with a `SKILL.md` entry point. Scripts, templates, and other supporting files live beside it. There are no skills here yet.

## Global context

The root `AGENTS.md` holds my shared context and guidelines for coding agents. On this machine, Codex reads it through `~/.codex/AGENTS.md`, which points to this repository.

## Across harnesses

Each harness can link to or install the skills it supports. Shared instructions live here; configuration specific to a harness stays with that harness.
