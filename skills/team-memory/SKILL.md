---
name: team-memory
description: Reads and writes the team's shared work memory in the repo's .memory/ (decisions and their reasons, approaches tried and abandoned, measurements). In a repo that has .memory/, before starting investigation, design, implementation or a bug fix where past decisions or earlier attempts may matter, look at .memory/INDEX.md and open only the related memories. Do not read it for small work unrelated to past decisions, such as fixing a typo. Write a memory when a direction is decided, when an experiment is dropped, before opening a PR, and when asked to record something (e.g. "remember this", "記憶に残して"). Also use it to gather material for status meetings and reports.
---

# team-memory

Keep what was learned during work as Markdown in `.memory/` at the repo root. Memories go into PRs and through review, and every agent on the team (Claude Code, Codex) reads them. They are not synced with personal memory such as Claude Code's auto memory. Write here only what is worth sharing with the team.

Look for `.memory/` relative to the root of the repo being worked on. In a worktree, read and write the `.memory/` inside that worktree.

## Reading

Before work where past decisions or earlier attempts may matter, look at `.memory/INDEX.md`.

- Open only the files on lines related to the current work. Do not read everything. If no line is related, usually stop at the INDEX.
- When INDEX.md is a list of areas, open only the `INDEX.md` of the related area.
- When the work needs to confirm earlier history or whether something was tried before (for example, when the user asks), search with `grep -ril <keyword> .memory/` even if the INDEX shows nothing. Include `archive/`.
- Do not reread a memory already read in the same conversation.
- Do not read for work unrelated to past decisions, such as fixing typos or formatting, or updating dependencies.

Treat what you read as follows.

- A memory records facts as of when it was written. Before relying on it, check that its scope (input conditions, the version or code it applies to) still matches.
- When a memory and the current code disagree, the code wins. Tell the user about the mismatch.
- For a memory with `status: superseded`, read the memory linked at the top of its body.
- If the user proposes the same approach as a rejected memory, show that memory before starting. If its conditions for revisiting are met, say so and go ahead.

## Writing

### Whether to write

Decide by asking: "Does this change the next person's decisions, or save them from redoing work?" If nothing new was learned, do not write.

- Write: decisions and why, approaches tried and dropped and why, measurements, changed assumptions. This includes priorities and assumptions a PM decided, and options they set aside.
- Do not write: lists of changes, command output, a timeline of the work, ordinary passing tests, anything already covered by the README, specs or an issue (link to it instead).

Write when a direction is decided, when an experiment is dropped, before opening a PR, and when the user asks. If a dropped attempt never becomes a PR but is worth keeping, open a PR that contains only the memory.

### Language

Write memories in the language the existing memories in `.memory/` use. If there are none yet, use the language the user is working in. Do not mix languages within one `.memory/`.

Section headings and the INDEX title come in pairs. Treat both forms as the same when reading.

| English | Japanese |
|---|---|
| `Conclusion` | `結論` |
| `Evidence` | `根拠` |
| `History` | `経緯` |
| `Revisit when` | `再検討の条件` |
| `Internal notes` | `内部メモ` |
| `# Team memory` (INDEX title) | `# チームの記憶` |

Frontmatter keys and fixed values (`status: current`, `agent: codex` and so on) stay in English in every language. Free text such as `title` and the titles in `related` follows the memory's language.

### New file or update

Grow one file per topic (one judgement about one subject). When you edit an existing file, set `updated` to that day.

- Additional checks that support the same conclusion go into `Evidence`.
- When the direction changes (an earlier conclusion is overturned), do all four of these in the same PR:
  1. Rewrite `Conclusion` to the current direction, and update `title` and the INDEX line to match. Do not rename the file.
  2. Add one line to `History`: "YYYY-MM-DD: Previously X; changed to Z because Y." Make both the old conclusion and the reason clear.
  3. If the change affects repo documents such as the README, specs or design docs, fix those documents too.
  4. If another memory's `Conclusion` now contradicts the current direction, fix it as well.
- Only when merging into another file (including merging duplicates on the same topic), set the original to `status: superseded`, add one line at the top of its body linking to the merged file, and move it to `archive/`. Add one line to the merged file's `History` saying what was merged.
- Do not leave contradicting `current` memories side by side. If they hold under different conditions, write each one's conditions into its scope.

### Files

Name files `YYYY-MM-DD-<short-lowercase-english-name>.md`. The date is the day the memory was first written. Do not rename a file after creating it (moving it into an area folder or `archive/` is fine).

```markdown
---
title: Do not use a fixed threshold for binarization
author: <GitHub login>
date: 2026-10-20
status: current
agent: claude-code
related:
  - "#12 Improve circle symbol detection accuracy"
---

## Conclusion
Binarize scanned images with an adaptive threshold (blockSize 31, C 5). Do not use a fixed threshold.
Scope: the scanned images currently accepted. Photo input has not been evaluated.

## Evidence
- With a fixed threshold (128), circles broke up in faint drawings and text was detected as circles in dark ones.
- Recall: fixed 0.62, adaptive 0.81 (30 evaluation images, measured 2026-10-20, final). Speed difference: 4 ms per image.

## History
- 2026-10-20: First recorded.

## Revisit when
Preprocessing is added that evens out input darkness.

## Internal notes
(Internal names and background not to be shown to the client. Omit the heading if there are none.)
```

Frontmatter:

| Key | Required | How to write it |
|---|---|---|
| `title` | yes | A sentence that states the subject and the conclusion. It becomes the INDEX line |
| `author` | yes | GitHub login of the person who directed the work, so it matches the account used for commits in that repo. First, if `git config user.email` has the form `<digits>+<login>@users.noreply.github.com`, use that login. Otherwise use `gh config get -h github.com user` (no network needed), then `gh api user -q .login`. If none of these works, ask the user. Do not guess |
| `date` | yes | The day it was first written |
| `status` | yes | `current` or `superseded`. A "do not adopt" conclusion that still holds is `current` |
| `agent` | no | The agent that wrote it (`claude-code`, `codex`, ...) |
| `updated` | no | The day an existing file was edited. Only when edited |
| `related` | no | Related issues and PRs as "number title", e.g. `"#12 Improve circle symbol detection accuracy"` |

Body:

- Headings are `Conclusion`, `Evidence`, `History`, `Revisit when` and `Internal notes` (Japanese equivalents in the Language section). Except for `Conclusion`, omit a heading when there is nothing to put under it.
- `History` holds only the days the direction changed, with the previous conclusion and the reason, and notes on merging other memories. Do not write a timeline of the work.
- Write `Conclusion` in words that people outside the team would understand. Internal names, other projects, and background not meant for reports go only in `Internal notes`.
- For numbers, state the data used, the count, the measurement date, and whether it is final or provisional. If something is unknown, say so, e.g. "measurement date unknown".
- Keep observations, guesses and decisions apart. If the cause has not been isolated, say so.
- Do not write people's names anywhere in the body, including `Internal notes`. Only `author` identifies a person. Refer to others by role (e.g. "a reviewer").
- Put issue and PR numbers in `related`; in the body, refer to their content.
- Do not write "it was delayed"; write the cause and the expected date.
- Keep the body short. Aim for one screen.

### INDEX.md

List only `current` memories, one per line. The link text is the same as `title`, so the conclusion is visible.

```markdown
# Team memory

- [Do not use a fixed threshold for binarization](2026-10-20-fixed-threshold-rejected.md)
```

- Insert a new line in file-name order. Do not reorder or reformat other lines.
- Remove the lines of memories that became `superseded` or were moved to `archive/`.
- If `.memory/` does not exist, create INDEX.md with just the title (`# Team memory`, or `# チームの記憶` when writing in Japanese) when writing the first memory.
- If INDEX.md conflicts in a merge, keep the lines added on both sides. Then remove the lines of memories that became `superseded`.

### When memories grow

Being able to find things even when there are many memories comes first. Do not tidy up on a schedule.

- **Split by area**: when writing a memory makes the INDEX.md list more than 100 memories, move the memories into per-area folders right away (e.g. `.memory/detection/`) and create an `INDEX.md` in each folder. Do not postpone this. The top INDEX.md becomes a list of areas (one line per area: the link and a summary of the memories in it). When an area's INDEX also exceeds 100, split it the same way.
- **Move to archive**: memories that were merged and marked `superseded`, and memories whose code or feature no longer exists, go to `.memory/archive/` and off the INDEX. Do not read the archive normally; include it only when searching with grep.
- **Tidy up**: only when asked. Merge memories on the same topic into one, note the merge in the target's `History`, mark the originals `superseded` and move them to the archive.
- Splitting into areas and tidying up go in commits separate from code changes. Tidying up goes in a PR that contains only memories.

## Using memories as report material

When gathering memories for a status meeting or similar:

1. Narrow by period and by issue. For the period, look at `date` and `updated`, and also the date on each `History` line (`updated` is only the last edit, so this avoids missing changes in between). For the issue, look at `related`. For memories whose direction changed during the period, take the change and its reason from `History`.
2. Use `Conclusion` and `Evidence` in the material. Use `Internal notes` only to understand; do not copy them.
3. Do not put `author` or issue and PR numbers into material for people outside the team. When using provisional numbers, mark them as provisional.
4. Do not fill in and assert things the memories do not say. Ask the person making the material to confirm what is unclear.
