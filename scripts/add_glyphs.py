#!/usr/bin/env python3
"""按课补字源条目，同时写入母本 md 与阅读版 HTML。

用法：python3 scripts/add_glyphs.py glyphs/L01.json
JSON 形如 {"1": [["洪", "大水", "从水、共声；本义为大水。"]], ...}
"""
from __future__ import annotations

import html as H
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MD = ROOT / "book" / "润泽说-蒙学之千字文.md"
HTML = ROOT / "book" / "润泽说-蒙学之千字文·阅读版.html"


def lesson_slices(s: str, head: str) -> list[tuple[int, int]]:
    """按 `## 第N课` 切段，返回每段的 (start, end)。"""
    marks = [(m.start(), n) for n, m in enumerate(re.finditer(r"(?m)^## 第[^\s\u3000]+课", s), start=1)]
    out = []
    for i, (p, n) in enumerate(marks):
        end = marks[i + 1][0] if i + 1 < len(marks) else len(s)
        out.append((p, end))
    return out


CN = {}


def main() -> int:
    data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    md = MD.read_text(encoding="utf-8")
    html = HTML.read_text(encoding="utf-8")
    added = 0

    for idx in range(1, 40):
        entries = data.get(str(idx))
        if not entries:
            continue
        start, end = lesson_slices(md, "## ")[idx - 1]
        seg = md[start:end]
        gl = re.findall(r"(?m)^- \*\*(.+?)\*\*：", seg)
        pos = seg.rfind("- **")
        nl = seg.find("\n", pos)
        if nl < 0:
            nl = len(seg)
        lines = []
        for ch, brief, detail in entries:
            if ch in gl:
                continue
            lines.append(f"\n- **{ch}**：{brief}：{detail}")
        if not lines:
            continue
        md = md[: start] + seg[:nl] + "".join(lines) + seg[nl:] + md[end:]
        added += len(lines)

        # 阅读版：插到该课 dl.glyphs 末尾
        anchor = f'<section class="lesson" data-index="{idx}"'
        i = html.find(anchor)
        if i < 0:
            print(f"[warn] 第{idx}课 HTML 未找到")
            continue
        j = html.find("</dl>", i)
        if j < 0:
            print(f"[warn] 第{idx}课 无 glyphs 列表")
            continue
        divs = "".join(
            f"<div><dt>{ch}</dt><dd><strong>{brief}</strong><span>{H.escape(detail)}</span></dd></div>"
            for ch, brief, detail in entries
        )
        html = html[:j] + divs + html[j:]

    MD.write_text(md, encoding="utf-8")
    HTML.write_text(html, encoding="utf-8")
    print(f"新增 {added} 条；md {MD.stat().st_size} B，html {HTML.stat().st_size/1024/1024:.2f} MB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
