#!/usr/bin/env python3
"""Siteyi uretir: src/<dil>/<sayfa>.html parcalarini src/layout.html ile birlestirir.

Cikti: kok dizinde TR sayfalar (index.html, privacy.html, ...), en/ altinda EN sayfalar.
Ayarlar config.env dosyasindan okunur. Yalnizca Python 3 standart kutuphanesi kullanilir.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PAGES = ["index", "privacy", "terms", "support"]

NAV = {
    "tr": {"index": "Ana sayfa", "privacy": "Gizlilik", "terms": "Şartlar", "support": "Destek"},
    "en": {"index": "Home", "privacy": "Privacy", "terms": "Terms", "support": "Support"},
}
UI = {
    "tr": {
        "skip": "İçeriğe geç",
        "menu": "Ana menü",
        "switch_label": "English",
        "switch_lang": "en",
        "switch_title": "Read this page in English",
        "footer_note": "Tıbbi tavsiye değildir. Sağlık konularında bir sağlık profesyoneline danış.",
        "footer_rights": "Tüm hakları saklıdır.",
        "lang_name": "Türkçe",
    },
    "en": {
        "skip": "Skip to content",
        "menu": "Main menu",
        "switch_label": "Türkçe",
        "switch_lang": "tr",
        "switch_title": "Bu sayfayı Türkçe oku",
        "footer_note": "Not medical advice. For health questions, talk to a health professional.",
        "footer_rights": "All rights reserved.",
        "lang_name": "English",
    },
}


def read_config():
    cfg = {}
    for line in (ROOT / "config.env").read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        key, _, value = line.partition("=")
        cfg[key.strip()] = value.strip()
    return cfg


def fill(text, values):
    """Tek geciste {{ANAHTAR}} degistirir; bilinmeyen anahtari ve degistirilmis metni oldugu gibi birakir."""
    return re.sub(r"\{\{([A-Z_]+)\}\}", lambda m: values.get(m.group(1), m.group(0)), text)


def parse_fragment(path):
    raw = path.read_text(encoding="utf-8")
    head, _, body = raw.partition("\n\n")
    meta = {}
    for line in head.splitlines():
        k, _, v = line.partition(":")
        meta[k.strip()] = v.strip()
    return meta, body.strip()


def out_path(lang, page):
    return ROOT / (f"{page}.html" if lang == "tr" else f"en/{page}.html")


def page_url(cfg, lang, page):
    base = cfg["SITE_URL"]
    path = f"{page}.html" if lang == "tr" else f"en/{page}.html"
    if page == "index":
        path = "" if lang == "tr" else "en/"
    return f"{base}/{path}"


def rel_link(lang, page, target_lang):
    """lang sayfasindan target_lang sayfasina goreli baglanti."""
    name = f"{page}.html"
    if lang == target_lang:
        return name
    return f"../{name}" if lang == "en" else f"en/{name}"


def main():
    cfg = read_config()
    layout = (ROOT / "src" / "layout.html").read_text(encoding="utf-8")
    for lang in ("tr", "en"):
        ui = UI[lang]
        prefix = "../" if lang == "en" else ""
        for page in PAGES:
            meta, body = parse_fragment(ROOT / "src" / lang / f"{page}.html")
            nav_items = []
            for p in PAGES:
                current = ' aria-current="page"' if p == page else ""
                nav_items.append(f'<a href="{p}.html"{current}>{NAV[lang][p]}</a>')
            footer_links = " ".join(f'<a href="{p}.html">{NAV[lang][p]}</a>' for p in PAGES[1:])
            other = ui["switch_lang"]
            values = dict(cfg)
            values.update({
                "LANG": lang,
                "ROOT": prefix,
                "PAGE_TITLE": meta["title"],
                "DESCRIPTION": meta["description"],
                "NAV": "\n        ".join(nav_items),
                "FOOTER_LINKS": footer_links,
                "CONTENT": body,
                "CANONICAL": page_url(cfg, lang, page),
                "ALT_TR": page_url(cfg, "tr", page),
                "ALT_EN": page_url(cfg, "en", page),
                "SWITCH_HREF": rel_link(lang, page, other),
                "SWITCH_LABEL": ui["switch_label"],
                "SWITCH_LANG": other,
                "SWITCH_TITLE": ui["switch_title"],
                "SKIP": ui["skip"],
                "MENU": ui["menu"],
                "FOOTER_NOTE": ui["footer_note"],
                "FOOTER_RIGHTS": ui["footer_rights"],
                "EFFECTIVE_DATE": cfg["EFFECTIVE_DATE_TR" if lang == "tr" else "EFFECTIVE_DATE_EN"],
                "APP_NAME": cfg["APP_NAME"] if lang == "tr" else cfg.get("APP_NAME_EN", cfg["APP_NAME"]),
                "HOME": "index.html",
            })
            # Once govde parcasi, sonra yerlesim: parcadaki belirtecler de dolsun.
            values["CONTENT"] = fill(body, values)
            values["DESCRIPTION"] = fill(meta["description"], values)
            values["PAGE_TITLE"] = fill(meta["title"], values)
            html = fill(layout, values)
            target = out_path(lang, page)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(html, encoding="utf-8")
            print("yazildi:", target.relative_to(ROOT))


if __name__ == "__main__":
    sys.exit(main())
