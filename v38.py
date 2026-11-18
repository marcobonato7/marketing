import sys, os, re
root = sys.argv[1]
def rd(p): return open(os.path.join(root, p)).read()
def wr(p, s): open(os.path.join(root, p), 'w').write(s)
def sub(path, old, new, n=1):
    s = rd(path)
    assert s.count(old) == n, (path, old[:70], s.count(old))
    wr(path, s.replace(old, new))

# ---------------------------------------------------------------- slot snippet
wr('snippets/renn-slot.liquid', '''{%- comment -%}
  Which pour a film block belongs to, read from its product's name (or its fallback name and photo):
  1 neck cream, 2 mud, 3 collagen, 4 PDRN, 5 kojic. This keeps every product on its own colour
  whatever order the blocks are in. Params: block, fallback_slot
{%- endcomment -%}
{%- liquid
  assign p = block.settings.product
  if p != blank
    assign h = p.handle | append: ' ' | append: p.title | downcase
  else
    assign h = block.settings.fallback_image | append: ' ' | append: block.settings.fallback_title | downcase
  endif
  assign s = fallback_slot
  if h contains 'neck' or h contains 'gua sha' or h contains 'gua-sha'
    assign s = 1
  elsif h contains 'kojic' or h contains 'turmeric'
    assign s = 5
  elsif h contains 'pdrn' or h contains 'caffeine'
    assign s = 4
  elsif h contains 'mud' or h contains 'pore' or h contains 'blackhead'
    assign s = 2
  elsif h contains 'collagen'
    assign s = 3
  endif
  echo s
-%}
''')

# ---------------------------------------------------------------- film section (markup above the JSON-LD)
F = 'sections/renn-film.liquid'
s = rd(F)
a = s.index('{%- comment -%}')
b = s.index('{%- comment -%} Product data for Google {%- endcomment -%}')
s = s[:a] + '''{%- comment -%}
  The scroll film. On arrival the neck cream's pour plays by itself and lands on the tube.
  Then, as you scroll, each product's own pour plays and comes to rest on it, where its card lands:
  1 neck cream (pink), 2 mud (blue), 3 collagen (clear), 4 PDRN (pink shimmer), 5 kojic (gold), then the bundle.
  Each block is matched to its pour by the product's name, so the block order doesn't matter.
  The frames ship inside the theme (seq-d-*.jpg for wide screens, seq-m-*.jpg for phones).
{%- endcomment -%}
{%- assign slot_labels = 'Neck care|Pore care|Moisture and firmness|Soothing and glow|Dullness care' | split: '|' -%}
{%- assign slot_alts = 'A ribbon of silky white cream pouring onto a blush-pink set|The pink medicube neck cream tube with its gua sha head, beside a swoosh of white cream|A smooth round pool of blue clay mud mask|A clear glassy pool of collagen gel|A shimmering pink pool of PDRN gel|A pale golden pool of kojic turmeric gel with amber flecks' | split: '|' -%}
<section class="film" id="film" aria-label="Product film"
  data-d="{{ 'seq-d-001.jpg' | asset_url }}" data-m="{{ 'seq-m-001.jpg' | asset_url }}" data-count="362" data-stops="120,180,240,300,360" data-fps="10">
  <div class="stage" id="stage">
    {%- for i in (0..5) -%}
      {%- assign f = 'frame-' | append: i | append: '.jpg' -%}
      {%- assign mf = 'm-frame-' | append: i | append: '.jpg' -%}
      <picture>
        <source media="(max-width: 820px)" srcset="{{ mf | asset_url }}">
        <img class="still{% if i == 0 %} on{% endif %}" data-i="{{ i }}" src="{{ f | asset_url }}" alt="{{ slot_alts[i] }}" width="1600" height="905"{% if i < 2 %} fetchpriority="high"{% else %} loading="lazy"{% endif %}>
      </picture>
    {%- endfor -%}
    <canvas id="seq" aria-hidden="true"></canvas>
    <div class="edge" aria-hidden="true"></div>
    <div class="glints" aria-hidden="true">
      <i style="left:58%;top:30%;animation-delay:0s"></i><i style="left:66%;top:62%;animation-delay:2.2s"></i>
      <i style="left:44%;top:70%;animation-delay:4.1s"></i><i style="left:72%;top:22%;animation-delay:6s"></i>
      <i style="left:52%;top:48%;animation-delay:7.3s"></i>
    </div>
    <div class="intro" id="intro">
      <h1>{{ settings.wordmark | default: 'renn' }}<b>.</b><span class="vh"> {{ section.settings.heading }}</span></h1>
      <p>{{ section.settings.heading }}</p>
      <span class="mono">{{ section.settings.subheading }}</span>
    </div>
    <div class="cue" id="cue"><span></span><small class="mono">Scroll</small></div>
    <div class="chapter mono" id="chapter" style="opacity:0">
      <span id="chapterTxt"></span>
      <div class="dots">
        {%- for i in (1..5) -%}
          {%- assign lab = slot_labels[forloop.index0] -%}
          {%- for block in section.blocks limit: 5 -%}
            {%- capture bs -%}{% render 'renn-slot', block: block, fallback_slot: forloop.index %}{%- endcapture -%}
            {%- assign bs = bs | strip | plus: 0 -%}
            {%- if bs == i and block.settings.label != blank -%}{%- assign lab = block.settings.label -%}{%- endif -%}
          {%- endfor -%}
          <i data-label="0{{ i }} / {{ lab | escape }}"></i>
        {%- endfor -%}
        {%- if section.settings.show_bundle -%}<i data-label="06 / Best value"></i>{%- endif -%}
      </div>
    </div>
    <div class="loader" id="loader" aria-hidden="true"><svg viewBox="0 0 26 26"><circle class="bg" cx="13" cy="13" r="11"/><circle class="fg" id="ring" cx="13" cy="13" r="11"/></svg></div>
    {%- for block in section.blocks limit: 5 -%}
      {%- capture bs -%}{% render 'renn-slot', block: block, fallback_slot: forloop.index %}{%- endcapture -%}
      {%- assign bs = bs | strip | plus: 0 -%}
      {%- assign side = 'left' -%}{%- assign r = bs | modulo: 2 -%}{%- if r == 0 -%}{%- assign side = 'right' -%}{%- endif -%}
      {% render 'renn-pcard', block: block, index: bs, side: side %}
    {%- endfor -%}
    {%- if section.settings.show_bundle -%}
      {% render 'renn-bundle-pcard', index: 6, side: 'right' %}
    {%- endif -%}
  </div>
  <div id="anchors"></div>
</section>

''' + s[b:]
wr(F, s)

# preload the first thing you see: the start of the neck cream pour
sub('layout/theme.liquid', "{{ 'frame-1.jpg' | asset_url | preload_tag: as: 'image', media: '(min-width: 821px)' }}",
                           "{{ 'frame-0.jpg' | asset_url | preload_tag: as: 'image', media: '(min-width: 821px)' }}")
sub('layout/theme.liquid', "{{ 'm-frame-1.jpg' | asset_url | preload_tag: as: 'image', media: '(max-width: 820px)' }}",
                           "{{ 'm-frame-0.jpg' | asset_url | preload_tag: as: 'image', media: '(max-width: 820px)' }}")

# ---------------------------------------------------------------- photos: use the theme's own product photo when the Shopify product has none
sub('snippets/renn-tile.liquid', '''  {%- elsif fallback != blank -%}''', '''  {%- elsif fallback != blank and fallback != 'none' -%}''')
sub('sections/main-product.liquid', '''        {%- elsif key == 'bundle' -%}
          {% render 'renn-bundle-collage' %}
        {%- endif -%}''', '''        {%- elsif key == 'bundle' -%}
          {% render 'renn-bundle-collage' %}
        {%- elsif key != blank -%}
          <img src="{{ key | append: '.jpg' | asset_url }}" alt="{{ product.title | escape }}" width="720" height="720" fetchpriority="high">
        {%- endif -%}''')

# ---------------------------------------------------------------- script: film part rewritten
J = 'assets/renn.js'
s = rd(J)
a = s.index('  /* =====================================================================\n     Scroll film')
s = s[:a] + r'''  /* =====================================================================
     Scroll film: the pours are a sequence of still frames drawn on a canvas.
     On arrival the first pour (the neck cream) plays by itself and lands on the tube.
     After that, scrolling moves through the frames; each pour stops on its product.
     ===================================================================== */
  var film = document.getElementById("film");
  if (!film) { addEventListener("scroll", hdrState, { passive: true }); hdrState(); return; }

  var stage = document.getElementById("stage"), cv = document.getElementById("seq"), cx = cv.getContext("2d");
  var stills = stage.querySelectorAll(".still"), pcards = stage.querySelectorAll(".pcard");
  var intro = document.getElementById("intro"), cue = document.getElementById("cue"), chapter = document.getElementById("chapter");
  var chapterTxt = document.getElementById("chapterTxt"), dots = chapter.querySelectorAll(".dots i");
  var loader = document.getElementById("loader"), ring = document.getElementById("ring");
  var conn = navigator.connection || {};
  var tiny = /(^|-)2g$/.test(conn.effectiveType || "");

  var COUNT = +film.dataset.count || 362, FPS = +film.dataset.fps || 10;
  var NB = stage.querySelectorAll(".pcard.bundle").length;
  /* the frame where each product's pour comes to rest: neck, mud, collagen, PDRN, kojic */
  var STOPS = (film.dataset.stops || "").split(",").map(Number).filter(function (n) { return n > 0; });
  if (!STOPS.length) STOPS = [120, 180, 240, 300, 360];
  var N = STOPS.length;
  var HOLD0 = 0.8, RAMP = 1.35, HOLD = 1.15;              /* in screen heights; RAMP is per 6 seconds of pour */
  /* the first pour plays on arrival, so scrolling starts from the neck cream tube */
  function rampLen(i) { return i === 0 ? 0 : Math.max(0.8, RAMP * (STOPS[i] - STOPS[i - 1]) / 60); }
  var useSeq = false, target = STOPS[0] / FPS, shown = -1, drawnF = -1, raf = 0, lastStill = -1, lastCard = -1;
  var vh = stage.clientHeight || innerHeight, lastW = innerWidth, bg = "#F5EEE6", bgT = "rgba(245,238,230,0)";

  /* opening: 1 = waiting for the first pour's frames, 2 = playing it, 0 = done (scroll drives the film) */
  var auto = (!reduce && !tiny && cx && scrollY < film.offsetTop + 30) ? 1 : 0, autoT0 = 0, AUTO_MS = 5200, scroll0 = scrollY;

  /* ---- frames ---- */
  var mobileSet = phone.matches;
  var base = (mobileSet ? film.dataset.m : film.dataset.d) || "";
  var STEP = mobileSet ? 2 : 1, NEED = Math.ceil(COUNT / STEP);   /* phones load every second frame and blend between them */
  var imgs = [], ok = [], loaded = 0, failed = 0, retried = {}, introNeed = 0, introGot = 0;
  function pad(n) { return ("00" + n).slice(-3); }
  function url(i) { return base.replace(/001\.jpg/, pad(i + 1) + ".jpg"); }
  function isIntro(k) { return k <= STOPS[0]; }
  function loadFrames() {
    var order = [], seen = {}, i, step, k;
    for (k = 0; k <= STOPS[0]; k += STEP) { seen[k] = 1; order.push(k); }   /* the opening pour first */
    introNeed = order.length;
    for (step = 8 * STEP; step >= STEP; step = step / 2 | 0) {           /* then the rest: coarse first, then fill in */
      for (i = STOPS[0]; i < COUNT; i += step) { k = i - (i % STEP); if (!seen[k]) { seen[k] = 1; order.push(k); } }
      if (step === STEP) break;
    }
    var next = 0, active = 0;
    function pump() {
      while (active < 6 && next < order.length) {
        (function (k) {
          active++;
          var im = new Image(); im.decoding = "async";
          im.onload = function () {
            imgs[k] = im; ok[k] = 1; loaded++; active--;
            if (isIntro(k)) introGot++;
            ring.style.strokeDashoffset = 69.1 * (1 - Math.min(1, loaded / NEED));
            if (auto === 1 && introGot >= introNeed) playIntro();
            else if (!auto && !useSeq && near(Math.round(target * FPS)) >= 0) start();
            else if (useSeq && !auto && Math.abs(k - target * FPS) < 9) { drawnF = -1; kick(); }
            if (loaded >= NEED) loader.classList.add("done");
            pump();
          };
          im.onerror = function () {
            active--; failed++;
            if (!retried[k]) { retried[k] = 1; setTimeout(function () { order.push(k); pump(); }, 1500); }
            else if (isIntro(k)) { introNeed--; if (auto === 1 && introGot >= introNeed) playIntro(); }
            pump();
          };
          im.src = url(k);
        })(order[next++]);
      }
    }
    pump();
  }
  function near(i) {                                          /* closest loaded frame */
    i = Math.max(0, Math.min(COUNT - 1, i));
    for (var d = 0; d < 24; d++) { if (ok[i - d]) return i - d; if (ok[i + d]) return i + d; }
    return -1;
  }

  /* ---- canvas ---- */
  function size() {
    var dpr = Math.min(window.devicePixelRatio || 1, 2);
    cv.width = Math.round(stage.clientWidth * dpr); cv.height = Math.round(stage.clientHeight * dpr);
    drawnF = -1;
  }
  function place(im) {
    var W = cv.width, H = cv.height, iw = im.naturalWidth, ih = im.naturalHeight, s, dw, dh;
    if (mobileSet) { s = Math.min(W / iw, (H * 0.7) / ih); dw = iw * s; dh = ih * s; return [(W - dw) / 2, H * 0.4 - dh / 2, dw, dh]; }
    s = Math.max(W / iw, H / ih); dw = iw * s; dh = ih * s; return [(W - dw) / 2, (H - dh) / 2, dw, dh];
  }
  function draw(f) {
    var i = Math.floor(f / STEP) * STEP, a = (f - i) / STEP, A = near(i);
    if (A < 0) return false;
    var r = place(imgs[A]);
    cx.globalAlpha = 1; cx.fillStyle = bg; cx.fillRect(0, 0, cv.width, cv.height);
    cx.drawImage(imgs[A], r[0], r[1], r[2], r[3]);
    if (A === i && a > 0.02 && ok[i + STEP]) { cx.globalAlpha = a; cx.drawImage(imgs[i + STEP], r[0], r[1], r[2], r[3]); cx.globalAlpha = 1; }
    if (mobileSet) {                                          /* soften the frame's edges into the page */
      var e = r[3] * 0.26, gt = cx.createLinearGradient(0, r[1], 0, r[1] + e), gb = cx.createLinearGradient(0, r[1] + r[3] - e, 0, r[1] + r[3]);
      gt.addColorStop(0, bg); gt.addColorStop(1, bgT); gb.addColorStop(0, bgT); gb.addColorStop(1, bg);
      cx.fillStyle = gt; cx.fillRect(0, r[1] - 1, cv.width, e + 1); cx.fillStyle = gb; cx.fillRect(0, r[1] + r[3] - e, cv.width, e + 1);
      var w = r[2] * 0.1, gl = cx.createLinearGradient(r[0], 0, r[0] + w, 0), gr = cx.createLinearGradient(r[0] + r[2] - w, 0, r[0] + r[2], 0);
      gl.addColorStop(0, bg); gl.addColorStop(1, bgT); gr.addColorStop(0, bgT); gr.addColorStop(1, bg);
      cx.fillStyle = gl; cx.fillRect(r[0] - 1, 0, w + 1, cv.height); cx.fillStyle = gr; cx.fillRect(r[0] + r[2] - w, 0, w + 1, cv.height);
    }
    return true;
  }

  /* ---- story position ---- */
  function layout() {
    vh = stage.clientHeight || innerHeight;
    var total = HOLD0 + NB * HOLD, a = "", y = HOLD0 * vh, i;
    for (i = 0; i < N; i++) total += rampLen(i) + HOLD;
    film.style.height = (total * vh + vh) + "px";
    for (i = 0; i < N; i++) { y += rampLen(i) * vh; a += '<span class="anchor" id="pour-' + (i + 1) + '" style="top:' + (y + 0.25 * vh) + 'px"></span>'; y += HOLD * vh; }
    if (NB) a += '<span class="anchor" id="bundle" style="top:' + (y + 0.25 * vh) + 'px"></span>';
    document.getElementById("anchors").innerHTML = a;
  }
  function state() {
    var y = (scrollY - film.offsetTop) / vh;
    if (y < HOLD0) return { t: STOPS[0] / FPS, hold: 0, k: Math.max(0, y / HOLD0), ramp: -1 };
    y -= HOLD0;
    for (var i = 0; i < N; i++) {
      var R = rampLen(i);
      if (y < R) { var k = y / R; return { t: (STOPS[i - 1] + k * (STOPS[i] - STOPS[i - 1])) / FPS, hold: -1, ramp: i, k: k }; }
      y -= R;
      if (y < HOLD || (i === N - 1 && !NB)) return { t: STOPS[i] / FPS, hold: i + 1, k: Math.min(y / HOLD, 1), ramp: -1 };
      y -= HOLD;
      if (i === N - 1) return { t: STOPS[i] / FPS, hold: N + 1, k: Math.min(y / HOLD, 1), ramp: -1 };
    }
  }

  function paint() {
    var s = state();
    var v = s.hold === 0 ? 1 - Math.max(0, (s.k - 0.55) / 0.45) : 0;
    intro.style.opacity = v; intro.style.setProperty("--lift", ((1 - v) * 30) + "px");
    cue.style.opacity = s.hold === 0 && s.k < 0.3 ? 1 : 0;
    chapter.style.opacity = s.hold === 0 ? 0 : 1;
    var idx = s.hold > 0 ? s.hold - 1 : (s.ramp >= 0 ? s.ramp : 0);
    if (dots[idx]) chapterTxt.textContent = dots[idx].dataset.label;
    dots.forEach(function (d, j) { d.classList.toggle("on", j === idx); });

    var c = s.hold > 0 ? s.hold : -1;
    if (c !== lastCard) { pcards.forEach(function (el) { el.classList.toggle("on", +el.dataset.i === c); }); lastCard = c; }

    target = Math.min(s.t, (COUNT - 1) / FPS);
    if (!useSeq) {                                            /* still images until frames arrive */
      var st = s.hold > 0 ? s.hold : s.hold === 0 ? (auto ? 0 : 1) : (s.k > 0.5 ? s.ramp + 1 : s.ramp);
      st = Math.min(st, N);
      if (st !== lastStill) { stills.forEach(function (el) { el.classList.toggle("on", +el.dataset.i === st); }); lastStill = st; }
    }
  }

  function tick() {
    raf = 0;
    if (auto === 2) return;
    if (shown < 0) shown = target;
    var d = target - shown;
    shown = Math.abs(d) < 0.004 ? target : shown + d * 0.16;     /* gentle easing toward the scroll position */
    var f = shown * FPS;
    if (Math.abs(f - drawnF) > 0.01) { if (draw(f)) drawnF = f; }
    if (shown !== target) raf = requestAnimationFrame(tick);
  }
  function kick() { if (useSeq && !raf && auto !== 2) raf = requestAnimationFrame(tick); }

  function start() {
    useSeq = true; size(); if (shown < 0) shown = target; drawnF = -1;
    if (draw(shown * FPS)) drawnF = shown * FPS;
    stage.classList.add("ready");
    stills.forEach(function (el) { el.classList.remove("on"); }); lastStill = -1;
  }

  /* ---- the opening pour, played on arrival ---- */
  function playIntro() {
    if (auto !== 1) return;
    auto = 2; shown = 0; start(); autoT0 = performance.now();
    requestAnimationFrame(autoTick);
  }
  function autoTick(now) {
    if (auto !== 2) return;
    var p = Math.min(1, (now - autoT0) / AUTO_MS), e = -(Math.cos(Math.PI * p) - 1) / 2;
    var f = e * STOPS[0];
    if (draw(f)) drawnF = f;
    shown = f / FPS;
    if (p < 1) requestAnimationFrame(autoTick);
    else { auto = 0; paint(); kick(); }
  }
  function endIntro() {                                       /* the visitor scrolled first, or the frames were slow */
    if (!auto) return;
    var was = auto; auto = 0; paint();
    if (was === 2) kick();
    else if (!useSeq && near(Math.round(target * FPS)) >= 0) start();
  }

  function onScroll() {
    if (auto && Math.abs(scrollY - scroll0) > 12) endIntro();
    hdrState(); paint(); kick();
  }

  layout(); paint();
  addEventListener("scroll", onScroll, { passive: true });
  addEventListener("resize", function () {
    if (mobileSet && innerWidth === lastW) return;            /* phone toolbars resizing: ignore */
    lastW = innerWidth; layout(); if (useSeq) size(); drawnF = -1; onScroll();
  });
  hdrState();
  /* The film only moves when the visitor scrolls (and once on arrival), so it also runs with Reduce Motion on. */
  if (tiny || !cx || !base) { auto = 0; paint(); loader.classList.add("done"); return; }   /* stills only */
  if (auto) setTimeout(function () { if (auto === 1) endIntro(); }, 8000);
  /* Start right away: waiting for the page "load" event can take a long time on phones and in-app browsers. */
  loadFrames();

  /* Status readout: add ?renn-debug to the page address to see it. */
  if (/renn-debug/.test(location.search)) {
    var dbg = document.createElement("div");
    dbg.style.cssText = "position:fixed;left:8px;bottom:8px;z-index:99;background:#000;color:#fff;font:12px/1.4 monospace;padding:6px 8px;border-radius:8px;opacity:.85";
    document.body.appendChild(dbg);
    setInterval(function () {
      dbg.textContent = "film 3.8 | set " + (mobileSet ? "phone" : "desktop") + " | frames " + loaded + "/" + NEED + " | failed " + failed + " | playing " + useSeq + " | intro " + auto + " | reduce-motion " + reduce + " | dpr " + (window.devicePixelRatio || 1);
    }, 500);
  }
})();
'''
wr(J, s)
print('patched')
