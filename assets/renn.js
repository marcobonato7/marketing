/* Renn theme script: header, reveals, add to cart, mask picker, scroll film. */
(function () {
  var R = window.RENN_ROUTES || { cartAdd: "/cart/add.js", cart: "/cart", cartJs: "/cart.js" };
  var hdr = document.getElementById("hdr");
  var phone = matchMedia("(max-width: 820px)");
  var reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---------- reveals ---------- */
  var io = "IntersectionObserver" in window ? new IntersectionObserver(function (es) {
    es.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add("in"); io.unobserve(en.target); } });
  }, { threshold: 0, rootMargin: "0px 0px -12% 0px" }) : null;
  document.querySelectorAll(".reveal").forEach(function (el) { io ? io.observe(el) : el.classList.add("in"); });

  /* ---------- TikTok reels: arrows and the in-page player ---------- */
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

  /* ---------- Black Friday / Christmas: show the running promotion, count down, copy codes ---------- */
  (function () {
    var P = window.RENN_PROMO; if (!P) return;
    var d = new Date(), today = d.getFullYear() * 10000 + (d.getMonth() + 1) * 100 + d.getDate();
    var s = P.mode === "off" ? "" : P.mode === "bf" ? "bf" : P.mode === "xmas" ? "xmas" :
      (today >= P.bf[0] && today < P.bf[1]) ? "bf" : (today >= P.xmas[0] && today < P.xmas[1]) ? "xmas" : "";
    var closed = false; try { closed = sessionStorage.getItem("renn-bar-" + s) === "1"; } catch (e) {}
    document.querySelectorAll("[data-season-off]").forEach(function (el) { el.hidden = !!s; });
    document.querySelectorAll("[data-season]").forEach(function (el) {
      el.hidden = el.dataset.season !== s || (closed && el.hasAttribute("data-bar"));
    });
    var bar = s && !closed && document.querySelector('[data-bar][data-season="' + s + '"]');
    document.documentElement.classList.toggle("has-bar", !!bar);
    document.querySelectorAll("[data-bar-close]").forEach(function (b) {
      b.addEventListener("click", function () {
        try { sessionStorage.setItem("renn-bar-" + s, "1"); } catch (e) {}
        b.parentNode.hidden = true; document.documentElement.classList.remove("has-bar");
        if (window.RENN_RELAYOUT) window.RENN_RELAYOUT();
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
  /* ---------- pick-three mask picker ---------- */
  document.querySelectorAll("[data-mpick]").forEach(function (fs) {
    var vars = []; try { vars = JSON.parse(fs.querySelector("script").textContent); } catch (x) {}
    var boxes = [].slice.call(fs.querySelectorAll("input[type=checkbox]")), out = fs.querySelector("input[name=id]"), cnt = fs.querySelector("[data-mcount]");
    function sync() {
      var on = boxes.filter(function (b) { return b.checked; }).map(function (b) { return b.value; }), hit = null;
      boxes.forEach(function (b) { b.disabled = !b.checked && on.length >= 3; b.closest(".mopt").classList.toggle("on", b.checked); });
      if (on.length === 3) vars.forEach(function (v) { var t = v.t.split(", "); if (v.a && on.every(function (n) { return t.indexOf(n) > -1; })) hit = v; });
      if (hit) out.value = hit.id;
      fs.dataset.ok = hit ? "1" : "0"; fs.classList.toggle("short", !hit);
      cnt.textContent = on.length === 3 ? (hit ? "3 of 3 chosen" : "That set is sold out") : "Pick " + (3 - on.length) + " more";
    }
    boxes.forEach(function (b) { b.addEventListener("change", sync); }); sync();
  });

  document.addEventListener("submit", function (e) {
    var f = e.target;
    if (!f.classList || !f.classList.contains("add") || !window.fetch) return;
    e.preventDefault();
    var mp = f.querySelector("[data-mpick]");
    if (mp && mp.dataset.ok !== "1") { showToast("<span>Choose 3 masks first.</span>"); mp.scrollIntoView({ block: "center", behavior: "smooth" }); return; }
    var btn = f.querySelector("[type=submit]"), label = btn ? btn.textContent : "";
    if (btn) { btn.disabled = true; btn.classList.add("busy"); btn.textContent = "Adding..."; }
    fetch(R.cartAdd, { method: "POST", headers: { "Accept": "application/json", "X-Requested-With": "XMLHttpRequest" }, body: new FormData(f) })
      .then(function (r) { return r.json().then(function (j) { if (!r.ok) throw j; return j; }); })
      .then(function (item) {
        var nm = String((item.product_title || "item") + (item.variant_title && item.variant_title !== "Default Title" ? " · " + item.variant_title : "")).replace(/</g, "&lt;");
        var img = item.image ? "<img src=\"" + item.image + (item.image.indexOf("?") < 0 ? "?" : "&") + "width=120\" alt=\"\">" : "";
        showToast(img + "<span class=\"t-txt\"><small>Added to your cart</small><b>" + nm + "</b></span><a href=\"" + R.cart + "\">View cart</a>");
        return fetch(R.cartJs, { headers: { "Accept": "application/json" } }).then(function (r) { return r.json(); }).then(function (c) { setCount(c.item_count); });
      })
      .catch(function (err) {
        showToast("<span>" + ((err && (err.description || err.message)) || "Couldn't add that. Please try again.") + "</span>");
      })
      .then(function () { if (btn) { btn.disabled = false; btn.classList.remove("busy"); btn.textContent = label; } });
  });

  /* ---------- product page: variant price + thumbnails ---------- */
  var vsel = document.getElementById("variant"), vprices = document.querySelectorAll("[data-price]");
  if (vsel) vsel.addEventListener("change", function () {
    var pr = vsel.options[vsel.selectedIndex].dataset.price;
    vprices.forEach(function (el) { el.textContent = pr; });
  });
  var main = document.querySelector(".main-img img"), thumbs = document.querySelectorAll(".thumb");
  thumbs.forEach(function (t) {
    t.addEventListener("click", function () {
      if (main) { main.removeAttribute("srcset"); main.src = t.dataset.src; }
      thumbs.forEach(function (o) { o.classList.toggle("on", o === t); });
    });
  });
  document.querySelectorAll("[data-step]").forEach(function (b) {
    b.addEventListener("click", function () {
      var q = document.getElementById("qty"); if (!q) return;
      q.value = Math.max(1, (parseInt(q.value, 10) || 1) + (+b.dataset.step));
    });
  });
  var sticky = document.getElementById("stickyBuy"), pform = document.getElementById("renn-pform");
  if (sticky && pform && "IntersectionObserver" in window) {
    new IntersectionObserver(function (es) {
      var show = !es[0].isIntersecting && es[0].boundingClientRect.top < 0;
      sticky.classList.toggle("on", show); sticky.setAttribute("aria-hidden", show ? "false" : "true");
      var sb = sticky.querySelector("button"); if (sb) sb.tabIndex = show ? 0 : -1;
    }).observe(pform);
  }

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
  var auto = (!reduce && !tiny && cx && scrollY < film.offsetTop + 30) ? 1 : 0, autoT0 = 0, AUTO_MS = 11000, scroll0 = scrollY;

  /* ---- frames ---- */
  var mobileSet = phone.matches;
  var base = (mobileSet ? film.dataset.m : film.dataset.d) || "";
  var STEP = mobileSet ? 2 : 1;                                   /* phones load every second frame after the opening and blend between them */
  var NEED = STOPS[0] + 1 + Math.ceil((COUNT - STOPS[0] - 1) / STEP);
  var imgs = [], ok = [], loaded = 0, failed = 0, retried = {}, introNeed = 0, introGot = 0;
  function pad(n) { return ("00" + n).slice(-3); }
  function url(i) { return base.replace(/001\.jpg/, pad(i + 1) + ".jpg"); }
  function isIntro(k) { return k <= STOPS[0]; }
  function stepAt(f) { return f <= STOPS[0] ? 1 : STEP; }          /* the opening always uses every frame */
  function loadFrames() {
    var order = [], seen = {}, i, step, k;
    for (k = 0; k <= STOPS[0]; k++) { seen[k] = 1; order.push(k); }       /* the opening pour first, every frame */
    introNeed = order.length;
    for (step = 8 * STEP; step >= STEP; step = step / 2 | 0) {           /* then the rest: coarse first, then fill in */
      for (i = STOPS[0]; i < COUNT; i += step) { k = i - (i % STEP); if (!seen[k]) { seen[k] = 1; order.push(k); } }
      if (step === STEP) break;
    }
    NEED = order.length;                                              /* every frame this device will load */
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
    var dpr = Math.min(window.devicePixelRatio || 1, 3);
    cv.width = Math.round(stage.clientWidth * dpr); cv.height = Math.round(stage.clientHeight * dpr);
    drawnF = -1;
  }
  function place(im) {
    var W = cv.width, H = cv.height, iw = im.naturalWidth, ih = im.naturalHeight, s, dw, dh;
    if (mobileSet) { s = Math.min(W / iw, (H * 0.7) / ih); dw = iw * s; dh = ih * s; return [(W - dw) / 2, H * 0.4 - dh / 2, dw, dh]; }
    s = Math.max(W / iw, H / ih); dw = iw * s; dh = ih * s; return [(W - dw) / 2, (H - dh) / 2, dw, dh];
  }
  function draw(f) {
    var st = stepAt(f), i = Math.floor(f / st) * st, a = (f - i) / st, A = near(i);
    if (A < 0) return false;
    var r = place(imgs[A]);
    cx.imageSmoothingEnabled = true; if ("imageSmoothingQuality" in cx) cx.imageSmoothingQuality = "high";
    cx.globalAlpha = 1; cx.fillStyle = bg; cx.fillRect(0, 0, cv.width, cv.height);
    cx.drawImage(imgs[A], r[0], r[1], r[2], r[3]);
    if (A === i && a > 0.02 && ok[i + st]) { cx.globalAlpha = a; cx.drawImage(imgs[i + st], r[0], r[1], r[2], r[3]); cx.globalAlpha = 1; }
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
    var p = Math.min(1, (now - autoT0) / AUTO_MS), e = p < 0.85 ? p * 0.9 / 0.85 : 0.9 + 0.1 * (1 - Math.pow(1 - (p - 0.85) / 0.15, 2));
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
  window.RENN_RELAYOUT = function () { layout(); if (useSeq) size(); drawnF = -1; onScroll(); };   /* the promotion bar was closed */
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
      dbg.textContent = "film 3.9 | set " + (mobileSet ? "phone" : "desktop") + " | frames " + loaded + "/" + NEED + " | failed " + failed + " | playing " + useSeq + " | intro " + auto + " | reduce-motion " + reduce + " | dpr " + (window.devicePixelRatio || 1);
    }, 500);
  }
})();
