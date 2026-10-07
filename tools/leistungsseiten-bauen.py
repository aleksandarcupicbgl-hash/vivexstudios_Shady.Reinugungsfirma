#!/usr/bin/env python3
"""
Erzeugt die Leistungsseiten (z. B. treppenhausreinigung-muenchen.html) aus tools/leistungen.py.
Header, Icon-Sprite und Footer werden aus index.html übernommen, damit alles einheitlich bleibt.

Aufruf (im Projektordner):  python3 tools/leistungsseiten-bauen.py
"""
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from leistungen import LEISTUNGEN  # noqa: E402

DOMAIN = "https://cdreinigungsservice.de"

ARROW_LEFT = ('      <symbol id="i-arrow-left" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
              'stroke-linecap="round" stroke-linejoin="round"><path d="M19 12H5"/><path d="m12 19-7-7 7-7"/></symbol>\n')


def tel_link(text):
    # Telefonnummer klickbar machen, optisch unverändert (Klasse link-plain)
    return text.replace("0176 72883621", '<a class="link-plain" href="tel:+4917672883621">0176 72883621</a>')


def plain(text):
    return html.unescape(text)


def ld(data):
    return '  <script type="application/ld+json">\n' + json.dumps(data, ensure_ascii=False, indent=2) + "\n  </script>\n"


def main():
    index = (ROOT / "index.html").read_text(encoding="utf-8")
    sprite = re.search(r'  <svg width="0".*?</svg>', index, re.S).group(0)
    sprite = sprite.replace("    </defs>", ARROW_LEFT + "    </defs>")
    header = re.search(r'  <header class="site-header".*?</header>', index, re.S).group(0).replace(' id="top"', "")
    footer = re.search(r'  <footer class="site-footer">.*?</footer>', index, re.S).group(0)

    for s in LEISTUNGEN:
        url = f"{DOMAIN}/{s['datei']}"
        name = plain(s["name"])
        others = [o for o in LEISTUNGEN if o is not s]

        service_ld = {
            "@context": "https://schema.org",
            "@type": "Service",
            "name": f"{name} in München",
            "serviceType": name,
            "description": plain(s["description"]),
            "url": url,
            "areaServed": {"@type": "City", "name": "München"},
            "provider": {
                "@type": "CleaningService",
                "@id": f"{DOMAIN}/#business",
                "name": "CD Reinigungsservice",
                "telephone": "+49 176 72883621",
                "url": f"{DOMAIN}/",
                "address": {
                    "@type": "PostalAddress",
                    "streetAddress": "Ravensburger Ring 26",
                    "postalCode": "81243",
                    "addressLocality": "München",
                    "addressCountry": "DE",
                },
            },
        }
        breadcrumb_ld = {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Startseite", "item": f"{DOMAIN}/"},
                {"@type": "ListItem", "position": 2, "name": f"{name} München", "item": url},
            ],
        }

        paragraphs = "\n".join(f"          <p>{p}</p>" for p in s["text"])
        umfang = "\n".join(
            f'            <li><svg aria-hidden="true"><use href="#i-check"/></svg><span>{u}</span></li>' for u in s["umfang"]
        )
        faq = "\n".join(
            f'          <details class="faq__item">\n            <summary>{q}</summary>\n            <p>{tel_link(a)}</p>\n          </details>'
            for q, a in s["faq"]
        )
        related = "\n".join(
            f'          <li><a class="related__link" href="{o["datei"]}"><svg aria-hidden="true"><use href="#{o["icon"]}"/></svg> {o["name"]}</a></li>'
            for o in others
        )
        anfrage = f'anfrage.html?leistung={s["slug"]}'

        page = f"""<!doctype html>
<html lang="de">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <title>{s['title']}</title>
  <meta name="description" content="{s['description']}">
  <meta name="theme-color" content="#FFFFFF">
  <link rel="canonical" href="{url}">

  <meta property="og:type" content="website">
  <meta property="og:locale" content="de_DE">
  <meta property="og:site_name" content="CD Reinigungsservice">
  <meta property="og:title" content="{s['title']}">
  <meta property="og:description" content="{s['description']}">
  <meta property="og:url" content="{url}">
  <meta property="og:image" content="{DOMAIN}/assets/img/og-image.png">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta name="twitter:card" content="summary_large_image">

  <link rel="icon" type="image/png" sizes="32x32" href="assets/img/favicon-32.png">
  <link rel="icon" type="image/png" sizes="192x192" href="assets/img/favicon-192.png">
  <link rel="apple-touch-icon" href="assets/img/apple-touch-icon.png">

  <link rel="preload" href="assets/fonts/inter-latin-var.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="stylesheet" href="assets/css/style.css">
  <!-- Plausible Analytics (cookielos, EU-Server) -->
  <script defer data-domain="cdreinigungsservice.de" src="https://plausible.io/js/script.js"></script>
  <script>document.documentElement.classList.add('js')</script>

{ld(service_ld)}{ld(breadcrumb_ld)}</head>
<body>
  <a class="skip-link" href="#main">Zum Inhalt springen</a>

  <!-- Seite erzeugt von tools/leistungsseiten-bauen.py – Texte in tools/leistungen.py ändern -->
{sprite}

{header}

  <main id="main">
    <section class="page-head service-head">
      <div class="container">
        <nav class="breadcrumb" aria-label="Brotkrumen">
          <ol>
            <li><a href="index.html">Startseite</a></li>
            <li><a href="index.html#leistungen">Leistungen</a></li>
            <li aria-current="page">{s['name']}</li>
          </ol>
        </nav>
        <div class="service-head__inner">
          <span class="service-head__icon"><svg aria-hidden="true"><use href="#{s['icon']}"/></svg></span>
          <div>
            <h1>{s['h1']}</h1>
            <p>{s['lead']}</p>
          </div>
        </div>
        <div class="hero__actions">
          <a class="btn btn--primary btn--lg" href="{anfrage}">Jetzt anfragen <svg aria-hidden="true"><use href="#i-arrow"/></svg></a>
          <a class="btn btn--ghost btn--lg" href="tel:+4917672883621"><svg aria-hidden="true"><use href="#i-phone"/></svg> 0176 72883621</a>
        </div>
      </div>
    </section>

    <section class="section service-body">
      <div class="container service-layout">
        <div class="prose">
{paragraphs}

          <h2>Warum CD Reinigungsservice?</h2>
          <p>{s['warum']}</p>

          <h2>Leistungsumfang</h2>
          <ul class="checklist">
{umfang}
          </ul>
        </div>
        <aside class="aside-card service-aside" aria-label="Auf einen Blick">
          <h2>Auf einen Blick</h2>
          <ul>
            <li><svg aria-hidden="true"><use href="#i-check"/></svg> Einsatz in München und Umgebung</li>
            <li><svg aria-hidden="true"><use href="#i-check"/></svg> Einmalig oder regelmäßig</li>
            <li><svg aria-hidden="true"><use href="#i-check"/></svg> Antwort innerhalb von 24 Stunden</li>
            <li><svg aria-hidden="true"><use href="#i-check"/></svg> Kostenloses, individuelles Angebot</li>
          </ul>
          <a class="btn btn--primary btn--block" href="{anfrage}">{s['name']} anfragen</a>
          <a class="btn btn--soft btn--block" href="https://wa.me/4917672883621" target="_blank" rel="noopener"><svg aria-hidden="true"><use href="#i-chat"/></svg> WhatsApp</a>
        </aside>
      </div>
    </section>

    <section class="section section--alt" aria-labelledby="faq-title">
      <div class="container">
        <div class="section__head">
          <span class="eyebrow">FAQ</span>
          <h2 id="faq-title">Häufige Fragen zur {s['name']} in München</h2>
        </div>
        <div class="faq">
{faq}
        </div>
      </div>
    </section>

    <section class="section">
      <div class="container">
        <div class="contact-box">
          <div>
            <span class="eyebrow">Angebot</span>
            <h2>{s['name']} in München anfragen</h2>
            <p>In weniger als einer Minute zum unverbindlichen Angebot – wir melden uns innerhalb von 24 Stunden.</p>
            <p class="contact-box__owner">Eric Nana Kofi Darko<small>Inhaber, CD Reinigungsservice</small></p>
          </div>
          <div class="contact-actions">
            <a class="btn btn--primary btn--lg" href="{anfrage}">Jetzt anfragen <svg aria-hidden="true"><use href="#i-arrow"/></svg></a>
            <a class="btn btn--soft btn--lg" href="tel:+4917672883621"><svg aria-hidden="true"><use href="#i-phone"/></svg> 0176 72883621</a>
            <a class="btn btn--soft btn--lg" href="mailto:eric.darko@freenet.de"><svg aria-hidden="true"><use href="#i-mail"/></svg> E-Mail schreiben</a>
          </div>
        </div>

        <nav class="related" aria-label="Weitere Leistungen">
          <h2>Weitere Leistungen in München</h2>
          <ul>
{related}
          </ul>
        </nav>
      </div>
    </section>
  </main>

{footer}

  <nav class="mobile-bar" aria-label="Schnellkontakt">
    <a class="btn btn--ghost" href="tel:+4917672883621"><svg aria-hidden="true"><use href="#i-phone"/></svg> Anrufen</a>
    <a class="btn btn--primary" href="{anfrage}">Anfragen</a>
  </nav>

  <script src="assets/js/main.js" defer></script>
</body>
</html>
"""
        (ROOT / s["datei"]).write_text(page, encoding="utf-8")
        words = len(" ".join(s["text"] + [s["warum"]] + s["umfang"]).split())
        print(f"{s['datei']} erstellt ({words} Wörter ohne FAQ)")


if __name__ == "__main__":
    main()
