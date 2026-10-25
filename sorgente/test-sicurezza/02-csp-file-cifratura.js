// CSP, file CSV malevoli, backup cifrato manomesso, memoria del telefono avvelenata
const {OUT, ok, fine, apri, demo, fs} = require('./comune');
const P = `"'><img src=x onerror=__x(1)><svg/onload=__x(2)>`;
(async () => { const {b, p, errs, hits} = await apri(); await demo(p);
  // 1. CSP: codice iniettato a mano nel DOM non deve partire, niente invio di dati verso altri siti
  await p.evaluate(() => { const d = document.createElement('div'); d.innerHTML = '<img src=x onerror=__x(91)><a id=jj href="javascript:__x(92)">x</a>'; document.body.appendChild(d); document.getElementById('jj').click(); const s = document.createElement('script'); s.textContent = '__x(93)'; document.body.appendChild(s); });
  await p.waitForTimeout(500); ok('CSP: il codice iniettato non parte', !hits.some(h => h.startsWith('EXEC')), hits.join(' | '));
  ok('CSP: fetch verso un altro sito bloccato', await p.evaluate(async () => { try { await fetch('https://example.com/x'); return false; } catch (e) { return true; } }));
  ok('CSP: immagine verso un altro sito bloccata', await p.evaluate(() => new Promise(r => { const i = new Image(); i.onload = () => r(false); i.onerror = () => r(true); i.src = 'https://example.com/p.png?x=1'; setTimeout(() => r(true), 3000); })));
  hits.length = 0;
  // 2. uso normale e PDF: l'app non viola la propria CSP
  let saved = []; await p.exposeFunction('__save', (f, l) => saved.push(f + ':' + l)); await p.evaluate(() => { downloads.save = async o => { await window.__save(o.filename, String(o.data && o.data.size || o.data).slice(0, 2000)); }; });
  for (const m of [['m', false], ['y', true]]) await p.evaluate(m => exportPDF(m[0], m[1]), m); await p.waitForTimeout(3000);
  ok('PDF mese e anno generati', saved.filter(s => s.includes('.pdf')).length === 2, saved.join(' '));
  ok('nessuna violazione CSP da parte dell\'app', !hits.length, hits.join(' | '));
  // 3. CSV malevolo in importazione
  const csv = 'Data;Categoria;Valore;Nota\n' + ['01/03/2026;' + P + ';-10,00;=HYPERLINK("http://evil","x")', '02/03/2026;Spesa ' + P + ' :: Sub' + P + ';-20,00;+cmd|calc', '03/03/2026;"=1+1";-5;@SUM(A1)', 'xx/yy/zzzz;Boh;abc;' + P, '04/03/2026;' + 'A'.repeat(5000) + ';-1;' + 'B'.repeat(20000), '05/03/2026;Stipendio;1e308;', '06/03/2026;Stipendio;-1e309;', '07/03/2026;__proto__;-3;', '08/03/2026;constructor;-3;'].join('\n');
  fs.writeFileSync(OUT + 'evil.csv', csv);
  await p.evaluate(() => nav({screen:'import'})); await p.waitForTimeout(400); await p.setInputFiles('#imp-f', OUT + 'evil.csv'); await p.waitForTimeout(800);
  const go = await p.$('#imp-go'); if (go) { await go.click(); await p.waitForTimeout(600); }
  ok('CSV: importi sempre numeri finiti', await p.evaluate(() => S.tx.every(x => typeof x.a === 'number' && isFinite(x.a) && Math.abs(x.a) < 1e15)));
  ok('CSV: Object.prototype non inquinato', await p.evaluate(() => ({}).polluted === undefined && Object.getPrototypeOf(S) === Object.prototype));
  for (const s of ['tx', 'stats', 'an', 'cats', 'home']) { await p.evaluate(s => nav({screen:s}), s); await p.waitForTimeout(250); }
  let out = ''; await p.exposeFunction('__csv', d => { out = d; }); await p.evaluate(() => { downloads.save = async o => { await window.__csv(String(o.data)); }; }); await p.evaluate(() => exportCSV()); await p.waitForTimeout(300);
  const formule = out.split('\n').flatMap(l => l.split('";"').map(c => c.replace(/^﻿?"/, ''))).filter(c => /^[=+@]/.test(c));
  ok('CSV esportato: nessuna cella diventa formula', !formule.length, formule.slice(0, 3).join(' | '));
  // 4. backup cifrato
  const env = await p.evaluate(async () => await encryptText(JSON.stringify({cats:S.cats, tx:S.tx}), 'segreto99')); const E = JSON.parse(env);
  const flip = s => { const a = s.split(''); const i = Math.floor(a.length / 2); a[i] = a[i] === 'A' ? 'B' : 'A'; return a.join(''); };
  ok('backup cifrato: nessun testo leggibile', !/Stipendio|Casa|Alimentari/.test(env));
  ok('backup cifrato: si apre con la password giusta', await p.evaluate(async e => { try { return JSON.parse(await decryptText(e, 'segreto99')).tx.length > 0; } catch (x) { return false; } }, E));
  for (const [k, v, pw] of [['password sbagliata', E, 'segreto98'], ['contenuto manomesso', {...E, data:flip(E.data)}], ['iterazioni = 1', {...E, iter:1}], ['iterazioni enormi', {...E, iter:1e12}], ['IV troncato', {...E, iv:'AAAA'}]]) {
    const t0 = Date.now(); const r = await p.evaluate(async ([v, pw]) => { try { await decryptText(v, pw); return false; } catch (e) { return true; } }, [v, pw || 'segreto99']);
    ok('backup cifrato rifiutato: ' + k, r && Date.now() - t0 < 5000, (Date.now() - t0) + ' ms'); }
  // 5. memoria del telefono avvelenata
  await p.evaluate(() => { const d = JSON.parse(localStorage.getItem('b4f-finanza-v1')); d.cats.out[0].id = 'x"><img src=x onerror=__x(7)>'; d.tx[0].c = d.cats.out[0].id; d.tx[1].a = '5<img src=x onerror=__x(8)>'; localStorage.setItem('b4f-finanza-v1', JSON.stringify(d).replace('{"v"', '{"__proto__":{"polluted":1},"v"')); });
  await p.reload(); await p.waitForTimeout(900);
  for (const s of ['tx', 'cats', 'stats', 'an', 'home']) { await p.evaluate(s => nav({screen:s}), s); await p.waitForTimeout(250); }
  ok('memoria avvelenata: prototipo intatto', await p.evaluate(() => Object.getPrototypeOf(S) === Object.prototype && ({}).polluted === undefined));
  ok('memoria avvelenata: importo riportato a numero', await p.evaluate(() => typeof S.tx[1].a === 'number'));
  ok('nessun codice eseguito o iniettato', !hits.length, hits.slice(0, 3).join(' | '));
  ok('nessun errore della pagina', !errs.length, errs.slice(0, 3).join(' | '));
  await b.close(); fine(); })();
