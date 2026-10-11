// Render QA/guide passes for every camera of a plan.
//
//   node engine/render.mjs plans/osnova-prizemlja [CAM_ID ...] [--size 1600x900]
//
// Output per camera -> output/<plan>/<CAM>/blockout/{guide,lines,edge_ids,surface_ids}.png
//                      + passes.json (legend, camera matrices) + visible.json
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { chromium } from 'playwright-core';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const args = process.argv.slice(2);
const planDir = path.resolve(ROOT, args[0]);
const sizeArg = args.includes('--size') ? args[args.indexOf('--size') + 1] : '1600x900';
const only = args.slice(1).filter(a => !a.startsWith('--') && a !== sizeArg);
const plan = JSON.parse(fs.readFileSync(path.join(planDir, 'plan.json')));
const cams = JSON.parse(fs.readFileSync(path.join(planDir, 'cameras.json'))).cameras
  .filter(c => !only.length || only.includes(c.id));
const planName = path.basename(planDir);

const MIME = { '.js': 'text/javascript', '.mjs': 'text/javascript', '.html': 'text/html', '.json': 'application/json' };
const server = http.createServer((req, res) => {
  const p = path.join(ROOT, decodeURIComponent(req.url.split('?')[0]));
  if (!p.startsWith(ROOT) || !fs.existsSync(p)) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { 'Content-Type': MIME[path.extname(p)] || 'application/octet-stream' });
  fs.createReadStream(p).pipe(res);
}).listen(0);
const port = server.address().port;

const exe = ['/opt/pw-browsers/chromium-1194/chrome-linux/chrome'].find(fs.existsSync);
const browser = await chromium.launch({ executablePath: exe, args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
const page = await browser.newPage();
page.on('console', m => m.type() === 'error' && console.error('[page]', m.text()));
await page.goto(`http://localhost:${port}/engine/page.html`);
await page.waitForFunction(() => window.ready === true);

for (const cam of cams) {
  const variants = cam.variants || [{ suffix: '', opts: {} }];
  for (const v of variants) {
    const [W, H] = (cam.size || sizeArg).split('x').map(Number);
    const id = cam.id + (v.suffix || '');
    const res = await page.evaluate(({ plan, cam, W, H, opts }) => window.render(plan, cam, W, H, opts),
      { plan, cam, W, H, opts: v.opts || {} });
    const dir = path.join(ROOT, 'output', planName, id, 'blockout');
    fs.mkdirSync(dir, { recursive: true });
    for (const k of ['guide', 'lines', 'edge_ids', 'surface_ids', 'normals', 'depth'])
      fs.writeFileSync(path.join(dir, `${k}.png`), Buffer.from(res[k].split(',')[1], 'base64'));
    fs.writeFileSync(path.join(dir, 'passes.json'), JSON.stringify({ camera: res.camera, variant: v, legend: res.legend }, null, 1));
    console.log('rendered', id, `${W}x${H}`);
  }
}
await browser.close();
server.close();
