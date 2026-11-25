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


  /* backlog planner */
  var bt = $("#bl-tool");
  if (bt) {
    var bopts = $$(".clash-opt", bt), bweek = $("#bl-week"), bstart = $("#bl-start"), bout = $("#bl-out");
    var bBy = {}; G.forEach(function (g) { bBy[g.slug] = g; });
    var besc = function (t) { return String(t).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); };
    var MN = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
    var bfmt = function (ms) { var d = new Date(ms); return d.getDate() + " " + MN[d.getMonth()] + " " + d.getFullYear(); };
    var BK = "dod-bl", saved = store.get(BK, {});
    if (saved.week) bweek.value = saved.week;
    bopts.forEach(function (o) { var cb = $("input[type=checkbox]", o), h = $(".bl-h", o); if (saved.h && saved.h[cb.value]) h.value = saved.h[cb.value]; });
    var save = function () { var h = {}; bopts.forEach(function (o) { var cb = $("input[type=checkbox]", o), hi = $(".bl-h", o); if (+hi.value && +hi.value !== 30) h[cb.value] = +hi.value; }); store.set(BK, { week: +bweek.value || 10, h: h }); };
    var drawBl = function () {
      var per = Math.max(1, Math.min(100, +bweek.value || 10)), day = 864e5;
      var pick = bopts.map(function (o) { var cb = $("input[type=checkbox]", o); return cb.checked ? { g: bBy[cb.value], h: Math.max(1, Math.min(500, +$(".bl-h", o).value || 30)) } : null; })
        .filter(function (x) { return x && x.g; }).sort(function (a, b) { return at(a.g) - at(b.g); });
      save();
      if (!pick.length) { bout.innerHTML = '<div class="empty">Tick at least one game to build your plan.</div>'; return; }
      var t0 = new Date(); t0.setHours(0, 0, 0, 0);
      var cur = bstart.value === "first" ? at(pick[0].g) : t0.getTime(), behind = 0, rows = "", total = 0;
      pick.forEach(function (p, i) {
        var launch = at(p.g), start = Math.max(cur, launch), end = start + Math.ceil(p.h / per * 7) * day;
        total += p.h; cur = end;
        var nx = pick[i + 1], late = nx && end > at(nx.g);
        if (late) behind++;
        var wait = start > launch ? Math.round((start - launch) / day) : 0;
        rows += '<div class="row' + (late ? " hot" : "") + '"><span><strong>' + besc(p.g.title) + '</strong> <span class="muted mono">out ' + bfmt(launch) + "</span><br><span class=\"muted\">" + p.h + " h · start " + bfmt(start) + (wait ? " (" + wait + " days after launch)" : "") +
          (late ? " · still playing when " + besc(nx.g.title) + " launches (" + Math.round((end - at(nx.g)) / day) + " days over)" : "") + "</span></span><b>Done " + bfmt(end) + "</b></div>";
      });
      var head = '<div class="row' + (behind ? " hot" : "") + '"><span><strong>' + (behind ? "You fall behind " + behind + " time" + (behind > 1 ? "s" : "") : "You finish every game before the next one launches") + "</strong><br><span class=\"muted\">" + total + " hours at " + per + " h/week · list clear by " + bfmt(cur) + "</span></span><b>" + pick.length + " game" + (pick.length > 1 ? "s" : "") + "</b></div>";
      bout.innerHTML = head + rows;
    };
    var bUseStars = function () { bopts.forEach(function (o) { var cb = $("input[type=checkbox]", o); cb.checked = WL.indexOf(cb.value) > -1; }); drawBl(); };
    bt.addEventListener("input", drawBl);
    bt.addEventListener("change", drawBl);
    $("#bl-star").addEventListener("click", function () { bUseStars(); if (!WL.length) toast("Your ★ list is empty. Star games on the board first."); });
    $("#bl-clear").addEventListener("click", function () { bopts.forEach(function (o) { $("input[type=checkbox]", o).checked = false; }); drawBl(); });
    var blw = $$("[data-blw]", bt);
    var markW = function () { blw.forEach(function (c) { c.setAttribute("aria-pressed", String(+c.getAttribute("data-blw") === +bweek.value)); }); };
    blw.forEach(function (c) { c.addEventListener("click", function () { bweek.value = c.getAttribute("data-blw"); markW(); drawBl(); }); });
    bweek.addEventListener("input", markW);
    var bbig = $("#bl-big");
    if (bbig) bbig.addEventListener("click", function () { bopts.forEach(function (o) { $("input[type=checkbox]", o).checked = o.hasAttribute("data-big"); }); drawBl(); });
    markW();
    bUseStars();
  }

  /* exclusives: which games will I miss? */
  var mt = $("#miss-tool");
  if (mt) {
    var mchips = $$("[data-own]", mt), mout = $("#miss-out"), PL = ["PS5", "Xbox Series X|S", "PC", "Switch 2"];
    var mesc = function (t) { return String(t).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); };
    var mwhen = function (g) { if (!g.date) return g.window || "TBC"; var p = g.date.split("-"); return +p[2] + " " + ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"][+p[1] - 1]; };
    var KEY = "dod-own";
    var drawMiss = function () {
      var own = mchips.filter(function (c) { return c.getAttribute("aria-pressed") === "true"; }).map(function (c) { return c.getAttribute("data-own"); });
      try { localStorage.setItem(KEY, JSON.stringify(own)); } catch (err) {}
      if (!own.length) { mout.innerHTML = '<div class="empty">Tap at least one console you own.</div>'; return; }
      var can = function (g, list) { return g.platforms.some(function (p) { return list.indexOf(p) > -1; }); };
      var known = G.filter(function (g) { return g.platforms && g.platforms.length; });
      var miss = known.filter(function (g) { return !can(g, own); });
      var html = '<div class="row"><span><strong>You can play ' + (known.length - miss.length) + " of " + known.length + " tracked 2027 games</strong></span><b>" + (miss.length ? miss.length + " missed" : "All of them") + "</b></div>";
      var best = null;
      PL.forEach(function (p) { if (own.indexOf(p) > -1) return; var n = miss.filter(function (g) { return g.platforms.indexOf(p) > -1; }).length; if (n && (!best || n > best[1])) best = [p, n]; });
      if (best) html += '<div class="row"><span>Best extra console for you: <strong>' + mesc(best[0]) + "</strong></span><b>+" + best[1] + " games</b></div>";
      html += miss.map(function (g) { return '<div class="row hot"><span>' + mesc(g.title) + ' <span class="muted">on ' + mesc(g.platforms.join(", ")) + "</span></span><b>" + mesc(mwhen(g)) + "</b></div>"; }).join("");
      mout.innerHTML = html;
    };
    var saved = [];
    try { saved = JSON.parse(localStorage.getItem(KEY) || "[]") || []; } catch (err) {}
    mchips.forEach(function (c) {
      if (saved.indexOf(c.getAttribute("data-own")) > -1) c.setAttribute("aria-pressed", "true");
      c.addEventListener("click", function () { c.setAttribute("aria-pressed", c.getAttribute("aria-pressed") === "true" ? "false" : "true"); drawMiss(); });
    });
    drawMiss();
  }

  /* last-gen 2027: do I need to upgrade? */
  var lt = $("#lg-tool");
  if (lt) {
    var lchips = $$("[data-lg]", lt), lout = $("#lg-out");
    var lesc = function (t) { return String(t).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); };
    var lwhen = function (g) { if (!g.date) return g.window || "TBC"; var p = g.date.split("-"); return +p[2] + " " + ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"][+p[1] - 1]; };
    var lsort = function (a, b) { return (a.month - b.month) || String(a.date || "9999").localeCompare(String(b.date || "9999")); };
    var drawLg = function (chip) {
      lchips.forEach(function (c) { c.setAttribute("aria-pressed", c === chip ? "true" : "false"); });
      if (!chip) { lout.innerHTML = '<div class="empty">Tap the console you have.</div>'; return; }
      var k = chip.getAttribute("data-lg"), nw = chip.getAttribute("data-new"), nm = chip.getAttribute("data-name");
      store.set("dod-lg", k);
      var all = G.filter(function (g) { return g.platforms && g.platforms.length; }).sort(lsort);
      var can = all.filter(function (g) { return (g.lastgen || []).indexOf(k) > -1; });
      var miss = all.filter(function (g) { return (g.lastgen || []).indexOf(k) < 0; });
      var onNew = miss.filter(function (g) { return g.platforms.indexOf(nw) > -1; }).length;
      var html = '<div class="row"><span><strong>' + can.length + " of " + all.length + " tracked 2027 games come to " + lesc(nm) + "</strong></span><b>" + miss.length + " missed</b></div>";
      html += '<div class="row"><span>Upgrading to <strong>' + lesc(nw) + "</strong> adds</span><b>+" + onNew + " games</b></div>";
      html += can.map(function (g) { return '<div class="row"><span>' + lesc(g.title) + ' <span class="muted">also on ' + lesc(g.platforms.join(", ")) + "</span></span><b>" + lesc(lwhen(g)) + "</b></div>"; }).join("");
      var big = miss.filter(function (g) { return g.page; }).slice(0, 8);
      if (big.length) html += '<div class="row hot"><span>You would miss: ' + lesc(big.map(function (g) { return g.title; }).join(", ")) + (miss.length > big.length ? " and more" : "") + "</span><b>" + miss.length + "</b></div>";
      lout.innerHTML = html;
    };
    lchips.forEach(function (c) { c.addEventListener("click", function () { drawLg(c); }); });
    var lsaved = store.get("dod-lg", "");
    drawLg(lchips.filter(function (c) { return c.getAttribute("data-lg") === lsaved; })[0] || null);
  }

  /* RPGs 2027: console + style filter */
  var rt = $("#rpg-tool");
  if (rt) {
    var rplat = "", rsty = "", rrows = $$("#rpg-list [data-rpg-style]"), rcount = $("#rpg-count"), rnone = $("#rpg-none");
    var drawRpg = function () {
      var n = 0;
      rrows.forEach(function (r) {
        var ok = (!rplat || r.getAttribute("data-plat").split("|").indexOf(rplat) > -1) && (!rsty || r.getAttribute("data-rpg-style") === rsty);
        r.hidden = !ok; if (ok) n++;
      });
      $$("#rpg-list .sec-head + .out").forEach(function (box) {
        var any = $$("[data-rpg-style]", box).some(function (r) { return !r.hidden; });
        box.hidden = !any; var h = box.previousElementSibling; if (h && h.querySelector("h3")) h.hidden = !any;
      });
      rcount.textContent = n + " RPG" + (n === 1 ? "" : "s") + (rplat ? " on " + rplat : "");
      rnone.hidden = n > 0;
    };
    var bind = function (attr, set) {
      var cs = $$("[" + attr + "]", rt);
      cs.forEach(function (c) { c.addEventListener("click", function () { cs.forEach(function (x) { x.setAttribute("aria-pressed", x === c ? "true" : "false"); }); set(c.getAttribute(attr)); drawRpg(); }); });
    };
    bind("data-rpg-plat", function (v) { rplat = v; });
    bind("data-rpg-s", function (v) { rsty = v; });
    drawRpg();
  }

  /* 2027 games by genre: genre + console filter */
  var gnt = $("#gen-tool");
  if (gnt) {
    var gsel = store.get("dod-gen", { g: "", p: "" }) || { g: "", p: "" };
    var grows = $$("#gen-list [data-genre]"), gcount = $("#gen-count"), gnone = $("#gen-none");
    var drawGen = function () {
      var n = 0;
      grows.forEach(function (r) {
        var ok = (!gsel.p || r.getAttribute("data-plat").split("|").indexOf(gsel.p) > -1) && (!gsel.g || r.getAttribute("data-genre") === gsel.g);
        r.hidden = !ok; if (ok) n++;
      });
      $$("#gen-list [data-gsec]").forEach(function (sec) {
        sec.hidden = !$$("[data-genre]", sec).some(function (r) { return !r.hidden; });
      });
      $$("[data-gen-g]", gnt).forEach(function (c) { c.setAttribute("aria-pressed", c.getAttribute("data-gen-g") === gsel.g ? "true" : "false"); });
      $$("[data-gen-p]", gnt).forEach(function (c) { c.setAttribute("aria-pressed", c.getAttribute("data-gen-p") === gsel.p ? "true" : "false"); });
      gcount.textContent = n + " game" + (n === 1 ? "" : "s") + (gsel.p ? " on " + gsel.p : "");
      gnone.hidden = n > 0;
      store.set("dod-gen", gsel);
    };
    $$("[data-gen-g]", gnt).forEach(function (c) { c.addEventListener("click", function () { gsel.g = c.getAttribute("data-gen-g"); drawGen(); }); });
    $$("[data-gen-p]", gnt).forEach(function (c) { c.addEventListener("click", function () { gsel.p = c.getAttribute("data-gen-p"); drawGen(); }); });
    drawGen();
  }

  /* Horror games 2027: console + date filter, next launch, add to list */
  var hot = $("#hor-tool");
  if (hot) {
    var hsel = store.get("dod-hor", { p: "", d: "" }) || { p: "", d: "" };
    var hrows = $$("#hor-list [data-hplat]"), hcount = $("#hor-count"), hnone = $("#hor-none"), hnext = $("#hor-next");
    var hesc = function (t) { return String(t).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); };
    var hshown = [];
    var drawHor = function () {
      hshown = [];
      hrows.forEach(function (r) {
        var ok = (!hsel.p || r.getAttribute("data-hplat").split("|").indexOf(hsel.p) > -1) && (!hsel.d || r.getAttribute("data-hdated") === "1");
        r.hidden = !ok; if (ok) hshown.push(r.getAttribute("data-slug"));
      });
      $$("[data-hor-p]", hot).forEach(function (c) { c.setAttribute("aria-pressed", c.getAttribute("data-hor-p") === hsel.p ? "true" : "false"); });
      $$("[data-hor-d]", hot).forEach(function (c) { c.setAttribute("aria-pressed", c.getAttribute("data-hor-d") === hsel.d ? "true" : "false"); });
      hcount.textContent = hshown.length + " horror game" + (hshown.length === 1 ? "" : "s") + (hsel.p ? " on " + hsel.p : "");
      hnone.hidden = hshown.length > 0;
      var now = Date.now(), nx = G.filter(function (g) { return hshown.indexOf(g.slug) > -1 && g.date && at(g) > now; }).sort(function (a, b) { return at(a) - at(b); })[0];
      hnext.innerHTML = nx ? '<div class="row"><span>Next horror launch' + (hsel.p ? " on " + hesc(hsel.p) : "") + ": <strong>" + hesc(nx.title) + "</strong></span><b>" + left(at(nx))[0] + " days</b></div>"
        : '<div class="empty">No dated horror game coming up for this choice yet.</div>';
      store.set("dod-hor", hsel);
    };
    $$("[data-hor-p]", hot).forEach(function (c) { c.addEventListener("click", function () { hsel.p = c.getAttribute("data-hor-p"); drawHor(); }); });
    $$("[data-hor-d]", hot).forEach(function (c) { c.addEventListener("click", function () { hsel.d = c.getAttribute("data-hor-d"); drawHor(); }); });
    var hadd = $("#hor-add");
    if (hadd) hadd.addEventListener("click", function () {
      var before = WL.length;
      WL = Array.from(new Set(WL.concat(hshown))); store.set("dod-watch", WL); syncStars();
      toast((WL.length - before) + " games added to your ★ list");
    });
    drawHor();
  }

  /* Xbox Games Showcase 2027: undated / dated + Game Pass filter, add to list */
  var xst = $("#xs-tool");
  if (xst) {
    var xsel = store.get("dod-xs", { d: "0", gp: "" }) || { d: "0", gp: "" };
    var xrows = $$("#xs-list [data-xsd]"), xcount = $("#xs-count"), xnone = $("#xs-none"), xshown = [];
    var drawXs = function () {
      xshown = [];
      xrows.forEach(function (r) {
        var ok = (xsel.d === "" || r.getAttribute("data-xsd") === xsel.d) && (!xsel.gp || r.getAttribute("data-xsgp") === "1");
        r.hidden = !ok; if (ok) xshown.push(r.getAttribute("data-slug"));
      });
      $$("[data-xs-d]", xst).forEach(function (c) { c.setAttribute("aria-pressed", c.getAttribute("data-xs-d") === xsel.d ? "true" : "false"); });
      $$("[data-xs-gp]", xst).forEach(function (c) { c.setAttribute("aria-pressed", c.getAttribute("data-xs-gp") === xsel.gp ? "true" : "false"); });
      xcount.textContent = xshown.length + " Xbox game" + (xshown.length === 1 ? "" : "s") + (xsel.d === "0" ? " with no exact date" : xsel.d === "1" ? " with a date" : "") + (xsel.gp ? " on Game Pass" : "");
      xnone.hidden = xshown.length > 0;
      store.set("dod-xs", xsel);
    };
    $$("[data-xs-d]", xst).forEach(function (c) { c.addEventListener("click", function () { xsel.d = c.getAttribute("data-xs-d"); drawXs(); }); });
    $$("[data-xs-gp]", xst).forEach(function (c) { c.addEventListener("click", function () { xsel.gp = c.getAttribute("data-xs-gp"); drawXs(); }); });
    var xadd = $("#xs-add");
    if (xadd) xadd.addEventListener("click", function () {
      var before = WL.length;
      WL = Array.from(new Set(WL.concat(xshown))); store.set("dod-watch", WL); syncStars();
      toast((WL.length - before) + " games added to your ★ list");
    });
    drawXs();
  }

  /* Games like GTA 6: platform + taste picker */
  var lkt = $("#like-tool");
  if (lkt) {
    var lsel = store.get("dod-like", { p: "", l: "" }) || { p: "", l: "" };
    var lrows = $$("#like-list [data-lp]"), lcount = $("#like-count"), lnone = $("#like-none");
    var drawLike = function () {
      var n = 0;
      lrows.forEach(function (r) {
        var ok = (!lsel.p || r.getAttribute("data-lp").split(" ").indexOf(lsel.p) > -1) && (!lsel.l || r.getAttribute("data-ll").split(" ").indexOf(lsel.l) > -1);
        r.hidden = !ok; if (ok) n++;
      });
      $$("[data-like-p]", lkt).forEach(function (c) { c.setAttribute("aria-pressed", c.getAttribute("data-like-p") === lsel.p ? "true" : "false"); });
      $$("[data-like-l]", lkt).forEach(function (c) { c.setAttribute("aria-pressed", c.getAttribute("data-like-l") === lsel.l ? "true" : "false"); });
      lcount.textContent = n + " game" + (n === 1 ? "" : "s") + " match";
      lnone.hidden = n > 0;
      store.set("dod-like", lsel);
    };
    $$("[data-like-p]", lkt).forEach(function (c) { c.addEventListener("click", function () { lsel.p = c.getAttribute("data-like-p"); drawLike(); }); });
    $$("[data-like-l]", lkt).forEach(function (c) { c.addEventListener("click", function () { lsel.l = c.getAttribute("data-like-l"); drawLike(); }); });
    drawLike();
  }

  /* Game Pass 2027: Game Pass or buy? */
  var gt = $("#gp-tool");
  if (gt) {
    var gboxes = $$("input[type=checkbox]", gt), gout = $("#gp-out"), gby = {};
    G.forEach(function (g) { gby[g.slug] = g; });
    var gesc = function (t) { return String(t).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); };
    var drawGp = function () {
      var pick = gboxes.filter(function (b) { return b.checked; });
      if (!pick.length) { gout.innerHTML = '<div class="empty">Tick the games you want to see which are on Game Pass.</div>'; return; }
      var inGp = pick.filter(function (b) { return b.getAttribute("data-gp") === "1"; }), buy = pick.filter(function (b) { return b.getAttribute("data-gp") !== "1"; });
      var nm = function (b) { var g = gby[b.value]; return g ? gesc(g.title) : gesc(b.value); };
      var html = '<div class="row"><span><strong>' + inGp.length + " of " + pick.length + " on Game Pass</strong></span><b>" + buy.length + " to buy</b></div>";
      html += inGp.map(function (b) { return '<div class="row"><span>' + nm(b) + "</span><b>Game Pass</b></div>"; }).join("");
      html += buy.map(function (b) { return '<div class="row hot"><span>' + nm(b) + "</span><b>Buy</b></div>"; }).join("");
      gout.innerHTML = html;
    };
    gboxes.forEach(function (b) { b.addEventListener("change", drawGp); });
    var gStars = function () { var wl = store.get("dod-watch", []); if (typeof WL !== "undefined") wl = WL; gboxes.forEach(function (b) { b.checked = wl.indexOf(b.value) > -1; }); drawGp(); return wl.length; };
    $("#gp-star").addEventListener("click", function () { if (!gStars()) toast("Your ★ list is empty. Star games on the board first."); });
    $("#gp-clear").addEventListener("click", function () { gboxes.forEach(function (b) { b.checked = false; }); drawGp(); });
    gStars();
  }

  /* Biggest games 2027: ranked top list you can copy or share by link (?top=slug,slug) */
  var tt = $("#top-tool");
  if (tt) {
    var tboxes = $$("input[type=checkbox]", tt), tout = $("#top-out"), tby = {}, order = [], MAXT = 10;
    G.forEach(function (g) { tby[g.slug] = g; });
    var valid = tboxes.map(function (b) { return b.value; });
    var tesc = function (s) { return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); };
    var MN = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
    var when = function (g) { if (!g.date) return g.window || "2027"; var p = g.date.split("-"); return (+p[2]) + " " + MN[+p[1] - 1] + " " + p[0]; };
    var base = location.origin && location.origin !== "null" ? location.origin + location.pathname : location.href.split("?")[0].split("#")[0];
    var link = function () { return base + (order.length ? "?top=" + order.join(",") : ""); };
    var text = function () {
      return "My top " + order.length + " games of 2027:\n" + order.map(function (s, i) { var g = tby[s]; return (i + 1) + ". " + g.title + " (" + when(g) + ")"; }).join("\n");
    };
    var drawTop = function () {
      tboxes.forEach(function (b) { b.checked = order.indexOf(b.value) > -1; });
      if (!order.length) { tout.innerHTML = '<div class="empty">Tick a game to start your list.</div>'; }
      else {
        var next = null;
        order.forEach(function (s) { var t = at(tby[s]); if (t && t > Date.now() && (!next || t < at(tby[next]))) next = s; });
        tout.innerHTML = order.map(function (s, i) {
          var g = tby[s];
          return '<div class="row"><span><strong>' + (i + 1) + ".</strong> " + tesc(g.title) + '<br><span class="muted">' + tesc((g.platforms || []).join(", ") || "Platforms TBC") + "</span></span><b>" + tesc(when(g)) + "</b></div>";
        }).join("") + (next ? '<div class="row hot"><span>First one out: <strong>' + tesc(tby[next].title) + "</strong></span><b>" + left(at(tby[next]))[0] + " days</b></div>" : "");
      }
      store.set("dod-top", order);
    };
    tboxes.forEach(function (b) {
      b.addEventListener("change", function () {
        var i = order.indexOf(b.value);
        if (b.checked && i < 0) { if (order.length >= MAXT) { b.checked = false; toast("Your top list holds 10 games"); return; } order.push(b.value); }
        if (!b.checked && i > -1) order.splice(i, 1);
        drawTop();
      });
    });
    var copy = function (s, ok) {
      if (!order.length) { toast("Tick some games first"); return; }
      if (navigator.clipboard) navigator.clipboard.writeText(s).then(function () { toast(ok); }, function () { toast("Copy blocked here"); }); else toast("Copy blocked here");
    };
    $("#top-copy").addEventListener("click", function () { copy(text() + "\n" + link(), "List copied"); });
    $("#top-link").addEventListener("click", function () { copy(link(), "Share link copied"); });
    $("#top-clear").addEventListener("click", function () { order = []; drawTop(); });
    $("#top-star").addEventListener("click", function () {
      var wl = store.get("dod-watch", []).filter(function (s) { return valid.indexOf(s) > -1; });
      if (!wl.length) { toast("None of your ★ games are on this list yet"); return; }
      order = wl.slice(0, MAXT); drawTop();
    });
    var q = /[?&]top=([^&#]*)/.exec(location.search), shared = [];
    if (q) { try { shared = decodeURIComponent(q[1]).split(","); } catch (e2) { shared = []; } }
    shared = shared.filter(function (s, i) { return valid.indexOf(s) > -1 && shared.indexOf(s) === i; }).slice(0, MAXT);
    if (shared.length) { order = shared; $("#top-shared").hidden = false; }
    else order = store.get("dod-top", []).filter(function (s) { return valid.indexOf(s) > -1; }).slice(0, MAXT);
    drawTop();
  }

  /* all games filter (games page) */
  var giList = $("#gi-list");
  if (giList) {
    var giRows = $$("[data-gi]", giList), giP = "all", giS = "all", giQ = $("#gi-q");
    var giRun = function () {
      var q = (giQ.value || "").trim().toLowerCase(), n = 0;
      giRows.forEach(function (r) {
        var ok = (giP === "all" || (r.dataset.plat || "").split("|").indexOf(giP) > -1)
          && (giS === "all" || (giS === "delayed" ? r.dataset.st === "delayed" : (giS === "dated") === (r.dataset.dated === "1")))
          && (!q || (r.dataset.q || "").indexOf(q) > -1);
        r.hidden = !ok; if (ok) n++;
      });
      $("#gi-count").textContent = n + (n === 1 ? " game" : " games");
      $("#gi-empty").hidden = n > 0;
    };
    [["#gi-plat", "p"], ["#gi-st", "s"]].forEach(function (pair) {
      $$(pair[0] + " .chip").forEach(function (b) {
        b.addEventListener("click", function () {
          $$(pair[0] + " .chip").forEach(function (x) { x.setAttribute("aria-pressed", "false"); });
          b.setAttribute("aria-pressed", "true");
          if (pair[1] === "p") giP = b.dataset.p; else giS = b.dataset.s;
          giRun();
        });
      });
    });
    giQ.addEventListener("input", giRun);
  }


  /* Game Awards 2026: pick your winners (saved on device, shareable ?a=&g=) */
  var tga = $("#tga-tool");
  if (tga) {
    var TK = "dod-tga-2026", tOut = $("#tga-out"), tPick = store.get(TK, {}) || {};
    var qs = new URLSearchParams(location.search);
    if (qs.get("a") || qs.get("g")) { tPick = { a: qs.get("a") || "", g: qs.get("g") || "" }; $("#tga-shared").hidden = false; }
    if (tPick.g === "Phantom Blade 0") tPick.g = "Phantom Blade Zero";
    var tSet = function () {
      ["a", "g"].forEach(function (k) {
        $$('input[name="tga-' + k + '"]', tga).forEach(function (r) { r.checked = r.value === tPick[k]; });
      });
    };
    var tText = function () {
      return "My Game Awards 2026 picks:\nMost Anticipated Game: " + (tPick.a || "?") + "\nGame of the Year: " + (tPick.g || "?") + "\n";
    };
    var tUrl = function () {
      var u = location.href.split("?")[0].split("#")[0], q = [];
      if (tPick.a) q.push("a=" + encodeURIComponent(tPick.a));
      if (tPick.g) q.push("g=" + encodeURIComponent(tPick.g));
      return u + (q.length ? "?" + q.join("&") : "");
    };
    var tRender = function () {
      if (!tPick.a && !tPick.g) { tOut.innerHTML = '<div class="empty">Pick a game in each category.</div>'; return; }
      tOut.innerHTML = "";
      [["Most Anticipated Game", tPick.a], ["Game of the Year", tPick.g]].forEach(function (r) {
        var d = document.createElement("div"); d.className = "row";
        var a = document.createElement("span"); a.textContent = r[0];
        var b = document.createElement("b"); b.textContent = r[1] || "Not picked";
        d.appendChild(a); d.appendChild(b); tOut.appendChild(d);
      });
    };
    $$('input[type="radio"]', tga).forEach(function (r) {
      r.addEventListener("change", function () {
        tPick[r.name === "tga-a" ? "a" : "g"] = r.value;
        store.set(TK, tPick); tRender();
      });
    });
    var tCopy = function (t, m) { navigator.clipboard.writeText(t).then(function () { toast(m); }, function () { toast("Copy blocked here"); }); };
    $("#tga-copy").addEventListener("click", function () { tCopy(tText() + tUrl(), "Picks copied"); });
    $("#tga-link").addEventListener("click", function () { tCopy(tUrl(), "Link copied"); });
    $("#tga-clear").addEventListener("click", function () { tPick = {}; store.set(TK, tPick); tSet(); tRender(); });
    tSet(); tRender();
  }

  /* December 2026: console filter + out-now marks */
  var dct = $("#dec-tool");
  if (dct) {
    var dp = store.get("dod-dec", ""), drows = $$("#dec-list [data-dec-date]"), dnow = new Date(), dpad = function (n) { return (n < 10 ? "0" : "") + n; };
    var dtoday = dnow.getFullYear() + "-" + dpad(dnow.getMonth() + 1) + "-" + dpad(dnow.getDate());
    $$("[data-dec-date]").forEach(function (r) {
      if (r.getAttribute("data-dec-date") <= dtoday) { var w = $(".dec-when", r); if (w) w.textContent = "Out now"; }
    });
    var drawDec = function () {
      var n = 0, next = null;
      drows.forEach(function (r) {
        var ok = !dp || (dp === "big" ? r.hasAttribute("data-big") : r.getAttribute("data-plat").split("|").indexOf(dp) > -1);
        r.hidden = !ok; r.classList.remove("hot");
        if (ok) { n++; if (!next && r.getAttribute("data-dec-date") > dtoday) next = r; }
      });
      if (next) next.classList.add("hot");
      $$("[data-dec-p]", dct).forEach(function (c) { c.setAttribute("aria-pressed", c.getAttribute("data-dec-p") === dp ? "true" : "false"); });
      $("#dec-count").textContent = n + " game" + (n === 1 ? "" : "s") + (dp && dp !== "big" ? " on " + dp : "");
      var nx = $("#dec-next");
      if (next) {
        var days = Math.round((new Date(next.getAttribute("data-dec-date") + "T00:00:00") - new Date(dtoday + "T00:00:00")) / 864e5);
        nx.textContent = "Next up: " + $("strong", next).textContent + " in " + days + " day" + (days === 1 ? "" : "s") + ".";
      } else nx.textContent = dtoday > "2026-12-31" ? "December 2026 is over. See January 2027 below." : "Everything on this list is out now.";
      $("#dec-none").hidden = n > 0;
    };
    $$("[data-dec-p]", dct).forEach(function (c) { c.addEventListener("click", function () { dp = c.getAttribute("data-dec-p"); store.set("dod-dec", dp); drawDec(); }); });
    drawDec();
  }

  /* month pages: console filter, next launch, add matches to the star list */
  var mot = $("#mo-tool");
  if (mot) {
    var mp = store.get("dod-mo", ""), mrows = $$("#mo-list [data-mo-slug]"), mshown = [];
    var drawMo = function () {
      mshown = []; var now = Date.now(), nx = null, nxd = 0;
      mrows.forEach(function (r) {
        var ok = !mp || (mp === "big" ? r.hasAttribute("data-mo-big") : r.getAttribute("data-mo-plat").split("|").indexOf(mp) > -1);
        r.hidden = !ok; r.classList.remove("hot");
        if (ok) {
          mshown.push(r.getAttribute("data-mo-slug"));
          var ds = r.getAttribute("data-mo-date"), t = ds ? at({ date: ds }) : 0;
          if (t && t > now && (!nx || t < nxd)) { nx = r; nxd = t; }
        }
      });
      if (nx) nx.classList.add("hot");
      $$("[data-mo-p]", mot).forEach(function (c) { c.setAttribute("aria-pressed", c.getAttribute("data-mo-p") === mp ? "true" : "false"); });
      $("#mo-count").textContent = mshown.length + " game" + (mshown.length === 1 ? "" : "s") + (mp && mp !== "big" ? " on " + mp : mp === "big" ? " (big releases)" : "");
      $("#mo-next").textContent = nx ? "First up: " + $("strong", nx).textContent + " in " + left(nxd)[0] + " days." : (mshown.length ? "No upcoming exact date in this list." : "");
      $("#mo-none").hidden = mshown.length > 0;
      $("#mo-add").disabled = !mshown.length;
    };
    $$("[data-mo-p]", mot).forEach(function (c) { c.addEventListener("click", function () { mp = c.getAttribute("data-mo-p"); store.set("dod-mo", mp); drawMo(); }); });
    $("#mo-add").addEventListener("click", function () {
      var before = WL.length;
      WL = Array.from(new Set(WL.concat(mshown))); store.set("dod-watch", WL); syncStars();
      toast((WL.length - before) + " games added to your ★ list");
    });
    drawMo();
  }

  /* copy page link */
  $$("[data-copy-link]").forEach(function (b) {
    b.addEventListener("click", function () { navigator.clipboard.writeText(location.href.split("#")[0]).then(function () { toast("Link copied"); }, function () { toast("Copy blocked here"); }); });
  });

  /* new games this week: live week labels, console filter */
  var wkt = $("#wk-tool");
  if (wkt) {
    var wp = store.get("dod-wk", ""), wnow = new Date(), wpad = function (n) { return (n < 10 ? "0" : "") + n; };
    var wiso = function (d) { return d.getFullYear() + "-" + wpad(d.getMonth() + 1) + "-" + wpad(d.getDate()); };
    var wtoday = wiso(wnow), wmon = new Date(wnow.getFullYear(), wnow.getMonth(), wnow.getDate() - ((wnow.getDay() + 6) % 7));
    var wthis = wiso(wmon), wnext = wiso(new Date(wmon.getFullYear(), wmon.getMonth(), wmon.getDate() + 7));
    var wblocks = $$("#wk-list .wk");
    $$("[data-wk-date]").forEach(function (r) { if (r.getAttribute("data-wk-date") <= wtoday) { var w = $(".wk-when", r); if (w) w.textContent = "Out now"; } });
    var wnames = function (all) { var big = all.filter(function (r) { return r.hasAttribute("data-big"); }), rows = big.length ? big : all; return rows.slice(0, 4).map(function (r) { return $("strong", r).textContent; }).join(", ") + (all.length > Math.min(4, rows.length) ? " and " + (all.length - Math.min(4, rows.length)) + " more" : ""); }, _wn = function (rows) { return rows.slice(0, 4).map(function (r) { return $("strong", r).textContent; }).join(", ") + (rows.length > 4 ? " and " + (rows.length - 4) + " more" : ""); };
    var drawWk = function () {
      var next = null, thisRows = [], nextRows = [];
      wblocks.forEach(function (b) {
        var st = b.getAttribute("data-wk-start"), en = b.getAttribute("data-wk-end"), n = 0;
        b.hidden = en < wtoday;
        var lbl = $(".wk-lbl", b); if (lbl) lbl.textContent = st === wthis ? "This week · " : st === wnext ? "Next week · " : "";
        $$("[data-wk-date]", b).forEach(function (r) {
          var ok = !wp || (wp === "big" ? r.hasAttribute("data-big") : r.getAttribute("data-plat").split("|").indexOf(wp) > -1);
          r.hidden = !ok; r.classList.remove("hot");
          if (ok) {
            n++;
            if (!next && r.getAttribute("data-wk-date") > wtoday) next = r;
            if (st === wthis && r.getAttribute("data-wk-date") >= wtoday) thisRows.push(r);
            if (st === wnext) nextRows.push(r);
          }
        });
        var nn = $(".wk-n", b); if (nn) nn.textContent = n;
        var none = $(".wk-none", b); if (none) none.hidden = n > 0 || !$("[data-wk-date]", b);
      });
      if (next) next.classList.add("hot");
      $$("[data-wk-p]", wkt).forEach(function (c) { c.setAttribute("aria-pressed", c.getAttribute("data-wk-p") === wp ? "true" : "false"); });
      var on = wp && wp !== "big" ? " on " + wp : wp === "big" ? " (big releases)" : "";
      $("#wk-count").textContent = "This week: " + thisRows.length + " left" + on + " · Next week: " + nextRows.length;
      var nx = $("#wk-next");
      if (next) {
        var days = Math.round((new Date(next.getAttribute("data-wk-date") + "T00:00:00") - new Date(wtoday + "T00:00:00")) / 864e5);
        nx.textContent = "Next up: " + $("strong", next).textContent + " in " + days + " day" + (days === 1 ? "" : "s") + ".";
      } else nx.textContent = "Nothing else is dated yet for that choice.";
      var q = $("#wk-quick");
      if (q && !wp) q.textContent = (thisRows.length ? "This week " + thisRows.length + " tracked game" + (thisRows.length === 1 ? " still comes" : "s still come") + " out: " + wnames(thisRows) + "." : "No tracked games come out for the rest of this week.") +
        (nextRows.length ? " Next week brings " + nextRows.length + ": " + wnames(nextRows) + "." : " Next week has no tracked launches.");
    };
    $$("[data-wk-p]", wkt).forEach(function (c) { c.addEventListener("click", function () { wp = c.getAttribute("data-wk-p"); store.set("dod-wk", wp); drawWk(); }); });
    drawWk();
  }
})();

/* Game Awards nominee search (25 Nov 2026) */
(function () {
  var box = document.getElementById("tga-find");
  if (!box) return;
  var q = document.getElementById("tga-q"), out = document.getElementById("tga-find-out");
  var cats = Array.prototype.slice.call(box.querySelectorAll(".tga-cat"));
  var base = out.textContent;
  function run() {
    var t = (q.value || "").trim().toLowerCase(), shown = 0;
    cats.forEach(function (c) {
      var rows = Array.prototype.slice.call(c.querySelectorAll(".row")), hit = 0;
      rows.forEach(function (r) {
        var m = !t || (r.getAttribute("data-n") || "").indexOf(t) > -1;
        r.classList.toggle("hot", !!t && m);
        r.hidden = !!t && !m;
        if (m) hit++;
      });
      c.hidden = !!t && !hit;
      if (t && hit) shown++;
    });
    out.textContent = !t ? base : (shown ? "Found in " + shown + " categor" + (shown === 1 ? "y" : "ies") + "." : "No nominee matches that. Check the spelling or try part of the name.");
  }
  q.addEventListener("input", run);
})();
