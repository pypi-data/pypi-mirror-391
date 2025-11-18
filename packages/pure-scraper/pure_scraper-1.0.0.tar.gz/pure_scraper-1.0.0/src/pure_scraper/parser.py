# src/pure_scraper/parser.py
from html.parser import HTMLParser
import re
import json

class Node:
    def __init__(self, tag=None, attrs=None, parent=None):
        self.tag = tag
        self.attrs = dict(attrs or [])
        self.children = []
        self.text = ""
        self.parent = parent

    def __repr__(self):
        return f"<{self.tag} {self.attrs}>"

    def get_text(self):
        parts = []
        if self.text:
            parts.append(self.text.strip())
        for c in self.children:
            parts.append(c.get_text())
        return " ".join(p for p in parts if p).strip()

    def find(self, tag=None, attrs=None):
        if (tag is None or self.tag == tag) and self._match_attrs(attrs):
            return self
        for c in self.children:
            res = c.find(tag, attrs)
            if res:
                return res
        return None

    def find_all(self, tag=None, attrs=None):
        out = []
        if (tag is None or self.tag == tag) and self._match_attrs(attrs):
            out.append(self)
        for c in self.children:
            out.extend(c.find_all(tag, attrs))
        return out

    def _match_attrs(self, attrs):
        if not attrs:
            return True
        for k, v in attrs.items():
            val = self.attrs.get(k)
            if isinstance(v, str) and v.startswith("regex:"):
                if not val or not re.search(v[6:], val):
                    return False
            else:
                if val != v:
                    return False
        return True

def extract_json_from_script(html, variable=None):
    results = []
    scripts = re.findall(r'<script.*?>(.*?)</script>', html, re.DOTALL)
    for s in scripts:
        s = s.strip()
        if not s:
            continue
        try:
            data = json.loads(s)
            results.append(data)
            continue
        except:
            pass
        if variable:
            pattern = re.compile(rf'{variable}\s*=\s*(\{{.*?\}});', re.DOTALL)
            m = pattern.search(s)
            if m:
                try:
                    data = json.loads(m.group(1))
                    results.append(data)
                except:
                    continue
    return results

class PureScraper(HTMLParser):
    def __init__(self, html=None, dynamic=False):
        super().__init__()
        self.root = Node("document")
        self.current = self.root
        self._lines = []
        self._indent = 0
        self._open_tags = []
        self.dynamic = dynamic
        self.json_data = []

        if html:
            self.feed(html)
            self._close_remaining_tags()

            if dynamic:
                self.json_data = extract_json_from_script(html)

    def handle_starttag(self, tag, attrs):
        node = Node(tag, attrs, parent=self.current)
        self.current.children.append(node)
        self.current = node
        self._open_tags.append(node)
        self._lines.append(self._indent_str() + self._tag_repr(tag, attrs))
        self._indent += 1

    def handle_endtag(self, tag):
        for i in range(len(self._open_tags)-1, -1, -1):
            if self._open_tags[i].tag == tag:
                while len(self._open_tags) > i:
                    node = self._open_tags.pop()
                    self._indent = max(0, self._indent - 1)
                    self._lines.append(self._indent_str() + f"</{node.tag}>")
                    if node.parent:
                        self.current = node.parent
                return
        self._lines.append(self._indent_str() + f"</{tag}>")

    def handle_data(self, data):
        text = data.strip()
        if text:
            self.current.text += (" " + text)
            self._lines.append(self._indent_str() + text)

    def _tag_repr(self, tag, attrs):
        attr_str = " ".join(f'{k}="{v}"' for k, v in attrs)
        return f"<{tag}{(' ' + attr_str) if attr_str else ''}>"

    def _indent_str(self):
        return " " * (2 * self._indent)

    def _close_remaining_tags(self):
        while self._open_tags:
            node = self._open_tags.pop()
            self._indent = max(0, self._indent - 1)
            self._lines.append(self._indent_str() + f"</{node.tag}>")
            if node.parent:
                self.current = node.parent

    def get_links(self, tag="a"):
        links = []
        nodes = self.find_all(tag)
        for n in nodes:
            href = n.attrs.get("href")
            if href:
                links.append({"text": n.get_text(), "href": href})
        return links

    def get_images(self, tag="img"):
        images = []
        nodes = self.find_all(tag)
        for n in nodes:
            src = n.attrs.get("src")
            alt = n.attrs.get("alt", "")
            if src:
                images.append({"src": src, "alt": alt})
        return images

    def get_tables(self):
        tables = []
        table_nodes = self.find_all("table")
        for t in table_nodes:
            table_data = []
            for row in t.find_all("tr"):
                row_data = []
                for cell in row.find_all("td") + row.find_all("th"):
                    row_data.append(cell.get_text())
                if row_data:
                    table_data.append(row_data)
            if table_data:
                tables.append(table_data)
        return tables

    def get_html(self):
        return "\n".join(self._lines)
    

    def get_title(self):
        title_node = self.find("title")
        if title_node:
            return title_node.get_text()
        return None


    def prettify(self):
        return self.get_html()

    def find(self, tag=None, attrs=None):
        return self.root.find(tag, attrs)

    def find_all(self, tag=None, attrs=None):
        return self.root.find_all(tag, attrs)

    def get_text(self):
        return self.root.get_text()
