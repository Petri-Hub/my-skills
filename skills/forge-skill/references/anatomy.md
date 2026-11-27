# Anatomy of a skill

This file covers what each part of a skill is for, when it belongs and how to write it. The snippets come from different kinds of skills on purpose, so that no single one becomes the template.

## The folder

```text
skill-name/
├── SKILL.md       the skill itself, and the only file every agent loads
├── references/    depth the agent reads on demand
├── scripts/       code the agent runs instead of rewriting it
└── assets/        templates and files the agent copies into its output
```

Add a folder only when it has something in it:
- **`references/` holds depth:** API details, long catalogs, rationale too long for the body. Link each file from SKILL.md with a line saying when to read it.
- **`scripts/` holds repeated or enforced work:** code the agent would otherwise rewrite on every run, and checks for rules that must never bend. A check that fails is stronger than a sentence in capitals.
- **`assets/` holds things to copy or fill in:** templates, boilerplate, images.

## Frontmatter

Two fields are required. `name` is 1 to 64 lowercase letters, digits and hyphens, with no hyphen at either end and never two in a row, and it matches the folder name. `description` is at most 1,024 characters.

The description is all an agent sees when it decides whether to load the skill, so write it for that decision:
- Start with what the skill does, in the third person.
- Follow with "Use when…" and the phrases a user would actually say.
- Put the main use case first, because some agents shorten long descriptions.
- Leave out the workflow. An agent that reads a summary of the steps tends to follow the summary and skip the body.

**Bad:**

```yaml
description: A powerful skill that scans migrations, flags destructive operations, verifies rollbacks and writes a detailed report.
```

**Good:**

```yaml
description: Reviews database migrations for data loss and missing rollbacks before they run. Use when the user asks to check, review or approve a migration, or before running one on a shared database.
```

The bad one summarizes the workflow and never says when to use the skill. The good one gives the agent the phrases to match.
## Opening

The title, then two to four sentences with no heading of their own. A reader is more likely to finish this part than any other, so it carries the most: who the agent is, why the skill exists, and what good output looks like.

A role earns its place when it implies decisions. "A teacher writing for a student who missed the lecture" tells the agent what to explain and what to skip, while "an expert assistant" tells it nothing. Prefer a stance or a "think like" line to a list of adjectives.

```markdown
# Incident summary

You write the summary an on-call engineer reads at 3 a.m. on a phone. They need to know what's broken, who's affected and what to do first, so lead with impact and the next action, and keep the timeline for the end.
```

## When not to use

A short list of requests that look like this skill's work but belong somewhere else, each naming where they go. Include it when a neighbor is easy to confuse, and skip it otherwise, since the description already scopes the skill.

```markdown
## When not to use

- **Writing the postmortem:** the `postmortem` skill owns the full analysis; this summary is for the first hour.
- **Updating the public status page:** that text is for customers, so use the `status-page` skill.
```

## Workflow

Use a workflow when the work happens in an order that matters. Give each phase a numbered heading, a short paragraph with its goal and what to do, and a line saying when it's done. Keep the content at the level of intent, since the agent already knows how to open a file.

```markdown
### 2. Reproduce the bug

Make the failure happen on demand before changing any code, because a fix you can't trigger is a fix you can't verify. A failing test beats a list of manual steps.

You're done when one command shows the failure.
```

Work that repeats for each item, such as each version or each service, is one phase with a short numbered loop inside it and one done line for the whole pass. When a phase branches, show the branches as a short table or as separate subsections. For a phase where agents tend to go wrong, a few things to avoid, each with its reason, help more than extra steps.

## Principles or a ladder

Judgment work, such as reviewing, writing or designing, has no fixed order. Give it principles as a bold-title list, or a ladder of ordered questions where the agent takes the first answer that works.

```markdown
Take the first option that fully works:

1. Does the project already have a helper for this? Use it.
2. Does the standard library do it? Use that.
3. Does an installed dependency do it? Use that.
4. Otherwise, write the smallest code that works.
```

A ladder is easy to audit, because a person sees the order of preference at a glance and can argue with it.

## Constraints and guidelines

The rules that bite, as a bold-title list: what to do, then why in one clause. Put the rule with the worst failure first and the next worst last, because the middle of a list gets the least attention. Five to eight rules is plenty, and past that, look for rules the agent would follow anyway.

When two rules can collide, say in one of them which wins. Do the same when a rule can collide with the repository's own instructions.

```markdown
## Constraints and guidelines

- **Send the campaign to yourself first:** a send has no undo, and a broken template reaches every subscriber at once.
- **Keep the unsubscribe link in every template:** the email provider suspends accounts that send without one.
```

## Gotchas

Facts about the environment that defy reasonable assumptions, such as an API that returns 200 on failure or a setting read from two places. They're often the most valuable lines in a skill, because they're exactly what the agent can't guess. When the user has to correct the agent, the correction usually belongs here.

```markdown
## Gotchas

- **The status endpoint returns 200 during maintenance:** check the `state` field in the body instead of the HTTP code.
- **`config.local.yaml` silently overrides `config.yaml`:** read both before reporting a setting.
```

## Examples

A good and a bad example side by side, each labeled, with one line on why the good one wins. They're for rules where the line is hard to describe in words: tone, format, scope. One or two pairs per rule is enough, and their content should vary so the agent doesn't copy incidental details. [principles.md](principles.md) has the reasoning, and SKILL.md shows the format.

## Output

Describe the output only when its shape is fixed, such as a report format, a file layout or a message template. Give a short sample in a fenced block and say which parts are fixed and which vary. Without this section, the agent tends to copy the formatting of the skill itself.

````markdown
## Output

Start the reply with the verdict line, then one line per change that needs review:

```text
Safe to merge after 2 changes
- orders table: drops column legacy_status (data loss)
- users table: index built without CONCURRENTLY (locks writes)
```

The verdict line is fixed; list only changes that need review unless the user asks for all.
````

## Checklist

Four to eight things the agent confirms before it reports done, each checkable by reading the result. A checklist suits workflows. A judgment skill gets more from its examples.

## References

A table of every bundled file and when to read it. The "when" column is what matters: without it, the agent either reads everything up front or reads nothing.

```markdown
| File | Read it when |
|---|---|
| [references/api-errors.md](references/api-errors.md) | A call returns anything other than 200 |
| [scripts/lint_feed.py](scripts/lint_feed.py) | Before publishing the feed |
```
