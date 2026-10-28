# Measurement results

Raw logs (`*/results/`) are kept locally and not committed, because they contain information about the user's environment.

Sections 1 to 4 were measured on 2026-10-26 with the Japanese version of the skill, using Japanese prompts and a Japanese sample repo. Section 5 was measured on 2026-10-27 after the skill was translated into English.

## 1. Does the agent read `.memory/` before work? (`trigger-test/`)

In a small sample repo (`trigger-test/fixture/`: one detection source file and two memories), each run gave one request to a new session and asked for a plan without editing files.

- Conditions
  - A: skill only (description says "always read .memory/INDEX.md before work")
  - B: A plus one line in CLAUDE.md and AGENTS.md
  - C: neither skill nor note
- Requests
  - p1: proposes the same approach as a rejected memory ("I think switching to a fixed threshold would be faster")
  - p2: neutral ("I want to improve detection accuracy")
- Environments
  - minimal: `--setting-sources project,local` (does not load the user's skills or CLAUDE.md)
  - full: also loads user settings (hooks disabled only)
  - Codex: `codex exec -s read-only` (skill in `.agents/skills/`)
- Count: runs that read `.memory` / total runs

| | A skill only | B + one-line note | C none |
|---|---|---|---|
| Sonnet, minimal | 7/7 | 6/6 | 5/6 |
| Opus, minimal | 6/6 | 6/6 | **2/6** (p2: 0/3) |
| Sonnet, full | 6/6 | 6/6 | 4/6 |
| Opus, full | 12/12 | 6/6 | 6/6 |
| Codex | 5/5 | 4/4 | 4/4 |

Every run that read the memories mentioned their content (the reason for rejection, the numbers) in its answer.

### Findings

- With the skill installed, agents read the memories every time, without the one-line note (36/36). Adding the note did not increase reads.
- Claude usually read INDEX.md directly without invoking the Skill. The "always read before work" sentence in the description, which is always in context, appears to be what works. However, no condition removed only that sentence.
- Without the skill, reads were missed (Opus, minimal, neutral request: 0/3). Condition C reads more often in the full environment probably because the user's global settings describe a memory workflow (not verified).

### Limits

- The repo has few files, and `.memory/` is immediately visible in the root listing. Large repos and requests in the middle of a long conversation were not checked.
- SKILL.md was rewritten partway through the runs. The "always read before work" sentence in the description was not changed.

## 2. Writing and making reports (`behavior-test/`)

With the same layout as distribution (the skill in `.agents/skills/`, `.claude/skills/` as a symlink), Opus and Codex ran twice each.

For publication, the internal name and control numbers in the internal notes of `behavior-test/extra-memory.md`, and the content of one memory (2026-10-22) in `trigger-test/fixture/.memory/`, were replaced with fictional ones. The runs used different names, but with the same role (internal information that must not be copied into reports).

### Writing ("We tried Otsu's method but are not adopting it. Sato pointed it out. The issue is #12. Remember this.")

- Claude 2/2: wrote almost exactly per the rules. The second run, however, did not give a measurement date or say whether the numbers were final (the request did not give a date either). A sentence was added to the skill to say "unknown" when something is unknown.
  - File name, frontmatter, section structure, the one-line INDEX addition and the `related` format were all followed.
  - No personal names in the body; author was the GitHub login obtained through `gh`.
  - It noticed the existing memory (the evaluation set grew to 45 images) and stated the scope: "compared on 30 images; not measured on 45".
- Codex 0/2: did not write, and asked for the author's GitHub login instead.
  - The sandbox had no network, so `gh api user` failed. Per the skill's "ask if you cannot get it; do not guess", this was correct behavior.
  - Fix: the skill now tries `gh config get -h github.com user`, which needs no network, first. Confirmed that this command works from Codex's sandbox.

### Making a report ("Build this week's client status report section from .memory")

- Claude 2/2, Codex 2/2: none of the author, issue numbers, internal names, client control numbers or wording about delays appeared in the report.
- Provisional numbers were marked "provisional".
- Claude added, separately from the report, notes for the PM on "what was left out" and "points to confirm" (about memories without a measurement date or final/provisional status).

## 3. Comparison with the softened description (v2)

By the user's decision, the description was changed from "always read the INDEX before work" (v1) to the following (v2):

- For work where past decisions may matter, look at the INDEX before starting and open only related memories.
- Do not read for small unrelated work.

In the environment that loads user settings (full) and with Codex, two more requests were added for comparison:

- p3: unrelated request (look for typos in the README)
- p4: loosely related request (tune HoughCircles' minDist)

Each cell is "runs that read the INDEX / total runs", with "memory bodies opened, time" per run in parentheses. Time was not taken for Codex.

| | p1, p2 (related) | p3 (unrelated) | p4 (loosely related) |
|---|---|---|---|
| Opus v1 | 12/12 | 3/3 (0, 11 s) | 3/3 (2.0, 48 s) |
| Opus v2 | 6/6 | **0/3** (0, 11 s) | 3/3 (1.0, 39 s) |
| Sonnet v1 | 6/6 | 1/3 (0, 6 s) | 3/3 (2.0, 19 s) |
| Sonnet v2 | 6/6 | 1/3 (0, 6 s) | 3/3 (2.0, 16 s) |
| Codex v2 | 4/4 | 0/2 | 2/2 (1.5) |

### Findings

- With v2, agents still read the memories on every related request (16/16). Softening did not make them skip when it mattered.
- Reads of the INDEX on unrelated requests dropped (Opus from 3/3 to 0/3).
- On the loosely related request, Opus opened 1.0 bodies instead of 2.0.
- Time differences were small and within run-to-run variation. This sample repo has only two memories, so the cost of over-reading was small to begin with. The difference with many memories needs to be checked on a real project.

## 4. Many memories, and changes of direction (`scale-test/`)

After adding the following two rules to the skill, Opus and Codex ran twice each:

- When the direction changes, rewrite the conclusion in the same file and add to `History`
- When the INDEX exceeds 100 lines, split into per-area folders (the wording at the time; later changed to "100 memories", not counting headings)

| Scenario | What | Opus | Codex |
|---|---|---|---|
| read | In a `.memory/` with 6 areas x 40 = 240 memories, a request proposing the same approach as a rejected memory | 2/2. Top INDEX → `detection/INDEX.md` → the target memory. Only that one was opened in full | 2/2. Reached the target memory. Also opened the loosely related `eval/INDEX.md`, and saw excerpts from other areas through grep results |
| policy | "We added preprocessing, so we are going back to a fixed threshold. Recall 0.83." Asked to update the memory | 2/2. No new file; rewrote the conclusion, title and INDEX line, and added `History` and `updated`. Kept the old numbers in Evidence | 2/2. Same |
| split | With exactly 100 memories in the INDEX (102 lines with headings), add a finding on an existing topic (binarization) | 2/2. Appended to the existing memory, so there were still 100 memories. Did not split | 2/2. Updated the existing memory and split into 3 areas (it seems to have read 102 lines as "over 100 lines") |
| split2 | Same, adding a new topic (CSV encoding) | 0/2 with the first version of the skill: it added the memory and postponed splitting as "a separate PR". 2/2 after the wording was fixed: split into 3 areas right away, in a separate commit | 1/1. Split right away |

### Findings

- Following the split INDEX, the agent reached the target memory among 240. Opus opened only that one in full.
- A change of direction was expressed by rewriting the same file and appending to its history, without adding files.
- "100 lines" was read differently depending on whether headings count (Opus and Codex differed in split). It was changed to "100 memories", not counting headings.
- The first wording, "split into areas in a memory-only PR, not mixed with other changes", could be read two ways. Opus read it as "not even mixed with adding this memory" and postponed splitting. It was changed to "split right away when exceeded; put it in a commit separate from code changes".

### Limits

- The memories were machine-generated ("make method N the default" and so on), so they are easier to tell apart than real project memories.
- The INDEX length after splitting, and how much reading the split saved, were not measured.

## 5. After translating the skill into English (2026-10-27)

The skill text (SKILL.md and its description) was translated into English, and a rule was added: write memories in the language of the existing memories in `.memory/`, or the user's language when there are none, with paired English and Japanese headings. To check that Japanese teams are not affected and that English teams work, the read and write tests were re-run in both languages.

- Japanese: the original fixture (`trigger-test/fixture/`) and the original Japanese prompts, unchanged.
- English: `trigger-test/fixture-en/` (the same repo with English memories) and English versions of the same prompts. Select with `LANG_SET=en`.
- Environment: Ubuntu, Claude Code 2.1.311 with `--setting-sources project,local` (minimal), Codex CLI 0.164.0. Condition A (skill only) throughout.

### Reading (`trigger-test/`, condition A)

Runs that read the INDEX / total runs, with memory bodies opened per run in parentheses.

| | p1, p2 (related) | p3 (unrelated) | p4 (loosely related) |
|---|---|---|---|
| Opus, Japanese | 4/4 | 0/1 | 1/1 (1.0) |
| Opus, English | 4/4 | 0/1 | 1/1 (2.0) |
| Sonnet, Japanese | 4/4 | 0/1 | 1/1 (2.0) |
| Sonnet, English | 4/4 | 0/1 | 1/1 (0.0) |
| Codex, Japanese | 4/4 | 0/1 | 1/1 (1.0) |
| Codex, English | 4/4 | 0/1 | 1/1 (2.0) |

- On related requests, every agent read the memories in both languages (24/24), and every answer to p1 cited the rejection or its numbers.
- On the unrelated request (typo check), none read the INDEX (0/6).

### Writing and reports (`behavior-test/`)

Opus and Codex, once per language per scenario, with the same prompts as section 2 (English versions for the English fixture).

- Language: all four write runs wrote in the language of the existing memories. Japanese repos got `結論` / `根拠` headings and a Japanese title; English repos got `Conclusion` / `Evidence`. The INDEX line was added in the same language.
- Scope: all four noticed the memory about the 45-drawing evaluation set and stated that the comparison was on 30 drawings only.
- Unknowns: all four wrote that the measurement date and final/provisional status were not given.
- Names: in the first round, Codex (English) put the reviewer's name in `Internal notes`. The rule was changed from "no names in the body" to "no names anywhere in the body, including `Internal notes`; refer to people by role". In four re-runs (Codex English x2, Codex Japanese, Opus English), no names appeared.
- `related`: Codex wrote `"[#12] ..."` instead of `"#12 ..."` in 4 of 5 runs, including both re-runs after the example was added. The machine's global Codex instructions ask for issue references in the `[#N] title` form, which probably caused this (not verified). An example was added to the `related` row of the frontmatter table.
- Reports: in all four runs (Opus and Codex, both languages), the client control numbers, the internal model name, personal names, issue numbers and the internal note about the schedule slipping stayed out of the report. The provisional number was marked provisional. Opus again listed, outside the report, what it left out and what the PM should confirm.

### Language edge cases (`behavior-test/`, `first` scenario and `PROMPT_LANG`)

After the review, two conditions of the language rule were added to the script and run once each with Opus and Codex (8 runs):

- Request language differs from the existing memories (`LANG_SET=en PROMPT_LANG=ja` and the reverse, `write`): all 4 wrote in the language of the existing memories, not the request's. One Codex run kept the Japanese issue title from the request in `related` of an English memory.
- No `.memory/` yet (`first`, request in English or Japanese): all 4 created `.memory/` in the request's language, with the INDEX title `# Team memory` or `# チームの記憶` to match.
- No personal names appeared in any of the 8 runs.

### Limits

- One or two runs per cell. The scale tests in section 4 were not re-run; the rules they test were translated without changing their meaning.
- The English prompts are translations of the Japanese ones, and the English fixture is a translation of the Japanese one.
