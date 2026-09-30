#!/usr/bin/env python3
"""Siteyi uretir: src/<dil>/<sayfa>.html parcalarini src/layout.html ile birlestirir.

11 dil: kok dizinde TR sayfalar (index.html, privacy.html, ...), diger her dil kendi klasorunde
(en/, de/, fr/, it/, es/, pt-br/, ru/, ja/, ko/, zh-hans/). Dil tablosu asagidaki LANGS listesidir.
Ayarlar config.env dosyasindan okunur. Yalnizca Python 3 standart kutuphanesi kullanilir.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PAGES = ["index", "privacy", "terms", "support"]

# Dil tablosu: kod (html lang ve hreflang), path (klasor; tr kokte), key (config.env eki), ad (kendi dilinde).
# Sira, dil listesinin gorunme sirasidir. tr kokte, digerleri kendi klasorunde.
LANGS = [
    {"code": "tr", "path": "", "key": "TR", "name": "Türkçe"},
    {"code": "en", "path": "en", "key": "EN", "name": "English"},
    {"code": "de", "path": "de", "key": "DE", "name": "Deutsch"},
    {"code": "fr", "path": "fr", "key": "FR", "name": "Français"},
    {"code": "it", "path": "it", "key": "IT", "name": "Italiano"},
    {"code": "es", "path": "es", "key": "ES", "name": "Español"},
    {"code": "pt-BR", "path": "pt-br", "key": "PT_BR", "name": "Português (Brasil)"},
    {"code": "ru", "path": "ru", "key": "RU", "name": "Русский"},
    {"code": "ja", "path": "ja", "key": "JA", "name": "日本語"},
    {"code": "ko", "path": "ko", "key": "KO", "name": "한국어"},
    {"code": "zh-Hans", "path": "zh-hans", "key": "ZH_HANS", "name": "简体中文"},
]
BY_CODE = {l["code"]: l for l in LANGS}
DEFAULT_LANG = "tr"     # kokte duran dil
X_DEFAULT_LANG = "en"   # hreflang x-default

# nav: Ana sayfa / Gizlilik / Sartlar / Destek. conflict: gizlilik ve sartlar sayfalarinin ustundeki
# "Celiskide Ingilizce surum gecerlidir" notu (yalniz tr ve en disindaki diller). conflict_link: Ingilizce surum baglanti metni.
UI = {
    "tr": {
        "nav": {"index": "Ana sayfa", "privacy": "Gizlilik", "terms": "Şartlar", "support": "Destek"},
        "skip": "İçeriğe geç", "menu": "Ana menü", "languages": "Dil",
        "footer_note": "Tıbbi tavsiye değildir. Sağlık konularında bir sağlık profesyoneline danış.",
        "footer_rights": "Tüm hakları saklıdır.",
    },
    "en": {
        "nav": {"index": "Home", "privacy": "Privacy", "terms": "Terms", "support": "Support"},
        "skip": "Skip to content", "menu": "Main menu", "languages": "Language",
        "footer_note": "Not medical advice. For health questions, talk to a health professional.",
        "footer_rights": "All rights reserved.",
    },
    "de": {
        "nav": {"index": "Start", "privacy": "Datenschutz", "terms": "Bedingungen", "support": "Support"},
        "skip": "Zum Inhalt springen", "menu": "Hauptmenü", "languages": "Sprache",
        "footer_note": "Keine medizinische Beratung. Bei Gesundheitsfragen wende dich an medizinisches Fachpersonal.",
        "footer_rights": "Alle Rechte vorbehalten.",
        "conflict": "Bei Abweichungen gilt die englische Fassung.", "conflict_link": "Englische Fassung",
    },
    "fr": {
        "nav": {"index": "Accueil", "privacy": "Confidentialité", "terms": "Conditions", "support": "Assistance"},
        "skip": "Aller au contenu", "menu": "Menu principal", "languages": "Langue",
        "footer_note": "Ceci n'est pas un avis médical. Pour toute question de santé, parle à un professionnel de santé.",
        "footer_rights": "Tous droits réservés.",
        "conflict": "En cas de divergence, la version anglaise prévaut.", "conflict_link": "Version anglaise",
    },
    "it": {
        "nav": {"index": "Home", "privacy": "Privacy", "terms": "Termini", "support": "Assistenza"},
        "skip": "Vai al contenuto", "menu": "Menu principale", "languages": "Lingua",
        "footer_note": "Non è un parere medico. Per questioni di salute, parla con un professionista sanitario.",
        "footer_rights": "Tutti i diritti riservati.",
        "conflict": "In caso di discrepanza prevale la versione inglese.", "conflict_link": "Versione inglese",
    },
    "es": {
        "nav": {"index": "Inicio", "privacy": "Privacidad", "terms": "Términos", "support": "Ayuda"},
        "skip": "Saltar al contenido", "menu": "Menú principal", "languages": "Idioma",
        "footer_note": "No es asesoramiento médico. Para cuestiones de salud, consulta a un profesional sanitario.",
        "footer_rights": "Todos los derechos reservados.",
        "conflict": "En caso de conflicto, prevalece la versión en inglés.", "conflict_link": "Versión en inglés",
    },
    "pt-BR": {
        "nav": {"index": "Início", "privacy": "Privacidade", "terms": "Termos", "support": "Suporte"},
        "skip": "Ir para o conteúdo", "menu": "Menu principal", "languages": "Idioma",
        "footer_note": "Não é aconselhamento médico. Para questões de saúde, fale com um profissional de saúde.",
        "footer_rights": "Todos os direitos reservados.",
        "conflict": "Em caso de divergência, prevalece a versão em inglês.", "conflict_link": "Versão em inglês",
    },
    "ru": {
        "nav": {"index": "Главная", "privacy": "Конфиденциальность", "terms": "Условия", "support": "Поддержка"},
        "skip": "Перейти к содержимому", "menu": "Главное меню", "languages": "Язык",
        "footer_note": "Это не медицинская рекомендация. По вопросам здоровья обратись к специалисту.",
        "footer_rights": "Все права защищены.",
        "conflict": "В случае расхождений приоритет имеет английская версия.", "conflict_link": "Английская версия",
    },
    "ja": {
        "nav": {"index": "ホーム", "privacy": "プライバシー", "terms": "利用規約", "support": "サポート"},
        "skip": "本文へスキップ", "menu": "メインメニュー", "languages": "言語",
        "footer_note": "医療上のアドバイスではありません。健康に関することは医療の専門家にご相談ください。",
        "footer_rights": "すべての権利を保有します。",
        "conflict": "内容に相違がある場合は、英語版が優先されます。", "conflict_link": "英語版",
    },
    "ko": {
        "nav": {"index": "홈", "privacy": "개인정보", "terms": "약관", "support": "지원"},
        "skip": "본문으로 건너뛰기", "menu": "주 메뉴", "languages": "언어",
        "footer_note": "의학적 조언이 아닙니다. 건강 문제는 의료 전문가와 상담하세요.",
        "footer_rights": "모든 권리 보유.",
        "conflict": "내용이 서로 다른 경우 영어판이 우선합니다.", "conflict_link": "영어판",
    },
    "zh-Hans": {
        "nav": {"index": "首页", "privacy": "隐私", "terms": "条款", "support": "支持"},
        "skip": "跳到正文", "menu": "主菜单", "languages": "语言",
        "footer_note": "本应用不提供医疗建议。健康问题请咨询医疗专业人员。",
        "footer_rights": "保留所有权利。",
        "conflict": "如有不一致，以英文版为准。", "conflict_link": "英文版",
    },
}
# Hukuki not yalniz bu sayfalarda, tr ve en disindaki dillerde eklenir.
LEGAL_PAGES = ("privacy", "terms")


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
    folder = ROOT / lang["path"] if lang["path"] else ROOT
    return folder / f"{page}.html"


def page_url(cfg, lang, page):
    base = cfg["SITE_URL"]
    prefix = f"{lang['path']}/" if lang["path"] else ""
    return f"{base}/{prefix}" + ("" if page == "index" else f"{page}.html")


def rel_link(lang, page, target):
    """lang sayfasindan target dilindeki ayni sayfaya goreli baglanti."""
    name = f"{page}.html"
    if lang["code"] == target["code"]:
        return name
    up = "../" if lang["path"] else ""
    down = f"{target['path']}/" if target["path"] else ""
    return f"{up}{down}{name}"


def effective_date(cfg, lang):
    return cfg.get(f"EFFECTIVE_DATE_{lang['key']}") or cfg["EFFECTIVE_DATE_EN"]


def app_name(cfg, lang):
    override = cfg.get(f"APP_NAME_{lang['key']}")
    if override:
        return override
    return cfg["APP_NAME"] if lang["code"] == DEFAULT_LANG else cfg.get("APP_NAME_EN", cfg["APP_NAME"])


def esc(text):
    return text.replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;")


def hreflang_links(cfg, page):
    lines = [
        f'<link rel="alternate" hreflang="{l["code"]}" href="{page_url(cfg, l, page)}">' for l in LANGS
    ]
    lines.append(
        f'<link rel="alternate" hreflang="x-default" href="{page_url(cfg, BY_CODE[X_DEFAULT_LANG], page)}">'
    )
    return "\n  ".join(lines)


def language_list(lang, page, cls):
    """Tum dillerin baglanti listesi; JavaScript gerektirmez. Gecerli dil aria-current ile isaretlenir."""
    items = []
    for t in LANGS:
        current = ' aria-current="true"' if t["code"] == lang["code"] else ""
        items.append(
            f'<li><a href="{rel_link(lang, page, t)}" hreflang="{t["code"]}" lang="{t["code"]}"{current}>{t["name"]}</a></li>'
        )
    return f'<ul class="{cls}">\n          ' + "\n          ".join(items) + "\n        </ul>"


def legal_note(lang, page, ui):
    if page not in LEGAL_PAGES or "conflict" not in ui:
        return ""
    en = BY_CODE[X_DEFAULT_LANG]
    href = rel_link(lang, page, en)
    return (
        '<div class="note legal-note" role="note">'
        f'<p>{ui["conflict"]} <a href="{href}" hreflang="en" lang="en">{ui["conflict_link"]}</a></p></div>'
    )


def insert_legal_note(body, note):
    """Notu sayfanin basina, h1 ve gecerlilik tarihi satirindan hemen sonra ekler."""
    if not note:
        return body
    m = re.search(r'<p class="meta">.*?</p>', body, re.S)
    if not m:
        raise SystemExit("legal not icin <p class=\"meta\"> bulunamadi")
    return body[: m.end()] + "\n\n" + note + body[m.end():]


def main():
    cfg = read_config()
    layout = (ROOT / "src" / "layout.html").read_text(encoding="utf-8")
    for lang in LANGS:
        ui = UI[lang["code"]]
        prefix = "../" if lang["path"] else ""
        for page in PAGES:
            meta, body = parse_fragment(ROOT / "src" / (lang["path"] or "tr") / f"{page}.html")
            nav_items = []
            for p in PAGES:
                current = ' aria-current="page"' if p == page else ""
                nav_items.append(f'<a href="{p}.html"{current}>{ui["nav"][p]}</a>')
            footer_links = " ".join(f'<a href="{p}.html">{ui["nav"][p]}</a>' for p in PAGES[1:])
            values = dict(cfg)
            values.update({
                "LANG": lang["code"],
                "ROOT": prefix,
                "PAGE_TITLE": meta["title"],
                "DESCRIPTION": meta["description"],
                "NAV": "\n        ".join(nav_items),
                "FOOTER_LINKS": footer_links,
                "CONTENT": insert_legal_note(body, legal_note(lang, page, ui)),
                "CANONICAL": page_url(cfg, lang, page),
                "HREFLANGS": hreflang_links(cfg, page),
                "LANG_NAME": lang["name"],
                "LANG_LABEL": ui["languages"],
                "LANG_LIST_MENU": language_list(lang, page, "lang-list"),
                "LANG_LIST_FOOTER": language_list(lang, page, "lang-list footer-langs"),
                "SKIP": ui["skip"],
                "MENU": ui["menu"],
                "FOOTER_NOTE": ui["footer_note"],
                "FOOTER_RIGHTS": ui["footer_rights"],
                "EFFECTIVE_DATE": effective_date(cfg, lang),
                "APP_NAME": app_name(cfg, lang),
                "HOME": "index.html",
            })
            # Once govde parcasi, sonra yerlesim: parcadaki belirtecler de dolsun.
            values["CONTENT"] = fill(values["CONTENT"], values)
            values["DESCRIPTION"] = esc(fill(meta["description"], values))
            values["PAGE_TITLE"] = fill(meta["title"], values)
            html = fill(layout, values)
            target = out_path(lang, page)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(html, encoding="utf-8")
            print("yazildi:", target.relative_to(ROOT))


if __name__ == "__main__":
    sys.exit(main())
