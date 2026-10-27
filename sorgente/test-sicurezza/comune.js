// Funzioni comuni ai test di sicurezza
const {chromium} = require('playwright');
const fs = require('fs'), path = require('path');
const BASE = process.env.B4F_URL || 'http://localhost:8767/';
const OUT = path.join(__dirname, 'out') + '/'; fs.mkdirSync(OUT, {recursive:true});
let fails = 0;
function ok(nome, cond, info){ console.log((cond ? 'OK   ' : 'FAIL ') + nome + (!cond && info !== undefined ? '  → ' + info : '')); if (!cond) fails++; }
function fine(){ console.log(fails ? '\n' + fails + ' prove FALLITE' : '\nTutte le prove superate'); process.exitCode = fails ? 1 : 0; }
// pagina con sonde: __x() segnala codice eseguito, l'osservatore segnala HTML iniettato, e le violazioni della CSP
async function apri(opts = {}){
  const b = await chromium.launch(); const ctx = await b.newContext({viewport:{width:400, height:860}, ...opts}); const p = await ctx.newPage();
  const errs = [], hits = []; p.on('pageerror', e => errs.push(e.message)); p.on('dialog', d => { hits.push('DIALOG ' + d.message()); d.dismiss(); });
  await p.exposeFunction('__hit', m => hits.push(m));
  await p.addInitScript(() => {
    window.__x = n => window.__hit('EXEC ' + n + ' @' + (typeof R !== 'undefined' && JSON.stringify(R)));
    document.addEventListener('securitypolicyviolation', e => window.__hit('CSP ' + e.violatedDirective + ' ' + (e.blockedURI || '')));
    new MutationObserver(ms => { for (const m of ms) for (const n of m.addedNodes) { if (n.nodeType !== 1) continue; for (const e of [n, ...n.querySelectorAll('*')]) {
      const bad = [...e.attributes].filter(a => /^on/i.test(a.name) || /javascript:/i.test(a.value));
      if (bad.length || (e.tagName === 'IMG' && e.getAttribute('src') === 'x') || (e.tagName === 'SCRIPT' && e.textContent.includes('__x')))
        window.__hit('INJECTED <' + e.tagName + ' ' + bad.map(a => a.name).join(',') + '> in ' + (e.parentElement ? e.parentElement.outerHTML.slice(0, 160) : '?'));
    } } }).observe(document, {childList:true, subtree:true});
  });
  return {b, ctx, p, errs, hits};
}
async function demo(p){
  await p.goto(BASE + '?' + Date.now()); await p.waitForTimeout(800); await p.evaluate(() => localStorage.clear()); await p.reload(); await p.waitForTimeout(700);
  await p.check('#w-terms'); await p.click('#demo'); await p.waitForTimeout(400); await p.evaluate(() => { S.demo = false; S.guideSeen = today(); save(); });
}
const PAYLOAD = `"'><img src=x onerror=__x(1)><svg/onload=__x(2)></style></script><script>__x(3)</script>\`\${__x(4)}`;
module.exports = {BASE, OUT, ok, fine, apri, demo, PAYLOAD, fs};
