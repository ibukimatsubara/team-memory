"""results/ の各実行で、.memory を読んだか・スキルを使ったか・不採用の理由に触れたかを数える。"""
import collections
import re
import json
import pathlib
import sys

root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else pathlib.Path(__file__).parent / "results")
rows = []
for f in sorted(root.rglob("*.jsonl")):
    skill = memory = False
    final = ""
    bodies = set()  # 開いた記憶の本文（INDEX 以外）
    duration = 0
    for line in f.read_text().splitlines():
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        if ev.get("type") == "assistant":
            for c in ev["message"].get("content", []):
                if c.get("type") == "tool_use":
                    s = json.dumps(c.get("input", {}), ensure_ascii=False)
                    if c["name"] == "Skill" and re.search(r"(project|team)-memory", s):
                        skill = True
                    if ".memory" in s:
                        memory = True
                    bodies.update(re.findall(r"\.memory/([\w.-]+\.md)", s))
        if ev.get("type") == "result":
            final = ev.get("result", "") or ""
            duration = ev.get("duration_ms", 0)
        # Codex（codex exec --json）の形式
        item = ev.get("item") or {}
        if item.get("type") == "command_execution":
            cmd = item.get("command", "")
            if re.search(r"(project|team)-memory/SKILL.md", cmd):
                skill = True
            if ".memory" in cmd:
                memory = True
            bodies.update(re.findall(r"\.memory/([\w.-]+\.md)", cmd))
        if item.get("type") == "agent_message":
            final = item.get("text", "") or ""
    bodies.discard("INDEX.md")
    cited = any(k in final for k in ("0.62", "0.81", "不採用", ".memory"))
    cond, p, n = f.stem.split("-")
    rows.append((f.parent.name, cond, p, n, skill, memory, cited, len(bodies), duration))

agg = collections.defaultdict(lambda: [0, 0, 0, 0, 0, 0])
for model, cond, p, n, skill, memory, cited, nbodies, duration in rows:
    a = agg[(model, cond, p)]
    a[0] += 1
    a[1] += skill
    a[2] += memory
    a[3] += cited
    a[4] += nbodies
    a[5] += duration
print("model\tcond\tprompt\truns\tskill\tread.memory\tcited\tbodies/run\tsec/run")
for k in sorted(agg):
    runs, skill, memory, cited, nbodies, duration = agg[k]
    print("\t".join(map(str, (*k, runs, skill, memory, cited, round(nbodies / runs, 1), round(duration / runs / 1000)))))
