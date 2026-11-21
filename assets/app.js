/* DayOneDrop interactions */
(function () {
  "use strict";
  var D = window.DOD || { games: [] }, G = D.games;
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var store = {
    get: function (k, d) { try { var v = localStorage.getItem(k); return v ? JSON.parse(v) : d; } catch (e) { return d; } },
    set: function (k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) {} }
  };
  var toastEl;
  function toast(m) {
    if (!toastEl) { toastEl = document.createElement("div"); toastEl.className = "toast"; toastEl.setAttribute("role", "status"); document.body.appendChild(toastEl); }
    toastEl.textContent = m; toastEl.classList.add("show"); clearTimeout(toastEl.t);
    toastEl.t = setTimeout(function () { toastEl.classList.remove("show"); }, 1800);
  }
  var top = $(".topbar"), mb = $(".menu-btn");
  if (mb) mb.addEventListener("click", function () { var o = top.classList.toggle("open"); mb.setAttribute("aria-expanded", o); });

  /* time helpers: release dates count down to midnight in the visitor's own time zone */
  function at(g) { if (!g.date) return null; var p = g.date.split("-"); return new Date(+p[0], +p[1] - 1, +p[2]).getTime(); }
  function left(ms) { var d = Math.max(0, ms - Date.now()); return [Math.floor(d / 864e5), Math.floor(d / 36e5) % 24, Math.floor(d / 6e4) % 60, Math.floor(d / 1e3) % 60]; }
  function pad(n, l) { n = String(n); while (n.length < (l || 2)) n = "0" + n; return n; }

  /* split-flap text */
  var CH = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
  function flap(el, text, opts) {
    opts = opts || {};
    text = String(text).toUpperCase();
    var cells = $$(".fl", el);
    if (cells.length !== text.length) {
      el.innerHTML = text.split("").map(function (c) { return '<span class="fl' + (c === " " ? " sp" : "") + '" aria-hidden="true"> </span>'; }).join("");
      el.setAttribute("aria-label", text);
      cells = $$(".fl", el);
    }
    text.split("").forEach(function (c, i) {
      var cell = cells[i];
      if (cell.textContent === c) return;
      if (reduce || opts.instant || c === " ") { cell.textContent = c; return; }
      var n = 4 + Math.floor(Math.random() * 6) + (opts.stagger ? i % 8 : 0), k = 0;
      (function step() {
        cell.classList.remove("flip"); void cell.offsetWidth; cell.classList.add("flip");
        cell.textContent = k >= n ? c : CH[Math.floor(Math.random() * CH.length)];
        if (k++ < n) setTimeout(step, 55);
      })();
    });
  }

  /* countdowns */
  function countdown(root, ms) {
    var units = $$("[data-u]", root);
    function tick() {
      var v = left(ms);
      units.forEach(function (u) { flap(u, pad(v[+u.dataset.u], u.dataset.u === "0" ? 3 : 2)); });
      if (ms - Date.now() > 0) setTimeout(tick, 1000);
    }
    tick();
  }
  $$("[data-countdown]").forEach(function (root) { countdown(root, at({ date: root.dataset.countdown })); });

  /* home: next drop */
  var nd = $("#next-drop");
  if (nd) {
    var now = Date.now(), upcoming = G.filter(function (g) { return g.date && at(g) > now; }).sort(function (a, b) { return at(a) - at(b); });
    var n = upcoming[0];
    if (n) {
      flap($("#nd-title", nd), n.title.length > 22 ? n.title.split(":")[0] : n.title, { stagger: true });
      $("#nd-date", nd).textContent = new Date(at(n)).toLocaleDateString(undefined, { weekday: "long", day: "numeric", month: "long", year: "numeric" });
      var link = $("#nd-link", nd); if (n.page) link.href = link.dataset.base + n.slug + link.dataset.ext; else link.hidden = true;
      countdown($("#nd-cd", nd), at(n));
    }
  }

  /* live clock on boards */
  $$("[data-clock]").forEach(function (c) {
    var t = function () { c.textContent = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }) + " LOCAL"; };
    t(); setInterval(t, 15000);
  });

  /* watchlist */
  var WL = store.get("dod-watch", []);
  var fromHash = (location.hash || "").match(/^#list-([\d-]+)$/);
  if (fromHash) {
    var shared = fromHash[1].split("-").map(Number).filter(function (i) { return G[i]; }).map(function (i) { return G[i].slug; });
    if (shared.length) { WL = Array.from(new Set(WL.concat(shared))); store.set("dod-watch", WL); setTimeout(function () { toast(shared.length + " games added to your list"); }, 600); }
  }
  function syncStars() {
    $$(".star").forEach(function (s) { var on = WL.indexOf(s.dataset.slug) > -1; s.setAttribute("aria-pressed", on); s.textContent = on ? "★" : "☆"; s.setAttribute("aria-label", (on ? "Remove " : "Add ") + s.dataset.name + (on ? " from" : " to") + " your list"); });
    $$("[data-wl-count]").forEach(function (e) { e.textContent = WL.length; });
  }
  document.addEventListener("click", function (e) {
    var s = e.target.closest(".star"); if (!s) return;
    var i = WL.indexOf(s.dataset.slug);
    if (i > -1) WL.splice(i, 1); else WL.push(s.dataset.slug);
    store.set("dod-watch", WL); syncStars(); toast(i > -1 ? "Removed from your list" : "Added to your list");
    if (typeof renderWatch === "function") renderWatch();
    if (typeof filterBoard === "function") filterBoard();
  });
  syncStars();

  /* board filters and T-minus */
  var board = $("#board"), plat = "all";
  var filterBoard = null;
  if (board) {
    var rows = $$("tbody tr", board);
    rows.forEach(function (r) {
      var g = G.filter(function (x) { return x.slug === r.dataset.slug; })[0], tm = $(".tminus", r);
      if (g && g.date && tm) { var v = left(at(g)); tm.textContent = at(g) > Date.now() ? "T-" + v[0] + "D" : "OUT NOW"; }
      var dc = $(".d span", r); if (dc && !reduce) { var txt = dc.textContent; dc.textContent = ""; setTimeout(function () { flapInline(dc, txt); }, 120 + rows.indexOf(r) * 70); }
    });
    filterBoard = function () {
      var shown = 0;
      rows.forEach(function (r) {
        var ps = (r.dataset.plat || "").split("|"), ok;
        if (plat === "all") ok = true;
        else if (plat === "watch") ok = WL.indexOf(r.dataset.slug) > -1;
        else ok = ps.indexOf(plat) > -1;
        r.hidden = !ok; if (ok) shown++;
      });
      var em = $("#board-empty"); if (em) em.hidden = shown > 0;
    };
    $$("#plat-chips .chip").forEach(function (b) {
      b.addEventListener("click", function () {
        $$("#plat-chips .chip").forEach(function (x) { x.setAttribute("aria-pressed", "false"); });
        b.setAttribute("aria-pressed", "true"); plat = b.dataset.p; filterBoard();
      });
    });
  }
  function flapInline(el, text) {
    var out = "", n = 0, target = text;
    (function step() {
      out = target.split("").map(function (c, i) { return i < n || c === " " || c === "-" ? c : CH[Math.floor(Math.random() * 36)]; }).join("");
      el.textContent = out; if (n++ <= target.length) setTimeout(step, 28);
    })();
  }

  /* share my list */
  var sh = $("#share-list");
  if (sh) sh.addEventListener("click", function () {
    if (!WL.length) { toast("Star some games first"); return; }
    var ids = WL.map(function (s) { return G.findIndex(function (g) { return g.slug === s; }); }).filter(function (i) { return i > -1; });
    var url = location.origin + location.pathname + "#list-" + ids.join("-");
    navigator.clipboard.writeText(url).then(function () { toast("Link copied. Send it to a friend!"); }, function () { toast("Copy blocked. Your link: " + url); });
  });

  /* tools: console lineup */
  var cp = $("#console-pick");
  if (cp) {
    var co = $("#console-out");
    var draw = function () {
      var p = cp.value, list = G.filter(function (g) { return g.platforms.indexOf(p) > -1; });
      var tbc = G.filter(function (g) { return !g.platforms.length; });
      co.innerHTML = (list.length ? list.map(function (g) { return '<div class="row"><span>' + g.title + "</span><b>" + (g.date ? g.date.split("-").reverse().slice(0, 2).join("/") : g.window) + "</b></div>"; }).join("") : '<div class="empty">No confirmed games for this console yet.</div>') +
        '<p class="muted" style="margin:6px 0 0;font-size:.9rem">' + tbc.length + " more games haven't confirmed all their platforms yet. We add them as soon as they do.</p>";
    };
    cp.addEventListener("change", draw); draw();
  }
  /* tools: my list countdowns */
  var wo = $("#watch-out");
  var renderWatch = null;
  if (wo) {
    renderWatch = function () {
      var list = G.filter(function (g) { return WL.indexOf(g.slug) > -1; }).sort(function (a, b) { return (at(a) || 9e15) - (at(b) || 9e15); });
      wo.innerHTML = list.length ? list.map(function (g) { var v = g.date ? left(at(g)) : null; return '<div class="row"><span>' + g.title + "</span><b>" + (v ? (at(g) > Date.now() ? v[0] + " days" : "Out now") : g.window) + "</b></div>"; }).join("") : '<div class="empty">Your list is empty. Tap the ☆ next to any game on the board to add it.</div>';
    };
    renderWatch();
  }
  /* tools: month load */
  var ml = $("#month-load");
  if (ml) {
    var names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"], counts = names.map(function () { return 0; });
    G.forEach(function (g) { counts[g.month - 1]++; });
    var max = Math.max.apply(null, counts) || 1;
    ml.innerHTML = names.map(function (m, i) { return '<div style="display:grid;grid-template-columns:44px 1fr 28px;gap:10px;align-items:center;margin-bottom:6px"><span class="mono muted">' + m + '</span><div style="height:12px;background:#0c0d10;border-radius:4px;overflow:hidden"><i style="display:block;height:100%;width:' + (counts[i] / max * 100) + '%;background:#ffc629"></i></div><span class="mono">' + counts[i] + "</span></div>"; }).join("");
  }


  /* clash finder */
  var ct = $("#clash-tool");
  if (ct) {
    var boxes = $$("input[type=checkbox]", ct), gapSel = $("#clash-gap"), cout = $("#clash-out");
    var bySlug = {}; G.forEach(function (g) { bySlug[g.slug] = g; });
    var esc = function (t) { return String(t).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); };
    var fmt = function (g) { var p = g.date.split("-"); return +p[2] + " " + ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"][+p[1] - 1]; };
    var drawClash = function () {
      var gap = +gapSel.value, day = 864e5;
      var pick = boxes.filter(function (b) { return b.checked; }).map(function (b) { return bySlug[b.value]; }).filter(Boolean).sort(function (a, b) { return at(a) - at(b); });
      if (pick.length < 2) { cout.innerHTML = '<div class="empty">Tick at least two games to check for clashes.</div>'; return; }
      var pairs = [];
      for (var i = 0; i < pick.length; i++) for (var j = i + 1; j < pick.length; j++) {
        var d = Math.round((at(pick[j]) - at(pick[i])) / day);
        if (d <= gap) pairs.push([pick[i], pick[j], d]);
      }
      var html = '<div class="row' + (pairs.length ? " hot" : "") + '"><span><strong>' + (pairs.length ? pairs.length + " clash" + (pairs.length > 1 ? "es" : "") + " found" : "No clashes. Nice spacing!") + "</strong></span><b>" + pick.length + " games</b></div>";
      html += pairs.map(function (p) { return '<div class="row hot"><span>' + esc(p[0].title) + " and " + esc(p[1].title) + "</span><b>" + (p[2] === 0 ? "Same day" : p[2] + " day" + (p[2] > 1 ? "s" : "") + " apart") + "</b></div>"; }).join("");
      html += '<div class="row"><span class="muted">Your launch order</span><b>Gap</b></div>';
      html += pick.map(function (g, k) { var d = k ? Math.round((at(g) - at(pick[k - 1])) / day) : null; return '<div class="row"><span>' + esc(g.title) + ' <span class="muted mono">' + fmt(g) + "</span></span><b>" + (d === null ? "First" : d === 0 ? "Same day" : "+" + d + " days") + "</b></div>"; }).join("");
      cout.innerHTML = html;
    };
    var useStars = function () { boxes.forEach(function (b) { b.checked = WL.indexOf(b.value) > -1; }); drawClash(); };
    boxes.forEach(function (b) { b.addEventListener("change", drawClash); });
    gapSel.addEventListener("change", drawClash);
    $("#clash-star").addEventListener("click", function () { useStars(); if (!WL.length) toast("Your ★ list is empty. Star games on the board first."); });
    $("#clash-clear").addEventListener("click", function () { boxes.forEach(function (b) { b.checked = false; }); drawClash(); });
    useStars();
  }

  /* copy page link */
  $$("[data-copy-link]").forEach(function (b) {
    b.addEventListener("click", function () { navigator.clipboard.writeText(location.href.split("#")[0]).then(function () { toast("Link copied"); }, function () { toast("Copy blocked here"); }); });
  });
})();
