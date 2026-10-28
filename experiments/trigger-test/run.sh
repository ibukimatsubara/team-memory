#!/bin/bash
# Usage: run.sh <condition A|B|C> <prompt 1-4> <run> <model>
# A: skill only / B: skill + one line in CLAUDE.md and AGENTS.md / C: neither
# LANG_SET=en uses the English fixture and prompts (default: ja).
set -u
E=$(cd "$(dirname "$0")" && pwd)
SKILL_SRC=${SKILL_SRC:-"$E/../../skills/team-memory"}
CLAUDE_BIN=${CLAUDE_BIN:-claude}
COND=$1 P=$2 N=$3 MODEL=$4
. "$E/prompts.sh"
# SOURCES=user,project,local includes the usual environment (user skills, CLAUDE.md, hooks)
SOURCES=${SOURCES:-project,local}
OUT="$E/results/$MODEL${SOURCES_TAG:-}${TAG:-}/$COND-p$P-$N"
WORK=$(mktemp -d "${TMPDIR:-/tmp}"/pm-trigger.XXXXXX)
cp -R "$FIXTURE/." "$WORK/"
if [ "$COND" != C ]; then
  mkdir -p "$WORK/.claude/skills"
  cp -R "$SKILL_SRC" "$WORK/.claude/skills/"
fi
if [ "$COND" = B ]; then
  printf "$NOTE" > "$WORK/CLAUDE.md"
  cp "$WORK/CLAUDE.md" "$WORK/AGENTS.md"
fi
(cd "$WORK" && git init -q && git add -A && git -c user.name=t -c user.email=t@example.com commit -qm init)
mkdir -p "$(dirname "$OUT")"
cd "$WORK" && "$CLAUDE_BIN" -p "$PROMPT" --model "$MODEL" \
  --setting-sources "$SOURCES" --settings '{"disableAllHooks": true}' --no-session-persistence \
  --permission-mode dontAsk --allowedTools Read Glob Grep Skill "Bash(ls:*)" "Bash(cat:*)" "Bash(git log:*)" \
  --output-format stream-json --verbose > "$OUT.jsonl" 2> "$OUT.err"
echo "$OUT"
