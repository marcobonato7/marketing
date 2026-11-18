import sys, os
root = sys.argv[1]
def rd(p): return open(os.path.join(root, p)).read()
def wr(p, s): open(os.path.join(root, p), 'w').write(s)
def sub(path, old, new, n=1):
    s = rd(path)
    assert s.count(old) == n, (path, old[:70], s.count(old))
    wr(path, s.replace(old, new))

J = 'assets/renn.js'
# ---- the opening plays the neck cream commercial at its real speed, with every frame (phones too) ----
sub(J, '''var auto = (!reduce && !tiny && cx && scrollY < film.offsetTop + 30) ? 1 : 0, autoT0 = 0, AUTO_MS = 5200, scroll0 = scrollY;''',
       '''var auto = (!reduce && !tiny && cx && scrollY < film.offsetTop + 30) ? 1 : 0, autoT0 = 0, AUTO_MS = 11000, scroll0 = scrollY;''')
sub(J, '''  function isIntro(k) { return k <= STOPS[0]; }''',
       '''  function isIntro(k) { return k <= STOPS[0]; }
  function stepAt(f) { return f <= STOPS[0] ? 1 : STEP; }          /* the opening always uses every frame */''')
sub(J, '''    for (k = 0; k <= STOPS[0]; k += STEP) { seen[k] = 1; order.push(k); }   /* the opening pour first */''',
       '''    for (k = 0; k <= STOPS[0]; k++) { seen[k] = 1; order.push(k); }       /* the opening pour first, every frame */''')
sub(J, '''  var STEP = mobileSet ? 2 : 1, NEED = Math.ceil(COUNT / STEP);   /* phones load every second frame and blend between them */''',
       '''  var STEP = mobileSet ? 2 : 1;                                   /* phones load every second frame after the opening and blend between them */
  var NEED = STOPS[0] + 1 + Math.ceil((COUNT - STOPS[0] - 1) / STEP);''')
sub(J, '''    var i = Math.floor(f / STEP) * STEP, a = (f - i) / STEP, A = near(i);''',
       '''    var st = stepAt(f), i = Math.floor(f / st) * st, a = (f - i) / st, A = near(i);''')
sub(J, '''    if (A === i && a > 0.02 && ok[i + STEP]) { cx.globalAlpha = a; cx.drawImage(imgs[i + STEP], r[0], r[1], r[2], r[3]); cx.globalAlpha = 1; }''',
       '''    if (A === i && a > 0.02 && ok[i + st]) { cx.globalAlpha = a; cx.drawImage(imgs[i + st], r[0], r[1], r[2], r[3]); cx.globalAlpha = 1; }''')
# real time: steady through the pour, settling gently onto the tube
sub(J, '''    var p = Math.min(1, (now - autoT0) / AUTO_MS), e = -(Math.cos(Math.PI * p) - 1) / 2;''',
       '''    var p = Math.min(1, (now - autoT0) / AUTO_MS), e = p < 0.85 ? p * 0.9 / 0.85 : 0.9 + 0.1 * (1 - Math.pow(1 - (p - 0.85) / 0.15, 2));''')
# sharper canvas on high-density phones
sub(J, '''    var dpr = Math.min(window.devicePixelRatio || 1, 2);''', '''    var dpr = Math.min(window.devicePixelRatio || 1, 3);''')
sub(J, '''    cx.globalAlpha = 1; cx.fillStyle = bg; cx.fillRect(0, 0, cv.width, cv.height);''',
       '''    cx.imageSmoothingEnabled = true; if ("imageSmoothingQuality" in cx) cx.imageSmoothingQuality = "high";
    cx.globalAlpha = 1; cx.fillStyle = bg; cx.fillRect(0, 0, cv.width, cv.height);''')
sub(J, '''"film 3.8 | set "''', '''"film 3.9 | set "''')

# ---- copy: the shop now has a neck cream as well as four masks ----
sub('sections/renn-shop.liquid', '"default": "Pick the mask that fits tonight."', '"default": "Pick what your skin needs."')
sub('sections/renn-about.liquid', 'We chose four medicube masks that cover what most of us need: clear pores, moisture, a reste',
                                  'We chose a medicube neck cream and four masks that cover what most of us need: a smoother-looking neck, clear pores, moisture, a reste')
sub('sections/renn-about.liquid', '"default": "One flat price: $25 per mask."', '"default": "Simple prices: $25 per mask, $35 for the neck cream."')
sub('sections/renn-about.liquid', '''<img src="{{ 'frame-4.jpg' | asset_url }}" alt="Shimmering pink PDRN gel" loading="lazy" width="1600" height="905">''',
                                  '''<img src="{{ 'frame-1.jpg' | asset_url }}" alt="The pink medicube neck cream with its gua sha head" loading="lazy" width="1600" height="905">''')

# ---- shop grid: show the five products with their own photos before they are created in Shopify ----
sub('sections/renn-shop.liquid', '''      {%- else -%}
        {%- if request.design_mode -%}<p class="muted">Add products in Shopify, then pick them here in the theme editor.</p>{%- endif -%}
      {%- endfor -%}''', '''      {%- else -%}
        {%- assign fb_names = 'PDRN Collagen Gua Sha Neck Wrinkle Cream|Zero Pore Blackhead Mud Mask|Collagen Night Wrapping Mask|PDRN Pink Caffeine Night Wrapping Mask|Kojic Acid Turmeric Night Wrapping Mask' | split: '|' -%}
        {%- assign fb_lines = 'PDRN, collagen and 5% Volufiline, with a built-in gua sha head that massages as you apply.|A 30% clay wash-off mask with AHA, BHA and PHA. Clears pores in three minutes.|An overnight wrapping mask that seals in moisture. Wake up smooth.|PDRN and caffeine for a rested, calm-looking face by morning.|Kojic acid and turmeric for a brighter, more even tone.' | split: '|' -%}
        {%- assign fb_imgs = 'neck|mud|collagen|pdrn|kojic' | split: '|' -%}
        {%- assign fb_prices = '$35.00|$25.00|$25.00|$25.00|$25.00' | split: '|' -%}
        {%- for n in fb_names -%}
          <article class="scard rise" style="transition-delay:{{ forloop.index0 | times: 90 }}ms">
            <a href="#pour-{{ forloop.index }}" class="tlink" aria-label="{{ n | escape }}">{% render 'renn-tile', product: blank, fallback: fb_imgs[forloop.index0], fallback_title: n %}</a>
            <h3><a href="#pour-{{ forloop.index }}">{{ n }}</a></h3>
            <p>{{ fb_lines[forloop.index0] }}</p>
            <div class="buy">{% render 'renn-buy', product: blank, label: 'Shop Now', fallback_price: fb_prices[forloop.index0] %}</div>
          </article>
        {%- endfor -%}
        {%- if request.design_mode -%}<p class="muted">These cards show until your products are created in Shopify.</p>{%- endif -%}
      {%- endfor -%}''')

# ---- css: five products sit in one row on wide screens; ingredient grid without empty grey cells ----
C = 'assets/renn.css'
sub(C, '''.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:20px}''',
       '''.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:20px}
@media (min-width:1200px){.grid{grid-template-columns:repeat(5,1fr)}}''')
sub(C, '''.ings{display:grid;grid-template-columns:repeat(5,1fr);gap:1px;background:rgba(42,36,33,.1);border-radius:var(--r);overflow:hidden}''',
       '''.ings{display:grid;grid-template-columns:repeat(4,1fr);gap:0;border-top:1px solid rgba(42,36,33,.12)}
@media (min-width:1300px){.ings{grid-template-columns:repeat(4,1fr)}}''')
sub(C, '''.ing{background:var(--cream);padding:26px 22px 28px;transition:background .4s}''',
       '''.ing{background:transparent;padding:26px 22px 28px;border-bottom:1px solid rgba(42,36,33,.12);border-radius:14px;transition:background .4s}''')
print('patched')
