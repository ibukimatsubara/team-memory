#!/bin/bash
# Usage: run-codex.sh <condition A|B|C> <prompt 1-4> <run>
# A: skill only (.agents/skills) / B: skill + one line in AGENTS.md / C: neither
# LANG_SET=en uses the English fixture and prompts (default: ja).
set -u
E=$(cd "$(dirname "$0")" && pwd)
SKILL_SRC=${SKILL_SRC:-"$E/../../skills/team-memory"}
COND=$1 P=$2 N=$3
. "$E/prompts.sh"
OUT="$E/results/codex${TAG:-}/$COND-p$P-$N"
WORK=$(mktemp -d "${TMPDIR:-/tmp}"/pm-trigger-codex.XXXXXX)
cp -R "$FIXTURE/." "$WORK/"
if [ "$COND" != C ]; then
  mkdir -p "$WORK/.agents/skills"
  cp -R "$SKILL_SRC" "$WORK/.agents/skills/"
fi
if [ "$COND" = B ]; then
  printf "$NOTE" > "$WORK/AGENTS.md"
fi
(cd "$WORK" && git init -q && git add -A && git -c user.name=t -c user.email=t@example.com commit -qm init)
mkdir -p "$(dirname "$OUT")"
codex exec --json -s read-only --ephemeral -C "$WORK" "$PROMPT" < /dev/null > "$OUT.jsonl" 2> "$OUT.err"
echo "$OUT"
