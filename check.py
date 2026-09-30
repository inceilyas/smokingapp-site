#!/usr/bin/env python3
"""Uretilen sitenin tutarlilik kontrolu (build.py'den sonra calistir): python3 check.py
Kontroller: goreli baglantilar ve #parca hedefleri, canonical, hreflang (11 dil + x-default, karsilikli),
html lang, kalan {{belirtec}}, emoji, tek h1, bos title."""
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse, unquote

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build  # noqa: E402

ROOT = build.ROOT
EMOJI = re.compile("[\U0001F000-\U0001FAFF☀-➿⬀-⯿️‍]")


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links, self.ids, self.alts, self.h1 = [], set(), {}, 0
        self.canonical = self.lang = self.title = None
        self._in_title = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.add(a["id"])
        if tag == "html":
            self.lang = a.get("lang")
        elif tag == "h1":
            self.h1 += 1
        elif tag == "title":
            self._in_title = True
            self.title = ""
        elif tag == "link" and a.get("rel") == "canonical":
            self.canonical = a.get("href")
        elif tag == "link" and a.get("rel") == "alternate":
            self.alts[a.get("hreflang")] = a.get("href")
        if tag in ("a", "link") and a.get("href") and a.get("rel") not in ("canonical", "alternate"):
            self.links.append(a["href"])
        if tag == "script" or (tag == "img" and a.get("src")):
            self.links.append(a.get("src", ""))

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False

    def handle_data(self, data):
        if self._in_title:
            self.title += data


def main():
    cfg = build.read_config()
    base = cfg["SITE_URL"]
    errors, pages, count = [], {}, 0
    for lang in build.LANGS:
        for page in build.PAGES:
            f = build.out_path(lang, page)
            if not f.exists():
                errors.append(f"EKSIK dosya: {f.relative_to(ROOT)}")
                continue
            text = f.read_text(encoding="utf-8")
            p = Page()
            p.feed(text)
            pages[f.resolve()] = (lang, page, p, text)
    for f, (lang, page, p, text) in pages.items():
        count += 1
        rel = f.relative_to(ROOT)
        where = str(rel)
        if p.lang != lang["code"]:
            errors.append(f"{where}: lang={p.lang}, beklenen {lang['code']}")
        if p.canonical != build.page_url(cfg, lang, page):
            errors.append(f"{where}: canonical {p.canonical}")
        expected = {l["code"]: build.page_url(cfg, l, page) for l in build.LANGS}
        expected["x-default"] = build.page_url(cfg, build.BY_CODE[build.X_DEFAULT_LANG], page)
        if p.alts != expected:
            errors.append(f"{where}: hreflang beklenenden farkli: {set(p.alts.items()) ^ set(expected.items())}")
        if p.h1 != 1:
            errors.append(f"{where}: h1 sayisi {p.h1}")
        if not (p.title or "").strip().replace("|", "").strip():
            errors.append(f"{where}: bos title")
        if re.search(r"\{\{|\}\}", text):
            errors.append(f"{where}: cozulmemis belirtec")
        if EMOJI.search(text):
            errors.append(f"{where}: emoji")
        for href in p.links:
            u = urlparse(href)
            if u.scheme in ("http", "https", "mailto"):
                continue
            target = f if not u.path else (f.parent / unquote(u.path)).resolve()
            if target.is_dir():
                target = target / "index.html"
            if not target.exists():
                errors.append(f"{where}: kirik baglanti {href}")
                continue
            if u.fragment and target.suffix == ".html":
                tp = pages.get(target)
                ids = tp[2].ids if tp else set()
                if u.fragment not in ids:
                    errors.append(f"{where}: kirik parca {href}")
    # hreflang karsilikli: her sayfanin alternatifi gercek dosyaya cozulmeli
    for f, (lang, page, p, text) in pages.items():
        for code, url in p.alts.items():
            path = url[len(base):].lstrip("/")
            tgt = ROOT / (path + "index.html" if path == "" or path.endswith("/") else path)
            if not tgt.exists():
                errors.append(f"{f.relative_to(ROOT)}: hreflang {code} dosyaya cozulmuyor ({url})")
    print(f"{count} sayfa kontrol edildi, {len(errors)} sorun")
    for e in errors:
        print(" -", e)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
