# 按《字源全解》构形文自动拼字：解析「从X、从Y、Z声」，落到构件库
import re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import oracle_map, oracle_glyph

RAD = {'水':'water','氵':'water','冫':'water','艸':'grass','艹':'grass','木':'tree','人':'person',
 '亻':'person','女':'woman','子':'child','宀':'roof','門':'gate','门':'gate','土':'soil','田':'field',
 '貝':'shell','贝':'shell','刀':'knife','弓':'bow','戈':'axe','糸':'silk','纟':'silk','馬':'horse',
 '鸟':'bird','鳥':'bird','龍':'dragon','玉':'jade','巾':'cloth','言':'sound','讠':'sound','彳':'walk',
 '行':'walk','邑':'city','阝':'city','衣':'cloth','日':'sun','月':'moon','山':'mountain','火':'fire',
 '禾':'grain','示':'altar','礻':'altar','耳':'ear','竹':'bamboo','羊':'sheep','谷':'valley','网':'net',
 '首':'head','食':'food','鼓':'drum','金':'metal','魚':'fish','鱼':'fish','虎':'tiger','羽':'feather',
 '舟':'vessel','車':'vessel','页':'head','頁':'head','見':'eye','见':'eye','攵':'hand','攴':'hand',
 '殳':'hand','又':'hand','爪':'hand','廾':'two_hands','臼':'two_hands','耒':'hand','斗':'vessel',
 '匕':'person','儿':'person','尸':'person','卩':'person','冖':'roof','广':'roof','穴':'roof',
 '厂':'mountain','厶':'thread','虫':'dragon','黽':'dragon','隹':'bird','燕':'bird','音':'sound',
 '革':'cloth','韋':'cloth','韦':'cloth','髟':'thread','里':'field','牜':'horse','牛':'horse',
 '犬':'tiger','豕':'tiger','豸':'tiger','而':'feather','非':'feather','白':'sun','自':'head',
 '矢':'bar','斤':'axe','刃':'knife','勺':'vessel','缶':'vessel','鬲':'vessel','斝':'vessel',
 '目':'eye','口':'mouth','手':'hand','心':'heart','足':'foot','止':'foot','大':'big',
 '門':'gate','車':'vessel','鼎':'vessel','豆':'vessel','酉':'vessel','皿':'vessel','缶':'vessel'}

def comps(text):
    # 取「从」后首个实字，去掉括号注释
    t = re.sub(r'（[^）]*）', '', text)
    out = []
    for m in re.finditer(r'从([^\s、，。；]+)', t):
        ch = m.group(1)[0]
        out.append(RAD.get(ch, None) if ch in RAD else None)
    # 声符：X声
    ph = None
    m = re.search(r'从?([^\s、，。；]{1})(?:声|為聲|为声)', t)
    if m:
        ph = m.group(1)[0]
    return [c for c in out if c], ph

def build(char, text, depth=0):
    ss, ph = comps(text)
    if not ss and depth < 2:
        # 退一步：从字若已被拼过，取其字形为构件
        t = re.sub(r'（[^）]*）', '', text)
        cs = [m.group(1)[0] for m in re.finditer(r'从([^\s、，。；]+)', t)]
        for c in cs:
            sub = oracle_map.M.get(c)
            if sub:
                ss = [('@', c)]
    specs = []
    if not ss:
        return None
    n = min(len(ss), 3)
    ys = {1: [0], 2: [-15, 15], 3: [-22, 0, 22]}[n]
    for i, c in enumerate(ss[:n]):
        specs.append((c, 0, ys[i], .8 if n == 1 else .58, 0))
    return specs


PATCH = {
 "馨":[("sound",0,-12,.7,0),("bar",0,16,.8,0)], "不":[("grass",0,10,.7,0),("bar",0,-14,.9,0)],
 "辞":[("mouth",-10,0,.75,0),("knife",12,0,.7,0)], "甚":[("mouth",-8,6,.8,0),("person",12,-4,.7,0)],
 "而":[("feather",0,0,.9,0)], "随":[("walk",-12,0,.75,0),("hand",12,2,.7,0)],
 "外":[("moon",-10,0,.65,0),("bar",12,6,.8,90)], "入":[("vessel",0,8,.8,0),("foot",0,-16,.6,180)],
 "交":[("person",-8,0,.75,0),("person",8,0,.75,180)], "隐":[("city",-10,2,.75,0),("hand",12,-2,.7,0)],
 "造":[("walk",-12,0,.75,0),("mouth_small",12,2,.75,0)], "次":[("person",0,6,.75,0),("bar",0,-14,.9,0)],
 "弗":[("thread",0,0,.95,0)], "亏":[("bar",0,-10,.9,0),("vessel",0,12,.7,0)],
 "静":[("water",-10,6,.7,0),("hand",12,-4,.75,0)], "逸":[("walk",-12,0,.7,0),("tiger",12,-2,.6,0)],
 "疲":[("person",-8,0,.8,0),("vessel",12,4,.6,0)], "自":[("head",0,0,.9,0)],
 "东":[("cloth",0,0,.85,0),("bar",0,0,.7,90)], "二":[("bar",0,-10,.9,0),("bar",0,10,.9,0)],
 "京":[("roof",0,-12,.8,0),("bar",0,12,.9,0)], "背":[("cloth",-8,0,.7,0),("feather",10,-2,.6,0)],
 "图":[("mouth_small",0,0,1.1,0),("field",0,0,.55,0)], "禽":[("net",0,-10,.85,0),("hand",0,14,.65,0)],
 "彩":[("feather",-8,0,.6,0),("hand",10,-2,.75,0)], "丙":[("vessel",0,0,.8,0)],
 "肆":[("thread",0,-8,.7,0),("bar",0,16,.85,0)], "瑟":[("jade",0,-10,.7,0),("thread",0,12,.6,0)],
 "阶":[("city",-10,2,.75,0),("hand",12,-2,.7,0)], "陛":[("city",-10,2,.75,0),("soil",12,4,.6,0)],
 "通":[("walk",-12,0,.75,0),("vessel",12,0,.7,0)], "内":[("vessel",0,8,.8,0),("foot",0,-14,.55,180)],
 "达":[("walk",-10,0,.75,0),("big",12,2,.7,0)], "八":[("bar",-10,0,.85,90),("bar",10,0,.85,90)],
 "高":[("roof",0,-16,.75,0),("bar",0,-2,.85,0),("bar",0,16,.85,0)],
 "陪":[("city",-10,2,.75,0),("mouth_small",12,2,.75,0)],
 "世":[("bar",-10,-14,.7,90),("bar",0,-16,.7,90),("bar",10,-14,.7,90),("bar",0,8,.9,0)],
 "肥":[("mouth",-8,0,.7,0),("dragon",12,0,.6,0)], "阿":[("city",-10,2,.75,0),("mouth",12,2,.7,0)],
 "曲":[("mouth_small",0,-2,.95,0),("bar",0,-2,.7,90)],
 "孰":[("two_hands",0,-10,.7,0),("food",0,14,.7,0)], "营":[("roof",0,-12,.8,0),("fire",0,12,.6,0)],
 "回":[("thread",0,0,.95,0),("thread",0,0,.5,180)], "丁":[("bar",0,-8,.9,0),("bar",0,10,.85,90)],
 "乂":[("bar",0,0,.9,45),("bar",0,0,.9,-45)], "勿":[("cloth",0,-8,.7,0),("bar",0,12,.85,0)],
 "多":[("moon",-8,0,.6,0),("moon",10,0,.6,180)], "赵":[("walk",-12,0,.7,0),("feather",12,-2,.6,0)],
 "魏":[("tiger",-8,0,.7,0),("woman",10,0,.6,0)], "途":[("walk",-12,0,.75,0),("vessel",12,0,.7,0)],
 "虢":[("tiger",0,-10,.7,0),("hand",0,14,.6,0)], "用":[("vessel",0,0,.85,0)],
 "丹":[("field",0,0,.7,0),("sun",0,0,.22,0)], "九":[("thread",0,0,.95,0)],
 "亭":[("roof",0,-14,.8,0),("bar",0,12,.9,0)], "远":[("walk",-12,0,.75,0),("person",12,2,.7,0)],
 "邈":[("walk",-12,0,.7,0),("feather",12,-2,.6,0)], "南":[("drum",0,0,.85,0)],
 "黜":[("fire",0,-10,.7,0),("soil",0,12,.7,0)], "陟":[("city",-12,0,.7,0),("foot",6,-8,.55,0),("foot",14,8,.55,0)],
 "几":[("bar",0,-6,.85,0),("bar",0,10,.85,0)], "庸":[("vessel",-8,0,.7,0),("hand",12,0,.7,0)],
 "嘉":[("drum",-8,0,.7,0),("hand",12,0,.65,0)], "其":[("net",0,4,.7,0),("two_hands",0,-14,.6,0)],
 "殆":[("person",-8,0,.75,0),("mouth_small",12,2,.75,0)], "疏":[("foot",-8,0,.7,0),("water",12,2,.7,0)],
 "逼":[("walk",-12,0,.75,0),("field",12,0,.6,0)], "处":[("foot",0,-6,.85,0),("bar",0,16,.85,0)],
 "逍":[("walk",-12,0,.7,0),("hand",12,0,.7,0)], "遥":[("walk",-12,0,.7,0),("vessel",12,0,.7,0)],
 "遣":[("walk",-10,0,.75,0),("hand",12,0,.7,0)], "欢":[("person",-8,0,.75,0),("bird",12,-2,.7,0)],
 "园":[("mouth_small",0,0,1.1,0),("person",0,0,.5,0)], "陈":[("city",-10,2,.75,0),("cloth",12,0,.7,0)],
 "飘":[("feather",-8,0,.65,0),("sun",10,2,.45,0)], "运":[("walk",-12,0,.7,0),("vessel",12,0,.7,0)],
 "畏":[("tiger",0,-8,.75,0),("bar",0,16,.8,0)], "属":[("dragon",0,-4,.6,0),("foot",0,16,.6,0)],
 "适":[("walk",-12,0,.75,0),("mouth_small",12,2,.75,0)], "肠":[("person",-8,0,.7,0),("sun",12,2,.5,0)],
 "少":[("child",0,0,.85,0),("bar",0,18,.85,0)], "圆":[("mouth_small",0,0,1.1,0),("shell",0,0,.5,0)],
 "歌":[("person",-8,0,.7,0),("sound",12,2,.65,0)], "豫":[("dragon",-8,0,.65,0),("hand",12,0,.65,0)],
 "且":[("vessel",0,0,.9,0)], "嗣":[("bamboo",-10,0,.7,0),("mouth",12,2,.7,0)],
 "牒":[("cloth",-8,0,.7,0),("tree",12,0,.65,0)], "骸":[("net",0,-8,.7,0),("person",0,14,.6,0)],
 "超":[("walk",-12,0,.7,0),("hand",12,0,.7,0)], "叛":[("hand",-8,0,.75,0),("bar",12,2,.8,60)],
 "丸":[("thread",0,0,.9,0),("sun",0,0,.2,0)], "琴":[("jade",0,-10,.7,0),("thread",0,12,.6,0)],
 "阮":[("city",-10,2,.7,0),("person",12,2,.7,0)], "巧":[("hand",0,-8,.8,0),("thread",0,14,.6,0)],
 "释":[("hand",-8,0,.75,0),("eye",12,0,.7,0)], "毛":[("feather",0,0,.95,0)],
 "施":[("cloth",-8,0,.7,0),("person",12,0,.7,0)], "工":[("bar",0,-8,.85,0),("bar",0,10,.85,90)],
 "颦":[("head",0,-6,.7,0),("hand",0,16,.6,0)], "矢":[("bar",0,2,.95,0),("foot",0,-20,.45,180)],
 "修":[("feather",-8,0,.6,0),("hand",12,-2,.75,0)], "矜":[("bar",-6,0,.9,0),("hand",12,4,.6,0)],
 "陋":[("city",-10,2,.7,0),("vessel",12,0,.65,0)],
 "乎":[("mouth_small",0,0,.85,0),("bar",-13,2,.6,0),("bar",13,2,.6,0)],
 "也":[("dragon",0,0,.9,0)],
}

def main():
    md = Path('book/字源全解-一千字.md').read_text()
    rows = re.findall(r'^\| ([^\s|]) \| ([^|]*) \| ([^|]*) \|', md, re.M)
    gen = {}
    KW = [('木','tree'),('林','tree'),('水','water'),('川','water'),('泉','water'),('雨','rain'),
          ('山','mountain'),('火','fire'),('日','sun'),('月','moon'),('星','star'),('云','cloud'),
          ('鸟','bird'),('隹','bird'),('马','horse'),('牛','horse'),('羊','sheep'),('犬','tiger'),
          ('虎','tiger'),('鱼','fish'),('虫','dragon'),('龍','dragon'),('龙','dragon'),('羽','feather'),
          ('目','eye'),('眼','eye'),('口','mouth'),('齿','mouth'),('耳','ear'),('手','hand'),('指','hand'),
          ('足','foot'),('趾','foot'),('心','heart'),('女','woman'),('母','woman'),('子','child'),
          ('儿','child'),('人','person'),('首','head'),('头','head'),('面','head'),('身','person'),
          ('衣','cloth'),('巾','cloth'),('冠','cloth'),('帽','cloth'),('屋','roof'),('室','roof'),
          ('门','gate'),('門','gate'),('户','gate'),('田','field'),('土','soil'),('石','mountain'),
          ('玉','jade'),('贝','shell'),('錢','shell'),('金','metal'),('刀','knife'),('剑','knife'),
          ('弓','bow'),('矢','bar'),('戈','axe'),('斤','axe'),('车','vessel'),('舟','vessel'),
          ('鼎','vessel'),('豆','vessel'),('壶','vessel'),('尊','vessel'),('爵','vessel'),
          ('丝','silk'),('糸','silk'),('网','net'),('竹','bamboo'),('草','grass'),('禾','grain'),
          ('米','grain'),('麦','grain'),('酒','water'),('示','altar'),('祭','altar'),('言','sound'),
          ('音','sound'),('鼓','drum'),('食','food'),('饭','food')]
    for ch, mean, shape in rows:
        if ch in ('字',) or ch in oracle_map.M:
            continue
        s = build(ch, shape)
        if not s and ch in PATCH:
            s = PATCH[ch]
        if not s:
            txt = shape + mean
            for k, c in KW:
                if k in txt:
                    s = [(c, 0, 0, .8, 0)]
                    break
        if s:
            gen[ch] = s
    out = 'M_AUTO = ' + repr(gen)
    Path('scripts/oracle_map_auto.py').write_text('# 自动拼字表：由构形文解析，义符为主\n' + out + '\n')
    print('自动拼出', len(gen), '字；仍缺', 1000 - len(gen) - len(oracle_map.M))

if __name__ == '__main__':
    main()
