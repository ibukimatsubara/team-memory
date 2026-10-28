#!/bin/bash
# Usage: run.sh <scenario write|report|first> <agent claude|codex> <run>
# Checks writing and report-making with the distributed layout (.agents/skills is the source, .claude/skills is a symlink).
# first: same request as write, in a repo with no .memory/ yet.
# LANG_SET=en uses the English fixture (default: ja). PROMPT_LANG picks the request language (default: LANG_SET).
set -u
E=$(cd "$(dirname "$0")" && pwd)
CLAUDE_BIN=${CLAUDE_BIN:-claude}
SCN=$1 AGENT=$2 N=$3
LANG_SET=${LANG_SET:-ja}
PROMPT_LANG=${PROMPT_LANG:-$LANG_SET}
OUT="$E/results/$AGENT${TAG:-}/$SCN-$N"
WORK=$(mktemp -d "${TMPDIR:-/tmp}"/pm-behavior.XXXXXX)
if [ "$LANG_SET" = en ]; then
  cp -R "$E/../trigger-test/fixture-en/." "$WORK/"
  cp "$E/extra-memory-en.md" "$WORK/.memory/2026-10-24-eval-set-expanded.md"
  printf -- '- [Evaluation set expanded from 30 to 45 drawings](2026-10-24-eval-set-expanded.md)\n' >> "$WORK/.memory/INDEX.md"
else
  cp -R "$E/../trigger-test/fixture/." "$WORK/"
  cp "$E/extra-memory.md" "$WORK/.memory/2026-10-24-eval-set-expanded.md"
  printf -- '- [評価用の図面を30枚から45枚に増やした](2026-10-24-eval-set-expanded.md)\n' >> "$WORK/.memory/INDEX.md"
fi
[ "$SCN" = first ] && rm -rf "$WORK/.memory"
if [ "$PROMPT_LANG" = en ]; then
  case $SCN in
    write|first) PROMPT="We tried binarizing with Otsu's method. On the 30 evaluation images recall was 0.74, lower than the current adaptive threshold's 0.81. It is 2 ms faster per image. We are not adopting it this time. Sato pointed out in review that it picks up text in dark drawings, and the issue is #12 Improve circle symbol detection accuracy. Remember this." ;;
    report) PROMPT='Using .memory, write the "Symbol detection accuracy" section for this week'"'"'s (2026-10-20 to 10-26) status report to the client, in Markdown. Do not write it to a file; put it in your reply.' ;;
  esac
else
  case $SCN in
    write|first) PROMPT='大津の方法（Otsu）での二値化を試した。評価用30枚で再現率 0.74 で、今の適応的しきい値の 0.81 より低かった。処理は1枚あたり 2ms 速い。今回は採用しない。佐藤さんがレビューで「濃い図面で文字を拾う」と指摘してくれた件で、Issue は #12 丸記号の検出精度の改善。これを記憶に残して。' ;;
    report) PROMPT='今週（2026-10-20〜10-26）の先方向け定例資料に載せる「記号検出の精度改善」の節を、.memory をもとに Markdown で作って。ファイルには書かず、返答に出して。' ;;
  esac
fi
mkdir -p "$WORK/.agents/skills" "$WORK/.claude/skills"
cp -R "$E/../../skills/team-memory" "$WORK/.agents/skills/"
ln -s ../../.agents/skills/team-memory "$WORK/.claude/skills/team-memory"
(cd "$WORK" && git init -q && git add -A && git -c user.name=t -c user.email=t@example.com commit -qm init)
mkdir -p "$(dirname "$OUT")"
if [ "$AGENT" = claude ]; then
  cd "$WORK" && "$CLAUDE_BIN" -p "$PROMPT" --model opus \
    --setting-sources project,local --no-session-persistence \
    --permission-mode acceptEdits --allowedTools Read Glob Grep Skill Edit Write "Bash(gh api user:*)" "Bash(gh config get:*)" "Bash(git config:*)" "Bash(ls:*)" "Bash(git log:*)" "Bash(git status:*)" "Bash(date:*)" \
    --output-format stream-json --verbose > "$OUT.jsonl" 2> "$OUT.err"
else
  codex exec --json -s workspace-write --ephemeral -C "$WORK" "$PROMPT" < /dev/null > "$OUT.jsonl" 2> "$OUT.err"
fi
# Keep what was written
mkdir -p "$OUT.memory" && { [ -d "$WORK/.memory" ] && cp -R "$WORK/.memory/." "$OUT.memory/"; true; }
(cd "$WORK" && git status --short) > "$OUT.status"
echo "$OUT"
