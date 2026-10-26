# team-memory 設計メモ

## 目的

複数人・複数エージェントで同じ repo を触るとき、Claude や Codex が作業中に得た知見（決定・理由・試して捨てた方法・計測値）を、repo の中に残して共有する。
PR に含めてレビューを通し、別の人のエージェント（例: PM の Claude）が読んで、定例資料や先方共有資料の材料にできるようにする。

## 背景

- CLAUDE.md / AGENTS.md は Git で共有されるが、規約・手順向けで、試行錯誤の経緯を置く場所ではない。
- Claude Code の auto memory は repo 単位だがマシンローカルで、他のメンバーには見えない。
- 先行事例（`discussion/01-prior-art.md`）: ccmemo・TeamBrain・Cline Memory Bank・ADR・memlay。読む側は hook・MCP・常時指示で補う例が多く、スキルだけで完結するものは見つからなかった。

## 決めたこと

| 項目 | 決定 | 根拠 |
|---|---|---|
| 配布 | スキル1つ（`skills/team-memory/SKILL.md`） | ユーザー合意 |
| 置き場所 | repo ルートの `.memory/`。`INDEX.md` と1トピック1ファイル | ユーザー合意 |
| 作業前に読ませる方法 | スキルの description に「過去の判断が関係しそうな作業では着手前に INDEX を見て、関係する記憶だけ開く。関係のない小さな作業では読まない」と書く。CLAUDE.md・AGENTS.md への追記は必須にしない | 実測（`experiments/RESULTS.md`）。description は常にコンテキストに入るため。「必ず読む」は読みすぎて速度を落とすのを避けたいというユーザーの判断で弱めた |
| 利用先での配置 | skills CLI・手作業では、正本は `.agents/skills/team-memory/`、`.claude/skills/team-memory` は symlink。Claude Code だけのチームは plugin マーケットプレイス（`--scope project`）も使える | Codex は `.agents/skills`、Claude Code は `.claude/skills` を探す。symlink は実機で認識を確認 |
| ファイル名 | `YYYY-MM-DD-<slug>.md`。日付は初回。改名しない | Codex 案。連番は並行 PR で衝突する（ADR の弱点） |
| frontmatter | 必須: title / author / date / status。任意: agent / updated / related | PM 案（5項目）と Codex 案（agent 必須）の間。agent は PM の用途で使わないので任意 |
| author | 作業を指示した人の GitHub login。repo の git の email（GitHub の noreply 形式）から取り、なければ `gh config get -h github.com user` か `gh api user`、取れなければ聞く | ユーザー案。PM 案（エージェント自身ではなく指示した人）。アカウントを2つ使い分ける人でも、その repo のコミットと同じアカウントになる |
| 本文 | 結論 / 根拠 / 再検討の条件 / 内部メモ。結論以外は省略可 | PM 案（結論は社外向けの言葉・内部メモを分離）と Codex 案（適用範囲・再検討条件） |
| 追加の検証 | 同じ結論なら既存ファイルに追記し `updated` を付ける。期間で絞るときに取りこぼさないため | Codex レビュー |
| 結論が変わったとき | 同じファイルの結論を書き換え、`経緯` に日付・以前の結論・変えた理由を1行足す。関係する repo の文書とほかの記憶も同じ PR で直す。superseded は別のファイルへ統合したとき（同じテーマの重複をまとめたときを含む）だけ | ユーザーの判断（10/26）。当初は ADR にならい「新しいファイル＋古い方を superseded、古い結論は書き換えない」だったが、方針転換を記憶と文書の両方に反映しやすく、ファイルも増えにくい形に変えた |
| INDEX | current だけ1行ずつ。ファイル名順に挿入、整形しない。衝突は両方の行を残す | Codex 案。自動マージ設定や生成方式は入れない |
| 書く基準 | 「次の担当者の判断や、やり直しの手間を変えるか」。知見がなければ書かない | Codex 案 |
| 捨てた試行 | 記憶だけの PR で残す | Codex 案 |
| 記憶が増えたとき | 膨大になっても探せることを優先する。INDEX の記憶が100件を超えたら、その場で分野のフォルダに分け、上の INDEX は分野の一覧にする。統合済み・対象がなくなった記憶は `archive/` へ。INDEX で見つからなければ grep。整理は頼まれたときだけ、記憶だけの PR で | ユーザーの判断（10/26）。「最終整理の日付」を INDEX に置く案は、整理が重なると衝突するので採らなかった。100件は INDEX 1行が約50トークンで、毎回約5千トークンになる目安 |
| 先方向け資料 | 結論・根拠を使う。内部メモ・author・番号は写さない。暫定値は暫定と明記して使う | PM 案 |

## 入れなかったもの

- SessionStart hook での INDEX 注入: 実測でスキルの description だけで十分だったため。Claude 専用で Codex に効かない点もある。
- INDEX の自動生成・`merge=union`: 手で解消できる規模のうちは不要。
- `shareable` のような公開可否の項目: 書く側が誤判断しやすい（PM 案）。
- 定期的な整理・最終整理日の記録: 整理が重なると衝突する。頼まれたときの整理と、分野分け・archive・grep で足りる。

## 未解決・今後

- 実測は小さなサンプル repo でのもの。大きな repo・長い会話の途中で読むかは、実際のプロジェクトで試して確かめる。
- 最初に試すプロジェクト。
