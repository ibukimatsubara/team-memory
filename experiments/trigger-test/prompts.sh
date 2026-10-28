# Sourced by run.sh and run-codex.sh. Sets FIXTURE, NOTE and PROMPT from LANG_SET (ja|en) and P.
# The Japanese prompts are the ones used for the original measurements; keep them unchanged.
LANG_SET=${LANG_SET:-ja}
if [ "$LANG_SET" = en ]; then
  FIXTURE="$E/fixture-en"
  NOTE='# symbol-detector\n\nBefore work, read `.memory/INDEX.md` and check related memories. Before opening a PR, write memories with the team-memory skill.\n'
  case $P in
    1) PROMPT='I think switching the binarization in src/detector.py to a simple fixed threshold would make it faster. Think about how to change it. Do not edit any files yet.' ;;
    2) PROMPT='I want to improve the accuracy of circle symbol detection in src/detector.py. Think about how to improve it. Do not edit any files yet.' ;;
    3) PROMPT='Check README.md for typos or inconsistent wording and point them out if any. Do not edit any files yet.' ;;
    4) PROMPT='I want to tune minDist of HoughCircles in src/detector.py so it picks up circles that are close together. Think about how to choose the value. Do not edit any files yet.' ;;
  esac
else
  FIXTURE="$E/fixture"
  NOTE='# symbol-detector\n\n作業前に `.memory/INDEX.md` を読み、関係する記憶を確認する。PR を作る前に team-memory スキルで記憶を書く。\n'
  case $P in
    1) PROMPT='src/detector.py の二値化を、固定しきい値の単純な方式に変えたら速くなると思う。変更方針を考えて。まだファイルは編集しないで。' ;;
    2) PROMPT='src/detector.py の丸記号の検出精度を上げたい。改善の方針を考えて。まだファイルは編集しないで。' ;;
    3) PROMPT='README.md に誤字や表記の揺れがないか見て、あれば指摘して。まだファイルは編集しないで。' ;;
    4) PROMPT='src/detector.py の HoughCircles の minDist を、近接した丸を拾えるように調整したい。値の決め方を考えて。まだファイルは編集しないで。' ;;
  esac
fi
