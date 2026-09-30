#!/usr/bin/env python3
"""
Baut eine Vorschau-Datei (vorschau.html), die alle Seiten, Bilder und die Schrift
enthält. Die Navigation funktioniert auch ohne JavaScript (CSS :target), z. B. in
App-Vorschauen. Aufruf:  python3 tools/vorschau-bauen.py [--demo]
  --demo  Formular sendet nichts, zeigt nur die Erfolgsmeldung.
"""
import base64
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEMO = "--demo" in sys.argv
PAGES = {"index.html": "start", "anfrage.html": "anfrage", "impressum.html": "impressum", "datenschutz.html": "datenschutz"}


def data_uri(rel, mime):
    return f"data:{mime};base64," + base64.b64encode((ROOT / rel).read_bytes()).decode()


def rewrite_links(html):
    def repl(m):
        href = m.group(1)
        path, _, query = href.partition("?")
        path, _, frag = path.partition("#")
        if path not in PAGES:
            return m.group(0)
        extra = ""
        q = re.match(r"leistung=([a-z]+)", query)
        if q:
            extra = f' data-leistung="{q.group(1)}"'
        target = "#" + (frag if frag and path == "index.html" else PAGES[path])
        return f'href="{target}"{extra}'
    html = re.sub(r'href="([^"#:][^"]*)"', repl, html)
    return re.sub(r'(href="#(?:start|anfrage|impressum|datenschutz)"[^>]*?) target="_blank"', r"\1", html)


def main():
    css = (ROOT / "assets/css/style.css").read_text(encoding="utf-8")
    css = css.replace('url("../fonts/inter-latin-var.woff2")', 'url("' + data_uri("assets/fonts/inter-latin-var.woff2", "font/woff2") + '")')
    imgs = {f"assets/img/{n}": data_uri(f"assets/img/{n}", m) for n, m in [("logo.png", "image/png"), ("logo-full.jpg", "image/jpeg")]}

    sprite, views = "", []
    for page, vid in PAGES.items():
        s = (ROOT / page).read_text(encoding="utf-8")
        body = s[s.index("<body>") + 6:s.index("</body>")]
        sp = re.search(r'<svg width="0".*?</svg>', body, re.S)
        if page == "anfrage.html":
            sprite = sp.group(0)
        body = body.replace(sp.group(0), "").replace("<!-- Icon-Sprite -->", "")
        body = re.sub(r"<script[^>]*></script>", "", body)
        body = re.sub(r'<a class="skip-link"[^>]*>.*?</a>', "", body)
        body = body.replace(' id="main"', "").replace(' id="top"', "")
        for rel, uri in imgs.items():
            body = body.replace(f'src="{rel}"', f'src="{uri}"')
        # Hero-Foto: nur eine eingebettete Version statt srcset
        body = re.sub(r'<source type="image/webp"[^>]*>\s*', "", body)
        body = re.sub(r'<img src="assets/img/hero-reinigung-1376.jpg" srcset="[^"]*" sizes="[^"]*"',
                      '<img src="' + data_uri("assets/img/hero-reinigung-1376.webp", "image/webp") + '"', body)
        views.append(f'<div class="view" id="{vid}">{rewrite_links(body)}</div>')

    js = (ROOT / "assets/js/anfrage.js").read_text(encoding="utf-8")
    js = js.replace("document.querySelector('.site-header').offsetHeight", "document.querySelector('#anfrage .site-header').offsetHeight")
    if DEMO:
        js = js.replace("  demo: false", "  demo: true")
    main_js = (ROOT / "assets/js/main.js").read_text(encoding="utf-8")
    router = """
document.addEventListener('click', function (e) {
  var a = e.target.closest('a[data-leistung]');
  if (!a) return;
  document.querySelectorAll('input[name="leistung"]').forEach(function (b) { b.checked = b.value === a.getAttribute('data-leistung'); });
});
window.addEventListener('hashchange', function () {
  if (/^#(start|anfrage|impressum|datenschutz)$/.test(location.hash)) window.scrollTo(0, 0);
});
document.querySelectorAll('.reveal').forEach(function (r) { r.classList.add('is-visible'); });
"""
    note = "Vorschau · Formular sendet nichts (Demo-Modus)" if DEMO else "Vorschau"
    html = f"""<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>CD Reinigungsservice – Vorschau</title>
<link rel="icon" href="{data_uri('assets/img/favicon-32.png', 'image/png')}">
<style>{css}
.view {{ display: none; }}
.view:target, #start {{ display: block; }}
body:has(.view:target) #start:not(:target) {{ display: none; }}
.preview-note {{ background: var(--text); color: #fff; font-size: .875rem; text-align: center; padding: .5rem 1rem; }}
</style>
<script>document.documentElement.classList.add('js')</script>
</head>
<body>
<div class="preview-note">{note}</div>
{sprite}
{''.join(views)}
<script>{main_js}</script>
<script>{js}</script>
<script>{router}</script>
</body>
</html>"""
    out = ROOT / "vorschau.html"
    out.write_text(html, encoding="utf-8")
    print(f"{out.name} erstellt ({len(html) // 1024} KB)")


if __name__ == "__main__":
    main()
