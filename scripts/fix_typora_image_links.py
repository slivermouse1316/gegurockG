# convert_images_verbose.py
# -*- coding: utf-8 -*-
import re
import sys
from pathlib import Path

MD_EXTS = {".md", ".markdown"}

# CHANGED: Markdown 이미지 패턴 (URL, optional "title", ) 를 분리 캡처
#  - URL: <...> 또는 닫는 괄호 전까지를 넉넉히 캡처(공백/괄호 허용)
#  - trailer: 선택적 "제목" + 닫는 )
MD_IMG = re.compile(
    r'(!\[[^\]]*\]\()\s*(?P<url><[^>]+>|.*?)(?P<trailer>\s*(?:"[^"]*"|\'[^\']*\')?\))'
)

# HTML <img src="..."> 는 기존대로
HTML_IMG = re.compile(r'(<img[^>]*\bsrc=["\'])(?P<url>[^"\']+)(["\'])', re.IGNORECASE)

# assets/images 경로 인식 (../, ./, 백슬래시 등 허용)
ASSETS_PATH = re.compile(r'(?:\.{1,2}/)*assets[/\\]images[/\\].*', re.IGNORECASE)

def _normalize_to_site_path(url: str) -> str | None:
    u = url.strip()

    # 양쪽 따옴표 제거
    if (u.startswith('"') and u.endswith('"')) or (u.startswith("'") and u.endswith("'")):
        u = u[1:-1]
    # <...> 감싸기 제거
    if u.startswith("<") and u.endswith(">"):
        u = u[1:-1]

    # 슬래시 통일
    u = u.replace("\\", "/")

    # 외부 링크나 이미 liquid면 스킵
    if u.startswith(("http://", "https://")) or "relative_url" in u:
        return None

    # CHANGED: 더 이상 "공백 이후 제목"으로 가정해서 자르지 않음
    # (제목은 정규식 trailer로 따로 분리했기 때문에 여기서 자를 필요 없음)

    m = ASSETS_PATH.search(u)
    if not m:
        return None

    path = m.group(0).replace("\\", "/")

    # ./, ../ 제거
    path = re.sub(r'^(?:\.{1,2}/)+', "", path)
    # /./ 접기
    path = re.sub(r'/\./', '/', path)
    # 선행 슬래시 보장
    if not path.startswith("/"):
        path = "/" + path
    # 다중 슬래시 정리
    path = re.sub(r"/{2,}", "/", path)

    # (선택) 필요 시 공백을 %20으로 인코딩하려면 아래 주석 해제
    # path = path.replace(" ", "%20")

    return path

def _to_liquid(url: str) -> str | None:
    site_path = _normalize_to_site_path(url)
    if site_path:
        return "{{ '" + site_path + "' | relative_url }}"
    return None

def convert_line(line: str, file: str, lineno: int) -> tuple[str, bool]:
    changed = False

    def _md_sub(m):
        nonlocal changed
        url = m.group("url")
        trailer = m.group("trailer")  # 제목+닫는 괄호 유지
        rep = _to_liquid(url)
        if rep:
            changed = True
            print(f"  [md] {file}:{lineno}  {url}  ->  {rep}")
            # 앞부분( ![...]() ) + 변환된 URL + 원래 trailer(제목/닫괄호)
            return f"{m.group(1)}{rep}{trailer}"
        return m.group(0)

    def _html_sub(m):
        nonlocal changed
        url = m.group("url")
        rep = _to_liquid(url)
        if rep:
            changed = True
            print(f"  [html] {file}:{lineno}  {url}  ->  {rep}")
            return f"{m.group(1)}{rep}{m.group(3)}"
        return m.group(0)

    new_line = MD_IMG.sub(_md_sub, line)
    new_line = HTML_IMG.sub(_html_sub, new_line)
    return new_line, changed

def process_file(fp: Path) -> bool:
    try:
        if not fp.is_file():
            return False
        if fp.suffix.lower() not in MD_EXTS:
            return False

        orig = fp.read_text(encoding="utf-8", errors="replace")
        out_lines = []
        touched = False
        for i, ln in enumerate(orig.splitlines(keepends=True), 1):
            nl, ch = convert_line(ln, str(fp), i)
            if ch:
                touched = True
            out_lines.append(nl)

        if touched:
            bak = fp.with_suffix(fp.suffix + ".bak")
            if not bak.exists():
                bak.write_text(orig, encoding="utf-8")
            fp.write_text("".join(out_lines), encoding="utf-8")
            print(f"[fixed] {fp}")
        return touched

    except Exception as e:
        print(f"[skip:{type(e).__name__}] {fp} -> {e}")
        return False

def main():
    root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
    print(f"ROOT = {root}")
    cnt = 0
    for f in root.rglob("*"):
        if process_file(f):
            cnt += 1
    print(f"Done. Updated {cnt} file(s).")

if __name__ == "__main__":
    main()
