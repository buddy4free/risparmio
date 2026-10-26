const {chromium}=require('playwright');const D='/tmp/claude-0/-home-user/5d688e9e-4cef-51e8-b416-070f144b3467/scratchpad/clips/shots/';
(async()=>{const b=await chromium.launch();const ctx=await b.newContext({viewport:{width:411,height:731},deviceScaleFactor:2.627,isMobile:true,hasTouch:true});const p=await ctx.newPage();
await p.goto('http://localhost:8767/?'+Date.now());await p.waitForTimeout(800);await p.evaluate(()=>localStorage.clear());await p.reload();await p.waitForTimeout(800);
await p.check('#w-terms');await p.click('#demo');await p.waitForTimeout(400);
await p.evaluate(()=>{S.since='2026-01-01';S.supportSeen='2026-10-25';S.demo=false;S.recAsked=true;S.lastBackup='2026-10-20';save();});
const clean=async()=>{await p.evaluate(()=>{document.querySelectorAll('.toast,#suppop').forEach(x=>x.remove());document.getElementById('fab').style.display='none';window.scrollTo(0,0)});await p.waitForTimeout(250);};
const shot=async(n,fn,after)=>{await p.evaluate(fn);await p.waitForTimeout(450);await clean();if(after)await p.evaluate(after);await p.waitForTimeout(250);await p.screenshot({path:D+n+'.png'});};
await shot('rec',()=>nav({screen:'rec'}));
await shot('add-list',()=>{F=null;nav({screen:'add',type:'out'})},()=>{document.querySelector('[data-cl="ristoranti"]').click()});
await shot('cats-ord',()=>{nav({screen:'cats',t:'out'})},()=>{document.getElementById('cx-ord').click()});
await b.close()})()
