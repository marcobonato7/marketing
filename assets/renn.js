/* Renn theme script: header, reveals, add to cart, mask picker, scroll film. */
(function () {
  var R = window.RENN_ROUTES || { cartAdd: "/cart/add.js", cart: "/cart", cartJs: "/cart.js" };
  var hdr = document.getElementById("hdr");
  var mq = matchMedia("(max-width: 820px), (hover: none) and (pointer: coarse)");
  var reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---------- reveals ---------- */
  var io = "IntersectionObserver" in window ? new IntersectionObserver(function (es) {
    es.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add("in"); io.unobserve(en.target); } });
  }, { threshold: 0.18 }) : null;
  document.querySelectorAll(".reveal, .mscene").forEach(function (el) { io ? io.observe(el) : el.classList.add("in"); });

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
  function hdrState() { if (hdr && !hdr.classList.contains("always")) hdr.classList.toggle("solid", scrollY > innerHeight * 0.6 || mq.matches); }

  /* ---------- scroll film (desktop only) ---------- */
  var film = document.getElementById("film");
  if (!film) { addEventListener("scroll", hdrState, { passive: true }); hdrState(); return; }

  var stage = document.getElementById("stage"), vid = document.getElementById("vid");
  var stills = stage.querySelectorAll(".still"), pcards = stage.querySelectorAll(".pcard");
  var intro = document.getElementById("intro"), cue = document.getElementById("cue"), chapter = document.getElementById("chapter");
  var chapterTxt = document.getElementById("chapterTxt"), dots = chapter.querySelectorAll(".dots i");
  var loader = document.getElementById("loader"), ring = document.getElementById("ring");
  var conn = navigator.connection || {};
  var slow = conn.saveData || /(^|-)2g$/.test(conn.effectiveType || "") || conn.effectiveType === "3g";

  var SEG = 6, N = Math.max(1, pcards.length);           /* each product is a 6 second pour */
  var HOLD0 = 0.7, RAMP = 1.35, HOLD = 1.15;             /* in screen heights */
  var useVideo = false, target = 0, shown = 0, raf = 0, lastStill = -1, lastCard = -1, seeking = false;

  function layout() {
    var vh = innerHeight;
    film.style.height = ((HOLD0 + N * (RAMP + HOLD)) * vh + vh) + "px";
    var a = "", y = HOLD0 * vh;
    for (var i = 1; i <= N; i++) { y += RAMP * vh; a += '<span class="anchor" id="pour-' + i + '" style="top:' + (y + 0.25 * vh) + 'px"></span>'; y += HOLD * vh; }
    document.getElementById("anchors").innerHTML = a;
  }

  function state() {
    var vh = innerHeight, y = (scrollY - film.offsetTop) / vh;
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
    intro.style.opacity = v; intro.style.transform = "translateY(calc(-50% - " + ((1 - v) * 30) + "px))";
    cue.style.opacity = s.hold === 0 && s.k < 0.3 ? 1 : 0;
    chapter.style.opacity = s.hold === 0 ? 0 : 1;
    var idx = s.hold > 0 ? s.hold - 1 : (s.ramp >= 0 ? s.ramp : 0);
    if (dots[idx]) chapterTxt.textContent = dots[idx].dataset.label;
    dots.forEach(function (d, j) { d.classList.toggle("on", j === idx); });

    var c = s.hold > 0 ? s.hold : -1;
    if (c !== lastCard) { pcards.forEach(function (el) { el.classList.toggle("on", +el.dataset.i === c); }); lastCard = c; }

    if (useVideo) { target = Math.min(s.t, (vid.duration || s.t + 1) - 0.04); }
    else {
      var st = s.hold >= 0 ? s.hold : (s.k > 0.5 ? s.ramp + 1 : s.ramp);
      if (st !== lastStill) { stills.forEach(function (el) { el.classList.toggle("on", +el.dataset.i === st); }); lastStill = st; }
    }
  }

  function tick() {
    raf = 0;
    var d = target - shown;
    shown = Math.abs(d) < 0.008 ? target : shown + d * 0.14;
    if (!seeking && Math.abs(vid.currentTime - shown) > 0.015) { seeking = true; vid.currentTime = shown; }
    if (shown !== target || seeking) raf = requestAnimationFrame(tick);
  }
  vid.addEventListener("seeked", function () { seeking = false; if (!raf && shown !== target) raf = requestAnimationFrame(tick); });

  function onScroll() {
    hdrState();
    if (mq.matches) return;
    paint();
    if (useVideo && !raf) raf = requestAnimationFrame(tick);
  }

  function loadFilm() {
    if (!window.fetch || !window.URL || !vid.dataset.src) return fallback();
    fetch(vid.dataset.src).then(function (r) {
      if (!r.ok) throw 0;
      var total = +r.headers.get("content-length") || 0;
      if (!r.body || !total) return r.blob();
      var rd = r.body.getReader(), got = 0, parts = [];
      return (function pump() {
        return rd.read().then(function (x) {
          if (x.done) return new Blob(parts, { type: "video/mp4" });
          parts.push(x.value); got += x.value.length;
          ring.style.strokeDashoffset = 69.1 * (1 - got / total);
          return pump();
        });
      })();
    }).then(function (b) {
      vid.src = URL.createObjectURL(b);
      vid.addEventListener("loadeddata", function () {
        useVideo = true; stage.classList.add("ready"); loader.classList.add("done");
        stills.forEach(function (el) { el.classList.remove("on"); });
        shown = target = state().t; vid.currentTime = shown; onScroll();
      }, { once: true });
      vid.load();
    }).catch(direct);
  }
  /* if the video host blocks fetch, play it straight from its link instead */
  function direct() {
    if (!vid.dataset.src) return fallback();
    vid.preload = "auto"; vid.src = vid.dataset.src;
    vid.addEventListener("loadeddata", function () {
      useVideo = true; stage.classList.add("ready"); loader.classList.add("done");
      stills.forEach(function (el) { el.classList.remove("on"); });
      shown = target = state().t; vid.currentTime = shown; onScroll();
    }, { once: true });
    vid.addEventListener("error", fallback, { once: true });
    vid.load();
  }
  function fallback() { useVideo = false; loader.classList.add("done"); onScroll(); }

  layout();
  addEventListener("resize", function () { layout(); onScroll(); });
  addEventListener("scroll", onScroll, { passive: true });
  onScroll();
  if (!mq.matches) {
    if (reduce || slow) fallback();
    else if (document.readyState === "complete") loadFilm();
    else addEventListener("load", loadFilm);
  } else { loader.classList.add("done"); }
})();
