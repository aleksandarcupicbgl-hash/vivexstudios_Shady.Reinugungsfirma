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
| `[E-MAIL]` | alle HTML-Seiten | E-Mail-Adresse der Firma |
| `[ADRESSE]` | alle HTML-Seiten | Straße, PLZ, Ort (Pflicht fürs Impressum) |
| `[WEB3FORMS-ACCESS-KEY]` | `assets/js/anfrage.js` (ganz oben) und `anfrage.html` (verstecktes Feld, für Besucher ohne JavaScript) | Kostenloser Key von https://web3forms.com – an die Firmen-E-Mail gebunden |
| `[DOMAIN]` | `<head>` von index.html & anfrage.html | Domain ohne https://, z. B. `cd-reinigungsservice.de` |

Alle auf einmal ersetzen (Beispiel):

```bash
sed -i 's/\[E-MAIL\]/info@beispiel.de/g; s/\[ADRESSE\]/Musterstraße 1, 12345 Musterstadt/g; s/\[DOMAIN\]/beispiel.de/g; s/\[WEB3FORMS-ACCESS-KEY\]/DEIN-KEY/g' *.html assets/js/anfrage.js
```

## Logo
1. `logo.png` in den Projektordner legen.
2. `pip install pillow` und `python3 tools/logo-vorbereiten.py` ausführen.

Das Skript liest die exakte Blau-Farbe aus dem Logo, trägt sie als `--accent` in
`assets/css/style.css` ein und erzeugt Header-Logo, freigestellte Version, Favicons und
Open-Graph-Bild in `assets/img/`. (Aktuell liegt dort ein Platzhalter-Monogramm „CD“.)

## Neue Referenz ergänzen
In `index.html` im Abschnitt „Referenzen“ einen `<li class="reveal">…</li>`-Block kopieren
und Firmenname/Text anpassen.

## Vorschau-Datei
`python3 tools/vorschau-bauen.py` erzeugt `vorschau.html`: alle Seiten in einer Datei,
Navigation funktioniert auch ohne JavaScript (z. B. in App-Vorschauen).
Mit `--demo` sendet das Formular nichts und zeigt nur die Erfolgsmeldung.
