// L'app non si deve aprire dentro la pagina di un altro sito (clickjacking)
const {chromium} = require('playwright'); const {BASE, ok, fine} = require('./comune');
(async () => { const b = await chromium.launch(); const f = await b.newPage(); await f.goto('about:blank');
  await f.setContent('<iframe src="' + BASE + '?frame" width=400 height=600></iframe>'); await f.waitForTimeout(2000);
  const fr = f.frames()[1]; const len = fr ? await fr.evaluate(() => document.documentElement.innerHTML.length).catch(() => 0) : 0;
  ok('dentro un altro sito l\'app resta vuota', len < 200, len + ' caratteri');
  await b.close(); fine(); })();
