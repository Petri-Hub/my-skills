# Writing style

This file covers how a skill should look and sound, so that a person can read it in one sitting and find any rule by scanning. The agent benefits too, because clear structure helps it find what applies.

## Headings

Use sentence case, plain text, no bold and no emoji. A heading names everything in its section and nothing else, so someone reading only the headings gets the outline. Number headings only when the sections are steps.

## Paragraphs

Put the most important sentence first, so a reader who stops there still gets the point. Keep paragraphs to a few sentences, and sentences under about 25 words. Use one term for each concept: if it's a "phase" in one section, it's still a "phase" in the next.

## Lists

Introduce each list with a sentence that says what it holds. Number a list when order matters, and use bullets when it doesn't.

Lead with a bold title when the items are parallel and a reader will scan or look them up, such as rules, checks, modes or options. The title states the point and ends with a colon, and the sentence after it adds the reason or the detail. When the titles would only repeat their sentences, drop the bold and write a plain list or a paragraph.

**Bad:**

```markdown
- **Important:** Run the tests before you commit.
- **Note:** The tests take a while.
```

**Good:**

```markdown
- **Commit only on green tests:** a red commit blocks everyone's merges until it's fixed.
- **Run the fast suite while you work:** `make test-fast` takes seconds, and the full suite takes twenty minutes.
```

"Important" and "Note" tell a scanning reader nothing. The good titles are the rules themselves.

## Tables

Use a table to compare several items across the same attributes. Two items with one attribute read better as a sentence. Keep cells short, and move anything that needs a paragraph into prose below the table.

## Code

Fence what the agent must reproduce exactly: commands, templates, file contents, output formats. Give every fence a language, and use inline code for names, paths, flags and values. Describe a procedure in prose rather than pseudo-code, because a fenced block reads as "copy this" and the agent will.

**Bad:**

```text
1) check DEPLOY_ENV
2) if set -> make deploy
3) else -> abort
```

**Good:**

```markdown
Check that `DEPLOY_ENV` is set, then run `make deploy`. If it isn't set, stop and tell the user, because the script falls back to production.
```

The prose version is shorter to read and carries the reason, which the pseudo-code had no room for.

Link to the canonical docs or to a `references/` file instead of pasting long snippets, since copied API details go stale without anyone noticing.

## Emphasis

Bold belongs on list titles, on the Bad and Good labels of an example pair, and on a term at the point where it's defined. Inside running prose, bold loses its effect after the second use, so write the sentence more clearly instead of making it louder.

## Punctuation

Use commas, semicolons, colons, periods and parentheses, and leave out em dashes, because a text full of them reads as generated. Skip exclamation marks too.

## Habits that mark text as generated

These patterns make readers skim and distrust a text. Each one is a symptom of vague writing, so fix the thought behind it as well as the words. If the humanizer skill is installed, its review catches more.

| Habit | Looks like | Fix |
|---|---|---|
| Inflated words | robust, seamless, leverage, crucial, delve, empower | Use the plain word, or cut it |
| Contrast for drama | "not just fast, but reliable" | Say the one thing that's true |
| Padded threes | "clear, concise and compelling" | Keep only the items that carry meaning |
| Staged openers | "Here's the thing:", "Let's dive in" | Start with the point |
| Summary closers | "In summary…", "Overall, this ensures…" | End when the content ends |
| Stacked hedges | "may potentially help to" | Say what it does |
| Bold everywhere | a **key** idea in **every** line | Bold only list titles and defined terms |
| Title case | "Running The Test Suite" | "Running the test suite" |
| Emoji in headings | "## 🚀 Setup" | "## Setup" |

## Length

Aim for about 150 lines in SKILL.md, with 500 as the ceiling. When a skill runs long, cut in this order and stop once it reads in one sitting:

1. What the agent already knows, such as how to write a commit message or use a common CLI.
2. Rules said twice, and emphasis piled onto a rule.
3. Structure that doesn't help anyone find anything.
4. Depth that can move to `references/`.
5. Examples that don't change behavior.

Stop before the opening, the reasons and the examples behind subtle rules; SKILL.md says why they stay.

## Formatting bleed

A skill heavy with headers, bold and bullets teaches the agent to answer the same way. When the output's shape matters, describe it in an Output section with a short sample, so the agent formats its reply on purpose instead of by imitation.

## Review checks

Read the draft from disk as someone who has never seen this conversation, and tick a check only when it holds:

- [ ] The headings alone give the outline, in sentence case and without bold.
- [ ] Each paragraph leads with its main point.
- [ ] Every bold title states a rule or a point, and its sentence adds to it.
- [ ] Running prose has no bold.
- [ ] Each fenced block holds literal text the agent must reproduce.
- [ ] Every concept keeps the same term throughout.
- [ ] The text has no em dashes and none of the habits in the table above.
- [ ] A maintainer could read the whole skill in one sitting and say why each rule exists.

## Sources

- [Text scanning patterns](https://www.nngroup.com/articles/text-scanning-patterns-eyetracking/), Nielsen Norman Group.
- [Excessive bold](https://martinfowler.com/bliki/ExcessiveBold.html), Martin Fowler.
- [Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing), Wikipedia.
- [The evidence for plain language](https://gds.blog.gov.uk/2014/02/17/guest-post-clarity-is-king-the-evidence-that-reveals-the-desperate-need-to-re-think-the-way-we-write/), Government Digital Service.
