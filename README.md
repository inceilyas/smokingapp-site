# smokingapp-site

Smoking App (iPhone) icin tanitim, gizlilik, kullanim sartlari ve destek sayfalari. Saf statik site: cerez yok, analitik yok, harici kaynak yok. GitHub Pages ile yayimlanir.

## Sayfalar

11 dil: Turkce kokte, digerleri kendi klasorunde. Her dilde 4 sayfa: ana sayfa (`/` ya da `/<klasor>/`), `privacy.html`, `terms.html`, `support.html`.

| Dil | Klasor | html lang |
|---|---|---|
| Turkish | `/` | tr |
| English | `/en/` | en |
| German | `/de/` | de |
| French | `/fr/` | fr |
| Italian | `/it/` | it |
| Spanish | `/es/` | es |
| Portuguese (Brazil) | `/pt-br/` | pt-BR |
| Russian | `/ru/` | ru |
| Japanese | `/ja/` | ja |
| Korean | `/ko/` | ko |
| Chinese (Simplified) | `/zh-hans/` | zh-Hans |

Dil gecisi her sayfanin ust cubugundaki acilir listedir (`<details>`, JavaScript gerekmez); ayni liste alt bilgide de gorunur. Her sayfada 11 dil + `x-default` (Ingilizce) icin `hreflang` baglantilari uretilir. Turkce ve Ingilizce disindaki dillerin gizlilik ve sart sayfalarinin ustunde "celiskide Ingilizce surum gecerlidir" notu vardir (`build.py` icindeki `UI[...]["conflict"]`).

Yeni dil eklemek: `build.py` icindeki `LANGS` ve `UI` tablolarina satir ekle, `config.env`'e `EFFECTIVE_DATE_<KOD>` ekle, `src/<klasor>/` altina 4 parca yaz (`src/en/` kaynak alinip cevrilir).

## Ad ve e-posta nerede degisir?

Tek ayar dosyasi: `config.env`.

- `APP_NAME`: uygulama adi (simdilik `Smoking App`). Magaza adi kesinlesince degistir.
- `SUPPORT_EMAIL`: destek adresi. Simdilik yer tutucu belirtec `{{SUPPORT_EMAIL}}`.
- `DEVELOPER_NAME`: gizlilik politikasinda ve sartlarda gecen veri sorumlusu / telif sahibi adi.
- `SITE_URL`: GitHub Pages adresi (canonical ve hreflang icin).
- `APP_NAME_EN`: TR disindaki tum dillerde gorunen ad (simdilik `Breathe In`); tek bir dil icin `APP_NAME_<KOD>` ile ezilebilir.
- `EFFECTIVE_DATE_<KOD>` (TR, EN, DE, FR, IT, ES, PT_BR, RU, JA, KO, ZH_HANS): politikanin yururluk tarihi, dilin kendi yazimiyla.

Degisiklikten sonra siteyi yeniden uret:

```sh
python3 build.py
```

`build.py`, `src/` altindaki sayfa parcalarini (`src/<klasor>/*.html`) ve `src/layout.html` sablonunu birlestirip kok dizindeki `*.html` ve her dil klasorundeki `*.html` dosyalarini yazar. Uretilen dosyalar git'e girer (GitHub Pages dogrudan bunlari sunar). Build sonrasi `python3 check.py` calistir: goreli baglantilari, canonical ve hreflang'lari, kalan belirtecleri ve emoji'yi kontrol eder. Metni degistirmek icin `src/` altindaki parcayi duzenle, sonra `python3 build.py` calistir. Uretilen `*.html` dosyalarini elle duzenleme; bir sonraki build ezer.

Hizli yol (build olmadan, yalnizca e-posta): `{{SUPPORT_EMAIL}}` belirtecini uretilen dosyalarda degistir:

```sh
grep -rl '{{SUPPORT_EMAIL}}' --include='*.html' . | grep -v '^./src' | xargs sed -i '' 's/{{SUPPORT_EMAIL}}/adres@ornek.com/g'
```

Bu yol `config.env`'i guncellemez; sonra `python3 build.py` calistirirsan eski belirteç geri gelir. Kalici olmasi icin `config.env` dosyasini da guncelle.

## GitHub Pages ile yayinlama

1. Repoyu olustur (`inceilyas/smokingapp-site`) ve bu dizini `main` dalina it. Gizlilik ve hukuk sitesi uygulama kodundan ayri ve public bir repo olmalidir (Pages'in ucretsiz plani public repo ister).
2. GitHub'da Settings > Pages > Build and deployment > Source: "Deploy from a branch", Branch: `main`, klasor `/ (root)`.
3. Bir iki dakika sonra site `https://inceilyas.github.io/smokingapp-site/` adresinde yayinda olur.
4. `.nojekyll` dosyasi Jekyll islemesini kapatir; silme.

URL'ler (taban `https://inceilyas.github.io/smokingapp-site`; Turkce kokte, digerleri `/<klasor>/`):

- Gizlilik: `/privacy.html` (TR), `/en/privacy.html`, `/de/privacy.html`, `/fr/privacy.html`, `/it/privacy.html`, `/es/privacy.html`, `/pt-br/privacy.html`, `/ru/privacy.html`, `/ja/privacy.html`, `/ko/privacy.html`, `/zh-hans/privacy.html`
- Sartlar: `/terms.html` (TR), `/en/terms.html`, `/de/terms.html`, `/fr/terms.html`, `/it/terms.html`, `/es/terms.html`, `/pt-br/terms.html`, `/ru/terms.html`, `/ja/terms.html`, `/ko/terms.html`, `/zh-hans/terms.html`
- Destek: `/support.html` (TR), `/en/support.html`, `/de/support.html`, `/fr/support.html`, `/it/support.html`, `/es/support.html`, `/pt-br/support.html`, `/ru/support.html`, `/ja/support.html`, `/ko/support.html`, `/zh-hans/support.html`

App Store Connect'te gizlilik politikasi URL'si her dil icin ayri girilir; uygulama ici paywall baglantilari (`PremiumLinks`) ile ayni adresler olmalidir.

## Yayin oncesi kontrol listesi

- `config.env` icindeki `SUPPORT_EMAIL` gercek adres oldu mu; `grep -r '{{' --include='*.html' .` bos donmeli (`src/` disinda).
- `DEVELOPER_NAME` gercek hukuki ad / marka mi.
- Politika metinleri uygulamanin son haliyle uyumlu mu (ozellikle iCloud sifreleme, uygulama dili, yas siniri, saklama sureleri). Hukuki gozden gecirme onerilir.
- App Store Connect "App Privacy" beyani bu politikayla tutarli mi.
- "Yakinda App Store'da" metni (`src/*/index.html`) yayindan sonra App Store baglantisiyla degistirilmeli.

## Tasarim

"Kul Defteri" paleti (koyu ve acik tema, `prefers-color-scheme`), sistem yazi tipleri, klavye odagi gorunur, "icerige gec" baglantisi var. Stil: `assets/style.css`.
