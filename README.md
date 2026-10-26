<p align="center"><img src="docs/banner.png" alt="team-memory" width="100%"></p>

# team-memory

Claude Code と Codex のためのスキル。エージェントが作業中に得た知見を repo の `.memory/` に残し、PR でチームと共有する。

> A skill for Claude Code and Codex that keeps a team's decisions, abandoned approaches and measurements in the repo's `.memory/` and shares them through pull requests. The skill text is written in Japanese.

## なぜ

複数の人が、それぞれのエージェントと同じ repo で作業すると、エージェントが試行錯誤して得た知見はその人の手元にしか残りません。Claude Code の auto memory はマシンの中だけにあり、CLAUDE.md や AGENTS.md は規約や手順を書く場所です。その結果、別の人のエージェントが、すでに試して捨てた方法をまた試すことになります。

team-memory は、次のことを repo の中に Markdown で残します。

- 何を決めたか、なぜそう決めたか
- 何を試して、なぜやめたか
- どんな条件で何を測ったか

記憶は PR に含めてレビューされ、チーム全員のエージェントが読みます。PM は、自分のエージェントに定例資料の材料を集めさせることもできます。

<p align="center"><img src="docs/how-it-works.gif" alt="Aさんの Claude Code が試行錯誤を .memory/ に書き、Bさんの Claude Code がそれを読んで同じ失敗を避ける流れ" width="100%"></p>

## 解決すること

### Issue: すでに試して捨てた方法を、別の人がまた試す

Aさんの Claude Code が、固定しきい値での二値化を試しました。薄い図面で丸が欠けたので、その方法はやめました。でも、その経緯はAさんの手元の会話にしか残りません。翌週、Bさんの Claude Code が「速くなりそう」と同じ方法を試し、同じ失敗をたどり直します。

**Solved:** Aさんの Claude Code が、やめた理由と数値を `.memory/` に書き、PR でマージされます。Bさんの Claude Code は着手前に `INDEX.md` を見てその記憶を開き、「10/20 に試して不採用」と手を止めます。上の GIF がこの流れです。

### Issue: 会話が変わるたびに、同じ試行錯誤を繰り返す

エージェントは、前の会話でやめた方法を覚えていません。新しい会話を始めるたびに、同じ方法から試し直して、同じところで止まります。

**Solved:** 試した方法とやめた理由が repo に残るので、前回の続きから始められます。

### Issue: PM の頭の中にある前提が、開発側のエージェントに届かない

PM が考えている優先順位、先方の意向の受け止め方、うっすら考えている案や見送った案は、会議やチャットの中にしかありません。開発者のエージェントは、それを知らないまま作業します。

**Solved:** PM も自分のエージェントに「この前提を記憶に残して」と頼めます。`.memory/` に入った前提は、チーム全員のエージェントが踏まえて動きます。

### Issue: 定例資料を作るたびに、経緯を聞いて回る

**Solved:** PM のエージェントが、`.memory/` から期間と課題で絞って資料の節を作ります。内部メモ、作成者、Issue 番号は写しません。

## 使い始める

対象の repo のルートで、次のどれかを実行します。どれも CLAUDE.md や AGENTS.md への追記は要りません。`.memory/` は、最初の記憶を書くときにエージェントが作ります。

| 方法 | 対応するエージェント | 向いている場面 |
|---|---|---|
| 1. skills CLI | Claude Code・Codex ほか | チームで Claude Code と Codex を両方使う（おすすめ） |
| 2. Claude Code の plugin マーケットプレイス | Claude Code | チーム全員が Claude Code だけを使う |
| 3. 手作業 | Claude Code・Codex | npx も plugin も使えない |

### 1. skills CLI

Node.js 22.20 以上が必要です。

```sh
npx skills add ibukimatsubara/team-memory -a claude-code -a codex -y
```

[skills](https://github.com/vercel-labs/skills) CLI が、スキルを repo に入れます。

- Codex 用: `.agents/skills/team-memory/` に本体を置く
- Claude Code 用: `.claude/skills/team-memory` に symlink を張る
- 更新の確認用: `skills-lock.json`

3つともコミットすれば、チーム全員のエージェントが使えます。新しい版は `npx skills update` で取り込めます。

### 2. Claude Code の plugin マーケットプレイス

```sh
claude plugin marketplace add ibukimatsubara/team-memory --scope project
claude plugin install team-memory@team-memory --scope project
```

書き換わった `.claude/settings.json` をコミットします。チームの人がこの repo のフォルダを信頼すると、Claude Code がマーケットプレイスを登録し、plugin を有効にします。

- スキルは `team-memory:team-memory` という名前で見えます。
- Codex には入りません。

### 3. 手作業

```sh
git clone https://github.com/ibukimatsubara/team-memory.git /tmp/team-memory
mkdir -p .agents/skills .claude/skills
cp -R /tmp/team-memory/skills/team-memory .agents/skills/
ln -s ../../.agents/skills/team-memory .claude/skills/team-memory
```

`.agents/skills/team-memory` と `.claude/skills/team-memory` をコミットします。

## 動き

**読む**: 過去の判断が関係しそうな作業では、エージェントが着手前に `.memory/INDEX.md` を見て、関係する記憶だけを開きます。誤字の修正のような小さな作業では読みません。

**書く**: 方針を決めたとき、実験を打ち切ったとき、PR を作る前に、エージェントが記憶を書きます。「記憶に残して」と頼むこともできます。PR にならずに捨てた試行も、記憶だけの PR で残します。開発者だけでなく、PM が決めた前提や見送った案も書けます。

**方針が変わったら**: 同じ記憶の結論を書き換え、「経緯」に日付・以前の結論・変えた理由を1行足します。README や仕様書など、関係する repo の文書も同じ PR で直します。

**増えてきたら**: INDEX の記憶が100件を超えたら、記憶を分野ごとのフォルダに分けます。上の INDEX は分野の一覧になります。統合した記憶や、対象がなくなった記憶は `archive/` に移します。INDEX で見つからないときは grep で探すので、膨大になっても探せます。整理は頼まれたときだけ行います。

**資料にする**: 「今週の定例資料の節を .memory から作って」のように頼むと、結論と根拠を使って資料を作ります。内部メモ、作成者、Issue 番号は写しません。

## 記憶の形

```
.memory/
├── INDEX.md                                  # 今有効な記憶を1件1行で（100件を超えたら分野の一覧に）
├── 2026-10-20-fixed-threshold-rejected.md
└── 2026-10-24-eval-set-expanded.md
```

```markdown
---
title: 固定しきい値の二値化は採用しない
author: octocat            # 作業を指示した人の GitHub login
date: 2026-10-20
status: current            # current / superseded
related:
  - "#12 丸記号の検出精度の改善"
---

## 結論
スキャン画像の二値化には適応的しきい値を使う。固定しきい値は採用しない。
適用範囲: 現在受け付けているスキャン画像。写真入力は未評価。

## 根拠
- 再現率: 固定 0.62、適応的 0.81（評価用30枚、2026-10-20 計測、確定）。

## 再検討の条件
入力の濃さがそろう前処理が入った場合。

## 経緯
- 2026-10-20: 初めて記録。

## 内部メモ
（社外の資料に出さない内部の呼び名や経緯）
```

- 方針が変わったら、同じファイルの結論を書き換え、`経緯` に変更を残します。
- 結論は社外の人にも通じる言葉で書き、内部の呼び名は内部メモに分けます。
- 作成者は、その repo のコミットと同じ GitHub アカウントにします。

詳しい決まりは [`skills/team-memory/SKILL.md`](skills/team-memory/SKILL.md) にあります。

## 実測

スキルが実際にそう動くかを、Claude Code（Sonnet・Opus）と Codex で測りました。結果は [`experiments/RESULTS.md`](experiments/RESULTS.md) にあります。

- スキルを入れれば、CLAUDE.md・AGENTS.md に案内を書かなくても、関係する依頼では毎回記憶を読みました。
- 関係のない依頼では、記憶をほとんど読みませんでした。
- 定例資料を作らせたとき、作成者・Issue 番号・内部の呼び名は資料に出ませんでした。
- 240件の記憶を分野に分けた repo でも、関係する分野の INDEX をたどって目的の記憶にたどり着き、全文を開いたのはその1件でした。
- 方針転換を頼むと、ファイルを増やさずに結論を書き換え、経緯を追記しました。

サンプル repo と、機械的に作った記憶での結果です。

## リポジトリの中身

- `skills/team-memory/`: スキル本体
- `DESIGN.md`: 設計で決めたことと、その根拠
- `experiments/`: 動作の実測に使ったスクリプトと結果

## ライセンス

[MIT](LICENSE)
