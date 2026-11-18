#!/usr/bin/env python3
"""依母本里的图片行重建阅读版插图区块（清干净再插，不叠加）。"""
from __future__ import annotations

import base64
import html as H
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MD = ROOT / "book" / "润泽说-蒙学之千字文.md"
PAGE = ROOT / "book" / "润泽说-蒙学之千字文·阅读版.html"
PLATES = ROOT / "book" / "plates"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from replates import lookup, parse_maps  # noqa: E402


def trim(quote: str, yw: str) -> str:
    """题注只留本课之内的句子；跨到下一课的尾巴剪掉。"""
    if not yw:
        return quote
    sents = [x for x in re.split(r"(?<=。)", quote) if x.strip()]
    keep = []
    for s in sents:
        if re.sub(r"[，。、；：“”‘’\s（）()]", "", s) and re.sub(
            r"[，。、；：“”‘’\s（）()]", "", s
        ) in yw:
            keep.append(s)
        else:
            break
    if keep:
        return "".join(keep)
    # 首句就不在本课：按逗号切，只留本课之内的连续片段
    frag = [x for x in re.split(r"[，。]", quote) if x.strip()]
    got = []
    for x in frag:
        nx = re.sub(r"[，。、；：“”‘’\s（）()]", "", x)
        if nx and nx in yw:
            got.append(x)
        elif got:
            break
    return "，".join(got) + "。" if got else quote


OVERRIDE = (
    __import__("json").loads((PLATES / "captions.json").read_text(encoding="utf-8"))
    if (PLATES / "captions.json").exists()
    else {}
)


def strip(page: str) -> str:
    while True:
        i = page.find('<section class="plates">')
        if i < 0:
            return page
        j = page.find("</section>", i) + len("</section>")
        page = page[:i] + page[j:]


def main() -> int:
    kv = parse_maps()
    md = MD.read_text(encoding="utf-8")
    page = strip(PAGE.read_text(encoding="utf-8"))

    ms = list(re.finditer(r"(?m)^## 第[^\s\u3000]+课", md))
    per = {}
    for i, m in enumerate(ms, start=1):
        e = ms[i].start() if i < len(ms) else len(md)
        seg = md[m.start() : e]
        for stem in re.findall(r"\(plates/(.+?)\.webp\)", seg):
            per.setdefault(i, []).append(stem)

    yw = {}
    for i, m in enumerate(ms, start=1):
        e = ms[i].start() if i < len(ms) else len(md)
        q = re.search(r"\*\*原文\*\*：(.+)", md[m.start() : e])
        yw[i] = re.sub(r"[，。、；：“”‘’\s]", "", q.group(1)) if q else ""

    anchors = list(re.finditer(r'<section class="lesson" data-index="(\d+)"', page))
    total = 0
    for m in reversed(anchors):
        n = int(m.group(1))
        if n not in per:
            continue
        j = page.find('<div class="lesson-grid">', m.start())
        figs = []
        for stem in per[n]:
            mm = re.match(r"第(\d\d)课-\S+?_(.+)", stem)
            quote = OVERRIDE.get(stem) or lookup(kv, int(mm.group(1)), mm.group(2)) or ""
            quote = trim(quote, yw[n])
            short = mm.group(2)
            b64 = base64.b64encode((PLATES / f"{stem}.webp").read_bytes()).decode()
            figs.append(
                f'<figure class="plate"><img alt="第{n}课插图·{short}" src="data:image/webp;base64,{b64}">'
                f"<figcaption>{H.escape(quote)}</figcaption></figure>"
            )
            total += 1
        page = page[:j] + '\n<section class="plates">\n' + "\n".join(figs) + "\n</section>\n" + page[j:]

    PAGE.write_text(page, encoding="utf-8")
    print(f"重建 {len(per)} 课 / {total} 幅；阅读版 {PAGE.stat().st_size/1024/1024:.2f} MB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
