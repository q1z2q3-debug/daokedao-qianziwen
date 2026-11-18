#!/usr/bin/env python3
"""按原文句的重合度把插图归课，并整块重排。

画册包的分课与本书不同：包的课次中段起整体错位（包第27课＝书第二十四课），
所以只认原文，不认文件名里的课号。每课最多留三幅，超出按重合度取前三条。
"""
from __future__ import annotations

import base64
import glob
import html as H
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MD = ROOT / "book" / "润泽说-蒙学之千字文.md"
PAGE = ROOT / "book" / "润泽说-蒙学之千字文·阅读版.html"
PLATES = ROOT / "book" / "plates"
GLOB = "/home/user/Doubao/chats/38451969562668034/千字文/来稿/解包*/**/课次对照*.md"
VAR = str.maketrans({"飖": "摇", "蚤": "早", "陣": "陈", "藁": "稿"})
CAP = 3


def norm(s: str) -> str:
    s = re.sub(r"（.*?）|\(.*?\)", "", s)
    s = re.sub(r"[，。、；：“”‘’\s]", "", s)
    return s.translate(VAR)


def parse_maps() -> dict[tuple[int, str], str]:
    kv: dict[tuple[int, str], str] = {}
    for f in glob.glob(GLOB, recursive=True):
        txt = Path(f).read_text(encoding="utf-8", errors="ignore")
        lesson, short = 0, ""
        for line in txt.splitlines():
            s = line.strip()
            h = re.match(r"^##\s*第(\d\d)课", s)
            if h:
                lesson, short = int(h.group(1)), ""
                m2 = re.match(r"^##\s*第\d\d课-\S+?_(.+)$", s)
                if m2:
                    short = m2.group(1).strip()
                continue
            b = re.match(r"^-\s*(\S+?)：", s)
            if b and lesson:
                short = b.group(1).strip()
                continue
            q = re.match(r"^(?:原文|>)\s*：?\s*(.+)", s)
            if q and lesson and short:
                kv.setdefault((lesson, short), q.group(1).strip())
                continue
            bb = re.match(r"^\*\*(.+?)\*\*｜", s)
            if bb and lesson:
                short = bb.group(1).strip()
                continue
            if s.count("|") >= 3 and ".png" in s:
                cells = [c.strip() for c in s.strip("|").split("|")]
                nm = re.match(r"第(\d\d)课-\S+?_(.+?)\.png", cells[0])
                if nm and len(cells) >= 3 and cells[-1] not in ("对应原文", ""):
                    kv.setdefault((int(nm.group(1)), nm.group(2)), cells[-1])
    return kv


def lookup(kv, pkg: int, short: str) -> str | None:
    if (pkg, short) in kv:
        return kv[(pkg, short)]
    for (n, s), q in kv.items():
        if s.replace("（第32课前半）", "").strip() == short:
            return q
    return None


def score(qn: str, yw: str) -> int:
    s = 0
    for k in range(len(qn) - 1):
        if qn[k : k + 2] in yw:
            s += 1
    for k in range(len(qn) - 2):
        if qn[k : k + 3] in yw:
            s += 2
    return s


def main() -> int:
    kv = parse_maps()
    md = MD.read_text(encoding="utf-8")
    page = PAGE.read_text(encoding="utf-8")

    def slices():
        ms = list(re.finditer(r"(?m)^## 第[^\s\u3000]+课", md))
        yw = {}
        for i, m in enumerate(ms, start=1):
            e = ms[i].start() if i < len(ms) else len(md)
            q = re.search(r"\*\*原文\*\*：(.+)", md[m.start() : e])
            yw[i] = norm(q.group(1)) if q else ""
        return ms, yw

    _, yw = slices()

    cand: dict[int, list] = {}
    fails = []
    for p in sorted(PLATES.glob("*.webp")):
        m = re.match(r"第(\d\d)课-\S+?_(.+)", p.stem)
        quote = lookup(kv, int(m.group(1)), m.group(2))
        if not quote:
            fails.append(p.stem)
            continue
        qn = norm(quote)
        best = max(range(1, 34), key=lambda i: score(qn, yw[i]))
        if score(qn, yw[best]) == 0:
            fails.append(p.stem)
            continue
        cand.setdefault(best, []).append((score(qn, yw[best]), p, quote, m.group(2)))

    per, dropped = {}, []
    for n, items in cand.items():
        items.sort(key=lambda x: -x[0])
        per[n] = items[:CAP]
        dropped += [(n, x[2], x[1].stem) for x in items[CAP:]]

    # 清旧
    md = re.sub(r"(?m)^!\[[^\]]*\]\(plates/[^)]*\)\n\n", "", md)
    page = re.sub(r'(?s)\n<section class="plates">.*?</section>\n', "\n", page)

    # 母本
    for n in sorted(per):
        ms, _ = slices()
        start = ms[n - 1].start()
        end = ms[n].start() if n < len(ms) else len(md)
        seg = md[start:end]
        q = re.search(r"(?m)^\*\*原文\*\*：.+\n", seg)
        if not q:
            continue
        lines = "".join(f"\n\n![{short}](plates/{p.stem}.webp)\n" for _, p, _, short in per[n])
        md = md[: start + q.end()] + lines + md[start + q.end() :]

    # 阅读版
    anchors = list(re.finditer(r'<section class="lesson" data-index="(\d+)"', page))
    for k, m in enumerate(anchors):
        n = int(m.group(1))
        if n not in per:
            continue
        j = page.find('<div class="lesson-grid">', m.start())
        figs = []
        for _, p, quote, short in per[n]:
            b64 = base64.b64encode(p.read_bytes()).decode()
            figs.append(
                f'<figure class="plate"><img alt="第{n}课插图·{short}" src="data:image/webp;base64,{b64}">'
                f"<figcaption>{H.escape(quote)}</figcaption></figure>"
            )
        page = page[:j] + '\n<section class="plates">\n' + "\n".join(figs) + "\n</section>\n" + page[j:]

    MD.write_text(md, encoding="utf-8")
    PAGE.write_text(page, encoding="utf-8")
    print(f"归课 {len(per)} 课 / 图 {sum(len(v) for v in per.values())} 幅 / 未归 {len(fails)} {fails}")
    print(f"超出三幅被撤 {len(dropped)}：")
    for d in dropped:
        print("  ", d)
    gaps = [i for i in range(1, 34) if i not in per]
    print("无插图课次", gaps)
    print(f"阅读版 {PAGE.stat().st_size/1024/1024:.2f} MB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
