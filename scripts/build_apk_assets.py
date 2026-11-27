# -*- coding: utf-8 -*-
"""把书库 docs/ 的离线可读部分灌进 APK 资产，可反复重跑。

用法：python3 scripts/build_apk_assets.py   （在书库根运行，读 dist/apk-<slug>/apk-config.json）

做的事：
1. 复制 entry、copy_files、copy_dirs 声明的文件/目录到 app/src/main/assets；
2. 站内绝对地址（site_prefixes）按页深改写为相对路径；裸 index.html 回链按层补 ../；
3. 剥除 strip_blocks 包住的块、strip_hrefs 链接、strip_link_regex 命中的 <link>；
4. 取全部用字，从系统 NotoSerifCJK 子集化 woff2，逐页注入 @font-face（家族名沿用页面 CSS 里的名字）。
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

def repo_root():
    """从脚本位置向上找含 docs/ 的书库根（脚本放 scripts/ 或 dist/apk-*/ 都行）。"""
    d = os.path.dirname(os.path.abspath(__file__))
    for _ in range(6):
        if os.path.isdir(os.path.join(d, 'docs')):
            return d
        d = os.path.dirname(d)
    raise SystemExit('找不到书库根（缺 docs/）')


ROOT = repo_root()


def load_config():
    slug = sys.argv[1] if len(sys.argv) > 1 else None
    if not slug:
        cands = [d for d in os.listdir(os.path.join(ROOT, 'dist'))
                 if d.startswith('apk-') and os.path.isdir(os.path.join(ROOT, 'dist', d))]
        if len(cands) != 1:
            sys.exit('多个 apk-* 工程，请显式传 slug：%s' % ' '.join(cands))
        slug = cands[0][4:]
    path = os.path.join(ROOT, 'dist', 'apk-' + slug, 'apk-config.json')
    cfg = json.load(open(path, encoding='utf-8'))
    cfg['_slug'] = slug
    cfg['_assets'] = os.path.join(ROOT, 'dist', 'apk-' + slug, 'app', 'src', 'main', 'assets')
    cfg['_docs'] = os.path.join(ROOT, cfg.get('docs', 'docs'))
    return cfg


def depth_prefix(dirpath, assets):
    if dirpath == assets:
        return ''
    return '../' * (os.path.relpath(dirpath, assets).count(os.sep) + 1)


def rewrite_html(path, prefix, cfg):
    s = open(path, encoding='utf-8').read()
    n = 0
    for p in cfg.get('site_prefixes', []):
        n += s.count(p)
        s = s.replace(p, prefix)
    if cfg.get('bare_index_fix') and prefix:
        # ke/ 里回首页的裸 index.html 需补层；先改 href="index.html"，再兜住无前缀的 x.html
        s = s.replace('href="index.html"', 'href="%sindex.html"' % prefix)
    for start, end in cfg.get('strip_blocks', []):
        s, k = re.subn(re.escape(start) + r'[\s\S]*?' + re.escape(end) + r'\n?', '', s)
        n += k
    for href in cfg.get('strip_hrefs', []):
        s, k = re.subn(r'<a href="%s">[^<]*</a>' % re.escape(href), '', s)
        n += k
    for pat in cfg.get('strip_link_regex', []):
        s, k = re.subn(r'[ \t]*<link[^>]*%s[^>]*>\s*\n?' % pat, '', s)
        n += k
    open(path, 'w', encoding='utf-8').write(s)
    return n


def collect_chars(assets):
    chars = set('　-~\u00a0\u3000，。、；：？！“”‘’（）《》〈〉「」『』【】…—～·・％‰')
    for dirpath, _, files in os.walk(assets):
        for f in files:
            if not f.endswith('.html'):
                continue
            s = open(os.path.join(dirpath, f), encoding='utf-8').read()
            s = re.sub(r'<script[\s\S]*?</script>|<style[\s\S]*?</style>', '', s)
            s = re.sub(r'<[^>]+>', '', s)
            for a, b in (('&nbsp;', ' '), ('&amp;', '&'), ('&lt;', '<'), ('&gt;', '>')):
                s = s.replace(a, b)
            chars |= set(s)
    return ''.join(sorted(c for c in chars if c.isprintable()))


def embed_fonts(cfg):
    font = cfg.get('font')
    if not font:
        return 0, []
    family = font.get('family', 'Noto Serif SC')
    assets = cfg['_assets']
    out = os.path.join(assets, 'fonts')
    os.makedirs(out, exist_ok=True)
    text = collect_chars(assets)
    tf = tempfile.NamedTemporaryFile('w', suffix='.txt', delete=False, encoding='utf-8')
    tf.write(text)
    tf.close()
    made = []
    faces = []
    for w, (ttc, idx) in font['weights'].items():
        if not os.path.exists(ttc):
            raise SystemExit('缺字体文件：%s（Debian/Ubuntu 装 fonts-noto-cjk）' % ttc)
        name = 'serif-%s.woff2' % w
        dst = os.path.join(out, name)
        subprocess.run(['pyftsubset', ttc, '--font-number=%d' % idx, '--flavor=woff2',
                        '--text-file=%s' % tf.name, '--layout-features=kern,vert,palt',
                        '--output-file=%s' % dst], check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        made.append((w, os.path.getsize(dst)))
        faces.append((w, name))
    os.unlink(tf.name)

    for dirpath, _, files in os.walk(assets):
        for f in files:
            if not f.endswith('.html'):
                continue
            path = os.path.join(dirpath, f)
            prefix = depth_prefix(dirpath, assets)
            s = open(path, encoding='utf-8').read()
            if 'data-lunyu-serif' in s:
                continue
            css = ''.join(
                '@font-face{font-family:"%s";font-style:normal;font-weight:%s;'
                'font-display:swap;src:url("%sfonts/%s") format("woff2")}' % (family, w, prefix, name)
                for w, name in faces)
            s = s.replace('</head>', '<style data-lunyu-serif>%s</style>\n</head>' % css, 1)
            open(path, 'w', encoding='utf-8').write(s)
    return len(text), made


def copy_tree(src, dst, skip):
    if os.path.isdir(dst):
        shutil.rmtree(dst)
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns(*skip))


def main():
    cfg = load_config()
    assets, docs = cfg['_assets'], cfg['_docs']
    if os.path.isdir(assets):
        shutil.rmtree(assets)
    os.makedirs(assets)

    for name in cfg.get('copy_files', []):
        src = os.path.join(docs, name)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(assets, name))

    for item in cfg.get('copy_dirs', []):
        d, skip = (item, []) if isinstance(item, str) else (item[0], item[1])
        copy_tree(os.path.join(docs, d), os.path.join(assets, d), skip)

    n_links = 0
    for dirpath, _, files in os.walk(assets):
        for f in files:
            if f.endswith('.html'):
                n_links += rewrite_html(os.path.join(dirpath, f), depth_prefix(dirpath, assets), cfg)

    n_chars, made = embed_fonts(cfg)
    size = sum(os.path.getsize(os.path.join(d, f))
               for d, _, fs in os.walk(assets) for f in fs)
    print('assets %.2f MB；改写/剥除 %d 处' % (size / 1048576, n_links))
    if made:
        print('字集 %d 字；字重 %s' % (n_chars, '，'.join('%s %.1f MB' % (w, s / 1048576) for w, s in made)))
    for d in cfg.get('copy_dirs', []):
        name = d if isinstance(d, str) else d[0]
        print('%s %d 页' % (name, len(os.listdir(os.path.join(assets, name)))))


if __name__ == '__main__':
    main()
