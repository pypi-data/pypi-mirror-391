# pure_scraper/utils.py
from pathlib import Path
from .config import config
import re
from lxml import html as lxml_html
from lxml import etree

def save_html(path: str, html: str):
    """
    Save HTML content to a file.
    """
    Path(path).write_text(html, encoding="utf-8")
    if config.show_logs:
        print(f"✅ Saved HTML to {path}")


def prettify_html(html: str, indent_unit: str = None) -> str:
    """
    Prettify HTML, handling malformed tags and JS-heavy content.
    """
    indent_unit = indent_unit or (" " * config.prettify_indent)
    try:
        parser = lxml_html.HTMLParser(remove_blank_text=True, recover=True)
        tree = lxml_html.fromstring(html, parser=parser)
        return etree.tostring(tree, encoding="unicode", pretty_print=True, method="html")
    except Exception:
        # Fallback: simple line-based indentation
        return _fallback_prettify(html, indent_unit)


def _fallback_prettify(html: str, indent_unit: str) -> str:
    """
    Simple regex-based prettify as a fallback if lxml fails.
    """
    TAG_TOKEN_RE = re.compile(r"(<[^>]*>)|([^<]+)", re.S)
    VOID_TAGS = {"area","base","br","col","embed","hr","img","input","link","meta","param","source","track","wbr"}

    tokens = TAG_TOKEN_RE.findall(html)
    out_lines = []
    indent = 0
    preserve = None

    for tag_token, text_token in tokens:
        if tag_token:
            tag = tag_token.strip()
            m = re.match(r"<\s*/?\s*([a-zA-Z0-9:-]+)", tag)
            tagname = m.group(1).lower() if m else ""
            if preserve and tag.startswith(f"</{preserve}"):
                out_lines.append(indent_unit * indent + tag)
                preserve = None
                indent = max(indent - 1, 0)
                continue
            if tag.startswith("<!--") or tag.upper().startswith("<!DOCTYPE") or tag.startswith("<!"):
                out_lines.append(indent_unit * indent + tag)
                continue
            if tag.startswith("</"):
                indent = max(indent - 1, 0)
                out_lines.append(indent_unit * indent + tag)
                continue
            is_self = tag.endswith("/>") or tagname in VOID_TAGS
            out_lines.append(indent_unit * indent + tag)
            if not is_self:
                indent += 1
                if tagname in ("pre","script","style"):
                    preserve = tagname
            continue
        if text_token:
            if preserve:
                for line in text_token.splitlines():
                    out_lines.append(indent_unit * indent + line)
                continue
            text = text_token.strip()
            if not text:
                continue
            for line in text.splitlines():
                line = line.strip()
                if line:
                    out_lines.append(indent_unit * indent + line)
    return "\n".join(out_lines)


def is_html_valid(html: str) -> bool:
    """
    Basic HTML sanity check.
    - Contains <html> and <body>
    - Reasonable length
    """
    if not html or len(html.strip()) < 100:
        return False
    lower = html.lower()
    if "<html" not in lower or "<body" not in lower:
        return False
    return True


def clean_html(raw_html: str) -> str:
    """
    Clean and fix malformed HTML using lxml.
    Handles huge JS-heavy pages gracefully.
    """
    try:
        parser = lxml_html.HTMLParser(remove_blank_text=True, recover=True)
        tree = lxml_html.fromstring(raw_html, parser=parser)
        return etree.tostring(tree, encoding="unicode", method="html")
    except Exception:
        # If lxml fails, return raw HTML as fallback
        return raw_html
