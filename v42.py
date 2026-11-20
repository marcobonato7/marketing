import sys, os, json
root = sys.argv[1]
def rd(p): return open(os.path.join(root, p)).read()
def wr(p, s): open(os.path.join(root, p), 'w').write(s)
def sub(path, old, new, n=1):
    s = rd(path)
    assert s.count(old) == n, (path, old[:70], s.count(old))
    wr(path, s.replace(old, new))

# ================================================================ product page: the five-product set gets its own story
M = 'sections/main-product.liquid'
sub(M, '''  elsif t contains 'bundle' or t contains 'full routine' or t contains 'routine set'
    assign key = 'bundle'
''', '''  elsif settings.set_product != blank and product.id == settings.set_product.id
    assign key = 'set'
  elsif t contains 'face to neck set' or t contains 'gift set'
    assign key = 'set'
  elsif t contains 'bundle' or t contains 'full routine' or t contains 'routine set'
    assign key = 'bundle'
''')
sub(M, '''    when 'neck'
      assign n = 0''', '''    when 'set'
      assign n = 0
      assign color = '#F2C1D3'
      assign label = 'Best value'
      assign line = 'The neck cream and all four masks.'
      assign kind = 'Neck cream + four masks in one set'
      assign benefits = 'Everything Renn sells: the gua sha neck cream plus the Zero Pore Mud, Collagen, PDRN Pink Caffeine and Kojic Turmeric masks.|Neck care every day, and a mask for every kind of night.|Costs less than buying all five on their own.'
      assign how = 'Every day: the neck cream, glided upward with its gua sha head.|Once or twice a week: Zero Pore Mud Mask for 3 to 5 minutes, then rinse.|Most nights: pick the wrapping mask for how your skin feels, and peel it off in the morning.'
      assign note = 'Night masks go on last, set for 15 to 20 minutes, and peel off in the morning.'
    when 'neck'
      assign n = 0''')
sub(M, '''        {%- elsif key == 'bundle' -%}
          {% render 'renn-bundle-collage' %}''', '''        {%- elsif key == 'bundle' -%}
          {% render 'renn-bundle-collage' %}
        {%- elsif key == 'set' -%}
          {% render 'renn-set-collage' %}''')
sub(M, '''{%- if key == 'bundle' -%}
  <section class="blk four reveal">
    <div class="wrap">
      <span class="kicker mono rise">Four textures</span>
      <div class="four-grid rise">
        {%- assign tnames = 'Blue clay|Clear gel|Pink shimmer|Golden gel' | split: '|' -%}
        {%- for tn in tnames -%}
          {%- assign fi = forloop.index | plus: 1 -%}{%- assign f = 'm-frame-' | append: fi | append: '.jpg' -%}''', '''{%- if key == 'bundle' or key == 'set' -%}
  <section class="blk four reveal">
    <div class="wrap">
      <span class="kicker mono rise">{% if key == 'set' %}Five textures{% else %}Four textures{% endif %}</span>
      <div class="four-grid{% if key == 'set' %} five{% endif %} rise">
        {%- if key == 'set' -%}{%- assign tnames = 'Silky cream|Blue clay|Clear gel|Pink shimmer|Golden gel' | split: '|' -%}{%- assign f0 = 0 -%}{%- else -%}{%- assign tnames = 'Blue clay|Clear gel|Pink shimmer|Golden gel' | split: '|' -%}{%- assign f0 = 1 -%}{%- endif -%}
        {%- for tn in tnames -%}
          {%- assign fi = forloop.index | plus: f0 -%}{%- assign f = 'm-frame-' | append: fi | append: '.jpg' -%}''')
sub(M, '''{%- if key == 'bundle' -%}
  <section class="blk pings reveal" style="--c:{{ color }}">
    <div class="wrap">
      <span class="kicker mono rise">What's in the set</span>
      <div class="grid rise">
        {%- assign c = 0 -%}
        {%- for p in collections.all.products limit: 12 -%}
          {%- if p.id != product.id and c < 4 -%}''', '''{%- if key == 'bundle' or key == 'set' -%}
  <section class="blk pings reveal" style="--c:{{ color }}">
    <div class="wrap">
      <span class="kicker mono rise">What's in the set</span>
      <div class="grid rise">
        {%- assign c = 0 -%}{%- if key == 'set' -%}{%- assign cmax = 5 -%}{%- else -%}{%- assign cmax = 4 -%}{%- endif -%}
        {%- for p in collections.all.products limit: 20 -%}
          {%- assign pt = p.title | downcase -%}
          {%- assign skip = false -%}
          {%- if pt contains 'routine' or pt contains ' set' or pt contains 'bundle' -%}{%- assign skip = true -%}{%- endif -%}
          {%- if key == 'bundle' and pt contains 'neck' -%}{%- assign skip = true -%}{%- endif -%}
          {%- if p.id != product.id and c < cmax and skip == false -%}''')
sub(M, '''{%- elsif key != '' -%}
  <section class="blk pings reveal" style="--c:{{ color }}">''', '''{%- elsif key != '' -%}
  <section class="blk pings reveal" style="--c:{{ color }}">''')
sub(M, '''{%- if key != '' and key != 'bundle' and settings.bundle_product != blank -%}''',
       '''{%- if key != '' and key != 'bundle' and key != 'set' and settings.bundle_product != blank -%}''')
sub(M, '''{%- if shown > 0 and key != 'bundle' -%}''', '''{%- if shown > 0 and key != 'bundle' and key != 'set' -%}''')

# shop grid: bundles live in their own cards
sub('sections/renn-shop.liquid', '''        {%- if settings.bundle_product != blank and p.id == settings.bundle_product.id -%}{%- continue -%}{%- endif -%}''',
    '''        {%- if settings.bundle_product != blank and p.id == settings.bundle_product.id -%}{%- continue -%}{%- endif -%}
        {%- if settings.set_product != blank and p.id == settings.set_product.id -%}{%- continue -%}{%- endif -%}''')

# ================================================================ TikTok reels
wr('sections/renn-reels.liquid', '''{%- comment -%}
  TikTok-style reels: a row of vertical clips you swipe through. Each reel can show a TikTok video (paste its link),
  a video uploaded to Shopify, or a still that slowly zooms. A product tag sits on each one.
{%- endcomment -%}
{%- assign stills = 'neck,mud,collagen,pdrn,kojic' | split: ',' -%}
<section class="blk reels reveal" id="reels">
  <div class="wrap">
    <div class="reels-head">
      <div>
        <span class="kicker mono rise">{{ section.settings.kicker }}</span>
        <h2 class="big rise">{{ section.settings.heading }}</h2>
        <p class="lede rise">{{ section.settings.text }}</p>
      </div>
      <div class="reels-nav">
        {%- if settings.tiktok != blank -%}<a class="btn ghost" href="{{ settings.tiktok }}" target="_blank" rel="noopener">{% render 'renn-tt-icon' %} Follow on TikTok</a>{%- endif -%}
        <button type="button" class="arrow" data-reels="-1" aria-label="Previous">&larr;</button>
        <button type="button" class="arrow" data-reels="1" aria-label="Next">&rarr;</button>
      </div>
    </div>
  </div>
  <div class="reel-row" data-reel-row>
    {%- for block in section.blocks -%}
      {%- assign s = block.settings -%}
      {%- assign tid = '' -%}
      {%- if s.tiktok_url contains '/video/' -%}{%- assign tid = s.tiktok_url | split: '/video/' | last | split: '?' | first | split: '/' | first -%}{%- endif -%}
      {%- assign fi = 1 -%}{%- for k in stills -%}{%- if k == s.look -%}{%- assign fi = forloop.index -%}{%- endif -%}{%- endfor -%}
      {%- assign p = s.product -%}
      <article class="reel" {{ block.shopify_attributes }}>
        <div class="reel-media">
          {%- if s.video != blank -%}
            {{ s.video | video_tag: autoplay: true, loop: true, muted: true, controls: false, image_size: '720x' }}
          {%- elsif s.poster != blank -%}
            {{ s.poster | image_url: width: 720 | image_tag: loading: 'lazy', class: 'kb', alt: s.caption }}
          {%- else -%}
            <img class="kb" src="{{ 'm-frame-' | append: fi | append: '.jpg' | asset_url }}" alt="{{ s.caption | escape }}" loading="lazy" width="760" height="1013">
          {%- endif -%}
        </div>
        <span class="reel-tt" aria-hidden="true">{% render 'renn-tt-icon' %}</span>
        {%- if tid != blank -%}
          <button type="button" class="reel-play" data-tt-open="{{ tid }}" aria-label="Play this TikTok"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8 5.5v13l11-6.5z" fill="currentColor"/></svg></button>
        {%- elsif settings.tiktok != blank -%}
          <a class="reel-play" href="{{ settings.tiktok }}" target="_blank" rel="noopener" aria-label="Watch on TikTok"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8 5.5v13l11-6.5z" fill="currentColor"/></svg></a>
        {%- endif -%}
        <div class="reel-cap">
          <b>{{ s.handle | default: settings.wordmark | default: 'renn' }}{% if s.handle == blank %}.{% endif %}</b>
          <p>{{ s.caption }}</p>
        </div>
        {%- if p != blank -%}
          {%- assign v = p.selected_or_first_available_variant -%}
          <a class="reel-chip" href="{{ p.url }}">
            {%- if p.featured_media -%}{{ p.featured_media | image_url: width: 120 | image_tag: loading: 'lazy', alt: '' }}{%- else -%}<img src="{{ s.look | append: '.jpg' | asset_url }}" alt="" loading="lazy" width="120" height="120">{%- endif -%}
            <span><em>{{ p.title }}</em><b>{{ v.price | money }}</b></span>
          </a>
        {%- elsif s.product_name != blank -%}
          <a class="reel-chip" href="{{ routes.root_url }}#shop">
            <img src="{{ s.look | append: '.jpg' | asset_url }}" alt="" loading="lazy" width="120" height="120">
            <span><em>{{ s.product_name }}</em><b>{{ s.product_price }}</b></span>
          </a>
        {%- endif -%}
      </article>
    {%- endfor -%}
  </div>
  <dialog class="tt-modal" data-tt-modal aria-label="TikTok video">
    <button type="button" class="x" data-tt-close aria-label="Close">&times;</button>
    <iframe title="TikTok video" allow="encrypted-media; fullscreen; autoplay" loading="lazy"></iframe>
  </dialog>
</section>

{% schema %}
{
  "name": "TikTok reels",
  "settings": [
    { "type": "text", "id": "kicker", "label": "Small label", "default": "On TikTok" },
    { "type": "text", "id": "heading", "label": "Heading", "default": "Watch it glow." },
    { "type": "textarea", "id": "text", "label": "Text", "default": "Textures, pours and five-minute routines. Swipe through, then shop what you see." },
    { "type": "paragraph", "content": "Add your TikTok profile link in Theme settings > Renn for the Follow button." }
  ],
  "blocks": [
    {
      "type": "reel", "name": "Reel",
      "settings": [
        { "type": "url", "id": "tiktok_url", "label": "TikTok video link", "info": "Paste the link of a TikTok video. It plays right on the page." },
        { "type": "video", "id": "video", "label": "Or a video uploaded to Shopify", "info": "Vertical (9:16), muted and looping." },
        { "type": "image_picker", "id": "poster", "label": "Or a picture" },
        { "type": "select", "id": "look", "label": "Picture to use when nothing is added", "default": "neck",
          "options": [ { "value": "neck", "label": "Neck cream" }, { "value": "mud", "label": "Mud mask" }, { "value": "collagen", "label": "Collagen mask" }, { "value": "pdrn", "label": "PDRN mask" }, { "value": "kojic", "label": "Kojic mask" } ] },
        { "type": "text", "id": "handle", "label": "Account name", "info": "For example @renn.skin. Leave empty to show your wordmark." },
        { "type": "text", "id": "caption", "label": "Caption", "default": "The gua sha glide. Five minutes a day." },
        { "type": "product", "id": "product", "label": "Product tag" },
        { "type": "text", "id": "product_name", "label": "Product name shown before a product is picked" },
        { "type": "text", "id": "product_price", "label": "Price shown before a product is picked" }
      ]
    }
  ],
  "presets": [ { "name": "TikTok reels" } ]
}
{% endschema %}
''')
wr('snippets/renn-tt-icon.liquid', '''<svg class="tt-ico" viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M16.6 3c.3 2.3 1.6 3.7 3.9 3.9v2.6c-1.4.1-2.6-.3-3.9-1.1v5.1c0 6.5-7.1 8.5-10 3.8-1.9-3-.7-8.3 5.3-8.5v2.7c-.5.1-1 .2-1.4.4-1.4.5-2.2 1.4-2 3 .4 3 6 3.9 5.5-2V3h2.6Z"/></svg>''')

# ================================================================ review bar
wr('sections/renn-reviewbar.liquid', '''{%- comment -%}
  A slim strip that scrolls on its own. Add Review blocks with real customer quotes and they take over;
  until then it shows the shop's promises. No made-up reviews.
{%- endcomment -%}
{%- capture items -%}
  {%- assign has_reviews = false -%}
  {%- for block in section.blocks -%}
    {%- if block.type == 'review' and block.settings.quote != blank -%}
      {%- assign has_reviews = true -%}
      <span class="ri" {{ block.shopify_attributes }}><i class="stars" aria-label="{{ block.settings.stars }} out of 5 stars">{%- for i in (1..5) -%}<b{% if i > block.settings.stars %} class="off"{% endif %}>&#9733;</b>{%- endfor -%}</i>&ldquo;{{ block.settings.quote }}&rdquo;{%- if block.settings.name != blank -%}<em>{{ block.settings.name }}</em>{%- endif -%}</span>
    {%- endif -%}
  {%- endfor -%}
  {%- unless has_reviews -%}
    {%- assign facts = section.settings.facts | split: '|' -%}
    {%- for f in facts -%}<span class="ri"><i class="dot" aria-hidden="true"></i>{{ f | strip }}</span>{%- endfor -%}
  {%- endunless -%}
{%- endcapture -%}
<section class="rbar{% if section.settings.dark %} dark{% endif %}" aria-label="{{ section.settings.label | escape }}">
  <div class="rbar-track" style="--rb-speed:{{ section.settings.speed }}s">
    <div class="rbar-set">{{ items }}</div>
    <div class="rbar-set" aria-hidden="true">{{ items }}</div>
  </div>
</section>

{% schema %}
{
  "name": "Review bar",
  "settings": [
    { "type": "text", "id": "label", "label": "Label for screen readers", "default": "What people say about Renn" },
    { "type": "textarea", "id": "facts", "label": "Shown until you add reviews (separate with |)", "default": "Genuine medicube, in the original box|Five products. One calm routine.|Less effort. More glow.|Real answers from real people|Korean skincare, picked with care" },
    { "type": "range", "id": "speed", "label": "Seconds per loop", "min": 20, "max": 90, "step": 5, "default": 45 },
    { "type": "checkbox", "id": "dark", "label": "Dark strip", "default": false }
  ],
  "blocks": [
    { "type": "review", "name": "Review", "settings": [
      { "type": "text", "id": "quote", "label": "Quote", "info": "Only real reviews from real customers." },
      { "type": "text", "id": "name", "label": "Name", "info": "For example: Jess, verified buyer" },
      { "type": "range", "id": "stars", "label": "Stars", "min": 1, "max": 5, "step": 1, "default": 5 }
    ] }
  ],
  "presets": [ { "name": "Review bar" } ]
}
{% endschema %}
''')

# ================================================================ home page order + deal prices that match the real products
idx = json.loads(rd('templates/index.json'))
idx['sections']['reviewbar'] = {"type": "renn-reviewbar", "settings": {}, "blocks": {}, "block_order": []}
looks = [('neck', 'The gua sha glide. Five minutes a day.', 'PDRN Collagen Gua Sha Neck Wrinkle Cream', '$35.00'),
         ('mud', 'Blue clay, three minutes, clearer-looking pores.', 'Zero Pore Blackhead Mud Mask', '$25.00'),
         ('collagen', 'A glassy gel that works while you sleep.', 'Collagen Night Wrapping Mask', '$25.00'),
         ('pdrn', 'Pink shimmer for rested-looking mornings.', 'PDRN Pink Caffeine Night Wrapping Mask', '$25.00'),
         ('kojic', 'Golden gel for dull mornings.', 'Kojic Acid Turmeric Night Wrapping Mask', '$25.00')]
idx['sections']['reels'] = {"type": "renn-reels", "settings": {},
  "blocks": {f"reel_{k}": {"type": "reel", "settings": {"look": k, "caption": c, "product_name": n, "product_price": pr}} for k, c, n, pr in looks},
  "block_order": [f"reel_{k}" for k, *_ in looks]}
o = idx['order']
i = o.index('deals_xmas') + 1
o = o[:i] + ['reviewbar'] + o[i:]
j = o.index('shop') + 1
o = o[:j] + ['reels'] + o[j:]
idx['order'] = o
b = idx['sections']['deals_bf']['blocks']
b['bf_bundle']['settings'].update({"badge": "Save $25", "price": "$75.00", "was": "$100.00"})
b = idx['sections']['deals_xmas']['blocks']
b['x_set']['settings'].update({"badge": "Save $46", "price": "$89.00", "was": "$135.00"})
b['x_bundle']['settings'].update({"badge": "Save $25", "price": "$75.00", "was": "$100.00"})
wr('templates/index.json', json.dumps(idx, indent=2, ensure_ascii=False) + '\n')
S = rd('config/settings_schema.json')
assert S.count('"default": "The Gift Edit: holiday sets from $65"') == 1
wr('config/settings_schema.json', S.replace('"default": "The Gift Edit: holiday sets from $65"', '"default": "The Gift Edit: holiday sets from $75"'))

# ================================================================ script: reel arrows + TikTok player
J = 'assets/renn.js'
sub(J, '''  /* ---------- Black Friday / Christmas''', '''  /* ---------- TikTok reels: arrows and the in-page player ---------- */
  document.querySelectorAll("[data-reels]").forEach(function (b) {
    b.addEventListener("click", function () {
      var row = document.querySelector("[data-reel-row]"); if (!row) return;
      var card = row.querySelector(".reel"); var w = card ? card.getBoundingClientRect().width + 16 : 300;
      row.scrollBy({ left: +b.dataset.reels * w * 2, behavior: reduce ? "auto" : "smooth" });
    });
  });
  var ttm = document.querySelector("[data-tt-modal]");
  if (ttm) {
    var ttf = ttm.querySelector("iframe");
    var ttClose = function () { ttf.src = "about:blank"; if (ttm.open) ttm.close(); };
    document.addEventListener("click", function (e) {
      var o = e.target.closest && e.target.closest("[data-tt-open]");
      if (o) { ttf.src = "https://www.tiktok.com/embed/v2/" + o.dataset.ttOpen; if (ttm.showModal) ttm.showModal(); else ttm.setAttribute("open", ""); return; }
      if (e.target === ttm || (e.target.closest && e.target.closest("[data-tt-close]"))) ttClose();
    });
    ttm.addEventListener("close", function () { ttf.src = "about:blank"; });
  }

  /* ---------- Black Friday / Christmas''')

# ================================================================ styles
C = 'assets/renn.css'
s = rd(C)
s += '''
/* ---------- five textures (set page) ---------- */
.four-grid.five{grid-template-columns:repeat(5,1fr)}
@media (max-width:820px){.four-grid.five{grid-template-columns:repeat(2,1fr)}}

/* ---------- review bar ---------- */
.rbar{overflow:hidden;background:var(--milk);border-block:1px solid rgba(42,36,33,.08);padding:16px 0;--rb-fade:var(--milk)}
.rbar.dark{background:var(--ink);color:var(--milk);border:0;--rb-fade:var(--ink)}
.rbar{-webkit-mask:linear-gradient(90deg,transparent,#000 6%,#000 94%,transparent);mask:linear-gradient(90deg,transparent,#000 6%,#000 94%,transparent)}
.rbar-track{display:flex;width:max-content;animation:rb var(--rb-speed,45s) linear infinite}
.rbar:hover .rbar-track{animation-play-state:paused}
.rbar-set{display:flex;align-items:center;gap:48px;padding-right:48px}
.ri{display:inline-flex;align-items:center;gap:12px;white-space:nowrap;font-size:15px}
.ri .dot{width:6px;height:6px;border-radius:50%;background:linear-gradient(90deg,var(--pearl),var(--clay))}
.ri .stars{font-style:normal;display:inline-flex;gap:1px;color:#C9973A;font-size:13px;letter-spacing:0}
.ri .stars .off{color:rgba(42,36,33,.18)}
.ri em{font:400 11.5px/1 var(--mono);letter-spacing:.1em;text-transform:uppercase;opacity:.6;font-style:normal}
@keyframes rb{to{transform:translateX(-50%)}}
@media (prefers-reduced-motion:reduce){.rbar-track{animation-duration:calc(var(--rb-speed,45s) * 3)}}

/* ---------- TikTok reels ---------- */
.reels{overflow:hidden}
.reels-head{display:flex;align-items:flex-end;justify-content:space-between;gap:24px;margin-bottom:32px}
.reels-head .lede{margin-bottom:0;max-width:46ch}
.reels-nav{display:flex;align-items:center;gap:10px;flex:none}
.reels-nav .arrow{width:46px;height:46px;border-radius:50%;border:1px solid rgba(42,36,33,.18);background:transparent;font-size:18px;cursor:pointer;transition:background .3s,border-color .3s}
.reels-nav .arrow:hover{background:var(--milk);border-color:transparent}
.btn.ghost{background:transparent;color:var(--ink);box-shadow:inset 0 0 0 1px rgba(42,36,33,.25)}
.btn.ghost:hover{background:var(--milk)}
.tt-ico{width:16px;height:16px;flex:none}
@media (max-width:820px){.reels-head{flex-direction:column;align-items:flex-start}.reels-nav .arrow{display:none}}
.reel-row{display:flex;gap:16px;overflow-x:auto;scroll-snap-type:x mandatory;padding:4px clamp(20px,5vw,64px) 24px;scroll-padding:0 clamp(20px,5vw,64px);scrollbar-width:none;-webkit-overflow-scrolling:touch}
.reel-row::-webkit-scrollbar{display:none}
.reel{position:relative;flex:none;width:clamp(220px,21vw,300px);aspect-ratio:9/16;border-radius:22px;overflow:hidden;background:#EDE3DA;scroll-snap-align:start;color:#fff;box-shadow:0 30px 60px -36px rgba(42,36,33,.45);isolation:isolate}
@media (max-width:620px){.reel{width:70vw}}
.reel-media,.reel-media video,.reel-media img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.reel-media::after{content:"";position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,.18) 0%,rgba(0,0,0,0) 22%,rgba(0,0,0,0) 52%,rgba(0,0,0,.55) 100%)}
.reel .kb{animation:kb 14s ease-in-out infinite alternate;transform-origin:50% 40%}
.reel:nth-child(2n) .kb{animation-delay:-5s}.reel:nth-child(3n) .kb{animation-delay:-9s}
@keyframes kb{from{transform:scale(1)}to{transform:scale(1.14)}}
@media (prefers-reduced-motion:reduce){.reel .kb{animation:none}}
.reel-tt{position:absolute;left:14px;top:14px;z-index:2;width:30px;height:30px;border-radius:50%;display:grid;place-items:center;background:rgba(0,0,0,.35);backdrop-filter:blur(6px);-webkit-backdrop-filter:blur(6px)}
.reel-play{position:absolute;left:50%;top:44%;z-index:2;transform:translate(-50%,-50%);width:58px;height:58px;border-radius:50%;border:0;display:grid;place-items:center;background:rgba(255,255,255,.22);backdrop-filter:blur(10px);-webkit-backdrop-filter:blur(10px);color:#fff;cursor:pointer;transition:transform .3s var(--ease),background .3s}
.reel-play svg{width:24px;height:24px;margin-left:3px}
.reel-play:hover{transform:translate(-50%,-50%) scale(1.06);background:rgba(255,255,255,.32)}
.reel-cap{position:absolute;left:14px;right:14px;bottom:86px;z-index:2;text-shadow:0 1px 8px rgba(0,0,0,.35)}
.reel-cap b{font:500 14px/1.2 var(--body)}
.reel-cap p{margin:4px 0 0;font-size:14px;line-height:1.35}
.reel-chip{position:absolute;left:10px;right:10px;bottom:10px;z-index:2;display:flex;align-items:center;gap:10px;padding:8px;border-radius:14px;background:rgba(251,248,244,.94);color:var(--ink);text-decoration:none;backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px)}
.reel-chip img{width:46px;height:46px;border-radius:10px;object-fit:contain;background:#fff;flex:none}
.reel-chip span{display:grid;gap:2px;min-width:0}
.reel-chip em{font-style:normal;font-size:12.5px;line-height:1.25;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.reel-chip b{font-weight:500;font-size:13px}
.tt-modal{border:0;padding:0;border-radius:20px;width:min(360px,92vw);height:min(720px,86vh);background:#000;overflow:hidden}
.tt-modal::backdrop{background:rgba(22,18,15,.7);backdrop-filter:blur(4px)}
.tt-modal iframe{width:100%;height:100%;border:0}
.tt-modal .x{position:absolute;right:10px;top:10px;z-index:2;width:34px;height:34px;border-radius:50%;border:0;background:rgba(255,255,255,.9);font-size:20px;cursor:pointer}
'''
wr(C, s)
print('patched')
