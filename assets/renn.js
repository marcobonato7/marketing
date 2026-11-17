/* Renn theme script: header, reveals, add to cart, mask picker, scroll film. */
(function () {
  var R = window.RENN_ROUTES || { cartAdd: "/cart/add.js", cart: "/cart", cartJs: "/cart.js" };
  var hdr = document.getElementById("hdr");
  var phone = matchMedia("(max-width: 820px)");
  var reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---------- reveals ---------- */
  var io = "IntersectionObserver" in window ? new IntersectionObserver(function (es) {
    es.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add("in"); io.unobserve(en.target); } });
  }, { threshold: 0.18 }) : null;
  document.querySelectorAll(".reveal").forEach(function (el) { io ? io.observe(el) : el.classList.add("in"); });

  /* ---------- add to cart without leaving the page ---------- */
  var toast = document.getElementById("toast"), toastT;
  function showToast(html) {
    if (!toast) return;
    toast.innerHTML = html; toast.classList.add("on");
    clearTimeout(toastT); toastT = setTimeout(function () { toast.classList.remove("on"); }, 4200);
  }
  function setCount(n) {
    document.querySelectorAll("[data-cart-count]").forEach(function (el) { el.textContent = n; el.hidden = !n; });
  }
  document.addEventListener("submit", function (e) {
    var f = e.target;
    if (!f.classList || !f.classList.contains("add") || !window.fetch) return;
    e.preventDefault();
    var btn = f.querySelector("[type=submit]"), label = btn ? btn.textContent : "";
    if (btn) { btn.disabled = true; btn.classList.add("busy"); btn.textContent = "Adding..."; }
    fetch(R.cartAdd, { method: "POST", headers: { "Accept": "application/json", "X-Requested-With": "XMLHttpRequest" }, body: new FormData(f) })
      .then(function (r) { return r.json().then(function (j) { if (!r.ok) throw j; return j; }); })
      .then(function (item) {
        showToast("<span>Added: " + String(item.product_title || "item").replace(/</g, "&lt;") + "</span><a href=\"" + R.cart + "\">View cart</a>");
        return fetch(R.cartJs, { headers: { "Accept": "application/json" } }).then(function (r) { return r.json(); }).then(function (c) { setCount(c.item_count); });
      })
      .catch(function (err) {
        showToast("<span>" + ((err && (err.description || err.message)) || "Couldn't add that. Please try again.") + "</span>");
      })
      .then(function () { if (btn) { btn.disabled = false; btn.classList.remove("busy"); btn.textContent = label; } });
  });

  /* ---------- product page: variant price + thumbnails ---------- */
  var vsel = document.getElementById("variant"), vprice = document.querySelector("[data-price]");
  if (vsel && vprice) vsel.addEventListener("change", function () { vprice.textContent = vsel.options[vsel.selectedIndex].dataset.price; });
  var main = document.querySelector(".main-img img");
  document.querySelectorAll(".thumb").forEach(function (t) {
    t.addEventListener("click", function () { if (main) { main.removeAttribute("srcset"); main.src = t.dataset.src; } });
  });

  /* ---------- "Which mask tonight?" picker ---------- */
  var pick = document.getElementById("pick");
  if (pick) {
    var opts = pick.querySelectorAll("[data-pick]"), res = pick.querySelectorAll("[data-for]");
    opts.forEach(function (b) {
      b.addEventListener("click", function () {
        opts.forEach(function (o) { o.setAttribute("aria-pressed", o === b ? "true" : "false"); });
        res.forEach(function (r) { r.hidden = r.dataset.for !== b.dataset.pick; });
      });
    });
  }

  /* ---------- header ---------- */
  function hdrState() {
    if (!hdr || hdr.classList.contains("always")) return;
    var fm = document.getElementById("film");
    var lim = fm ? fm.offsetTop + fm.offsetHeight - innerHeight * 1.02 : innerHeight * 0.6;
    hdr.classList.toggle("solid", scrollY > lim);
  }

  /* =====================================================================
     Scroll film: the pours are a sequence of still frames drawn on a canvas.
     Scrolling moves through the frames; each pour stops on its product.
     ===================================================================== */
  var film = document.getElementById("film");
  if (!film) { addEventListener("scroll", hdrState, { passive: true }); hdrState(); return; }

  var stage = document.getElementById("stage"), cv = document.getElementById("seq"), cx = cv.getContext("2d");
  var stills = stage.querySelectorAll(".still"), pcards = stage.querySelectorAll(".pcard");
  var intro = document.getElementById("intro"), cue = document.getElementById("cue"), chapter = document.getElementById("chapter");
  var chapterTxt = document.getElementById("chapterTxt"), dots = chapter.querySelectorAll(".dots i");
  var loader = document.getElementById("loader"), ring = document.getElementById("ring");
  var conn = navigator.connection || {};
  var tiny = conn.saveData || /(^|-)2g$/.test(conn.effectiveType || "");

  var COUNT = +film.dataset.count || 242, FPS = +film.dataset.fps || 10;
  var SEG = 6, N = Math.max(1, pcards.length);            /* each product is a 6 second pour */
  var HOLD0 = 0.7, RAMP = 1.35, HOLD = 1.15;              /* in screen heights */
  var useSeq = false, target = 0, shown = -1, drawnF = -1, raf = 0, lastStill = -1, lastCard = -1;
  var vh = stage.clientHeight || innerHeight, lastW = innerWidth, bg = "#F5EEE6", bgT = "rgba(245,238,230,0)";

  /* ---- frames ---- */
  var mobileSet = phone.matches;
  var base = (mobileSet ? film.dataset.m : film.dataset.d) || "";
  var imgs = [], ok = [], loaded = 0, failed = 0, retried = {};
  function pad(n) { return ("00" + n).slice(-3); }
  function url(i) { return base.replace(/001\.jpg/, pad(i + 1) + ".jpg"); }
  function loadFrames(startAt) {
    var order = [], seen = {}, i, step;
    for (step = 8; step >= 1; step = step / 2 | 0) {            /* coarse pass first, then fill in */
      for (i = 0; i < COUNT; i += step) { var k = (startAt + i) % COUNT; if (!seen[k]) { seen[k] = 1; order.push(k); } }
      if (step === 1) break;
    }
    var next = 0, active = 0;
    function pump() {
      while (active < 6 && next < order.length) {
        (function (k) {
          active++;
          var im = new Image(); im.decoding = "async";
          im.onload = function () {
            imgs[k] = im; ok[k] = 1; loaded++; active--;
            ring.style.strokeDashoffset = 69.1 * (1 - loaded / COUNT);
            if (loaded === 1) sampleBg(im);
            if (!useSeq && near(Math.round(target * FPS)) >= 0) start();
            if (useSeq && Math.abs(k - target * FPS) < 9) { drawnF = -1; kick(); }
            if (loaded === COUNT) loader.classList.add("done");
            pump();
          };
          im.onerror = function () {
            active--; failed++;
            if (!retried[k]) { retried[k] = 1; setTimeout(function () { order.push(k); pump(); }, 1500); }
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
    for (var d = 0; d < 16; d++) { if (ok[i - d]) return i - d; if (ok[i + d]) return i + d; }
    return -1;
  }
  function sampleBg() { /* the film fades into the page colour, so there is nothing to sample */ }

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
    var i = Math.floor(f), a = f - i, A = near(i);
    if (A < 0) return false;
    var r = place(imgs[A]);
    cx.globalAlpha = 1; cx.fillStyle = bg; cx.fillRect(0, 0, cv.width, cv.height);
    cx.drawImage(imgs[A], r[0], r[1], r[2], r[3]);
    if (A === i && a > 0.02 && ok[i + 1]) { cx.globalAlpha = a; cx.drawImage(imgs[i + 1], r[0], r[1], r[2], r[3]); cx.globalAlpha = 1; }
    if (mobileSet) {                                          /* soften the frame's top and bottom edges */
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
    film.style.height = ((HOLD0 + N * (RAMP + HOLD)) * vh + vh) + "px";
    var a = "", y = HOLD0 * vh;
    for (var i = 1; i <= N; i++) { y += RAMP * vh; a += '<span class="anchor" id="pour-' + i + '" style="top:' + (y + 0.25 * vh) + 'px"></span>'; y += HOLD * vh; }
    document.getElementById("anchors").innerHTML = a;
  }
  function state() {
    var y = (scrollY - film.offsetTop) / vh;
    if (y < HOLD0) return { t: 0, hold: 0, k: Math.max(0, y / HOLD0), ramp: -1 };
    y -= HOLD0;
    for (var i = 0; i < N; i++) {
      if (y < RAMP) { var k = y / RAMP; return { t: (i + k) * SEG, hold: -1, ramp: i, k: k }; }
      y -= RAMP;
      if (y < HOLD || i === N - 1) return { t: (i + 1) * SEG, hold: i + 1, k: Math.min(y / HOLD, 1), ramp: -1 };
      y -= HOLD;
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
      var st = s.hold >= 0 ? s.hold : (s.k > 0.5 ? s.ramp + 1 : s.ramp);
      if (st !== lastStill) { stills.forEach(function (el) { el.classList.toggle("on", +el.dataset.i === st); }); lastStill = st; }
    }
  }

  function tick() {
    raf = 0;
    if (shown < 0) shown = target;
    var d = target - shown;
    shown = Math.abs(d) < 0.004 ? target : shown + d * 0.16;     /* gentle easing toward the scroll position */
    var f = shown * FPS;
    if (Math.abs(f - drawnF) > 0.01) { if (draw(f)) drawnF = f; }
    if (shown !== target) raf = requestAnimationFrame(tick);
  }
  function kick() { if (useSeq && !raf) raf = requestAnimationFrame(tick); }

  function start() {
    useSeq = true; size(); shown = target; drawnF = -1;
    if (draw(target * FPS)) drawnF = target * FPS;
    stage.classList.add("ready");
    stills.forEach(function (el) { el.classList.remove("on"); }); lastStill = -1;
  }

  function onScroll() { hdrState(); paint(); kick(); }

  layout(); paint();
  addEventListener("scroll", onScroll, { passive: true });
  addEventListener("resize", function () {
    if (mobileSet && innerWidth === lastW) return;            /* phone toolbars resizing: ignore */
    lastW = innerWidth; layout(); if (useSeq) size(); onScroll();
  });
  hdrState();
  /* The film only moves when the visitor scrolls, so it also runs with Reduce Motion on. */
  if (tiny || !cx || !base) { loader.classList.add("done"); return; }   /* stills only */
  /* Start right away: waiting for the page "load" event can take a long time on phones and in-app browsers. */
  loadFrames(Math.round(target * FPS));

  /* Status readout: add ?renn-debug to the page address to see it. */
  if (/renn-debug/.test(location.search)) {
    var dbg = document.createElement("div");
    dbg.style.cssText = "position:fixed;left:8px;bottom:8px;z-index:99;background:#000;color:#fff;font:12px/1.4 monospace;padding:6px 8px;border-radius:8px;opacity:.85";
    document.body.appendChild(dbg);
    setInterval(function () {
      dbg.textContent = "film 3.1 | set " + (mobileSet ? "phone" : "desktop") + " | frames " + loaded + "/" + COUNT + " | failed " + failed + " | playing " + useSeq + " | reduce-motion " + reduce + " | dpr " + (window.devicePixelRatio || 1);
    }, 500);
  }
})();
