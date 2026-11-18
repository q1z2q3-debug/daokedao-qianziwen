#!/usr/bin/env python3
"""把附录三「字源全解·一千字」装进阅读版 HTML（作为第三十五页）。

幂等：重复运行只替换 <!-- APPENDIX3:START --> 与 END 之间的内容，
并维持 CSS、目录按钮、标题表、面包屑四处联动。
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import oracle_map as om  # noqa: E402
import oracle_glyph as og  # noqa: E402

MD = ROOT / "book" / "字源全解-一千字.md"
HTML = ROOT / "book" / "润泽说-蒙学之千字文·阅读版.html"

S_START = "<!-- APPENDIX3:START -->"
S_END = "<!-- APPENDIX3:END -->"
C_START = "/* APPENDIX3:START */"
C_END = "/* APPENDIX3:END */"

CSS = """
/* APPENDIX3:START */
.ap3 .page{max-width:1120px}
.zx-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px 14px;margin:18px 0 30px}
.zx-card{display:flex;gap:9px;padding:9px 10px 10px;border:1px solid #E2D9C9;border-radius:3px;background:#FBF6EC}
.zx-glyph{flex:0 0 46px;height:52px;display:flex;align-items:center;justify-content:center;color:#2E2620}
.zx-glyph svg{width:46px;height:52px}
.zx-body{min-width:0;font-size:12.5px;line-height:1.62;color:#4A3F34}
.zx-char{font-size:15px;font-weight:600;color:#2E2620;margin-right:4px}
.zx-sense{color:#2E2620}
.zx-form{display:block;color:#6E6152;font-size:11.5px}
.zx-ext{display:block;color:#8C7A62;font-size:11.5px}
.zx-course{font-size:13px;letter-spacing:.08em;color:#8A6E4B;margin:34px 0 0;padding-bottom:6px;border-bottom:1px solid #E2D9C9}
.ap3-lead{font-size:13.5px;line-height:1.95;color:#5C5044}
@media (max-width:960px){.zx-grid{grid-template-columns:repeat(3,minmax(0,1fr))}}
@media (max-width:720px){.zx-grid{grid-template-columns:repeat(2,minmax(0,1fr));gap:9px}
.zx-glyph{flex-basis:38px;height:44px}.zx-glyph svg{width:38px;height:44px}
.zx-body{font-size:12px}}
/* APPENDIX3:END */
"""


def build_fragment():
    text = MD.read_text(encoding="utf-8")
    blocks = re.split(r"\n## ", text)
    out = []
    total = 0
    for blk in blocks[1:]:
        head = blk.split("\n", 1)[0].strip()
        rows = re.findall(r"^\| ([^\s|]) \| ([^|]*) \| ([^|]*) \| ([^|]*) \|", blk, re.M)
        if not rows:
            continue
        cards = []
        rows = [r for r in rows if r[1].strip() != "本义"]
        for ch, sense, form, ext in rows:
            g = om.M.get(ch)
            glyph = og.glyph(g, 46) if g else ""
            ext = ext.strip()
            cards.append(
                '<article class="zx-card"><div class="zx-glyph">%s</div>'
                '<div class="zx-body"><span class="zx-char">%s</span>'
                '<span class="zx-sense">%s</span>'
                '<span class="zx-form">%s</span>%s</div></article>'
                % (glyph, ch, sense.strip(), form.strip(),
                   ('<span class="zx-ext">%s</span>' % ext) if ext else "")
            )
        total += len(rows)
        out.append('<h2 class="zx-course">%s　·　%s字</h2><div class="zx-grid">%s</div>'
                   % (head, {16: "十六", 24: "二十四", 32: "三十二", 40: "四十"}.get(len(rows), str(len(rows))),
                      "".join(cards)))

    sec = f"""{S_START}
<section class="lesson appendix ap3" data-index="35" hidden id="appendix-3">
<div class="page">
<header class="lesson-head">
<div class="lesson-no">附录</div>
<div class="lesson-titles">
<h1>字源全解 · 一千字</h1>
<p class="lesson-deck">一千字，一字一条：本义在前，构形次之，引申只收正文用得到的那一层。</p>
</div>
<div class="lesson-mark">附 录 · 字 源</div>
</header>
<p class="ap3-lead">本页补足全书一千字，与正文「字源」一节同体例：正文本课只解八至十二个关键字，余字尽在此表。左侧单线字形是按构形文重排的<b>释形示意</b>，不是拓本摹写，也不是某一家写定的小篆。构形有异说的，正文已标「一说」，此处不再强断。</p>
<p class="ap3-lead">共 {total} 条，依三十三课顺序排；课界依句意，与正文同。</p>
{''.join(out)}
<p class="ap3-lead">字形说明：构件取甲骨、金文常见写法，按「从某、某声」还原位置，笔画关系较拓本为简。凡释形示意与拓本不合者，以拓本为准。</p>
</div>
</section>
{S_END}"""
    return sec, total


def main():
    html = HTML.read_text(encoding="utf-8")
    frag, total = build_fragment()

    # 1 CSS
    if C_START in html:
        html = re.sub(re.escape(C_START) + r".*?" + re.escape(C_END), CSS.strip(), html, flags=re.S)
    else:
        html = html.replace("</style>", CSS.strip() + "\n</style>", 1)

    # 2 页面
    if S_START in html:
        html = re.sub(re.escape(S_START) + r".*?" + re.escape(S_END), frag.strip(), html, flags=re.S)
    else:
        idx = html.rindex("</section>") + len("</section>")
        html = html[:idx] + "\n" + frag.strip() + html[idx:]

    # 3 标题表
    if '"字源全解·一千字"' not in html:
        html = html.replace('"指薪修祜", "从甲骨文开始"]', '"指薪修祜", "从甲骨文开始", "字源全解·一千字"]', 1)

    # 4 面包屑
    if "n === 35" not in html:
        html = html.replace(
            "    if (n === 34) {",
            "    if (n === 35) {\n      crumb.textContent = '附 录　字源全解：一千字';\n    } else if (n === 34) {",
            1)

    # 5 目录按钮
    if 'data-go="35"' not in html:
        html = html.replace(
            '<button data-go="34"><i>附</i><span>识字：从甲骨文开始</span></button>',
            '<button data-go="34"><i>附</i><span>识字：从甲骨文开始</span></button>\n'
            '<button data-go="35"><i>附</i><span>字源全解：一千字</span></button>', 1)

    # 6 附录二 说明补一句覆盖率
    old = '<p>按六组排：天地、时序、人身、动物、器物、数字动作。每字给一个取象关键词，右侧小字是它在书中首次出现的课次；“外”表示课外扩展字。</p>'
    new = ('<p>按六组排：天地、时序、人身、动物、器物、数字动作。每字给一个取象关键词，'
           '右侧小字是它在书中首次出现的课次；“外”表示课外扩展字。</p>'
           '<p class="ap2-note">一百二十字中，七十九字见于本书正文，其字形与本义另见<a href="javascript:void(0)" data-go="35">附录三 · 字源全解</a>；'
           '其余四十一字为课外扩展，标“外”，本书不解其形。</p>')
    if "ap2-note" not in html:
        html = html.replace(old, new, 1)

    HTML.write_text(html, encoding="utf-8")
    print(f"附录三写入 {total} 条；HTML {HTML.stat().st_size} bytes")


if __name__ == "__main__":
    main()
