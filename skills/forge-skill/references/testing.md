# Testing a skill

A light test answers two questions: does the skill load when it should, and does the agent behave better with it than without it. It costs tokens and time, so offer it and run it only when the user agrees. It matters most for skills that load on their own. A skill the user always invokes by name can skip the trigger half.

## Does it trigger?

Write five prompts that should load the skill and five near misses that shouldn't. Near misses share words with the skill but belong to a neighbor or to no skill at all. Phrase every prompt the way the user really talks, including the vague ones.

Read each prompt next to the descriptions of the skill and its neighbors, and decide which one an agent would pick:
- **A should-trigger prompt loses:** the description is missing that phrasing.
- **A near miss wins:** the description is too broad, or the skill needs a "When not to use" line.

If the harness can start fresh sessions, run the prompts for real and see which skill loads.

| Prompt | Should trigger | Why |
|---|---|---|
| "write release notes for v2.3" | Yes | The main use case |
| "what changed since the last release?" | Yes | Same job, vaguer wording |
| "tag the v2.3 release" | No | Release work that the `release` skill owns |

## Does it help?

Pick two or three realistic tasks and run each one twice in a fresh context, once with the skill and once without it. Subagents work well where the harness has them: tell one to read the SKILL.md before starting, and give the other only the task.

Read the transcripts as well as the results, because the transcript shows whether the agent followed a rule, worked around it or never reached it. The comparison usually lands in one of these cases:
- **The baseline already gets it right:** the rule behind that behavior isn't needed, so cut it.
- **The skilled run ignores a rule:** the rule is unclear, buried mid-section or contradicted elsewhere. Fix its wording or position before adding emphasis.
- **Both runs fail the same way:** the skill is missing something the agent can't know. Add it as a rule with its reason, or as a gotcha.
- **The skilled run over-applies a rule:** the rule is too absolute or said twice. Give it a scope.

## Across agents

When the skill will run in more than one agent, such as Claude Code, Codex or OpenCode, repeat at least one task in a second agent. Models differ in how literally they read, and a rule one model applies sensibly another may apply everywhere.

## Reporting

Tell the user what you ran, what changed in the agent's behavior, and which edits you'd make. Keep no benchmark files unless the user asks for them; the skill and its git history are the record.
