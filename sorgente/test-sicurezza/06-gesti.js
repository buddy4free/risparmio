// Gesti col dito (telefono simulato) e col mouse: scorrere la pagina, girare il cerchio, cambiare scheda, finestra veloce, fumetti delle novità
const {chromium, devices} = require('playwright');
const {BASE, ok, fine} = require('./comune');
(async () => { const b = await chromium.launch(); const errs = [];
  const nuova = async (opts) => { const ctx = await b.newContext(opts); const p = await ctx.newPage(); p.on('pageerror', e => errs.push(e.message));
    await p.goto(BASE + '?' + Date.now()); await p.waitForTimeout(800); await p.evaluate(() => localStorage.clear()); await p.reload(); await p.waitForTimeout(700);
    await p.check('#w-terms'); await p.click('#demo'); await p.waitForTimeout(400);
    await p.evaluate(() => { S.demo = false; S.guideSeen = today(); S.payAsk = today(); S.newsSeen = NEWS.map(n => n.k); save(); });
    return {ctx, p}; };

  // ---- dito ----
  const {ctx, p} = await nuova({...devices['Pixel 7']}); const cdp = await ctx.newCDPSession(p);
  const swipe = async (x, y, dx, dy) => { await cdp.send('Input.dispatchTouchEvent', {type:'touchStart', touchPoints:[{x, y}]});
    for (let i = 1; i <= 12; i++) { await cdp.send('Input.dispatchTouchEvent', {type:'touchMove', touchPoints:[{x:x + i * dx, y:y + i * dy}]}); await p.waitForTimeout(16); }
    await cdp.send('Input.dispatchTouchEvent', {type:'touchEnd', touchPoints:[]}); await p.waitForTimeout(700); };
  await p.evaluate(() => nav({screen:'stats'})); await p.waitForTimeout(700);
  const svg = await p.$('.donut svg:has(circle[data-dk])');
  await svg.evaluate(el => { const c = el.closest('.carousel'); c.scrollLeft = el.closest('.slide').offsetLeft - c.children[0].offsetLeft; el.scrollIntoView({block:'center'}); }); await p.waitForTimeout(700);
  const st = () => svg.evaluate(el => ({y:Math.round(scrollY), x:Math.round(el.closest('.carousel').scrollLeft), r:Math.round(+(el.querySelector('.drot').dataset.r || 0))}));
  let bb = await svg.boundingBox(); const sc = bb.width / 340, cx = bb.x + 170 * sc, cy = bb.y + 115 * sc;
  let a = await st(); await swipe(bb.x + 20 * sc, cy, 0, -18); let z = await st();
  ok('dito in su fuori dall\'anello: la pagina scorre', z.y > a.y + 50, JSON.stringify([a, z]));
  await svg.evaluate(el => el.scrollIntoView({block:'center'})); await p.waitForTimeout(500); bb = await svg.boundingBox();
  a = await st(); await swipe(bb.x + 170 * sc, bb.y + (115 - 62) * sc, 10, 0); z = await st();
  ok('dito di lato sull\'anello: il cerchio gira e la scheda resta', z.r !== a.r && z.x === a.x, JSON.stringify([a, z]));
  bb = await svg.boundingBox(); a = await st(); await swipe(bb.x + 15 * sc, bb.y + 115 * sc, 24, 0); z = await st();
  ok('dito di lato fuori dall\'anello: torna alla scheda precedente', z.x < a.x, JSON.stringify([a, z]));
  // tocco su uno spicchio → pulsanti → finestra veloce
  await svg.evaluate(el => { const c = el.closest('.carousel'); c.scrollLeft = el.closest('.slide').offsetLeft - c.children[0].offsetLeft; el.scrollIntoView({block:'center'}); }); await p.waitForTimeout(700);
  const pt = await svg.evaluate(el => { const c = el.querySelector('circle[data-dk]'), r = el.getBoundingClientRect(), s = r.width / 340, g = (+c.dataset.dm + +(el.querySelector('.drot').dataset.r || 0) - 90) * Math.PI / 180; return [r.left + (170 + 62 * Math.cos(g)) * s, r.top + (115 + 62 * Math.sin(g)) * s]; });
  await p.mouse.click(pt[0], pt[1]); await p.waitForTimeout(400);
  ok('tocco su uno spicchio: compaiono Movimenti e Dettaglio', await p.evaluate(() => { const a = document.querySelector('.dact'); return !!a && !a.hidden; }));
  await p.click('.dact:not([hidden]) .dlist'); await p.waitForTimeout(500);
  ok('Movimenti: finestra con andamento ed elenco', await p.evaluate(() => !!document.querySelector('#dnpop .dncum') && document.querySelectorAll('#dnpop .item').length > 0));
  await p.click('#dnpop [data-m="see"]'); await p.waitForTimeout(400);
  ok('Dettaglio: un altro cerchio con le parti', await p.evaluate(() => !!document.querySelector('#dnpop .donut svg') && document.querySelectorAll('#dnpop .dnrows button').length > 0));
  const pin = await p.$('#dnpop .donut svg'); const pb = await pin.boundingBox(); const ps = pb.width / 340;
  a = await p.evaluate(() => ({y:Math.round(scrollY), s:document.querySelector('.dnpin').scrollTop})); await swipe(pb.x + 232 * ps, pb.y + 105 * ps, 0, 6);
  z = await p.evaluate(() => ({y:Math.round(scrollY), s:document.querySelector('.dnpin').scrollTop, r:+(document.querySelector('#dnpop .drot').dataset.r || 0)}));
  ok('nella finestra il cerchio gira senza muovere quello che c\'è sotto', z.y === a.y && z.s === a.s && z.r !== 0, JSON.stringify([a, z]));
  await p.evaluate(() => document.getElementById('dnpop').remove());
  // barra di una categoria in Home → finestra veloce
  await p.evaluate(() => nav({screen:'home'})); await p.waitForTimeout(600); await p.evaluate(() => document.querySelectorAll('.psheet').forEach(x => x.remove()));
  const bar = await p.$('.catscroll .hbar[data-dnp]'); await bar.scrollIntoViewIfNeeded(); await bar.click(); await p.waitForTimeout(500);
  ok('Home: toccando una categoria si apre la finestra veloce', await p.evaluate(() => !!document.getElementById('dnpop')));
  await p.evaluate(() => document.getElementById('dnpop').remove());
  // fumetti delle novità: tester con novità non viste sì, nuova installazione no
  await p.evaluate(() => { S.newsSeen = []; NEWSN = 0; save(); nav({screen:'home'}); }); await p.waitForTimeout(400); await p.evaluate(() => document.querySelectorAll('.psheet').forEach(x => x.remove())); await p.waitForTimeout(2600);
  ok('novità: il fumetto compare a chi non l\'ha visto', await p.evaluate(() => !!document.querySelector('.tipb.nwb')));
  await p.click('.tipb.nwb .skip'); await p.waitForTimeout(300);
  ok('novità: "Salta tutte" le segna tutte come viste', await p.evaluate(() => newsTodo().length === 0));
  await ctx.close();

  // ---- mouse (computer) ----
  const m = await nuova({viewport:{width:1280, height:900}}); await m.p.evaluate(() => nav({screen:'stats'})); await m.p.waitForTimeout(700);
  const car = await m.p.$('.carousel'); await car.scrollIntoViewIfNeeded(); const cb = await car.boundingBox(); const sl = () => car.evaluate(el => Math.round(el.scrollLeft));
  await m.p.mouse.move(cb.x + cb.width * .8, cb.y + 30); await m.p.mouse.down(); await m.p.mouse.move(cb.x + cb.width * .3, cb.y + 30, {steps:10}); await m.p.mouse.up(); await m.p.waitForTimeout(800);
  const x1 = await sl(); ok('mouse: trascinando si passa alla scheda dopo', x1 > 100, x1);
  await m.p.mouse.move(cb.x + cb.width * .05, cb.y + 30); await m.p.mouse.down(); await m.p.mouse.move(cb.x + cb.width * .6, cb.y + 30, {steps:10}); await m.p.mouse.up(); await m.p.waitForTimeout(800);
  ok('mouse: e si torna indietro', await sl() < x1, await sl());
  await m.ctx.close();
  ok('nessun errore della pagina', !errs.length, errs.join(' | '));
  await b.close(); fine();
})();
