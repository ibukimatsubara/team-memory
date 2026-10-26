#!/bin/bash
# 使い方: run-codex.sh <条件 A|B|C> <プロンプト番号 1|2> <回>
# A: スキルだけ（.agents/skills）/ B: スキル + AGENTS.md の1行 / C: どちらもなし
set -u
E=$(cd "$(dirname "$0")" && pwd)
SKILL_SRC=${SKILL_SRC:-"$E/../../skills/team-memory"}
COND=$1 P=$2 N=$3
OUT="$E/results/codex${TAG:-}/$COND-p$P-$N"
WORK=$(mktemp -d "${TMPDIR:-/tmp}"/pm-trigger-codex.XXXXXX)
cp -R "$E/fixture/." "$WORK/"
if [ "$COND" != C ]; then
  mkdir -p "$WORK/.agents/skills"
  cp -R "$SKILL_SRC" "$WORK/.agents/skills/"
fi
if [ "$COND" = B ]; then
  printf '# symbol-detector\n\n作業前に `.memory/INDEX.md` を読み、関係する記憶を確認する。PR を作る前に team-memory スキルで記憶を書く。\n' > "$WORK/AGENTS.md"
fi
(cd "$WORK" && git init -q && git add -A && git -c user.name=t -c user.email=t@example.com commit -qm init)
case $P in
  1) PROMPT='src/detector.py の二値化を、固定しきい値の単純な方式に変えたら速くなると思う。変更方針を考えて。まだファイルは編集しないで。' ;;
  2) PROMPT='src/detector.py の丸記号の検出精度を上げたい。改善の方針を考えて。まだファイルは編集しないで。' ;;
  3) PROMPT='README.md に誤字や表記の揺れがないか見て、あれば指摘して。まだファイルは編集しないで。' ;;
  4) PROMPT='src/detector.py の HoughCircles の minDist を、近接した丸を拾えるように調整したい。値の決め方を考えて。まだファイルは編集しないで。' ;;
esac
mkdir -p "$(dirname "$OUT")"
codex exec --json -s read-only --ephemeral -C "$WORK" "$PROMPT" < /dev/null > "$OUT.jsonl" 2> "$OUT.err"
echo "$OUT"
