# -*- coding: utf-8 -*-
"""
Convert local/relative image links in Markdown to Jekyll's relative_url form.

Examples converted:
  ![alt](../assets/images/foo.jpg)      -> ![alt]({{ '/assets/images/foo.jpg' | relative_url }})
  ![alt](./assets/images/foo.jpg)       -> same
  ![alt](/assets/images/foo.jpg)        -> same
  ![alt](assets/images/foo.jpg)         -> same
  ![alt](..\assets\images\foo.jpg)      -> same (Windows backslashes)
  <img src="../assets/images/foo.jpg">  -> <img src="{{ '/assets/images/foo.jpg' | relative_url }}">

Won't touch lines that already contain 'relative_url', Liquid '{{', or 'http(s)://' links.

Backups: create .bak once per file if we change it.
"""
import re
from pathlib import Path

MD_EXTS = {".md", ".markdown"}
ROOT = Path(__file__).resolve().parents[1]

# Detect markdown image syntax and HTML <img ...> tags
MD_IMG = re.compile(r'(!\[[^\]]*\]\()(?P<url>[^)]+)(\))')
HTML_IMG = re.compile(r'(<img[^>]*\bsrc=["\'])(?P<url>[^"\']+)(["\'])', re.IGNORECASE)

# Matching any assets/images path with optional ../, ./, /, or bare, and either / or \ separators
ASSET_RE = re.compile(
    r'(?P<prefix>(?:\.\./|\./|/)?|)(?P<assets>(?:assets[/\\\\]images[/\\\\].+))',
    re.IGNORECASE
)

def _normalize_to_site_path(url: str) -> str:
    # Replace backslashes with forward slashes
    u = url.replace("\\\\", "/").replace("\\", "/")
    # If it contains assets/images, strip leading ./ or ../
    m = re.search(r'(?:\.\./|\./)?(/?assets/images/.*)', u, flags=re.IGNORECASE)
    if not m:
        return None
    # Ensure single leading slash for site-root
    path = m.group(1)
    if not path.startswith("/"):
        path = "/" + path
    # Collapse any double slashes
    path = re.sub(r"/{2,}", "/", path)
    return path

def convert_line(line: str) -> str:
    # Skip if contains Liquid or already converted or external
    if "relative_url" in line or "{{" in line or "http://" in line or "https://" in line:
        return line

    def _md_sub(m):
        url = m.group("url").strip()
        site_path = _normalize_to_site_path(url)
        if site_path:
            return f"{m.group(1)}{{{{ '{site_path}' | relative_url }}}}{m.group(3)}"
        return m.group(0)

    def _html_sub(m):
        url = m.group("url").strip()
        site_path = _normalize_to_site_path(url)
        if site_path:
            return f"{m.group(1)}{{{{ '{site_path}' | relative_url }}}}{m.group(3)}"
        return m.group(0)

    changed = False
    new_line = MD_IMG.sub(_md_sub, line)
    if new_line != line:
        changed = True
    newer_line = HTML_IMG.sub(_html_sub, new_line)
    if newer_line != new_line:
        changed = True
    return newer_line if changed else line

def process_file(fp: Path) -> bool:
    orig = fp.read_text(encoding="utf-8", errors="replace")
    lines = orig.splitlines(keepends=True)
    new_lines = [convert_line(ln) for ln in lines]
    new = "".join(new_lines)
    if new != orig:
        bak = fp.with_suffix(fp.suffix + ".bak")
        if not bak.exists():
            bak.write_text(orig, encoding="utf-8")
        fp.write_text(new, encoding="utf-8")
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
