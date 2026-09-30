# smokingapp-site

Smoking App (iPhone) icin tanitim, gizlilik, kullanim sartlari ve destek sayfalari. Saf statik site: cerez yok, analitik yok, harici kaynak yok. GitHub Pages ile yayimlanir.

## Sayfalar

| Sayfa | Turkce | English |
|---|---|---|
| Ana sayfa | `/` (`index.html`) | `/en/` |
| Gizlilik Politikasi | `/privacy.html` | `/en/privacy.html` |
| Kullanim Sartlari | `/terms.html` | `/en/terms.html` |
| Destek | `/support.html` | `/en/support.html` |

Dil gecisi her sayfanin ust cubugundaki baglantidir (JavaScript gerekmez).

## Ad ve e-posta nerede degisir?

Tek ayar dosyasi: `config.env`.

- `APP_NAME`: uygulama adi (simdilik `Smoking App`). Magaza adi kesinlesince degistir.
- `SUPPORT_EMAIL`: destek adresi. Simdilik yer tutucu belirtec `{{SUPPORT_EMAIL}}`.
- `DEVELOPER_NAME`: gizlilik politikasinda ve sartlarda gecen veri sorumlusu / telif sahibi adi.
- `SITE_URL`: GitHub Pages adresi (canonical ve hreflang icin).
- `EFFECTIVE_DATE_TR` / `EFFECTIVE_DATE_EN`: politikanin yururluk tarihi.

Degisiklikten sonra siteyi yeniden uret:

```sh
python3 build.py
```

`build.py`, `src/` altindaki sayfa parcalarini (`src/tr/*.html`, `src/en/*.html`) ve `src/layout.html` sablonunu birlestirip kok dizindeki `*.html` ve `en/*.html` dosyalarini yazar. Uretilen dosyalar git'e girer (GitHub Pages dogrudan bunlari sunar). Metni degistirmek icin `src/` altindaki parcayi duzenle, sonra `python3 build.py` calistir. Uretilen `*.html` dosyalarini elle duzenleme; bir sonraki build ezer.

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

URL'ler:

- Gizlilik (TR): `https://inceilyas.github.io/smokingapp-site/privacy.html`
- Gizlilik (EN): `https://inceilyas.github.io/smokingapp-site/en/privacy.html`
- Sartlar (TR): `https://inceilyas.github.io/smokingapp-site/terms.html`
- Sartlar (EN): `https://inceilyas.github.io/smokingapp-site/en/terms.html`
- Destek (TR): `https://inceilyas.github.io/smokingapp-site/support.html`
- Destek (EN): `https://inceilyas.github.io/smokingapp-site/en/support.html`

App Store Connect'te gizlilik politikasi URL'si her dil icin ayri girilir; uygulama ici paywall baglantilari (`PremiumLinks`) ile ayni adresler olmalidir.

## Yayin oncesi kontrol listesi

- `config.env` icindeki `SUPPORT_EMAIL` gercek adres oldu mu; `grep -r '{{' --include='*.html' .` bos donmeli (`src/` disinda).
- `DEVELOPER_NAME` gercek hukuki ad / marka mi.
- Politika metinleri uygulamanin son haliyle uyumlu mu (ozellikle iCloud sifreleme, uygulama dili, yas siniri, saklama sureleri). Hukuki gozden gecirme onerilir.
- App Store Connect "App Privacy" beyani bu politikayla tutarli mi.
- "Yakinda App Store'da" metni (`src/*/index.html`) yayindan sonra App Store baglantisiyla degistirilmeli.

## Tasarim

"Kul Defteri" paleti (koyu ve acik tema, `prefers-color-scheme`), sistem yazi tipleri, klavye odagi gorunur, "icerige gec" baglantisi var. Stil: `assets/style.css`.
