/* ==========================================================================
   CD Reinigungsservice – Anfrageformular (3 Schritte, Versand via Web3Forms)
   ========================================================================== */

/* ---------------------------------------------------------------------------
   KONFIGURATION – hier den Web3Forms Access Key eintragen!
   Kostenlosen Key erhalten: https://web3forms.com → E-Mail-Adresse der Firma
   eingeben → Key kommt per E-Mail → unten statt [WEB3FORMS-ACCESS-KEY] einfügen.
   --------------------------------------------------------------------------- */
var ANFRAGE_CONFIG = {
  web3formsAccessKey: '[WEB3FORMS-ACCESS-KEY]',
  endpoint: 'https://api.web3forms.com/submit',
  fromName: 'Website CD Reinigungsservice',
  demo: false // true = nichts senden, nur Erfolgsmeldung zeigen (für Vorschau)
};

(function () {
  'use strict';

  var form = document.getElementById('anfrage-form');
  if (!form) return;

  var CONFIG = ANFRAGE_CONFIG;
  var TOTAL = 3;
  var current = 1;
  var steps = form.querySelectorAll('.step');
  var card = document.getElementById('form-card');
  var btnNext = document.getElementById('btn-next');
  var btnBack = document.getElementById('btn-back');
  var btnSubmit = document.getElementById('btn-submit');
  var alertBox = document.getElementById('form-alert');
  var success = document.getElementById('success');
  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  var ERR_ICON = '<svg aria-hidden="true"><use href="#i-alert"/></svg>';

  /* ---------- Hilfsfunktionen ---------- */
  function $(sel) { return form.querySelector(sel); }
  function checkedValues(name) {
    return Array.prototype.map.call(form.querySelectorAll('input[name="' + name + '"]:checked'), function (el) { return el.value; });
  }
  function checkedLabels(name) {
    return Array.prototype.map.call(form.querySelectorAll('input[name="' + name + '"]:checked'), function (el) { return el.getAttribute('data-label') || el.value; });
  }
  function val(id) { return (document.getElementById(id).value || '').trim(); }

  function showError(key, msg, target) {
    var el = document.getElementById('err-' + key);
    if (el) { el.innerHTML = ERR_ICON + '<span>' + msg + '</span>'; el.classList.add('is-visible'); }
    if (target) {
      if (target.classList.contains('tiles') || target.classList.contains('choices')) target.classList.add('is-invalid');
      else target.setAttribute('aria-invalid', 'true');
    }
  }
  function clearError(key, target) {
    var el = document.getElementById('err-' + key);
    if (el) { el.textContent = ''; el.classList.remove('is-visible'); }
    if (target) { target.classList.remove('is-invalid'); target.removeAttribute('aria-invalid'); }
  }

  /* ---------- Validierung pro Schritt ---------- */
  function validate(step) {
    var ok = true;
    var first = null;
    function fail(key, msg, target, focusEl) {
      showError(key, msg, target);
      if (ok) first = focusEl || target;
      ok = false;
    }

    if (step === 1) {
      var tiles = document.getElementById('tiles-leistung');
      clearError('leistung', tiles);
      if (!checkedValues('leistung').length) {
        fail('leistung', 'Bitte wählen Sie mindestens eine Leistung aus.', tiles, tiles.querySelector('input'));
      }
    }

    if (step === 2) {
      var obj = document.getElementById('choices-objekt');
      clearError('objektart', obj);
      if (!checkedValues('objektart').length) fail('objektart', 'Bitte wählen Sie die Art des Objekts.', obj, obj.querySelector('input'));

      var ort = document.getElementById('ort');
      clearError('ort', ort);
      if (val('ort').length < 3) fail('ort', 'Bitte geben Sie Ort oder Postleitzahl an, damit wir planen können.', ort);

      var hf = document.getElementById('choices-haeufigkeit');
      clearError('haeufigkeit', hf);
      if (!checkedValues('haeufigkeit').length) fail('haeufigkeit', 'Bitte wählen Sie, wie oft gereinigt werden soll.', hf, hf.querySelector('input'));
    }

    if (step === 3) {
      var name = document.getElementById('name');
      clearError('name', name);
      if (val('name').length < 2) fail('name', 'Bitte geben Sie Ihren Namen an.', name);

      var tel = document.getElementById('telefon');
      clearError('telefon', tel);
      var digits = val('telefon').replace(/\D/g, '');
      if (!val('telefon')) fail('telefon', 'Bitte geben Sie Ihre Telefonnummer an – so erreichen wir Sie am schnellsten.', tel);
      else if (digits.length < 6 || !/^[+\d\s()\/-]+$/.test(val('telefon'))) fail('telefon', 'Diese Telefonnummer sieht unvollständig aus. Bitte prüfen Sie sie noch einmal.', tel);

      var email = document.getElementById('email');
      clearError('email', email);
      var wantsMail = checkedValues('kontaktart')[0] === 'E-Mail';
      if (!val('email') && wantsMail) fail('email', 'Sie möchten per E-Mail kontaktiert werden – bitte geben Sie Ihre E-Mail-Adresse an.', email);
      else if (val('email') && !/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(val('email'))) fail('email', 'Bitte prüfen Sie Ihre E-Mail-Adresse (z. B. name@beispiel.de).', email);

      var ds = document.getElementById('datenschutz');
      clearError('datenschutz', ds);
      if (!ds.checked) fail('datenschutz', 'Bitte bestätigen Sie die Datenschutzerklärung, damit wir Ihre Anfrage bearbeiten dürfen.', ds);
    }

    if (first) first.focus({ preventScroll: false });
    return ok;
  }

  /* ---------- Schrittwechsel ---------- */
  function scrollToForm() {
    var top = card.getBoundingClientRect().top + window.pageYOffset - (document.querySelector('.site-header').offsetHeight + 12);
    window.scrollTo({ top: Math.max(top, 0), behavior: reduced ? 'auto' : 'smooth' });
  }

  function goTo(step) {
    current = step;
    steps.forEach(function (s) { s.hidden = Number(s.getAttribute('data-step')) !== step; });
    var active = form.querySelector('.step[data-step="' + step + '"]');

    document.getElementById('progress-num').textContent = step;
    document.getElementById('progress-label').textContent = active.getAttribute('data-title');
    document.getElementById('progress-fill').style.width = (step / TOTAL * 100) + '%';
    form.querySelector('.progress__bar').setAttribute('aria-valuenow', step);
    form.querySelectorAll('.progress__steps li').forEach(function (li, i) { li.classList.toggle('is-active', i === step - 1); });

    btnBack.hidden = step === 1;
    btnNext.hidden = step === TOTAL;
    btnSubmit.hidden = step !== TOTAL;
    alertBox.classList.remove('is-visible');

    if (step === TOTAL) renderSummary();

    scrollToForm();
    var h = active.querySelector('h2');
    if (h) h.focus({ preventScroll: true });
  }

  btnNext.addEventListener('click', function () {
    if (validate(current)) goTo(current + 1);
  });
  btnBack.addEventListener('click', function () { goTo(current - 1); });

  // Enter in Textfeldern führt zum nächsten Schritt statt zum Absenden
  form.addEventListener('keydown', function (e) {
    if (e.key === 'Enter' && e.target.tagName === 'INPUT' && current < TOTAL) {
      e.preventDefault();
      btnNext.click();
    }
  });

  // Fehler sofort entfernen, sobald korrigiert wird
  form.addEventListener('change', function (e) {
    var n = e.target.name;
    if (n === 'leistung') clearError('leistung', document.getElementById('tiles-leistung'));
    if (n === 'objektart') clearError('objektart', document.getElementById('choices-objekt'));
    if (n === 'haeufigkeit') clearError('haeufigkeit', document.getElementById('choices-haeufigkeit'));
    if (n === 'datenschutz') clearError('datenschutz', e.target);
    if (n === 'kontaktart') {
      document.getElementById('email-optional').hidden = e.target.value === 'E-Mail';
      clearError('email', document.getElementById('email'));
    }
  });
  form.addEventListener('input', function (e) {
    if (['ort', 'name', 'telefon', 'email'].indexOf(e.target.id) > -1 && e.target.getAttribute('aria-invalid')) {
      clearError(e.target.id, e.target);
    }
  });

  /* ---------- Zusammenfassung vor dem Absenden ---------- */
  function esc(s) {
    return String(s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; });
  }
  function renderSummary() {
    var rows = [
      ['Leistung', checkedLabels('leistung').join(', ')],
      ['Objekt', checkedValues('objektart')[0]],
      ['Ort / PLZ', val('ort')],
      ['Häufigkeit', checkedValues('haeufigkeit')[0]],
      ['Termin', val('termin')]
    ].filter(function (r) { return r[1]; });
    document.getElementById('summary').innerHTML = '<dl>' + rows.map(function (r) {
      return '<dt>' + esc(r[0]) + '</dt><dd>' + esc(r[1]) + '</dd>';
    }).join('') + '</dl>';
  }

  /* ---------- Vorauswahl über URL (?leistung=bueroreinigung) ---------- */
  var pre = new URLSearchParams(window.location.search).get('leistung');
  if (pre) {
    pre.split(',').forEach(function (v) {
      var box = form.querySelector('input[name="leistung"][value="' + v.trim().toLowerCase().replace(/[^a-z]/g, '') + '"]');
      if (box) box.checked = true;
    });
  }

  /* ---------- Absenden ---------- */
  function setLoading(on) {
    btnSubmit.disabled = on;
    btnBack.disabled = on;
    btnSubmit.querySelector('span').textContent = on ? 'Wird gesendet …' : 'Anfrage absenden';
  }
  function showAlert(msg) {
    alertBox.innerHTML = msg;
    alertBox.classList.add('is-visible');
  }
  function showSuccess() {
    form.hidden = true;
    success.hidden = false;
    scrollToForm();
    success.querySelector('h2').focus({ preventScroll: true });
  }

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    if (current !== TOTAL) { btnNext.click(); return; }
    if (!validate(3)) return;

    // Honeypot: Bots füllen das versteckte Feld aus → still "erfolgreich" beenden
    if (val('website')) { showSuccess(); return; }

    if (CONFIG.demo) { showSuccess(); return; }

    var fallback = 'Bitte rufen Sie uns direkt an: <a href="tel:+4917672883621">0176 72883621</a>.';
    if (!CONFIG.web3formsAccessKey || CONFIG.web3formsAccessKey.indexOf('[') === 0) {
      console.warn('Web3Forms Access Key fehlt – bitte in assets/js/anfrage.js eintragen.');
      showAlert('Das Anfrageformular ist noch nicht vollständig eingerichtet. ' + fallback);
      return;
    }

    var leistungen = checkedLabels('leistung');
    var name = val('name');
    var payload = {
      access_key: CONFIG.web3formsAccessKey,
      subject: 'Neue Anfrage: ' + leistungen.join(', ') + ' – ' + name,
      from_name: CONFIG.fromName,
      botcheck: '',
      'Leistung(en)': leistungen.join(', '),
      'Objektart': checkedValues('objektart')[0],
      'Ort / PLZ': val('ort'),
      'Gewünschter Termin / Zeitraum': val('termin') || '–',
      'Häufigkeit': checkedValues('haeufigkeit')[0],
      'Nachricht': val('nachricht') || '–',
      'Name': name,
      'Telefon': val('telefon'),
      'E-Mail': val('email') || '–',
      'Bevorzugte Kontaktart': checkedValues('kontaktart')[0],
      'Datenschutz akzeptiert': 'Ja',
      'Gesendet am': new Date().toLocaleString('de-DE')
    };
    if (val('email')) payload.replyto = val('email');

    setLoading(true);
    fetch(CONFIG.endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify(payload)
    })
      .then(function (res) { return res.json().catch(function () { return {}; }).then(function (data) { return { ok: res.ok, data: data }; }); })
      .then(function (r) {
        if (r.ok && r.data.success !== false) showSuccess();
        else throw new Error(r.data.message || 'Versand fehlgeschlagen');
      })
      .catch(function (err) {
        console.error(err);
        showAlert('Ihre Anfrage konnte leider nicht gesendet werden. Bitte versuchen Sie es erneut oder ' + fallback.charAt(0).toLowerCase() + fallback.slice(1));
      })
      .then(function () { setLoading(false); });
  });
})();
