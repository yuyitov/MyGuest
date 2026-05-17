const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..', '..', '..');
const SYS_ROOT = path.resolve(__dirname, '..');
const POSTS_FILE = path.join(SYS_ROOT, 'posts.json');
const TEMPLATES_DIR = path.join(SYS_ROOT, 'templates');
const EXPORTS_DIR = path.join(SYS_ROOT, 'exports');

const TEMPLATE_FILES = {
  'brand-intro': '01-brand-intro.html',
  'core-promise': '02-core-promise.html',
  'how-it-works': '03-how-it-works.html',
  'host-problem': '04-host-problem.html',
  'myguest-solution': '05-myguest-solution.html',
  'before-after': '06-before-after.html',
  'whats-included': '07-whats-included.html',
  'template-showcase': '08-template-showcase.html',
  'cta-launch-price': '09-cta-launch-price.html',
};

async function main() {
  const args = process.argv.slice(2);
  const includeDraft = args.includes('--draft');

  if (!fs.existsSync(POSTS_FILE)) {
    console.error('✗ posts.json not found at:', POSTS_FILE);
    process.exit(1);
  }

  const posts = JSON.parse(fs.readFileSync(POSTS_FILE, 'utf8'));

  if (!fs.existsSync(EXPORTS_DIR)) {
    fs.mkdirSync(EXPORTS_DIR, { recursive: true });
  }

  const toExport = posts.filter(p => {
    if (p.status === 'skip') return false;
    if (!includeDraft && p.status === 'draft') return false;
    return true;
  });

  if (toExport.length === 0) {
    console.log('No posts to export.');
    console.log('  • Use --draft to include draft posts');
    console.log('  • Set status to "ready" in posts.json to export without --draft');
    return;
  }

  console.log(`\nExporting ${toExport.length} post${toExport.length !== 1 ? 's' : ''}...`);
  if (includeDraft) console.log('  (including drafts)\n');
  else console.log('  (ready posts only — use --draft to include drafts)\n');

  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-web-security', '--allow-file-access-from-files']
  });

  let successCount = 0;
  let errorCount = 0;

  for (const post of toExport) {
    const templateFile = TEMPLATE_FILES[post.template];
    if (!templateFile) {
      console.warn(`  ⚠ Unknown template: "${post.template}" (${post.id}) — skipping`);
      errorCount++;
      continue;
    }

    const templatePath = path.join(TEMPLATES_DIR, templateFile);
    if (!fs.existsSync(templatePath)) {
      console.warn(`  ⚠ Template file not found: ${templateFile} — skipping ${post.id}`);
      errorCount++;
      continue;
    }

    try {
      let html = fs.readFileSync(templatePath, 'utf8');

      // Fix relative asset paths to absolute file:// paths
      const templatesBase = TEMPLATES_DIR.replace(/\\/g, '/');
      // Replace relative src/href for assets going up two levels (../../public/...)
      html = html.replace(/<head>/i, `<head>\n  <base href="file:///${templatesBase}/">`);

      // Inject post data before </head>
      const dataScript = `<script>window.POST_DATA = ${JSON.stringify(post)};<\/script>`;
      html = html.replace('</head>', dataScript + '\n</head>');

      // Write temp file
      const tempPath = path.join(EXPORTS_DIR, `_tmp_${post.id}.html`);
      fs.writeFileSync(tempPath, html, 'utf8');

      const page = await browser.newPage();
      await page.setViewport({ width: 1080, height: 1080, deviceScaleFactor: 2 });

      const fileUrl = `file:///${tempPath.replace(/\\/g, '/')}`;
      await page.goto(fileUrl, { waitUntil: 'networkidle0', timeout: 20000 });

      // Wait for fonts and layout
      await new Promise(r => setTimeout(r, 1000));

      // Build output filename: 01-post-001.png etc.
      const postIndex = posts.indexOf(post) + 1;
      const numStr = String(postIndex).padStart(2, '0');
      const outPath = path.join(EXPORTS_DIR, `${numStr}-${post.id}.png`);

      await page.screenshot({
        path: outPath,
        type: 'png',
        clip: { x: 0, y: 0, width: 1080, height: 1080 }
      });

      await page.close();

      // Clean up temp file
      try { fs.unlinkSync(tempPath); } catch {}

      console.log(`  ✓ ${post.id} → ${path.basename(outPath)}`);
      successCount++;

    } catch (err) {
      console.error(`  ✗ ${post.id} → Error: ${err.message}`);
      errorCount++;
      // Clean up temp file on error
      try {
        const tempPath = path.join(EXPORTS_DIR, `_tmp_${post.id}.html`);
        if (fs.existsSync(tempPath)) fs.unlinkSync(tempPath);
      } catch {}
    }
  }

  await browser.close();

  console.log(`\n${'─'.repeat(50)}`);
  console.log(`✅  Export complete`);
  console.log(`   Exported: ${successCount} post${successCount !== 1 ? 's' : ''}`);
  if (errorCount > 0) console.log(`   Errors:   ${errorCount}`);
  console.log(`   Output:   marketing/social-post-system/exports/`);
  console.log(`${'─'.repeat(50)}\n`);
}

main().catch(err => {
  console.error('\n✗ Export failed:', err.message);
  process.exit(1);
});
