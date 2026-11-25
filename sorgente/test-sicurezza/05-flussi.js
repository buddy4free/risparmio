// Flussi principali, come li usa un tester: aggiungere un movimento, backup protetto e ripristino, import CSV, tutte le schermate senza errori
const {OUT, ok, fine, apri, demo, fs} = require('./comune');
(async () => { const {b, p, errs, hits} = await apri();
  await demo(p); await p.evaluate(() => { S.newsSeen = NEWS.map(n => n.k); save(); nav({screen:'home'}); }); await p.waitForTimeout(500);
  const close = () => p.evaluate(() => { document.querySelectorAll('.psheet, #dial').forEach(x => x.remove()); });

  // 1. aggiungere un'uscita dal tasto +, passo per passo
  await close(); const n0 = await p.evaluate(() => S.tx.length);
  await p.click('#fab'); await p.waitForTimeout(300); await p.click('[data-dial="out"]'); await p.waitForTimeout(400);
  await p.click('[data-cl="alimentari"]'); await p.waitForTimeout(300);
  const sub = await p.$('[data-cs="Supermercato"]'); if (sub) { await sub.click(); await p.waitForTimeout(300); }
  const dst = await p.$('[data-p="liq"]'); if (dst) { await dst.click(); await p.waitForTimeout(400); }
  for (const k of ['1', '2', ',', '5', '0']) await p.click('[data-k2="' + k + '"]');
  await p.click('[data-k2="ok"]'); await p.waitForTimeout(400);
  await p.fill('#f-n', 'Prova automatica'); await p.click('[data-savebig]'); await p.waitForTimeout(600);
  const nuovo = await p.evaluate(() => S.tx.find(x => x.n === 'Prova automatica'));
  ok('movimento aggiunto dal tasto +', await p.evaluate(() => S.tx.length) === n0 + 1 && !!nuovo, JSON.stringify(nuovo));
  ok('importo, categoria e data giusti', nuovo && nuovo.a === 12.5 && nuovo.t === 'out' && nuovo.c === 'alimentari' && nuovo.d === (await p.evaluate(() => today())), JSON.stringify(nuovo));
  await p.evaluate(() => nav({screen:'tx'})); await p.waitForTimeout(500);
  ok('il movimento compare nei Movimenti', await p.evaluate(() => document.getElementById('view').innerText.includes('Prova automatica')), await p.evaluate(() => document.getElementById('view').innerText.slice(0, 300)));

  // 1b. etichetta e nota scritte prima dell'importo non si perdono
  await p.evaluate(() => { F = null; nav({screen:'add', type:'out'}); }); await p.waitForTimeout(400);
  await p.click('[data-cl="alimentari"]'); await p.waitForTimeout(300); const sb2 = await p.$('[data-cs="Supermercato"]'); if (sb2) { await sb2.click(); await p.waitForTimeout(300); } const ds2 = await p.$('[data-p="liq"]'); if (ds2) { await ds2.click(); await p.waitForTimeout(400); }
  await p.fill('#f-tag', 'Prima etichetta'); await p.fill('#f-n', 'Prima nota'); await p.click('#f-a'); await p.waitForTimeout(300);
  for (const k of ['8', '5']) await p.click('[data-k2="' + k + '"]'); await p.click('[data-k2="ok"]'); await p.waitForTimeout(400); await p.click('[data-savebig]'); await p.waitForTimeout(500);
  ok('etichetta e nota scritte prima dell\'importo restano', await p.evaluate(() => S.tx.some(x => x.n === 'Prima nota' && x.tag === 'Prima etichetta' && x.a === 85)), await p.evaluate(() => JSON.stringify(S.tx.filter(x => x.a === 85).map(x => [x.n, x.tag]))));

  // 2. backup protetto e ripristino
  let file = ''; await p.exposeFunction('__bk', d => { file = d; });
  await p.evaluate(() => { downloads.save = async o => { await window.__bk(String(o.data)); }; nav({screen:'settings', sec:'sicurezza'}); }); await p.waitForTimeout(400);
  await p.click('#s-bk'); await p.waitForTimeout(300); await p.fill('#bk-p1', 'prova123'); await p.fill('#bk-p2', 'prova123'); await p.click('#bk-enc'); await p.waitForTimeout(1500);
  ok('backup protetto salvato e illeggibile senza password', file.length > 100 && !file.includes('Prova automatica'));
  const prima = await p.evaluate(() => JSON.stringify({n:S.tx.length, tot:S.tx.reduce((t, x) => t + x.a, 0).toFixed(2), cats:S.cats.out.length, goals:(S.goals || []).length}));
  fs.writeFileSync(OUT + 'flussi-backup.json', file);
  await p.evaluate(() => { S.tx = S.tx.slice(0, 3); S.goals = []; save(); nav({screen:'settings', sec:'sicurezza'}); }); await p.waitForTimeout(400);
  await p.setInputFiles('#s-rs', OUT + 'flussi-backup.json'); await p.waitForTimeout(500);
  const pw = await p.$('#rb-pw'); if (pw) { await pw.fill('prova123'); await p.click('#rb-ok'); await p.waitForTimeout(1500); }
  const yes = await p.$('#rb-yes'); if (yes) { await yes.click(); await p.waitForTimeout(800); }
  const dopo = await p.evaluate(() => JSON.stringify({n:S.tx.length, tot:S.tx.reduce((t, x) => t + x.a, 0).toFixed(2), cats:S.cats.out.length, goals:(S.goals || []).length}));
  ok('ripristino: tornano tutti i dati (movimenti, totali, categorie, obiettivi)', prima === dopo, prima + ' → ' + dopo);
  await p.reload(); await p.waitForTimeout(900);
  ok('i dati ripristinati restano dopo la riapertura', await p.evaluate(() => S.tx.some(x => x.n === 'Prova automatica')));

  // 3. import CSV
  await close(); const n1 = await p.evaluate(() => S.tx.length);
  fs.writeFileSync(OUT + 'flussi.csv', 'Data;Categoria;Valore;Nota\n03/11/2026;Alimentari;-23,40;Spesa CSV\n04/11/2026;Stipendio;1500,00;Stipendio CSV\n05/11/2026;Trasporti;-9,90;Treno CSV\n');
  await p.evaluate(() => nav({screen:'import'})); await p.waitForTimeout(400); await p.setInputFiles('#imp-f', OUT + 'flussi.csv'); await p.waitForTimeout(800);
  const go = await p.$('#imp-go'); if (go) { await go.click(); await p.waitForTimeout(800); }
  const imp = await p.evaluate(() => S.tx.filter(x => / CSV$/.test(x.n || '')).map(x => x.t + ':' + x.a + ':' + x.d).sort());
  ok('import CSV: 3 movimenti con segno, importo e data', imp.length === 3 && imp.includes('out:23.4:2026-11-03') && imp.includes('in:1500:2026-11-04'), JSON.stringify(imp) + ' (prima ' + n1 + ')');

  // 3b. stipendi impostati: restano dopo la riapertura (il 24/11/2026 un errore li cancellava all'avvio)
  await p.evaluate(() => { S.pays = [1, 2, 3].map(i => mkPay({kind:i === 3 ? 'pens' : 'stip', net:1000 * i, day:10 + i, mens:13, name:'P' + i})); save(); });
  await p.reload(); await p.waitForTimeout(900);
  ok('stipendi: dopo la riapertura ci sono ancora tutti', await p.evaluate(() => pays().length === 3 && pays().every(q => q.net > 0)), await p.evaluate(() => JSON.stringify(S.pays)));
  // recupero per chi li ha persi: ricostruiti dalle entrate confermate, stesso collegamento
  const rid = await p.evaluate(() => { const q = S.pays[0]; S.tx.push({id:'rz1', t:'in', c:'stipendio', s:'', a:1234, d:addMonths(curYM(), -1) + '-11', n:'P1', pay:q.id}); S.pays = []; delete S.payRescueNo; save(); return q.id; });
  await p.evaluate(() => nav({screen:'home'})); await p.waitForTimeout(400); await p.evaluate(() => document.querySelectorAll('.psheet').forEach(x => x.remove())); await p.evaluate(() => nav({screen:'home'})); await p.waitForTimeout(1500);
  const rs = await p.$('#prs-ok'); if (rs) { await rs.click(); await p.waitForTimeout(400); }
  ok('stipendi persi: si ripristinano dalle entrate confermate', await p.evaluate(id => pays().some(q => q.id === id && q.net === 1234 && q.day === 11), rid), await p.evaluate(() => JSON.stringify(S.pays)));

  // 4. tutte le schermate si aprono senza errori
  const scr = ['home', 'tx', 'charts', 'stats', 'an', 'review', 'pillars', 'goals', 'sim', 'debts', 'gym', 'missions', 'learn', 'well', 'rec', 'dues', 'tags', 'cats', 'pay', 'notif', 'legend', 'howto', 'support', 'privacy', 'terms'];
  const vuote = [];
  for (const s of scr) { await close(); const e0 = errs.length; await p.evaluate(s => { try { nav({screen:s}); } catch (e) { console.error(e); } }, s); await p.waitForTimeout(250);
    const t = await p.evaluate(() => document.getElementById('view').innerText.trim().length); if (t < 20 || errs.length > e0) vuote.push(s + (errs.length > e0 ? ' (' + errs[errs.length - 1] + ')' : ' (vuota)')); }
  for (const sec of ['profilo', 'aspetto', 'sicurezza', 'dati', 'aiuto', 'info', 'avanzate']) { const e0 = errs.length; await p.evaluate(sec => nav({screen:'settings', sec}), sec); await p.waitForTimeout(200); if (errs.length > e0) vuote.push('settings/' + sec); }
  ok('tutte le schermate si aprono con contenuto e senza errori', !vuote.length, vuote.join(', '));
  // statistiche nei tre periodi
  for (const m of ['m', 'y', 'p']) { await p.evaluate(m => { ST.mode = m; nav({screen:'stats'}); }, m); await p.waitForTimeout(250); }
  ok('statistiche: mese, anno e periodo senza errori', !errs.length, errs.join(' | '));
  ok('nessun errore in tutto il percorso', !errs.length, errs.join(' | '));
  ok('nessun codice eseguito o iniettato', !hits.length, hits.join(' | '));
  await b.close(); fine();
})();
