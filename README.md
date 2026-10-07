# CD Reinigungsservice – Website

Reines HTML/CSS/JS, kein Build-Schritt. Lokal testen:

```bash
python3 -m http.server 8080   # dann http://localhost:8080 öffnen
```

## Seiten
- `index.html` – Startseite
- `anfrage.html` – Anfrageformular in 3 Schritten (Versand über Web3Forms)
- `treppenhausreinigung-muenchen.html`, `bueroreinigung-muenchen.html`, `fensterreinigung-muenchen.html`,
  `winterdienst-muenchen.html`, `grundreinigung-muenchen.html` – Leistungsseiten für lokales SEO
- `impressum.html`, `datenschutz.html` – Pflichtseiten (im Footer verlinkt)
- `robots.txt`, `sitemap.xml` – für Suchmaschinen (Domain: https://cdreinigungsservice.de)

## Platzhalter ausfüllen

| Platzhalter | Wo | Was eintragen |
|---|---|---|
| `[WEB3FORMS-ACCESS-KEY]` | `assets/js/anfrage.js` (ganz oben) und `anfrage.html` (verstecktes Feld, für Besucher ohne JavaScript) | Kostenloser Key von https://web3forms.com – mit eric.darko@freenet.de anlegen |
| `[GOOGLE-SEARCH-CONSOLE-CODE]` | `index.html` (Meta-Tag `google-site-verification`) | In der Google Search Console „URL-Präfix“ → Methode „HTML-Tag“ wählen und nur den `content`-Wert eintragen |

Alle auf einmal ersetzen (Beispiel):

```bash
sed -i 's/\[WEB3FORMS-ACCESS-KEY\]/DEIN-KEY/g' anfrage.html assets/js/anfrage.js
sed -i 's/\[GOOGLE-SEARCH-CONSOLE-CODE\]/DEIN-CODE/' index.html
```

## Leistungsseiten bearbeiten
Texte, FAQ und Leistungsumfang stehen in `tools/leistungen.py`. Nach einer Änderung:

```bash
python3 tools/leistungsseiten-bauen.py
```

Header und Footer werden dabei aus `index.html` übernommen. Bei neuen Seiten auch `sitemap.xml` ergänzen.

## Analytics (Plausible)
Alle Seiten laden `https://plausible.io/js/script.js` mit `data-domain="cdreinigungsservice.de"`.
Damit Zahlen ankommen, muss die Domain in einem Plausible-Konto (plausible.io) angelegt sein.
Plausible setzt keine Cookies – ein Cookie-Banner ist dafür nicht nötig.

## Logo
1. `logo.png` in den Projektordner legen.
2. `pip install pillow` und `python3 tools/logo-vorbereiten.py` ausführen.

Das Skript liest die exakte Blau-Farbe aus dem Logo, trägt sie als `--accent` in
`assets/css/style.css` ein und erzeugt Header-Logo, freigestellte Version, Favicons und
Open-Graph-Bild in `assets/img/`.

## Hero-Foto
`assets/img/hero-reinigung-*.jpg/.webp` (800 px und 1376 px breit). Zum Austauschen einfach
Dateien mit gleichem Namen ersetzen.

## Neue Referenz ergänzen
In `index.html` im Abschnitt „Referenzen“ einen `<li class="reveal">…</li>`-Block kopieren
und Firmenname/Text anpassen.

## Vorschau-Datei
`python3 tools/vorschau-bauen.py` erzeugt `vorschau.html`: alle Seiten in einer Datei,
Navigation funktioniert auch ohne JavaScript (z. B. in App-Vorschauen).
Mit `--demo` sendet das Formular nichts und zeigt nur die Erfolgsmeldung.
