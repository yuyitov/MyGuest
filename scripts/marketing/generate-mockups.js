const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');
const os = require('os');

const MOCKUPS = ['coastal', 'minimalist', 'sunset', 'classic'];
const OUT_DIR = path.resolve('marketing/instagram/assets/mockups/phone');
const SCALE = 3; // 1044×2130px output
const SVG_W = 348;
const SVG_H = 710;

function toFileUrl(p) {
  return 'file:///' + p.replace(/\\/g, '/');
}

function makeHtml(screenshotUrl, frameUrl) {
  return `<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  html, body { width: ${SVG_W}px; height: ${SVG_H}px; background: transparent; overflow: hidden; }
  .wrap {
    position: relative;
    width: ${SVG_W}px; height: ${SVG_H}px;
    filter: drop-shadow(0 24px 48px rgba(0,0,0,0.45));
  }
  .screen { position: absolute; top: 45px; left: 13px; width: 322px; height: auto; z-index: 1; }
  .frame  { position: absolute; top: 0; left: 0; width: ${SVG_W}px; height: ${SVG_H}px; z-index: 2; }
</style>
</head>
<body>
<div class="wrap">
  <img class="screen" src="${screenshotUrl}">
  <img class="frame"  src="${frameUrl}">
</div>
</body>
</html>`;
}

async function run() {
  fs.mkdirSync(OUT_DIR, { recursive: true });

  // --allow-file-access-from-files lets file:// pages load other file:// resources
  const browser = await puppeteer.launch({
    args: ['--no-sandbox', '--allow-file-access-from-files']
  });
  const page = await browser.newPage();
  await page.setViewport({ width: SVG_W, height: SVG_H, deviceScaleFactor: SCALE });

  const frameUrl = toFileUrl(path.resolve('marketing/instagram/assets/phone-frame.svg'));
  const tmpDir = os.tmpdir();

  for (const name of MOCKUPS) {
    const screenshotUrl = toFileUrl(path.resolve(`marketing/instagram/assets/mockups/${name}-hi.png`));
    const outPath = path.join(OUT_DIR, `${name}-phone.png`);

    // Write to temp file so page.goto loads it as file:// (setContent blocks file:// image loading)
    const tmpFile = path.join(tmpDir, `mockup-${name}.html`);
    fs.writeFileSync(tmpFile, makeHtml(screenshotUrl, frameUrl), 'utf8');

    await page.goto(toFileUrl(tmpFile), { waitUntil: 'load' });
    await new Promise(r => setTimeout(r, 600));

    await page.screenshot({ path: outPath, omitBackground: true });
    fs.unlinkSync(tmpFile);

    console.log(`✓ ${name} → ${outPath}`);
  }

  await browser.close();
  console.log('\nDone! 4 mockups generated.');
}

run().catch(err => { console.error(err); process.exit(1); });
