# team-memory design notes

## Purpose

When several people and several agents work on the same repo, keep what Claude or Codex learns during work (decisions, reasons, approaches tried and dropped, measurements) inside the repo and share it.
Memories go through review as part of PRs, so that another person's agent (for example, the PM's Claude) can read them and use them as material for status meetings and client reports.

## Background

- CLAUDE.md / AGENTS.md are shared through Git, but they are for rules and procedures, not for the history of trial and error.
- Claude Code's auto memory is per repo but local to one machine, and invisible to other members.
- Prior art (`discussion/01-prior-art.md`, not published): ccmemo, TeamBrain, Cline Memory Bank, ADR, memlay. Most make agents read memories through hooks, MCP or always-on instructions. We found none that works with a skill alone.

## Decisions

| Item | Decision | Reason |
|---|---|---|
| Distribution | One skill (`skills/team-memory/SKILL.md`) | Agreed with the user |
| Location | `.memory/` at the repo root. `INDEX.md` plus one file per topic | Agreed with the user |
| How to make agents read before work | The skill's description says: "for work where past decisions may matter, look at the INDEX before starting and open only related memories; do not read for small unrelated work". Adding to CLAUDE.md / AGENTS.md is not required | Measured (`experiments/RESULTS.md`). The description is always in context. "Always read" was softened because the user did not want over-reading to slow work down |
| Layout in the target repo | With the skills CLI or by hand, the skill lives in `.agents/skills/team-memory/` and `.claude/skills/team-memory` is a symlink. Teams using only Claude Code can also use the plugin marketplace (`--scope project`) | Codex looks in `.agents/skills`, Claude Code in `.claude/skills`. The symlink was confirmed to work on a real machine |
| File name | `YYYY-MM-DD-<slug>.md`. The date is the first day. Never renamed | Codex's proposal. Sequence numbers collide in parallel PRs (a weakness of ADRs) |
| Frontmatter | Required: title / author / date / status. Optional: agent / updated / related | Between the PM's proposal (5 keys) and Codex's (agent required). agent is optional because the PM does not use it |
| author | GitHub login of the person who directed the work. Taken from the repo's git email (GitHub noreply form); otherwise `gh config get -h github.com user` or `gh api user`; ask if none works | The user's proposal, following the PM's (the person who directed, not the agent). Even people who switch between two accounts get the same account as their commits in that repo |
| Body | Conclusion / Evidence / History / Revisit when / Internal notes. All but Conclusion are optional | The PM's proposal (conclusion in words for outsiders, internal notes kept apart) and Codex's (scope, conditions for revisiting) |
| Language | The skill text is in English. Memories are written in the language of the existing memories in `.memory/`, or, when there are none, the language of the person working. Headings and the INDEX title have English and Japanese forms that are read as the same. Frontmatter stays in English | Decided 2026-10-27 to make the skill usable for English-speaking teams (issue #1). Teams already writing Japanese memories keep working without rewriting them. Re-measured after the translation (`experiments/RESULTS.md` section 5) |
| Additional checks | If the conclusion is the same, append to the existing file and set `updated`, so filtering by period does not miss them | Codex review |
| When the conclusion changes | Rewrite the conclusion in the same file and add one line to `History` with the date, the previous conclusion and the reason. Fix related repo documents and other memories in the same PR. Use superseded only when merging into another file (including merging duplicates on the same topic) | The user's decision (10/26). It first followed ADRs: "new file, mark the old one superseded, never rewrite the old conclusion". Changed so that a change of direction is easy to reflect in both memories and documents, and files do not pile up |
| INDEX | Only current memories, one line each. Insert in file-name order, no reformatting. On conflicts, keep both sides' lines | Codex's proposal. No automatic merge settings or generation |
| What to write | "Does it change the next person's decisions, or save them from redoing work?" Nothing new learned, nothing written | Codex's proposal |
| Dropped attempts | Kept in a memory-only PR | Codex's proposal |
| As memories grow | Finding things even with many memories comes first. When the INDEX lists more than 100 memories, split into area folders right away and turn the top INDEX into a list of areas. Merged memories and those whose subject is gone go to `archive/`. If the INDEX does not show it, grep. Tidy up only when asked, in a memory-only PR | The user's decision (10/26). Putting a "last tidied" date in the INDEX was rejected because concurrent tidying would conflict. 100 is a guide: one INDEX line is about 50 tokens, so about 5k tokens per read |
| Client material | Use Conclusion and Evidence. Do not copy internal notes, author or numbers. Provisional values are used, marked as provisional | The PM's proposal |

## What we left out

- Injecting the INDEX through a SessionStart hook: measurements showed the skill's description is enough. It would also only work for Claude, not Codex.
- Generating the INDEX automatically, `merge=union`: not needed while conflicts are small enough to resolve by hand.
- A field such as `shareable` for whether something may be shown outside: writers easily get it wrong (PM's view).
- Scheduled tidying and recording the last tidy date: concurrent tidying conflicts. Tidying on request, splitting into areas, archive and grep are enough.

## Open questions

- Measurements are from a small sample repo. Whether agents read memories in a large repo, or in the middle of a long conversation, needs to be checked on a real project.
- Which project to try it on first.
