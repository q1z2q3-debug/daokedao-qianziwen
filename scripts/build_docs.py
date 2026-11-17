#!/usr/bin/env python3
"""把阅读版同步到 docs/，供 GitHub Pages 使用。"""
from pathlib import Path
import shutil
ROOT = Path(__file__).resolve().parent.parent
src = ROOT / "book" / "润泽说-蒙学之千字文·阅读版.html"
dst = ROOT / "docs" / "book.html"
if not src.exists():
    raise SystemExit(f"缺阅读版：{src}")
shutil.copyfile(src, dst)
print(f"{dst}  {dst.stat().st_size} bytes")
