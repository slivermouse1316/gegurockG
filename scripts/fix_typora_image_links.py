# -*- coding: utf-8 -*-
"""
Typora가 삽입하는 이미지 링크를 Jekyll 권장형식으로 일괄 변환:
  ![alt](../assets/images/foo.jpg)
  ![alt](./assets/images/foo.jpg)
  ![alt](/assets/images/foo.jpg)
  ![alt](C:\...\assets\images\foo.jpg)
→ ![alt]({{ '/assets/images/foo.jpg' | relative_url }})

- 이미 relative_url이 들어간 줄, http(s) 외부 링크는 건드리지 않음
- 모든 .md, .markdown 파일 대상
- 원본 파일은 .bak로 백업
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MD_EXTS = {".md", ".markdown"}

# 스킵 조건: 이미 변환됨 / 외부 URL
rx_skip = re.compile(r"relative_url\s*}}|]\(\s*https?://", re.I)

# ../assets/images/foo.jpg  ./assets/images/foo.jpg  /assets/images/foo.jpg  (공백·괄호 방지)
rx_assets_rel = re.compile(
    r"!\[([^\]]*)\]\(\s*(?:\.\./|\./|/)?assets/images/([^)#\s]+?)\s*\)", re.I
)

# 윈도 경로 C:\...\assets\images\foo.jpg  또는 D:/...\assets/images/foo.jpg
rx_assets_win = re.compile(
    r"!\[([^\]]*)\]\(\s*[A-Za-z]:[\\/].*?[\\/]assets[\\/]images[\\/]+([^)\\/:#\s]+)\s*\)", re.I
)

def convert_text(text: str) -> str:
    # 이미 변환/외부URL 포함 라인은 그대로 두기
    if rx_skip.search(text):
        return text
    text2 = rx_assets_rel.sub(r"![\1]({{ '/assets/images/\2' | relative_url }})", text)
    text2 = rx_assets_win.sub(r"![\1]({{ '/assets/images/\2' | relative_url }})", text2)
    return text2

def process_file(p: Path) -> bool:
    try:
        original = p.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        # CP949 등으로 저장된 경우에도 동작하도록
        original = p.read_text(encoding="cp949")

    new = convert_text(original)
    if new != original:
        # 백업 저장
        p.with_suffix(p.suffix + ".bak").write_text(original, encoding="utf-8")
        p.write_text(new, encoding="utf-8")
        return True
    return False

def main():
    md_files = [f for f in ROOT.rglob("*") if f.suffix.lower() in MD_EXTS]
    touched = 0
    for f in md_files:
        if process_file(f):
            touched += 1
            print(f"[fixed] {f.relative_to(ROOT)}")
    print(f"Done. Updated {touched} file(s). ROOT={ROOT}")

if __name__ == "__main__":
    main()
