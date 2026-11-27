# Principles

These principles keep a skill working for the agent that runs it. Each one is a trade-off with a failure at both ends, so lean the way it suggests for the skill in front of you, and skip a principle that doesn't apply. When the skeleton and a principle seem to conflict, the skeleton decides which sections exist and the principles decide how each section is worded.

The checks at the end turn the principles into a read-back.

## Open with a role and a reason

Without a role, a skill reads as a bare list of commands, and the agent has nothing to fall back on when a case isn't covered. A grand persona fails the other way: studies of personas in system prompts found they don't make answers more accurate, so "world-class expert" adds words and nothing else. Lean toward two to four sentences: a stance the agent can act from, why the skill exists, and what good output looks like.

**Bad:**

```markdown
You are a world-class, highly skilled code review expert with decades of experience.
```

**Good:**

```markdown
Answer each support ticket as the person who gets the follow-up if the answer doesn't work. Lead with what the customer should do next, and explain only as much as they need to do it.
```

The good role implies decisions. It tells the agent what to put first and when to stop explaining, which the adjectives never do.

## Goal over procedure

A list of micro-steps gives false control: the agent reads the whole instruction for intent, turns mechanical when steps are spelled out, and breaks on cases the steps didn't anticipate. Current vendor guides say to describe the destination and let the model choose the path. A bare goal drifts, though, so it needs a way to tell when it's done and the boundaries it works within. Number the steps only where order matters, the work is fragile, or a mistake can't be undone, and give each of those steps its reason. Show branching as a table or as separate subsections instead of "if … otherwise …" chained through prose.

**Bad:**

```markdown
1. Open the file with the bug.
2. Find the function.
3. Read the function.
4. Change the function.
5. Run the tests.
```

**Good:**

```markdown
Fix the root cause in the shared function, rather than in the caller that exposed it. You're done when the failing case has a test and the full suite passes.
```

The good version says where the fix belongs and how to know it's finished. The steps describe what any agent does anyway.

## Reason as a clause

A bare rule gets dropped the moment the agent decides it doesn't apply, and a maintainer can't tell whether it still matters. A backstory has the opposite problem: it costs attention every time the skill loads. Lean toward one clause that names what breaks without the rule, and give reasons only to the rules that bite.

**Bad:**

```markdown
- Store timestamps in UTC.
```

**Good:**

```markdown
- **Store timestamps in UTC:** the reports run on servers in three time zones, and local times have already counted the same day twice.
```

With the reason, the agent applies the rule to a field it doesn't name, and a maintainer knows the rule can go if the reports ever run in one place.

## Write only what the agent can't see

Restating standard practice costs attention and buys nothing: one study found that repository context files didn't improve task success and raised cost by over 20%, and that overviews were the least useful part. Leaving out local facts fails the other way, because the agent has to guess. Lean toward the things the agent can't know: conventions, facts about the environment, preferences between valid options, traps. For each line, ask whether deleting it would change what the agent does.

**Bad:**

```markdown
Write a clear commit message. Use the imperative mood, keep the subject under 50 characters, and explain what and why in the body.
```

**Good:**

```markdown
Use Conventional Commits with the package folder as the scope, such as `fix(billing): …`.
```

The agent already writes reasonable commit messages. What it can't know is this repository's format.

## Show the shape with pairs

One example conveys a format better than paragraphs of rules, and a bad example next to it shows where the line is. Examples anchor hard, though: the agent copies their length, names and structure, including accidents. Learning research adds that a bad example helps only when someone explains what's wrong with it. Lean toward one or two labeled pairs for each subtle rule, a line saying why the good one wins, and varied content across pairs. For pure judgment calls, criteria often work better than examples.

**Bad:**

```markdown
Example error message: "Upload failed."
```

**Good:**

```markdown
**Bad:** "Error 413."

**Good:** "This file is 30 MB and the limit is 25 MB. Compress it or split it into two uploads."

The good message says what happened and what the user can do next.
```

A single unlabeled example leaves the agent guessing which of its features matter. The pair shows the contrast, and the line under it names it.

## Absolutes only for invariants

Capitals, stacked "must" and repeated warnings made up for older models that ignored instructions. Current models follow instructions literally, and both Anthropic and OpenAI now say this emphasis makes a rule fire where it shouldn't. Some rules really can't bend, though. Lean toward a plain "use this when" for anything that takes judgment. For a true invariant, let a script, hook or validator enforce it, and have the skill say so.

**Bad:**

```markdown
CRITICAL: You MUST ALWAYS run the linter before committing!!!
```

**Good:**

```markdown
Run `make lint` before you commit. The pre-commit hook rejects unlinted code, so running it first saves a round trip.
```

The good version is calmer and stronger: the hook enforces the rule, and the sentence tells the agent why it pays to follow it early.

## Say what to do, with its scope

"Don't do Y" makes the agent think about Y, and a long list of banned phrases can prime the very output it forbids. Some boundaries are real, so they still need saying. Lean toward stating the action. When a prohibition is needed, give it a scope and the alternative to take instead.

**Bad:**

```markdown
Never delete files.
```

**Good:**

```markdown
Ask before deleting any file you didn't create in this session.
```

The bad rule stops the agent from cleaning up its own temporary files and says nothing about what to do with the rest.

## Say it once, and say which rule wins

Repeating a rule to make it stick makes it fire too often: OpenAI found that repeating "ask first" made its models ask for approval they didn't need. Contradictions are worse. Models notice conflicting instructions but rarely say so, and they resolve them differently from one run to the next. Lean toward each rule living in one place, and where two rules can collide, write down which one wins.

**Bad:**

```markdown
- Keep replies short.
- Explain every change in detail.
```

**Good:**

```markdown
- **Keep replies short:** the user reads them between other work. When a change deletes data or touches security, explain it in full; that case wins over brevity.
```

The bad pair leaves the agent to pick a rule on each run. The good version settles it once.

## Point instead of pasting

Inlining keeps a skill self-contained. A body that grows with the work, though, becomes unusable exactly when the work is largest, and copied facts go stale without anyone noticing. Lean toward inlining what's bounded and pointing at what isn't: depth goes in `references/`, one level deep, each file with a line saying when to read it, and canonical docs are linked instead of copied. The same goes for what the skill asks the agent to report: a count, a status or a path, rather than every item.

**Bad:**

```markdown
## Error codes

| Code | Meaning | What to do |
|---|---|---|
| 1001 | Token expired | Refresh and retry |
| 1002 | ... (and 80 more rows)
```

**Good:**

```markdown
When a call fails, look up its code in [references/errors.md](references/errors.md).
```

The table costs attention on every run, while it matters only on the runs that fail.

## Review checks

Read the draft from disk, and tick a check only when it holds:

- [ ] The opening gives a role the agent can act from and says why the skill exists.
- [ ] Each numbered step is there because order, fragility or risk demands it.
- [ ] Each rule that matters carries its reason, in one clause.
- [ ] Deleting any line would change what the agent does.
- [ ] Each subtle rule has a labeled pair with a line on why, and the pairs vary.
- [ ] No rule is in capitals, stacked with "must", or said twice.
- [ ] Every prohibition is scoped and names what to do instead.
- [ ] Where two rules can collide, one says which wins.
- [ ] Anything that grows with the work is a pointer, not pasted.

## Sources

- [Demiurge forge-principles](https://github.com/Petri-Hub/demiurge/blob/main/skills/forge-principles/SKILL.md), where most of these principles started.
- [Ponytail](https://github.com/DietrichGebert/ponytail), the model for the short, stance-first style.
- [Claude prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices) and [skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices), Anthropic.
- [Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents), Anthropic.
- [Prompt guidance for GPT-5.6](https://developers.openai.com/api/docs/guides/prompt-guidance-gpt-5p6), OpenAI.
- [How many instructions can LLMs follow at once?](https://arxiv.org/abs/2507.11538), Jaroslawicz et al., 2025.
- [Personas in system prompts do not improve performance](https://arxiv.org/abs/2311.10054), Zheng et al., 2024.
- [Evaluating AGENTS.md](https://arxiv.org/abs/2602.11988), Gloaguen et al., 2026.
- [Learning through case comparisons](https://doi.org/10.1080/00461520.2013.775712), Alfieri et al., 2013.
