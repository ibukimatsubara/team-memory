#!/bin/bash
# 使い方: run.sh <シナリオ write|report> <エージェント claude|codex> <回>
# 配布時の配置（.agents/skills が正本、.claude/skills は symlink）で、書く・資料にする動作を確かめる。
set -u
E=$(cd "$(dirname "$0")" && pwd)
SCN=$1 AGENT=$2 N=$3
OUT="$E/results/$AGENT/$SCN-$N"
WORK=$(mktemp -d "${TMPDIR:-/tmp}"/pm-behavior.XXXXXX)
cp -R "$E/../trigger-test/fixture/." "$WORK/"
cp "$E/extra-memory.md" "$WORK/.memory/2026-10-24-eval-set-expanded.md"
printf -- '- [評価用の図面を30枚から45枚に増やした](2026-10-24-eval-set-expanded.md)\n' >> "$WORK/.memory/INDEX.md"
mkdir -p "$WORK/.agents/skills" "$WORK/.claude/skills"
cp -R "$E/../../skills/team-memory" "$WORK/.agents/skills/"
ln -s ../../.agents/skills/team-memory "$WORK/.claude/skills/team-memory"
(cd "$WORK" && git init -q && git add -A && git -c user.name=t -c user.email=t@example.com commit -qm init)
case $SCN in
  write) PROMPT='大津の方法（Otsu）での二値化を試した。評価用30枚で再現率 0.74 で、今の適応的しきい値の 0.81 より低かった。処理は1枚あたり 2ms 速い。今回は採用しない。佐藤さんがレビューで「濃い図面で文字を拾う」と指摘してくれた件で、Issue は #12 丸記号の検出精度の改善。これを記憶に残して。' ;;
  report) PROMPT='今週（2026-10-20〜10-26）の先方向け定例資料に載せる「記号検出の精度改善」の節を、.memory をもとに Markdown で作って。ファイルには書かず、返答に出して。' ;;
esac
mkdir -p "$(dirname "$OUT")"
if [ "$AGENT" = claude ]; then
  cd "$WORK" && /opt/homebrew/bin/claude -p "$PROMPT" --model opus \
    --setting-sources project,local --no-session-persistence \
    --permission-mode acceptEdits --allowedTools Read Glob Grep Skill Edit Write "Bash(gh api user:*)" "Bash(ls:*)" "Bash(git log:*)" "Bash(git status:*)" "Bash(date:*)" \
    --output-format stream-json --verbose > "$OUT.jsonl" 2> "$OUT.err"
else
  codex exec --json -s workspace-write --ephemeral -C "$WORK" "$PROMPT" < /dev/null > "$OUT.jsonl" 2> "$OUT.err"
fi
# 書いた結果を残す
mkdir -p "$OUT.memory" && cp -R "$WORK/.memory/." "$OUT.memory/"
(cd "$WORK" && git status --short) > "$OUT.status"
echo "$OUT"
