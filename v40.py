import sys, os, json
root = sys.argv[1]
def rd(p): return open(os.path.join(root, p)).read()
def wr(p, s): open(os.path.join(root, p), 'w').write(s)
def sub(path, old, new, n=1):
    s = rd(path)
    assert s.count(old) == n, (path, old[:70], s.count(old))
    wr(path, s.replace(old, new))

# =========================================================== settings
sch = json.loads(rd('config/settings_schema.json'))
assert not any(g.get('name') == 'Promotions' for g in sch)
sch.append({
  "name": "Promotions",
  "settings": [
    {"type": "paragraph", "content": "Black Friday and Christmas deals switch on and off by themselves on the dates below. Create the matching discount codes and bundle products in Shopify (Discounts, Products): the theme only shows them."},
    {"type": "select", "id": "promo_mode", "label": "Which promotion to show", "default": "auto",
     "options": [{"value": "auto", "label": "Automatic, by date"}, {"value": "bf", "label": "Always Black Friday"}, {"value": "xmas", "label": "Always Christmas"}, {"value": "off", "label": "None"}]},
    {"type": "header", "content": "Black Friday"},
    {"type": "text", "id": "bf_start", "label": "Starts (YYYY-MM-DD)", "default": "2026-11-19"},
    {"type": "text", "id": "bf_end", "label": "Ends before (YYYY-MM-DD)", "default": "2026-12-01", "info": "The sale runs until the start of this day."},
    {"type": "text", "id": "bf_code", "label": "Discount code", "default": "RENNBF20"},
    {"type": "text", "id": "bf_bar", "label": "Top bar message", "default": "Black Friday: 20% off everything"},
    {"type": "header", "content": "Christmas"},
    {"type": "text", "id": "xmas_start", "label": "Starts (YYYY-MM-DD)", "default": "2026-12-01"},
    {"type": "text", "id": "xmas_end", "label": "Ends before (YYYY-MM-DD)", "default": "2026-12-26"},
    {"type": "text", "id": "xmas_code", "label": "Discount code", "default": "RENNGIFT"},
    {"type": "text", "id": "xmas_bar", "label": "Top bar message", "default": "The Gift Edit: holiday sets from $65"},
    {"type": "header", "content": "Face to Neck Set"},
    {"type": "product", "id": "set_product", "label": "Five-product set", "info": "Create a product with the neck cream and all four masks (for example $89, compare-at price $135), then pick it here. It is used in the deals."}
  ]
})
wr('config/settings_schema.json', json.dumps(sch, indent=2, ensure_ascii=False) + '\n')

# =========================================================== which promotion is on (server side; the script re-checks with the visitor's clock)
wr('snippets/renn-promo-season.liquid', '''{%- comment -%} Prints bf, xmas or nothing: the promotion running today. {%- endcomment -%}
{%- liquid
  assign today = 'now' | date: '%Y%m%d' | plus: 0
  assign bf_a = settings.bf_start | remove: '-' | plus: 0
  assign bf_b = settings.bf_end | remove: '-' | plus: 0
  assign x_a = settings.xmas_start | remove: '-' | plus: 0
  assign x_b = settings.xmas_end | remove: '-' | plus: 0
  assign s = ''
  case settings.promo_mode
    when 'bf'
      assign s = 'bf'
    when 'xmas'
      assign s = 'xmas'
    when 'off'
      assign s = ''
    else
      if today >= bf_a and today < bf_b
        assign s = 'bf'
      elsif today >= x_a and today < x_b
        assign s = 'xmas'
      endif
  endcase
  echo s
-%}
''')

# =========================================================== top bar
wr('snippets/renn-promo-bar.liquid', '''{%- comment -%} Slim announcement bar for Black Friday or Christmas, with the code and a countdown. {%- endcomment -%}
{%- capture season -%}{% render 'renn-promo-season' %}{%- endcapture -%}
{%- assign season = season | strip -%}
{%- if settings.promo_mode != 'off' -%}
  {%- assign bf_end = settings.bf_end | remove: '-' -%}
  {%- assign x_end = settings.xmas_end | remove: '-' -%}
  <div class="pbar bf" data-season="bf" data-bar{% unless season == 'bf' %} hidden{% endunless %}>
    <p><b>{{ settings.bf_bar }}</b>{%- if settings.bf_code != blank -%}<span class="sep" aria-hidden="true"></span>Code <button type="button" class="code" data-copy="{{ settings.bf_code | escape }}">{{ settings.bf_code }}</button>{%- endif -%}<span class="sep hide-s" aria-hidden="true"></span><span class="ends hide-s" data-ends="{{ bf_end }}"></span></p>
    <button type="button" class="x" data-bar-close aria-label="Hide this message">&times;</button>
  </div>
  <div class="pbar xmas" data-season="xmas" data-bar{% unless season == 'xmas' %} hidden{% endunless %}>
    <p><b>{{ settings.xmas_bar }}</b>{%- if settings.xmas_code != blank -%}<span class="sep" aria-hidden="true"></span>Code <button type="button" class="code" data-copy="{{ settings.xmas_code | escape }}">{{ settings.xmas_code }}</button>{%- endif -%}<span class="sep hide-s" aria-hidden="true"></span><span class="ends hide-s" data-ends="{{ x_end }}"></span></p>
    <button type="button" class="x" data-bar-close aria-label="Hide this message">&times;</button>
  </div>
{%- endif -%}
''')

# =========================================================== five-product photo grid
wr('snippets/renn-set-collage.liquid', '''{%- comment -%} The neck cream and the four masks: one large photo and a 2 x 2 grid. {%- endcomment -%}
<div class="tile collage5">
  <img class="big" src="{{ 'neck.jpg' | asset_url }}" alt="" loading="lazy" width="1440" height="1440">
  {%- assign names = 'mud,collagen,pdrn,kojic' | split: ',' -%}
  {%- for k in names -%}<img src="{{ k | append: '.jpg' | asset_url }}" alt="" loading="lazy" width="1440" height="1440">{%- endfor -%}
</div>
''')

# =========================================================== product page strip
wr('snippets/renn-promo-strip.liquid', '''{%- comment -%} One line under the price on product pages while a promotion runs. {%- endcomment -%}
{%- capture season -%}{% render 'renn-promo-season' %}{%- endcapture -%}
{%- assign season = season | strip -%}
{%- if settings.promo_mode != 'off' -%}
  <p class="pstrip bf" data-season="bf"{% unless season == 'bf' %} hidden{% endunless %}><span class="tag">Black Friday</span>{{ settings.bf_bar }}{%- if settings.bf_code != blank -%}: code <button type="button" class="code" data-copy="{{ settings.bf_code | escape }}">{{ settings.bf_code }}</button>{%- endif -%}</p>
  <p class="pstrip xmas" data-season="xmas"{% unless season == 'xmas' %} hidden{% endunless %}><span class="tag">Christmas</span>{{ settings.xmas_bar }}{%- if settings.xmas_code != blank -%}: code <button type="button" class="code" data-copy="{{ settings.xmas_code | escape }}">{{ settings.xmas_code }}</button>{%- endif -%}</p>
{%- endif -%}
''')

# =========================================================== deals section
wr('sections/renn-promo.liquid', '''{%- comment -%}
  Seasonal deals: one copy of this section is set to Black Friday, another to Christmas.
  Each shows itself only while its promotion runs (see Theme settings > Promotions).
{%- endcomment -%}
{%- capture season -%}{% render 'renn-promo-season' %}{%- endcapture -%}
{%- assign season = season | strip -%}
{%- assign me = section.settings.season -%}
{%- if me == 'bf' -%}{%- assign code = settings.bf_code -%}{%- assign ends = settings.bf_end | remove: '-' -%}{%- else -%}{%- assign code = settings.xmas_code -%}{%- assign ends = settings.xmas_end | remove: '-' -%}{%- endif -%}
{%- if settings.promo_mode != 'off' -%}
<section class="blk promo {{ me }}" id="deals-{{ me }}" data-season="{{ me }}"{% unless season == me %} hidden{% endunless %}>
  <div class="wrap">
    <div class="promo-head">
      <div>
        <span class="kicker mono">{{ section.settings.kicker }}</span>
        <h2 class="big">{{ section.settings.heading }}</h2>
        <p class="lede">{{ section.settings.text }}</p>
      </div>
      <div class="promo-meta">
        <span class="mono ends" data-ends="{{ ends }}"></span>
        {%- if code != blank -%}<button type="button" class="code big-code" data-copy="{{ code | escape }}"><small class="mono">Code</small>{{ code }}<em class="mono">Tap to copy</em></button>{%- endif -%}
      </div>
    </div>
    <div class="deals">
      {%- for block in section.blocks -%}
        {%- assign p = block.settings.product -%}
        {%- if block.settings.image == 'set' and p == blank -%}{%- assign p = settings.set_product -%}{%- endif -%}
        {%- if block.settings.image == 'bundle' and p == blank -%}{%- assign p = settings.bundle_product -%}{%- endif -%}
        <article class="deal{% if forloop.first %} lead{% endif %}" {{ block.shopify_attributes }}>
          <div class="deal-img">
            {%- if p != blank and p.featured_media and block.settings.use_product_photo -%}
              {{ p.featured_media | image_url: width: 1200 | image_tag: loading: 'lazy', widths: '600, 900, 1200', sizes: '(max-width: 820px) 90vw, 33vw', alt: p.title }}
            {%- elsif block.settings.image == 'set' -%}{% render 'renn-set-collage' %}
            {%- elsif block.settings.image == 'bundle' -%}{% render 'renn-bundle-collage' %}
            {%- elsif block.settings.image == 'code' -%}<div class="tile codeart"><span>{{ block.settings.badge | default: '20% off' }}</span></div>
            {%- else -%}<div class="tile"><img src="{{ block.settings.image | append: '.jpg' | asset_url }}" alt="" loading="lazy" width="1440" height="1440"></div>
            {%- endif -%}
            {%- if block.settings.badge != blank and block.settings.image != 'code' -%}<span class="badge">{{ block.settings.badge }}</span>{%- endif -%}
          </div>
          <div class="deal-txt">
            <h3>{%- if p != blank -%}<a href="{{ p.url }}">{{ block.settings.title | default: p.title }}</a>{%- else -%}{{ block.settings.title }}{%- endif -%}</h3>
            <p>{{ block.settings.line }}</p>
            <div class="buy">
              {%- if block.settings.image == 'code' -%}
                <span class="price">{{ block.settings.price }}</span>
                {%- if code != blank -%}<button type="button" class="btn" data-copy="{{ code | escape }}">Copy {{ code }}</button>{%- endif -%}
              {%- elsif p != blank -%}
                {%- assign v = p.selected_or_first_available_variant -%}
                <span class="price">{{ v.price | money }}{% if v.compare_at_price > v.price %} <s>{{ v.compare_at_price | money }}</s>{% endif %}</span>
                {%- if p.available -%}
                  <form method="post" action="{{ routes.cart_add_url }}" class="add">
                    <input type="hidden" name="id" value="{{ v.id }}"><input type="hidden" name="quantity" value="1">
                    <button class="btn" type="submit">Add to Cart</button>
                  </form>
                {%- else -%}<button class="btn" type="button" disabled>Sold out</button>{%- endif -%}
              {%- else -%}
                <span class="price">{{ block.settings.price }}{% if block.settings.was != blank %} <s>{{ block.settings.was }}</s>{% endif %}</span>
                <a class="btn" href="{{ routes.all_products_collection_url }}">Shop Now</a>
              {%- endif -%}
            </div>
          </div>
        </article>
      {%- endfor -%}
    </div>
    {%- if section.settings.note != blank -%}<p class="note">{{ section.settings.note }}</p>{%- endif -%}
  </div>
</section>
{%- endif -%}

{% schema %}
{
  "name": "Seasonal deals",
  "settings": [
    { "type": "select", "id": "season", "label": "Promotion", "default": "bf", "options": [ { "value": "bf", "label": "Black Friday" }, { "value": "xmas", "label": "Christmas" } ] },
    { "type": "text", "id": "kicker", "label": "Small label", "default": "Black Friday week" },
    { "type": "text", "id": "heading", "label": "Heading", "default": "Black Friday" },
    { "type": "textarea", "id": "text", "label": "Text", "default": "Our best prices of the year, through Cyber Monday." },
    { "type": "text", "id": "note", "label": "Small print" }
  ],
  "blocks": [
    {
      "type": "deal", "name": "Deal",
      "settings": [
        { "type": "product", "id": "product", "label": "Product", "info": "Optional. Its price and Add to Cart are used. For the five-product set and the four-mask bundle, the products picked in Theme settings are used." },
        { "type": "select", "id": "image", "label": "Picture", "default": "set",
          "options": [ { "value": "set", "label": "Face to Neck Set (all five)" }, { "value": "bundle", "label": "The Full Routine (four masks)" }, { "value": "code", "label": "Discount code card" },
                       { "value": "neck", "label": "Neck cream" }, { "value": "mud", "label": "Mud mask" }, { "value": "collagen", "label": "Collagen mask" }, { "value": "pdrn", "label": "PDRN mask" }, { "value": "kojic", "label": "Kojic mask" } ] },
        { "type": "checkbox", "id": "use_product_photo", "label": "Use the product's own photo instead", "default": false },
        { "type": "text", "id": "badge", "label": "Badge", "default": "Save $46" },
        { "type": "text", "id": "title", "label": "Title", "default": "The Face to Neck Set" },
        { "type": "text", "id": "line", "label": "One line", "default": "The neck cream and all four masks." },
        { "type": "text", "id": "price", "label": "Price shown before a product is picked", "default": "$89.00" },
        { "type": "text", "id": "was", "label": "Was-price shown before a product is picked", "default": "$135.00" }
      ]
    }
  ],
  "presets": [ { "name": "Seasonal deals" } ]
}
{% endschema %}
''')

# =========================================================== home page: deals right after the film
idx = json.loads(rd('templates/index.json'))
idx['sections']['deals_bf'] = {
  "type": "renn-promo",
  "settings": {"season": "bf", "kicker": "Black Friday week", "heading": "Black Friday", "text": "Our best prices of the year, through Cyber Monday. Bundles are already marked down, and the code takes 20% off everything else.", "note": "Bundle prices are final, so the code doesn't stack on them. While stocks last."},
  "blocks": {
    "bf_set": {"type": "deal", "settings": {"image": "set", "badge": "Save $46", "title": "The Face to Neck Set", "line": "The neck cream and all four masks, for the whole routine.", "price": "$89.00", "was": "$135.00"}},
    "bf_bundle": {"type": "deal", "settings": {"image": "bundle", "badge": "Save $40", "title": "The Full Routine", "line": "All four masks. One clean routine.", "price": "$60.00", "was": "$100.00"}},
    "bf_code": {"type": "deal", "settings": {"image": "code", "badge": "20% off", "title": "Everything else", "line": "20% off every single product at checkout.", "price": "20% off", "was": ""}}
  },
  "block_order": ["bf_set", "bf_bundle", "bf_code"]
}
idx['sections']['deals_xmas'] = {
  "type": "renn-promo",
  "settings": {"season": "xmas", "kicker": "Christmas", "heading": "The Gift Edit", "text": "Calm skincare sets, ready to give. Order early for delivery before Christmas.", "note": "Gift sets are already marked down, so the code doesn't stack on them."},
  "blocks": {
    "x_set": {"type": "deal", "settings": {"image": "set", "badge": "Save $36", "title": "The Face to Neck Gift Set", "line": "The neck cream and all four masks, for someone you love.", "price": "$99.00", "was": "$135.00"}},
    "x_bundle": {"type": "deal", "settings": {"image": "bundle", "badge": "Save $35", "title": "The Full Routine", "line": "All four masks for a month of calm nights.", "price": "$65.00", "was": "$100.00"}},
    "x_code": {"type": "deal", "settings": {"image": "code", "badge": "15% off", "title": "Stocking fillers", "line": "15% off any single mask or the neck cream.", "price": "15% off", "was": ""}}
  },
  "block_order": ["x_set", "x_bundle", "x_code"]
}
order = idx['order']
i = order.index('film') + 1
idx['order'] = order[:i] + ['deals_bf', 'deals_xmas'] + order[i:]
wr('templates/index.json', json.dumps(idx, indent=2, ensure_ascii=False) + '\n')

# =========================================================== layout: bar above the header; promotion dates for the script
sub('layout/theme.liquid', '''  <a class="skip" href="#main">Skip to content</a>
  {% section 'renn-header' %}''', '''  <a class="skip" href="#main">Skip to content</a>
  {% render 'renn-promo-bar' %}
  {% section 'renn-header' %}''')
sub('layout/theme.liquid', '''    window.RENN_ROUTES = {''', '''    window.RENN_PROMO = { mode: {{ settings.promo_mode | json }}, bf: [{{ settings.bf_start | remove: '-' | plus: 0 }}, {{ settings.bf_end | remove: '-' | plus: 0 }}], xmas: [{{ settings.xmas_start | remove: '-' | plus: 0 }}, {{ settings.xmas_end | remove: '-' | plus: 0 }}] };
    window.RENN_ROUTES = {''')

sub('layout/theme.liquid', '''<html lang="{{ request.locale.iso_code }}">''', '''{%- capture season -%}{% render 'renn-promo-season' %}{%- endcapture -%}
<html lang="{{ request.locale.iso_code }}"{% if season != blank %} class="has-bar"{% endif %}>''')

# product page: strip under the price
sub('sections/main-product.liquid', '''      <p class="pprice"><span data-price>{{ v.price | money }}</span>{% if v.compare_at_price > v.price %} <s>{{ v.compare_at_price | money }}</s>{% endif %}</p>
''', '''      <p class="pprice"><span data-price>{{ v.price | money }}</span>{% if v.compare_at_price > v.price %} <s>{{ v.compare_at_price | money }}</s>{% endif %}</p>
      {% render 'renn-promo-strip' %}
''')

# sharper Shopify product photos: bigger sources for high-density screens
sub('snippets/renn-tile.liquid', "image_url: width: 720 | image_tag: loading: 'lazy', widths: '360, 540, 720',", "image_url: width: 1080 | image_tag: loading: 'lazy', widths: '360, 540, 720, 1080',")
sub('sections/main-product.liquid', "{{ product.featured_media | image_url: width: 1200 | image_tag: loading: 'eager', fetchpriority: 'high', widths: '600, 900, 1200',", "{{ product.featured_media | image_url: width: 1600 | image_tag: loading: 'eager', fetchpriority: 'high', widths: '600, 900, 1200, 1600',")
sub('sections/main-product.liquid', '''data-src="{{ m | image_url: width: 1200 }}"''', '''data-src="{{ m | image_url: width: 1600 }}"''')
# the theme's own product photos are now 1440 px
for f in ['snippets/renn-bundle-collage.liquid']:
    sub(f, 'width="720" height="720"', 'width="1440" height="1440"')

# =========================================================== script
J = 'assets/renn.js'
sub(J, '''  document.querySelectorAll(".reveal").forEach(function (el) { io ? io.observe(el) : el.classList.add("in"); });
''', '''  document.querySelectorAll(".reveal").forEach(function (el) { io ? io.observe(el) : el.classList.add("in"); });

  /* ---------- Black Friday / Christmas: show the running promotion, count down, copy codes ---------- */
  (function () {
    var P = window.RENN_PROMO; if (!P) return;
    var d = new Date(), today = d.getFullYear() * 10000 + (d.getMonth() + 1) * 100 + d.getDate();
    var s = P.mode === "off" ? "" : P.mode === "bf" ? "bf" : P.mode === "xmas" ? "xmas" :
      (today >= P.bf[0] && today < P.bf[1]) ? "bf" : (today >= P.xmas[0] && today < P.xmas[1]) ? "xmas" : "";
    var closed = false; try { closed = sessionStorage.getItem("renn-bar-" + s) === "1"; } catch (e) {}
    document.querySelectorAll("[data-season]").forEach(function (el) {
      el.hidden = el.dataset.season !== s || (closed && el.hasAttribute("data-bar"));
    });
    var bar = s && !closed && document.querySelector('[data-bar][data-season="' + s + '"]');
    document.documentElement.classList.toggle("has-bar", !!bar);
    document.querySelectorAll("[data-bar-close]").forEach(function (b) {
      b.addEventListener("click", function () {
        try { sessionStorage.setItem("renn-bar-" + s, "1"); } catch (e) {}
        b.parentNode.hidden = true; document.documentElement.classList.remove("has-bar");
      });
    });
    function ends() {
      var now = Date.now();
      document.querySelectorAll("[data-ends]").forEach(function (el) {
        var v = String(el.dataset.ends), end = new Date(+v.slice(0, 4), +v.slice(4, 6) - 1, +v.slice(6, 8)).getTime(), m = Math.max(0, Math.floor((end - now) / 60000));
        var dd = Math.floor(m / 1440), hh = Math.floor(m % 1440 / 60), mm = m % 60;
        el.textContent = m <= 0 ? "Ended" : "Ends in " + (dd ? dd + "d " + hh + "h" : hh + "h " + (mm < 10 ? "0" : "") + mm + "m");
      });
    }
    ends(); setInterval(ends, 30000);
    document.addEventListener("click", function (e) {
      var b = e.target.closest && e.target.closest("[data-copy]"); if (!b) return;
      var code = b.dataset.copy, done = function () { showToast("Code <b>" + code + "</b> copied. Paste it at checkout."); };
      if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(code).then(done, done); else done();
    });
  })();
''')
# showToast is defined later in the file; hoisted function declaration, so the click handler can use it.

# =========================================================== styles
C = 'assets/renn.css'
s = rd(C)
s += '''
/* ---------- promotions ---------- */
:root{--barh:0px;--bf:#16120F;--bf-2:#2A2421;--xm:#1E3329;--xm-2:#28443A}
html.has-bar{--barh:40px}
html.has-bar body{padding-top:var(--barh)}
html.has-bar .hdr{top:var(--barh)}
.pbar{position:fixed;inset:0 0 auto 0;z-index:60;height:var(--barh,40px);min-height:40px;display:flex;align-items:center;justify-content:center;padding:0 48px;font-size:13.5px;line-height:1.2;color:var(--milk)}
.pbar[hidden]{display:none}
.pbar.bf{background:var(--bf)}
.pbar.xmas{background:var(--xm)}
.pbar p{margin:0;display:flex;align-items:center;gap:10px;white-space:nowrap;overflow:hidden}
.pbar b{font-weight:500;letter-spacing:.01em}
.pbar .sep{width:3px;height:3px;border-radius:50%;background:currentColor;opacity:.45}
.pbar .ends{font:400 12px/1 var(--mono);letter-spacing:.08em;text-transform:uppercase;opacity:.75}
.pbar .x{position:absolute;right:10px;top:50%;transform:translateY(-50%);width:30px;height:30px;border:0;border-radius:50%;background:transparent;color:inherit;font-size:20px;line-height:1;cursor:pointer;opacity:.7}
.pbar .x:hover{opacity:1;background:rgba(255,255,255,.08)}
.code{font:500 12px/1 var(--mono);letter-spacing:.1em;padding:6px 9px;border-radius:7px;border:1px dashed currentColor;background:transparent;color:inherit;cursor:pointer;transition:background .25s}
.code:hover{background:rgba(255,255,255,.1)}
@media (max-width:640px){.pbar{font-size:12.5px;padding:0 40px 0 14px;justify-content:flex-start}.pbar .hide-s{display:none}}

.pstrip{display:flex;align-items:center;flex-wrap:wrap;gap:8px;margin:-6px 0 22px;padding:10px 12px;border-radius:12px;font-size:14px;color:var(--ink)}
.pstrip[hidden]{display:none}
.pstrip.bf{background:#EDE6DE}
.pstrip.xmas{background:#E3EAE4}
.pstrip .tag{font:500 10.5px/1 var(--mono);letter-spacing:.1em;text-transform:uppercase;padding:5px 8px;border-radius:999px;color:var(--milk)}
.pstrip.bf .tag{background:var(--bf)}
.pstrip.xmas .tag{background:var(--xm)}
.pstrip .code{border-color:rgba(42,36,33,.35)}
.pstrip .code:hover{background:rgba(42,36,33,.06)}

section.promo[hidden]{display:none}
section.promo{color:var(--milk)}
section.promo.bf{background:radial-gradient(120% 90% at 85% 0%,#2C2420 0%,var(--bf) 60%)}
section.promo.xmas{background:radial-gradient(120% 90% at 85% 0%,#2A4A3C 0%,var(--xm) 62%)}
section.promo .kicker{color:rgba(251,248,244,.7)}
section.promo .lede{color:rgba(251,248,244,.78)}
section.promo h2.big{color:var(--milk)}
.promo-head{display:flex;align-items:flex-end;justify-content:space-between;gap:32px;margin-bottom:clamp(32px,4vw,52px)}
.promo-head .lede{max-width:52ch;margin-bottom:0}
.promo-meta{display:flex;flex-direction:column;align-items:flex-end;gap:12px;flex:none}
.promo-meta .ends{color:rgba(251,248,244,.75)}
.big-code{display:grid;gap:4px;text-align:left;padding:14px 18px;border-radius:16px;border:1px dashed rgba(251,248,244,.5);font:500 22px/1 var(--mono);letter-spacing:.12em}
.big-code small,.big-code em{font-size:10px;font-style:normal;letter-spacing:.14em;opacity:.65}
@media (max-width:820px){.promo-head{flex-direction:column;align-items:flex-start}.promo-meta{align-items:flex-start}}
.deals{display:grid;grid-template-columns:1.25fr 1fr 1fr;gap:18px}
@media (max-width:1000px){.deals{grid-template-columns:1fr 1fr}.deal.lead{grid-column:1/-1}}
@media (max-width:620px){.deals{grid-template-columns:1fr}}
.deal{background:var(--milk);color:var(--ink);border-radius:var(--r);padding:12px 12px 20px;display:flex;flex-direction:column;transition:transform .5s var(--ease),box-shadow .5s var(--ease)}
.deal:hover{transform:translateY(-4px);box-shadow:0 30px 60px -30px rgba(0,0,0,.5)}
.deal-img{position:relative}
.deal-img .tile,.deal-img img{border-radius:14px}
.deal-img > img{width:100%;aspect-ratio:1;object-fit:cover;display:block}
.deal .badge{position:absolute;left:12px;top:12px;font:500 11px/1 var(--mono);letter-spacing:.1em;text-transform:uppercase;padding:7px 10px;border-radius:999px;background:var(--ink);color:var(--milk)}
.promo.xmas .deal .badge{background:var(--xm)}
.deal-txt{padding:16px 8px 0;display:flex;flex-direction:column;flex:1}
.deal h3{font:400 clamp(22px,2vw,28px)/1.1 var(--display);margin:0 0 6px}
.deal h3 a{text-decoration:none}
.deal p{font-size:15px;color:var(--ink-2);margin:0 0 18px}
.deal .buy{margin-top:auto;display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap}
.deal .price{font-size:20px}
.deal .price s{font-size:15px;color:var(--ink-2);margin-left:4px}
.promo .note{color:rgba(251,248,244,.6);margin-top:24px;font-size:13.5px}
.codeart{display:grid;place-items:center;background:repeating-linear-gradient(135deg,#F3ECE4 0 14px,#EFE6DC 14px 28px)}
.promo.xmas .codeart{background:repeating-linear-gradient(135deg,#EAF0EA 0 14px,#E2EAE3 14px 28px)}
.codeart span{font:300 clamp(54px,6vw,86px)/.9 var(--display);letter-spacing:-.02em;text-align:center;max-width:5ch}
.collage5{display:grid;grid-template-columns:1.2fr 1fr 1fr;grid-template-rows:1fr 1fr;gap:2px;background:#fff;aspect-ratio:1}
.collage5 img{width:100%;height:100%;object-fit:contain;background:#fff;min-height:0}
.collage5 .big{grid-row:1/3}
'''
wr(C, s)
print('patched')
