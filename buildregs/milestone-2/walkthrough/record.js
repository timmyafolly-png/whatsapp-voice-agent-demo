const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const path = require('path');
const HOLD = [5500, 7200, 9500, 8000, 7800, 8000, 8500, 8500, 5200];
(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ viewport:{width:1280,height:720},
    recordVideo:{ dir: path.join(__dirname,'out6'), size:{width:1280,height:720} } });
  const p = await ctx.newPage();
  await p.goto('file://' + path.join(__dirname,'page.html'));
  await p.waitForTimeout(800);
  for (let i = 0; i < HOLD.length; i++) {
    await p.evaluate(i => window.show(i), i);
    await p.waitForTimeout(HOLD[i]);
  }
  await p.waitForTimeout(400);
  await ctx.close(); await b.close();
  console.log('recorded, total ~' + (HOLD.reduce((a,c)=>a+c,0)/1000).toFixed(0) + 's');
})().catch(e=>{console.error('FAIL', e.message); process.exit(1);});
