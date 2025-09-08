# -*- coding: utf-8 -*-
"""
Typora가 삽입한 이미지 경로를 Jekyll 친화적 경로로 일괄 변환합니다.
대상:
  1) ![alt](../assets/images/foo.jpg)
  2) ![alt](./assets/images/foo.jpg)
  3) ![alt](/assets/images/foo.jpg)
  4) ![alt](C:\...\assets\images\foo.jpg)  # 윈도 경로
이미 relative_url 이 들어간 줄, http(s) 외부 URL은 건드리지 않습니다.
"""

import re
from pathlib import Path

ROOT = Path(__file__).parent
# 필요하면 확장자 추가 가능
EXTS = (".md", ".markdown")

# 정규식들
# 이미 변환된 줄은 건드리지 않기
already_ok = re.compile(r"relative_url\s*}}")

# http/https 외부 링크는 무시
is_http = re.compile(r"]\(\s*https?://", re.I)

# ../assets/images/foo.jpg  또는 ./assets/images/foo.jpg  또는 /assets/images/foo.jpg
p_assets_rel = re.compile(
    r"!\[([^\]]*)\]\(\s*(?:\.\./|\./|/)?assets/images/([^)]+?)\s*\)", re.I
)

# 윈도 경로 C:\...\assets\images\foo.jpg  또는 D:/...\assets/images/foo.jpg
p_assets_win = re.compile(
    r"!\[([^\]]*)\]\(\s*[A-Za-z]:[\\/].*?[\\/]assets[\\/]images[\\/]([^)\\/:]+)\s*\)", re.I
)

def convert_line(line: str) -> str:
    if already_ok.search(line) or is_http.search(line):
        return line
    # 순서 중요: 먼저 상대/절대 assets 패턴
    new = p_assets_rel.sub(r"![\1]({{ '/assets/images/\2' | relative_url }})", line)
    if new != line:
        return new
    # 윈도 경로 패턴
    new = p_assets_win.sub(r"![\1]({{ '/assets/images/\2' | relative_url }})", line)
    return new

def process_file(path: Path) -> bool:
    original = path.read_text(encoding="utf-8")
    lines = original.splitlines(keepends=True)
    changed = False
    for i, ln in enumerate(lines):
        new_ln = convert_line(ln)
        if new_ln != ln:
            lines[i] = new_ln
            changed = True
    if changed:
        path.write_text("".join(lines), encoding="utf-8")
    return changed

def main():
    md_files = [p for p in ROOT.rglob("*") if p.suffix.lower() in EXTS]
    touched = []
    for p in md_files:
        if process_file(p):
            touched.append(p)
    print(f"Processed {len(md_files)} files.")
    if touched:
        print("Updated:")
        for p in touched:
            print(" -", p.relative_to(ROOT))
    else:
        print("No changes were necessary.")

if __name__ == "__main__":
    main()
