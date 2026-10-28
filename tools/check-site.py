#!/usr/bin/env python3
"""Static checks: internal links, one <h1>, self-canonical, unique title/description,
JSON-LD (BreadcrumbList + FAQPage) parses, sitemap covers every page, CSP-safe scripts.
Run from the site root: python3 tools/check-site.py"""
import json, os, re, sys
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
DOMAIN = re.search(r'^DOMAIN = "([^"]+)"', open(os.path.join(ROOT, "tools", "build.py"), encoding="utf-8").read(), re.M).group(1)


class P(HTMLParser):
    def __init__(self):
        super().__init__(); self.links, self.h1, self.scripts, self.ld, self.ids = [], 0, [], [], set()
        self._ld = False; self.title = ""; self._t = False; self.meta = {}; self.canon = None
    def handle_starttag(self, tag, a):
        a = dict(a)
        if "id" in a: self.ids.add(a["id"])
        if tag == "a" and a.get("href"): self.links.append(a["href"])
        if tag in ("link",) and a.get("rel") == "canonical": self.canon = a.get("href")
        if tag in ("link", "img", "script") and (a.get("href") or a.get("src")): self.links.append(a.get("href") or a.get("src"))
        if tag == "h1": self.h1 += 1
        if tag == "script":
            self.scripts.append(a); self._ld = a.get("type") == "application/ld+json"; self._buf = ""
        if tag == "title": self._t = True
        if tag == "meta" and a.get("name") == "description": self.meta["description"] = a.get("content", "")
    def handle_endtag(self, tag):
        if tag == "script" and self._ld: self.ld.append(self._buf); self._ld = False
        if tag == "title": self._t = False
    def handle_data(self, d):
        if self._ld: self._buf += d
        if self._t: self.title += d


def page_files():
    for dp, dn, fn in os.walk(ROOT):
        if "/tools" in dp or "/." in dp: continue
        for f in fn:
            if f.endswith(".html"): yield os.path.join(dp, f)


def url_path(fp):
    rel = os.path.relpath(fp, ROOT).replace(os.sep, "/")
    return "/" + rel[:-len("index.html")] if rel.endswith("index.html") else "/" + rel


def resolves(href):
    h = href.split("#")[0].split("?")[0]
    if not h: return True
    t = os.path.join(ROOT, h.lstrip("/"))
    return os.path.isfile(t) or os.path.isfile(os.path.join(t, "index.html"))


errs, titles, descs, pages = [], {}, {}, {}
for fp in sorted(page_files()):
    path = url_path(fp); p = P(); p.feed(open(fp, encoding="utf-8").read()); pages[path] = p
    is404 = path == "/404.html"
    if p.h1 != 1: errs.append(f"{path}: {p.h1} <h1>")
    for href in p.links:
        if href.startswith(DOMAIN): href = href[len(DOMAIN):]
        if href.startswith(("http://", "https://", "mailto:", "tel:")): continue
        if href.startswith("#"):
            if href[1:] and href[1:] not in p.ids: errs.append(f"{path}: broken anchor {href}")
            continue
        if not resolves(href): errs.append(f"{path}: broken internal link {href}")
    for s in p.scripts:
        src = s.get("src")
        if src and not src.startswith("/"): errs.append(f"{path}: external script {src}")
        if not src and s.get("type") != "application/ld+json": errs.append(f"{path}: inline script (blocked by CSP)")
    if is404: continue
    if p.canon != DOMAIN + path: errs.append(f"{path}: canonical {p.canon}")
    titles.setdefault(p.title, []).append(path); descs.setdefault(p.meta.get("description"), []).append(path)
    types = []
    for raw in p.ld:
        try: types.append(json.loads(raw)["@type"])
        except Exception as e: errs.append(f"{path}: bad JSON-LD {e}")
    for need in ("BreadcrumbList", "FAQPage"):
        if need not in types: errs.append(f"{path}: missing {need}")
    if len(p.title) > 70: print(f"note: {path} title {len(p.title)} chars")
for k, v in list(titles.items()) + list(descs.items()):
    if len(v) > 1: errs.append(f"duplicate title/description on {v}")
sm = re.findall(r"<loc>([^<]+)</loc>", open(os.path.join(ROOT, "sitemap.xml"), encoding="utf-8").read())
smp = {u[len(DOMAIN):] for u in sm}
for path in pages:
    if path != "/404.html" and path not in smp: errs.append(f"sitemap missing {path}")
for u in smp:
    if u not in pages: errs.append(f"sitemap lists non-existent {u}")
vc = json.load(open(os.path.join(ROOT, "vercel.json")))
csp = [h["value"] for r in vc["headers"] for h in r["headers"] if h["key"] == "Content-Security-Policy"][0]
if "script-src 'self';" not in csp: errs.append("CSP script-src is not 'self' only")
print(f"checked {len(pages)} HTML files, {len(sm)} sitemap URLs")
if errs:
    print("\n".join("ERROR " + e for e in errs)); sys.exit(1)
print("OK: no broken internal links, one H1 each, self-canonicals, unique titles/descriptions, JSON-LD valid, sitemap complete, CSP strict")
