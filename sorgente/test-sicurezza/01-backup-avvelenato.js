// Backup malevolo: codice in ogni campo (A = testi e codici, B = anche numeri, date e colori), ripristino e giro di tutte le schermate
const {OUT, ok, fine, apri, demo, PAYLOAD, fs} = require('./comune');
const SCREENS = ['home','tx','stats','an','cats','pillars','pillar','goal','dues','debts','settings','gym','missions','mission','learn','lesson','read','whatif','sim','review','gtips','well','wbi','legend','champ','notif','import','add','privacy','terms','breath'];
const SEL = '#view button:not(.danger), #view [data-nav], #view .chip, #view [data-id], #view summary';
(async () => { for (const V of ['A', 'B']) {
  const {b, p, errs, hits} = await apri(); await demo(p);
  const bk = await p.evaluate(([P, V]) => { const d = JSON.parse(JSON.stringify(S)); const skip = new Set(['t', 'screen', 'kind', 'rec', 'g']);
    const isDate = s => /^\d{4}-\d{2}(-\d{2})?(T.*)?$/.test(s), isCol = s => /^#[0-9a-f]{3,8}$/i.test(s);
    const walk = (o, k) => { if (Array.isArray(o)) return o.map(x => walk(x, k)); if (o && typeof o === 'object') { for (const kk of Object.keys(o)) if (kk !== 'lock') o[kk] = walk(o[kk], kk); return o; }
      if (typeof o === 'string') { if (V === 'A' && (skip.has(k) || isDate(o) || isCol(o) || k === 'i' || k === 'col')) return o; if (V === 'B' && skip.has(k) && k !== 'g') return o; return o + P; }
      if (typeof o === 'number' && V === 'B' && ['a', 'target', 'saved', 'v'].includes(k)) return String(o) + P; return o; };
    walk(d, ''); d.app = 'buddy4free-risparmio'; d.exported = '2026-01-01' + P; d.XPROTOX = {polluted:1}; return JSON.stringify(d); }, [PAYLOAD, V]);
  fs.writeFileSync(OUT + 'evil-' + V + '.json', bk.replace('"XPROTOX"', '"__proto__"'));
  await p.evaluate(() => nav({screen:'settings'})); await p.waitForTimeout(400); await p.setInputFiles('#s-rs', OUT + 'evil-' + V + '.json'); await p.waitForTimeout(500); await p.click('#rb-yes'); await p.waitForTimeout(600);
  ok(V + ' backup ripristinato', await p.evaluate(() => S.tx.length > 50));
  ok(V + ' nessun __proto__ inquinato', await p.evaluate(() => Object.getPrototypeOf(S) === Object.prototype && ({}).polluted === undefined));
  const q = await p.evaluate(() => ({g:(S.goals[0] || {}).id, c:(S.cats.out[0] || {}).id, ci:(S.cats.in[0] || {}).id, d:(S.debts[0] || {}).id, du:(S.dues[0] || {}).id}));
  const routes = SCREENS.map(s => ({screen:s})).concat([{screen:'goal', id:q.g}, {screen:'cats', t:'out', id:q.c}, {screen:'cats', t:'in', id:q.ci}, {screen:'cats', t:'out'}, {screen:'pillar', id:'liq'}, {screen:'pillar', id:'emerg'}, {screen:'pillar', id:'inv'}, {screen:'debts', open:q.d}, {screen:'dues', form:q.du}, {screen:'lesson', i:0}, {screen:'read', i:0}]);
  let clicks = 0;
  for (const r of routes) { try { await p.evaluate(r => nav(r), r); await p.waitForTimeout(200); } catch (e) { errs.push('nav ' + JSON.stringify(r) + ' ' + e.message.split('\n')[0]); continue; }
    const n = await p.evaluate(s => document.querySelectorAll(s).length, SEL);
    for (let i = 0; i < Math.min(n, 45); i++) { try { await p.evaluate(r => { if (R.screen !== r.screen || document.querySelector('#catpop,.sheet')) nav(r); }, r);
      const did = await p.evaluate(([i, s]) => { const el = document.querySelectorAll(s)[i]; if (!el || /elimina|cancella|ripristina|reset|azzera/i.test(el.textContent)) return false; el.click(); return true; }, [i, SEL]);
      if (did) { clicks++; await p.waitForTimeout(50); await p.evaluate(() => { const o = document.querySelector('#catpop'); if (o) o.querySelectorAll('button').forEach((b, j) => { if (j < 6 && !/elimina|cancella/i.test(b.textContent)) try { b.click(); } catch (e) {} }); }); }
    } catch (e) {} }
    await p.evaluate(() => document.querySelectorAll('#catpop,.sheet').forEach(x => x.remove()));
  }
  let saved = []; await p.exposeFunction('__save', (f, l) => saved.push(f + ':' + l)); await p.evaluate(() => { downloads.save = async o => { await window.__save(o.filename, o.data && o.data.size || String(o.data).length); }; });
  await p.evaluate(async () => { await exportCSV(); await exportPDF('y', true); }).catch(e => errs.push('export ' + e.message)); await p.waitForTimeout(3000);
  ok(V + ' CSV e PDF generati con dati avvelenati', saved.length >= 2, saved.join(' '));
  ok(V + ' nessun codice eseguito o HTML iniettato (' + clicks + ' clic)', !hits.length, hits.slice(0, 3).join(' | '));
  ok(V + ' nessun errore della pagina', !errs.length, errs.slice(0, 3).join(' | '));
  await b.close(); } fine(); })();
