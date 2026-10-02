# CD Reinigungsservice – Website

Reines HTML/CSS/JS, kein Build-Schritt. Lokal testen:

```bash
python3 -m http.server 8080   # dann http://localhost:8080 öffnen
```

## Seiten
- `index.html` – Startseite
- `anfrage.html` – Anfrageformular in 3 Schritten (Versand über Web3Forms)
- `impressum.html`, `datenschutz.html` – Pflichtseiten (nur im Footer verlinkt)

## Platzhalter ausfüllen

| Platzhalter | Wo | Was eintragen |
|---|---|---|
| `[WEB3FORMS-ACCESS-KEY]` | `assets/js/anfrage.js` (ganz oben) und `anfrage.html` (verstecktes Feld, für Besucher ohne JavaScript) | Kostenloser Key von https://web3forms.com – mit eric.darko@freenet.de anlegen |
| `[DOMAIN]` | `<head>` von index.html & anfrage.html | Domain ohne https://, z. B. `cd-reinigungsservice.de` |

Alle auf einmal ersetzen (Beispiel):

```bash
sed -i 's/\[DOMAIN\]/beispiel.de/g; s/\[WEB3FORMS-ACCESS-KEY\]/DEIN-KEY/g' *.html assets/js/anfrage.js
```

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
