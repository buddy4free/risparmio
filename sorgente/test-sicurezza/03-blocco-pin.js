// Blocco con PIN e impronta: tempo "Richiedi dopo", tentativi ripetuti, tastiera, tasto indietro, backup con un altro PIN
const {OUT, ok, fine, apri, demo, fs} = require('./comune');
(async () => { const {b, ctx, p, errs, hits} = await apri();
  const cdp = await ctx.newCDPSession(p); await cdp.send('WebAuthn.enable'); await cdp.send('WebAuthn.addVirtualAuthenticator', {options:{protocol:'ctap2', transport:'internal', hasResidentKey:true, hasUserVerification:true, isUserVerified:true, automaticPresenceSimulation:true}});
  await demo(p);
  const locked = () => p.evaluate(() => !!document.getElementById('lock'));
  const reopen = async (agoMin) => { await p.addInitScript(m => { if (m != null && !sessionStorage['r' + m]) { sessionStorage['r' + m] = 1; localStorage.setItem('b4f-lock-seen', String(Date.now() - m * 60000)); } }, agoMin); await p.reload(); await p.waitForTimeout(900); };
  const type = async pin => { for (const k of pin) await p.click('[data-k="' + k + '"]'); await p.waitForTimeout(450); };
  await p.evaluate(() => nav({screen:'settings'})); await p.waitForTimeout(400);
  await p.click('#lk-on'); await p.fill('#pn1', '2580'); await p.fill('#pn2', '2580'); await p.click('#pn-ok'); await p.waitForTimeout(700);
  ok('PIN salvato solo come impronta (hash)', await p.evaluate(() => S.lock.on && S.lock.hash && !JSON.stringify(S).includes('"2580"')));
  // tempo "Richiedi dopo"
  await p.evaluate(() => { S.lock.after = 1800; save(); });
  await reopen(5); ok('30 min: riaperta dopo 5 min, nessun PIN', !(await locked()));
  await reopen(31); ok('30 min: riaperta dopo 31 min, PIN richiesto', await locked());
  await type('2580'); ok('PIN giusto sblocca', !(await locked()));
  await p.evaluate(() => { S.lock.after = 0; save(); });
  await reopen(0); ok('"Subito": PIN richiesto a ogni apertura', await locked());
  // sotto il blocco
  ok('contenuto nascosto sotto il blocco', await p.evaluate(() => getComputedStyle(view).visibility === 'hidden'));
  for (let i = 0; i < 4; i++) await p.keyboard.press('Tab');
  ok('la tastiera non raggiunge l\'app sotto il blocco', await p.evaluate(() => { const a = document.activeElement; return !a || a === document.body || !!a.closest('#lock'); }));
  await p.evaluate(() => history.back()); await p.waitForTimeout(400); ok('il tasto indietro non toglie il blocco', await locked());
  await p.evaluate(() => { try { nav({screen:'tx'}); } catch (e) {} }); await p.waitForTimeout(200); ok('navigare non toglie il blocco', await locked() && await p.evaluate(() => getComputedStyle(view).visibility === 'hidden'));
  // tentativi ripetuti
  for (let i = 0; i < 5; i++) await type('1111');
  ok('dopo 5 PIN sbagliati: attesa', await p.evaluate(() => /attendi|riprova/.test(document.querySelector('.lkmsg').textContent)));
  await reopen(0); await type('2580'); ok('riaprire l\'app non azzera l\'attesa', await locked());
  await p.evaluate(() => { const f = JSON.parse(localStorage.getItem('b4f-lock-fails')); f.u = Date.now() + 1e12; localStorage.setItem('b4f-lock-fails', JSON.stringify(f)); }); await reopen(0);
  ok('attesa manomessa limitata a 15 minuti', await p.evaluate(() => LOCK.until - Date.now() <= 9e5 + 1000));
  await p.evaluate(() => localStorage.removeItem('b4f-lock-fails')); await reopen(0); await type('2580'); ok('sblocco dopo l\'attesa', !(await locked()));
  // backup con un altro PIN
  const evil = await p.evaluate(() => { const d = JSON.parse(JSON.stringify(S)); d.lock = {on:true, len:4, salt:'AAAAAAAAAAAAAAAAAAAAAA==', hash:'xxxx', after:0}; return JSON.stringify(d); }); fs.writeFileSync(OUT + 'evil-lock.json', evil);
  await p.evaluate(() => nav({screen:'settings'})); await p.waitForTimeout(300); await p.setInputFiles('#s-rs', OUT + 'evil-lock.json'); await p.waitForTimeout(400); await p.click('#rb-yes'); await p.waitForTimeout(400);
  ok('un backup non sostituisce il PIN del telefono', await p.evaluate(() => S.lock.hash !== 'xxxx' && S.lock.on));
  // impronta
  await p.evaluate(() => nav({screen:'settings'})); await p.waitForTimeout(400); await p.check('#lk-bio'); await p.waitForTimeout(1200);
  ok('impronta attivata', await p.evaluate(() => !!S.lock.bio));
  await reopen(0); await p.waitForTimeout(1500); ok('impronta sblocca', !(await locked()));
  ok('nessun codice eseguito o iniettato', !hits.length, hits.join(' | '));
  ok('nessun errore della pagina', !errs.length, errs.slice(0, 3).join(' | '));
  await b.close(); fine(); })();
