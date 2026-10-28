# Petri — Global Agent Context

## Who you're working with

> Fernando Petri (Petri) is a Brazilian software engineer in the `America/Sao_Paulo` time zone. He has worked professionally since 2022, mainly on backend and platform systems, including financial software. His work spans service design, integrations, releases, infrastructure, and full-stack projects. He works with Java, Quarkus, Kubernetes, AWS, TypeScript, Next.js, Terraform, and Docker. He also builds tools with Python and MCP, maintains a homelab, and is completing a Computer Science degree at Faculdade de Americana (FAM).

## Desktop layout

Petri uses this layout on most computers:

| Folder | Purpose |
|---|---|
| `~/Desktop/Personal` | Personal work, projects, and related material. |
| `~/Desktop/Work` | General work. This folder may not exist on every computer. |
| `~/Desktop/Temporary` | Short-term work that needs to survive a reboot. |

## Storages

These are starting points for context. Use the storage relevant to the task, and read its own documentation before changing it.

| Storage | What it holds | When to read or write |
|---|---|---|
| [my-skills](https://github.com/Petri-Hub/my-skills) | Shared global agent context and reusable skills for coding agents. | Read for agent setup and skill workflows; write when updating shared instructions, skills, or their linking setup. |
| [pepper](https://github.com/Petri-Hub/pepper) | Public repository documenting Pepper, Petri's personal agent, and the choices behind her configuration. | Read to understand Pepper's setup; write when updating her documented behavior or configuration. |
| [lab](https://github.com/Petri-Hub/lab) | Configuration and infrastructure for Petri's homelab. | Read for homelab context; write when changing its infrastructure configuration. |
| [atlas](https://github.com/Petri-Hub/atlas) | Private workspace for Petri's career and professional life, including his background, goals, and plans. | Read for career or professional context; write when updating career plans, research, or materials. |
| [portfolio](https://github.com/Petri-Hub/portfolio) | Petri's personal website and portfolio. | Read for website or public profile context; write when changing the site. |
| [documents](https://github.com/Petri-Hub/documents) | Private archive of Petri's personal paperwork and company documents. | Read when a task involves stored documents; write when filing or updating them. |
| [notebook](https://github.com/Petri-Hub/notebook) | Public Obsidian wiki for technical knowledge and study notes. | Read for existing technical notes; write when adding or revising public notes. |
| [university-fam](https://github.com/Petri-Hub/university-fam) | Repository for projects, coursework, and study material from Petri's Computer Science degree at FAM. | Read for course or assignment context; write when adding or updating university work. |

## Skills to use

Use these skills whenever a request matches the description below, even when Petri does not name the skill or use a slash command. Read the installed skill before applying it.

| Skill | Use when | Reference |
|---|---|---|
| `/humanizer` | Asked to draft, rewrite, or polish blog posts, social posts, essays, or personal messages that should sound like the writer. Apply it as a final editing pass while preserving facts and the requested voice. | [blader/humanizer](https://github.com/blader/humanizer) |
| `/brag` | Asked to showcase a website or app with a short launch video, including requests to "brag about this" or share what was built. Read the project code, plan and render the video with Hyperframes, and write share copy. | [latent-spaces/brag](https://github.com/latent-spaces/brag/tree/main/skills/brag) |
| `/style` | Writing, changing, reviewing, or refactoring code. Apply Kent Beck's simple design and incremental improvement principles throughout the work. | [kent-beck-style](https://github.com/nathankim0/clean-architecture-skills/tree/main/plugins/kent-beck-style/skills/kent-beck-style) |
| `/simplify` | Asked to simplify code, or when recently changed code has avoidable complexity. Preserve behavior and stay within the task's scope. | [akitaonrails/my-skills](https://github.com/akitaonrails/my-skills/tree/master/simplify) |

## Memory

Long-term memory is [ai-memory](https://github.com/akitaonrails/ai-memory), self-hosted and shared by every coding agent here. It keeps each project's wiki, sessions and observations in one store, so work started in one harness can continue in another. Lifecycle hooks capture sessions as they run, and the `ai-memory-*` skills explain how to read that memory, write to it and keep it tidy. Use them whenever a task needs prior context, a handoff, or a note worth keeping.

## Constraints and Guidelines

- **Conventional commits.** Whenever you create a Git commit, use the Conventional Commits format. Choose a type that matches the change, add a scope when it clarifies the affected area, and write a concise summary of what changed. Apply this to every commit you make.
- **Follow the conversation language.** Reply in the language the user is using. If a conversation starts in Portuguese, continue in Portuguese unless the user switches languages or asks otherwise.
- **English for project material by default.** Write code, identifiers, comments, documentation, commit messages, pull request text, and other project material in English unless the user asks for another language or the task clearly calls for it, such as Portuguese university work. Preserve existing text you are not changing, and keep proper names and exact quotations as written.
