#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""扫描 packages/*.yyjio-task，重建 index.json。

用法：python scripts/build_index.py
"""
from __future__ import annotations

import hashlib
import json
import sys
import zipfile
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PACKAGES = ROOT / "packages"
INDEX = ROOT / "index.json"
FORMAT = "yyjio-tasks"
FORMAT_VERSION = 1


def read_manifest(path: Path) -> dict:
    with zipfile.ZipFile(path) as zf:
        try:
            raw = zf.read("task.json")
        except KeyError:
            raise SystemExit(f"{path.name}: 缺 task.json")
    try:
        data = json.loads(raw.decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"{path.name}: task.json 不是合法 JSON（{exc}）")
    if data.get("format") != "yyjio-task":
        raise SystemExit(f"{path.name}: format 不是 yyjio-task")
    for key in ("id", "name", "author", "version"):
        if not str(data.get(key) or "").strip():
            raise SystemExit(f"{path.name}: 缺字段 {key}")
    steps = ((data.get("plan") or {}).get("steps") or [])
    return {
        "id": str(data["id"]).strip().lower(),
        "name": str(data["name"]).strip(),
        "author": str(data["author"]).strip(),
        "version": str(data["version"]).strip(),
        "date": str(data.get("date") or date.today().isoformat()).strip(),
        "description": str(data.get("description") or "").strip(),
        "file": f"packages/{path.name}",
        "size": path.stat().st_size,
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "steps": len(steps),
    }


def main() -> int:
    if not PACKAGES.exists():
        PACKAGES.mkdir(parents=True)
    files = sorted(p for p in PACKAGES.glob("*.yyjio-task") if p.is_file())
    entries = [read_manifest(p) for p in files]
    # 同一 id 只保留版本号最大的那个
    best: dict[str, dict] = {}
    for e in entries:
        cur = best.get(e["id"])
        if cur is None or _vtuple(e["version"]) > _vtuple(cur["version"]):
            best[e["id"]] = e
    items = sorted(best.values(), key=lambda x: (x["name"], x["id"]))
    index = {
        "format": FORMAT,
        "format_version": FORMAT_VERSION,
        "updated": date.today().isoformat(),
        "count": len(items),
        "packages": items,
    }
    INDEX.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"index.json 已更新：{len(items)} 个任务包")
    for it in items:
        print(f"  - {it['name']} v{it['version']}（{it['author']}）{it['size']} B")
    return 0


def _vtuple(text: str) -> tuple[int, ...]:
    out = []
    for part in str(text).split("."):
        try:
            out.append(int(part))
        except ValueError:
            out.append(0)
    return tuple(out + [0] * (3 - len(out)))


if __name__ == "__main__":
    sys.exit(main())
