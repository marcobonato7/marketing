// Minimal Shopify-like preview renderer for the Renn theme (liquidjs). Usage: node render.js THEME OUT [products|empty]
const { Liquid, Tag, Hash } = require('liquidjs');
const fs = require('fs'), path = require('path');
const T = process.argv[2], OUT = process.argv[3], MODE = process.argv[4] || 'empty';
fs.mkdirSync(OUT + '/products', { recursive: true });
fs.rmSync(OUT + '/assets', { recursive: true, force: true });
fs.symlinkSync(path.resolve(T + '/assets'), OUT + '/assets');

const engine = new Liquid({ root: [T + '/snippets', T + '/sections', T + '/layout'], extname: '.liquid', strictFilters: false, strictVariables: false, jsTruthy: false, dynamicPartials: true, globals: {} });
const G = engine.options.globals;
const money = c => '$' + (Number(c) / 100).toFixed(2);
engine.registerFilter('asset_url', v => 'assets/' + v);
engine.registerFilter('money', money);
engine.registerFilter('money_without_trailing_zeros', c => { const s = money(c); return s.endsWith('.00') ? s.slice(0, -3) : s; });
engine.registerFilter('image_url', (v, ...a) => (v && v.src) || String(v || ''));
engine.registerFilter('image_tag', function (v, ...a) { return `<img src="${v}">`; });
engine.registerFilter('preload_tag', v => `<link rel="preload" href="${v}">`);
engine.registerFilter('stylesheet_tag', v => `<link rel="stylesheet" href="${v}">`);
engine.registerFilter('json', v => JSON.stringify(v === undefined ? null : v));
engine.registerFilter('t', v => v);
const schemaOf = f => { const m = fs.readFileSync(f, 'utf8').match(/{%-?\s*schema\s*-?%}([\s\S]*?){%-?\s*endschema\s*-?%}/); return m ? JSON.parse(m[1]) : {}; };
engine.registerTag('schema', { parse(tk, rem) { this.tpl = []; const s = this.liquid.parser.parseStream(rem); s.on('tag:endschema', () => s.stop()).on('template', t => {}).on('end', () => { throw new Error('schema not closed'); }); s.start(); }, * render() { return ''; } });
engine.registerTag('form', {
  parse(tk, rem) { this.args = tk.args; this.tpl = []; const s = this.liquid.parser.parseStream(rem); s.on('tag:endform', () => s.stop()).on('template', t => this.tpl.push(t)).on('end', () => { throw new Error('form'); }); s.start(); },
  * render(ctx, emitter) { emitter.write('<form method="post" action="/cart/add" class="pform add" id="renn-pform">'); yield this.liquid.renderer.renderTemplates(this.tpl, ctx, emitter); emitter.write('</form>'); }
});
function defaults(settings) { const o = {}; (settings || []).forEach(s => { if (s.id) o[s.id] = s.default !== undefined ? s.default : (s.type === 'checkbox' ? false : ''); }); return o; }
const gs = JSON.parse(fs.readFileSync(T + '/config/settings_schema.json'));
const settings = {}; gs.forEach(g => Object.assign(settings, defaults(g.settings)));
const mk = (id, k, title, desc, price, cmp) => ({ id, handle: k, title, vendor: 'medicube', url: '/products/' + k + '.html', price, available: true, has_only_default_variant: true, description: '<p>' + desc + '</p>',
  featured_media: { src: 'assets/' + (k === 'bundle' || k === 'set' ? 'mud' : k) + '.jpg', media_type: 'image' }, media: [{ src: 'assets/' + (k === 'bundle' || k === 'set' ? 'mud' : k) + '.jpg', media_type: 'image' }],
  selected_or_first_available_variant: { id: id * 100, price, compare_at_price: cmp || null }, variants: [{ id: id * 100, price, available: true, title: 'Default' }], options: ['Title'] });
const P = [mk(6, 'neck', 'PDRN Collagen Gua Sha Neck Wrinkle Cream', 'Neck cream with 5% Volufiline.', 3500), mk(1, 'mud', 'Zero Pore Blackhead Mud Mask', '30% clay wash-off mask.', 2500), mk(2, 'collagen', 'Collagen Night Wrapping Mask', 'Overnight wrapping mask.', 2500), mk(3, 'pdrn', 'PDRN Pink Caffeine Night Wrapping Mask', 'PDRN and caffeine.', 2500), mk(4, 'kojic', 'Kojic Acid Turmeric Night Wrapping Mask', 'Kojic acid and turmeric.', 2500)];
const B = mk(5, 'bundle', 'The Full Routine', 'All four masks in one set.', 7500, 10000); B.featured_media = null;
if (MODE === 'products') { settings.bundle_product = B; }
const routes = { root_url: '/', cart_url: '/cart', cart_add_url: '/cart/add', all_products_collection_url: '/collections/all' };
const base = { settings, routes, shop: { name: 'Renn', email: 'hello@renn.shop', url: 'https://renn.shop' }, cart: { item_count: 0 }, request: { locale: { iso_code: 'en' }, design_mode: false }, collections: { all: { products: MODE === 'products' ? P : [] } }, canonical_url: '/', content_for_header: '', localization: {} };
Object.assign(G, base);
engine.registerTag('section', { parse(tk) { this.name = tk.args.replace(/['"]/g, '').trim(); }, * render(ctx, em) { const f = T + '/sections/' + this.name + '.liquid'; const sc = schemaOf(f); const html = yield engine.renderFile(this.name, { ...base, ...ctx.getAll(), section: { id: this.name, settings: defaults(sc.settings), blocks: [] } }); em.write(html); } });

async function renderSections(order, sections, extra) {
  let out = '';
  for (const id of order) {
    const s = sections[id]; const f = T + '/sections/' + s.type + '.liquid'; const sc = schemaOf(f);
    const st = { ...defaults(sc.settings), ...(s.settings || {}) };
    const blocks = (s.block_order || Object.keys(s.blocks || {})).map(bid => { const b = s.blocks[bid]; const bs = (sc.blocks || []).find(x => x.type === b.type) || {}; const set = { ...defaults(bs.settings), ...(b.settings || {}) };
      if (MODE === 'products' && set.product === '' && bs.settings && bs.settings.find(x => x.id === 'product')) { const k = set.fallback_image; set.product = P.find(p => p.handle === k) || ''; }
      return { id: bid, type: b.type, settings: set, shopify_attributes: '' }; });
    out += await engine.renderFile(s.type, { ...base, ...extra, section: { id, settings: st, blocks } });
  }
  return out;
}
async function page(tplName, content, extra, file) {
  const html = await engine.renderFile('theme', { ...base, ...extra, template: { name: tplName }, content_for_layout: content, page_title: 'Renn' });
  fs.writeFileSync(file, html.replace(/(src|href)="assets\//g, (m, a) => `${a}="${file.includes('/products/') ? '../' : ''}assets/`));
}
(async () => {
  const idx = JSON.parse(fs.readFileSync(T + '/templates/index.json'));
  await page('index', await renderSections(idx.order, idx.sections, {}), {}, OUT + '/index.html');
  const pj = JSON.parse(fs.readFileSync(T + '/templates/product.json'));
  for (const p of [...P, B]) await page('product', await renderSections(pj.order, pj.sections, { product: p }), { product: p }, OUT + '/products/' + p.handle + '.html');
  console.log('rendered', MODE);
})().catch(e => { console.error('RENDER ERROR', e.message); process.exit(1); });
