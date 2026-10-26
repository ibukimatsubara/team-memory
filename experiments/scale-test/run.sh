#!/bin/bash
# 使い方: run.sh <シナリオ read|policy|split> <エージェント claude|codex> <回> [モデル]
# read:   240件を分野に分けた .memory/ で、関係する分野と記憶だけを開くか
# policy: 方針転換を頼んだとき、同じファイルの結論を書き換えて経緯を足すか
# split:  INDEX がちょうど100行のときに1件書き足すと、分野に分けるか（既存テーマへの追記になる依頼）
# split2: 同じく、新しいテーマを書き足す依頼
set -u
E=$(cd "$(dirname "$0")" && pwd)
SCN=$1 AGENT=$2 N=$3 MODEL=${4:-opus}
TAG=$AGENT
[ "$AGENT" = claude ] && TAG=$MODEL
OUT="$E/results/$TAG/$SCN-$N"
WORK=$(mktemp -d "${TMPDIR:-/tmp}"/tm-scale.XXXXXX)
case $SCN in
  read) python3 "$E/make_fixture.py" "$WORK/repo" split >/dev/null ;;
  split|split2) python3 "$E/make_fixture.py" "$WORK/repo" flat100 >/dev/null ;;
  policy) cp -R "$E/../trigger-test/fixture" "$WORK/repo" ;;
esac
R="$WORK/repo"
mkdir -p "$R/.agents/skills" "$R/.claude/skills"
cp -R "$E/../../skills/team-memory" "$R/.agents/skills/"
ln -s ../../.agents/skills/team-memory "$R/.claude/skills/team-memory"
(cd "$R" && git init -q && git add -A && git -c user.name=t -c user.email=t@example.com commit -qm init)
case $SCN in
  read) PROMPT='src/detector.py の二値化を、固定しきい値の単純な方式に変えたら速くなると思う。変更方針を考えて。まだファイルは編集しないで。' ;;
  policy) PROMPT='前処理で図面の濃さをそろえるようにしたので、二値化は固定しきい値（140）に戻すことにした。評価用30枚で再現率 0.83、適応的しきい値は 0.81 だった。記憶を更新して。コードはまだ直さなくていい。' ;;
  split2) PROMPT='CSV 出力の文字コードは、先方の Excel でそのまま開けるように UTF-8（BOM 付き）にすると決めた。BOM なしだと文字化けした。これを記憶に残して。' ;;
  split) PROMPT='大津の方法（Otsu）での二値化を試した。評価用30枚で再現率 0.74 で、今の適応的しきい値の 0.81 より低かったので採用しない。これを記憶に残して。' ;;
esac
mkdir -p "$(dirname "$OUT")"
if [ "$AGENT" = claude ]; then
  (cd "$R" && /opt/homebrew/bin/claude -p "$PROMPT" --model "$MODEL" \
    --setting-sources project,local --settings '{"disableAllHooks": true}' --no-session-persistence \
    --permission-mode bypassPermissions --output-format stream-json --verbose > "$OUT.jsonl" 2> "$OUT.err")
else
  codex exec --json -s workspace-write --ephemeral -C "$R" "$PROMPT" < /dev/null > "$OUT.jsonl" 2> "$OUT.err"
fi
(cd "$R" && git add -A && git status --short) > "$OUT.status"
(cd "$R" && git diff --cached -- .memory) > "$OUT.diff"
rm -rf "$OUT.memory" && cp -R "$R/.memory" "$OUT.memory"
echo "$OUT"
