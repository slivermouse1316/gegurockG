# -*- coding: utf-8 -*-
"""
Convert local/relative image links in Markdown to Jekyll's relative_url form.

Supported:
  ![alt](../assets/images/foo.jpg)
  ![alt](../../assets/images/foo.jpg)
  ![alt](./assets/images/foo.jpg)
  ![alt](/assets/images/foo.jpg)
  ![alt](assets/images/foo.jpg)
  <img src="../assets/images/foo.jpg">
"""

import re
from pathlib import Path

MD_EXTS = {".md", ".markdown"}

# ✅ 리포 루트를 현재 작업 디렉터리로 고정 (스크립트를 어디서 실행하든 안전)
ROOT = Path.cwd()

# 마크다운 이미지 / HTML <img> 캡처
MD_IMG = re.compile(r'(!\[[^\]]*\]\()(?P<url>[^)]+)(\))')
HTML_IMG = re.compile(r'(<img[^>]*\bsrc=["\'])(?P<url>[^"\']+)(["\'])', re.IGNORECASE)

# assets/images 경로 탐지: ../ 또는 ./ 가 여러 번 나와도 OK, \도 /로 정규화
ASSETS_PATH = re.compile(r'(?:\.{1,2}/)*assets/images/.*', re.IGNORECASE)

def _normalize_to_site_path(url: str) -> str | None:
    # Windows 구분자 정규화
    u = url.replace("\\", "/").strip()

    # 따옴표/타이틀 제거 (e.g., foo.png "caption")
    if " " in u and not u.startswith("http"):
        u = u.split(" ")[0]

    # 외부 링크는 제외
    if u.startswith(("http://", "https://")):
        return None

    # assets/images/ 이하만 허용
    m = ASSETS_PATH.search(u)
    if not m:
        return None

    path = m.group(0)
    # 앞쪽 ../ ./ 제거 후 선행 슬래시 붙이기
    path = re.sub(r'^(?:\.{1,2}/)+', "", path)
    if not path.startswith("/"):
        path = "/" + path
    # 이중 슬래시 정리
    path = re.sub(r"/{2,}", "/", path)
    return path

def _sub_image_url(url: str) -> str:
    site_path = _normalize_to_site_path(url)
    if site_path:
        return "{{ '" + site_path + "' | relative_url }}"
    return url  # 매칭 안 되면 원본 유지

def convert_line(line: str) -> str:
    # 마크다운 ![]() 안의 url만 치환
    def _md_sub(m):
        url = m.group("url")
        return f"{m.group(1)}{_sub_image_url(url)}{m.group(3)}"

    # HTML <img src="..."> 의 url만 치환
    def _html_sub(m):
        url = m.group("url")
        return f"{m.group(1)}{_sub_image_url(url)}{m.group(3)}"

    new_line = MD_IMG.sub(_md_sub, line)
    new_line = HTML_IMG.sub(_html_sub, new_line)
    return new_line

def process_file(fp: Path) -> bool:
    orig = fp.read_text(encoding="utf-8", errors="replace")
    lines = orig.splitlines(keepends=True)
    new_lines = []
    changed = False
    for ln in lines:
        nl = convert_line(ln)
        if nl != ln:
            changed = True
        new_lines.append(nl)
    if changed:
        bak = fp.with_suffix(fp.suffix + ".bak")
        if not bak.exists():
            bak.write_text(orig, encoding="utf-8")
        fp.write_text("".join(new_lines), encoding="utf-8")
    return changed

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
