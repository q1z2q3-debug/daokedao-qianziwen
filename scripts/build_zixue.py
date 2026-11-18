# -*- coding: utf-8 -*-
"""把 book/字源全解-一千字.md 生成为单文件离线检索页 docs/zixue.html"""
import re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import oracle_glyph as og
from oracle_map import M as GLYPH_MAP

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "book" / "字源全解-一千字.md"
OUT = ROOT / "docs" / "zixue.html"
VER = (ROOT / "VERSION").read_text().strip()

def parse(text):
    groups, cur = [], None
    for line in text.splitlines():
        h = re.match(r"## (第[^\s]*课)\s*(.*)$", line)
        if h:
            cur = {"name": h.group(1), "title": h.group(2).strip(), "rows": []}
            groups.append(cur)
            continue
        r = re.match(r"\| (\S{1,2}) \| (.+?) \| (.+?) \| (.+?) \|", line)
        if r and cur and r.group(2) != "本义":
            cur["rows"].append([x.strip() for x in r.groups()])
    return groups

ROWS = parse(SRC.read_text(encoding="utf-8"))
TOTAL = sum(len(g["rows"]) for g in ROWS)

CSS = """
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:#EFE7D6;color:#3A3230;
 font-family:"Songti SC","Noto Serif SC","Source Han Serif SC",SimSun,serif;
 font-feature-settings:"palt" 1;line-height:1.75}
a{color:#9C3B2E}
.wrap{max-width:1120px;margin:0 auto;padding:44px 30px 70px}
.hero{border-bottom:1px solid #D6CBB6;padding-bottom:26px;margin-bottom:26px;display:flex;
 justify-content:space-between;align-items:flex-end;gap:24px;flex-wrap:wrap}
h1{margin:0;font-size:38px;letter-spacing:.12em;font-weight:600}
.hero .sub{margin:8px 0 0;font-size:14px;color:#7C6D5C;letter-spacing:.06em}
.stat{text-align:right;font-size:13px;color:#7C6D5C;line-height:1.9}
.stat b{font-size:30px;color:#9C3B2E;font-weight:600;letter-spacing:.04em}
.bar{position:sticky;top:0;z-index:9;background:#EFE7D6;padding:14px 0 10px;
 border-bottom:1px solid #D6CBB6;display:flex;gap:10px;flex-wrap:wrap;align-items:center}
input[type=search]{flex:1 1 240px;min-width:200px;padding:11px 14px;font:inherit;font-size:16px;
 border:1px solid #C9BCA4;background:#F7F1E4;color:#3A3230;border-radius:2px;outline:none}
input[type=search]:focus{border-color:#9C3B2E}
.chip{padding:8px 13px;border:1px solid #C9BCA4;background:#F7F1E4;font:inherit;font-size:14px;
 color:#5A4E42;cursor:pointer;border-radius:2px;min-height:40px}
.chip[aria-pressed=true]{background:#3A3230;border-color:#3A3230;color:#F2EAD8}
.count{font-size:13px;color:#7C6D5C;margin-left:auto}
h2{font-size:22px;letter-spacing:.1em;margin:34px 0 10px;font-weight:600;display:flex;
 gap:12px;align-items:baseline}
h2 em{font-style:normal;font-size:13px;color:#9C3B2E;letter-spacing:.06em}
table{width:100%;table-layout:fixed;border-collapse:collapse;font-size:15px;background:#F7F1E4}
col.c1{width:9%}col.c2{width:8%}col.c3{width:19%}col.c4{width:33%}col.c5{width:31%}
thead th{background:#E5DAC4;font-weight:600;font-size:13px;letter-spacing:.14em;
 color:#5A4E42;padding:9px 12px;text-align:left;border-bottom:1px solid #C9BCA4}
tbody td{padding:10px 12px;border-bottom:1px solid #E1D7C3;vertical-align:top;word-break:break-word}
tbody td:nth-child(2){font-size:26px;line-height:1.3;letter-spacing:.06em;color:#2E2620;text-align:center}
tbody td:first-child{padding:6px 8px;white-space:nowrap}
.glyph{display:block;margin:0 auto}
.jin{color:#C3B49D;font-size:16px}
tr.hit td{background:#FBF3DE}
.lesson{display:block}
.lesson.hide{display:none}
.rule{font-size:13.5px;color:#7C6D5C;background:#F2E9D6;border-left:3px solid #C9BCA4;
 padding:12px 16px;margin:22px 0 8px}
.foot{margin-top:44px;padding-top:18px;border-top:1px solid #D6CBB6;font-size:12.5px;
 color:#8A7A66;display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap}
@media (max-width:680px){
 .wrap{padding:26px 16px 52px}
 h1{font-size:26px}
 .hero{flex-direction:column;align-items:flex-start}
 .stat{text-align:left}
 .stat b{font-size:24px}
 table{font-size:13.5px}
 col.c1{width:13%}col.c2{width:25%}col.c3{width:32%}col.c4{width:30%}
 tbody td:first-child{font-size:22px}
 thead th{padding:8px 8px;font-size:12px}
 tbody td{padding:9px 8px}
}
"""

def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

secs = []
for g in ROWS:
    def row(r):
        gsvg = og.glyph(GLYPH_MAP[r[0]], 46) if r[0] in GLYPH_MAP else '<span class="jin">—</span>'
        return (f'<tr><td title="释形示意">{gsvg}</td><td>{esc(r[0])}</td>'
                f'<td>{esc(r[1])}</td><td>{esc(r[2])}</td><td>{esc(r[3])}</td></tr>')
    rows = "\n".join(row(r) for r in g["rows"])
    secs.append(f'''<section class="lesson" data-lesson="{g["name"]}">
<h2>{g["name"]}　{g["title"]}<em>{len(g["rows"])} 字</em></h2>
<table><colgroup><col class="c1"><col class="c2"><col class="c3"><col class="c4"><col class="c5"></colgroup>
<thead><tr><th>字形</th><th>字</th><th>本义</th><th>构形</th><th>引申</th></tr></thead>
<tbody>
{rows}
</tbody></table>
</section>''')

html = f'''<html lang="zh-Hans"><head><meta charset="utf-8">
<title>字源全解 · 一千字｜润泽说 蒙学之千字文</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>{CSS}</style></head><body><div class="wrap">
<header class="hero">
 <div><h1>字源全解 · 一千字</h1>
 <p class="sub">润泽说 蒙学之千字文 · 附录三 · 一字一条：本义在前，构形取甲骨、金文、小篆之一，引申只列正文用到的义</p></div>
 <div class="stat"><b>{TOTAL}</b> 字已成<br>已校 {len(ROWS)} 课｜离线可查</div>
</header>
<div class="bar">
 <input type="search" id="q" placeholder="查字、查义、查构形，如「玄」「甲骨」" aria-label="检索">
 <button class="chip" data-filter="all" aria-pressed="true">全部课</button>
 <button class="chip" data-filter="done" aria-pressed="false">已成字</button>
 <span class="count" id="cnt">共 {TOTAL} 字</span>
</div>
<p class="rule">体例：本义为第一义；构形取甲骨文、金文、小篆中最能说明造字本意的一说，异说标「一说」，不冒充定诂；引申只收正文实际用到的义。全书一千字已成，三十三课一字不缺。字形为按构形自绘的释形示意，非拓本摹写：一至十课二百五十六字为逐字手工拼制，余字按本表构形文（从某、某声）自动拼出，笔画关系较简，待分批精修。</p>
{"".join(secs)}
<div class="foot"><span>润泽说 · 蒙学之千字文 · v{VER}</span><span>单文件离线，不取外链</span></div>
</div>
<script>
(function(){{
 var q=document.getElementById('q'),cnt=document.getElementById('cnt'),rows=document.querySelectorAll('tbody tr');
 var secs=document.querySelectorAll('.lesson'),chip=document.querySelectorAll('.chip');
 function norm(s){{return s.toLowerCase().replace(/\\s+/g,'');}}
 function run(){{
  var k=norm(q.value),hit=0;
  secs.forEach(function(sec){{
   var n=0;
   sec.querySelectorAll('tbody tr').forEach(function(tr){{
    var m=k===''||norm(tr.textContent).indexOf(k)>-1;
    tr.classList.toggle('hit',m&&k!=='');
    if(m)n++;
   }});
   sec.classList.toggle('hide',n===0&&k!=='');
   hit+=n;
  }});
  cnt.textContent=k===''?'共 {TOTAL} 字':'命中 '+hit+' 字';
 }}
 q.addEventListener('input',run);
 chip.forEach(function(b){{b.addEventListener('click',function(){{
  chip.forEach(function(x){{x.setAttribute('aria-pressed','false')}});
  b.setAttribute('aria-pressed','true');
  var f=b.dataset.filter;
  secs.forEach(function(s){{s.classList.toggle('hide',f==='done'&&s.querySelectorAll('tbody tr').length===0)}});
  run();
 }})}});
 run();
}})();
</script></body></html>'''

OUT.write_text(html, encoding="utf-8")
print(OUT, len(html), "bytes /", TOTAL, "字 /", len(ROWS), "课")
