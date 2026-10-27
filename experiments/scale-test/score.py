"""Summarize scale-test results.

read:   INDEX files and memory bodies opened; whether the target memory (fixed-threshold) was opened
policy: whether an existing file was rewritten or a new one created; History, updated and INDEX changes
split:  whether memories were split into area folders and the top INDEX became a list of areas
"""
import json
import pathlib
import re

root = pathlib.Path(__file__).parent / "results"
PATH = re.compile(r"\.memory/[\w./-]+\.md")


def opened(jsonl: pathlib.Path) -> list[str]:
    seen = []
    for line in jsonl.read_text().splitlines():
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        texts = []
        if ev.get("type") == "assistant":
            for c in ev["message"].get("content", []):
                if c.get("type") == "tool_use":
                    texts.append(json.dumps(c.get("input", {}), ensure_ascii=False))
        item = ev.get("item") or {}
        if item.get("type") == "command_execution" and ev.get("type") == "item.completed":
            texts.append(item.get("command", ""))
        for t in texts:
            for m in PATH.findall(t):
                if m not in seen:
                    seen.append(m)
    return seen


for f in sorted(root.glob("*/*.jsonl")):
    who, name = f.parent.name, f.stem
    scn = name.split("-")[0]
    if scn == "read":
        paths = opened(f)
        idx = [p for p in paths if p.endswith("INDEX.md")]
        bodies = [p for p in paths if not p.endswith("INDEX.md")]
        hit = any("fixed-threshold" in p for p in bodies)
        print(f"{who}\t{name}\tINDEX {len(idx)} {idx}\tbodies {len(bodies)}\ttarget {hit}")
    else:
        status = (f.with_suffix(".status")).read_text().strip().splitlines()
        diff = (f.with_suffix(".diff")).read_text()
        added = [s for s in status if s.startswith("A ")]
        modified = [s for s in status if s.startswith("M ")]
        renamed = [s for s in status if s.startswith("R ")]
        mem = f.with_suffix(".memory")
        if scn == "policy":
            target = mem / "2026-10-20-fixed-threshold-rejected.md"
            text = target.read_text() if target.exists() else ""
            print(f"{who}\t{name}\tadded {len(added)} modified {len(modified)}\t"
                  f"経緯 {'## 経緯' in text}\tupdated {'updated:' in text}\t"
                  f"INDEX changed {'INDEX.md' in diff}")
        else:
            dirs = sorted(p.name for p in mem.iterdir() if p.is_dir())
            top = (mem / "INDEX.md").read_text().strip().splitlines()
            print(f"{who}\t{name}\tdirs {dirs}\ttop INDEX lines {len(top)}\t"
                  f"added {len(added)} modified {len(modified)} renamed {len(renamed)}")
