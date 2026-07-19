#!/usr/bin/env python3
from pathlib import Path
from html.parser import HTMLParser
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
required = [
    "index.html","books.html","fiction.html","fragments.html","framework.html",
    "notes.html","about.html","contact.html","start-here.html","privacy.html",
    "favicon.ico","site.webmanifest","CNAME","assets/css/site.css","assets/js/site.js",
    "ai-editorial-policy.html","legal.html","cookies.html","corrections.html"
]

errors = []
for name in required:
    if not (ROOT / name).exists():
        errors.append(f"Missing: {name}")

class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.images = []
    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag == "a" and values.get("href"):
            self.links.append(values["href"])
        if tag == "img" and values.get("src"):
            self.images.append(values["src"])

for page in ROOT.glob("*.html"):
    parser = LinkParser()
    try:
        parser.feed(page.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"Cannot parse {page.name}: {exc}")
        continue
    for ref in parser.links + parser.images:
        if ref.startswith(("http://","https://","mailto:","#","javascript:")):
            continue
        clean = ref.split("#",1)[0].split("?",1)[0]
        if clean and not (ROOT / clean).exists():
            errors.append(f"{page.name}: missing local reference {ref}")

try:
    books = json.loads((ROOT/"content/books.json").read_text(encoding="utf-8"))
    slugs = [book.get("slug") for book in books]
    if len(slugs) != len(set(slugs)):
        errors.append("Duplicate book slug.")
except Exception as exc:
    errors.append(f"Invalid books.json: {exc}")

# v5.1 policy-layer checks
for page in ROOT.glob("*.html"):
    text = page.read_text(encoding="utf-8", errors="replace")
    for required_link in ("ai-editorial-policy.html", "legal.html", "privacy.html", "cookies.html", "corrections.html"):
        if required_link not in text:
            errors.append(f"{page.name}: Policy footer missing {required_link}")
for page in ROOT.glob("book-*.html"):
    text = page.read_text(encoding="utf-8", errors="replace")
    if "publication-record-section" not in text or "mariusjohanstokknes.com" not in text:
        errors.append(f"{page.name}: official publication record missing")


if errors:
    print("\n".join(f"ERROR: {item}" for item in sorted(set(errors))))
    sys.exit(1)

print("Site validation passed, including v5.1 policy and publication records.")
