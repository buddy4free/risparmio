const {chromium}=require('playwright');const fs=require('fs');
(async()=>{const b=await chromium.launch();const p=await b.newPage();
await p.goto('http://localhost:8765/');await p.waitForTimeout(800);
const d=await p.evaluate(()=>({t:TERMS(),p:PRIVACY(),tv:TERMS_V,td:TERMS_DATE,pv:PRIVACY_V,pd:PRIVACY_DATE}));
const page=(title,ver,secs,other)=>`<!doctype html><html lang="it"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="dark only"><title>${title} · Buddy4Free Risparmio</title><link rel="icon" href="icons/icon-192.png"><link rel="stylesheet" href="fonts/fonts.css"><style>
:root{color-scheme:dark}body{margin:0;background:#000;color:#fff;font:16px/1.6 Figtree,system-ui,sans-serif}main{max-width:720px;margin:0 auto;padding:24px 16px 64px}
h1{font-family:Archivo,sans-serif;font-weight:900;font-size:1.9rem;line-height:1.15;margin:8px 0}h2{font-family:Archivo,sans-serif;font-size:1.15rem;margin:28px 0 8px}.muted{color:#A3A39E;font-size:.85rem}
a{color:#FFC90A}.tbox{border:3px solid #FFC90A;border-radius:14px;padding:12px 16px;margin:8px 0}ul{padding-left:20px}header{display:flex;align-items:center;gap:12px}header img{width:56px;height:56px;border-radius:12px}nav{margin-top:40px;border-top:1px solid #2A2A2A;padding-top:16px}
.y{color:#FFC90A}</style></head><body><main><header><img src="icons/icon-192.png" alt=""><b>Buddy4Free Risparmio</b></header><h1>${title}</h1><p class="muted">${ver}</p>
${secs.map(s=>'<h2>'+s[0]+'</h2>'+s[1].replace(/<ul class="tiplist">/g,'<ul>').replace(/<button class="textlink" data-nav='\{"screen":"privacy"\}'>([^<]*)<\/button>/g,'<a href="privacy.html">$1</a>')).join('\n')}
<nav><a href="./">Apri l'app</a> · ${other}</nav></main></body></html>`;
fs.writeFileSync('/home/user/risparmio/privacy.html',page('Informativa sulla privacy','Versione '+d.pv+' · aggiornata al '+d.pd,d.p,'<a href="terms.html">Termini e condizioni</a>'));
fs.writeFileSync('/home/user/risparmio/terms.html',page('Termini e condizioni','Versione '+d.tv+' · in vigore dal '+d.td,d.t,'<a href="privacy.html">Informativa sulla privacy</a>'));

console.log('ok');await b.close();})();
