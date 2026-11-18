#!/usr/bin/env python3
"""把无字满幅插图插进《千字文》母本与阅读版。

- 源图：来稿目录里的 PNG（1328×1776）
- 处理：统一转 WebP（长边 1200，质量 82）存 book/plates/
- 母本：每课「**原文**」之后加一行图片引用
- 阅读版：每课 verse-wrap 之后、lesson-grid 之前插入 plate 区块（base64 内嵌，离线可用）
"""
from __future__ import annotations

import base64
import io
import re
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
PLATES = ROOT / "book" / "plates"
SRC_DIRS = [Path(p) for p in sys.argv[1:]] or [
    Path("/home/user/Doubao/chats/38451969562668034/千字文/来稿/解包-卷一"),
    Path("/home/user/Doubao/chats/38451969562668034/千字文/来稿/解包-卷二"),
    Path("/home/user/Doubao/chats/38451969562668034/千字文/来稿/解包-卷三"),
    Path("/home/user/Doubao/chats/38451969562668034/千字文/来稿/解包/拆包B_18-33课"),
    Path("/home/user/Doubao/chats/38451969562668034/千字文/来稿/解包-补发"),
]

NAME_RE = re.compile(r"第(\d\d)课-(\S+?)_(\S+)\.png")


def collect() -> dict[int, list[tuple[str, Path]]]:
    """课次 → [(短名, 源图)]，同名去重（多包重复）。"""
    seen: dict[str, Path] = {}
    per: dict[int, list[tuple[str, Path]]] = {}
    for d in SRC_DIRS:
        for p in sorted(d.rglob("*.png")):
            m = NAME_RE.match(p.name)
            if not m:
                continue
            n = int(m.group(1))
            if p.name in seen:
                continue
            seen[p.name] = p
            per.setdefault(n, []).append((m.group(3), p))
    return per


def to_webp(src: Path, dst: Path) -> int:
    im = Image.open(src).convert("RGB")
    w, h = im.size
    if max(w, h) > 780:
        k = 780 / max(w, h)
        im = im.resize((round(w * k), round(h * k)), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "WEBP", quality=66, method=6)
    dst.write_bytes(buf.getvalue())
    return len(buf.getvalue())


def parse_captions(dirs: list[Path]) -> dict[tuple[int, str], str]:
    """(课次, 短名) → 原文句。兼容三种对照写法：表格 / 标题加原文 / 项目加缩进原文 / 加粗短名加引文。"""
    out: dict[tuple[int, str], str] = {}
    for d in dirs:
        for md in d.rglob("课次对照*.md"):
            txt = md.read_text(encoding="utf-8", errors="ignore")
            lesson, short = 0, ""
            for line in txt.splitlines():
                s = line.strip()
                h = re.match(r"^##\s*第(\d\d)课", s)
                if h:
                    lesson, short = int(h.group(1)), ""
                    tail = re.match(r"^##\s*第\d\d课-\S+?_(\S+)", s)
                    if tail:
                        short = tail.group(1).strip()
                    continue
                b = re.match(r"^-\s*(\S+?)：", s)
                if b and lesson:
                    short = b.group(1).strip()
                    continue
                q = re.match(r"^(?:原文|>)\s*：?\s*(.+)", s)
                if q and lesson and short:
                    out.setdefault((lesson, short), q.group(1).strip())
                    continue
                bb = re.match(r"^\*\*(.+?)\*\*｜", s)
                if bb and lesson:
                    short = bb.group(1).strip()
                    continue
                row = line.strip().strip("|")
                if row.startswith("|") is False and row.count("|") >= 3 and ".png" in row:
                    cells = [c.strip() for c in row.split("|")]
                    nm = re.match(r"第(\d\d)课-\S+?_(\S+)\.png", cells[0])
                    if nm and len(cells) >= 3 and cells[-1] not in ("对应原文", ""):
                        out.setdefault((int(nm.group(1)), nm.group(2)), cells[-1])
    return out


def main() -> int:
    per = collect()
    PLATES.mkdir(parents=True, exist_ok=True)
    caps = parse_captions(SRC_DIRS)

    md = ROOT / "book" / "润泽说-蒙学之千字文.md"
    html_p = ROOT / "book" / "润泽说-蒙学之千字文·阅读版.html"
    src = md.read_text(encoding="utf-8")
    html = html_p.read_text(encoding="utf-8")

    total = 0
    size = 0
    matched = 0
    for n, items in sorted(per.items()):
        lesson_heads = re.findall(r"^## 第[^\n]*课[^\n]*", src, flags=re.M)
        # 每课的原文句，用于兜底题注
        blk_re = re.compile(rf"^## (第{cn(n)}课[^\n]*)\n(.*?)(?=^## |\Z)", re.M | re.S)
        m = blk_re.search(src)
        fallback = ""
        if m:
            q = re.search(r"\*\*原文\*\*：(.+)", m.group(2))
            if q:
                fallback = q.group(1).strip().split("。")[0] + "。"
        figs = []
        for short, path in items:
            dst = PLATES / f"{path.stem}.webp"
            if not dst.exists() or dst.stat().st_mtime < path.stat().st_mtime:
                size += to_webp(path, dst)
            else:
                size += dst.stat().st_size
            stem = path.stem
            cap = caps.get((n, short)) or fallback
            if caps.get((n, short)):
                matched += 1
            b64 = base64.b64encode(dst.read_bytes()).decode()
            figs.append(
                f'<figure class="plate"><img alt="{cn(n)}课插图·{short}" '
                f'src="data:image/webp;base64,{b64}"><figcaption>{cap}</figcaption></figure>'
            )
            total += 1
        # 母本插入
        if m:
            title = m.group(1)
            old = m.group(0)
            md_lines = "".join(
                f"\n\n![{title.split('　')[-1]}·{short}](plates/{path.stem}.webp)\n"
                for short, path in items
            )
            if "](plates/" not in old:
                newq = re.sub(r"(\*\*原文\*\*：.+\n)", r"\1" + md_lines.replace("\\", "\\\\"), old, count=1)
                src = src.replace(old, newq, 1)
        # 阅读版插入
        anchor = f'<section class="lesson" data-index="{n}"'
        i = html.find(anchor)
        if i < 0:
            print(f"[skip] 第{n}课：阅读版找不到课节")
            continue
        j = html.find('<div class="lesson-grid">', i)
        if j < 0:
            print(f"[skip] 第{n}课：找不到正文栅格")
            continue
        block = '\n<section class="plates">\n' + "\n".join(figs) + "\n</section>\n"
        if '<section class="plates">' not in html[i:j]:
            html = html[:j] + block + html[j:]

    html = html.replace(
        "</style>",
        """
.plates{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:14px;
 margin:24px 0 8px}
.plate{margin:0;background:#EFE7D6;border:1px solid #DCD5C8;border-radius:2px;overflow:hidden}
.plate img{display:block;width:100%;height:auto}
.plate figcaption{font-size:12.5px;color:#7C6D5C;letter-spacing:.02em;padding:8px 10px 10px;
 line-height:1.6;border-top:1px solid rgba(220,213,200,.7)}
@media (max-width:620px){.plates{grid-template-columns:1fr 1fr;gap:10px}
 .plate figcaption{font-size:11.5px;padding:6px 8px}}
</style>""",
        1,
    )

    md.write_text(src, encoding="utf-8")
    html_p.write_text(html, encoding="utf-8")
    print(f"插图 {total} 幅 / 课 {len(per)} 课 / 对照题注命中 {matched} 幅")
    print(f"阅读版 {html_p.stat().st_size/1024/1024:.2f} MB；plates {len(list(PLATES.glob('*.webp')))} 个文件")
    return 0


def cn(n: int) -> str:
    digits = "零一二三四五六七八九"
    if n <= 10:
        return "十" if n == 10 else digits[n]
    if n < 20:
        return "十" + digits[n % 10]
    return digits[n // 10] + "十" + (digits[n % 10] if n % 10 else "")


if __name__ == "__main__":
    sys.exit(main())
