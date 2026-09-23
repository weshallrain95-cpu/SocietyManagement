// Pack the demo web export (dist/) into ONE self-contained HTML page:
// the JS bundle inlined, every asset embedded as a data: URI, and a small boot shim
// so the app starts at its home route whatever address the page is served from.
//
//   EXPO_PUBLIC_DEMO=1 npx expo export --platform web --clear
//   node scripts/single-file-demo.mjs dist ../demo/only-broker-demo.html
import fs from 'node:fs';
import path from 'node:path';

const [distDir = 'dist', out = 'only-broker-demo.html'] = process.argv.slice(2);
const html = fs.readFileSync(path.join(distDir, 'index.html'), 'utf8');
const entry = /<script src="([^"]+)"/.exec(html)[1];
let js = fs.readFileSync(path.join(distDir, entry.replace(/^\//, '')), 'utf8');

const MIME = { '.ttf': 'font/ttf', '.otf': 'font/otf', '.png': 'image/png', '.jpg': 'image/jpeg', '.webp': 'image/webp', '.svg': 'image/svg+xml' };
let embedded = 0;
js = js.replace(/"(\/assets\/[^"]+)"/g, (whole, url) => {
  const file = path.join(distDir, url.replace(/^\//, ''));
  if (!fs.existsSync(file)) return whole;
  embedded++;
  const mime = MIME[path.extname(file)] ?? 'application/octet-stream';
  return `"data:${mime};base64,${fs.readFileSync(file).toString('base64')}"`;
});

const reset = /<style id="expo-reset">([\s\S]*?)<\/style>/.exec(html)[1];
// Boot shim: Expo Router reads the page path. Wherever this page is hosted, start at "/".
const shim = `(function(){try{if(location.pathname!=='/'){history.replaceState(null,'','/'+location.hash);}}catch(e){window.__OB_PATH_LOCKED__=true;}})();`;
const safeJs = js.replace(/<\/script/gi, '<\\/script');

const page = `<title>Only Broker Demo</title>
<style>${reset}
html, body { margin: 0; background: #F5F6F3; }
@media (prefers-color-scheme: dark) { html, body { background: #0C1413; } }
</style>
<div id="root"></div>
<script>${shim}</script>
<script>${safeJs}</script>
`;
fs.mkdirSync(path.dirname(path.resolve(out)), { recursive: true });
fs.writeFileSync(out, page);
console.log(`wrote ${out}: ${(page.length / 1024 / 1024).toFixed(2)} MB, ${embedded} assets embedded`);
