/* Les Petits Papiers - bandeau cookies (RGPD / recommandations CNIL)
   - Aucun traceur non essentiel n'est déposé avant consentement.
   - Google Analytics (GA4) n'est chargé qu'après acceptation de la mesure d'audience.
   - Refuser est aussi simple qu'accepter ; le choix est conservé 6 mois puis redemandé.
   - Rouvrir le panneau : lppCookies.open() (lien "Gérer les cookies" du pied de page). */
(function () {
  var GA_ID = 'G-7FV756KQ9N';
  var KEY = 'lpp_consent_v1';
  var MAX_AGE = 1000 * 60 * 60 * 24 * 182; // ~6 mois

  function read() {
    try {
      var c = JSON.parse(localStorage.getItem(KEY) || 'null');
      if (c && c.t && (Date.now() - c.t) < MAX_AGE) return c;
    } catch (e) {}
    return null;
  }
  function save(analytics) {
    var c = { analytics: !!analytics, t: Date.now() };
    try { localStorage.setItem(KEY, JSON.stringify(c)); } catch (e) {}
    return c;
  }

  var gaLoaded = false;
  function loadGA() {
    if (gaLoaded) return;
    gaLoaded = true;
    window.dataLayer = window.dataLayer || [];
    window.gtag = function () { window.dataLayer.push(arguments); };
    window.gtag('js', new Date());
    window.gtag('config', GA_ID, { anonymize_ip: true });
    var s = document.createElement('script');
    s.async = true;
    s.src = 'https://www.googletagmanager.com/gtag/js?id=' + GA_ID;
    document.head.appendChild(s);
  }
  function clearGACookies() {
    var host = location.hostname.replace(/^www\./, '');
    document.cookie.split(';').forEach(function (c) {
      var name = c.split('=')[0].trim();
      if (/^_ga/.test(name) || name === '_gid' || name === '_gat') {
        ['', '; domain=' + host, '; domain=.' + host].forEach(function (d) {
          document.cookie = name + '=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/' + d;
        });
      }
    });
  }
  function apply(c) {
    if (c && c.analytics) loadGA();
    else clearGACookies();
  }

  var css = '' +
    '#lpp-cc{position:fixed;left:16px;right:16px;bottom:16px;z-index:100000;display:flex;justify-content:center;pointer-events:none;font-family:Outfit,system-ui,sans-serif}' +
    '#lpp-cc .cc-box{pointer-events:auto;max-width:640px;width:100%;background:#fff;color:#2d2d3a;border:1px solid #e8e6e0;border-radius:20px;box-shadow:0 12px 40px rgba(26,26,46,.18);padding:22px 24px}' +
    '#lpp-cc h2{font-size:17px;font-weight:700;color:#1a1a2e;margin:0 0 6px;font-family:Outfit,system-ui,sans-serif}' +
    '#lpp-cc p{font-size:14px;line-height:1.55;margin:0 0 14px;color:#2d2d3a}' +
    '#lpp-cc a{color:#EB356F;text-decoration:underline}' +
    '#lpp-cc .cc-actions{display:flex;gap:10px;flex-wrap:wrap;justify-content:flex-end}' +
    '#lpp-cc button{font-family:inherit;font-size:14px;font-weight:600;border-radius:50px;padding:10px 18px;cursor:pointer;border:1.5px solid #1a1a2e;background:#fff;color:#1a1a2e;transition:opacity .2s}' +
    '#lpp-cc button:hover{opacity:.85}' +
    '#lpp-cc button.cc-accept{background:#1a1a2e;color:#fff}' +
    '#lpp-cc button.cc-link{border-color:transparent;background:none;color:#7a7a8c;text-decoration:underline;padding:10px 6px;margin-right:auto}' +
    '#lpp-cc .cc-prefs{display:none;border-top:1px solid #e8e6e0;margin:4px 0 14px;padding-top:12px}' +
    '#lpp-cc.cc-open-prefs .cc-prefs{display:block}' +
    '#lpp-cc .cc-row{display:flex;align-items:flex-start;justify-content:space-between;gap:16px;padding:8px 0}' +
    '#lpp-cc .cc-row strong{display:block;font-size:14px;color:#1a1a2e}' +
    '#lpp-cc .cc-row span{display:block;font-size:13px;color:#7a7a8c;line-height:1.45}' +
    '#lpp-cc .cc-switch{position:relative;flex-shrink:0;width:44px;height:24px}' +
    '#lpp-cc .cc-switch input{opacity:0;width:0;height:0;position:absolute}' +
    '#lpp-cc .cc-slider{position:absolute;inset:0;background:#d9d7d1;border-radius:24px;transition:.2s;cursor:pointer}' +
    '#lpp-cc .cc-slider:before{content:"";position:absolute;width:18px;height:18px;left:3px;top:3px;background:#fff;border-radius:50%;transition:.2s}' +
    '#lpp-cc input:checked+.cc-slider{background:#5ACAF1}' +
    '#lpp-cc input:checked+.cc-slider:before{transform:translateX(20px)}' +
    '#lpp-cc input:disabled+.cc-slider{opacity:.6;cursor:not-allowed}' +
    '#lpp-cc input:focus-visible+.cc-slider{outline:2px solid #EB356F;outline-offset:2px}' +
    '@media(max-width:560px){#lpp-cc{left:10px;right:10px;bottom:10px}#lpp-cc .cc-box{padding:18px}#lpp-cc .cc-actions button{flex:1 1 auto}#lpp-cc button.cc-link{flex-basis:100%;text-align:left;margin:0}}';

  var el;
  function build() {
    if (el) return el;
    var st = document.createElement('style');
    st.textContent = css;
    document.head.appendChild(st);
    el = document.createElement('div');
    el.id = 'lpp-cc';
    el.setAttribute('role', 'dialog');
    el.setAttribute('aria-live', 'polite');
    el.setAttribute('aria-label', 'Gestion des cookies');
    el.innerHTML =
      '<div class="cc-box">' +
        '<h2>Un petit cookie ?</h2>' +
        '<p>Nous utilisons des cookies de mesure d\'audience (Google Analytics) pour comprendre comment notre site est utilisé et l\'améliorer. Ils ne sont déposés qu\'avec votre accord. Vous pouvez changer d\'avis à tout moment via le lien « Gérer les cookies » en bas de page. <a href="/politique-de-confidentialite/#cookies">En savoir plus</a></p>' +
        '<div class="cc-prefs" id="lpp-cc-prefs">' +
          '<div class="cc-row"><div><strong>Cookies nécessaires</strong><span>Mémorisent vos choix de cookies. Toujours actifs.</span></div>' +
            '<label class="cc-switch"><input type="checkbox" checked disabled aria-label="Cookies nécessaires (toujours actifs)"><span class="cc-slider"></span></label></div>' +
          '<div class="cc-row"><div><strong>Mesure d\'audience</strong><span>Google Analytics : pages vues, durée de visite, provenance. Données agrégées, IP anonymisée.</span></div>' +
            '<label class="cc-switch"><input type="checkbox" id="lpp-cc-analytics" aria-label="Mesure d\'audience"><span class="cc-slider"></span></label></div>' +
        '</div>' +
        '<div class="cc-actions">' +
          '<button type="button" class="cc-link" data-cc="prefs">Personnaliser</button>' +
          '<button type="button" class="cc-refuse" data-cc="refuse">Tout refuser</button>' +
          '<button type="button" class="cc-accept" data-cc="accept">Tout accepter</button>' +
        '</div>' +
      '</div>';
    el.addEventListener('click', function (e) {
      var b = e.target.closest('[data-cc]');
      if (!b) return;
      var a = b.getAttribute('data-cc');
      if (a === 'accept') done(true);
      else if (a === 'refuse') done(false);
      else if (a === 'save') done(document.getElementById('lpp-cc-analytics').checked);
      else if (a === 'prefs') {
        el.classList.add('cc-open-prefs');
        b.textContent = 'Enregistrer mes choix';
        b.setAttribute('data-cc', 'save');
        b.classList.remove('cc-link');
      }
    });
    document.body.appendChild(el);
    return el;
  }
  function show() {
    build();
    var c = read();
    document.getElementById('lpp-cc-analytics').checked = !!(c && c.analytics);
    el.style.display = 'flex';
  }
  function done(analytics) {
    var c = save(analytics);
    if (el) el.style.display = 'none';
    apply(c);
  }

  window.lppCookies = {
    open: function () { show(); el.classList.add('cc-open-prefs'); var p = el.querySelector('[data-cc="prefs"]'); if (p) { p.textContent = 'Enregistrer mes choix'; p.setAttribute('data-cc', 'save'); p.classList.remove('cc-link'); } },
    accept: function () { done(true); },
    refuse: function () { done(false); }
  };

  function init() {
    var c = read();
    if (c) apply(c); else show();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
