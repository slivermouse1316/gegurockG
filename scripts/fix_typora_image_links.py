# convert_images_verbose.py
# -*- coding: utf-8 -*-
"""
Fix Typora-style image links to Jekyll {{ '...'/ | relative_url }} in Markdown.

Supported inputs:
  ![alt](../assets/images/foo.jpg)
  ![alt](../../assets/images/foo.jpg)
  ![alt](./assets/images/foo.jpg)
  ![alt](/assets/images/foo.jpg)
  ![alt](assets/images/foo.jpg)
  ![alt](<../assets/images/foo.jpg>)       # angle brackets OK
  <img src="../assets/images/foo.jpg">

Also supports filenames with spaces and parentheses, e.g.
  ![](/assets/images/그림3 (소형)-1762866200013-1.png)
"""

import re
import sys
from pathlib import Path

# -------- Settings --------
MD_EXTS = {".md", ".markdown"}

# Markdown image: capture URL greedily so filenames with ')' don't get cut.
# Groups:
#   1: opening '![alt]('
#   url: <...> OR anything up to the last ')' (greedy)
#   trailer: optional "title" and the final ')'
MD_IMG = re.compile(
    r'(!\[[^\]]*\]\()\s*(?P<url><[^>]+>|.*)(?P<trailer>\s*(?:"[^"]*"|\'[^\']*\')?\))'
)

# HTML <img src="..."> (case-insensitive)
HTML_IMG = re.compile(r'(<img[^>]*\bsrc=["\'])(?P<url>[^"\']+)(["\'])', re.IGNORECASE)

# Match assets/images path with ../ or ./ repeated, also backslashes
ASSETS_PATH = re.compile(r'(?:\.{1,2}/)*assets[/\\]images[/\\].*', re.IGNORECASE)


def _normalize_to_site_path(url: str) -> str | None:
    u = url.strip()

    # strip wrapping quotes "..." or '...'
    if (u.startswith('"') and u.endswith('"')) or (u.startswith("'") and u.endswith("'")):
        u = u[1:-1]
    # strip wrapping angle brackets: <...>
    if u.startswith("<") and u.endswith(">"):
        u = u[1:-1]

    # normalize slashes
    u = u.replace("\\", "/")

    # skip external or already-liquid
    if u.startswith(("http://", "https://")) or "relative_url" in u:
        return None

    # NOTE: do NOT split on space here; the title part is handled by regex 'trailer'

    m = ASSETS_PATH.search(u)
    if not m:
        return None

    path = m.group(0).replace("\\", "/")

    # remove leading ../ or ./ repeats
    path = re.sub(r'^(?:\.{1,2}/)+', "", path)
    # collapse /./
    path = re.sub(r'/\./', '/', path)
    # ensure single leading slash
    if not path.startswith("/"):
        path = "/" + path
    # collapse multiple slashes
    path = re.sub(r"/{2,}", "/", path)

    # (optional) If your host dislikes spaces in URLs, uncomment:
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
        trailer = m.group("trailer")  # preserves optional "title" and final ')'
        rep = _to_liquid(url)
        if rep:
            changed = True
            print(f"  [md] {file}:{lineno}  {url}  ->  {rep}")
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
    # If an arg is provided, treat it as the repo root.
    # Otherwise default to the parent of this script (…/scripts -> repo root).
    root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
    print(f"ROOT = {root}")

    cnt = 0
    for f in root.rglob("*"):
        if process_file(f):
            cnt += 1
    print(f"Done. Updated {cnt} file(s).")


if __name__ == "__main__":
    main()
