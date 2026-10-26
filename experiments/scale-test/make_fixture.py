"""記憶の多い .memory/ を作る。

使い方: make_fixture.py <出力先> <split|flat100>
- split: 6分野×40件＝240件。上の INDEX.md は分野の一覧、分野ごとに INDEX.md。
- flat100: 分けていない INDEX.md にちょうど100件。
どちらにも、trigger-test と同じ「固定しきい値の二値化は採用しない」を detection 分野に入れる。
"""
import pathlib
import shutil
import sys

out = pathlib.Path(sys.argv[1])
mode = sys.argv[2]
here = pathlib.Path(__file__).parent
fixture = here.parent / "trigger-test" / "fixture"

AREAS = {
    "detection": ("記号検出", ["丸記号", "矢印", "寸法線", "文字領域", "破線", "交点", "引出線", "表の罫線"]),
    "export": ("出力", ["JSON", "CSV", "Excel", "PDF", "座標系", "文字コード", "ファイル名", "差分出力"]),
    "ui": ("画面", ["一覧画面", "確認ダイアログ", "ショートカット", "ズーム", "選択枠", "色分け", "読み込み表示", "エラー表示"]),
    "eval": ("評価", ["評価用の図面", "再現率", "適合率", "計測手順", "比較基準", "正解データ", "集計表", "回帰確認"]),
    "infra": ("環境", ["GPU サーバー", "Docker", "CI", "依存の固定", "キャッシュ", "ログ", "バックアップ", "権限"]),
    "pm": ("進め方", ["優先順位", "先方の要望", "見送った案", "納期の前提", "定例の形式", "レビュー体制", "対象範囲", "用語"]),
}
VERBS = ["は採用しない", "を既定にする", "は次の版で見直す", "は条件つきで使う", "を先にやる"]


def memories():
    for area, (label, topics) in AREAS.items():
        for i in range(40):
            topic = topics[i % len(topics)]
            verb = VERBS[i % len(VERBS)]
            day = 1 + (i % 28)
            name = f"2026-09-{day:02d}-{area}-{i:02d}.md"
            title = f"{label}: {topic}の方式{i // len(topics) + 1}{verb}"
            body = f"""---
title: {title}
author: example-dev
date: 2026-09-{day:02d}
status: current
---

## 結論
{topic}について、方式{i // len(topics) + 1}{verb}。

## 根拠
- 評価用の図面20枚で比較した（2026-09-{day:02d} 計測、確定）。
"""
            yield area, name, title, body


if out.exists():
    shutil.rmtree(out)
shutil.copytree(fixture, out)
mem = out / ".memory"
shutil.rmtree(mem)
mem.mkdir()
target = (fixture / ".memory" / "2026-10-20-fixed-threshold-rejected.md").read_text(encoding="utf-8")
target_line = "- [固定しきい値の二値化は不採用](2026-10-20-fixed-threshold-rejected.md) — スキャンの濃さの差で誤検出、適応的しきい値へ"

if mode == "split":
    lines = ["# チームの記憶", ""]
    for area, (label, topics) in AREAS.items():
        lines.append(f"- [{area}/](./{area}/INDEX.md) — {label}（{'・'.join(topics[:4])} など）")
        (mem / area).mkdir()
    (mem / "INDEX.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    per_area = {a: [f"# チームの記憶: {AREAS[a][0]}", ""] for a in AREAS}
    for area, name, title, body in memories():
        (mem / area / name).write_text(body, encoding="utf-8")
        per_area[area].append(f"- [{title}]({name})")
    (mem / "detection" / "2026-10-20-fixed-threshold-rejected.md").write_text(target, encoding="utf-8")
    per_area["detection"].append(target_line)
    for area, ls in per_area.items():
        (mem / area / "INDEX.md").write_text("\n".join(ls) + "\n", encoding="utf-8")
elif mode == "flat100":
    lines = ["# チームの記憶", ""]
    count = 0
    for area, name, title, body in memories():
        if count == 99:
            break
        (mem / name).write_text(body, encoding="utf-8")
        lines.append(f"- [{title}]({name})")
        count += 1
    (mem / "2026-10-20-fixed-threshold-rejected.md").write_text(target, encoding="utf-8")
    lines.append(target_line)
    (mem / "INDEX.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print(out)
