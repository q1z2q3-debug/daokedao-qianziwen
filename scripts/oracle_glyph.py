# -*- coding: utf-8 -*-
"""甲骨文构件字形生成器：一套笔画构件 + 造字理据拼字，输出内联 SVG。

体例：不是拓本摹写，是按《说文》构形与甲骨常见写法做的「释形示意」字形。
所有构件画在 100×100 的骨面坐标里，线条略作抖动，避免矢量过于齐整。
"""
import math, random

STROKE = 4.6

def _w(i=1):
    """笔画粗细微差，制造刻辞的手感（确定性，不用随机）"""
    return STROKE + ((i % 3) - 1) * 0.35

def path(d, w=None, cap="round"):
    return f'<path d="{d}" stroke-width="{w or STROKE}" stroke-linecap="{cap}"/>'

# ——— 构件：每个返回 SVG 片段（已含 stroke 属性），坐标居中于 0,0，尺度约 ±30 ———
def sun():      # 日：圆中有实点
    return ('<circle cx="0" cy="0" r="26" fill="none" stroke-width="%.1f"/>' % _w(0)
            + '<circle cx="0" cy="0" r="5.5" fill="currentColor" stroke="none"/>')

def moon():     # 月：半月，内加一短划
    return ('<path d="M6,-27 C-16,-22 -22,0 -16,22 C-11,27 4,27 9,25" stroke-width="%.1f"/>' % _w(1)
            + '<path d="M-6,-12 C-11,0 -9,12 -2,18" stroke-width="%.1f" opacity=".85"/>' % _w(2))

def star():     # 辰/星：三星成列
    return ('<path d="M-20,-14 l7,7 M-20,-14 l7,-7 M-20,-14 l-7,0" stroke-width="%.1f"/>' % _w(0)
            + '<path d="M4,2 l7,7 M4,2 l7,-7 M4,2 l-7,0" stroke-width="%.1f"/>' % _w(1)
            + '<path d="M26,18 l6,6 M26,18 l6,-6 M26,18 l-6,0" stroke-width="%.1f"/>' % _w(2))

def mountain(): # 山：三峰
    return ('<path d="M-30,18 L-15,-14 L-2,18 M-2,18 L12,-20 L26,18 M-30,18 L26,18" stroke-width="%.1f"/>' % _w(0))

def water():    # 水：中流两侧波
    return ('<path d="M0,-26 C2,-8 -2,8 0,26" stroke-width="%.1f"/>' % _w(0)
            + '<path d="M-16,-18 C-9,-6 -12,10 -6,20" stroke-width="%.1f"/>' % _w(1)
            + '<path d="M15,-16 C9,-4 12,10 6,22" stroke-width="%.1f"/>' % _w(2)
            + '<circle cx="-18" cy="4" r="2.6" fill="currentColor" stroke="none"/>'
            + '<circle cx="18" cy="6" r="2.6" fill="currentColor" stroke="none"/>')

def fire():      # 火：焰舌上腾
    return ('<path d="M0,26 C-14,10 -10,-6 0,-26 C10,-6 14,10 0,26" stroke-width="%.1f"/>' % _w(0)
            + '<path d="M0,-6 C-5,4 -4,14 0,22" stroke-width="2.2" opacity=".8"/>')

def tree():      # 木：干、枝、根
    return ('<path d="M0,-26 L0,26" stroke-width="%.1f"/>' % _w(0)
            + '<path d="M0,-12 C-10,-16 -16,-22 -20,-26" stroke-width="%.1f"/>' % _w(1)
            + '<path d="M0,-12 C10,-16 16,-22 20,-26" stroke-width="%.1f"/>' % _w(2)
            + '<path d="M0,20 C-9,24 -14,26 -18,26 M0,20 C9,24 14,26 18,26" stroke-width="%.1f"/>' % _w(3))

def grain():     # 禾：穗下垂
    return tree() + '<path d="M-1,-26 C-8,-32 -3,-38 0,-40" stroke-width="2.4"/>'

def person():    # 人：侧立，微躬
    return ('<circle cx="2" cy="-24" r="6" fill="none" stroke-width="%.1f"/>' % _w(0)
            + '<path d="M1,-18 C-4,-6 -2,8 -6,24" stroke-width="%.1f"/>' % _w(1)
            + '<path d="M-1,-14 C-10,-8 -14,-2 -16,6" stroke-width="%.1f"/>' % _w(2))

def big_person(): # 大：正面张手足
    return ('<circle cx="0" cy="-22" r="5.5" fill="none" stroke-width="%.1f"/>' % _w(0)
            + '<path d="M0,-16 L0,10" stroke-width="%.1f"/>' % _w(1)
            + '<path d="M0,-12 L-18,-2 M0,-12 L18,-2" stroke-width="%.1f"/>' % _w(2)
            + '<path d="M0,8 L-13,26 M0,8 L13,26" stroke-width="%.1f"/>' % _w(3))

def woman():     # 女：跪坐敛手
    return ('<circle cx="-2" cy="-22" r="5.5" fill="none" stroke-width="%.1f"/>' % _w(0)
            + '<path d="M-3,-16 C-10,-6 -12,4 -8,12" stroke-width="%.1f"/>' % _w(1)
            + '<path d="M-10,-6 C2,-10 14,-4 18,4" stroke-width="%.1f"/>' % _w(2)
            + '<path d="M-8,12 C0,20 10,18 16,10" stroke-width="%.1f"/>' % _w(3))

def child():     # 子：大头小儿，举臂
    return ('<circle cx="0" cy="-18" r="8" fill="none" stroke-width="%.1f"/>' % _w(0)
            + '<path d="M0,-10 L0,6" stroke-width="%.1f"/>' % _w(1)
            + '<path d="M0,-6 L-13,-14 M0,-6 L13,-14" stroke-width="%.1f"/>' % _w(2)
            + '<path d="M0,6 L-6,22 M0,6 L7,22" stroke-width="2.6"/>')

def eye():       # 目：横目，中一竖为瞳
    return ('<path d="M-26,0 C-16,-12 16,-12 26,0 C16,12 -16,12 -26,0 Z" fill="none" stroke-width="%.1f"/>' % _w(0)
            + '<path d="M0,-10 L0,10" stroke-width="2.2"/>')

def mouth():     # 口：开口
    return ('<path d="M-18,-12 L18,-12 L18,12 L-18,12 Z" fill="none" stroke-width="%.1f"/>' % _w(0))

def hand():      # 又：三指手
    return ('<path d="M-8,22 L-2,0" stroke-width="%.1f"/>' % _w(0)
            + '<path d="M-2,0 L-14,-14 M-2,0 L0,-20 M-2,0 L13,-15" stroke-width="%.1f"/>' % _w(1))

def foot():      # 止：足趾
    return ('<path d="M0,24 L0,-6" stroke-width="%.1f"/>' % _w(0)
            + '<path d="M0,-6 L-12,-18 M0,-6 L0,-22 M0,-6 L11,-18" stroke-width="%.1f"/>' % _w(1)
            + '<path d="M-8,24 L8,24" stroke-width="2.6"/>')

def roof():      # 宀：屋盖
    return ('<path d="M-26,2 C-12,-22 12,-22 26,2" stroke-width="%.1f"/>' % _w(0)
            + '<path d="M-20,2 L-20,24 M20,2 L20,24" stroke-width="2.4"/>')

def vessel():    # 皿：圈足器
    return ('<path d="M-22,-10 L22,-10" stroke-width="%.1f"/>' % _w(0)
            + '<path d="M-18,-10 C-16,10 -12,18 0,18 C12,18 16,10 18,-10" stroke-width="%.1f"/>' % _w(1)
            + '<path d="M-8,18 L-6,26 M8,18 L6,26" stroke-width="2.4"/>')

def field():     # 田：阡陌
    return ('<path d="M-22,-22 L22,-22 L22,22 L-22,22 Z" fill="none" stroke-width="%.1f"/>' % _w(0)
            + '<path d="M0,-22 L0,22 M-22,0 L22,0" stroke-width="2.4"/>')

def shell():     # 贝：贝纹
    return ('<path d="M0,-24 C-14,-20 -16,0 0,24 C16,0 14,-20 0,-24 Z" fill="none" stroke-width="%.1f"/>' % _w(0)
            + '<path d="M-8,-12 L8,-12 M-10,0 L10,0 M-8,12 L8,12" stroke-width="2.2"/>')

def bow():       # 弓
    return ('<path d="M8,-24 C-14,-14 -14,14 8,24" stroke-width="%.1f"/>' % _w(0)
            + '<path d="M8,-24 L8,24" stroke-width="2.2" opacity=".75"/>')

def axe():       # 戈：横刃
    return ('<path d="M-4,26 L-4,-20" stroke-width="%.1f"/>' % _w(0)
            + '<path d="M-4,-20 C-16,-24 -24,-18 -26,-8" stroke-width="%.1f"/>' % _w(1)
            + '<path d="M-4,-2 L8,-8" stroke-width="2.4"/>')

def silk():      # 糸：束丝
    return ('<path d="M0,24 C-16,10 -12,-10 0,-22 C12,-10 16,10 0,24" stroke-width="%.1f"/>' % _w(0)
            + '<path d="M-12,-14 L12,-14" stroke-width="2.2"/>'
            + '<path d="M0,-14 L0,14" stroke-width="2.2" opacity=".8"/>')

def horse():     # 马：长面、鬃、四足
    return ('<path d="M-8,-20 C-2,-28 12,-26 16,-16 L16,6" stroke-width="%.1f"/>' % _w(0)
            + '<circle cx="6" cy="-20" r="2" fill="currentColor" stroke="none"/>'
            + '<path d="M16,6 L-14,6" stroke-width="%.1f"/>' % _w(1)
            + '<path d="M-12,6 L-16,24 M-2,6 L0,24 M8,6 L10,24" stroke-width="2.4"/>')

def bird():      # 鸟：喙、翼、爪
    return ('<path d="M-12,-6 C-6,-18 8,-20 18,-12 L26,-16" stroke-width="%.1f"/>' % _w(0)
            + '<circle cx="12" cy="-14" r="2.2" fill="currentColor" stroke="none"/>'
            + '<path d="M-12,-6 C-2,2 10,4 20,0" stroke-width="%.1f"/>' % _w(1)
            + '<path d="M-6,2 L-8,20 M6,2 L8,20 M-14,20 L0,20 M2,20 L14,20" stroke-width="2.2"/>')

def dragon():    # 龙：巨口长身
    return ('<path d="M-24,-14 C-10,-24 4,-22 8,-12 C12,-2 4,6 -6,4 C-14,2 -18,10 -14,18" stroke-width="%.1f"/>' % _w(0)
            + '<path d="M-24,-14 L-18,-20" stroke-width="2.2"/>'
            + '<path d="M8,-12 C18,-14 24,-6 20,4" stroke-width="%.1f"/>' % _w(1))

def jade():      # 玉：绳贯三玉
    rects = "".join(
        '<rect x="-7" y="%d" width="14" height="10" stroke-width="2.4"/>' % y for y in (-20, -4, 12)
    )
    return '<path d="M0,-26 L0,26" stroke-width="2.2"/>' + rects

def cloth():     # 衣：交领
    return ('<path d="M-22,-18 L0,-26 L22,-18 L14,22 L0,14 L-14,22 Z" fill="none" stroke-width="%.1f"/>' % _w(0)
            + '<path d="M-22,-18 L4,4 M22,-18 L-4,4" stroke-width="2.2"/>')

def speech():    # 口+气：言语
    return mouth() + '<path d="M-6,-18 C0,-26 10,-26 14,-20" stroke-width="2.2"/>'

def gate():      # 门：双扉
    return ('<path d="M-20,24 L-20,-14 C-20,-24 -8,-26 -8,-14 L-8,24" stroke-width="%.1f"/>' % _w(0)
            + '<path d="M20,24 L20,-14 C20,-24 8,-26 8,-14 L8,24" stroke-width="%.1f"/>' % _w(1))

def walk():      # 彳：半行
    return ('<path d="M-6,-14 L6,-4 L-6,8 L4,18" stroke-width="%.1f"/>' % _w(0))

def city():      # 邑：口上有节
    return mouth() + '<path d="M-10,12 L-10,24 M10,12 L10,24" stroke-width="2.4"/>'

def knife():     # 刀：刃向前
    return ('<path d="M-16,22 C-6,10 2,-6 6,-20" stroke-width="%.1f"/>' % _w(0)
            + '<path d="M-20,24 L-4,18" stroke-width="2.4"/>')

def heart():     # 心：器中有血
    return ('<path d="M-18,-12 C-6,-20 6,-20 18,-12 C20,6 10,20 0,22 C-10,20 -20,6 -18,-12 Z" fill="none" stroke-width="%.1f"/>' % _w(0)
            + '<circle cx="0" cy="4" r="3" fill="currentColor" stroke="none"/>')

def sound():     # 声/言：口出三线
    return mouth() + '<path d="M2,-18 L2,-28 M-8,-16 L-12,-26 M12,-16 L16,-26" stroke-width="2.2"/>'

def mountain_ridge():
    return mountain()

def dot(x, y):
    return f'<circle cx="{x}" cy="{y}" r="3.2" fill="currentColor" stroke="none"/>'


def bar():
    return '<path d="M-24,0 L24,0" stroke-width="3.0"/>'

def grass():     # 艸：草叶上出
    return ('<path d="M-20,26 C-24,6 -18,-8 -14,-18" stroke-width="2.4"/>'
            '<path d="M-6,26 C-10,6 -4,-10 0,-20" stroke-width="2.4"/>'
            '<path d="M8,26 C6,6 10,-8 16,-16" stroke-width="2.4"/>')

def soil():      # 土：土块隆起
    return ('<path d="M-22,6 C-14,-6 14,-6 22,6" stroke-width="3.0"/>'
            '<path d="M-18,6 L-18,24 M18,6 L18,24" stroke-width="2.4"/>')

def thread():    # 玄/丝：回环之绳
    return ('<path d="M0,-26 C-18,-18 -18,4 0,10 C18,16 18,-6 0,-14" stroke-width="2.8"/>')

def two_hands(): # 共：两手相向
    return ('<path d="M-16,-20 L16,-20" stroke-width="2.8"/>'
            '<path d="M-14,-14 L-20,6 M14,-14 L20,6" stroke-width="2.4"/>'
            '<path d="M-20,6 L-24,18 M20,6 L24,18" stroke-width="2.4"/>')

def cloud():     # 云：回旋之气
    return ('<path d="M-22,8 C-14,-10 10,-10 14,6 C22,10 16,20 4,18" stroke-width="2.8"/>'
            '<path d="M-22,8 C-26,20 -12,24 0,22" stroke-width="2.4"/>')

def rain():      # 雨：天幕下点滴
    return ('<path d="M-26,-14 L26,-14" stroke-width="3.0"/>'
            + ''.join('<path d="M%d,-6 L%d,10" stroke-width="2.2"/>' % (x, x) for x in (-18,-8,2,12,22)))

def mouth_small():
    return '<path d="M-12,-8 L12,-8 L12,8 L-12,8 Z" stroke-width="2.4"/>'


def fish():      # 鱼：身、鳍、尾
    return ('<path d="M-20,0 C-10,-16 8,-16 18,0 C8,16 -10,16 -20,0 Z" stroke-width="3.0"/>'
            '<path d="M-20,0 L-30,-8 M-20,0 L-30,8" stroke-width="2.6"/>'
            '<path d="M0,-12 L0,12" stroke-width="2.2"/>'
            '<circle cx="10" cy="-4" r="2" fill="currentColor" stroke="none"/>')

def tiger():     # 虍：虎头
    return ('<path d="M-20,-8 C-16,-24 4,-26 12,-18" stroke-width="2.8"/>'
            '<path d="M-20,-8 L-20,10 M14,-14 L14,10" stroke-width="2.4"/>'
            '<path d="M-6,-12 L-6,-2 M4,-10 L4,0" stroke-width="2.2"/>')

def feather():   # 羽：一根羽
    return ('<path d="M0,-26 C-6,-10 -6,10 0,26" stroke-width="2.8"/>'
            + ''.join('<path d="M%d,%d L%d,%d" stroke-width="2.1"/>' % (0,y, s*x, y+4)
                      for (x,y,s) in ((-1,-16,-1),(-1,-6,-1),(1,4,1),(1,14,1)))
            )

def metal():     # 金：土中两点
    return ('<path d="M-24,6 L24,6" stroke-width="3.0"/>'
            '<circle cx="-10" cy="-6" r="3" fill="currentColor" stroke="none"/>'
            '<circle cx="8" cy="-6" r="3" fill="currentColor" stroke="none"/>'
            '<path d="M-16,10 L-16,24 M14,10 L14,24" stroke-width="2.4"/>')

COMP = dict(sun=sun, moon=moon, star=star, mountain=mountain, water=water, fire=fire,
            tree=tree, grain=grain, person=person, big=big_person, woman=woman, child=child,
            eye=eye, mouth=mouth, hand=hand, foot=foot, roof=roof, vessel=vessel,
            field=field, shell=shell, bow=bow, axe=axe, silk=silk, horse=horse, bird=bird,
            dragon=dragon, jade=jade, cloth=cloth, speech=speech, gate=gate, walk=walk,
            city=city, knife=knife, heart=heart, sound=sound, bar=bar, grass=grass,
            soil=soil, thread=thread, two_hands=two_hands, cloud=cloud, rain=rain,
            mouth_small=mouth_small, fish=fish, tiger=tiger, feather=feather, metal=metal)

def glyph(chars, size=64, cls=""):
    """按构件规格拼字；chars 为 [(构件名, dx, dy, scale, rot)]，返回内联 SVG"""
    body = []
    for spec in chars:
        name, dx, dy, sc, rot = (list(spec) + [0, 0, 1, 0])[:5]
        inner = COMP[name]()
        body.append(f'<g transform="translate({dx},{dy}) scale({sc}) rotate({rot})">{inner}</g>')
    return (f'<svg class="glyph {cls}" viewBox="-38 -40 76 80" width="{size}" height="{size}" '
            f'aria-hidden="true" stroke="currentColor" fill="none" style="color:#2E2620">{ "".join(body) }</svg>')
