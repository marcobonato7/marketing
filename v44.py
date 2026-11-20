import sys, os, json
root = sys.argv[1]
def rd(p): return open(os.path.join(root, p)).read()
def wr(p, s): open(os.path.join(root, p), 'w').write(s)
def sub(path, old, new, n=1):
    s = rd(path)
    assert s.count(old) == n, (path, old[:70], s.count(old))
    wr(path, s.replace(old, new))

# ---------- reveal sections as soon as they come into view (tall sections never reached 18% on phones) ----------
sub('assets/renn.js', '''  }, { threshold: 0.18 }) : null;''', '''  }, { threshold: 0, rootMargin: "0px 0px -12% 0px" }) : null;''')

# ---------- brand name: "Renn" everywhere, not the Shopify store name ----------
sch = json.loads(rd('config/settings_schema.json'))
for g in sch:
    if g.get('name') == 'Renn':
        g['settings'].insert(0, {"type": "text", "id": "brand_name", "label": "Shop name shown on the site", "default": "Renn", "info": "Used in the footer, page titles and search results."})
wr('config/settings_schema.json', json.dumps(sch, indent=2, ensure_ascii=False) + '\n')
B = "{{ settings.brand_name | default: shop.name }}"
sub('sections/renn-footer.liquid', '''{{ shop.name }}</span>''', B + '''</span>''')
sub('sections/renn-reviews.liquid', '''We only post reviews from real {{ shop.name }} customers. Bought a mask? We'd love to hear how it went.''',
    '''We only post reviews from real ''' + B + ''' customers. Bought from us? We'd love to hear how it went.''')
sub('sections/renn-header.liquid', '''aria-label="{{ shop.name }} home"''', '''aria-label="''' + B + ''' home"''')
sub('sections/renn-film.liquid', '''"name": {{ shop.name | json }}''', '''"name": {{ settings.brand_name | default: shop.name | json }}''')
sub('sections/main-product.liquid', '''"name": {{ shop.name | json }}''', '''"name": {{ settings.brand_name | default: shop.name | json }}''')
sub('layout/theme.liquid', '''"name":{{ shop.name | json }}''', '''"name":{{ settings.brand_name | default: shop.name | json }}''')
s = rd('layout/theme.liquid')
s = s.replace('''{% unless page_title contains shop.name %} | {{ shop.name }}{% endunless %}''', '''{%- assign bn = settings.brand_name | default: shop.name -%}{% unless page_title contains bn %} | {{ bn }}{% endunless %}''')
wr('layout/theme.liquid', s)
M = rd('snippets/meta-tags.liquid')
M = M.replace('''assign og_title = page_title | default: shop.name''', '''assign og_title = page_title | default: settings.brand_name | default: shop.name''')
M = M.replace('''default: shop.description | default: shop.name''', '''default: shop.description | default: settings.brand_name''')
M = M.replace('''<meta property="og:site_name" content="{{ shop.name }}">''', '''<meta property="og:site_name" content="{{ settings.brand_name | default: shop.name }}">''')
wr('snippets/meta-tags.liquid', M)

# ---------- wording ----------
sub('sections/main-cart.liquid', '>Shop the masks</a>', '>Shop now</a>')
sub('sections/main-simple.liquid', 'It may have moved. The masks are still right where you left them.', 'It may have moved. Everything else is right where you left it.')
sub('sections/main-simple.liquid', 'placeholder="Search masks"', 'placeholder="Search products"')
sub('sections/main-product.liquid', "{% render 'renn-bundle-card', kicker: 'Get all four' %}", "{% render 'renn-bundle-card', kicker: 'Get all four masks' %}")
# neck cream: only what the product sheet supports (5% Volufiline, PDRN, collagen, gua sha, dermatologist tested)
sub('sections/main-product.liquid', '''|Collagen::Helps skin feel plump and smooth.|Niacinamide::Vitamin B3. Supports the skin barrier and evens out tone.'
      assign note = 'Contains retinol: wear sunscreen during the day, and stop using it if irritation occurs.\'''',
    '''|Collagen::Helps skin feel plump and smooth.'
      assign note = 'Dermatologist tested. New to it? Try it on a small patch of skin first, and stop if irritation occurs.\'''')

# ---------- contact page: a real contact form ----------
sub('sections/main-simple.liquid', '''        <div class="rte">{{ page.content }}</div>''', '''        <div class="rte">{{ page.content }}</div>
        {%- if page.handle == 'contact' -%}
          {%- form 'contact', class: 'cform' -%}
            {%- if form.posted_successfully? -%}
              <p class="cform-ok">Thanks. Your message is on its way, and we'll reply by email.</p>
            {%- else -%}
              {%- if form.errors -%}<p class="cform-err">{{ form.errors | default_errors }}</p>{%- endif -%}
              <p class="lede">Questions about an order or a product? Send us a note and a real person will reply.</p>
              <label for="c-name">Name</label>
              <input id="c-name" type="text" name="contact[name]" autocomplete="name" value="{{ form.name }}">
              <label for="c-email">Email</label>
              <input id="c-email" type="email" name="contact[email]" autocomplete="email" required value="{{ form.email }}">
              <label for="c-msg">Message</label>
              <textarea id="c-msg" name="contact[body]" rows="6" required>{{ form.body }}</textarea>
              <button class="btn" type="submit">Send message</button>
            {%- endif -%}
          {%- endform -%}
        {%- endif -%}''')

# ---------- home page content ----------
idx = json.loads(rd('templates/index.json'))
faq = idx['sections']['faq']['blocks']
answers = {
  'Are these genuine medicube products?': '<p>Yes. Renn sells genuine medicube products in their original packaging. Renn is an independent retailer and is not run by medicube.</p>',
  'Can I use these on sensitive skin?': "<p>Many people with sensitive skin use them, but every face is different. Try a small patch first, and if you feel itching or stinging, rinse it off and stop using it.</p>",
  'How often should I use each one?': '<p>The neck cream, every day. The mud mask, once or twice a week. The night wrapping masks, 2 to 3 nights a week, or whenever your skin needs it.</p>',
  'How long does shipping take?': '<p>Shipping options, times and costs are shown at checkout before you pay. Our full shipping and returns policies are linked at the bottom of every page.</p>',
}
done = set()
for b in faq.values():
    q = b['settings'].get('q')
    if q in answers:
        b['settings']['a'] = answers[q]; done.add(q)
assert done == set(answers), done
ins = idx['sections']['inside']['blocks']
assert ins['ing4']['settings']['title'] == 'Niacinamide'
ins['ing4']['settings']['neck'] = False
wr('templates/index.json', json.dumps(idx, indent=2, ensure_ascii=False) + '\n')

# ---------- shop grid: the big bundle card only when no Black Friday / Christmas deals are showing (they already show it) ----------
sub('sections/renn-shop.liquid', '''      {%- if section.settings.show_bundle -%}{% render 'renn-bundle-card' %}{%- endif -%}''',
    '''      {%- capture season -%}{% render 'renn-promo-season' %}{%- endcapture -%}
      {%- assign season = season | strip -%}
      {%- if section.settings.show_bundle -%}<div class="bcard-wrap" data-season-off{% if season != blank %} hidden{% endif %}>{% render 'renn-bundle-card' %}</div>{%- endif -%}''')
sub('assets/renn.js', '''    document.querySelectorAll("[data-season]").forEach(function (el) {''', '''    document.querySelectorAll("[data-season-off]").forEach(function (el) { el.hidden = !!s; });
    document.querySelectorAll("[data-season]").forEach(function (el) {''')

# ---------- styles: tighter lists on phones, less scrolling ----------
s = rd('assets/renn.css')
s += '''
/* ---------- less scrolling on phones: two-up product cards, two-up ingredients ---------- */
.bcard-wrap{grid-column:1/-1}
.bcard-wrap[hidden],[data-season-off][hidden]{display:none}
@media (max-width:620px){
  .grid{grid-template-columns:1fr 1fr;gap:10px}
  .scard{padding:8px 8px 12px;border-radius:16px}
  .scard .tile{border-radius:12px}
  .scard h3{font-size:15px;line-height:1.25;margin:10px 2px 6px}
  .scard p,.scard .mono{display:none}
  .scard .buy{flex-direction:column;align-items:stretch;gap:8px;padding:0 2px}
  .scard .buy .price{font-size:15px}
  .scard .buy .btn,.scard .buy form .btn{width:100%;height:38px;padding:0 10px;font-size:13.5px}
  .scard .buy form{width:100%}
  .ings{grid-template-columns:1fr 1fr}
  .ing{padding:16px 12px 18px}
  .ing .dot{margin-bottom:12px}
  .ing h3{font-size:17px}
  .ing p{font-size:13.5px}
  section.blk{padding-top:64px;padding-bottom:64px}
}
/* contact form */
.cform{display:grid;gap:10px;margin-top:28px;max-width:560px}
.cform label{font:400 12px/1 var(--mono);letter-spacing:.1em;text-transform:uppercase;color:var(--ink-2);margin-top:8px}
.cform input,.cform textarea{font:400 16px/1.4 var(--body);padding:14px 16px;border-radius:14px;border:1px solid rgba(42,36,33,.18);background:var(--milk);color:var(--ink)}
.cform textarea{resize:vertical}
.cform .btn{justify-self:start;margin-top:8px}
.cform-ok{padding:16px 18px;border-radius:14px;background:#E3EAE4}
.cform-err{padding:12px 16px;border-radius:14px;background:#F6E1DE}
'''
wr('assets/renn.css', s)
print('patched')
