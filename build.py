#!/usr/bin/env python3
"""Builds DayOneDrop. Run `python3 build.py` for the live site (clean URLs) or `python3 build.py --preview` for local files."""
import json, html, pathlib, sys, hashlib, datetime, collections
import pathlib as _pl, sys as _sy
_sy.path.insert(0, str(_pl.Path(__file__).resolve().parent / "tools"))
from og import og_image

ROOT = pathlib.Path(__file__).resolve().parent
DOMAIN = "https://getdayonedrop.com"
ADSENSE_CLIENT = "ca-pub-1558743317014653"  # AdSense publisher ID
GA_ID = "G-2NJQ0RSMTP"                # Google Analytics measurement ID
SITE = "DayOneDrop"
PREVIEW = "--preview" in sys.argv
DATA = json.loads((ROOT / "assets" / "games.json").read_text())
GAMES = DATA["games"]
UPDATED = DATA["updated"]
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
PLATS = ["PS5", "Xbox Series X|S", "PC", "Switch 2"]
PLAT_PAGES_FOOT = [("PS5", "ps5", "PS5"), ("Xbox Series X|S", "xbox-series", "Xbox Series X|S"), ("PC", "pc", "PC"), ("Switch 2", "switch-2", "Nintendo Switch 2")]
e = html.escape


def v(name):
    return hashlib.md5((ROOT / "assets" / name).read_bytes()).hexdigest()[:8]


def href(page, depth):
    """Link to another page. Live: clean absolute URLs. Preview: relative .html files."""
    if PREVIEW:
        return ("../" * depth) + page
    if page == "index.html":
        return "/"
    return "/" + page[:-5]


def canon(page):
    return DOMAIN + ("/" if page == "index.html" else "/" + page[:-5])


_INLINE_CSS = (pathlib.Path(__file__).resolve().parent / "assets" / "style.css").read_text()

def asset(name, depth):
    return ("../" * depth if PREVIEW else "/") + "assets/" + name + "?v=" + v(name)


def nice_date(g):
    if not g["date"]:
        return g["window"]
    d = datetime.date.fromisoformat(g["date"])
    return f"{d.day} {MONTHS[d.month - 1]} {d.year}"


def short_date(g):
    if not g["date"]:
        return g["window"].upper()
    d = datetime.date.fromisoformat(g["date"])
    return f"{d.day:02d} {MONTHS[d.month - 1][:3].upper()}"



def _plat_short(g):
    m = {"PS5": "PS5", "Xbox Series X|S": "Xbox", "PC": "PC", "Switch 2": "Switch 2", "Switch": "Switch", "PS4": "PS4", "Xbox One": "Xbox One"}
    ps = [m.get(p, p) for p in (g.get("platforms") or [])]
    ps = list(dict.fromkeys(ps))
    return ", ".join(ps[:3]) + (" +more" if len(ps) > 3 else "")


def _us_date(g):
    if not g["date"]:
        return g["window"]
    d = datetime.date.fromisoformat(g["date"])
    return f"{MONTHS[d.month - 1][:3]} {d.day}, {d.year}"


def _ctr_title(g):
    # CTR rewrite 25 Nov 2026: the date itself in the title (searchers want the answer), platforms in brackets.
    ps = _plat_short(g)
    t = f"{g['title']} Release Date: {_us_date(g)}" + (f" ({ps})" if ps else "")
    if len(t) > 62:
        t = f"{g['title']} Release Date: {_us_date(g)}"
    if len(t) > 62:
        t = f"{g['title']} Release Date"
    return t


def _ctr_desc(g):
    lead = (f"{g['title']} comes out {nice_date(g)}" + (f" on {plat_text(g)}" if g.get("platforms") else "") + ".")
    tail = " Delayed once: full date history." if g["status"] == "delayed" else " Live countdown, date history and a free calendar reminder."
    return lead + tail

def tile_color(slug):
    h = int(hashlib.md5(slug.encode()).hexdigest()[:6], 16)
    palette = ["#ffc629", "#6ec1ff", "#ff8f5e", "#b9f27c", "#ff6fa3", "#c7a6ff"]
    return palette[h % len(palette)]


def gcal(g):
    if not g["date"]:
        return ""
    d = datetime.date.fromisoformat(g["date"])
    nxt = d + datetime.timedelta(days=1)
    from urllib.parse import quote
    return ("https://calendar.google.com/calendar/render?action=TEMPLATE&text=" + quote(g["title"] + " launches")
            + f"&dates={d:%Y%m%d}/{nxt:%Y%m%d}&details=" + quote("Release day reminder from DayOneDrop. Dates can change, check getdayonedrop.com for the latest."))


def ics(g):
    if not g["date"]:
        return ""
    d = datetime.date.fromisoformat(g["date"])
    nxt = d + datetime.timedelta(days=1)
    from urllib.parse import quote
    body = "\r\n".join(["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//DayOneDrop//EN", "BEGIN:VEVENT",
                        f"UID:{g['slug']}@dayonedrop", f"DTSTAMP:{UPDATED.replace('-', '')}T000000Z",
                        f"DTSTART;VALUE=DATE:{d:%Y%m%d}", f"DTEND;VALUE=DATE:{nxt:%Y%m%d}",
                        f"SUMMARY:{g['title']} launches", "END:VEVENT", "END:VCALENDAR"])
    return "data:text/calendar;charset=utf-8," + quote(body)


def plat_text(g):
    return ", ".join(g["platforms"]) if g["platforms"] else "TBC"


def status_html(g):
    lab = {"dated": "ON TIME", "delayed": "DELAYED", "window": "SCHEDULED"}[g["status"]]
    return f'<span class="stat {g["status"]}">{lab}</span>'


AD = '<div class="ad-slot" data-ad="{}"><!-- AdSense ad unit goes here --></div>'
NAV = [("index.html", "Departures"), ("calendar.html", "2027 Calendar"), ("games.html", "All games"), ("tools.html", "Tools")]


MONTH_SLUGS = [m.lower() + "-2027" for m in MONTHS]
def month_pages_list():
    return [m for m in range(1, 13) if sum(1 for g in GAMES if g["month"] == m and (g["date"] or (g["window"] and g["window"] != "2027"))) >= 3]


def month_foot(depth):
    return "".join(f'<li><a href="{href("months/" + MONTH_SLUGS[m - 1] + ".html", depth)}">{MONTHS[m - 1]} 2027 games</a></li>' for m in month_pages_list()[:4])


def plat_foot(depth):
    return "".join(f'<li><a href="{href("platforms/" + s2 + ".html", depth)}">{e(l2)} games</a></li>' for p2, s2, l2 in PLAT_PAGES_FOOT)


def faq_block(faqs):
    if not faqs:
        return ""
    items = "".join(f"<details><summary>{e(q)}</summary><p>{e(a)}</p></details>" for q, a in faqs)
    return f'<section class="faq"><div class="wrap"><h2>Questions players ask</h2>{items}</div></section>'


# ---- Email signup (Kit form 10215426). Sign-ups go to Kit; Kit redirects to /thanks, then /welcome after confirming. ----
NL_SKIP = ("thanks.html", "welcome.html", "404.html", "privacy.html")
NOINDEX = ("thanks.html", "welcome.html", "404.html")
def signup(file):
    if file in NL_SKIP:
        return ""
    return """<section class="nl" id="newsletter"><div class="wrap"><div class="nl-card">
<div><h2>Get the 2027 release calendar</h2><p>All the 2027 games we track, month by month, as a free printable calendar. Plus a short weekly email when a date moves or a new game gets dated.</p></div>
<form class="nl-form" action="https://app.kit.com/forms/10215426/subscriptions" method="post">
<label class="nl-sr" for="nl-email">Email address</label>
<input id="nl-email" type="email" name="email_address" required placeholder="Your email address" autocomplete="email">
<button type="submit">Send my calendar</button>
</form>
<p class="nl-fine">Free. No spam, unsubscribe in one click. See our <a href="/privacy.html">privacy policy</a>.</p>
</div></div></section>"""
NL_THANKS = """<section><div class="wrap nl-done"><h1>Check your inbox</h1>
<p>We've just emailed you a confirmation link. Tap the button in that email and your 2027 game release calendar opens straight away.</p>
<p>Can't see it after a minute? Look in your spam or promotions folder.</p>
<div class="nl-links"><a href="/calendar">Release calendar</a><a href="/games">All 2027 games</a><a href="/tools">Launch list tools</a></div></div></section>"""
NL_WELCOME = """<section><div class="wrap nl-done"><h1>You're in!</h1>
<p>Thanks for confirming. Here's your 2027 game release calendar:</p>
<a class="nl-btn" href="/assets/free/2027-game-release-calendar.pdf" download>Download the PDF</a>
<p>We'll email you when there's something worth knowing, never more than once a week.</p>
<div class="nl-links"><a href="/calendar">Release calendar</a><a href="/games">All 2027 games</a><a href="/tools">Launch list tools</a></div></div></section>"""


from urllib.parse import quote_plus as _qp
AFF = {}
def amz_slug(g):
    """Registers /go/amz-<slug> -> Amazon search for the game on its first console platform."""
    plat = next((x for x in g.get("platforms") or [] if x != "PC"), "")
    AFF["amz-" + g["slug"]] = "https://www.amazon.com/s?k=" + _qp((g["title"] + " " + plat).strip()) + "&i=videogames&tag=purlandpaper-20"
    return "amz-" + g["slug"]
# ---- Affiliate links. Pages link to /go/<slug>; _redirects sends it to the store.
# Until a programme approves us these are plain store URLs; when approved, replace the URL with the tracked link and rebuild.
AFF_ATTR = 'rel="sponsored nofollow noopener" target="_blank"'
AFF_NOTE = '<p class="aff-note">We may earn a commission if you buy through these links, at no extra cost to you. As an Amazon Associate we earn from qualifying purchases.</p>'
def go(slug): return "/go/" + slug
def write_redirects(root):
    lines = "".join(f"/go/{k} {v} 302\n" for k, v in AFF.items())
    _retired = "".join(f"/months/{m}-2027 /later-2027 301\n/months/{m}-2027.html /later-2027 301\n" for m in [x.lower() for x in MONTHS] if (MONTHS.index(m.capitalize()) + 1) not in month_pages_list())
    (root / "_redirects").write_text(_retired + lines)


def page(file, title, desc, body, depth=0, faqs=None, crumbs=None, extra_ld=None):
    _og = og_image(file, title, DOMAIN)
    url = canon(file)
    ld = [{"@context": "https://schema.org", "@type": "WebPage", "name": title, "description": desc, "url": url,
           "dateModified": UPDATED, "isPartOf": {"@type": "WebSite", "name": SITE, "url": DOMAIN + "/"}}]
    if crumbs:
        ld.append({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": n, "item": u} for i, (n, u) in enumerate(crumbs)]})
    if faqs:
        ld.append({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs]})
    if extra_ld:
        ld.append(extra_ld)
    ga = ""
    if GA_ID:
        ga = f'<script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script><script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag("js",new Date());gtag("config","{GA_ID}");</script>'
    nav = "".join(f'<li><a href="{href(f, depth)}"{" aria-current=\"page\"" if f == file else ""}>{n}</a></li>' for f, n in NAV)
    tick = "".join(f"<span><b>{e(short_date(g))}</b> {e(g['title'].upper())}</span>" for g in GAMES)
    doc = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
{ga}
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="msvalidate.01" content="215145BE38DEE30C2985F40FB4D4041F">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{url}">
<meta name="robots" content="{"noindex, follow" if file in NOINDEX else "index, follow, max-image-preview:large"}">
<meta property="og:type" content="website"><meta property="og:site_name" content="{SITE}">
<meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}"><meta property="og:url" content="{url}">
<meta property="og:image" content="{_og}"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta name="twitter:card" content="summary_large_image"><meta name="twitter:image" content="{_og}">
<meta name="theme-color" content="#0c0d10">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='6' fill='%230c0d10'/%3E%3Crect x='5' y='7' width='9' height='18' rx='2' fill='%2323272f'/%3E%3Crect x='18' y='7' width='9' height='18' rx='2' fill='%23ffc629'/%3E%3Crect x='4' y='15.5' width='24' height='1' fill='%23000'/%3E%3C/svg%3E">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;700;800;900&family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet" media="print" onload="this.media='all'"><noscript><link href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;700;800;900&family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet"></noscript>
<style>{_INLINE_CSS}</style>
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={ADSENSE_CLIENT}" crossorigin="anonymous"></script>
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
</head>
<body>
<nav class="topbar" aria-label="Main"><div class="wrap">
<a class="logo" href="{href("index.html", depth)}"><span class="logo-mark" aria-hidden="true"><i></i><i></i><i></i></span>DayOne<b>Drop</b></a>
<button class="menu-btn" type="button" aria-expanded="false" aria-controls="links">Menu</button>
<ul class="links" id="links">{nav}</ul>
</div></nav>
<div class="ticker" aria-hidden="true"><div class="ticker-run">{tick}{tick}</div></div>
<main>
{body}
{faq_block(faqs)}
{signup(file)}
{AD.format(file + "-bottom")}
</main>
<footer><div class="wrap">
<div class="foot">
<div><a class="logo" href="{href("index.html", depth)}"><span class="logo-mark" aria-hidden="true"><i></i><i></i><i></i></span>DayOne<b>Drop</b></a>
<p style="margin-top:12px">Every big game launch of 2027 in one place: release dates, platforms, delays and countdowns, checked against official news.</p></div>
<div><strong>Browse</strong><ul>{"".join(f'<li><a href="{href(f, depth)}">{n}</a></li>' for f, n in NAV)}</ul></div>
<div><strong>By console</strong><ul>{plat_foot(depth)}</ul></div>
<div><strong>By month</strong><ul>{month_foot(depth)}</ul></div>
<div><strong>Site</strong><ul><li><a href="{href("new-games-this-week.html", depth)}">New games this week</a></li><li><a href="{href("later-2027.html", depth)}">Games later in 2027 (May–Dec)</a></li><li><a href="{href("games-without-release-date-2027.html", depth)}">2027 games with no release date</a></li><li><a href="{href("countdown.html", depth)}">Game release countdown</a></li><li><a href="{href("games-december-2026.html", depth)}">Games coming out in December 2026</a></li><li><a href="{href("biggest-games-2027.html", depth)}">Biggest games of 2027</a></li><li><a href="{href("after-gta-6.html", depth)}">What to play after GTA 6</a></li><li><a href="{href("games-like-gta-6.html", depth)}">Games like GTA 6</a></li><li><a href="{href("games-like-elden-ring.html", depth)}">Games like Elden Ring</a></li><li><a href="{href("delayed-games-2027.html", depth)}">Delayed games of 2027</a></li><li><a href="{href("release-clashes-2027.html", depth)}">2027 release clashes</a></li><li><a href="{href("exclusives-2027.html", depth)}">2027 console exclusives</a></li><li><a href="{href("rpgs-2027.html", depth)}">Every RPG of 2027</a></li><li><a href="{href("games-by-genre-2027.html", depth)}">2027 games by genre</a></li><li><a href="{href("horror-games-2027.html", depth)}">Horror games of 2027</a></li><li><a href="{href("fighting-games-2027.html", depth)}">Fighting games of 2027</a></li><li><a href="{href("game-awards-2026.html", depth)}">Game Awards 2026: 2027 nominees</a></li><li><a href="{href("games/resident-evil-veronica.html", depth)}">Resident Evil Veronica</a></li><li><a href="{href("games/kirby-and-the-world-beyond.html", depth)}">Kirby and the World Beyond</a></li><li><a href="{href("games/xenoblade-genesis.html", depth)}">Xenoblade Genesis</a></li><li><a href="{href("games/the-duskbloods.html", depth)}">The Duskbloods</a></li><li><a href="{href("games/state-of-decay-3.html", depth)}">State of Decay 3</a></li><li><a href="{href("games/lords-of-the-fallen-ii.html", depth)}">Lords of the Fallen 2</a></li><li><a href="{href("games/squadron-42.html", depth)}">Squadron 42</a></li><li><a href="{href("games/ananta.html", depth)}">Ananta (free-to-play)</a></li><li><a href="{href("games/titan-quest-ii.html", depth)}">Titan Quest II</a></li><li><a href="{href("games/warhammer-40-000-dark-heresy.html", depth)}">Warhammer 40K: Dark Heresy</a></li><li><a href="{href("game-pass-2027.html", depth)}">Xbox Game Pass 2027</a></li><li><a href="{href("ps-plus-monthly-games.html", depth)}">PS Plus monthly games</a></li><li><a href="{href("epic-free-games.html", depth)}">Epic free games this week</a></li><li><a href="{href("steam-sale-dates.html", depth)}">Steam sale dates 2026-2027</a></li><li><a href="{href("movies-2027.html", depth)}">Upcoming movies 2027</a></li><li><a href="{href("nintendo-direct.html", depth)}">Next Nintendo Direct</a></li><li><a href="{href("xbox-games-showcase-2027.html", depth)}">Xbox Games Showcase 2027</a></li><li><a href="{href("backlog-planner-2027.html", depth)}">2027 backlog planner</a></li><li><a href="{href("last-gen-games-2027.html", depth)}">2027 games on PS4 and Switch 1</a></li><li><a href="{href("games/hyrule-warriors-age-of-calamity-definitive-edition.html", depth)}">Hyrule Warriors: Age of Calamity DE</a></li><li><a href="{href("games/final-fantasy-xiv-evercold.html", depth)}">FFXIV Evercold</a></li><li><a href="{href("games/spyro-a-realm-beyond.html", depth)}">Spyro: A Realm Beyond</a></li><li><a href="{href("games/007-first-light.html", depth)}">007 First Light on Switch 2</a></li><li><a href="{href("games/kingdom-hearts-iv.html", depth)}">Kingdom Hearts 4</a></li><li><a href="{href("games/danganronpa-2x2.html", depth)}">Danganronpa 2x2</a></li><li><a href="{href("games/pokemon-winds-and-waves.html", depth)}">Pokémon Winds and Waves</a></li><li><a href="{href("games/stranger-than-heaven.html", depth)}">Stranger Than Heaven</a></li><li><a href="https://neoncoast.org" rel="noopener">GTA 6 map and guides (NeonCoast)</a></li><li><a href="{href("about.html", depth)}">About and contact</a></li><li><a href="{href("privacy.html", depth)}">Privacy policy</a></li></ul></div>
</div>
<p class="legal">DayOneDrop is an independent fan site and is not linked to any game publisher. Game names belong to their owners. Every date is checked against the publisher or platform holder plus a second trusted source (<a href="{href("about.html", depth)}#editorial">editorial policy</a>). Spotted an error? Email <a href="mailto:awaiskaramat@hotmail.com">awaiskaramat@hotmail.com</a>. Last checked {e(UPDATED)}.</p>
</div></footer>
<script>window.DOD={json.dumps({"games": [{k: g.get(k) for k in ("slug","title","platforms","date","window","month","page")} for g in GAMES]}, ensure_ascii=False, separators=(",", ":"))};</script>
<script src="{asset("app.js", depth)}"></script>
</body>
</html>
'''
    out = ROOT / file
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(doc, encoding="utf-8")


def board_rows(depth):
    rows = []
    for g in GAMES:
        t = f'<a href="{href("games/" + g["slug"] + ".html", depth)}">{e(g["title"])}</a>' if g["page"] else e(g["title"])
        rows.append(f'''<tr data-slug="{g["slug"]}" data-plat="{e("|".join(g["platforms"]))}">
<td><button class="star" type="button" data-slug="{g["slug"]}" data-name="{e(g["title"])}" aria-pressed="false">☆</button></td>
<td class="d"><span>{e(short_date(g))}</span></td><td class="t">{t}</td><td class="p">{e(plat_text(g))}</td>
<td class="tminus">--</td><td>{status_html(g)}</td></tr>''')
    return "".join(rows)


def board(depth, title="DEPARTURES · 2027"):
    chips = '<button class="chip" type="button" data-p="all" aria-pressed="true">All</button>' + "".join(
        f'<button class="chip" type="button" data-p="{e(p)}" aria-pressed="false">{e(p)}</button>' for p in PLATS) + \
        '<button class="chip" type="button" data-p="watch" aria-pressed="false">★ My list (<span data-wl-count>0</span>)</button>'
    return f'''<div class="board" id="board">
<div class="board-top"><span class="board-title">{title}</span><div class="chips" id="plat-chips" role="group" aria-label="Filter by platform">{chips}</div><span class="clock" data-clock></span></div>
<div class="board-scroll"><table class="dep"><thead><tr><th><span class="sr-only">Save</span></th><th>Date</th><th>Game</th><th>Platforms</th><th>Countdown</th><th>Status</th></tr></thead>
<tbody>{board_rows(depth)}</tbody></table></div>
<p class="empty" id="board-empty" hidden style="margin:14px">No games here yet. Tap ☆ on any game to build your list.</p>
</div>'''


def pass_card(g, depth):
    code = "".join(w[0] for w in g["title"].replace(":", "").split()[:3]).upper()
    target = href("games/" + g["slug"] + ".html", depth)
    return f'''<a class="pass" href="{target}"><span class="code">FLIGHT {e(code)}-27 · {e(g["genre"].upper())}</span>
<div class="tile" style="background:{tile_color(g["slug"])}" aria-hidden="true">{e(code)}</div>
<h3>{e(g["title"])}</h3><span class="big">{e(short_date(g))}</span><span class="muted">{e(plat_text(g))}</span>{status_html(g)}
<span class="stub" aria-hidden="true">BOARDING PASS</span></a>'''


# ---------------- HOME ----------------
featured = [g for g in GAMES if g["page"]]
def _hlink(g):
    return f'<a href="{href("games/" + g["slug"] + ".html", 0)}">{e(g["title"])}</a>' if g["page"] else e(g["title"])
_h_dated = sorted([g for g in GAMES if g["date"] and g["date"] >= UPDATED], key=lambda g: g["date"])
_h_next = _h_dated[:6]
_h_mc = [sum(1 for g in GAMES if g["date"] and g["month"] == m) for m in range(1, 13)]
_h_busy = max(range(12), key=lambda i: _h_mc[i])
_h_delayed = [g for g in GAMES if g["status"] == "delayed"]
_h_undated = [g for g in GAMES if not g["date"]]
_h_quick = (f"We track {len(GAMES)} games launching in 2027. The first is {_h_next[0]['title']} on {nice_date(_h_next[0])}" if _h_next else f"We track {len(GAMES)} games launching in 2027")
_h_quick += (f". {MONTHS[_h_busy]} is the busiest month with {_h_mc[_h_busy]} dated launches, {len(_h_delayed)} games have been delayed and "
             f"{len(_h_undated)} still have only a season or year.")
_h_plat = [(p, sl, lg, sum(1 for g in GAMES if p in g["platforms"])) for p, sl, lg in PLAT_PAGES_FOOT]
_h_section = (f'<section><div class="wrap">'
    f'<div class="out" style="margin-bottom:24px"><div class="row"><span><strong>Quick answer:</strong> {e(_h_quick)}</span></div></div>'
    f'<p class="muted" style="margin:0 0 18px">Last checked {e(UPDATED)}</p>'
    f'<div class="cols"><div><h2>What are the next games to come out?</h2><div class="out">'
    + "".join(f'<div class="row"><span>{_hlink(g)} <span class="muted">· {e(plat_text(g))}</span></span><b>{e(short_date(g))}</b></div>' for g in _h_next)
    + f'</div></div><div><h2>How many 2027 games are on my console?</h2><div class="out">'
    + "".join(f'<div class="row"><span><a href="{href("platforms/" + sl + ".html", 0)}">{e(lg)}</a></span><b>{n} games</b></div>' for p, sl, lg, n in _h_plat)
    + f'<div class="row"><span><a href="{href("months/" + MONTH_SLUGS[_h_busy] + ".html", 0) if (_h_busy + 1) in month_pages_list() else href("calendar.html", 0)}">Busiest month: {MONTHS[_h_busy]} 2027</a></span><b>{_h_mc[_h_busy]} games</b></div>'
    + f'<div class="row"><span><a href="{href("delayed-games-2027.html", 0)}">Delayed so far</a></span><b>{len(_h_delayed)} games</b></div>'
    + '</div></div></div></div></section>')
_h_related = (f'<section><div class="wrap"><div class="sec-head"><h2>Which tools help me plan 2027?</h2></div><ul>'
    f'<li><a href="{href("biggest-games-2027.html", 0)}">The biggest games of 2027, with a shareable top-10 maker</a></li>'
    f'<li><a href="{href("release-clashes-2027.html", 0)}">Release clash finder: which of my games land the same week?</a></li>'
    f'<li><a href="{href("backlog-planner-2027.html", 0)}">Backlog planner: can I finish my games before the next big launch?</a></li>'
    f'<li><a href="{href("exclusives-2027.html", 0)}">Which 2027 games will I miss on my console?</a></li>'
    f'<li><a href="{href("movies-2027.html", 0)}">Upcoming movies 2027</a>: Zelda, Shrek 5, Avengers: Secret Wars dates</li><li><a href="{href("tools.html", 0)}">Every DayOneDrop tool</a></li></ul></div></section>')
home = f'''<header class="hero"><div class="wrap">
<span class="kicker">Live release board · updated {e(UPDATED)}</span>
<h1>Every big game of 2027,<br><span class="amber">on one board.</span></h1>
<p class="lead">Release dates, platforms, delays and live countdowns for the year's biggest launches. Star the games you want, add them to your calendar and never miss a launch day.</p>
<div class="next-drop" id="next-drop">
<span class="next-label">Next drop</span>
<div class="next-title"><span class="flaps" id="nd-title"></span></div>
<span class="muted" id="nd-date"></span>
<div class="cd" id="nd-cd" role="timer">
<div class="cd-unit"><span class="flaps" data-u="0"></span><span>Days</span></div>
<div class="cd-unit"><span class="flaps" data-u="1"></span><span>Hours</span></div>
<div class="cd-unit"><span class="flaps" data-u="2"></span><span>Mins</span></div>
<div class="cd-unit"><span class="flaps" data-u="3"></span><span>Secs</span></div>
</div>
<div class="btns"><a class="btn" id="nd-link" href="#" data-base="{"games/" if PREVIEW else "/games/"}" data-ext="{".html" if PREVIEW else ""}">Game details</a><a class="btn line" href="{href("calendar.html", 0)}">See the full calendar</a></div>
</div>
</div></header>
{_h_section}
<section><div class="wrap">
<div class="sec-head"><h2>When does every 2027 game come out?</h2><p class="muted">The live departures board. Tap ☆ to save a game. Filter by your console.</p></div>
{board(0)}
<div class="btns" style="margin-top:14px"><button class="btn line sm" type="button" id="share-list">Share my list</button></div>
</div></section>
{AD.format("home-mid")}
<section><div class="wrap">
<div class="sec-head"><h2>Which 2027 games have a full guide?</h2><p class="muted">Release history, platforms and countdowns for the games everyone is waiting for.</p></div>
<div class="grid">{"".join(pass_card(g, 0) for g in featured)}</div>
</div></section>
{_h_related}'''
home_faq = [
    ("How many games come out in 2027?", _h_quick),
    ("What is the next big game release?", (f"The next game on our 2027 board is {_h_next[0]['title']} on {nice_date(_h_next[0])}, followed by " + ", ".join(f"{g['title']} ({nice_date(g)})" for g in _h_next[1:4]) + ".") if len(_h_next) > 3 else "See the departures board for the next launch."),
    ("How many 2027 games are on PS5, Xbox, PC and Switch 2?", "So far: " + ", ".join(f"{n} on {lg}" for p, sl, lg, n in _h_plat) + ". Each console has its own page with the full list."),
    ("What are the biggest games coming in 2027?", "The big names so far include Fable (23 February), Final Fantasy VII Revelation (8 April), God of War: Laufey (20 May), Tomb Raider: Legacy of Atlantis (12 February), Persona 4 Revival (18 February) and Exodus (7 April)."),
    ("Why is February 2027 so busy?", "Many publishers picked February 2027, so Metro 2039, Tomb Raider: Legacy of Atlantis, Persona 4 Revival, Fable and more all land within a few weeks of each other."),
    ("Can release dates change?", "Yes. God of War: Laufey already moved from February to May. We mark every game as on time, delayed or scheduled, and update the board when publishers announce changes."),
    ("What time do games unlock?", "Most console games unlock at midnight local time on release day, but some publishers use one worldwide time. We add exact unlock times as soon as publishers share them."),
]
page("index.html", "2027 Game Release Dates: Live Launch Board | DayOneDrop",
     "Every big 2027 game release date on one live board: Fable, Final Fantasy VII Revelation, God of War Laufey and more, with countdowns and delay tracking.",
     home, 0, home_faq,
     extra_ld={"@context": "https://schema.org", "@type": "ItemList", "name": "2027 game release dates",
               "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": g["title"] + " (" + nice_date(g) + ")"} for i, g in enumerate(GAMES)]})

# ---------------- CALENDAR ----------------
def month_html(m):
    first = datetime.date(2027, m, 1)
    days_in = (datetime.date(2027 + (m == 12), (m % 12) + 1, 1) - first).days
    lead_blank = first.weekday()
    dated = {}
    for g in GAMES:
        if g["date"]:
            d = datetime.date.fromisoformat(g["date"])
            if d.month == m:
                dated.setdefault(d.day, []).append(g)
    cells = "".join(f"<b>{x}</b>" for x in "MTWTFSS") + "<span></span>" * lead_blank
    for d in range(1, days_in + 1):
        if d in dated:
            names = ", ".join(x["title"] for x in dated[d])
            cells += f'<span class="day has" title="{e(names)}">{d}</span>'
        else:
            cells += f'<span class="day">{d}</span>'
    games = [g for g in GAMES if g["month"] == m]
    items = ""
    for g in games:
        name = f'<a href="{href("games/" + g["slug"] + ".html", 0)}">{e(g["title"])}</a>' if g["page"] else e(g["title"])
        items += f'<li><span class="dd">{e(short_date(g) if g["date"] else "TBC")}</span><span>{name}</span></li>'
    return f'''<div class="month"><h3>{(f'<a href="{href("months/" + MONTH_SLUGS[m - 1] + ".html", 0)}">{MONTHS[m - 1]} 2027</a>') if m in month_pages_list() else MONTHS[m - 1] + " 2027"} <small>{len(games)} game{"s" if len(games) != 1 else ""}</small></h3><div class="days">{cells}</div>{f'<ul class="mlist">{items}</ul>' if items else '<p class="muted" style="margin:10px 0 0;font-size:.9rem">No dates announced yet.</p>'}</div>'''

_cal_counts = {m: sum(1 for g in GAMES if g["month"] == m) for m in range(1, 13)}
_cal_busy = max(_cal_counts, key=lambda m: _cal_counts[m])
_cal_dated = sorted([g for g in GAMES if g["date"]], key=lambda x: x["date"])
_cal_window = [g for g in GAMES if not g["date"]]
_cal_quick = (f"We track {len(GAMES)} games for 2027: {len(_cal_dated)} with an exact date and {len(_cal_window)} with only a season or year. "
              f"{MONTHS[_cal_busy - 1]} 2027 is the busiest month with {_cal_counts[_cal_busy]} launches"
              + (f", and the first dated game is {_cal_dated[0]['title']} on {nice_date(_cal_dated[0])}." if _cal_dated else "."))
_cal_mrows = "".join(f'<div class="row"><span>{(f'<a href="{href("months/" + MONTH_SLUGS[m - 1] + ".html", 0)}">{MONTHS[m - 1]} 2027</a>') if m in month_pages_list() else MONTHS[m - 1] + " 2027"}</span><b>{_cal_counts[m]} game{"s" if _cal_counts[m] != 1 else ""}</b></div>' for m in range(1, 13))
cal = f'''<header class="hero"><div class="wrap"><span class="kicker">2027 calendar</span><h1>The 2027 game<br><span class="amber">release calendar.</span></h1>
<p class="lead">Every confirmed date, month by month. Highlighted days have a launch. Games with only a season or year are listed in their likely month.</p>
<p class="muted" style="margin:0">Last checked {e(UPDATED)} · {len(_cal_dated)} exact dates</p></div></header>
<section><div class="wrap"><div class="out" style="margin-bottom:24px"><div class="row"><span><strong>Quick answer:</strong> {e(_cal_quick)}</span></div></div>
<div class="sec-head"><h2>What games come out in each month of 2027?</h2></div><div class="months">{"".join(month_html(m) for m in range(1, 13))}</div></div></section>
{AD.format("cal-mid")}
<section><div class="wrap"><div class="sec-head"><h2>How many games launch each month of 2027?</h2></div><div class="out" style="margin-bottom:28px">{_cal_mrows}</div>
<div class="sec-head"><h2>How do I add a 2027 release date to my calendar?</h2><p class="muted">One tap, and your phone reminds you on launch day.</p></div>
<div class="out">{"".join(f'<div class="row"><span>{e(g["title"])} · <span class="muted">{e(nice_date(g))}</span></span><span class="btns"><a class="btn sm" href="{gcal(g)}" rel="nofollow noopener" target="_blank">Google Calendar</a><a class="btn line sm" href="{ics(g)}" download="{g["slug"]}.ics">Apple / Outlook</a></span></div>' for g in _cal_dated)}</div>
<div class="sec-head" style="margin-top:28px"><h2>Related pages and tools</h2></div><ul>
<li><a href="{href("backlog-planner-2027.html", 0)}">2027 backlog planner</a>: will you finish each game before the next launch?</li>
<li><a href="{href("release-clashes-2027.html", 0)}">2027 release clashes</a>: which games land the same week</li>
<li><a href="{href("delayed-games-2027.html", 0)}">Games delayed to 2027</a></li></ul></div></section>'''
cal_faq = [
    ("Which month has the most game releases in 2027?", f"{MONTHS[_cal_busy - 1]} 2027, with {_cal_counts[_cal_busy]} tracked launches so far."),
    ("What is the first game of 2027?", (f"{_cal_dated[0]['title']}, on {nice_date(_cal_dated[0])}." if _cal_dated else "No exact dates yet.")),
    ("How many 2027 games have a release date?", f"{len(_cal_dated)} of the {len(GAMES)} games we track have an exact day. The rest have a season or year, such as spring 2027."),
    ("How do I get a reminder for a release date?", "Use the Google Calendar or Apple / Outlook buttons on this page. They add the launch day to your calendar for free."),
    ("Why do some games show TBC?", "Some publishers have only shared a season or a year. We add the exact day as soon as it's announced."),
]
page("calendar.html", "2027 Video Game Release Calendar, Month by Month | DayOneDrop",
     f"The full 2027 video game release calendar, month by month: {len(_cal_dated)} exact dates, the busiest month and one-tap Google, Apple or Outlook reminders. Checked {UPDATED}."[:160],
     cal, 0, cal_faq, crumbs=[("Home", DOMAIN + "/"), ("2027 Calendar", canon("calendar.html"))])

# ---------------- GAMES INDEX ----------------
others = [g for g in GAMES if not g["page"]]
_gi_all = sorted(GAMES, key=lambda x: (x["date"] or "9999", x["month"] or 13, x["title"]))
_gi_dated = [g for g in GAMES if g["date"]]
_gi_undated = [g for g in _gi_all if not g["date"]]
_gi_delayed = [g for g in GAMES if g["status"] == "delayed"]
_gi_pc = {p: sum(1 for g in GAMES if p in g["platforms"]) for p, _s, _l in PLAT_PAGES_FOOT}
_gi_all4 = [g for g in GAMES if all(p in g["platforms"] for p, _s, _l in PLAT_PAGES_FOOT)]
_gi_quick = (f"We track {len(GAMES)} games coming in 2027: {len(_gi_dated)} have an exact release date and {len(_gi_undated)} only have a season or year. "
             f"{len(_gi_delayed)} of them were delayed at least once, and {len(_gi_all4)} are coming to all four of PS5, Xbox Series X|S, PC and Switch 2.")
def _gi_link(g):
    return f'<a href="{href("games/" + g["slug"] + ".html", 0)}">{e(g["title"])}</a>' if g["page"] else e(g["title"])
def _gi_row(g):
    nm = f'<a href="{href("games/" + g["slug"] + ".html", 0)}"><strong>{e(g["title"])}</strong></a> <span class="muted mono">· guide</span>' if g["page"] else f'<strong>{e(g["title"])}</strong>'
    st = "delayed" if g["status"] == "delayed" else ("dated" if g["date"] else "window")
    return (f'<div class="row" data-gi data-plat="{e("|".join(g["platforms"]))}" data-st="{st}" data-dated="{1 if g["date"] else 0}" data-q="{e((g["title"] + " " + g["genre"] + " " + (g["dev"] or "")).lower())}">'
            f'<span>{nm}<br><span class="muted">{e(plat_text(g))} · {e(g["genre"])}</span></span><b>{e(nice_date(g))}</b></div>')
_gi_chips = ('<div class="chips" id="gi-plat" role="group" aria-label="Filter by console"><button class="chip" type="button" data-p="all" aria-pressed="true">All consoles</button>'
             + "".join(f'<button class="chip" type="button" data-p="{e(p)}" aria-pressed="false">{e(p)}</button>' for p, _s, _l in PLAT_PAGES_FOOT) + '</div>'
             '<div class="chips" id="gi-st" role="group" aria-label="Filter by date status" style="margin-top:8px"><button class="chip" type="button" data-s="all" aria-pressed="true">Any date</button>'
             '<button class="chip" type="button" data-s="dated" aria-pressed="false">Exact date</button><button class="chip" type="button" data-s="window" aria-pressed="false">No exact date</button>'
             '<button class="chip" type="button" data-s="delayed" aria-pressed="false">Delayed</button></div>')
gi = f'''<header class="hero"><div class="wrap"><span class="kicker">All games</span><h1>Every 2027 launch<br><span class="amber">we're tracking.</span></h1>
<p class="lead">Every confirmed 2027 game in one list, with dates, consoles and full guides for the biggest ones. Filter it to see what is coming to your console.</p>
<p class="muted" style="margin:0">Last checked {e(UPDATED)} · {len(GAMES)} games · dates confirmed by publishers or two trusted outlets</p></div></header>
<section><div class="wrap"><div class="out" style="margin-bottom:24px"><div class="row"><span><strong>Quick answer:</strong> {e(_gi_quick)}</span></div></div>
<div class="sec-head"><h2>Which 2027 games are coming to my console?</h2><p class="muted">Pick a console, a date type or type a name. Results update instantly.</p></div>
<div class="tool"><label for="gi-q" class="sr-only">Search games</label><input id="gi-q" type="search" placeholder="Search by game, genre or studio" autocomplete="off" style="margin-bottom:10px">{_gi_chips}
<p class="muted mono" id="gi-count" aria-live="polite" style="margin:12px 0 0">{len(GAMES)} games</p>
<div class="out" id="gi-list">{"".join(_gi_row(g) for g in _gi_all)}</div><div class="empty" id="gi-empty" hidden>No games match. Try another console or clear the search.</div></div></div></section>
{AD.format("games-mid")}
<section><div class="wrap"><div class="sec-head"><h2>Which 2027 games have a full guide?</h2><p class="muted">Countdowns, delay history, platforms and FAQs.</p></div><div class="grid">{"".join(pass_card(g, 0) for g in featured)}</div></div></section>
<section><div class="wrap"><div class="sec-head"><h2>How many 2027 games are on each console?</h2></div>
<div class="out" style="margin-bottom:28px">{"".join(f'<div class="row"><span><a href="{href("platforms/" + s + ".html", 0)}">{e(l)}</a></span><b>{_gi_pc[p]} games</b></div>' for p, s, l in PLAT_PAGES_FOOT)}<div class="row"><span>All four consoles</span><b>{len(_gi_all4)} games</b></div></div>
<div class="sec-head"><h2>Which 2027 games still have no exact date?</h2></div>
<div class="out" style="margin-bottom:28px">{"".join(f'<div class="row"><span>{_gi_link(g)}</span><b>{e(nice_date(g))}</b></div>' for g in _gi_undated)}</div>
<div class="sec-head"><h2>Related pages and tools</h2></div><ul>
<li><a href="{href("biggest-games-2027.html", 0)}">The biggest games of 2027</a>, and make your own top list</li>
<li><a href="{href("calendar.html", 0)}">The 2027 release calendar</a> with one-tap reminders</li>
<li><a href="{href("release-clashes-2027.html", 0)}">2027 release clashes</a>: which games land the same week</li>
<li><a href="{href("delayed-games-2027.html", 0)}">Every game delayed into 2027</a></li></ul></div></section>'''
gi_faq = [
    ("How many video games are coming out in 2027?", f"We track {len(GAMES)} confirmed 2027 games so far. {len(_gi_dated)} have an exact day and {len(_gi_undated)} only a season or year. The list grows as publishers announce more."),
    ("Which 2027 games have no release date yet?", (", ".join(g["title"] for g in _gi_undated[:8]) + (", and more." if len(_gi_undated) > 8 else ".")) if _gi_undated else "Every tracked game has an exact date."),
    ("Which console gets the most 2027 games?", (lambda m: f"{m}, with {_gi_pc[m]} of the {len(GAMES)} games we track.")(max(_gi_pc, key=lambda k: _gi_pc[k]))),
    ("How many 2027 games have been delayed?", f"{len(_gi_delayed)} of the games on this list were delayed at least once. The delayed games page lists each one."),
    ("Where do your release dates come from?", "From publishers' own announcements, or from at least two trusted gaming news sites when there is no publisher post."),
]
page("games.html", f"Upcoming Games 2027: All {len(GAMES)} Release Dates, Month by Month | DayOneDrop",
     f"Every game coming out in 2027 ({len(GAMES)}) with its release date, consoles and delays, month by month. Filter by PS5, Xbox, PC or Switch 2. Checked {UPDATED}."[:160],
     gi, 0, gi_faq, crumbs=[("Home", DOMAIN + "/"), ("All games", canon("games.html"))])

# ---------------- GAME PAGES ----------------
GP_TRACKED_ALL = {"stranger-than-heaven", "persona-4-revival", "fable", "wo-long-2", "spyro-a-realm-beyond", "the-expanse-osiris-reborn", "state-of-decay-3", "at-fates-end"}
PLAT_LINKS = [("platforms/" + s2 + ".html", p2) for p2, s2, l2 in PLAT_PAGES_FOOT]
def _glink(g, depth=0):
    return f'<a href="{href("games/" + g["slug"] + ".html", depth)}">{e(g["title"])}</a>' if g["page"] else e(g["title"])
def month_file(m):
    return "months/" + MONTH_SLUGS[m - 1] + ".html" if m in month_pages_list() else None
BIG_WHY_SLUGS = {"stranger-than-heaven", "forza-horizon-6", "metroid-ravenous", "until-dawn-2", "metro-2039", "tomb-raider-legacy-of-atlantis", "persona-4-revival", "fable", "wo-long-2", "exodus", "final-fantasy-vii-revelation", "lords-of-the-fallen-ii", "spyro-a-realm-beyond", "god-of-war-laufey", "squadron-42", "kingdom-hearts-iv", "kirby-and-the-world-beyond", "pokemon-winds-and-waves", "xenoblade-genesis", "resident-evil-veronica"}
# 2027 versions of games already out elsewhere: single-platform in our data but NOT exclusives (checked 22 Nov 2026).
PORTS = {"forza-horizon-6": "Already out on Xbox Series X|S and PC since May 2026. This is the PS5 version.",
         "007-first-light": "Already out on PS5, Xbox Series X|S and PC. This is the delayed Switch 2 version."}
for g in featured:
    f = "games/" + g["slug"] + ".html"
    if not g["date"]:
        same_month = sorted([x for x in GAMES if not x["date"] and x["slug"] != g["slug"]], key=lambda x: x["month"])
        also_h = "What other 2027 games have no exact date yet?"
    else:
        same_month = [x for x in GAMES if x["month"] == g["month"] and x["slug"] != g["slug"]]
        also_h = f"What else launches in {MONTHS[g['month'] - 1]} 2027?"
    cd = ""
    if g["date"]:
        cd = f'''<div class="cdw"><span class="lbl">Countdown to launch</span><div class="cd" data-countdown="{g["date"]}">
<div class="cd-unit"><span class="flaps" data-u="0"></span><span>Days</span></div><div class="cd-unit"><span class="flaps" data-u="1"></span><span>Hrs</span></div>
<div class="cd-unit"><span class="flaps" data-u="2"></span><span>Min</span></div><div class="cd-unit"><span class="flaps" data-u="3"></span><span>Sec</span></div></div></div>'''
    acts = ""
    if g["date"]:
        acts += f'<a class="btn sm" href="{gcal(g)}" rel="nofollow noopener" target="_blank">Add to Google Calendar</a><a class="btn line sm" href="{ics(g)}" download="{g["slug"]}.ics">Apple / Outlook</a>'
    if not (g.get("free") or g.get("no_preorder")):  # free-to-play games (e.g. Ananta) have nothing to pre-order
        acts += f'<a class="btn sm" href="{go(amz_slug(g))}" {AFF_ATTR}>Pre-order on Amazon</a>'
    acts += f'<button class="btn line sm star" type="button" data-slug="{g["slug"]}" data-name="{e(g["title"])}" aria-pressed="false">☆</button><button class="btn line sm" type="button" data-copy-link>Copy link</button>'
    from urllib.parse import quote
    share = canon(f)
    shares = (f'<a class="btn line sm" href="https://www.reddit.com/submit?url={quote(share)}&title={quote(g["title"] + " release date and countdown")}" target="_blank" rel="noopener">Share on Reddit</a>'
              f'<a class="btn line sm" href="https://wa.me/?text={quote(g["title"] + " release date: " + share)}" target="_blank" rel="noopener">WhatsApp</a>'
              f'<a class="btn line sm" href="https://twitter.com/intent/tweet?text={quote(g["title"] + " launches " + nice_date(g))}&url={quote(share)}" target="_blank" rel="noopener">Post on X</a>')
    if g["date"]:
        qa = f"{g['title']} comes out on {nice_date(g)} for {plat_text(g)}."
    else:
        _w = nice_date(g)
        _w = _w[0].lower() + _w[1:] if _w.split()[0] in ("Late", "Early", "Mid", "Spring", "Summer", "Autumn", "Fall", "Winter") else _w
        qa = f"{g['title']} has no exact release date yet. It is set for {_w} on {plat_text(g)}."
    if g["slug"] in PORTS:
        qa += " " + PORTS[g["slug"]]
    if g.get("qa_note"):
        qa += " " + g["qa_note"]
    if g["status"] == "delayed":
        qa += " It has been delayed before, so we watch it closely."
    if g["slug"] in GP_TRACKED_ALL:
        qa += " It is also coming to Xbox Game Pass."
    short = g["title"].split(":")[0]
    rel = [("calendar.html", "The full 2027 release calendar")]
    rel.append((month_file(g["month"]), f"Every game coming in {MONTHS[g['month'] - 1]} 2027") if month_file(g["month"]) and g["date"] else ("games.html", "Every tracked 2027 game"))
    for pf, pn in PLAT_LINKS:
        if pn in g["platforms"]:
            rel.append((pf, f"Every {pn} game coming in 2027")); break
    if g["slug"] in ("fable", "final-fantasy-vii-revelation", "god-of-war-laufey", "resident-evil-veronica"):  # TGA 2026 Most Anticipated nominees
        rel.insert(1, ("game-awards-2026.html", f"{short} at The Game Awards 2026: every Most Anticipated nominee"))
    if g["slug"] in ("wo-long-2", "lords-of-the-fallen-ii", "the-duskbloods"): rel.insert(1, ("games-like-elden-ring.html", "Games like Elden Ring and every 2027 soulslike"))
    if g["slug"] in GP_TRACKED_ALL: rel.append(("game-pass-2027.html", "Every 2027 Xbox Game Pass game"))
    if "RPG" in g["genre"]: rel.append(("rpgs-2027.html", "Every RPG coming in 2027"))
    if g["status"] == "delayed": rel.append(("delayed-games-2027.html", "Every delayed game of 2027"))
    if g["date"]: rel.append(("release-clashes-2027.html", f"What else launches the same week as {short}?"))
    if g["date"]: rel.append(("backlog-planner-2027.html", f"Can I finish my backlog before {short}?"))
    rel_html = "".join(f'<li><a href="{href(rf, 1)}">{e(rn)}</a></li>' for rf, rn in rel[:6])
    src_html = f'<p class="muted" style="margin-top:14px">Sources checked: {e(g["sources"])}.</p>' if g.get("sources") else ""
    body = f'''<header class="hero"><div class="wrap"><span class="kicker">Release guide</span>
<div class="gp-head"><div><h1>{e(g["title"])}<br><span class="amber">release date</span></h1>
<p class="lead">{e(g["about"])}</p><p class="muted" style="margin:0">Last checked {e(UPDATED)}</p>
<div class="out" style="margin-top:16px"><div class="row"><span><strong>Quick answer:</strong> {e(qa)}</span></div></div></div>
<div class="ticket">
<div class="ticket-row"><div><span class="lbl">Launch</span><span class="val">{e(nice_date(g))}</span></div><div><span class="lbl">Status</span>{status_html(g)}</div></div>
<div class="ticket-row"><div><span class="lbl">Platforms</span><span class="val">{e(plat_text(g))}</span></div><div><span class="lbl">Made by</span><span class="val">{e(g["dev"] or "TBC")}</span></div></div>
{cd}<div class="acts">{acts}</div>{"" if (g.get("free") or g.get("no_preorder")) else AFF_NOTE}</div>
</div></div></header>
<section><div class="wrap cols">
<div><h2>What do we know about {e(short)}?</h2><ul class="facts-list">{"".join(f"<li>{e(x)}</li>" for x in g["facts"])}</ul>{src_html}</div>
<div><h2>Has {e(short)} been delayed?</h2><p class="muted">{"Yes. See the changes below." if g["status"] == "delayed" else "No delay so far. Here is how the date has been set."}</p><div class="hist">{"".join(f"<div><small>{e(h['when'])}</small>{e(h['text'])}</div>" for h in g["history"])}</div>
<h3 style="margin-top:26px">Tell your friends</h3><div class="btns">{shares}</div></div>
</div></section>
{AD.format(g["slug"] + "-mid")}
<section><div class="wrap"><div class="sec-head"><h2>{e(also_h)}</h2><a class="btn line sm" href="{href("calendar.html", 1)}">Full calendar</a></div>
<div class="out">{"".join(f'<div class="row"><span>{_glink(x, 1)}</span><b>{e(nice_date(x))}</b></div>' for x in same_month) or '<div class="empty">No other launches that month yet.</div>'}</div>
<div class="sec-head" style="margin-top:28px"><h2>Related pages and tools</h2></div><ul>{rel_html}</ul></div></section>'''
    faqs = [
        (f"When does {g['title']} come out?", f"{g['title']} is set for {nice_date(g)}." + (" It was delayed once, so we track any further changes." if g["status"] == "delayed" else " We update this page if the date changes.")),
        (f"What platforms is {g['title']} on?", (f"It's confirmed for {plat_text(g)}." if g["platforms"] else "The full platform list hasn't been confirmed yet. We add it as soon as it is.")),
        (f"Who is making {g['title']}?", f"{g['title']} is made by {g['dev']}." if g["dev"] else "The developer will be listed once confirmed."),
        (f"How can I get a reminder for {g['title']}?", "Use the Add to Google Calendar or Apple / Outlook button on this page. Your calendar will remind you on launch day." if g["date"] else "Tap the ☆ button to add it to your launch list, or join our email list. We update this page the day an exact date is announced."),
    ] + [tuple(x) for x in g.get("faq", [])]
    page(f, (g.get("seo_title") or _ctr_title(g)) + " | DayOneDrop" if len((g.get("seo_title") or "")) < 76 else g["seo_title"],
         _ctr_desc(g)[:160],
         body, 1, faqs, crumbs=[("Home", DOMAIN + "/"), ("All games", canon("games.html")), (g["title"], canon(f))])

# ---------------- PLATFORM PAGES ----------------
PLAT_PAGES = PLAT_PAGES_FOOT
def is_excl(g, plat):
    return g["platforms"] == [plat] and g["slug"] not in PORTS
plat_urls = []


def _plat_extra(plat, long, games, excl):
    """Question-style summary blocks for a platform page (refresh 23 Nov 2026)."""
    out = ""
    ex_rows = "".join(plat_row(g, 1, plat) for g in excl) or f'<div class="empty">None right now. Every {e(long)} game we track is also announced elsewhere.</div>'
    out += f'<div class="sec-head"><h2>Which 2027 games are only on {e(long)}?</h2><span class="muted">{len(excl)}</span></div><div class="out" style="margin-bottom:28px">{ex_rows}</div>'
    late = [g for g in games if g["slug"] in PORTS]
    if late:
        out += (f'<div class="sec-head"><h2>Which games are coming to {e(long)} late?</h2><span class="muted">{len(late)}</span></div>'
                f'<p class="muted">These are already out on other systems. The {e(long)} version lands in 2027.</p>'
                f'<div class="out" style="margin-bottom:28px">{"".join(plat_row(g, 1, plat) for g in late)}</div>')
    if plat == "Xbox Series X|S":
        out += (f'<div class="sec-head"><h2>When is the next Xbox Games Showcase?</h2></div>'
                f'<p>Microsoft has not announced the 2027 show yet. Every showcase since 2023 aired on a Sunday in early June. See <a href="{href("xbox-games-showcase-2027.html", 1)}">Xbox Games Showcase 2027</a> for past dates and the Xbox games still waiting for a release date.</p>')
    if plat == "PC":
        out += (f'<div class="sec-head"><h2>When is the next Steam sale?</h2></div>'
                f'<p>The Steam Winter Sale 2026 runs 17 December 2026 to 4 January 2027, then the Spring Sale is 18 to 25 March and the Summer Sale 24 June to 8 July 2027. See <a href="{href("steam-sale-dates.html", 1)}">every Steam sale date</a> with a live countdown and the 2027 PC games that launch during a sale.</p>')
    if plat == "Switch 2":
        out += (f'<div class="sec-head"><h2>When is the next Nintendo Direct?</h2></div>'
                f'<p>Nintendo has not announced it yet; the last full Direct was on 9 September 2026. See <a href="{href("nintendo-direct.html", 1)}">Nintendo Direct</a> for every 2026 show and the Switch 2 games still waiting for a date.</p>')
    skip = [g for g in GAMES if plat not in g["platforms"] and g["platforms"] and g["slug"] not in PORTS]
    big_skip = [g for g in skip if g["slug"] in BIG_WHY_SLUGS]
    show = (big_skip or skip)[:8]
    if show:
        rows = "".join(f'<div class="row"><span><strong>{_glink(g, 1)}</strong><br><span class="muted">On {e(", ".join(g["platforms"]))}</span></span><b>{e(nice_date(g))}</b></div>' for g in show)
        out += (f'<div class="sec-head"><h2>Which big 2027 games are not coming to {e(long)}?</h2><span class="muted">{len(skip)} in total</span></div>'
                f'<div class="out" style="margin-bottom:28px">{rows}</div>')
    return out


def plat_row(g, depth, plat):
    t = f'<a href="{href("games/" + g["slug"] + ".html", depth)}">{e(g["title"])}</a>' if g["page"] else e(g["title"])
    others = [x for x in g["platforms"] if x != plat]
    also = PORTS[g["slug"]] if g["slug"] in PORTS else ("Only on " + plat) if not others else ("Also on " + ", ".join(others))
    genre = (e(g["genre"]) + " · ") if g["genre"] else ""
    return f'<div class="row"><span><strong>{t}</strong><br><span class="muted">{genre}{e(also)}</span></span><b>{e(nice_date(g))}</b></div>'


for plat, slug, long in PLAT_PAGES:
    f = "platforms/" + slug + ".html"
    plat_urls.append(f)
    games = [g for g in GAMES if plat in g["platforms"]]
    dated = [g for g in games if g["date"]]
    excl = [g for g in games if is_excl(g, plat)]
    by_month = {}
    for g in games:
        by_month.setdefault(g["month"] if g["date"] else 13, []).append(g)
    blocks = ""
    for m, gs in sorted(by_month.items()):
        head = f"Which {long} games have no exact date yet?" if m == 13 else f"What is coming to {long} in {MONTHS[m - 1]} 2027?"
        n = f'{len(gs)} game{"s" if len(gs) != 1 else ""}'
        rows = "".join(plat_row(g, 1, plat) for g in gs)
        blocks += f'<div class="sec-head"><h2>{head}</h2><span class="muted">{n}</span></div><div class="out" style="margin-bottom:28px">{rows}</div>'
    cd = ""
    if dated:
        nxt = dated[0]
        cd = ('<div class="cdw"><span class="lbl">Next ' + e(plat) + ' launch: ' + e(nxt["title"]) + '</span>'
              '<div class="cd" data-countdown="' + nxt["date"] + '">'
              '<div class="cd-unit"><span class="flaps" data-u="0"></span><span>Days</span></div>'
              '<div class="cd-unit"><span class="flaps" data-u="1"></span><span>Hrs</span></div>'
              '<div class="cd-unit"><span class="flaps" data-u="2"></span><span>Min</span></div>'
              '<div class="cd-unit"><span class="flaps" data-u="3"></span><span>Sec</span></div></div></div>')
    other_links = " · ".join(f'<a href="{href("platforms/" + s2 + ".html", 1)}">{e(l2)}</a>' for p2, s2, l2 in PLAT_PAGES if p2 != plat)
    body = (f'<header class="hero"><div class="wrap"><span class="kicker">{e(long)} lineup</span>'
            f'<h1>Every {e(long)} game<br><span class="amber">coming in 2027.</span></h1>'
            f'<p class="lead">{len(games)} confirmed {e(long)} launches so far, {len(dated)} with an exact date. '
            f'Sorted by release date and checked against official announcements.</p>'
            f'<p class="muted" style="margin:0">Last checked {e(UPDATED)} · Other consoles: {other_links}</p>{cd}</div></header>'
            f'<section><div class="wrap"><div class="out" style="margin-bottom:24px"><div class="row"><span><strong>Quick answer:</strong> {len(games)} confirmed 2027 games are coming to {e(long)}'
            + (f', and the next one is {e(dated[0]["title"])} on {e(nice_date(dated[0]))}' if dated else '')
            + (f'. Only on {e(long)}: {e(", ".join(g["title"] for g in excl))}.' if excl else f'. None of them are {e(long)} exclusives right now.')
            + f'</span></div></div>{blocks}'
            + _plat_extra(plat, long, games, excl) +
            f'<div class="sec-head"><h2>What else helps plan my {e(long)} year?</h2></div><ul>'
            f'<li><a href="{href("exclusives-2027.html", 1)}">2027 console exclusives</a> and which games skip {e(long)}</li>'
            f'<li><a href="{href("release-clashes-2027.html", 1)}">2027 release clashes</a>: games landing the same week</li>'
            f'<li><a href="{href("delayed-games-2027.html", 1)}">Games delayed to 2027</a></li>'
            f'<li><a href="{href("biggest-games-2027.html", 1)}">The biggest games of 2027</a></li>'
            f'<li><a href="{href("backlog-planner-2027.html", 1)}">2027 backlog planner</a>: will you finish before the next launch?</li>'
            + (f'<li><a href="{href("game-pass-2027.html", 1)}">Every 2027 game on Xbox Game Pass</a></li>' if plat in ("Xbox Series X|S", "PC") else "")
            + '</ul>'
            f'<p class="muted">Star games on the <a href="{href("index.html", 1)}#board">departures board</a> to build your launch list, '
            f'and every guide has one-tap calendar reminders.</p></div></section>')
    first = dated[0] if dated else None
    if excl:
        ex = ", ".join(g["title"] for g in excl) + (" is" if len(excl) == 1 else " are") + f" only confirmed for {long} so far."
    else:
        ex = f"None of the 2027 games we track are {long} exclusives right now."
    skip = [g for g in GAMES if plat not in g["platforms"] and g["platforms"]]
    faqs = [
        (f"How many {long} games are coming in 2027?", f"We track {len(games)} confirmed {long} games for 2027 so far. This list grows as publishers announce dates and platforms."),
        (f"What is the next big {long} game in 2027?", (f"{first['title']} is the first dated {long} game on our list, launching {nice_date(first)}." if first else "No exact dates are confirmed yet.")),
        (f"Which 2027 games are only on {long}?", ex),
        (f"Which 2027 games are not coming to {long}?", (f"{len(skip)} tracked games are not announced for {long}, including " + ", ".join(g["title"] for g in skip[:5]) + ". See our 2027 console exclusives page for the full list.") if skip else f"Every 2027 game we track is announced for {long}."),
    ]
    page(f, f"{long} Game Release Dates 2027: All {len(games)} Upcoming Games | DayOneDrop",
         f"All {len(games)} upcoming {long} games and new releases in 2027, month by month: exact release dates, exclusives, delays and countdowns. Updated {UPDATED}."[:160],
         body, 1, faqs, crumbs=[("Home", DOMAIN + "/"), ("All games", canon("games.html")), (long + " games 2027", canon(f))])

# ---------------- MONTH PAGES ----------------
month_urls = []
for m in month_pages_list():
    f = "months/" + MONTH_SLUGS[m - 1] + ".html"
    month_urls.append(f)
    mname = MONTHS[m - 1]
    games = [g for g in GAMES if g["month"] == m]
    dated = [g for g in games if g["date"]]
    loose = [g for g in games if not g["date"]]
    def mrow(g):
        t = f'<a href="{href("games/" + g["slug"] + ".html", 1)}">{e(g["title"])}</a>' if g["page"] else e(g["title"])
        plats = ", ".join(g["platforms"]) or "Platforms TBC"
        genre = (e(g["genre"]) + " · ") if g.get("genre") else ""
        flag = ' <span class="muted">(delayed)</span>' if g["status"] == "delayed" else ""
        gp = ' <span class="muted">· Game Pass</span>' if g["slug"] in GP_TRACKED_ALL else ""
        return (f'<div class="row" data-mo-slug="{g["slug"]}" data-mo-plat="{e("|".join(g["platforms"]))}" data-mo-date="{g["date"] or ""}"{" data-mo-big=\"1\"" if g["slug"] in BIG_WHY_SLUGS else ""}>'
                f'<span><strong>{t}</strong>{flag}{gp}<br><span class="muted">{genre}{e(plats)}</span></span><b>{e(nice_date(g))}</b></div>')
    weeks = {}
    for g in dated:
        d = datetime.date.fromisoformat(g["date"])
        weeks.setdefault(d.isocalendar()[1], []).append(g)
    busiest = max(weeks.values(), key=len) if weeks else []
    _mochips = ('<div class="chips" role="group" aria-label="Console"><button class="chip" type="button" data-mo-p="" aria-pressed="true">All consoles</button>'
                + "".join(f'<button class="chip" type="button" data-mo-p="{e(p)}" aria-pressed="false">{e(p)}</button>' for p in PLATS)
                + '<button class="chip" type="button" data-mo-p="big" aria-pressed="false">Big releases only</button></div>')
    _motool = (f'<div class="tool" id="mo-tool" data-month="{mname} 2027"><h2 style="font-size:1.5rem;margin-top:0">Which {mname} 2027 games can I play on my console?</h2>'
               f'<p class="muted">Tap your console to filter the list below, then add every match to your ★ launch list in one go. Your choice is remembered on this device.</p>{_mochips}'
               f'<p class="mono amber" id="mo-count" aria-live="polite" style="margin:12px 0 0">{len(games)} games</p><p class="muted" id="mo-next" style="margin:6px 0 10px"></p>'
               f'<button class="btn sm" type="button" id="mo-add">Add these to my ★ list</button></div>')
    blocks = f'<div id="mo-list"><div class="sec-head"><h2>What games come out in {mname} 2027?</h2><span class="muted">{len(dated)} dated</span></div><div class="out" style="margin-bottom:28px">{"".join(mrow(g) for g in dated) or "<div class=empty>No exact dates yet.</div>"}</div>'
    if loose:
        blocks += f'<div class="sec-head"><h2>Which {mname} 2027 games have no exact date yet?</h2><span class="muted">{len(loose)}</span></div><div class="out" style="margin-bottom:28px">{"".join(mrow(g) for g in loose)}</div>'
    blocks += f'<p class="empty" id="mo-none" hidden>None of the {mname} 2027 games we track are on that console yet. Try another one.</p></div>'
    _mdel = [g for g in games if g["status"] == "delayed"]
    _mgp = [g for g in games if g["slug"] in GP_TRACKED_ALL]
    _mx = lambda xs: "".join(f'<div class="row"><span>{_glink(x, 1)}<br><span class="muted">{e(", ".join(x["platforms"]))}</span></span><b>{e(nice_date(x))}</b></div>' for x in xs)
    _mextra = (f'<div class="sec-head"><h2>Which {mname} 2027 games were delayed?</h2><span class="muted">{len(_mdel)}</span></div>'
               + (f'<div class="out" style="margin-bottom:12px">{_mx(_mdel)}</div><p class="muted">Each one moved at least once. See why on the <a href="{href("delayed-games-2027.html", 1)}">delayed games of 2027</a> page.</p>' if _mdel else f'<p>None so far. Every {mname} 2027 game we track is still on its first announced date.</p>')
               + f'<div class="sec-head" style="margin-top:28px"><h2>Which {mname} 2027 games are on Xbox Game Pass?</h2><span class="muted">{len(_mgp)}</span></div>'
               + (f'<div class="out" style="margin-bottom:12px">{_mx(_mgp)}</div>' if _mgp else f'<p>None of the {mname} 2027 games we track are confirmed for Game Pass yet.</p>')
               + f'<p class="muted" style="margin-bottom:28px">Only games Microsoft or the publisher confirmed for Game Pass. Full list on the <a href="{href("game-pass-2027.html", 1)}">Game Pass 2027</a> page.</p>')
    pc = {pl: sum(1 for g in games if pl in g["platforms"]) for pl, _, _ in PLAT_PAGES}
    platline = " · ".join(f'<a href="{href("platforms/" + s2 + ".html", 1)}">{e(l2)}</a>: {pc[p2]}' for p2, s2, l2 in PLAT_PAGES)
    _mbig = [g for g in games if g["slug"] in BIG_WHY_SLUGS]
    first = dated[0] if dated else None
    _mq = (f"{len(games)} games are set for {mname} 2027 ({len(dated)} with an exact date)"
           + (f", starting with {first['title']} on {nice_date(first)}" if first else "")
           + (". The big ones are " + ", ".join(f"{g['title']} ({nice_date(g)})" for g in _mbig[:5]) + "." if _mbig else "."))
    _mwk = ""
    if len(busiest) > 1:
        _mwk = (f'<div class="sec-head"><h2>What is the busiest week of {mname} 2027?</h2><span class="mono amber">{len(busiest)} launches</span></div>'
                f'<div class="out" style="margin-bottom:28px">{"".join(mrow(g) for g in busiest)}</div>')
    _mpl = ("".join(f'<div class="row"><span><a href="{href("platforms/" + s2 + ".html", 1)}">{e(l2)}</a><br><span class="muted">{e(", ".join(g["title"] for g in games if p2 in g["platforms"]) or "Nothing yet")}</span></span><b>{pc[p2]} of {len(games)}</b></div>' for p2, s2, l2 in PLAT_PAGES))
    prev_next = []
    ml = month_pages_list(); i = ml.index(m)
    if m == 1: prev_next.append(f'<a class="btn line sm" href="{href("games-december-2026.html", 1)}">← December 2026</a>')
    if i > 0: prev_next.append(f'<a class="btn line sm" href="{href("months/" + MONTH_SLUGS[ml[i-1] - 1] + ".html", 1)}">← {MONTHS[ml[i-1] - 1]} 2027</a>')
    if i < len(ml) - 1: prev_next.append(f'<a class="btn line sm" href="{href("months/" + MONTH_SLUGS[ml[i+1] - 1] + ".html", 1)}">{MONTHS[ml[i+1] - 1]} 2027 →</a>')
    body = (f'<header class="hero"><div class="wrap"><span class="kicker">{mname} 2027</span>'
            f'<h1>Games coming out in {mname} 2027:<br><span class="amber">{len(games)} games on the board.</span></h1>'
            f'<p class="lead">Every video game launching in {mname} 2027 on PS5, Xbox Series X|S, PC and Switch 2, in date order. '
            f'Each date is checked against the publisher or two trusted outlets, and we mark delays as they happen.</p>'
            f'<p class="muted" style="margin:0">Last checked {e(UPDATED)} · Games per console: {platline}</p></div></header>'
            f'<section><div class="wrap"><div class="out" style="margin-bottom:24px"><div class="row"><span><strong>Quick answer:</strong> {e(_mq)}</span></div></div>{_motool}{blocks}{_mwk}{_mextra}'
            f'<div class="sec-head"><h2>Which {mname} 2027 games are on my console?</h2></div><div class="out" style="margin-bottom:28px">{_mpl}</div>'
            f'<p class="muted">See which weeks clash in the <a href="{href("release-clashes-2027.html", 1)}">2027 release clash finder</a>. Add any date to your calendar from the <a href="{href("calendar.html", 1)}">2027 calendar</a>, or star games on the <a href="{href("index.html", 1)}#board">departures board</a>.</p>'
            f'<div class="btns" style="display:flex;gap:10px;flex-wrap:wrap">{"".join(prev_next)}</div>'
            f'<div class="sec-head" style="margin-top:28px"><h2>Related pages and tools</h2></div><ul>'
            f'<li><a href="{href("biggest-games-2027.html", 1)}">The biggest games of 2027</a>, and a shareable top list maker</li>'
            f'<li><a href="{href("backlog-planner-2027.html", 1)}">2027 backlog planner</a>: can you finish one game before the next?</li>'
            f'<li><a href="{href("new-games-this-week.html", 1)}">New games this week</a>: every launch grouped Monday to Sunday</li>'
            f'<li><a href="{href("delayed-games-2027.html", 1)}">Every delayed game of 2027</a></li></ul></div></section>')
    first = dated[0] if dated else None
    big_week = (f"The busiest week has {len(busiest)} launches: " + ", ".join(g["title"] for g in busiest) + ".") if len(busiest) > 1 else f"Launches are spread across {mname}."
    faqs = [
        (f"What games come out in {mname} 2027?", f"{len(games)} games are on our list for {mname} 2027, including " + ", ".join(g["title"] for g in games[:5]) + ". The full list with dates and consoles is above."),
        (f"What is the first game out in {mname} 2027?", (f"{first['title']}, on {nice_date(first)}." if first else "No exact dates are confirmed yet.")),
        (f"What is the busiest week of {mname} 2027?", big_week),
        (f"Which {mname} 2027 games were delayed?", (f"{len(_mdel)}: " + ", ".join(g["title"] for g in _mdel) + ".") if _mdel else f"None of the {mname} 2027 games we track have been delayed so far."),
        (f"Are any {mname} 2027 games on Xbox Game Pass?", ("Yes: " + ", ".join(g["title"] for g in _mgp) + ".") if _mgp else f"None of the {mname} 2027 games we track are confirmed for Game Pass yet."),
    ] + [(f"Which {mname} 2027 games are on {l2}?", (f"{pc[p2]}: " + ", ".join(g["title"] for g in games if p2 in g["platforms"]) + ".") if pc[p2] else f"None of the {mname} 2027 games we track are confirmed for {l2} yet.") for p2, s2, l2 in PLAT_PAGES if p2 in ("PS5", "Switch 2")]
    page(f, f"Games Coming Out in {mname} 2027 ({len(games)} Games): Dates and Consoles | DayOneDrop"[:90],
         f"All {len(games)} video games releasing in {mname} 2027 on PS5, Xbox, PC and Switch 2, in date order with platforms and delays. Checked {UPDATED}."[:160],
         body, 1, faqs, crumbs=[("Home", DOMAIN + "/"), ("2027 calendar", canon("calendar.html")), (f"{mname} 2027", canon(f))])

# ---------------- LATER 2027 HUB (25 Nov 2026): covers Jul-Dec + undated, replaces thin month pages ----------------
_late = [g for g in GAMES if g["month"] >= 5 and g["month"] not in month_pages_list()]
_late.sort(key=lambda g: (0 if g["date"] else 1, g["date"] or "", g["month"], g["title"]))
_l_dated = [g for g in _late if g["date"]]
_l_win = [g for g in _late if not g["date"] and g["window"] and g["window"] != "2027"]
_l_tba = [g for g in _late if not g["date"] and (not g["window"] or g["window"] == "2027")]
def _lsec(h, gs, note):
    if not gs: return ""
    return f'<div class="sec-head"><h2>{h}</h2></div><p class="muted">{note}</p><div class="board">' + "".join(mrow(g) for g in gs) + '</div>'
_lbody = (f'<section><div class="wrap" style="max-width:860px"><h1>Games Coming Out Later in 2027: May to December</h1>'
    f'<p class="lede">Most 2027 dates announced so far sit in the first four months. Here is everything after that: {len(_l_dated)} dated game{"s" if len(_l_dated)!=1 else ""}, '
    f'{len(_l_win)} with a season or window, and {len(_l_tba)} confirmed only for "2027". No game has an exact July, August, September, October or November 2027 date yet; '
    f'publishers usually fill those months at summer showcases (Summer Game Fest, Xbox Games Showcase, gamescom). We add each date the day it is announced.</p>'
    + _lsec("Dated games, May to December 2027", _l_dated, "Exact release dates confirmed by the publisher.")
    + _lsec("Games with a 2027 window", _l_win, "A season or half-year has been given, but no day.")
    + _lsec("Confirmed for 2027, date TBA", _l_tba, "Announced for 2027 with no month. These are the most likely to slip into 2028.")
    + f'<div class="sec-head"><h2>Earlier in 2027</h2></div><ul>' + "".join(f'<li><a href="{href("months/" + MONTH_SLUGS[m - 1] + ".html", 0)}">Games coming out in {MONTHS[m - 1]} 2027</a></li>' for m in month_pages_list())
    + f'<li><a href="{href("calendar.html", 0)}">Full 2027 release calendar</a></li><li><a href="{href("delayed-games-2027.html", 0)}">Games delayed to 2027</a></li></ul></div></section>')
_lfaq = [
    ("Are there any games coming out in July to November 2027?", "Not with exact dates yet. As of " + UPDATED + ", no game we track has a confirmed day between July and November 2027. " + (", ".join(g["title"] for g in _l_win[:4]) + " have windows that may land there." if _l_win else "")),
    ("Which 2027 games have no release date yet?", (", ".join(g["title"] for g in _l_tba) + " are confirmed for 2027 with no month.") if _l_tba else "Every tracked game has at least a window."),
    ("When will later 2027 dates be announced?", "Most are revealed at June showcases (Summer Game Fest, Xbox Games Showcase) and at gamescom in August. Fall dates are often set by then."),
]
page("later-2027.html", f"Games Coming Out Later in 2027 (May–Dec, TBA): All {len(_late)} | DayOneDrop",
     f"Every game coming out later in 2027: {len(_l_dated)} dated, {len(_l_win)} with a window and {len(_l_tba)} TBA, plus which have no July–November date yet. Updated {UPDATED}."[:160],
     _lbody, 0, _lfaq, crumbs=[("Home", DOMAIN + "/"), ("Later 2027 games", canon("later-2027.html"))])

# ---------------- RELEASE CLASH FINDER (22 Nov 2026) ----------------
# Built only from dated games in games.json. Weeks run Monday to Sunday.
def _monday(g):
    d = datetime.date.fromisoformat(g["date"])
    return d - datetime.timedelta(days=d.weekday())
def _dm(d):
    return f"{d.day} {MONTHS[d.month - 1]}"
_wk = {}
for _g in GAMES:
    if _g["date"]:
        _wk.setdefault(_monday(_g), []).append(_g)
_clash_weeks = sorted([(k, sorted(v, key=lambda x: x["date"])) for k, v in _wk.items() if len(v) >= 2], key=lambda kv: (-len(kv[1]), kv[0]))
_days = {}
for _g in GAMES:
    if _g["date"]:
        _days.setdefault(_g["date"], []).append(_g)
_same_days = sorted([(k, v) for k, v in _days.items() if len(v) >= 2])
def _gname(g, depth=0):
    return f'<a href="{href("games/" + g["slug"] + ".html", depth)}">{e(g["title"])}</a>' if g["page"] else e(g["title"])
def _week_label(mon):
    sun = mon + datetime.timedelta(days=6)
    return f"{_dm(mon)} to {_dm(sun)} {sun.year}"
def _cw_block(mon, gs):
    rows = "".join(f'<div class="row"><span>{_gname(g)}<br><span class="muted">{e(", ".join(g["platforms"]) or "Platforms TBC")}</span></span><b>{e(nice_date(g))}</b></div>' for g in gs)
    return (f'<div class="tool" style="margin-bottom:14px"><div class="sec-head" style="margin:0"><h3 style="margin:0;font-size:1.15rem">Week of {e(_week_label(mon))}</h3>'
            f'<span class="mono amber">{len(gs)} games</span></div><div class="out">{rows}</div></div>')
_top = _clash_weeks[0] if _clash_weeks else None
_top_day = max(_same_days, key=lambda kv: len(kv[1])) if _same_days else None
_plat_clash = []
for _p, _s, _l in PLAT_PAGES_FOOT:
    _pw = {}
    for _g in GAMES:
        if _g["date"] and _p in _g["platforms"]:
            _pw.setdefault(_monday(_g), []).append(_g)
    if _pw:
        _m, _gs = max(_pw.items(), key=lambda kv: (len(kv[1]), -kv[0].toordinal()))
        _plat_clash.append((_l, _s, _m, _gs))
# Refresh 24 Nov 2026: big-game clashes (games with a full guide) and quiet gaps
_bigd = sorted([g for g in GAMES if g["page"] and g["date"]], key=lambda x: x["date"])
def _dd(a, b): return (datetime.date.fromisoformat(b["date"]) - datetime.date.fromisoformat(a["date"])).days
_big_pairs = [(a, b2, _dd(a, b2)) for i, a in enumerate(_bigd) for b2 in _bigd[i + 1:] if _dd(a, b2) <= 7]
_alld = sorted([g for g in GAMES if g["date"]], key=lambda x: x["date"])
_gaps_all = sorted([(a, b2, _dd(a, b2)) for a, b2 in zip(_alld, _alld[1:])], key=lambda x: -x[2])
_gaps_big = sorted([(a, b2, _dd(a, b2)) for a, b2 in zip(_bigd, _bigd[1:])], key=lambda x: -x[2])
_quick = ""
if _top:
    _quick = (f"The most crowded week of 2027 so far is {_week_label(_top[0])}, with {len(_top[1])} launches: "
              + ", ".join(g["title"] for g in _top[1]) + ".")
    if _top_day:
        _quick += f" The busiest single day is {nice_date(_top_day[1][0])}, when {len(_top_day[1])} games come out."
    if _big_pairs:
        _quick += f" {len(_big_pairs)} pairs of big games launch within a week of each other, such as {_big_pairs[0][0]['title']} and {_big_pairs[0][1]['title']}."
_picker = "".join(f'<label class="clash-opt"><input type="checkbox" value="{e(g["slug"])}"> <span>{e(g["title"])}</span> <span class="muted mono">{e(short_date(g))}</span></label>' for g in sorted([g for g in GAMES if g["date"]], key=lambda x: x["date"]))
clash_tool = f'''<div class="tool" id="clash-tool"><h2 style="font-size:1.5rem;margin-top:0">Do my games clash?</h2>
<p class="muted">Tick the games you plan to buy (your ★ list is ticked for you). We show which ones land close together and how many days you get between each launch.</p>
<label for="clash-gap">Count it as a clash if games are within</label>
<select id="clash-gap"><option value="0">the same day</option><option value="7" selected>7 days</option><option value="14">14 days</option><option value="30">30 days</option></select>
<div class="clash-list" role="group" aria-label="Pick games">{_picker}</div>
<div class="btns" style="margin-top:10px;display:flex;gap:8px;flex-wrap:wrap"><button class="btn sm" type="button" id="clash-star">Use my ★ list</button><button class="btn line sm" type="button" id="clash-clear">Clear</button></div>
<div class="out" id="clash-out" aria-live="polite"></div></div>'''
clash_body = (f'<header class="hero"><div class="wrap"><span class="kicker">Clash finder</span>'
              f'<h1>2027 release clashes:<br><span class="amber">which games launch the same week?</span></h1>'
              f'<p class="lead">Big games landing days apart means less time to play each one and a bigger bill. Here is every crowded week of 2027, plus a checker for your own list.</p>'
              f'<p class="muted" style="margin:0">Last checked {e(UPDATED)} · {sum(1 for g in GAMES if g["date"])} dated games</p></div></header>'
              f'<section><div class="wrap"><div class="out" style="margin-bottom:24px"><div class="row"><span><strong>Quick answer:</strong> {e(_quick)}</span></div></div>'
              f'{clash_tool}</div></section>'
              + AD.format("clash-mid") +
              f'<section><div class="wrap"><div class="sec-head"><h2>Which weeks of 2027 have the most game releases?</h2><span class="muted">{len(_clash_weeks)} weeks with 2+ games</span></div>'
              f'<p class="muted">Weeks run Monday to Sunday, busiest first.</p>'
              + "".join(_cw_block(m, gs) for m, gs in _clash_weeks) +
              f'<div class="sec-head" style="margin-top:28px"><h2>Which 2027 games come out on the same day?</h2><span class="muted">{len(_same_days)} days</span></div>'
              f'<div class="out" style="margin-bottom:28px">'
              + "".join(f'<div class="row"><span>{", ".join(_gname(g) for g in gs)}</span><b>{e(nice_date(gs[0]))}</b></div>' for _, gs in _same_days) +
              f'</div><div class="sec-head"><h2>What is the busiest week on my console?</h2></div><div class="out" style="margin-bottom:28px">'
              + "".join(f'<div class="row"><span><a href="{href("platforms/" + s + ".html", 0)}">{e(l)}</a>: {", ".join(e(g["title"]) for g in gs)}</span><b>{len(gs)} · {e(_dm(m))}</b></div>' for l, s, m, gs in _plat_clash) +
              f'</div><div class="sec-head"><h2>Which big 2027 games launch within a week of each other?</h2><span class="muted">{len(_big_pairs)} pairs</span></div>'
              f'<p class="muted">Big games here means games with a full DayOneDrop release guide. Days between the two launches on the right.</p><div class="out" style="margin-bottom:28px">'
              + ("".join(f'<div class="row"><span>{_gname(a)} ({e(short_date(a))}) and {_gname(b2)} ({e(short_date(b2))})</span><b>{"same day" if d == 0 else str(d) + (" day" if d == 1 else " days")}</b></div>' for a, b2, d in _big_pairs) or '<div class="empty">No big games launch within a week of each other yet.</div>') +
              f'</div><div class="sec-head"><h2>When is the quietest stretch of 2027?</h2></div>'
              f'<p class="muted">The longest waits between one dated launch and the next. Good windows to catch up on your backlog.</p><div class="out" style="margin-bottom:12px">'
              + "".join(f'<div class="row"><span>{_gname(a)} ({e(short_date(a))}) → {_gname(b2)} ({e(short_date(b2))})</span><b>{d} days</b></div>' for a, b2, d in _gaps_all[:3]) +
              f'</div><p class="muted">Between big games only, the longest wait is ' + (f'{e(str(_gaps_big[0][2]))} days, from {_gname(_gaps_big[0][0])} to {_gname(_gaps_big[0][1])}' if _gaps_big else 'not known yet') + '.</p>'
              f'<div class="sec-head" style="margin-top:28px"><h2>Related tools</h2></div><ul>'
              f'<li><a href="{href("backlog-planner-2027.html", 0)}">2027 backlog planner</a>: will you finish before the next launch?</li>'
              f'<li><a href="{href("biggest-games-2027.html", 0)}">The biggest games of 2027</a>, ranked, with a top list maker</li>'
              f'<li><a href="{href("horror-games-2027.html", 0)}">Every horror game of 2027</a>, with a console filter</li>'
              f'<li><a href="{href("tools.html", 0)}">What is coming to my console</a> and the busiest months chart</li>'
              f'<li><a href="{href("delayed-games-2027.html", 0)}">Games delayed to 2027</a>: dates that already moved</li>'
              f'<li><a href="{href("calendar.html", 0)}">The full 2027 release calendar</a> with calendar reminders</li></ul></div></section>')
clash_faq = []
if _top:
    clash_faq.append(("What is the busiest week for game releases in 2027?", _quick))
if _same_days:
    clash_faq.append(("Which 2027 games release on the same day?", " ".join(f"{nice_date(gs[0])}: " + ", ".join(g["title"] for g in gs) + "." for _, gs in _same_days)))
if _big_pairs:
    clash_faq.append(("Which big 2027 games come out in the same week?", " ".join(f"{a['title']} ({nice_date(a)}) and {b2['title']} ({nice_date(b2)})." for a, b2, d in _big_pairs)))
if _gaps_all:
    clash_faq.append(("When is the quietest time for new games in 2027?", f"The longest wait between dated launches is {_gaps_all[0][2]} days, from {_gaps_all[0][0]['title']} ({nice_date(_gaps_all[0][0])}) to {_gaps_all[0][1]['title']} ({nice_date(_gaps_all[0][1])}). Dates later in 2027 are still being announced, so this can shrink."))
clash_faq.append(("Does a clash mean a game will be delayed?", "Not always. Publishers do sometimes move a date to avoid a bigger launch, but a clash on its own is not a delay. We only change a date when the publisher or two trusted outlets confirm it."))
clash_faq.append(("How does the clash checker work?", "Tick the games you want and pick a gap, such as 7 days. The checker lists every pair of your games that launch within that gap and shows the days between each launch. It runs in your browser and nothing is sent anywhere."))
page("release-clashes-2027.html", "2027 Release Clashes: Games Launching the Same Week | DayOneDrop",
     (f"Which 2027 games launch the same week? Crowded weeks, big-game clashes, the quietest gaps and a free clash checker for your list. Checked {UPDATED}.")[:160],
     clash_body, 0, clash_faq, crumbs=[("Home", DOMAIN + "/"), ("Tools", canon("tools.html")), ("Release clashes 2027", canon("release-clashes-2027.html"))])


# ---------------- CONSOLE EXCLUSIVES 2027 (22 Nov 2026) ----------------
# Built from games.json platforms (2-source checked). Ports in PORTS are listed separately so they are never called exclusives.
_ex = {p: [g for g in GAMES if is_excl(g, p)] for p in PLATS}
_ports = [g for g in GAMES if g["slug"] in PORTS]
_skip = {p: [g for g in GAMES if g["platforms"] and p not in g["platforms"]] for p in PLATS}
_all4 = [g for g in GAMES if all(p in g["platforms"] for p in PLATS)]
_lab = {p: l for p, s2, l in PLAT_PAGES_FOOT}
_pslug = {p: s2 for p, s2, l in PLAT_PAGES_FOOT}
def _xrow(g, note=""):
    return (f'<div class="row"><span><strong>{_gname(g)}</strong><br><span class="muted">{e(note or g.get("about") or "")}</span>'
            f'<br><span class="muted">{e(g.get("genre") or "")}</span></span><b>{e(nice_date(g))}</b></div>')
_ex_n = sum(len(v) for v in _ex.values())
_ex_quick = (f"We count {_ex_n} console exclusives among the {len(GAMES)} games of 2027 we track. "
             + " ".join(f"{_lab[p]}: {len(_ex[p])}" + (f" ({', '.join(g['title'] for g in _ex[p])})." if _ex[p] else ".") for p in PLATS)
             + " Fable, made by Xbox studio Playground Games, launches on Xbox, PS5 and PC on the same day.")
_xsec = ""
for p in PLATS:
    rows = "".join(_xrow(g) for g in _ex[p]) or f'<div class="row"><span>No {e(_lab[p])}-only games on our 2027 board right now.</span><b>0</b></div>'
    _xsec += (f'<div class="sec-head"><h2>Which 2027 games are only on {e(_lab[p])}?</h2><span class="muted">{len(_ex[p])}</span></div>'
              f'<div class="out" style="margin-bottom:28px">{rows}</div>')
_mx = "".join(f'<tr><td class="t">{_gname(g)}</td>' + "".join(f'<td class="p">{"✓" if p in g["platforms"] else "-"}</td>' for p in PLATS) + f'<td class="d"><span>{e(short_date(g))}</span></td></tr>'
              for g in sorted(GAMES, key=lambda x: (x["month"], x["date"] or "9999")))
_matrix = (f'<div class="board"><div class="board-top"><span class="board-title">WHO GETS WHAT · 2027</span></div><div class="board-scroll"><table class="dep">'
           f'<thead><tr><th>Game</th>' + "".join(f'<th>{e(p)}</th>' for p in PLATS) + '<th>Date</th></tr></thead><tbody>' + _mx + '</tbody></table></div></div>')
_chips = "".join(f'<button class="chip" type="button" data-own="{e(p)}" aria-pressed="false">{e(p)}</button>' for p in PLATS)
_miss_tool = (f'<div class="tool" id="miss-tool"><h2 style="font-size:1.5rem;margin-top:0">Which 2027 games will I miss?</h2>'
              f'<p class="muted">Tap the consoles you own. We show how many of the {len(GAMES)} tracked 2027 games you can play, the ones you would miss, and which extra console would add the most.</p>'
              f'<div class="chips" role="group" aria-label="Consoles you own" style="margin-bottom:12px">{_chips}</div>'
              f'<div class="out" id="miss-out" aria-live="polite"></div></div>')
# Refresh 24 Nov 2026: next exclusive countdown, per-console counts, undated exclusives, guides.
_ex_all = sorted([g for p in PLATS for g in _ex[p]], key=lambda x: (x["date"] or "9999", x["month"]))
_ex_dated = [g for g in _ex_all if g["date"] and g["date"] >= UPDATED]
_ex_undated = [g for g in _ex_all if not g["date"]]
_ex_guides = [g for g in _ex_all if g["page"]]
_ex_next = _ex_dated[0] if _ex_dated else None
_ex_next_html = ""
if _ex_next:
    _ex_next_html = (f'<div class="sec-head"><h2>Which 2027 exclusive comes out next?</h2><span class="muted">{e(_lab[_ex_next["platforms"][0]])} only</span></div>'
        f'<div class="tool" style="margin-bottom:28px"><p style="margin-top:0"><strong>{_gname(_ex_next)}</strong> launches {e(nice_date(_ex_next))} on {e(_lab[_ex_next["platforms"][0]])} only.</p>'
        f'<div class="cdw"><span class="lbl">Countdown to launch</span><div class="cd" data-countdown="{_ex_next["date"]}">'
        '<div class="cd-unit"><span class="flaps" data-u="0"></span><span>Days</span></div><div class="cd-unit"><span class="flaps" data-u="1"></span><span>Hrs</span></div>'
        '<div class="cd-unit"><span class="flaps" data-u="2"></span><span>Min</span></div><div class="cd-unit"><span class="flaps" data-u="3"></span><span>Sec</span></div></div></div>'
        + ('<p class="muted" style="margin-bottom:0">After that: ' + ", ".join(f'{_gname(g)} ({e(short_date(g))}, {e(_lab[g["platforms"][0]])})' for g in _ex_dated[1:4]) + '.</p>' if len(_ex_dated) > 1 else '')
        + '</div>')
_ex_next_html += ('<div class="sec-head"><h2>How many exclusives does each console get in 2027?</h2></div><div class="out" style="margin-bottom:28px">'
    + "".join(f'<div class="row"><span><a href="{href("platforms/" + _pslug[p] + ".html", 0)}">{e(_lab[p])}</a>: {len([g for g in _ex[p] if g["date"]])} dated, {len([g for g in _ex[p] if not g["date"]])} with no exact date</span><b>{len(_ex[p])}</b></div>' for p in PLATS)
    + '</div>')
if _ex_undated:
    _ex_next_html += (f'<div class="sec-head"><h2>Which 2027 exclusives have no release date yet?</h2><span class="muted">{len(_ex_undated)}</span></div>'
        '<div class="out" style="margin-bottom:28px">' + "".join(_xrow(g, f'{_lab[g["platforms"][0]]} only. {g.get("about") or ""}') for g in _ex_undated) + '</div>')
if _ex_guides:
    _ex_next_html += ('<div class="sec-head"><h2>Which exclusives have a full release guide?</h2></div><ul style="margin-bottom:28px">'
        + "".join(f'<li>{_gname(g)}: {e(nice_date(g))}, {e(_lab[g["platforms"][0]])} only</li>' for g in _ex_guides) + '</ul>')
if _ex_next:
    _ex_quick += f" The next exclusive to launch is {_ex_next['title']} on {nice_date(_ex_next)}."
excl_body = (f'<header class="hero"><div class="wrap"><span class="kicker">Exclusives</span>'
             f'<h1>2027 console exclusives:<br><span class="amber">which games are only on one console?</span></h1>'
             f'<p class="lead">Every confirmed 2027 game that is only coming to PS5, Xbox, PC or Switch 2, the ports that are not really exclusives, and a checker for the games your consoles will miss.</p>'
             f'<p class="muted" style="margin:0">Last checked {e(UPDATED)} · based on announced platforms, which can still change</p></div></header>'
             f'<section><div class="wrap"><div class="out" style="margin-bottom:24px"><div class="row"><span><strong>Quick answer:</strong> {e(_ex_quick)}</span></div></div>'
             f'{_miss_tool}</div></section>' + AD.format("excl-mid") +
             f'<section><div class="wrap">{_ex_next_html}{_xsec}'
             f'<div class="sec-head"><h2>Which "exclusives" are really late ports?</h2><span class="muted">{len(_ports)}</span></div>'
             f'<p class="muted">These show up on only one console in 2027, but they are already out elsewhere.</p>'
             f'<div class="out" style="margin-bottom:28px">{"".join(_xrow(g, PORTS[g["slug"]]) for g in _ports)}</div>'
             f'<div class="sec-head"><h2>Which 2027 games skip each console?</h2></div><div class="out" style="margin-bottom:28px">'
             + "".join(f'<div class="row"><span><a href="{href("platforms/" + _pslug[p] + ".html", 0)}">{e(_lab[p])}</a> misses: {e(", ".join(g["title"] for g in _skip[p][:8]))}{" and more" if len(_skip[p]) > 8 else ""}</span><b>{len(_skip[p])} games</b></div>' for p in PLATS) +
             f'</div><div class="sec-head"><h2>Which 2027 games are on every console?</h2><span class="muted">{len(_all4)}</span></div>'
             f'<p>{e(", ".join(g["title"] for g in _all4))}.</p>'
             f'<div class="sec-head"><h2>Which consoles is every 2027 game on?</h2></div>{_matrix}'
             f'<div class="sec-head" style="margin-top:28px"><h2>Related pages and tools</h2></div><ul>'
             f'<li><a href="{href("tools.html", 0)}">What is coming to my console</a> and your launch list</li>'
             f'<li><a href="{href("release-clashes-2027.html", 0)}">2027 release clashes</a>: which games land the same week</li>'
             f'<li><a href="{href("delayed-games-2027.html", 0)}">Games delayed to 2027</a></li>'
             f'<li><a href="{href("last-gen-games-2027.html", 0)}">2027 games still coming to PS4, Xbox One and Switch 1</a></li>'
             f'<li><a href="{href("platforms/switch-2.html", 0)}">Every Switch 2 game coming in 2027</a></li>'
             f'<li><a href="{href("biggest-games-2027.html", 0)}">The biggest games of 2027</a></li></ul></div></section>')
_cnt = {p: sum(1 for g in GAMES if p in g["platforms"]) for p in PLATS}
excl_faq = [
    ("What are the PS5 exclusives of 2027?", (", ".join(f"{g['title']} ({nice_date(g)})" for g in _ex["PS5"]) + " are only announced for PS5.") if _ex["PS5"] else "None on our board right now."),
    ("Are there any Xbox exclusives in 2027?", ("Not on our board. " if not _ex["Xbox Series X|S"] else ", ".join(g["title"] for g in _ex["Xbox Series X|S"]) + ". ") + "Fable launches on Xbox Series X|S, PS5 and PC on 23 February 2027, and on Game Pass the same day."),
    ("What are the Switch 2 exclusives of 2027?", (", ".join(f"{g['title']} ({nice_date(g)})" for g in _ex["Switch 2"]) + ".") if _ex["Switch 2"] else "None on our board right now."),
    ("Is Forza Horizon 6 a PS5 exclusive?", "No. Forza Horizon 6 came out on Xbox Series X|S and PC in May 2026. The PS5 version launches 26 January 2027."),
    ("Which 2027 exclusive comes out first?", (f"{_ex_next['title']} on {nice_date(_ex_next)}, only on {_lab[_ex_next['platforms'][0]]}." if _ex_next else "None with a date right now.")),
    ("Which 2027 exclusives have no exact release date?", (", ".join(f"{g['title']} ({nice_date(g)}, {_lab[g['platforms'][0]]})" for g in _ex_undated) + ".") if _ex_undated else "Every exclusive on our board has a date."),
    ("Which console gets the most 2027 games?", "On our board: " + ", ".join(f"{_lab[p]} {_cnt[p]}" for p in sorted(PLATS, key=lambda q: -_cnt[q])) + "."),
]
page("exclusives-2027.html", "2027 Console Exclusives: PS5, Xbox, Switch 2, PC | DayOneDrop",
     (f"Every 2027 console exclusive: PS5-only, Switch 2-only and PC-only games, which are late ports, and a checker for games your console misses. Checked {UPDATED}.")[:160],
     excl_body, 0, excl_faq, crumbs=[("Home", DOMAIN + "/"), ("All games", canon("games.html")), ("Console exclusives 2027", canon("exclusives-2027.html"))])


# ---------------- RPGs OF 2027 (22 Nov 2026) ----------------
# Every tracked game whose genre includes "RPG". Built only from games.json (dates/platforms 2-source checked).
_rpg = sorted([g for g in GAMES if "RPG" in (g.get("genre") or "")], key=lambda x: (x["month"], x["date"] or "9999"))
_rpg_dated = [g for g in _rpg if g["date"]]
_rpg_action = [g for g in _rpg if g.get("genre") == "Action RPG"]
_rpg_other = [g for g in _rpg if g.get("genre") != "Action RPG"]
_rpg_cnt = {p: [g for g in _rpg if p in g["platforms"]] for p in PLATS}
# busiest 30-day stretch of dated RPG launches
_rb = (0, None, [])
for _i, _g in enumerate(_rpg_dated):
    _s = datetime.date.fromisoformat(_g["date"])
    _in = [x for x in _rpg_dated if 0 <= (datetime.date.fromisoformat(x["date"]) - _s).days <= 29]
    if len(_in) > _rb[0]:
        _rb = (len(_in), _s, _in)
_rb_n, _rb_start, _rb_games = _rb
_rb_end = datetime.date.fromisoformat(_rb_games[-1]["date"]) if _rb_games else None
_rpg_months = {}
for _g in _rpg:
    _rpg_months.setdefault(_g["month"] if _g["date"] else 13, []).append(_g)
def _rrow(g):
    plats = ", ".join(g["platforms"]) or "Platforms TBC"
    style = "action" if g.get("genre") == "Action RPG" else "other"
    return (f'<div class="row" data-rpg-style="{style}" data-plat="{e("|".join(g["platforms"]))}"><span><strong>{_gname(g)}</strong>'
            f'<br><span class="muted">{e(g.get("about") or "")}</span><br><span class="muted">{e(g.get("genre") or "")} · {e(plats)}</span></span>'
            f'<b>{e(nice_date(g))}</b></div>')
_rpg_secs = ""
for _m in sorted(_rpg_months):
    _lbl = f"{MONTHS[_m - 1]} 2027" if _m <= 12 else "No exact date yet"
    _rpg_secs += (f'<div class="sec-head"><h3 style="margin:0;font-size:1.2rem">{e(_lbl)}</h3><span class="muted">{len(_rpg_months[_m])}</span></div>'
                  f'<div class="out" style="margin-bottom:22px">{"".join(_rrow(g) for g in _rpg_months[_m])}</div>')
_rpg_quick = (f"We track {len(_rpg)} RPGs for 2027, {len(_rpg_dated)} with an exact date. The first is {_rpg_dated[0]['title']} on {nice_date(_rpg_dated[0])}. "
              f"The biggest crunch is {_dm(_rb_start)} to {_dm(_rb_end)} 2027, with {_rb_n} RPGs in 30 days, including "
              + ", ".join(g["title"] for g in _rb_games[:4]) + ".") if _rpg_dated else "No dated RPGs yet."
_rchips = ('<div class="chips" role="group" aria-label="Console" style="margin-bottom:10px"><button class="chip" type="button" data-rpg-plat="" aria-pressed="true">All consoles</button>'
           + "".join(f'<button class="chip" type="button" data-rpg-plat="{e(p)}" aria-pressed="false">{e(p)}</button>' for p in PLATS) + '</div>'
           '<div class="chips" role="group" aria-label="RPG style"><button class="chip" type="button" data-rpg-s="" aria-pressed="true">All RPGs</button>'
           '<button class="chip" type="button" data-rpg-s="action" aria-pressed="false">Action RPGs</button>'
           '<button class="chip" type="button" data-rpg-s="other" aria-pressed="false">JRPG, tactical and classic RPGs</button></div>')
_rpg_switch = _rpg_cnt["Switch 2"]
_rpg_only = {p: [g for g in _rpg if g["platforms"] == [p]] for p in PLATS}
_rpg_del = [g for g in _rpg if g["status"] == "delayed"]
_rpg_gp = [g for g in _rpg if g["slug"] in GP_TRACKED_ALL]
_rpg_lg = [g for g in _rpg if g.get("lastgen")]
rpg_body = (f'<header class="hero"><div class="wrap"><span class="kicker">RPGs</span>'
            f'<h1>Every RPG coming in 2027:<br><span class="amber">{len(_rpg)} games, dates and consoles.</span></h1>'
            f'<p class="lead">2027 is packed with role-playing games: Persona 4 Revival, Fable, Final Fantasy VII Revelation, Exodus, Kingdom Hearts IV and more. Here is every one we track, in release order, with a filter for your console.</p>'
            f'<p class="muted" style="margin:0">Last checked {e(UPDATED)} · dates confirmed by publishers or two trusted outlets</p></div></header>'
            f'<section><div class="wrap"><div class="out" style="margin-bottom:24px"><div class="row"><span><strong>Quick answer:</strong> {e(_rpg_quick)}</span></div></div>'
            f'<div class="tool" id="rpg-tool"><h2 style="font-size:1.5rem;margin-top:0">Which 2027 RPGs can I play?</h2>'
            f'<p class="muted">Pick your console and the kind of RPG you like. The list below updates as you tap.</p>{_rchips}'
            f'<p class="mono amber" id="rpg-count" aria-live="polite" style="margin:12px 0 0">{len(_rpg)} RPGs</p></div></div></section>'
            + AD.format("rpg-mid") +
            f'<section><div class="wrap" id="rpg-list"><div class="sec-head"><h2>When do the 2027 RPGs come out?</h2><span class="muted">{len(_rpg)}</span></div>{_rpg_secs}'
            f'<p class="empty" id="rpg-none" hidden>No tracked 2027 RPGs match that filter yet.</p></div></section>'
            f'<section><div class="wrap">'
            f'<div class="sec-head"><h2>When is the big RPG crunch of 2027?</h2><span class="mono amber">{_rb_n} in 30 days</span></div>'
            f'<p>From {e(_dm(_rb_start))} to {e(_dm(_rb_end))} 2027, {_rb_n} RPGs launch. If you want to finish one before the next arrives, plan this stretch first.</p>'
            f'<div class="out" style="margin-bottom:28px">' + "".join(f'<div class="row"><span>{_gname(g)}</span><b>{e(nice_date(g))}</b></div>' for g in _rb_games) + '</div>'
            f'<div class="sec-head"><h2>How many 2027 RPGs are on each console?</h2></div><div class="out" style="margin-bottom:28px">'
            + "".join(f'<div class="row"><span><a href="{href("platforms/" + _pslug[p] + ".html", 0)}">{e(_lab[p])}</a>'
                      + (f'<br><span class="muted">Only here: {e(", ".join(g["title"] for g in _rpg_only[p]))}</span>' if _rpg_only[p] else "")
                      + f'</span><b>{len(_rpg_cnt[p])} RPGs</b></div>' for p in sorted(PLATS, key=lambda q: -len(_rpg_cnt[q]))) +
            f'</div><div class="sec-head"><h2>Which 2027 RPGs are action RPGs?</h2></div>'
            f'<p><strong>Action RPGs ({len(_rpg_action)}):</strong> {e(", ".join(g["title"] for g in _rpg_action))}.</p>'
            f'<p><strong>JRPG, tactical and classic RPGs ({len(_rpg_other)}):</strong> {e(", ".join(g["title"] for g in _rpg_other))}.</p>'
            f'<p class="muted">Genre labels follow how each game is announced. Star the ones you want on the <a href="{href("index.html", 0)}#board">departures board</a> to get countdowns.</p>'
            f'<div class="sec-head" style="margin-top:28px"><h2>Which 2027 RPGs have been delayed?</h2><span class="muted">{len(_rpg_del)}</span></div>'
            f'<div class="out" style="margin-bottom:28px">' + ("".join(f'<div class="row"><span>{_gname(g)}</span><b>{e(nice_date(g))}</b></div>' for g in _rpg_del) or '<div class="empty">No delayed RPGs.</div>') + '</div>'
            f'<div class="sec-head"><h2>Which 2027 RPGs are on Xbox Game Pass?</h2><span class="muted">{len(_rpg_gp)}</span></div>'
            f'<div class="out" style="margin-bottom:28px">' + ("".join(f'<div class="row"><span>{_gname(g)}</span><b>{e(nice_date(g))}</b></div>' for g in _rpg_gp) or '<div class="empty">None announced yet.</div>') + '</div>'
            f'<div class="sec-head"><h2>Which 2027 RPGs are on PS4 or Switch 1?</h2><span class="muted">{len(_rpg_lg)}</span></div>'
            f'<div class="out" style="margin-bottom:28px">' + ("".join(f'<div class="row"><span>{_gname(g)}<br><span class="muted">Also on {e(", ".join("Switch 1" if x == "Switch" else x for x in g["lastgen"]))}</span></span><b>{e(nice_date(g))}</b></div>' for g in _rpg_lg) or '<div class="empty">None confirmed.</div>') + '</div>'
            f'<div class="sec-head" style="margin-top:28px"><h2>Related pages and tools</h2></div><ul>'
            f'<li><a href="{href("games-by-genre-2027.html", 0)}">2027 games by genre</a>: horror, shooters, platformers and more</li>'
            f'<li><a href="{href("backlog-planner-2027.html", 0)}">2027 backlog planner</a>: can you finish one RPG before the next?</li>'
            f'<li><a href="{href("game-pass-2027.html", 0)}">Every 2027 Game Pass game</a> and <a href="{href("last-gen-games-2027.html", 0)}">2027 games on PS4 and Switch 1</a></li>'
            f'<li><a href="{href("release-clashes-2027.html", 0)}">2027 release clashes</a>: check if your RPGs land the same week</li>'
            f'<li><a href="{href("exclusives-2027.html", 0)}">2027 console exclusives</a> and which games your consoles will miss</li>'
            f'<li><a href="{href("after-gta-6.html", 0)}">What to play after GTA 6</a></li></ul></div></section>')
_ff = _gby.get("final-fantasy-vii-revelation") if "_gby" in globals() else next((g for g in GAMES if g["slug"] == "final-fantasy-vii-revelation"), None)
rpg_faq = [
    ("What RPGs are coming out in 2027?", f"We track {len(_rpg)}: " + ", ".join(f"{g['title']} ({nice_date(g)})" for g in _rpg) + "."),
    ("What is the first big RPG of 2027?", f"{_rpg_dated[0]['title']} launches first, on {nice_date(_rpg_dated[0])}." if _rpg_dated else "None are dated yet."),
    ("When is the busiest month for RPGs in 2027?", f"The busiest stretch is {_dm(_rb_start)} to {_dm(_rb_end)} 2027, with {_rb_n} RPGs in 30 days."),
    ("Which 2027 RPGs are coming to Switch 2?", f"{len(_rpg_switch)} so far: " + ", ".join(g["title"] for g in _rpg_switch) + "."),
]
rpg_faq += [
    ("Which 2027 RPGs have been delayed?", (f"{len(_rpg_del)}: " + ", ".join(f"{g['title']} (now {nice_date(g)})" for g in _rpg_del) + ".") if _rpg_del else "None so far."),
    ("Which 2027 RPGs are on Xbox Game Pass?", (", ".join(g["title"] for g in _rpg_gp) + ".") if _rpg_gp else "None announced yet."),
    ("Which 2027 RPGs can I play on PS4 or the original Switch?", (", ".join(g["title"] + " (" + ", ".join("Switch 1" if x == "Switch" else x for x in g["lastgen"]) + ")" for g in _rpg_lg) + ".") if _rpg_lg else "None confirmed yet."),
]
if _ff:
    rpg_faq.append(("When does Final Fantasy VII Revelation come out?", f"{nice_date(_ff)}, on {', '.join(_ff['platforms'])}."))
page("rpgs-2027.html", f"Every RPG Coming in 2027: Dates and Consoles ({len(_rpg)} Games) | DayOneDrop"[:90],
     f"All {len(_rpg)} RPGs releasing in 2027, in date order: Persona 4 Revival, Fable, Final Fantasy VII Revelation and more, with a console filter. Checked {UPDATED}."[:160],
     rpg_body, 0, rpg_faq, crumbs=[("Home", DOMAIN + "/"), ("All games", canon("games.html")), ("RPGs 2027", canon("rpgs-2027.html"))])


# ---------------- 2027 GAMES BY GENRE (23 Nov 2026) ----------------
# Groups every tracked game by its announced genre label (games.json "genre"). First matching group wins.
GENRE_GROUPS = [
    ("horror", "Horror", "horror games", lambda s: "horror" in s),
    ("shooter", "Shooters", "shooters", lambda s: "shooter" in s),
    ("rpg", "RPGs", "RPGs", lambda s: "rpg" in s),
    ("platformer", "Platformers and Metroidvanias", "platformers", lambda s: "platformer" in s or "metroidvania" in s),
    ("action", "Action and adventure", "action and adventure games", lambda s: s in ("action", "action adventure", "adventure", "mystery adventure")),
    ("sim", "Sims, strategy and racing", "sims, strategy and racing games", lambda s: any(k in s for k in ("sim", "builder", "racing", "strategy"))),
    ("other", "Fighting, card and other games", "fighting, card and other games", lambda s: True),
]
def _genre_key(g):
    s = (g.get("genre") or "").lower()
    for k, _, _, f in GENRE_GROUPS:
        if f(s):
            return k
    return "other"
_gsort = lambda x: (x["month"], x["date"] or "9999")
_gen = {k: sorted([g for g in GAMES if _genre_key(g) == k], key=_gsort) for k, _, _, _ in GENRE_GROUPS}
_gen = {k: v for k, v in _gen.items() if v}
_gen_meta = {k: (n, low) for k, n, low, _ in GENRE_GROUPS}
_gen_rank = sorted(_gen, key=lambda k: -len(_gen[k]))
def _gen_first(k):
    d = [g for g in _gen[k] if g["date"]]
    return d[0] if d else None
_gen_quick = (f"We track {len(GAMES)} games for 2027. The biggest genre is {_gen_meta[_gen_rank[0]][1]} ({len(_gen[_gen_rank[0]])}), then "
              + ", ".join(f"{_gen_meta[k][1]} ({len(_gen[k])})" for k in _gen_rank[1:4]) + ".")
if "horror" in _gen:
    _gen_quick += f" There are {len(_gen['horror'])} horror games, starting with {_gen_first('horror')['title']} on {nice_date(_gen_first('horror'))}." if _gen_first("horror") else ""
def _genrow(g):
    return (f'<div class="row" data-genre="{_genre_key(g)}" data-plat="{e("|".join(g["platforms"]))}"><span><strong>{_gname(g)}</strong>'
            f'<br><span class="muted">{e(g["genre"])} · {e(", ".join(g["platforms"]) or "Platforms TBC")}</span></span><b>{e(nice_date(g))}</b></div>')
_gen_secs = ""
for _k in _gen:
    _n, _low = _gen_meta[_k]
    _f = _gen_first(_k)
    _lead = f'The first is {_gname(_f)} on {e(nice_date(_f))}.' if _f else "None has an exact date yet."
    _extra = f' See <a href="{href("rpgs-2027.html", 0)}">every RPG of 2027</a> for the full RPG guide.' if _k == "rpg" else (f' See <a href="{href("horror-games-2027.html", 0)}">every horror game of 2027</a> for countdowns and delays.' if _k == "horror" else (f' See <a href="{href("fighting-games-2027.html", 0)}">every fighting game of 2027</a>, including Virtua Fighter Crossroads and DCKO.' if _k == "other" else ""))
    _gen_secs += (f'<div class="gen-sec" data-gsec="{_k}"><div class="sec-head"><h2 id="{_k}">What {e(_low)} come out in 2027?</h2><span class="muted">{len(_gen[_k])}</span></div>'
                  f'<p class="muted">{_lead}{_extra}</p><div class="out" style="margin-bottom:26px">{"".join(_genrow(g) for g in _gen[_k])}</div></div>')
_gchips = ('<div class="chips" role="group" aria-label="Genre" style="margin-bottom:10px"><button class="chip" type="button" data-gen-g="" aria-pressed="true">All genres</button>'
           + "".join(f'<button class="chip" type="button" data-gen-g="{k}" aria-pressed="false">{e(_gen_meta[k][0])}</button>' for k in _gen) + '</div>'
           '<div class="chips" role="group" aria-label="Console"><button class="chip" type="button" data-gen-p="" aria-pressed="true">All consoles</button>'
           + "".join(f'<button class="chip" type="button" data-gen-p="{e(p)}" aria-pressed="false">{e(p)}</button>' for p in PLATS) + '</div>')
_gen_tbl = ('<div style="overflow-x:auto"><table class="gen-table" style="width:100%;border-collapse:collapse;font-size:.92rem"><thead><tr><th style="text-align:left;padding:6px">Genre</th>'
            + "".join(f'<th style="padding:6px">{e(p)}</th>' for p in PLATS) + '</tr></thead><tbody>'
            + "".join(f'<tr><td style="padding:6px;border-top:1px solid var(--rule)"><a href="#{k}">{e(_gen_meta[k][0])}</a></td>'
                      + "".join(f'<td style="padding:6px;text-align:center;border-top:1px solid var(--rule)" class="mono">{sum(1 for g in _gen[k] if p in g["platforms"])}</td>' for p in PLATS) + '</tr>' for k in _gen)
            + '</tbody></table></div>')
_gen_top = {p: max(_gen, key=lambda k: sum(1 for g in _gen[k] if p in g["platforms"])) for p in PLATS}
def _and(xs): return xs[0] if len(xs) == 1 else ', '.join(xs[:-1]) + ' and ' + xs[-1]
_gen_next = {k: next((g for g in _gen[k] if g["date"] and g["date"] >= UPDATED), None) for k in _gen}
_gen_und = {k: [g for g in _gen[k] if not g["date"]] for k in _gen}
_race = [g for g in GAMES if "racing" in (g.get("genre") or "").lower() or "truck" in (g.get("genre") or "").lower()]
_sport_race = ("we track " + _and([f'{_gname(g)} ({e(nice_date(g))}, {e(", ".join(g["platforms"]))})' for g in _race]) + ".") if _race else "nothing is dated yet."
_gen_quick += f" No sports game (FIFA/FC, Madden, NBA 2K) has a 2027 date yet."
gen_body = (f'<header class="hero"><div class="wrap"><span class="kicker">By genre</span>'
            f'<h1>2027 games by genre:<br><span class="amber">horror, shooters, RPGs and more.</span></h1>'
            f'<p class="lead">Looking for a scary game, a new shooter or a platformer to play in 2027? Every game we track, sorted by genre, in release order, with a filter for your console.</p>'
            f'<p class="muted" style="margin:0">Last checked {e(UPDATED)} · {len(GAMES)} games · dates confirmed by publishers or two trusted outlets</p></div></header>'
            f'<section><div class="wrap"><div class="out" style="margin-bottom:24px"><div class="row"><span><strong>Quick answer:</strong> {e(_gen_quick)}</span></div></div>'
            f'<div class="tool" id="gen-tool"><h2 style="font-size:1.5rem;margin-top:0">Which 2027 games match what I like?</h2>'
            f'<p class="muted">Tap a genre and your console. The lists below update as you tap, and your choice is remembered on this device.</p>{_gchips}'
            f'<p class="mono amber" id="gen-count" aria-live="polite" style="margin:12px 0 0">{len(GAMES)} games</p></div></div></section>'
            + AD.format("genre-mid") +
            f'<section><div class="wrap" id="gen-list">{_gen_secs}<p class="empty" id="gen-none" hidden>No tracked 2027 games match that yet. Try another console or genre.</p></div></section>'
            f'<section><div class="wrap"><div class="sec-head"><h2>Which genre has the most 2027 games on my console?</h2></div>'
            f'<p class="muted">Number of tracked 2027 games in each genre, per console.</p>{_gen_tbl}'
            f'<ul style="margin-top:16px">' + "".join(f'<li><a href="{href("platforms/" + _pslug[p] + ".html", 0)}">{e(_lab[p])}</a>: most games are {e(_gen_meta[_gen_top[p]][1])}.</li>' for p in PLATS) + '</ul>'
            f'<p class="muted">Genre labels follow how each game is announced by its publisher. A game sits in one group only.</p>'
            f'<div class="sec-head" style="margin-top:28px"><h2>What is the next game in each genre?</h2></div>'
            f'<div style="overflow-x:auto"><table class="gen-table" style="width:100%;border-collapse:collapse;font-size:.92rem"><thead><tr><th style="text-align:left;padding:6px">Genre</th><th style="text-align:left;padding:6px">Next game</th><th style="text-align:left;padding:6px">Date</th></tr></thead><tbody>'
            + "".join(f'<tr><td style="padding:6px;border-top:1px solid var(--rule)"><a href="#{k}">{e(_gen_meta[k][0])}</a></td><td style="padding:6px;border-top:1px solid var(--rule)">{_gname(_gen_next[k]) if _gen_next[k] else "No exact date yet"}</td><td style="padding:6px;border-top:1px solid var(--rule)" class="mono">{e(short_date(_gen_next[k])) if _gen_next[k] else "-"}</td></tr>' for k in _gen)
            + '</tbody></table></div>'
            f'<div class="sec-head" style="margin-top:28px"><h2>Which 2027 games have no exact date yet, by genre?</h2></div><ul>'
            + "".join(f'<li>{e(_gen_meta[k][0])}: {", ".join(_gname(g) for g in _gen_und[k])}</li>' for k in _gen if _gen_und[k]) + '</ul>'
            f'<div class="sec-head" style="margin-top:28px"><h2>Are there any sports games coming out in 2027?</h2></div>'
            f'<p>Not yet. No 2027 sports game (football, soccer, basketball, golf) has been announced with a release date. EA\'s current editions came out in 2026: College Football 27 on 9 July 2026 (PS5, Xbox Series X|S, PC) and EA Sports FC 27 on 25 September 2026 (also on Switch 2). The yearly 2027 editions are normally revealed a few months before launch, so expect news in spring and summer 2027.</p>'
            f'<p>For racing and driving games, {_sport_race}</p>'
            f'<div class="sec-head" style="margin-top:28px"><h2>Related pages and tools</h2></div><ul>'
            f'<li><a href="{href("horror-games-2027.html", 0)}">Every horror game of 2027</a>, with a console filter and countdown</li>'
            f'<li><a href="{href("fighting-games-2027.html", 0)}">Every fighting game of 2027</a>: Melty Blood, Xenoverse 3, Virtua Fighter</li>'
            f'<li><a href="{href("xbox-games-showcase-2027.html", 0)}">Xbox Games Showcase 2027</a>: which Xbox games still need a date</li>'
            f'<li><a href="{href("rpgs-2027.html", 0)}">Every RPG coming in 2027</a>, with action RPG and JRPG filters</li>'
            f'<li><a href="{href("games-like-elden-ring.html", 0)}">Games like Elden Ring</a>: soulslikes out now and in 2027</li>'
            f'<li><a href="{href("biggest-games-2027.html", 0)}">The biggest games of 2027</a> and a shareable top list maker</li>'
            f'<li><a href="{href("release-clashes-2027.html", 0)}">2027 release clashes</a>: do your picks land the same week?</li>'
            f'<li><a href="{href("backlog-planner-2027.html", 0)}">2027 backlog planner</a>: finish one before the next arrives</li></ul></div></section>')
gen_faq = [("What genre has the most games in 2027?", _gen_quick)]
for _k in _gen:
    _n, _low = _gen_meta[_k]
    gen_faq.append((f"What {_low} are coming out in 2027?", f"We track {len(_gen[_k])}: " + ", ".join(f"{g['title']} ({nice_date(g)})" for g in _gen[_k]) + "."))
gen_faq.append(("Are there any sports games coming out in 2027?", "None with a 2027 date yet. College Football 27 (9 July 2026) and EA Sports FC 27 (25 September 2026) are the current editions; the 2027 editions have not been announced."))
gen_faq.append(("What is the next 2027 game in each genre?", "; ".join(f"{_gen_meta[k][0]}: {_gen_next[k]['title']} ({nice_date(_gen_next[k])})" for k in _gen if _gen_next[k]) + "."))
gen_faq.append(("Which genre has the most 2027 games on Switch 2?", f"{_gen_meta[_gen_top['Switch 2']][0]}, with {sum(1 for g in _gen[_gen_top['Switch 2']] if 'Switch 2' in g['platforms'])} games."))
page("games-by-genre-2027.html", "Upcoming Games 2027 by Genre: Horror, Shooters, RPGs, Sports | DayOneDrop",
     f"Every 2027 game by genre: horror, shooters, RPGs, platformers, racing and sims, the next game in each genre, and are there sports games in 2027? Checked {UPDATED}."[:160],
     gen_body, 0, gen_faq, crumbs=[("Home", DOMAIN + "/"), ("All games", canon("games.html")), ("2027 games by genre", canon("games-by-genre-2027.html"))])


# ---------------- HORROR GAMES 2027 (24 Nov 2026) ----------------
# Built from games.json: genre contains "horror". Horror-adjacent picks are listed by slug and labelled.
# Neverway sits in HORROR_EXTRA because it is on PC and Switch 1 only (not a console we track); 2027 window from Gematsu + RPGFan (Aug 2026).
HORROR_ADJ = {"grave-seasons": "A farming life sim with a dark mystery underneath. GamesRadar lists it with upcoming horror games.",
              "state-of-decay-3": "Open-world zombie survival with community building. More survival than scares."}
HORROR_EXTRA = [("Neverway", "Coldblood Inc", "Horror life sim RPG, delayed from October 2026", "PC, Switch 1", "2027")]
_hor = sorted([g for g in GAMES if "horror" in (g.get("genre") or "").lower()], key=lambda x: (x["month"], x["date"] or "9999"))
_hor_adj = [g for g in GAMES if g["slug"] in HORROR_ADJ]
_hor_dated = [g for g in _hor if g["date"]]
_hor_undated = [g for g in _hor if not g["date"]]
_hor_delayed = [g for g in _hor if g["status"] == "delayed"]
_hor_next = _hor_dated[0] if _hor_dated else None
_hor_p = {p: [g for g in _hor if p in g["platforms"]] for p in PLATS}
_hor_all = [g for g in _hor if all(p in g["platforms"] for p in PLATS)]
_hor_ex = [g for g in _hor if len(g["platforms"]) == 1]
def _and(xs): return xs[0] if len(xs) == 1 else ', '.join(xs[:-1]) + ' and ' + xs[-1]
_hor_quick = (f"We track {len(_hor)} horror games for 2027. "
              + (f"The first is {_hor_next['title']} on {nice_date(_hor_next)}" + (f", then {_hor_dated[1]['title']} on {nice_date(_hor_dated[1])}" if len(_hor_dated) > 1 else "") + ". " if _hor_next else "")
              + (f"{_and([g['title'] for g in _hor_undated])} {'are' if len(_hor_undated) > 1 else 'is'} due in 2027 with no exact date yet." if _hor_undated else ""))
def _hrow(g, note=""):
    return (f'<div class="row" data-hplat="{e("|".join(g["platforms"]))}" data-hdated="{1 if g["date"] else 0}" data-slug="{e(g["slug"])}"><span><strong>{_gname(g)}</strong>'
            f'<br><span class="muted">{e(note or g.get("about") or g["genre"])}</span>'
            f'<br><span class="muted">{e(g["genre"])} · {e(g.get("dev") or "Studio TBC")} · {e(", ".join(g["platforms"]) or "Platforms TBC")}</span></span><b>{e(nice_date(g))}</b></div>')
_hchips = ('<div class="chips" role="group" aria-label="Console"><button class="chip" type="button" data-hor-p="" aria-pressed="true">All consoles</button>'
           + "".join(f'<button class="chip" type="button" data-hor-p="{e(p)}" aria-pressed="false">{e(p)}</button>' for p in PLATS) + '</div>'
           '<div class="chips" role="group" aria-label="Date" style="margin-top:10px"><button class="chip" type="button" data-hor-d="" aria-pressed="true">Any date</button>'
           '<button class="chip" type="button" data-hor-d="1" aria-pressed="false">Exact date only</button></div>')
_hor_tbl = ('<div style="overflow-x:auto"><table class="gen-table" style="width:100%;border-collapse:collapse;font-size:.92rem"><thead><tr><th style="text-align:left;padding:6px">Console</th><th style="padding:6px">Horror games</th><th style="text-align:left;padding:6px">First one</th></tr></thead><tbody>'
            + "".join(f'<tr><td style="padding:6px;border-top:1px solid var(--rule)"><a href="{href("platforms/" + _pslug[p] + ".html", 0)}">{e(_lab[p])}</a></td>'
                      f'<td style="padding:6px;text-align:center;border-top:1px solid var(--rule)" class="mono">{len(_hor_p[p])}</td>'
                      f'<td style="padding:6px;border-top:1px solid var(--rule)">{e(next((g["title"] + " (" + nice_date(g) + ")" for g in _hor_p[p] if g["date"]), "No exact date yet"))}</td></tr>' for p in PLATS)
            + '</tbody></table></div>')
_hor_body = (f'<header class="hero"><div class="wrap"><span class="kicker">Horror</span>'
             f'<h1>Horror games coming in 2027:<br><span class="amber">every date, every console.</span></h1>'
             f'<p class="lead">Every scary game we track for 2027, from Until Dawn 2 to the Resident Evil Code: Veronica remake, in release order, with a console filter and a countdown to the next one.</p>'
             f'<p class="muted" style="margin:0">Last checked {e(UPDATED)} · {len(_hor)} horror games · dates confirmed by publishers or two trusted outlets</p></div></header>'
             f'<section><div class="wrap"><div class="out" style="margin-bottom:24px"><div class="row"><span><strong>Quick answer:</strong> {e(_hor_quick)}</span></div></div>'
             f'<div class="tool" id="hor-tool"><h2 style="font-size:1.5rem;margin-top:0">Which 2027 horror games can I play on my console?</h2>'
             f'<p class="muted">Tap your console. The list updates, the countdown jumps to the next horror launch you can play, and your choice is remembered on this device.</p>{_hchips}'
             f'<div class="out" id="hor-next" style="margin-top:14px" aria-live="polite"></div>'
             f'<p class="mono amber" id="hor-count" aria-live="polite" style="margin:12px 0 0">{len(_hor)} games</p>'
             f'<div class="btns" style="margin-top:10px;display:flex;gap:8px;flex-wrap:wrap"><button class="btn sm" type="button" id="hor-add">Add these to my ★ list</button>'
             f'<a class="btn line sm" href="{href("release-clashes-2027.html", 0)}">Check them for clashes</a></div></div></div></section>'
             + AD.format("horror-mid") +
             f'<section><div class="wrap"><div class="sec-head"><h2>What horror games come out in 2027?</h2><span class="muted">{len(_hor)}</span></div>'
             f'<p class="muted">In release order. Games with only a year sit at the end.</p>'
             f'<div class="out" id="hor-list" style="margin-bottom:10px">{"".join(_hrow(g) for g in _hor)}</div><p class="empty" id="hor-none" hidden>No tracked 2027 horror games match that yet. Try another console.</p>'
             f'<div class="sec-head" style="margin-top:28px"><h2>What is the next horror game to come out?</h2></div>'
             + (f'<p>{_gname(_hor_next)} is next, on {e(nice_date(_hor_next))} ({e(", ".join(_hor_next["platforms"]))}). {e(_hor_next.get("about") or "")}</p>'
                f'<div class="cdw"><span class="lbl">Countdown to launch</span><div class="cd" data-countdown="{_hor_next["date"]}">'
                '<div class="cd-unit"><span class="flaps" data-u="0"></span><span>Days</span></div><div class="cd-unit"><span class="flaps" data-u="1"></span><span>Hrs</span></div>'
                '<div class="cd-unit"><span class="flaps" data-u="2"></span><span>Min</span></div><div class="cd-unit"><span class="flaps" data-u="3"></span><span>Sec</span></div></div></div>' if _hor_next else '<p>No 2027 horror game has an exact date yet.</p>')
             + f'<div class="sec-head" style="margin-top:28px"><h2>How many 2027 horror games are on PS5, Xbox, PC and Switch 2?</h2></div>{_hor_tbl}'
             + (f'<p style="margin-top:14px">On every console we track: {", ".join(_gname(g) for g in _hor_all)}.</p>' if _hor_all else "")
             + (f'<p>On one console only: ' + ", ".join(f'{_gname(g)} ({e(g["platforms"][0])})' for g in _hor_ex) + '.</p>' if _hor_ex else "")
             + f'<div class="sec-head" style="margin-top:28px"><h2>Which horror games were delayed to 2027?</h2><span class="muted">{len(_hor_delayed)}</span></div>'
             f'<div class="out" style="margin-bottom:10px">' + "".join(f'<div class="row"><span><strong>{_gname(g)}</strong><br><span class="muted">{e(g["history"][-1]["when"] + ": " + g["history"][-1]["text"]) if g.get("history") else ""}</span></span><b>{e(nice_date(g))}</b></div>' for g in _hor_delayed) + '</div>'
             f'<p class="muted">See <a href="{href("delayed-games-2027.html", 0)}">every game delayed to 2027</a> for all genres.</p>'
             f'<div class="sec-head" style="margin-top:28px"><h2>Is the Resident Evil Code: Veronica remake coming in 2027?</h2></div>'
             f'<p>Yes. Capcom announced <a href="{href("games/resident-evil-veronica.html", 0)}">Resident Evil Veronica</a> at Summer Game Fest on 5 June 2026 for 2027 on PS5, Xbox Series X|S, Switch 2 and PC. Capcom has not given a month or day yet, so treat any exact date you see as a guess until Capcom confirms it.</p>'
             f'<div class="sec-head" style="margin-top:28px"><h2>When does Until Dawn 2 come out?</h2></div>'
             f'<p>Until Dawn 2 launches on 28 January 2027 on PS5 only. Firesprite is making it, and as in the first game your choices decide who lives and who dies.</p>'
             f'<div class="sec-head" style="margin-top:28px"><h2>Which 2027 games are close to horror?</h2></div>'
             f'<p class="muted">Not horror games first, but worth a look if you like dark settings. They are not counted above.</p>'
             f'<div class="out" style="margin-bottom:10px">{"".join(_hrow(g, HORROR_ADJ[g["slug"]]) for g in _hor_adj)}</div>'
             f'<div class="sec-head" style="margin-top:28px"><h2>Which 2027 horror games are not on new consoles?</h2></div>'
             f'<div class="out" style="margin-bottom:10px">' + "".join(f'<div class="row"><span><strong>{e(t)}</strong><br><span class="muted">{e(gn)} · {e(dv)} · {e(pl)}</span></span><b>{e(w)}</b></div>' for t, dv, gn, pl, w in HORROR_EXTRA) + '</div>'
             f'<p class="muted">Not on our board because it is not announced for PS5, Xbox Series X|S or Switch 2. Source: Gematsu and RPGFan, August 2026.</p>'
             f'<div class="sec-head" style="margin-top:28px"><h2>Related pages and tools</h2></div><ul>'
             f'<li><a href="{href("games-by-genre-2027.html", 0)}">2027 games by genre</a>: shooters, RPGs, platformers and more</li>'
             f'<li><a href="{href("fighting-games-2027.html", 0)}">Fighting games of 2027</a>, with a console filter</li>'
             f'<li><a href="{href("release-clashes-2027.html", 0)}">2027 release clashes</a>: do your picks land the same week?</li>'
             f'<li><a href="{href("games/resident-evil-veronica.html", 0)}">Resident Evil Veronica release date and platforms</a></li>'
             f'<li><a href="{href("biggest-games-2027.html", 0)}">The biggest games of 2027</a></li></ul></div></section>')
hor_faq = [("What horror games are coming out in 2027?", f"We track {len(_hor)}: " + ", ".join(f"{g['title']} ({nice_date(g)})" for g in _hor) + ".")]
if _hor_next:
    hor_faq.append(("What is the first horror game of 2027?", f"{_hor_next['title']}, on {nice_date(_hor_next)} for {', '.join(_hor_next['platforms'])}."))
for _p in PLATS:
    hor_faq.append((f"What horror games are coming to {_lab[_p]} in 2027?", (f"{len(_hor_p[_p])}: " + ", ".join(f"{g['title']} ({nice_date(g)})" for g in _hor_p[_p]) + ".") if _hor_p[_p] else "None confirmed yet."))
hor_faq.append(("Is Resident Evil Veronica out in 2027?", "Yes, Capcom says 2027 on PS5, Xbox Series X|S, Switch 2 and PC. No month or day has been announced."))
if _hor_delayed:
    hor_faq.append(("Which horror games were delayed to 2027?", ", ".join(g["title"] for g in _hor_delayed) + "."))
page("horror-games-2027.html", f"Horror Games Coming Out in 2027: Dates and Consoles ({len(_hor)} Games) | DayOneDrop"[:90],
     f"Every horror game coming in 2027: Until Dawn 2, Resident Evil Veronica, Ontos and more, with dates, PS5/Xbox/PC/Switch 2 filter and countdown. Checked {UPDATED}."[:160],
     _hor_body, 0, hor_faq, crumbs=[("Home", DOMAIN + "/"), ("2027 games by genre", canon("games-by-genre-2027.html")), ("Horror games 2027", canon("horror-games-2027.html"))])


# ---------------- FIGHTING GAMES 2027 (26 Nov 2026) ----------------
# Built from games.json: genre contains "fighting". FG_EXTRA = 2027 fighting games not on our console board:
# Virtua Fighter Crossroads: RGG Studio / SEGA, "2027" (VGC + Gematsu, 5 Jun 2026); platforms not confirmed in SEGA's reveal text (WorthPlaying lists PS5/Xbox/PC), so not on the board.
# DCKO: Drop Fake / WB Games, free-to-play mobile 2v2 tag fighter, 2027 (Kotaku 20 Jul 2026 + Gamereactor 21 Jul 2026).
# Injustice 3: NOT announced (PC Gamer / GamesRadar report it in development). Labelled as a rumour only.
FG_EXTRA = [
    ("Virtua Fighter Crossroads", "RGG Studio (Like a Dragon team) / SEGA", "The sixth main Virtua Fighter: a story-driven game with four heroes, group brawls and boss fights, plus a Versus mode with local and online play.", "Consoles and PC not confirmed by SEGA yet", "2027"),
    ("DCKO", "Drop Fake / Warner Bros. Games", "A free-to-play 2-on-2 tag fighter with Batman, Superman, Wonder Woman and Constantine. Pre-registration is open.", "iOS and Android (mobile only)", "2027"),
]
_fg = sorted([g for g in GAMES if "fighting" in (g.get("genre") or "").lower()], key=lambda x: (x["month"], x["date"] or "9999"))
_fg_dated = [g for g in _fg if g["date"]]
_fg_undated = [g for g in _fg if not g["date"]]
_fg_next = _fg_dated[0] if _fg_dated else None
_fg_p = {p: [g for g in _fg if p in g["platforms"]] for p in PLATS}
_fg_total = len(_fg) + len(FG_EXTRA)
_fg_quick = (f"We track {_fg_total} fighting games for 2027. "
             + (f"The only one with an exact date so far is {_fg_next['title']} on {nice_date(_fg_next)}. " if len(_fg_dated) == 1 else (f"The first is {_fg_next['title']} on {nice_date(_fg_next)}. " if _fg_next else ""))
             + f"{_and([g['title'] for g in _fg_undated] + [x[0] for x in FG_EXTRA])} are all due in 2027 with no day yet. Injustice 3 has not been announced.")
def _fgrow(g):
    return (f'<div class="row" data-fplat="{e("|".join(g["platforms"]))}" data-fdated="{1 if g["date"] else 0}" data-slug="{e(g["slug"])}"><span><strong>{_gname(g)}</strong>'
            f'<br><span class="muted">{e(g.get("about") or g["genre"])}</span>'
            f'<br><span class="muted">{e(g.get("dev") or "Studio TBC")} · {e(", ".join(g["platforms"]))}'
            + (f' · also {e(", ".join(g["lastgen"]))}' if g.get("lastgen") else "") + f'</span></span><b>{e(nice_date(g))}</b></div>')
_fchips = ('<div class="chips" role="group" aria-label="Console"><button class="chip" type="button" data-fg-p="" aria-pressed="true">All consoles</button>'
           + "".join(f'<button class="chip" type="button" data-fg-p="{e(p)}" aria-pressed="false">{e(p)}</button>' for p in PLATS) + '</div>')
_fg_tbl = ('<div style="overflow-x:auto"><table class="gen-table" style="width:100%;border-collapse:collapse;font-size:.92rem"><thead><tr><th style="text-align:left;padding:6px">Console</th><th style="padding:6px">Fighting games</th><th style="text-align:left;padding:6px">Which ones</th></tr></thead><tbody>'
           + "".join(f'<tr><td style="padding:6px;border-top:1px solid var(--rule)"><a href="{href("platforms/" + _pslug[p] + ".html", 0)}">{e(_lab[p])}</a></td>'
                     f'<td style="padding:6px;text-align:center;border-top:1px solid var(--rule)" class="mono">{len(_fg_p[p])}</td>'
                     f'<td style="padding:6px;border-top:1px solid var(--rule)">{e(", ".join(g["title"] for g in _fg_p[p]) or "None confirmed yet")}</td></tr>' for p in PLATS)
           + '</tbody></table></div>')
_fg_cd = (f'<div class="cdw"><span class="lbl">Countdown to {e(_fg_next["title"])}</span><div class="cd" data-countdown="{_fg_next["date"]}">'
          '<div class="cd-unit"><span class="flaps" data-u="0"></span><span>Days</span></div><div class="cd-unit"><span class="flaps" data-u="1"></span><span>Hrs</span></div>'
          '<div class="cd-unit"><span class="flaps" data-u="2"></span><span>Min</span></div><div class="cd-unit"><span class="flaps" data-u="3"></span><span>Sec</span></div></div></div>') if _fg_next else ""
_fg_body = (f'<header class="hero"><div class="wrap"><span class="kicker">Fighting games</span>'
            f'<h1>Fighting games coming in 2027:<br><span class="amber">every date, every console.</span></h1>'
            f'<p class="lead">Every fighting game confirmed for 2027, from Melty Blood: Twi-Lumina to Dragon Ball Xenoverse 3 and the new Virtua Fighter, with a console filter, a countdown and what is still only a rumour.</p>'
            f'<p class="muted" style="margin:0">Last checked {e(UPDATED)} · {_fg_total} fighting games · dates and consoles from publishers or two trusted outlets</p></div></header>'
            f'<section><div class="wrap"><div class="out" style="margin-bottom:24px"><div class="row"><span><strong>Quick answer:</strong> {e(_fg_quick)}</span></div></div>'
            f'<div class="tool" id="fg-tool"><h2 style="font-size:1.5rem;margin-top:0">Which 2027 fighting games can I play on my console?</h2>'
            f'<p class="muted">Tap your console. The list below updates, and your choice is remembered on this device. Add the lot to your ★ list to get countdowns and delay news on the board.</p>{_fchips}'
            f'<p class="mono amber" id="fg-count" aria-live="polite" style="margin:12px 0 0">{len(_fg)} games</p>'
            f'<div class="btns" style="margin-top:10px;display:flex;gap:8px;flex-wrap:wrap"><button class="btn sm" type="button" id="fg-add">Add these to my ★ list</button>'
            f'<a class="btn line sm" href="{href("countdown.html", 0)}">Make a countdown</a></div></div></div></section>'
            + AD.format("fg-mid") +
            f'<section><div class="wrap"><div class="sec-head"><h2>What fighting games come out in 2027?</h2><span class="muted">{len(_fg)} on consoles we track</span></div>'
            f'<p class="muted">In release order. Games with only a year sit at the end.</p>'
            f'<div class="out" id="fg-list" style="margin-bottom:10px">{"".join(_fgrow(g) for g in _fg)}</div><p class="empty" id="fg-none" hidden>No tracked 2027 fighting game is confirmed for that console yet.</p>'
            f'<div class="sec-head" style="margin-top:28px"><h2>Which other fighting games are coming in 2027?</h2><span class="muted">{len(FG_EXTRA)}</span></div>'
            f'<p class="muted">Confirmed for 2027 but not on our console board: one has no confirmed platforms yet, the other is mobile only.</p>'
            f'<div class="out" style="margin-bottom:10px">' + "".join(f'<div class="row"><span><strong>{e(t)}</strong><br><span class="muted">{e(ab)}</span><br><span class="muted">{e(dv)} · {e(pl)}</span></span><b>{e(w)}</b></div>' for t, dv, ab, pl, w in FG_EXTRA) + '</div>'
            f'<div class="sec-head" style="margin-top:28px"><h2>What is the next fighting game to come out?</h2></div>'
            + (f'<p>{_gname(_fg_next)} is next, on {e(nice_date(_fg_next))} for {e(", ".join(_fg_next["platforms"]))}' + (f' (and {e(", ".join(_fg_next["lastgen"]))})' if _fg_next.get("lastgen") else "") + f'. {e(_fg_next.get("about") or "")}</p>{_fg_cd}' if _fg_next else '<p>No 2027 fighting game has an exact date yet.</p>')
            + f'<div class="sec-head" style="margin-top:28px"><h2>When does Dragon Ball Xenoverse 3 come out?</h2></div>'
            f'<p>In 2027. Bandai Namco revealed it in April 2026 for PS5, Xbox Series X|S and PC (Steam), and its European site lists late 2027. No day has been announced and no Switch 2 version has been confirmed. It is set in a new world in Age 1000, with West City as the hub and original characters drawn by Akira Toriyama.</p>'
            f'<div class="sec-head" style="margin-top:28px"><h2>Is the new Virtua Fighter coming out in 2027?</h2></div>'
            f'<p>Yes. SEGA and RGG Studio, the team behind Like a Dragon, named it Virtua Fighter Crossroads at Summer Game Fest on 5 June 2026 and said it launches in 2027. It is the sixth main Virtua Fighter, but it plays differently: a story campaign with four heroes, fights against groups and bosses, plus a Versus mode for local and online matches. SEGA has not listed the consoles in its reveal, so we will add it to the board once it does.</p>'
            f'<div class="sec-head" style="margin-top:28px"><h2>Is Injustice 3 coming out in 2027?</h2></div>'
            f'<p>Not officially. Warner Bros. and NetherRealm have not announced Injustice 3. PC Gamer and GamesRadar+ have reported signs that NetherRealm is working on it, and Ed Boon has said another Mortal Kombat is also planned, but neither game has a name, platforms or a year. The only DC fighting game confirmed for 2027 is DCKO, a free-to-play mobile game from a new studio, Drop Fake.</p>'
            f'<div class="sec-head" style="margin-top:28px"><h2>Are there any retro fighting game collections in 2027?</h2></div>'
            f'<p>Yes: Toshinden Collection brings the first three PS1 Battle Arena Toshinden games to PS5, Switch 2 and PC (Steam) in 2027, with same-screen multiplayer. Edia announced it at Tokyo Game Show 2026.</p>'
            f'<div class="sec-head" style="margin-top:28px"><h2>How many 2027 fighting games are on PS5, Xbox, PC and Switch 2?</h2></div>{_fg_tbl}'
            f'<div class="sec-head" style="margin-top:28px"><h2>Which fighting games are up for an award this year?</h2></div>'
            f'<p>The Best Fighting Game nominees at <a href="{href("game-awards-2026.html", 0)}">The Game Awards 2026</a> (10 December) are 2XKO, Avatar Legends: The Fighting Game, Invincible VS, Marvel Tokon: Fighting Souls and My Hero Academia: All\'s Justice. They are all 2026 games, so they are not on this list.</p>'
            f'<div class="sec-head" style="margin-top:28px"><h2>Related pages and tools</h2></div><ul>'
            f'<li><a href="{href("games-by-genre-2027.html", 0)}">2027 games by genre</a>: horror, shooters, RPGs and more</li>'
            f'<li><a href="{href("games-without-release-date-2027.html", 0)}">2027 games with no release date yet</a>, by console and season</li>'
            f'<li><a href="{href("release-clashes-2027.html", 0)}">2027 release clashes</a>: do your picks land the same week?</li>'
            f'<li><a href="{href("countdown.html", 0)}">Game release countdown</a> for any dated 2027 game</li></ul></div></section>')
fg_faq = [("What fighting games are coming out in 2027?", f"We track {_fg_total}: " + ", ".join(f"{g['title']} ({nice_date(g)})" for g in _fg) + ", " + ", ".join(f"{x[0]} ({x[4]})" for x in FG_EXTRA) + "."),
          ("When does Dragon Ball Xenoverse 3 come out?", "In 2027 on PS5, Xbox Series X|S and PC. Bandai Namco's European site says late 2027. No exact date yet."),
          ("Is Virtua Fighter Crossroads coming out in 2027?", "Yes. SEGA and RGG Studio say 2027. The consoles have not been confirmed in SEGA's reveal yet."),
          ("Is Injustice 3 announced?", "No. There are reports that NetherRealm is working on it, but Warner Bros. has not announced it, so there is no date or platform."),
          ("Is DCKO on PS5 or Xbox?", "No. DCKO is a free-to-play DC tag fighter for iOS and Android only, due in 2027.")]
if _fg_next:
    fg_faq.insert(1, ("What is the first fighting game of 2027?", f"{_fg_next['title']}, on {nice_date(_fg_next)} for {', '.join(_fg_next['platforms'])}."))
for _p in ("Switch 2", "PS5"):
    fg_faq.append((f"What fighting games are coming to {_lab[_p]} in 2027?", (", ".join(f"{g['title']} ({nice_date(g)})" for g in _fg_p[_p]) + ".") if _fg_p[_p] else "None confirmed yet."))
page("fighting-games-2027.html", "Fighting Games Coming Out in 2027: Dates and Consoles | DayOneDrop",
     f"Every fighting game coming in 2027: Melty Blood: Twi-Lumina ({nice_date(_fg_next) if _fg_next else 'TBC'}), Dragon Ball Xenoverse 3, Virtua Fighter Crossroads and more, with a console filter.",
     _fg_body, 0, fg_faq, crumbs=[("Home", DOMAIN + "/"), ("2027 games by genre", canon("games-by-genre-2027.html")), ("Fighting games 2027", canon("fighting-games-2027.html"))])


# ---------------- BACKLOG PLANNER (22 Nov 2026) ----------------
# Gaps come only from games.json dates. Playtimes are the visitor's own estimates (we publish none).
_big = sorted([g for g in GAMES if g["page"] and g["date"]], key=lambda x: x["date"])
_gaps = []
for _i, _g in enumerate(_big[:-1]):
    _n = _big[_i + 1]
    _gaps.append((_g, _n, (datetime.date.fromisoformat(_n["date"]) - datetime.date.fromisoformat(_g["date"])).days))
_tight = min(_gaps, key=lambda x: x[2]) if _gaps else None
_long = max(_gaps, key=lambda x: x[2]) if _gaps else None
_first_big = _big[0] if _big else None
_bl_quick = ""
if _tight and _long:
    _tg = ("two of them launch on the same day" if _tight[2] == 0 else f"the shortest gap is {_tight[2]} day{'s' if _tight[2] != 1 else ''}")
    _bl_quick = (f"The {len(_big)} biggest dated games of 2027 are close together: {_tg} "
                 f"({_tight[0]['title']} and {_tight[1]['title']}, {nice_date(_tight[1])}), and the longest gap is {_long[2]} days "
                 f"({_long[0]['title']} to {_long[1]['title']}). At 10 hours a week, a 30-hour game takes 3 weeks, so playing them back to back means launches will overlap.")
def _hrs(days, per):
    return round(days / 7 * per)
_gap_rows = "".join(
    f'<div class="row"><span>{_gname(a)} <span class="muted mono">{e(short_date(a))}</span> → {_gname(b)} <span class="muted mono">{e(short_date(b))}</span>'
    f'<br><span class="muted">At 5 h/week: {_hrs(dd, 5)} h · 10 h/week: {_hrs(dd, 10)} h · 20 h/week: {_hrs(dd, 20)} h</span></span><b>{dd} day{"s" if dd != 1 else ""}</b></div>'
    for a, b, dd in _gaps)
_bl_pick = "".join(
    f'<label class="clash-opt"{" data-big" if g["page"] else ""}><input type="checkbox" value="{e(g["slug"])}"> <span>{e(g["title"])}</span> <span class="muted mono">{e(short_date(g))}</span>'
    f'<input class="bl-h" type="number" min="1" max="500" step="1" value="30" inputmode="numeric" aria-label="Hours you expect to spend on {e(g["title"])}" style="width:72px !important;padding:6px 8px"></label>'
    for g in sorted([g for g in GAMES if g["date"]], key=lambda x: x["date"]))
# Refresh 25 Nov 2026: time before the first big launch, big games per month, undated guides, presets.
_bl_today = datetime.date.fromisoformat(UPDATED)
_bl_up = [g for g in _big if g["date"] > UPDATED]
_bl_first_up = _bl_up[0] if _bl_up else None
_bl_wait = (datetime.date.fromisoformat(_bl_first_up["date"]) - _bl_today).days if _bl_first_up else 0
_bl_month = {}
for _g in _big:
    _bl_month.setdefault(int(_g["date"][5:7]), []).append(_g)
_bl_busy = max(_bl_month.items(), key=lambda kv: len(kv[1])) if _bl_month else None
_bl_undated = sorted([g for g in GAMES if g["page"] and not g["date"]], key=lambda x: (x["month"], x["title"]))
def _blm_row(m, gs):
    days = (datetime.date(2027 + (m == 12), m % 12 + 1, 1) - datetime.date(2027, m, 1)).days
    return (f'<tr><td style="padding:6px;border-top:1px solid var(--rule)">{e(MONTHS[m - 1])} 2027</td><td style="padding:6px;border-top:1px solid var(--rule)">{len(gs)}</td>'
            f'<td style="padding:6px;border-top:1px solid var(--rule)">{_hrs(days, 10)} h</td><td style="padding:6px;border-top:1px solid var(--rule)">{round(_hrs(days, 10) / len(gs))} h</td>'
            f'<td style="padding:6px;border-top:1px solid var(--rule)">{", ".join(_gname(g) for g in gs)}</td></tr>')
_bl_month_html = ('<div style="overflow-x:auto;margin-bottom:12px"><table class="gen-table" style="width:100%;border-collapse:collapse;font-size:.92rem"><thead><tr>'
    '<th style="text-align:left;padding:6px">Month</th><th style="text-align:left;padding:6px">Big games</th><th style="text-align:left;padding:6px">Play time at 10 h/week</th><th style="text-align:left;padding:6px">Per game</th><th style="text-align:left;padding:6px">Games</th></tr></thead><tbody>'
    + "".join(_blm_row(m, gs) for m, gs in sorted(_bl_month.items())) + '</tbody></table></div>')
bl_tool = f'''<div class="tool" id="bl-tool"><h2 style="font-size:1.5rem;margin-top:0">Can I finish my games before the next one launches?</h2>
<p class="muted">Tick the 2027 games you want (your ★ list is ticked for you), set the hours you expect each one to take, and how many hours a week you play. We line them up in launch order and show when you would finish each one and where you fall behind.</p>
<div class="bl-grid"><div><label for="bl-week">Hours you play per week</label><input id="bl-week" type="number" min="1" max="100" value="10" inputmode="numeric">
<div class="chips" role="group" aria-label="Quick weekly hours" style="margin-top:8px">{"".join(f'<button class="chip" type="button" data-blw="{h}" aria-pressed="false">{h} h ({lab})</button>' for h, lab in ((5, "light"), (10, "regular"), (20, "heavy")))}</div></div>
<div><label for="bl-start">Start playing from</label><select id="bl-start"><option value="now" selected>Today</option><option value="first">The first game I tick</option></select></div></div>
<div class="clash-list" role="group" aria-label="Pick games and hours">{_bl_pick}</div>
<p class="muted" style="font-size:.85rem;margin:8px 0 0">Hours start at 30 as a placeholder. Change them to your own guess; we do not publish playtimes.</p>
<div class="btns" style="margin-top:10px;display:flex;gap:8px;flex-wrap:wrap"><button class="btn sm" type="button" id="bl-star">Use my ★ list</button><button class="btn line sm" type="button" id="bl-big">Tick the {len(_big)} big games</button><button class="btn line sm" type="button" id="bl-clear">Clear</button></div>
<div class="out" id="bl-out" aria-live="polite"></div></div>'''
if _bl_first_up and _bl_quick:
    _bl_quick += f" You have {_bl_wait} days before {_bl_first_up['title']}, the first big launch."
if _bl_busy and _bl_quick:
    _bl_quick += f" {MONTHS[_bl_busy[0] - 1]} is the busiest month, with {len(_bl_busy[1])} big games."
bl_body = (f'<header class="hero"><div class="wrap"><span class="kicker">Backlog planner</span>'
           f'<h1>2027 backlog planner:<br><span class="amber">will you finish before the next launch?</span></h1>'
           f'<p class="lead">2027 starts with big games days apart. Plan your hours so you are not three games behind by March.</p>'
           f'<p class="muted" style="margin:0">Last checked {e(UPDATED)} · {sum(1 for g in GAMES if g["date"])} dated games · runs in your browser</p></div></header>'
           f'<section><div class="wrap"><div class="out" style="margin-bottom:24px"><div class="row"><span><strong>Quick answer:</strong> {e(_bl_quick)}</span></div></div>'
           f'{bl_tool}</div></section>' + AD.format("bl-mid") +
           f'<section><div class="wrap"><div class="sec-head"><h2>How much time is there between the big 2027 launches?</h2><span class="muted">{len(_big)} games</span></div>'
           f'<p class="muted">Days from one big dated game to the next, and the hours that gives you at 5, 10 or 20 hours of play a week.</p>'
           f'<div class="out" style="margin-bottom:28px">{_gap_rows}</div>'
           + (f'<div class="sec-head"><h2>How much time do I have before the first big 2027 game?</h2></div>'
              f'<div class="tool" style="margin-bottom:28px"><p style="margin-top:0"><strong>{_gname(_bl_first_up)}</strong> launches {e(nice_date(_bl_first_up))}, {_bl_wait} days after {e(nice_date({"date": UPDATED, "window": ""}))}. '
              f'That is about {_hrs(_bl_wait, 5)} hours of play at 5 h/week, {_hrs(_bl_wait, 10)} h at 10 h/week or {_hrs(_bl_wait, 20)} h at 20 h/week to clear what you have now.</p>'
              f'<div class="cdw"><span class="lbl">Countdown to launch</span><div class="cd" data-countdown="{_bl_first_up["date"]}">'
              '<div class="cd-unit"><span class="flaps" data-u="0"></span><span>Days</span></div><div class="cd-unit"><span class="flaps" data-u="1"></span><span>Hrs</span></div>'
              '<div class="cd-unit"><span class="flaps" data-u="2"></span><span>Min</span></div><div class="cd-unit"><span class="flaps" data-u="3"></span><span>Sec</span></div></div></div></div>' if _bl_first_up else '')
           + (f'<div class="sec-head"><h2>Which month of 2027 has the most big games?</h2><span class="muted">{e(MONTHS[_bl_busy[0] - 1])}: {len(_bl_busy[1])}</span></div>'
              f'<p class="muted">Big dated games per month, the play time a 10-hour-a-week player has that month, and how much of it each game gets if you play them all.</p>{_bl_month_html}'
              f'<p style="margin-bottom:28px">Every dated game, big or small, is in the <a href="{href("calendar.html", 0)}">2027 calendar</a>, and the <a href="{href("new-games-this-week.html", 0)}">week-by-week list</a> shows what lands next.</p>' if _bl_busy else '')
           + (f'<div class="sec-head"><h2>Which big 2027 games are not in the planner yet?</h2><span class="muted">{len(_bl_undated)}</span></div>'
              f'<p class="muted">These have a guide but no exact day, so they cannot be lined up yet. We add each one the day a date is announced.</p>'
              '<div class="out" style="margin-bottom:28px">' + "".join(f'<div class="row"><span>{_gname(g)}<br><span class="muted">{e(", ".join(g["platforms"]))}</span></span><b>{e(nice_date(g))}</b></div>' for g in _bl_undated) + '</div>' if _bl_undated else '')
           + f'<div class="sec-head"><h2>How do I plan a gaming backlog for 2027?</h2></div>'
           f'<ol><li>Star the games you really plan to buy on the <a href="{href("index.html", 0)}#board">departures board</a>.</li>'
           f'<li>Be honest about your weekly hours. Two evenings and a weekend afternoon is often 8 to 10 hours.</li>'
           f'<li>Put your own hour guess on each game. Long RPGs take far more than a story shooter.</li>'
           f'<li>Where the planner shows you falling behind, wait for a sale on the later game or drop one. A date change can also open space, so check the <a href="{href("delayed-games-2027.html", 0)}">delay tracker</a>.</li></ol>'
           f'<div class="sec-head" style="margin-top:28px"><h2>Related pages and tools</h2></div><ul>'
           f'<li><a href="{href("release-clashes-2027.html", 0)}">2027 release clashes</a>: which games land the same week</li>'
           f'<li><a href="{href("rpgs-2027.html", 0)}">Every RPG coming in 2027</a>: the long games to plan around</li>'
           f'<li><a href="{href("calendar.html", 0)}">The full 2027 release calendar</a> with calendar reminders</li>'
           f'<li><a href="{href("new-games-this-week.html", 0)}">New games this week</a>, week by week</li>'
           f'<li><a href="{href("biggest-games-2027.html", 0)}">The biggest games of 2027</a>: which ones to make room for</li></ul></div></section>')
bl_faq = []
if _bl_first_up:
    bl_faq.append((f"How long do I have before {_bl_first_up['title']} comes out?", f"{_bl_wait} days from {nice_date({"date": UPDATED, "window": ""})} to {nice_date(_bl_first_up)}. At 10 hours a week that is about {_hrs(_bl_wait, 10)} hours of play."))
if _bl_busy:
    bl_faq.append(("Which month of 2027 has the most big game releases?", f"{MONTHS[_bl_busy[0] - 1]} 2027, with {len(_bl_busy[1])}: " + ", ".join(g["title"] for g in _bl_busy[1]) + "."))
if _tight:
    bl_faq.append(("Which big 2027 games launch closest together?", f"{_tight[0]['title']} ({nice_date(_tight[0])}) and {_tight[1]['title']} ({nice_date(_tight[1])}), {_tight[2]} day{'s' if _tight[2] != 1 else ''} apart."))
if _first_big:
    bl_faq.append(("What is the first big game of 2027?", f"{_first_big['title']}, on {nice_date(_first_big)}."))
bl_faq += [
    ("How does the backlog planner work?", "It puts your games in launch order and assumes you play one at a time. Each game starts when it launches or when you finish the one before, whichever is later. Your weekly hours decide how long each takes. It runs in your browser and saves your hours on this device only."),
    ("Where do the hours per game come from?", "From you. Every game starts at 30 hours as a placeholder. We only list release dates we can confirm, so we do not publish playtime estimates."),
    ("How many hours a week does the average gamer play?", "It varies a lot, so the planner lets you set your own. Try 10 hours a week as a starting point and adjust."),
]
page("backlog-planner-2027.html", "2027 Backlog Planner: Can You Finish Before the Next Big Game? | DayOneDrop",
     (f"Free 2027 backlog planner: pick your games and weekly hours, see if you finish before each launch, the busiest month and days left before the first big game.")[:160],
     bl_body, 0, bl_faq, crumbs=[("Home", DOMAIN + "/"), ("Tools", canon("tools.html")), ("Backlog planner 2027", canon("backlog-planner-2027.html"))])


# ---------------- LAST-GEN: 2027 GAMES ON PS4, XBOX ONE AND SWITCH 1 (23 Nov 2026) ----------------
# games.json "lastgen" = last-gen versions confirmed by the publisher or 2+ trusted outlets (checked 23 Nov 2026:
# Gematsu, RPG Site, Siliconera, Nintendo Everything, Nintendo Life, Game Informer, Push Square, official stores).
# Left out: Melty Blood Xbox One (Gematsu lists it, Shacknews does not), Grave Seasons Switch 1 (wording unclear).
LG_PLATS = [("PS4", "PS4", "PS5"), ("Xbox One", "Xbox One", "Xbox Series X|S"), ("Switch", "Switch 1", "Switch 2")]
_lgk = lambda g: (g["month"], g["date"] or "9999")
_lg = sorted([g for g in GAMES if g.get("lastgen")], key=_lgk)
_lg_on = {k: [g for g in _lg if k in g["lastgen"]] for k, _, _ in LG_PLATS}
_lg_big_miss = [g for g in sorted(GAMES, key=_lgk) if g["slug"] in BIG_WHY_SLUGS and not g.get("lastgen")]
def _lgrow(g):
    old = ", ".join(n for k, n, _ in LG_PLATS if k in g.get("lastgen", []))
    return (f'<div class="row"><span><strong>{_gname(g)}</strong><br><span class="muted">{e(g.get("about") or "")}</span>'
            f'<br><span class="muted">Old consoles: {e(old)} · New: {e(", ".join(g["platforms"]))}</span></span><b>{e(nice_date(g))}</b></div>')
_lg_quick = (f"{len(_lg)} of the {len(GAMES)} games of 2027 we track are also coming to a last-gen console: "
             + ", ".join(f"{len(_lg_on[k])} on {n}" for k, n, _ in LG_PLATS[:-1]) + f" and {len(_lg_on[LG_PLATS[-1][0]])} on {LG_PLATS[-1][1]}"
             + ". Most are smaller RPGs, remakes and ports. The biggest 2027 games, such as "
             + ", ".join(g["title"] for g in _lg_big_miss[:2]) + f" and {_lg_big_miss[2]['title']}, are not coming to PS4, Xbox One or Switch 1.")
_lg_secs = ""
for k, n, new in LG_PLATS:
    rows = "".join(_lgrow(g) for g in _lg_on[k]) or f'<div class="row"><span>No 2027 games on our board are confirmed for {e(n)}.</span><b>0</b></div>'
    _lg_secs += (f'<div class="sec-head"><h2>Which 2027 games are coming to {e(n)}?</h2><span class="muted">{len(_lg_on[k])}</span></div>'
                 f'<div class="out" style="margin-bottom:28px">{rows}</div>')
_lg_tbl = "".join(f'<tr><td class="t">{_gname(g)}</td>' + "".join(f'<td class="p">{"✓" if k in g["lastgen"] else "-"}</td>' for k, _, _ in LG_PLATS)
                  + f'<td class="d"><span>{e(short_date(g))}</span></td></tr>' for g in _lg)
_lg_matrix = (f'<div class="board"><div class="board-top"><span class="board-title">LAST-GEN · 2027</span></div><div class="board-scroll"><table class="dep">'
              f'<thead><tr><th>Game</th>' + "".join(f'<th>{e(n)}</th>' for _, n, _ in LG_PLATS) + '<th>Date</th></tr></thead><tbody>' + _lg_tbl + '</tbody></table></div></div>')
_lg_chips = "".join(f'<button class="chip" type="button" data-lg="{e(k)}" data-new="{e(new)}" data-name="{e(n)}" aria-pressed="false">{e(n)}</button>' for k, n, new in LG_PLATS)
lg_body = (f'<header class="hero"><div class="wrap"><span class="kicker">Old consoles</span>'
           f'<h1>2027 games on PS4, Xbox One<br><span class="amber">and the original Switch.</span></h1>'
           f'<p class="lead">Still on a PS4, Xbox One or Switch 1? Here is every 2027 game confirmed for your console, the big ones you will miss, '
           f'and a quick check of whether it is time to upgrade.</p>'
           f'<p class="muted" style="margin:0">Last checked {e(UPDATED)} · only versions confirmed by the publisher or two trusted outlets</p></div></header>'
           f'<section><div class="wrap"><div class="out" style="margin-bottom:24px"><div class="row"><span><strong>Quick answer:</strong> {e(_lg_quick)}</span></div></div>'
           f'<div class="tool" id="lg-tool"><h2 style="font-size:1.5rem;margin-top:0">Do I need to upgrade for 2027?</h2>'
           f'<p class="muted">Tap the old console you have. We show the 2027 games you can still play on it, the tracked games you would miss, and how many of those the newer console in the same family gets.</p>'
           f'<div class="chips" role="group" aria-label="Your console" style="margin-bottom:12px">{_lg_chips}</div>'
           f'<div class="out" id="lg-out" aria-live="polite"></div></div></div></section>' + AD.format("lastgen-mid") +
           f'<section><div class="wrap">{_lg_secs}'
           f'<div class="sec-head"><h2>Which big 2027 games are not coming to old consoles?</h2><span class="muted">{len(_lg_big_miss)}</span></div>'
           f'<div class="out" style="margin-bottom:28px">' + "".join(f'<div class="row"><span>{_gname(g)}<br><span class="muted">{e(", ".join(g["platforms"]))}</span></span><b>{e(nice_date(g))}</b></div>' for g in _lg_big_miss) + '</div>'
           f'<div class="sec-head"><h2>Can I play the old version on a new console?</h2></div>'
           f'<p>Usually, yes. PS5 plays almost all PS4 games, Xbox Series X|S plays Xbox One games, and Switch 2 plays most Switch 1 games. '
           f'So buying a last-gen version is not wasted if you upgrade later. But a free upgrade to the new-console version is not automatic: some publishers give one, some sell a discounted upgrade, and some ask you to buy again. '
           f'Check the store page before you buy.</p>'
           f'<p class="muted">Example: Hyrule Warriors: Age of Calamity owners on Switch 1 get a discount on the separate Switch 2 Definitive Edition rather than a free upgrade. See the <a href="{href("games/hyrule-warriors-age-of-calamity-definitive-edition.html", 0)}">guide</a>.</p>'
           f'<div class="sec-head"><h2>Every 2027 last-gen version at a glance</h2></div>{_lg_matrix}'
           f'<div class="sec-head" style="margin-top:28px"><h2>Related pages and tools</h2></div><ul>'
           f'<li><a href="{href("exclusives-2027.html", 0)}">2027 console exclusives</a> and which games your new consoles will miss</li>'
           f'<li><a href="{href("platforms/switch-2.html", 0)}">Every Switch 2 game coming in 2027</a> and <a href="{href("platforms/ps5.html", 0)}">every PS5 game</a></li>'
           f'<li><a href="{href("biggest-games-2027.html", 0)}">The biggest games of 2027</a></li></ul></div></section>')
lg_faq = [
    ("Which 2027 games are coming to PS4?", (", ".join(f"{g['title']} ({nice_date(g)})" for g in _lg_on["PS4"]) + ".") if _lg_on["PS4"] else "None on our board."),
    ("Are any 2027 games coming to the original Switch?", f"Yes, {len(_lg_on['Switch'])} on our board, including " + ", ".join(g["title"] for g in _lg_on["Switch"][:6]) + "."),
    ("Are any 2027 games coming to Xbox One?", (", ".join(g["title"] for g in _lg_on["Xbox One"]) + " is confirmed for Xbox One. Almost every other 2027 game is Xbox Series X|S only.") if _lg_on["Xbox One"] else "None confirmed on our board."),
    ("Is GTA 6 on PS4 or Xbox One?", "No. Rockstar has only announced GTA 6 for PS5 and Xbox Series X|S."),
    ("Is Pokémon Winds and Waves on Switch 1?", "No. It is only announced for Switch 2."),
    ("Is Final Fantasy XIV Evercold on PS4?", "Yes. The Evercold expansion comes to every platform Final Fantasy XIV is on, PS4 included."),
]
page("last-gen-games-2027.html", f"2027 Games on PS4, Xbox One and Switch 1: Full List ({len(_lg)}) | DayOneDrop"[:90],
     f"Every 2027 game confirmed for PS4, Xbox One or the original Switch, the big games old consoles miss, and an upgrade checker. Checked {UPDATED}."[:160],
     lg_body, 0, lg_faq, crumbs=[("Home", DOMAIN + "/"), ("All games", canon("games.html")), ("Last-gen games 2027", canon("last-gen-games-2027.html"))])


# ---------------- TOOLS ----------------
plat_links0 = " · ".join(f'<a href="{href("platforms/" + s2 + ".html", 0)}">{e(l2)} games</a>' for p2, s2, l2 in PLAT_PAGES)
_busy_m = max(range(1, 13), key=lambda m: sum(1 for g in GAMES if g["month"] == m))
_busy_n = sum(1 for g in GAMES if g["month"] == _busy_m)
tools = f'''<header class="hero"><div class="wrap"><span class="kicker">Tools</span><h1>Plan your<br><span class="amber">2027 gaming year.</span></h1>
<p class="lead">Free tools to see what's coming to your console, keep track of the games you want, spot release clashes and find the busiest months.</p>
<p class="muted" style="margin:0">Last checked {e(UPDATED)} · Full lists: {plat_links0}</p></div></header>
<section><div class="wrap"><div class="out" style="margin-bottom:20px"><div class="row"><span><strong>Quick answer:</strong> we track {len(GAMES)} games for 2027. {MONTHS[_busy_m - 1]} is the busiest month with {_busy_n} launches. Pick your console below to see only your games, or use the <a href="{href("release-clashes-2027.html", 0)}">clash finder</a> to see which of them land the same week.</span></div></div></div></section>
<section><div class="wrap grid" style="grid-template-columns:repeat(auto-fit,minmax(min(320px,100%),1fr))">
<div class="tool"><h2 style="font-size:1.5rem">What's coming to my console?</h2><label for="console-pick">Your console</label>
<select id="console-pick">{"".join(f'<option>{e(p)}</option>' for p in PLATS)}</select><div class="out" id="console-out"></div></div>
<div class="tool"><h2 style="font-size:1.5rem">What's on my launch list?</h2><p class="muted">Games you've starred, with days left. Saved on this device.</p><div class="out" id="watch-out"></div>
<div class="btns" style="margin-top:12px"><a class="btn sm" href="{href("index.html", 0)}#board">Add games</a><button class="btn line sm" type="button" id="share-list">Share my list</button></div></div>
<div class="tool"><h2 style="font-size:1.5rem">Which months of 2027 are busiest?</h2><p class="muted">Number of tracked launches each month.</p><div id="month-load"></div></div>
<div class="tool"><h2 style="font-size:1.5rem">Do my games clash?</h2><p class="muted">See which 2027 games launch in the same week, and check your own list for clashes.</p>
<div class="out">{"".join(f'<div class="row"><span>Week of {e(_dm(m))}</span><b>{len(gs)} games</b></div>' for m, gs in sorted(_clash_weeks[:3], key=lambda kv: kv[0]))}</div>
<div class="btns" style="margin-top:12px"><a class="btn sm" href="{href("release-clashes-2027.html", 0)}">Open the clash finder</a></div></div>
<div class="tool"><h2 style="font-size:1.5rem">Can I finish my games in time?</h2><p class="muted">Set your hours per week and per game. See when you finish each 2027 game and where you fall behind.</p>
<div class="out">{"".join(f'<div class="row"><span>{e(a["title"])} → {e(b["title"])}</span><b>{dd} days</b></div>' for a, b, dd in sorted(_gaps, key=lambda x: x[2])[:3])}</div>
<div class="btns" style="margin-top:12px"><a class="btn sm" href="{href("backlog-planner-2027.html", 0)}">Open the backlog planner</a></div></div>
<div class="tool"><h2 style="font-size:1.5rem">What are my top games of 2027?</h2><p class="muted">Pick up to 10 of the biggest 2027 games in order. Copy a ready-to-paste list with dates, or send a link that opens your picks.</p>
<div class="btns" style="margin-top:12px"><a class="btn sm" href="{href("biggest-games-2027.html", 0)}#top-tool">Make my top list</a></div></div>
<div class="tool"><h2 style="font-size:1.5rem">What 2027 games match my taste?</h2><p class="muted">Filter every 2027 game by genre and console: horror, shooters, RPGs, platformers and more.</p>
<div class="out">{"".join(f'<div class="row"><span>{e(_gen_meta[k][0])}</span><b>{len(_gen[k])} games</b></div>' for k in _gen_rank[:3])}</div>
<div class="btns" style="margin-top:12px"><a class="btn sm" href="{href("games-by-genre-2027.html", 0)}">Open the genre finder</a></div></div>
</div></section>
<section><div class="wrap"><div class="sec-head"><h2>More ways to plan</h2></div><ul>
<li><a href="{href("countdown.html", 0)}">Game release countdown</a>: a live, shareable timer for any dated 2027 game</li>
<li><a href="{href("games-without-release-date-2027.html", 0)}">2027 games with no release date yet</a>, by console and season</li>
<li><a href="{href("release-clashes-2027.html", 0)}">2027 release clashes</a>: every crowded week</li>
<li><a href="{href("backlog-planner-2027.html", 0)}">2027 backlog planner</a>: finish each game before the next launch</li>
<li><a href="{href("delayed-games-2027.html", 0)}">Games delayed to 2027</a></li>
<li><a href="{href("exclusives-2027.html", 0)}">2027 console exclusives</a> and which games your consoles will miss</li>
<li><a href="{href("rpgs-2027.html", 0)}">Every RPG coming in 2027</a> with a console filter</li>
<li><a href="{href("games-by-genre-2027.html", 0)}">2027 games by genre</a>: horror, shooters, platformers and more</li>
<li><a href="{href("horror-games-2027.html", 0)}">Every horror game of 2027</a>, with a console filter and countdown</li>
<li><a href="{href("fighting-games-2027.html", 0)}">Every fighting game of 2027</a>, with a console filter and countdown</li>
<li><a href="{href("game-pass-2027.html", 0)}">Every 2027 game on Xbox Game Pass</a>, with a Game Pass or buy checker</li>
<li><a href="{href("biggest-games-2027.html", 0)}">The biggest games of 2027</a>, with a shareable top list maker</li>
<li><a href="{href("last-gen-games-2027.html", 0)}">2027 games on PS4, Xbox One and Switch 1</a>, with a do-I-need-to-upgrade check</li>
<li><a href="{href("game-awards-2026.html", 0)}">The Game Awards 2026</a>: Most Anticipated nominees, their 2027 dates and a winner predictor</li>
<li><a href="{href("new-games-this-week.html", 0)}">New games coming out this week</a>: every launch grouped Monday to Sunday, with a console filter</li>
<li><a href="{href("games-december-2026.html", 0)}">Games coming out in December 2026</a>, with a console filter and live "out now" marks</li>
<li><a href="{href("steam-sale-dates.html", 0)}">Steam sale dates</a>: countdown to the next Steam sale, every 2027 sale and fest</li>
<li><a href="{href("nintendo-direct.html", 0)}">Next Nintendo Direct</a>: every 2026 Direct and the Switch 2 games still without a date</li>
<li><a href="{href("movies-2027.html", 0)}">Upcoming movies 2027</a>: every big release date with type and month filters and calendar reminders</li>
<li><a href="{href("after-gta-6.html", 0)}">What to play after GTA 6</a></li></ul></div></section>'''
sw2 = [g["title"] for g in GAMES if "Switch 2" in g["platforms"]]
both = [g["title"] for g in GAMES if "PS5" in g["platforms"] and "Xbox Series X|S" in g["platforms"]]
tools_faq = [
    ("Which 2027 games are coming to Switch 2?", f"{len(sw2)} tracked 2027 games are confirmed for Switch 2, including {', '.join(sw2[:4])}. See the full Switch 2 list or use the console tool above."),
    ("Which 2027 games are on PS5 and Xbox?", f"{len(both)} tracked games are confirmed for both, including {', '.join(both[:4])}. The platform pages list them all."),
    ("Is my launch list saved?", "Yes, on this device and browser. Use Share my list to send it to a friend or open it on another device."),
    ("Which week of 2027 has the most game releases?", _quick or "See the clash finder for every crowded week."),
]
page("tools.html", "2027 Game Release Tools: Console Lineup and Launch List | DayOneDrop",
     "Free 2027 gaming tools: see every game coming to PS5, Xbox, PC or Switch 2, build a launch list with countdowns, and find the busiest release months.",
     tools, 0, tools_faq, crumbs=[("Home", DOMAIN + "/"), ("Tools", canon("tools.html"))])


# ---------------- DECEMBER 2026 (24 Nov 2026, demand radar R1: "games coming out december 2026") ----------------
# Only games on 2+ of: VGC, Game Informer, GamesRadar+ and Wikipedia 2026 calendars, plus publisher/news confirmation for the big ones
# (Gematsu, RPG Site, Nintendo Life, Push Square, Shacknews, Time Extension, Koei Tecmo, Ubisoft, Epic Games Store news). Checked 24 Nov 2026.
# Left out (one calendar only or unclear): Ravenswatch S2 (18 Dec), Silver Palace (14 Dec), Coral Island S2 (7 Dec), Ancestors S2/PS5/XSX (8 Dec),
# The Road of Dust and Sorrow (3 Dec on 2 calendars but listed for 2027 elsewhere), Rayman Origins Enhanced (GI only).
# (date, title, platforms on our 4 consoles, also-on, genre, note, big, kind)
DEC26 = [
    ("2026-12-01", "Hela", ["PS5", "Xbox Series X|S", "PC", "Switch 2"], "", "Co-op adventure", "A small mouse on a big adventure.", False, "new"),
    ("2026-12-02", "The Ascent: Ultimate Edition", ["Switch 2"], "", "Action RPG", "Switch 2 version of the 2021 cyberpunk shooter.", False, "port"),
    ("2026-12-03", "Dragon Quest Monsters: The Withered World", ["PS5", "Xbox Series X|S", "PC", "Switch 2"], "Switch", "Monster-taming RPG", "Square Enix's next Dragon Quest Monsters, with over 500 monsters to recruit.", True, "new"),
    ("2026-12-03", "Rayman Legends Retold", ["PS5", "Xbox Series X|S", "PC", "Switch 2"], "", "Platformer", "Ubisoft's remake of Rayman Legends. Delayed to 3 December.", True, "remake"),
    ("2026-12-03", "Thief: The Dark Project Remastered", ["PS5", "Xbox Series X|S", "PC", "Switch 2"], "PS4, Xbox One, Switch", "Stealth", "Nightdive's remaster of the 1998 stealth classic.", True, "remake"),
    ("2026-12-03", "Warhammer 40,000: Dawn of War IV", ["PC"], "", "Real-time strategy", "The return of the Dawn of War strategy series. Delayed to 3 December.", True, "new"),
    ("2026-12-03", "Xenoblade Chronicles 3: Nintendo Switch 2 Edition", ["Switch 2"], "", "RPG", "The upgraded Switch 2 version of Xenoblade Chronicles 3.", True, "port"),
    ("2026-12-03", "Edge of Memories", ["PS5", "Xbox Series X|S", "PC"], "", "Action RPG", "Delayed from 5 November to 3 December.", False, "new"),
    ("2026-12-03", "Aeterna Lucis", ["PS5", "Xbox Series X|S", "PC"], "PS4, Xbox One, Switch", "Metroidvania", "Also on Switch 1, not listed for Switch 2.", False, "new"),
    ("2026-12-03", "Eriksholm: The Stolen Dream", ["Switch 2"], "", "Stealth", "Switch 2 version of the 2025 stealth game.", False, "port"),
    ("2026-12-04", "Monster Hunter Wilds", ["Switch 2"], "", "Action RPG", "Capcom's 2025 hit arrives on Switch 2, with local and cross-platform play.", True, "port"),
    ("2026-12-07", "Stronghold 4 (Early Access)", ["PC"], "", "Strategy", "Castle-building strategy in Early Access.", False, "early"),
    ("2026-12-08", "Guns of Eschaton", ["PS5", "Xbox Series X|S", "PC"], "", "", "", False, "new"),
    ("2026-12-10", "Attack on Titan 3", ["PS5", "Xbox Series X|S", "PC", "Switch 2"], "", "Action", "Koei Tecmo's third Attack on Titan game, out the same day as The Game Awards.", True, "new"),
    ("2026-12-10", "Professor Layton and the New World of Steam", ["Switch 2", "PS5", "PC"], "Switch", "Puzzle adventure", "The first new Layton game in over ten years, and the series' first time on PlayStation.", True, "new"),
    ("2026-12-10", "Stage Tour", ["PS5", "Xbox Series X|S", "PC", "Switch 2"], "", "", "", False, "new"),
    ("2026-12-11", "Path of Exile 2 (1.0)", ["PS5", "Xbox Series X|S", "PC"], "", "Action RPG", "The full 1.0 launch after Early Access. Free to play.", True, "early"),
]
DEC26.sort(key=lambda x: x[0])
_dkind = {"new": "New game", "port": "New console version", "remake": "Remake / remaster", "early": "Full launch / Early Access"}
_dbig = [x for x in DEC26 if x[6]]
_dcnt = {p: [x for x in DEC26 if p in x[2]] for p in PLATS}
_dday = {}
for _x in DEC26: _dday.setdefault(_x[0], []).append(_x)
_dbusy = max(_dday.items(), key=lambda kv: len(kv[1]))
_dlast = DEC26[-1]
def _dnice(d): return nice_date({"date": d, "window": ""})
def _drowd(x):
    d, t, pl, also, gen, note, big, kind = x
    meta = " · ".join(v for v in [gen, ", ".join(pl) + (f" (also {also})" if also else ""), _dkind[kind]] if v)
    star = ' <span class="muted">· big release</span>' if big else ""
    return (f'<div class="row" data-dec-date="{d}" data-plat="{e("|".join(pl))}"{" data-big=\"1\"" if big else ""}><span><strong>{e(t)}</strong>{star}'
            + (f'<br><span class="muted">{e(note)}</span>' if note else "")
            + f'<br><span class="muted">{e(meta)}</span></span><b><span class="dec-when">{e(_dnice(d))}</span></b></div>')
_dquick = (f"{len(DEC26)} confirmed games come out in December 2026. The biggest are Dragon Quest Monsters: The Withered World and Rayman Legends Retold (3 December), "
           f"Monster Hunter Wilds on Switch 2 (4 December), Attack on Titan 3 and Professor Layton and the New World of Steam (10 December) and the Path of Exile 2 1.0 launch (11 December). "
           f"The busiest day is {_dnice(_dbusy[0])[:-5]} with {len(_dbusy[1])} launches, and the month goes quiet after {_dnice(_dlast[0])[:-5]}.")
_dchips = ('<div class="chips" role="group" aria-label="Console"><button class="chip" type="button" data-dec-p="" aria-pressed="true">All consoles</button>'
           + "".join(f'<button class="chip" type="button" data-dec-p="{e(p)}" aria-pressed="false">{e(p)}</button>' for p in PLATS)
           + '<button class="chip" type="button" data-dec-p="big" aria-pressed="false">Big releases only</button></div>')
_dtbl = ('<div style="overflow-x:auto"><table class="gen-table" style="width:100%;border-collapse:collapse;font-size:.92rem"><thead><tr><th style="text-align:left;padding:6px">Console</th><th style="padding:6px">December 2026 games</th><th style="text-align:left;padding:6px">Biggest one</th></tr></thead><tbody>'
         + "".join(f'<tr><td style="padding:6px;border-top:1px solid var(--rule)">{e(p)}</td><td class="mono" style="padding:6px;text-align:center;border-top:1px solid var(--rule)">{len(_dcnt[p])}</td>'
                   f'<td style="padding:6px;border-top:1px solid var(--rule)">{e(next((x[1] for x in _dcnt[p] if x[6]), "-"))}</td></tr>' for p in PLATS) + '</tbody></table></div>')
_dremake = [x for x in DEC26 if x[7] in ("port", "remake")]
_ddelay = [x for x in DEC26 if "Delayed" in x[5]]
_jan = sorted([g for g in GAMES if g["month"] == 1 and g["date"]], key=lambda g: g["date"])
_dwk1 = [x for x in DEC26 if x[0] <= "2026-12-06"]
_dold = [x for x in DEC26 if x[3]]
_dfree = [x for x in DEC26 if "free to play" in x[5].lower()]
dec_body = (f'<header class="hero"><div class="wrap"><span class="kicker">December 2026</span>'
            f'<h1>Games coming out in December 2026:<br><span class="amber">{len(DEC26)} launches before 2027.</span></h1>'
            f'<p class="lead">Every confirmed video game release for December 2026 on PS5, Xbox Series X|S, PC and Switch 2, in date order. Games that are already out get marked as you scroll the month.</p>'
            f'<p class="muted" style="margin:0">Last checked {e(UPDATED)} · each date is on at least two trusted release calendars or confirmed by the publisher</p></div></header>'
            f'<section><div class="wrap"><div class="out" style="margin-bottom:24px"><div class="row"><span><strong>Quick answer:</strong> {e(_dquick)}</span></div></div>'
            f'<div class="tool" id="dec-tool"><h2 style="font-size:1.5rem;margin-top:0">What comes out in December 2026 on my console?</h2>'
            f'<p class="muted">Tap your console. Released games are marked "Out now", and the next launch is highlighted. Your choice is remembered on this device.</p>{_dchips}'
            f'<p class="mono amber" id="dec-count" aria-live="polite" style="margin:12px 0 0">{len(DEC26)} games</p><p class="muted" id="dec-next" style="margin:6px 0 0"></p></div></div></section>'
            + AD.format("dec-mid") +
            f'<section><div class="wrap"><div class="sec-head"><h2>What games come out in December 2026?</h2><span class="muted">{len(DEC26)}</span></div>'
            f'<div class="out" id="dec-list" style="margin-bottom:8px">{"".join(_drowd(x) for x in DEC26)}</div>'
            f'<p class="empty" id="dec-none" hidden>No December 2026 games for that console. Try another one.</p>'
            f'<div class="sec-head" style="margin-top:28px"><h2>What are the biggest games of December 2026?</h2><span class="muted">{len(_dbig)}</span></div>'
            f'<div class="out" style="margin-bottom:28px">{"".join(_drowd(x) for x in _dbig)}</div>'
            f'<div class="sec-head"><h2>What is the busiest day in December 2026?</h2><span class="mono amber">{len(_dbusy[1])} launches</span></div>'
            f'<p>{e(_dnice(_dbusy[0]))} is the busiest day of the month: ' + e(", ".join(x[1] for x in _dbusy[1])) + '.</p>'
            f'<div class="sec-head" style="margin-top:28px"><h2>How many December 2026 games are on each console?</h2></div>{_dtbl}'
            f'<div class="sec-head" style="margin-top:28px"><h2>Which December 2026 games were delayed?</h2><span class="muted">{len(_ddelay)}</span></div>'
            f'<div class="out" style="margin-bottom:28px">{"".join(_drowd(x) for x in _ddelay)}</div>'
            f'<div class="sec-head"><h2>Which December 2026 games are remakes or new versions?</h2><span class="muted">{len(_dremake)}</span></div>'
            f'<p>' + e(", ".join(x[1] for x in _dremake)) + '. If you already own the original, check each store for an upgrade price before you buy.</p>'
            f'<div class="sec-head" style="margin-top:28px"><h2>What games come out in the first week of December 2026?</h2><span class="muted">{len(_dwk1)}</span></div>'
            f'<p>Tuesday 1 to Sunday 6 December is the busiest week of the month, with {len(_dwk1)} launches, {len([x for x in _dwk1 if x[6]])} of them big releases:</p>'
            f'<div class="out" style="margin-bottom:28px">{"".join(_drowd(x) for x in _dwk1)}</div>'
            f'<div class="sec-head"><h2>Which December 2026 games are also on PS4, Xbox One or Switch 1?</h2><span class="muted">{len(_dold)}</span></div>'
            f'<div class="out" style="margin-bottom:8px">' + "".join(f'<div class="row"><span><strong>{e(x[1])}</strong><br><span class="muted">Also on {e(x[3])}</span></span><b>{e(_dnice(x[0])[:-5])}</b></div>' for x in _dold) + '</div>'
            f'<p class="muted" style="margin-bottom:28px">Still on an older console in 2027? See <a href="{href("last-gen-games-2027.html", 0)}">2027 games on PS4 and Switch 1</a>.</p>'
            f'<div class="sec-head"><h2>Are any December 2026 games free to play?</h2></div>'
            f'<p>Yes: ' + e(", ".join(f"{x[1]} ({_dnice(x[0])[:-5]})" for x in _dfree)) + '. For free games to keep, see <a href="' + href("epic-free-games.html", 0) + '">Epic free games this week</a> (in recent years Epic has given away a free game every day over the holidays; the 2026 event is not announced yet) and the <a href="' + href("ps-plus-monthly-games.html", 0) + '">PS Plus monthly games</a>.</p>'
            f'<div class="sec-head" style="margin-top:28px"><h2>When is the Steam Winter Sale 2026?</h2></div>'
            f'<p>17 December 2026 to 4 January 2027, per Valve\'s published schedule, so most December PC releases will get their first discount within weeks. Live timer on our <a href="{href("steam-sale-dates.html", 0)}">Steam sale dates</a> page.</p>'
            f'<div class="sec-head" style="margin-top:28px"><h2>Are there any big games out at Christmas 2026?</h2></div>'
            f'<p>No big confirmed launches land between {e(_dnice(_dlast[0])[:-5])} and the end of the year in the release calendars we checked. Publishers rarely launch in the last two weeks of December, '
            f'so the Christmas gap is the time to catch up on GTA 6 (out since 19 November 2026) and the early-December releases above.</p>'
            f'<div class="sec-head" style="margin-top:28px"><h2>What comes out next, in January 2027?</h2><span class="muted">{len(_jan)} dated</span></div>'
            f'<div class="out" style="margin-bottom:12px">' + "".join(f'<div class="row"><span>{_gname(g)}<br><span class="muted">{e(", ".join(g["platforms"]))}</span></span><b>{e(nice_date(g))}</b></div>' for g in _jan[:6]) + '</div>'
            f'<p class="muted"><a href="{href("months/january-2027.html", 0)}">See every January 2027 game →</a></p>'
            f'<p class="muted">Not on the list? We only add a December game once two trusted calendars agree on the date or the publisher confirms it. Smaller PC and mobile releases are left out.</p>'
            f'<div class="sec-head" style="margin-top:28px"><h2>Related pages and tools</h2></div><ul>'
            f'<li><a href="{href("new-games-this-week.html", 0)}">New games this week</a>: the same launches grouped Monday to Sunday</li>'
            f'<li><a href="{href("game-awards-2026.html", 0)}">The Game Awards 2026</a> on 10 December: how to watch, the 2027 nominees and a winner predictor</li>'
            f'<li><a href="{href("after-gta-6.html", 0)}">What to play after GTA 6</a>: the next big games of 2027</li>'
            f'<li><a href="{href("months/january-2027.html", 0)}">January 2027 game releases</a> and the full <a href="{href("calendar.html", 0)}">2027 calendar</a></li>'
            f'<li><a href="{href("backlog-planner-2027.html", 0)}">2027 backlog planner</a>: finish your December games before 2027 starts</li>'
            f'<li><a href="{href("countdown.html", 0)}">Game release countdown</a>: a live timer for any game</li></ul></div></section>')
dec_faq = [
    ("What games come out in December 2026?", _dquick),
    ("What is the biggest game coming out in December 2026?", "Dragon Quest Monsters: The Withered World (3 December), Monster Hunter Wilds on Switch 2 (4 December), Professor Layton and the New World of Steam and Attack on Titan 3 (both 10 December) and the Path of Exile 2 1.0 launch (11 December) are the biggest."),
    ("What games come out on PS5 in December 2026?", f"{len(_dcnt['PS5'])}: " + ", ".join(f"{x[1]} ({_dnice(x[0])[:-5]})" for x in _dcnt["PS5"]) + "."),
    ("What Switch 2 games come out in December 2026?", f"{len(_dcnt['Switch 2'])}: " + ", ".join(f"{x[1]} ({_dnice(x[0])[:-5]})" for x in _dcnt["Switch 2"]) + "."),
    ("What Xbox games come out in December 2026?", f"{len(_dcnt['Xbox Series X|S'])}: " + ", ".join(f"{x[1]} ({_dnice(x[0])[:-5]})" for x in _dcnt["Xbox Series X|S"]) + "."),
    ("Is Monster Hunter Wilds coming to Switch 2?", "Yes. Capcom released the date in the September 2026 Nintendo Direct: 4 December 2026, with local and cross-platform play."),
    ("Is Professor Layton and the New World of Steam on PS5?", "Yes. It launches on 10 December 2026 on Switch 2, Switch, PS5 and PC."),
    ("What games come out the first week of December 2026?", f"{len(_dwk1)} games from 1 to 6 December: " + ", ".join(f"{x[1]} ({_dnice(x[0])[:-5]})" for x in _dwk1) + "."),
    ("Are any December 2026 games on PS4 or Switch 1?", ", ".join(f"{x[1]} (also on {x[3]})" for x in _dold) + "."),
    ("Are any big games coming out at Christmas 2026?", f"No. The last notable confirmed release is {_dlast[1]} on {_dnice(_dlast[0])}. The next wave starts in January 2027."),
]
page("games-december-2026.html", f"Games Coming Out in December 2026: All {len(DEC26)} Releases by Date and Console | DayOneDrop",
     f"Every confirmed game coming out in December 2026 on PS5, Xbox, PC and Switch 2: Dragon Quest Monsters, Monster Hunter Wilds Switch 2, Layton, Attack on Titan 3."[:160],
     dec_body, 0, dec_faq, crumbs=[("Home", DOMAIN + "/"), ("2027 calendar", canon("calendar.html")), ("December 2026 games", canon("games-december-2026.html"))])


# ---------------- WHAT TO PLAY AFTER GTA 6 (21 Nov 2026) ----------------
# GTA 6 launched 19 Nov 2026 and is the biggest search topic in gaming; this page catches "what to play after GTA 6" / "games coming after GTA 6"
# and points GTA players at the 2027 board. Built only from games.json facts (dates/platforms already 2-source checked). Sister site: neoncoast.org.
AFTER_PICKS = [
    ("stranger-than-heaven", "If you love GTA's crime stories"),
    ("forza-horizon-6", "If you love driving around an open world"),
    ("metro-2039", "If you want a tense shooter"),
    ("tomb-raider-legacy-of-atlantis", "If you want a big action adventure"),
    ("persona-4-revival", "If you want a long story with a mystery"),
    ("fable", "If you want another huge world full of choices"),
    ("exodus", "If you want a story-heavy sci-fi RPG"),
    ("final-fantasy-vii-revelation", "If you want the year's biggest RPG finale"),
    ("god-of-war-laufey", "If you want a blockbuster PlayStation exclusive"),
    ("kingdom-hearts-iv", "If you want the long-awaited sequel"),
]
_gby = {g["slug"]: g for g in GAMES}
_picks = [(_gby[s], why) for s, why in AFTER_PICKS if s in _gby]
def _arow(g, why):
    t = f'<a href="{href("games/" + g["slug"] + ".html", 0)}">{e(g["title"])}</a>' if g["page"] else e(g["title"])
    plats = ", ".join(g["platforms"]) or "Platforms TBC"
    return (f'<div class="row"><span><strong>{t}</strong><br><span class="muted">{e(why)}. {e(g.get("about") or "")}</span>'
            f'<br><span class="muted">{e(g.get("genre") or "")} · {e(plats)}</span></span><b>{e(nice_date(g))}</b></div>')
_first = next((g for g, _ in _picks if g["date"]), None)
after_body = (f'<header class="hero"><div class="wrap"><span class="kicker">After GTA 6</span>'
              f'<h1>What to play after GTA 6:<br><span class="amber">the big games of 2027.</span></h1>'
              f'<p class="lead">Finished Leonida, or need a break? These are the biggest confirmed games coming next, in release order, with consoles and dates.</p>'
              f'<p class="muted" style="margin:0">Last checked {e(UPDATED)}</p></div></header>'
              f'<section><div class="wrap"><div class="out" style="margin-bottom:12px"><div class="row"><span><strong>Quick answer:</strong> the next big releases after GTA 6 are '
              + ", ".join(f"{g['title']} ({nice_date(g)})" for g, _ in _picks[:4]) +
              f'. The busiest stretch is February 2027. Before that, December 2026 brings {len(DEC26)} smaller launches, led by Monster Hunter Wilds on Switch 2 and Professor Layton.</span></div></div>'
              f'<div class="sec-head"><h2>What are the next big games after GTA 6?</h2><span class="muted">{len(_picks)} picks</span></div>'
              f'<div class="out" style="margin-bottom:28px">{"".join(_arow(g, w) for g, w in _picks)}</div>'
              f'<div class="sec-head"><h2>Which of these can I play on my console?</h2></div><div class="out" style="margin-bottom:28px">'
              + "".join(f'<div class="row"><span><a href="{href("platforms/" + s2 + ".html", 0)}">{e(l2)}</a><br><span class="muted">{e(", ".join(g["title"] for g, _ in _picks if p2 in g["platforms"]))}</span></span>'
                        f'<b>{sum(1 for g, _ in _picks if p2 in g["platforms"])} of {len(_picks)}</b></div>' for p2, s2, l2 in PLAT_PAGES_FOOT) +
              f'</div><div class="sec-head"><h2>What comes out before 2027, in December 2026?</h2><span class="muted">{len(_dbig)} big ones</span></div>'
              f'<div class="out" style="margin-bottom:12px">' + "".join(f'<div class="row"><span><strong>{e(x[1])}</strong><br><span class="muted">{e(", ".join(x[2]))}</span></span><b>{e(_dnice(x[0]))}</b></div>' for x in _dbig) + '</div>'
              f'<p class="muted" style="margin-bottom:28px">All {len(DEC26)} December launches, with a console filter: <a href="{href("games-december-2026.html", 0)}">games coming out in December 2026</a>.</p>'
              f'<div class="sec-head"><h2>Will there be a GTA 7?</h2></div>'
              f'<p>Not announced. Rockstar and Take-Two have not named a GTA 7, a date or a setting. GTA 6 itself took over ten years after GTA 5 (2013), so any sequel is many years away. '
              f'Anything you read about GTA 7 right now is a rumour.</p>'
              f'<div class="sec-head" style="margin-top:28px"><h2>What is Rockstar making after GTA 6?</h2></div>'
              f'<p>Rockstar has not announced its next game. There is no confirmed Red Dead Redemption 3, Bully 2 or L.A. Noire sequel. For now its focus is GTA 6 and its online mode. '
              f'We will add Rockstar\'s next game to the board the day it is announced with a date.</p>'
              f'<div class="sec-head" style="margin-top:28px"><h2>Is GTA 6 coming to PC?</h2></div>'
              f'<p>No PC version has been announced. GTA 6 launched on PS5 and Xbox Series X|S on 19 November 2026, and Take-Two did not give a PC date in its November 2026 earnings. '
              f'Past Rockstar games reached PC later: GTA 5 (2013) reached PC in April 2015, and Red Dead Redemption 2 (October 2018) in November 2019.</p>'
              f'<div class="sec-head" style="margin-top:28px"><h2>Still playing GTA 6?</h2></div>'
              f'<p>Our sister site <a href="https://neoncoast.org/map" rel="noopener">NeonCoast</a> has an interactive GTA 6 map, a mission tracker, '
              f'every cheat code and a "Can my PC run GTA 6?" checker. There is no GTA 6 PC release date yet.</p>'
              f'<div class="sec-head" style="margin-top:28px"><h2>Related pages and tools</h2></div><ul>'
              f'<li><a href="{href("games-like-gta-6.html", 0)}">Games like GTA 6</a> you can play right now, on every platform</li>'
              f'<li><a href="{href("biggest-games-2027.html", 0)}">The biggest games of 2027</a>: the full list, plus a top list you can share</li>'
              f'<li><a href="{href("rpgs-2027.html", 0)}">Every RPG coming in 2027</a>, with a console filter</li>'
              f'<li><a href="{href("games-like-elden-ring.html", 0)}">Games like Elden Ring</a> and the 2027 soulslikes</li>'
              f'<li><a href="{href("release-clashes-2027.html", 0)}">2027 release clashes</a>: which of these land the same week</li>'
              f'<li><a href="{href("calendar.html", 0)}">2027 release calendar</a> and the <a href="{href("index.html", 0)}#board">departures board</a> for countdowns</li></ul></div></section>')
after_faq = [
    ("What should I play after GTA 6?", "If you liked the crime story, look at Stranger Than Heaven from the makers of Like a Dragon. For open-world driving, Forza Horizon 6 comes to PS5. For a huge world full of choices, Fable. The full list with dates is above."),
    ("What is the next big game after GTA 6?", (f"{_first['title']}, on {nice_date(_first)}, is the first big release on our list." if _first else "See the list above for dates.")),
    ("Which games after GTA 6 are coming to PS5?", ", ".join(f"{g['title']} ({nice_date(g)})" for g, _ in _picks if "PS5" in g["platforms"]) + "."),
    ("Is there a crime game like GTA coming in 2027?", "Stranger Than Heaven, from the Like a Dragon studio, is a crime drama dated " + (nice_date(_gby["stranger-than-heaven"]) if "stranger-than-heaven" in _gby else "for 2027") + ". It is the closest story match to GTA on our 2027 list."),
    ("Will there be a GTA 7?", "Rockstar has not announced GTA 7. There is no date, setting or official confirmation, so any GTA 7 news right now is a rumour."),
    ("What is Rockstar's next game after GTA 6?", "Rockstar has not announced one. Red Dead Redemption 3 and other sequels are unconfirmed."),
    ("What games come out after GTA 6 in December 2026?", f"{len(DEC26)} confirmed games, including Dragon Quest Monsters: The Withered World (3 December), Monster Hunter Wilds on Switch 2 (4 December), Professor Layton and the New World of Steam (10 December) and the Path of Exile 2 1.0 launch (11 December)."),
    ("Is GTA 6 coming to PC?", "Not yet. Rockstar has not announced a PC version or date. GTA 6 launched on PS5 and Xbox Series X|S on 19 November 2026."),
]
page("after-gta-6.html", "What to Play After GTA 6: The Next Big Games (2027) | DayOneDrop",
     "Finished GTA 6? The big games coming next, from December 2026 into 2027, plus: will there be a GTA 7, what Rockstar does next and GTA 6 on PC.",
     after_body, 0, after_faq, crumbs=[("Home", DOMAIN + "/"), ("After GTA 6", canon("after-gta-6.html"))])


# ---------------- GAMES LIKE GTA 6 (24 Nov 2026, demand radar #1) ----------------
# Autocomplete: "games like gta 6" + for ps5 / for pc / for android / roblox / coming out / better than / similar. Facts: Red Bull, Beebom,
# Green Man Gaming, Gaming.net, Sportskeeda, Pro Game Guides (2+ lists per pick); platforms as sold today. Sister site link: neoncoast.org.
LIKE_GTA = [
    # (title, platforms, why, tags)
    ("Grand Theft Auto V", "PS5, Xbox Series X|S, PS4, Xbox One, PC", "The closest thing to GTA 6: Rockstar's last crime epic, three playable criminals, a huge city and GTA Online. Also the only Rockstar GTA on PC right now.", "ps5 pc xbox", "crime chaos cars"),
    ("Red Dead Redemption 2", "PS4, Xbox One, PC (plays on PS5 and Xbox Series X|S)", "Same studio, same level of detail. A Wild West outlaw story with the most alive open world of the last generation.", "ps5 pc xbox", "detail story"),
    ("Cyberpunk 2077", "PS5, Xbox Series X|S, PC, Switch 2", "A neon city full of gangs, cars and side jobs, played in first person with RPG choices. Night City feels the most like Vice City's energy.", "ps5 pc xbox switch", "rpg crime cars"),
    ("Mafia: The Old Country", "PS5, Xbox Series X|S, PC", "A cinematic, story-first mob game set in 1900s Sicily. Less sandbox than GTA, more crime drama.", "ps5 pc xbox", "crime story"),
    ("Mafia: Definitive Edition", "PS4, Xbox One, PC (plays on PS5 and Xbox Series X|S)", "A remake of the 1930s gangster classic: tommy guns, old cars and a tight crime story.", "ps5 pc xbox", "crime story cars"),
    ("Sleeping Dogs: Definitive Edition", "PS4, Xbox One, PC", "GTA in Hong Kong: an undercover cop inside a triad, with martial-arts fights, night markets and car chases.", "pc xbox ps4", "crime cars"),
    ("Watch Dogs 2", "PS4, Xbox One, PC", "Open-world San Francisco where you hack the city instead of only shooting it. Lighter and funnier than GTA.", "pc xbox ps4", "chaos cars"),
    ("Yakuza 0", "PS4, Xbox One, PC", "A 1980s Japanese crime drama with street brawls and hours of side stories. The Like a Dragon series is the GTA of Japan.", "pc xbox ps4", "crime story"),
    ("L.A. Noire", "PS4, Xbox One, Switch, PC", "Rockstar-published 1940s detective game: solve crimes in a recreated Los Angeles instead of committing them.", "pc xbox switch ps4", "story detail cars"),
    ("Just Cause 3", "PS4, Xbox One, PC", "Pure open-world chaos: grappling hooks, wingsuits and explosions. Great if GTA's rampages are your favourite part.", "pc xbox ps4", "chaos"),
    ("Crimson Desert", "PS5, Xbox Series X|S, PC", "A huge 2026 open world to explore. Fantasy, not crime, but the same feeling of freedom and discovery.", "ps5 pc xbox", "detail rpg"),
]
LIKE_MOBILE = [
    ("Grand Theft Auto: The Trilogy (Netflix Games)", "Android, iPhone and iPad (free with a Netflix subscription)", "GTA III, Vice City and San Andreas on your phone. Vice City is the original Miami-style GTA that GTA 6 returns to."),
    ("Bully: Anniversary Edition", "Android, iPhone", "Rockstar's school-yard open world. Small, funny and full of GTA's humour."),
]
LIKE_ROBLOX = [
    ("Jailbreak", "Cops and robbers: escape prison, rob banks and stores, and run from police in fast cars. The most-recommended GTA-style Roblox game."),
    ("Emergency Hamburg", "City roleplay in Hamburg: be a police officer, firefighter, medic, driver or criminal."),
    ("Southwest Florida", "Florida city roleplay based around Bonita Springs, with jobs, cars and police. The closest Roblox setting to GTA 6's Leonida."),
]
_LIKE_LABEL = {"crime": "Crime story", "chaos": "Open-world chaos", "cars": "Cars and chases", "story": "Big story", "detail": "Detailed world", "rpg": "RPG choices"}
_like_rows = "".join(f'<div class="row" data-lp="{e(x[3])}" data-ll="{e(x[4])}"><span><strong>{e(x[0])}</strong><br><span class="muted">{e(x[2])}</span><br><span class="muted">{e(x[1])}</span>'
                     f'<br><span class="muted mono" style="font-size:.78rem">{e(" · ".join(_LIKE_LABEL[k] for k in x[4].split()))}</span></span></div>' for x in LIKE_GTA)
def _plat_list(tag): return ", ".join(x[0] for x in LIKE_GTA if tag in x[3].split())
_like_chips = ('<div class="chips" role="group" aria-label="Platform"><button class="chip" type="button" data-like-p="" aria-pressed="true">Any platform</button>'
               + "".join(f'<button class="chip" type="button" data-like-p="{k}" aria-pressed="false">{l}</button>' for k, l in [("ps5", "PS5"), ("xbox", "Xbox"), ("pc", "PC"), ("switch", "Switch / Switch 2"), ("ps4", "PS4")]) + '</div>'
               '<div class="chips" role="group" aria-label="What you liked" style="margin-top:10px"><button class="chip" type="button" data-like-l="" aria-pressed="true">Anything</button>'
               + "".join(f'<button class="chip" type="button" data-like-l="{k}" aria-pressed="false">{e(l)}</button>' for k, l in _LIKE_LABEL.items()) + '</div>')
# "Is there a game better than GTA 6?" (demand radar R6): honest per-taste comparison, no scores
LIKE_BETTER = [
    ("A slower, more detailed world", "Red Dead Redemption 2", "Same studio. Hunting, camp life and an outlaw story told over dozens of hours."),
    ("More choices and character builds", "Cyberpunk 2077", "You build your character and pick how missions go. GTA 6 has a fixed story."),
    ("A tighter crime story", "Mafia: The Old Country", "Shorter and more cinematic, with no sandbox padding."),
    ("More side stories and fist fights", "Yakuza 0", "Hours of strange side stories and a brawler combat system."),
    ("Bigger explosions", "Just Cause 3", "Grappling hook, wingsuit and destruction everywhere."),
    ("Playing on PC today", "Grand Theft Auto V", "GTA 6 has no PC version yet. GTA V is on PC now, with GTA Online."),
]
_like_soon = [g for g in GAMES if g["slug"] in ("stranger-than-heaven", "forza-horizon-6", "fable", "ananta")]
_like_soon.sort(key=lambda g: (g["date"] or "9999"))
like_body = (f'<header class="hero"><div class="wrap"><span class="kicker">Games like GTA 6</span>'
             f'<h1>Games like GTA 6:<br><span class="amber">what to play next.</span></h1>'
             f'<p class="lead">Open-world crime games you can play right now on PS5, Xbox, PC, phones and Roblox, plus the 2027 games coming next.</p>'
             f'<p class="muted" style="margin:0">Last checked {e(UPDATED)}</p></div></header>'
             f'<section><div class="wrap"><div class="out" style="margin-bottom:12px"><div class="row"><span><strong>Quick answer:</strong> the best games like GTA 6 are '
             f'GTA V and Red Dead Redemption 2 (same studio), Cyberpunk 2077, Mafia: The Old Country and Sleeping Dogs. On phones, play the GTA Trilogy on Netflix Games; '
             f'on Roblox, try Jailbreak. GTA 6 itself is not on PC yet. The next GTA-style game is Stranger Than Heaven, a crime drama due in 2027.</span></div></div>'
             f'<div class="tool" id="like-tool" style="margin-bottom:24px"><h2 style="font-size:1.5rem;margin-top:0">Which game like GTA 6 should I play?</h2>'
             f'<p class="muted">Pick your platform and the part of GTA 6 you liked most. The list below narrows to matching games, and your choice is remembered on this device.</p>{_like_chips}'
             f'<p class="mono amber" id="like-count" aria-live="polite" style="margin:12px 0 0">{len(LIKE_GTA)} games</p></div>'
             f'<div class="sec-head"><h2>What are the best games like GTA 6?</h2><span class="muted">{len(LIKE_GTA)} picks</span></div>'
             f'<div class="out" id="like-list" style="margin-bottom:10px">{_like_rows}</div><p class="empty" id="like-none" hidden>No pick matches both. Try "Anything" or another platform.</p>'
             f'<div style="margin-bottom:28px"></div>'
             f'<div class="sec-head"><h2>What games are like GTA 6 on PS5?</h2></div><p>{e(_plat_list("ps5"))}.</p>'
             f'<div class="sec-head"><h2>What games are like GTA 6 on PC?</h2></div><p>{e(_plat_list("pc"))}. GTA 6 has no PC version or date yet, so GTA V is the closest Rockstar game you can play on PC.</p>'
             f'<div class="sec-head"><h2>What games are like GTA 6 on Xbox?</h2></div><p>{e(_plat_list("xbox"))}.</p>'
             f'<div class="sec-head"><h2>Are there games like GTA 6 for Android and iPhone?</h2></div><div class="out" style="margin-bottom:28px">'
             + "".join(f'<div class="row"><span><strong>{e(t)}</strong><br><span class="muted">{e(w)}</span><br><span class="muted">{e(pl)}</span></span></div>' for t, pl, w in LIKE_MOBILE) +
             f'</div><div class="sec-head"><h2>What are the best free Roblox games like GTA 6?</h2></div><div class="out" style="margin-bottom:28px">'
             + "".join(f'<div class="row"><span><strong>{e(t)}</strong><br><span class="muted">{e(w)}</span></span><b>Free</b></div>' for t, w in LIKE_ROBLOX) +
             f'</div><div class="sec-head"><h2>Is there a game better than GTA 6?</h2></div>'
             f'<p>No game has a bigger, busier modern city than Leonida, but some do one thing better. Pick by what you want more of:</p>'
             f'<div style="overflow-x:auto;margin-bottom:28px"><table class="gen-table" style="width:100%;border-collapse:collapse;font-size:.92rem"><thead><tr><th style="text-align:left;padding:6px">If you want</th><th style="text-align:left;padding:6px">Play</th><th style="text-align:left;padding:6px">Why</th></tr></thead><tbody>'
             + "".join(f'<tr><td style="padding:6px;border-top:1px solid var(--rule)">{e(a)}</td><td style="padding:6px;border-top:1px solid var(--rule)"><strong>{e(b)}</strong></td><td style="padding:6px;border-top:1px solid var(--rule)">{e(c)}</td></tr>' for a, b, c in LIKE_BETTER) +
             f'</tbody></table></div>'
             f'<div class="sec-head"><h2>What upcoming games are like GTA 6?</h2><span class="muted">confirmed dates</span></div>'
             f'<div class="out" style="margin-bottom:12px">' + "".join(_arow(g, w) for g, w in [(g, {"stranger-than-heaven": "Closest crime story", "forza-horizon-6": "Open-world driving", "fable": "Huge open world full of choices", "ananta": "Free modern open city with cars, helicopters and street fights (not a crime story)"}[g["slug"]]) for g in _like_soon]) + '</div>'
             f'<p style="margin-bottom:28px">No other open-world crime game is dated for 2027 yet. Rockstar has not announced its next game. More picks with dates: '
             f'<a href="{href("after-gta-6.html", 0)}">what to play after GTA 6</a> and the <a href="{href("biggest-games-2027.html", 0)}">biggest games of 2027</a>.</p>'
             f'<div class="sec-head"><h2>Still playing GTA 6?</h2></div>'
             f'<p>Our sister site <a href="https://neoncoast.org/map" rel="noopener">NeonCoast</a> has the interactive GTA 6 map, every cheat code, '
             f'<a href="https://neoncoast.org/best-early-cars" rel="noopener">the best early cars</a> and a 100% checklist.</p>'
             f'<div class="sec-head" style="margin-top:28px"><h2>Related pages and tools</h2></div><ul>'
             f'<li><a href="{href("after-gta-6.html", 0)}">What to play after GTA 6</a>: the next big releases in date order</li>'
             f'<li><a href="{href("new-games-this-week.html", 0)}">New games this week</a>, week by week</li>'
             f'<li><a href="{href("games-december-2026.html", 0)}">Games coming out in December 2026</a>, with a console filter</li>'
             f'<li><a href="{href("games-like-elden-ring.html", 0)}">Games like Elden Ring</a>: soulslikes to play now and in 2027</li>'
             f'<li><a href="{href("backlog-planner-2027.html", 0)}">2027 backlog planner</a>: what you can finish before each launch</li></ul></div></section>')
like_faq = [
    ("What is the best game like GTA 6?", "GTA V is the closest: same studio, same kind of crime story and open city. If you have played it, try Red Dead Redemption 2 for Rockstar's detail, or Cyberpunk 2077 for a modern neon city."),
    ("What games are like GTA 6 on PC?", _plat_list("pc") + ". GTA 6 is not on PC yet."),
    ("What games are like GTA 6 on PS5?", _plat_list("ps5") + "."),
    ("Are there games like GTA 6 for Android?", "Yes. The GTA Trilogy (GTA III, Vice City and San Andreas) is on Android and iPhone through Netflix Games, and Bully: Anniversary Edition is on both phones."),
    ("What are the best Roblox games like GTA 6?", "Jailbreak, Emergency Hamburg and Southwest Florida. All three are free open-world roleplay games with cars, jobs and police."),
    ("Is there a game better than GTA 6?", "That depends on what you like. Red Dead Redemption 2 has deeper detail, Cyberpunk 2077 has more RPG choices and Yakuza 0 has more side stories. None has a bigger modern city than GTA 6's Leonida."),
    ("What upcoming games are like GTA 6?", "; ".join(f"{g['title']} ({nice_date(g)}, {', '.join(g['platforms'])})" for g in _like_soon) + ". Stranger Than Heaven, a crime drama from the Like a Dragon studio, is the closest match."),
    ("Is there a GTA-style game coming in 2027?", "Stranger Than Heaven is the closest: a 20th-century Japanese crime drama from Ryu Ga Gotoku Studio. No other open-world crime game has a 2027 date yet."),
    ("What game like GTA 6 can I play on Switch?", _plat_list("switch") + ". GTA 6 is not on Switch 2."),
]
page("games-like-gta-6.html", "Games Like GTA 6: Best Picks for PS5, PC, Android and Roblox | DayOneDrop",
     "Games like GTA 6 to play now, by platform and taste: GTA V, Red Dead 2, Cyberpunk 2077, Mafia. Plus: is any game better than GTA 6, and what's coming next.",
     like_body, 0, like_faq, crumbs=[("Home", DOMAIN + "/"), ("Games like GTA 6", canon("games-like-gta-6.html"))])


# ---------------- DELAYED GAMES TRACKER (21 Nov 2026) ----------------
# Built from games.json status/history only (already 2-source checked). Grows automatically as the data check marks delays.
_delayed = sorted([g for g in GAMES if g["status"] == "delayed"], key=lambda g: (g["month"], g["date"] or "9999"))
def _drow(g):
    t = f'<a href="{href("games/" + g["slug"] + ".html", 0)}">{e(g["title"])}</a>' if g["page"] else e(g["title"])
    last = (g.get("history") or [{}])[-1].get("text", "")
    plats = ", ".join(g["platforms"]) or "Platforms TBC"
    return f'<div class="row"><span><strong>{t}</strong><br><span class="muted">{e(last)}</span><br><span class="muted">{e(plats)}</span></span><b>{e(nice_date(g))}</b></div>'
_dl_m = {}
for _g in _delayed:
    _dl_m.setdefault(_g["month"], []).append(_g)
_dl_top = max(_dl_m.items(), key=lambda kv: len(kv[1])) if _dl_m else None
_dl_month_txt = (f"{MONTHS[_dl_top[0] - 1]} 2027, with {len(_dl_top[1])} delayed games now landing there: " + ", ".join(g["title"] for g in _dl_top[1]) + ". "
                 "Many games that missed late 2026 moved into the first months of 2027.") if _dl_top else "No delayed games right now."
_dl_today = datetime.date.fromisoformat(UPDATED)
_dl_dated = [g for g in _delayed if g["date"] and datetime.date.fromisoformat(g["date"]) >= _dl_today]
_dl_loose = [g for g in _delayed if not g["date"]]
_dl_next = _dl_dated[0] if _dl_dated else None
_dl_next_html = ((f'<div class="sec-head"><h2>Which delayed game launches next?</h2></div>'
                  f'<div class="out" style="margin-bottom:12px">{_drow(_dl_next)}</div>'
                  f'<div class="cdw" style="margin-bottom:28px"><span class="lbl">Countdown to {e(_dl_next["title"])}</span><div class="cd" data-countdown="{_dl_next["date"]}">'
                  '<div class="cd-unit"><span class="flaps" data-u="0"></span><span>Days</span></div><div class="cd-unit"><span class="flaps" data-u="1"></span><span>Hrs</span></div>'
                  '<div class="cd-unit"><span class="flaps" data-u="2"></span><span>Min</span></div><div class="cd-unit"><span class="flaps" data-u="3"></span><span>Sec</span></div></div></div>') if _dl_next else "")
# Refresh 25 Nov 2026: delay counts from history, games moved earlier, GTA 6 delays (only where the developer named GTA 6, 2+ sources).
def _ndel(g): return sum(1 for h in g.get("history", []) if "delay" in h.get("text", "").lower())
_dl_multi = sorted([g for g in _delayed if _ndel(g) >= 2], key=lambda g: (-_ndel(g), g["month"]))
_dl_early = [g for g in GAMES if any(w in h.get("text", "").lower() for h in g.get("history", []) for w in ("moved up", "earlier"))]
DL_GTA6 = [("squadron-42", "Chris Roberts said he did not want to launch into the \"attention buzz saw\" of GTA 6. Moved from 2026 to Q2 2027.", "Letter From the Chairman, Aug 2026, via GamingBolt and TechSpot")]
_dl_gta6 = [(_gby[s2], why, src) for s2, why, src in DL_GTA6 if s2 in _gby]
_dl_multi_html = (f'<div class="sec-head"><h2>Which games have been delayed more than once?</h2><span class="muted">{len(_dl_multi)}</span></div>'
                  f'<p class="muted">Counted from each game\'s date history on this site. Two or more delays is a warning sign, so treat these dates with care.</p>'
                  f'<div class="out" style="margin-bottom:28px">' + ("".join(f'<div class="row"><span><strong>{_gname(g)}</strong><br><span class="muted">' + e(" → ".join(h["when"] + ": " + h["text"] for h in g["history"] if "delay" in h["text"].lower())) + f'</span></span><b>{_ndel(g)} delays · {e(nice_date(g))}</b></div>' for g in _dl_multi) or '<div class="empty">No game on our board has been delayed twice yet.</div>') + '</div>')
_dl_gta6_html = (f'<div class="sec-head"><h2>Which games were delayed because of GTA 6?</h2><span class="muted">{len(_dl_gta6)}</span></div>'
                 f'<p class="muted">GTA 6 launches in November 2026 and many publishers have kept clear of it. We only list a game here when its developer or publisher named GTA 6 as a reason, confirmed by two trusted outlets. Guesses by fans and analysts do not count.</p>'
                 f'<div class="out" style="margin-bottom:28px">' + "".join(f'<div class="row"><span><strong>{_gname(g)}</strong><br><span class="muted">{e(why)}</span><br><span class="muted">Source: {e(src)}</span></span><b>{e(nice_date(g))}</b></div>' for g, why, src in _dl_gta6) + '</div>')
_dl_early_html = ((f'<div class="sec-head"><h2>Have any 2027 games moved earlier?</h2><span class="muted">{len(_dl_early)}</span></div>'
                   f'<div class="out" style="margin-bottom:28px">' + "".join(f'<div class="row"><span><strong>{_gname(g)}</strong><br><span class="muted">{e(g["history"][-1]["text"])}</span></span><b>{e(nice_date(g))}</b></div>' for g in _dl_early) + '</div>') if _dl_early else "")
_dl_loose_html = ((f'<div class="sec-head"><h2>Which delayed games still have no exact date?</h2><span class="muted">{len(_dl_loose)}</span></div>'
                   f'<p class="muted">These were pushed back to a window, not a day. A window is the most likely place for another slip, so we check them on every data run.</p>'
                   f'<div class="out" style="margin-bottom:28px">{"".join(_drow(g) for g in _dl_loose)}</div>') if _dl_loose else "")
delays_body = (f'<header class="hero"><div class="wrap"><span class="kicker">Delay tracker</span>'
               f'<h1>Games delayed to 2027<br><span class="amber">{len(_delayed)} on our board.</span></h1>'
               f'<p class="lead">Every tracked game that has slipped into 2027 or moved to a later date, with its new date and what changed. We add each delay as soon as the publisher or two trusted outlets confirm it.</p>'
               f'<p class="muted" style="margin:0">Last checked {e(UPDATED)}</p></div></header>'
               f'<section><div class="wrap"><div class="out" style="margin-bottom:12px"><div class="row"><span><strong>Quick answer:</strong> {len(_delayed)} games on our 2027 board have been delayed' + (f", and {_dl_next['title']} ({nice_date(_dl_next)}) is the next to launch" if _dl_next else "") + '. The full list: '
               + (", ".join(f"{g['title']} (now {nice_date(g)})" for g in _delayed) if _delayed else "no tracked games are delayed right now") +
               '.' + (f' {len(_dl_multi)} have slipped more than once: ' + ", ".join(g["title"] for g in _dl_multi) + '.' if _dl_multi else '') +
               (f' {_dl_gta6[0][0]["title"]} is the clearest GTA 6 delay: its developer named GTA 6 as the reason.' if _dl_gta6 else '') + f'</span></div></div><div class="sec-head"><h2>Which games have been delayed to 2027?</h2><span class="muted">{len(_delayed)}</span></div>'
               f'<div class="out" style="margin-bottom:28px">{"".join(_drow(g) for g in _delayed)}</div>'
               f'<div class="sec-head"><h2>Which delayed games are on my console?</h2></div><div class="out" style="margin-bottom:28px">'
               + "".join(f'<div class="row"><span><a href="{href("platforms/" + s2 + ".html", 0)}">{e(l2)}</a><br><span class="muted">{e(", ".join(g["title"] for g in _delayed if p2 in g["platforms"]) or "None right now")}</span></span>'
                         f'<b>{sum(1 for g in _delayed if p2 in g["platforms"])} delayed</b></div>' for p2, s2, l2 in PLAT_PAGES_FOOT) +
               f'</div>' + _dl_next_html + _dl_loose_html + _dl_multi_html + _dl_gta6_html + _dl_early_html + f'<div class="sec-head"><h2>Which month do most delayed games land in?</h2></div>'
               f'<p>{e(_dl_month_txt)}</p>'
               f'<p class="muted">Want a heads-up before launch? Star games on the <a href="{href("index.html", 0)}#board">departures board</a> for countdowns.</p>'
               f'<div class="sec-head" style="margin-top:28px"><h2>Related pages and tools</h2></div><ul>'
               f'<li><a href="{href("release-clashes-2027.html", 0)}">2027 release clashes</a>: did a delay push two of your games into the same week?</li>'
               f'<li><a href="{href("calendar.html", 0)}">2027 release calendar</a></li>'
               f'<li><a href="{href("backlog-planner-2027.html", 0)}">2027 backlog planner</a>: use the extra time a delay gives you</li>'
               f'<li><a href="{href("game-pass-2027.html", 0)}">Every 2027 game on Xbox Game Pass</a></li>'
               f'<li><a href="{href("after-gta-6.html", 0)}">What to play after GTA 6</a></li>'
               f'<li><a href="{href("games/squadron-42.html", 0)}">Squadron 42 release guide</a>: the Q2 2027 window and the GTA 6 delay</li></ul></div></section>')
delays_faq = [
    ("Which delayed game comes out next?", f"{_dl_next['title']}, on {nice_date(_dl_next)}." if _dl_next else "None of the delayed games we track has an upcoming exact date."),
    ("Which delayed games still have no release date?", (", ".join(f"{g['title']} ({nice_date(g)})" for g in _dl_loose) + ".") if _dl_loose else "All delayed games we track have an exact date now."),
    ("Which games were delayed to 2027?", ("On our board: " + ", ".join(g["title"] for g in _delayed) + ".") if _delayed else "None of the games we track right now."),
    ("Is God of War Laufey delayed?", "Yes. It was planned for February 2027 and is now dated 20 May 2027 on PS5.") if any(g["slug"] == "god-of-war-laufey" for g in _delayed) else ("How do you track delays?", "We only mark a delay when the publisher or two trusted outlets confirm the new date."),
    ("How do you check delays?", "We only mark a game as delayed when the publisher or at least two trusted gaming news sites confirm the new date or window."),
    ("Which month has the most delayed games?", _dl_month_txt),
    ("Which games have been delayed more than once?", (", ".join(f"{g['title']} ({_ndel(g)} delays, now {nice_date(g)})" for g in _dl_multi) + ".") if _dl_multi else "None on our board yet."),
    ("Which games were delayed because of GTA 6?", " ".join(f"{g['title']}: {why}" for g, why, _ in _dl_gta6) + " We only list games whose developer or publisher named GTA 6 as a reason."),
    ("Is 007 First Light delayed on Switch 2?", "Yes. The Switch 2 version of 007 First Light is now dated 18 March 2027.") if "007-first-light" in {g["slug"] for g in _delayed} else ("Can a delayed game move again?", "Yes. We update the date as soon as a new one is confirmed."),
]
page("delayed-games-2027.html", f"Games Delayed to 2027: Every Delay and New Date ({len(_delayed)}) | DayOneDrop"[:90],
     f"Every game delayed into 2027 or pushed later: the new date, what changed, which delayed game is next and which still have no date. Checked {UPDATED}."[:160],
     delays_body, 0, delays_faq, crumbs=[("Home", DOMAIN + "/"), ("Delayed games 2027", canon("delayed-games-2027.html"))])


# ---------------- XBOX GAME PASS 2027 (22 Nov 2026) ----------------
# Game Pass list = games named for Xbox Game Pass in 2027 by BOTH Pure Xbox (14 Jun 2026 roundup) and Digital Citizen's 2027 Game Pass table
# (Moosa: Pure Xbox Mar + Jun 2026 and Digital Citizen prose). Magicians: The Devil's Deal left out (one source only).
# At Fate's End added 24 Nov 2026: Xbox Wire (Jun 2025 reveal) + Pure Xbox (Oct 2026 delay: 'still coming to Game Pass').
# Day one wording only where confirmed: Fable (Gematsu, RPG Site, VGChartz), Wo Long 2 (games.json fact).
GP_TRACKED = sorted(GP_TRACKED_ALL)
GP_DAY_ONE = {"fable", "wo-long-2"}
GP_OTHER = [("Bad Magpie", "Early 2027"), ("Join Us", "March 2027"), ("Clockwork Revolution", "Spring 2027"),
            ("Alien Deathstorm", "2027"), ("Moosa: Dirty Fate", "2027"), ("Senua", "2027"),
            ("Valor Mortis", "2027"), ("Vivarium", "2027")]
_gp = sorted([_gby[s] for s in GP_TRACKED if s in _gby], key=lambda g: (g["month"], g["date"] or "9999"))
_gp_slugs = {g["slug"] for g in _gp}
_gp_total = len(_gp) + len(GP_OTHER)
_gp_ps5 = [g for g in _gp if "PS5" in g["platforms"]]
_gp_dated = [g for g in _gp if g["date"]]
_xb_buy = sorted([g for g in GAMES if g["slug"] not in _gp_slugs and ("Xbox Series X|S" in g["platforms"] or "PC" in g["platforms"])],
                 key=lambda g: (g["month"], g["date"] or "9999"))
def _gprow(g):
    tag = "Game Pass day one" if g["slug"] in GP_DAY_ONE else "Announced for Game Pass"
    return (f'<div class="row"><span><strong>{_gname(g)}</strong><br><span class="muted">{e(g.get("about") or "")}</span>'
            f'<br><span class="muted">{e(tag)} · {e(", ".join(g["platforms"]))}</span></span><b>{e(nice_date(g))}</b></div>')
_gp_pick = "".join(f'<label class="clash-opt"><input type="checkbox" value="{e(g["slug"])}" data-gp="{1 if g["slug"] in _gp_slugs else 0}"> <span>{e(g["title"])}</span> <span class="muted mono">{e(short_date(g))}</span></label>'
                   for g in sorted(_gp + _xb_buy, key=lambda g: (g["month"], g["date"] or "9999")))
# Refresh 24 Nov 2026: next Game Pass launch, month-by-month table, delayed Game Pass games
_gp_up = [g for g in _gp_dated if g["date"] >= UPDATED]
_gp_n = _gp_up[0] if _gp_up else None
_gp_next_html = ""
if _gp_n:
    _gp_next_html = (f'<div class="sec-head"><h2>Which Game Pass game comes out next?</h2></div>'
                     f'<p>{_gname(_gp_n)} on {e(nice_date(_gp_n))}' + (", on Game Pass from launch day" if _gp_n["slug"] in GP_DAY_ONE else ", announced for Game Pass") + '.'
                     + (" After that: " + e(", ".join(f"{g['title']} ({nice_date(g)})" for g in _gp_up[1:4])) + "." if len(_gp_up) > 1 else "") + '</p>'
                     f'<div class="cdw" style="margin-bottom:28px"><span class="lbl">Countdown to {e(_gp_n["title"])}</span><div class="cd" data-countdown="{_gp_n["date"]}">'
                     '<div class="cd-unit"><span class="flaps" data-u="0"></span><span>Days</span></div><div class="cd-unit"><span class="flaps" data-u="1"></span><span>Hrs</span></div>'
                     '<div class="cd-unit"><span class="flaps" data-u="2"></span><span>Min</span></div><div class="cd-unit"><span class="flaps" data-u="3"></span><span>Sec</span></div></div></div>')
_gp_bym = {}
for _g in _gp:
    _gp_bym.setdefault(_g["month"] if _g["date"] else 13, []).append(_g)
_gp_mtbl = ('<div style="overflow-x:auto"><table class="gen-table" style="width:100%;border-collapse:collapse;font-size:.92rem"><thead><tr><th style="text-align:left;padding:6px">When</th><th style="padding:6px">Games</th><th style="text-align:left;padding:6px">Which ones</th></tr></thead><tbody>'
            + "".join(f'<tr><td style="padding:6px;border-top:1px solid var(--rule)">{e(MONTHS[m - 1] + " 2027" if m < 13 else "No exact date yet")}</td><td class="mono" style="padding:6px;text-align:center;border-top:1px solid var(--rule)">{len(gs)}</td>'
                      f'<td style="padding:6px;border-top:1px solid var(--rule)">{e(", ".join(g["title"] + ("" if g["date"] else " (" + g["window"] + ")") for g in gs))}</td></tr>' for m, gs in sorted(_gp_bym.items()))
            + '</tbody></table></div>')
_gp_del = [g for g in _gp if g["status"] == "delayed" or any("elay" in h.get("text", "") for h in g.get("history") or [])]
_gp_extra = (f'<div class="sec-head" style="margin-top:28px"><h2>When does each Game Pass game arrive in 2027?</h2></div>{_gp_mtbl}'
             f'<p class="muted" style="margin-top:8px">The eight announced games without even a month (Senua, Vivarium and others) are listed above under "What other games are coming".</p>'
             f'<div class="sec-head" style="margin-top:28px"><h2>Which 2027 Game Pass games were delayed?</h2><span class="muted">{len(_gp_del)}</span></div>'
             + (f'<div class="out" style="margin-bottom:12px">' + "".join(f'<div class="row"><span><strong>{_gname(g)}</strong><br><span class="muted">{e(next((h["text"] for h in reversed(g.get("history") or []) if "elay" in h.get("text", "")), "Delayed"))}</span></span><b>{e(nice_date(g))}</b></div>' for g in _gp_del) + '</div>' if _gp_del else '<p>None so far.</p>')
             + f'<p class="muted">A delay does not take a game off Game Pass. Every game above is still announced for the service. Full delay history: <a href="{href("delayed-games-2027.html", 0)}">games delayed to 2027</a>.</p>')
_gp_quick = (f"{_gp_total} games are announced for Xbox Game Pass in 2027 so far. The first big ones are "
             + ", ".join(f"{g['title']} ({nice_date(g)})" for g in _gp_dated[:2]) + (f" and {_gp_dated[2]['title']} ({nice_date(_gp_dated[2])})" if len(_gp_dated) > 2 else "")
             + ". Fable and Wo Long 2 are confirmed for Game Pass on launch day."
             + (f" The next Game Pass launch is {_gp_n['title']} on {nice_date(_gp_n)}." if _gp_n else ""))
gp_body = (f'<header class="hero"><div class="wrap"><span class="kicker">Xbox Game Pass</span>'
           f'<h1>Every 2027 game coming to<br><span class="amber">Xbox Game Pass.</span></h1>'
           f'<p class="lead">Fable, Persona 4 Revival, Wo Long 2 and more are heading to Game Pass in 2027. Here is every confirmed game, when it arrives, '
           f'and a quick check of which games on your list you would still need to buy.</p>'
           f'<p class="muted" style="margin:0">Last checked {e(UPDATED)} · only games announced for Game Pass and reported by trusted outlets</p></div></header>'
           f'<section><div class="wrap"><div class="out" style="margin-bottom:24px"><div class="row"><span><strong>Quick answer:</strong> {e(_gp_quick)}</span></div></div>'
           + _gp_next_html +
           f'<div class="sec-head"><h2>Which 2027 games are on Game Pass?</h2><span class="muted">{len(_gp)}</span></div>'
           f'<div class="out" style="margin-bottom:28px">{"".join(_gprow(g) for g in _gp)}</div>'
           f'<div class="sec-head"><h2>What other games are coming to Game Pass in 2027?</h2><span class="muted">{len(GP_OTHER)}</span></div>'
           f'<p class="muted">Announced for Game Pass, but without an exact date yet. We add them to the board once a date is confirmed.</p>'
           f'<div class="out" style="margin-bottom:28px">' + "".join(f'<div class="row"><span>{e(t)}</span><b>{e(w)}</b></div>' for t, w in GP_OTHER) + '</div>'
           f'<div class="tool" id="gp-tool"><h2 style="font-size:1.5rem;margin-top:0">Game Pass or buy? Check your 2027 list</h2>'
           f'<p class="muted">Tick the Xbox and PC games you want (your ★ list is ticked for you). We split them into games you get with Game Pass and games you would still buy.</p>'
           f'<div class="clash-list" role="group" aria-label="Pick games">{_gp_pick}</div>'
           f'<div class="btns" style="margin-top:10px;display:flex;gap:8px;flex-wrap:wrap"><button class="btn sm" type="button" id="gp-star">Use my ★ list</button><button class="btn line sm" type="button" id="gp-clear">Clear</button></div>'
           f'<div class="out" id="gp-out" aria-live="polite"></div></div></div></section>'
           + AD.format("gp-mid") +
           f'<section><div class="wrap">'
           f'<div class="sec-head"><h2>Are the 2027 Game Pass games also on PS5?</h2></div>'
           f'<p>Yes, most of them. {len(_gp_ps5)} of the {len(_gp)} dated Game Pass games are also coming to PS5: {e(", ".join(g["title"] for g in _gp_ps5))}. '
           f'On PlayStation you buy them; Game Pass only covers Xbox consoles, PC and cloud.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>Which big 2027 Xbox games are not on Game Pass?</h2><span class="muted">{len(_xb_buy)}</span></div>'
           f'<p>These tracked 2027 games are coming to Xbox or PC but are not announced for Game Pass, so plan to buy them: '
           f'{e(", ".join(g["title"] for g in _xb_buy[:14]))}{" and more" if len(_xb_buy) > 14 else ""}. Publishers can add games to Game Pass later.</p>'
           f'<p class="muted">Which Game Pass plan gets new games on launch day can change, so check Xbox\'s own Game Pass page before you subscribe.</p>'
           + _gp_extra +
           f'<div class="sec-head" style="margin-top:28px"><h2>Related pages and tools</h2></div><ul>'
           f'<li><a href="{href("new-games-this-week.html", 0)}">New games this week</a>, week by week, with an Xbox filter</li>'
           f'<li><a href="{href("platforms/xbox-series.html", 0)}">Every Xbox Series X|S game coming in 2027</a></li>'
           f'<li><a href="{href("exclusives-2027.html", 0)}">2027 console exclusives</a>: is anything Xbox-only?</li>'
           f'<li><a href="{href("xbox-games-showcase-2027.html", 0)}">Xbox Games Showcase 2027</a>: likely date and games still without one</li>'
           f'<li><a href="{href("release-clashes-2027.html", 0)}">2027 release clashes</a>: which games land the same week</li></ul></div></section>')
gp_faq = [
    ("What games are coming to Xbox Game Pass in 2027?", f"{_gp_total} announced so far: " + ", ".join(g["title"] for g in _gp) + ", " + ", ".join(t for t, _ in GP_OTHER) + "."),
    ("Is Fable on Game Pass day one?", f"Yes. Fable launches on {nice_date(_gby['fable'])} and is on Game Pass from launch day. It also comes to PS5 and PC." if "fable" in _gby else "Yes, Fable is on Game Pass from launch day."),
    ("Is Persona 4 Revival on Game Pass?", f"Yes. Persona 4 Revival is announced for Game Pass and launches on {nice_date(_gby['persona-4-revival'])}." if "persona-4-revival" in _gby else "Yes, it is announced for Game Pass."),
    ("What is the first Game Pass game of 2027?", f"{_gp_dated[0]['title']}, on {nice_date(_gp_dated[0])}, is the first dated one we track." if _gp_dated else "None are dated yet."),
    ("Is At Fate's End on Game Pass?", "Yes. Thunder Lotus's At Fate's End is still coming to Game Pass after its delay to 2027. It has no exact date yet."),
    ("Which Game Pass game comes out next?", (f"{_gp_n['title']} on {nice_date(_gp_n)}." + (" After that: " + ", ".join(f"{g['title']} ({nice_date(g)})" for g in _gp_up[1:3]) + "." if len(_gp_up) > 1 else "")) if _gp_n else "None are dated yet."),
    ("Are Game Pass games also on PS5?", f"Many are. {', '.join(g['title'] for g in _gp_ps5)} are also coming to PS5, where you buy them."),
]
page("game-pass-2027.html", f"Xbox Game Pass 2027: Every Confirmed Game ({_gp_total}) | DayOneDrop"[:90],
     f"All {_gp_total} games announced for Xbox Game Pass in 2027, with dates: Fable, Persona 4 Revival, Wo Long 2, Spyro and more. Plus a Game Pass or buy checker."[:160],
     gp_body, 0, gp_faq, crumbs=[("Home", DOMAIN + "/"), ("All games", canon("games.html")), ("Game Pass 2027", canon("game-pass-2027.html"))])


# ---------------- NEW GAMES THIS WEEK (24 Nov 2026) ----------------
# Week-by-week release schedule (Monday to Sunday) from DEC26 + dated games.json games. Build-time text uses the build date;
# app.js (#wk-tool) re-works out "this week" / "next week" in the reader's own time, so the page stays right between builds.
_WK_DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
_wk_items = []
for _x in DEC26:
    _wk_items.append({"date": _x[0], "title": _x[1], "plats": _x[2], "big": bool(_x[6]), "name": e(_x[1]), "note": _x[4] or _dkind[_x[7]]})
for _g in GAMES:
    if _g["date"]:
        _wk_items.append({"date": _g["date"], "title": _g["title"], "plats": _g["platforms"], "big": bool(_g["page"] or _g["slug"] in BIG_WHY_SLUGS),
                          "name": _gname(_g), "note": _g["genre"] + (" · delayed" if _g["status"] == "delayed" else "")})
_wk_items.sort(key=lambda x: (x["date"], not x["big"], x["title"]))
def _wk_mon(ds):
    d = datetime.date.fromisoformat(ds)
    return d - datetime.timedelta(days=d.weekday())
_wk_today = datetime.date.fromisoformat(UPDATED)
_wk_this = _wk_today - datetime.timedelta(days=_wk_today.weekday())
_wk_last = _wk_mon(_wk_items[-1]["date"])
_wk_map = {}
for _x in _wk_items:
    _wk_map.setdefault(_wk_mon(_x["date"]), []).append(_x)
_wk_list = []
_m = _wk_this
while _m <= _wk_last:
    _wk_list.append((_m, _wk_map.get(_m, [])))
    _m += datetime.timedelta(days=7)
def _wk_lab(mon):
    sun = mon + datetime.timedelta(days=6)
    return f"{_dm(mon)} to {_dm(sun)} {sun.year}"
def _wk_dayname(ds): return _WK_DAYS[datetime.date.fromisoformat(ds).weekday()]
def _wk_row(x):
    return (f'<div class="row" data-wk-date="{x["date"]}" data-plat="{e("|".join(x["plats"]))}"{" data-big=\"1\"" if x["big"] else ""}>'
            f'<span><strong>{x["name"]}</strong>{" <span class=\"muted\">· big release</span>" if x["big"] else ""}'
            f'<br><span class="muted">{e(x["note"])} · {e(", ".join(x["plats"]))}</span></span>'
            f'<b><span class="wk-when">{e(_wk_dayname(x["date"])[:3])} {e(_dm(datetime.date.fromisoformat(x["date"])))}</span></b></div>')
def _wk_block(mon, xs):
    end = mon + datetime.timedelta(days=6)
    lab = "This week" if mon == _wk_this else "Next week" if mon == _wk_this + datetime.timedelta(days=7) else ""
    rows = "".join(_wk_row(x) for x in xs) or '<div class="empty">No tracked launches this week.</div>'
    return (f'<div class="tool wk" data-wk-start="{mon.isoformat()}" data-wk-end="{end.isoformat()}" style="margin-bottom:14px">'
            f'<div class="sec-head" style="margin:0"><h3 style="margin:0;font-size:1.15rem">Week of {e(_wk_lab(mon))}</h3>'
            f'<span class="mono amber"><span class="wk-lbl">{lab}</span>{" · " if lab else ""}<span class="wk-n">{len(xs)}</span> game{"s" if len(xs) != 1 else ""}</span></div>'
            f'<div class="out">{rows}</div><p class="empty wk-none" hidden>Nothing for that console this week.</p></div>')
_wk_now = _wk_map.get(_wk_this, [])
_wk_now_left = [x for x in _wk_now if x["date"] >= UPDATED]
_wk_next = _wk_map.get(_wk_this + datetime.timedelta(days=7), [])
_wk_future = [(m, xs) for m, xs in _wk_list if xs]
_wk_busy = sorted(_wk_future, key=lambda kv: (-len(kv[1]), kv[0]))[:6]
_wk_nextbig = next((x for x in _wk_items if x["big"] and x["date"] >= UPDATED), None)
_wk_dow = {}
for _x in _wk_items:
    _wk_dow[_wk_dayname(_x["date"])] = _wk_dow.get(_wk_dayname(_x["date"]), 0) + 1
_wk_dow_sorted = sorted(_wk_dow.items(), key=lambda kv: -kv[1])
_wk_quiet = [m for m, xs in _wk_list if not any(x["big"] for x in xs)]
def _wk_names(xs, n=4):
    big = [x for x in xs if x["big"]] or xs
    out = ", ".join(x["title"] for x in big[:n])
    return out + (f" and {len(xs) - min(n, len(big))} more" if len(xs) > min(n, len(big)) else "")
if _wk_now_left:
    _wk_q1 = f"This week ({_wk_lab(_wk_this)}) {len(_wk_now_left)} tracked game{'s' if len(_wk_now_left) != 1 else ''} still come{'s' if len(_wk_now_left) == 1 else ''} out: {_wk_names(_wk_now_left)}."
else:
    _wk_q1 = f"No tracked games come out for the rest of this week ({_wk_lab(_wk_this)})."
_wk_q2 = (f" Next week ({_wk_lab(_wk_this + datetime.timedelta(days=7))}) brings {len(_wk_next)}: {_wk_names(_wk_next)}." if _wk_next else " Next week has no tracked launches.")
_wk_quick = _wk_q1 + _wk_q2
_wk_chips = ('<div class="chips" role="group" aria-label="Console"><button class="chip" type="button" data-wk-p="" aria-pressed="true">All consoles</button>'
             + "".join(f'<button class="chip" type="button" data-wk-p="{e(p)}" aria-pressed="false">{e(p)}</button>' for p in PLATS)
             + '<button class="chip" type="button" data-wk-p="big" aria-pressed="false">Big releases only</button></div>')
_wk_busy_tbl = ('<div style="overflow-x:auto"><table class="gen-table" style="width:100%;border-collapse:collapse;font-size:.92rem"><thead><tr><th style="text-align:left;padding:6px">Week</th><th style="padding:6px">Games</th><th style="text-align:left;padding:6px">Biggest launches</th></tr></thead><tbody>'
                + "".join(f'<tr><td style="padding:6px;border-top:1px solid var(--rule)">{e(_wk_lab(m))}</td><td class="mono" style="padding:6px;text-align:center;border-top:1px solid var(--rule)">{len(xs)}</td>'
                          f'<td style="padding:6px;border-top:1px solid var(--rule)">{e(_wk_names(xs, 3))}</td></tr>' for m, xs in _wk_busy) + '</tbody></table></div>')
_wk_dow_rows = "".join(f'<div class="row"><span>{e(d)}</span><b>{n} launch{"es" if n != 1 else ""}</b></div>' for d, n in _wk_dow_sorted)
wk_body = (f'<header class="hero"><div class="wrap"><span class="kicker">Week by week</span>'
           f'<h1>New games coming out<br><span class="amber">this week and next.</span></h1>'
           f'<p class="lead">Every confirmed game launch on PS5, Xbox Series X|S, PC and Switch 2, grouped Monday to Sunday from now until {e(_dm(_wk_last + datetime.timedelta(days=6)))} {(_wk_last + datetime.timedelta(days=6)).year}. '
           f'"This week" moves on by itself, so you can bookmark this page and check it every Monday.</p>'
           f'<p class="muted" style="margin:0">Last checked {e(UPDATED)} · {len(_wk_items)} dated launches · each date confirmed by the publisher or two trusted outlets</p></div></header>'
           f'<section><div class="wrap"><div class="out" style="margin-bottom:24px"><div class="row"><span><strong>Quick answer:</strong> <span id="wk-quick">{e(_wk_quick)}</span></span></div></div>'
           f'<div class="tool" id="wk-tool"><h2 style="font-size:1.5rem;margin-top:0">What games come out this week on my console?</h2>'
           f'<p class="muted">Tap your console. Past weeks are hidden, games already out are marked "Out now" and the next launch is highlighted. Your choice is remembered on this device.</p>{_wk_chips}'
           f'<p class="mono amber" id="wk-count" aria-live="polite" style="margin:12px 0 0">{len(_wk_items)} games</p><p class="muted" id="wk-next" style="margin:6px 0 0"></p></div></div></section>'
           + AD.format("wk-mid") +
           f'<section><div class="wrap"><div class="sec-head"><h2>What games are coming out week by week?</h2><span class="muted">{len(_wk_list)} weeks</span></div>'
           f'<div id="wk-list">{"".join(_wk_block(m, xs) for m, xs in _wk_list)}</div>'
           f'<div class="sec-head" style="margin-top:28px"><h2>When is the next big release?</h2></div>'
           + (f'<p>{_wk_nextbig["name"]} on {e(_wk_dayname(_wk_nextbig["date"]))} {e(nice_date({"date": _wk_nextbig["date"], "window": ""}))} ({e(", ".join(_wk_nextbig["plats"]))}).</p>'
              f'<div class="cdw"><span class="lbl">Countdown to {e(_wk_nextbig["title"])}</span><div class="cd" data-countdown="{_wk_nextbig["date"]}">'
              '<div class="cd-unit"><span class="flaps" data-u="0"></span><span>Days</span></div><div class="cd-unit"><span class="flaps" data-u="1"></span><span>Hrs</span></div>'
              '<div class="cd-unit"><span class="flaps" data-u="2"></span><span>Min</span></div><div class="cd-unit"><span class="flaps" data-u="3"></span><span>Sec</span></div></div></div>' if _wk_nextbig else '<p>No big release is dated yet.</p>')
           + f'<div class="sec-head" style="margin-top:28px"><h2>Which weeks are the busiest?</h2></div>{_wk_busy_tbl}'
           f'<p class="muted" style="margin-top:8px">Planning around a crowded week? The <a href="{href("release-clashes-2027.html", 0)}">release clash checker</a> shows which of your own games land close together.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>What day of the week do new games come out?</h2></div>'
           f'<p>Mostly {e(_wk_dow_sorted[0][0])}s and {e(_wk_dow_sorted[1][0])}s. Of the {len(_wk_items)} dated launches on this page, {_wk_dow_sorted[0][1]} land on a {e(_wk_dow_sorted[0][0])} and {_wk_dow_sorted[1][1]} on a {e(_wk_dow_sorted[1][0])}. '
           f'Digital versions usually unlock at midnight local time or at a set global time, so check the store page for the exact hour.</p>'
           f'<div class="out" style="margin-bottom:28px">{_wk_dow_rows}</div>'
           f'<div class="sec-head"><h2>Which weeks have no big releases?</h2><span class="muted">{len(_wk_quiet)} of {len(_wk_list)}</span></div>'
           f'<p>{len(_wk_quiet)} of the next {len(_wk_list)} weeks have no big launch, which makes them good weeks to catch up on your backlog. The <a href="{href("backlog-planner-2027.html", 0)}">backlog planner</a> works out what you can finish before each launch.</p>'
           f'<p class="muted">Not on the list? We add a game once its exact day is confirmed. Games with only a month or season (like Spyro: A Realm Beyond in spring 2027) are on the <a href="{href("calendar.html", 0)}">2027 calendar</a> and move here when they get a date.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>Related pages and tools</h2></div><ul>'
           f'<li><a href="{href("games-december-2026.html", 0)}">Games coming out in December 2026</a>, with the busiest day and Christmas gap</li>'
           f'<li><a href="{href("months/january-2027.html", 0)}">January 2027 game releases</a> and the full <a href="{href("calendar.html", 0)}">2027 calendar</a></li>'
           f'<li><a href="{href("biggest-games-2027.html", 0)}">The biggest games of 2027</a></li>'
           f'<li><a href="{href("release-clashes-2027.html", 0)}">2027 release clash checker</a></li></ul></div></section>')
wk_faq = [
    ("What games come out this week?", _wk_q1 + " This page updates the week on its own, so it is always the current week when you open it."),
    ("What games come out next week?", _wk_q2.strip()),
    ("What day do new video games come out?", f"Most launch on a {_wk_dow_sorted[0][0]} or {_wk_dow_sorted[1][0]}: {_wk_dow_sorted[0][1]} and {_wk_dow_sorted[1][1]} of the {len(_wk_items)} dated launches we track."),
    ("What is the busiest week for game releases coming up?", f"{_wk_lab(_wk_busy[0][0])}, with {len(_wk_busy[0][1])} launches including {_wk_names(_wk_busy[0][1], 3)}." if _wk_busy else "No week has more than one launch yet."),
    ("When is the next big game release?", (f"{_wk_nextbig['title']} on {nice_date({'date': _wk_nextbig['date'], 'window': ''})}." if _wk_nextbig else "No big release is dated yet.")),
]
page("new-games-this-week.html", "New Games Coming Out This Week and Next (Week by Week) | DayOneDrop",
     f"New games coming out this week and next on PS5, Xbox, PC and Switch 2: every confirmed launch grouped Monday to Sunday, with console filter and countdowns."[:160],
     wk_body, 0, wk_faq, crumbs=[("Home", DOMAIN + "/"), ("2027 calendar", canon("calendar.html")), ("New games this week", canon("new-games-this-week.html"))])


# ---------------- THE GAME AWARDS 2026 (24 Nov 2026) ----------------
# Nominees: Kotaku (17 Nov 2026) and ScreenRant (17 Nov 2026) list the same five Most Anticipated nominees; Nintendo's own post confirms the
# Switch ones (FFVII Revelation, RE Veronica) and three GOTY nominees. Date/venue: thegameawards.com (2 Feb 2026), Nintendo Life (Peacock Theater).
# Streams: Shacknews (13 Nov 2026: YouTube, Twitch, Roblox 18+, Disney+), Disney+ also GGRecon / Pocket Tactics. Start time NOT confirmed by a trusted
# outlet when checked (24 Nov). 26 Nov: start time 7:30pm ET / 4:30pm PT from Disney's press release (via GamingTrend 12 Nov) + GGRecon + Pocket Tactics (13 Nov);
# Roblox is Shacknews-only, so kept as "reported". Disney+ needs a subscription (implied by Shacknews + Pocket Tactics); YouTube/Twitch stay free. Witcher 4: CD Projekt "targeting" 2028 (TechRadar, 25 Aug 2026), so it is not on our 2027 board.
TGA_DATE = "2026-12-10"
TGA_ANTICIPATED = ["fable", "final-fantasy-vii-revelation", "god-of-war-laufey", "resident-evil-veronica", "the-witcher-4"]
TGA_EXTRA = {"the-witcher-4": {"title": "The Witcher 4", "platforms": [], "dev": "CD Projekt Red",
             "when": "2028 (target)", "note": "CD Projekt said in August 2026 it is targeting 2028, so it is not a 2027 game."}}
TGA_GOTY = ["007 First Light", "Control Resonant", "Grand Theft Auto 6", "Phantom Blade Zero", "Resident Evil Requiem", "The Legend of Zelda: Ocarina of Time"]

TGA_CATS = [  # official list 17 Nov 2026, cross-checked Gematsu + Push Square
    ("Game of the Year", TGA_GOTY),
    ("Best Game Direction", ["Control Resonant", "Grand Theft Auto 6", "Phantom Blade Zero", "Pragmata", "Resident Evil Requiem"]),
    ("Best Narrative", ["007 First Light", "The Blood of Dawnwalker", "Control Resonant", "Grand Theft Auto 6", "Resident Evil Requiem"]),
    ("Best Art Direction", ["Control Resonant", "Grand Theft Auto 6", "Mouse: P.I. for Hire", "The Legend of Zelda: Ocarina of Time", "Phantom Blade Zero"]),
    ("Best Score and Music", ["Ace Combat 8: Wings of Theve", "Grand Theft Auto 6", "Mixtape", "The Legend of Zelda: Ocarina of Time", "Phantom Blade Zero"]),
    ("Best Audio Design", ["Ace Combat 8: Wings of Theve", "Control Resonant", "Grand Theft Auto 6", "Resident Evil Requiem", "Star Wars: Galactic Racer"]),
    ("Best Performance", ["Angela Sant'Albano (Resident Evil Requiem)", "Liam McIntyre (Marvel's Wolverine)", "Manni L. Perez (Grand Theft Auto 6)", "Patrick Gibson (007 First Light)", "Rahul Kohli (Saros)"]),
    ("Innovation in Accessibility", ["Assassin's Creed Black Flag Resynced", "Forza Horizon 6", "Gears of War: E-Day", "Marvel's Wolverine", "Rhythm Heaven Groove"]),
    ("Games for Impact", ["Big Walk", "Cairn", "Forever Ago", "Life is Strange: Reunion", "Lily's World XD", "Mixtape"]),
    ("Best Ongoing Game", ["Arc Raiders", "Final Fantasy XIV", "Fortnite", "No Man's Sky", "The Witcher 3: Wild Hunt"]),
    ("Best Community Support", ["Crimson Desert", "Helldivers 2", "No Man's Sky", "The Witcher 3: Wild Hunt", "Warframe"]),
    ("Best Independent Game", ["Big Walk", "Cairn", "Denshattack!", "Mewgenics", "Mina the Hollower"]),
    ("Best Debut Indie Game", ["Dressmaker", "Esoteric Ebb", "Orbitals", "Replaced", "Silver Pines"]),
    ("Best Mobile Game", ["Arknights: Endfield", "Monster Hunter Outlanders", "Neverness to Everness", "Pokémon Champions", "Where Winds Meet"]),
    ("Best VR / AR Game", ["Forefront", "Into the Radius 2", "Little Nightmares VR: Altered Echoes", "Teenage Mutant Ninja Turtles: Empire City", "Thief VR: Legacy of Shadow"]),
    ("Best Action Game", ["Ace Combat 8: Wings of Theve", "Gears of War: E-Day", "Onimusha: Way of the Sword", "Phantom Blade Zero", "Saros"]),
    ("Best Action / Adventure Game", ["007 First Light", "Control Resonant", "Grand Theft Auto 6", "Pragmata", "Resident Evil Requiem", "The Legend of Zelda: Ocarina of Time"]),
    ("Best Role-Playing Game", ["The Blood of Dawnwalker", "Final Fantasy Resonance", "Fire Emblem: Fortune's Weave", "Monster Hunter Stories 3: Twisted Reflection", "Trails in the Sky 2nd Chapter"]),
    ("Best Fighting Game", ["2XKO", "Avatar Legends: The Fighting Game", "Invincible VS", "Marvel Tokon: Fighting Souls", "My Hero Academia: All's Justice"]),
    ("Best Family Game", ["Big Walk", "LEGO Batman: Legacy of the Dark Knight", "Nintendo Switch Sports Resort", "Pokémon Pokopia", "Yoshi and the Mysterious Book"]),
    ("Best Sim / Strategy Game", ["Mewgenics", "Planet Zoo 2", "Pokémon Pokopia", "Slay the Spire 2", "Star Wars Zero Company"]),
    ("Best Sports / Racing Game", ["EA Sports FC 27", "Forza Horizon 6", "Nintendo Switch Sports Resort", "Screamer", "Star Wars: Galactic Racer"]),
    ("Best Multiplayer Game", ["Big Walk", "Call of Duty: Modern Warfare 4", "Gears of War: E-Day", "Marathon", "Meccha Chameleon", "Orbitals"]),
    ("Best Adaptation", ["Cyberpunk: Edgerunners 2", "Fallout (Season 2)", "Mortal Kombat II", "Resident Evil", "The Super Mario Galaxy Movie"]),
    ("Most Anticipated Game", ["Fable", "Final Fantasy VII Revelation", "God of War Laufey", "Resident Evil Veronica", "The Witcher 4"]),
]
TGA_VOTE_END = "9 December 2026, 6pm PT (9pm ET)"
TGA_START_UTC = "2026-12-11T00:30:00Z"  # 7:30pm ET / 4:30pm PT on 10 Dec
TGA_ZONES = [("Los Angeles (PT)", "4:30pm Thu 10 Dec"), ("New York (ET)", "7:30pm Thu 10 Dec"), ("London (GMT)", "12:30am Fri 11 Dec"), ("Paris, Berlin (CET)", "1:30am Fri 11 Dec"), ("Dubai (GST)", "4:30am Fri 11 Dec"), ("Karachi, Lahore (PKT)", "5:30am Fri 11 Dec"), ("India (IST)", "6:00am Fri 11 Dec"), ("Tokyo (JST)", "9:30am Fri 11 Dec"), ("Sydney (AEDT)", "11:30am Fri 11 Dec")]

# ---------------- BIGGEST GAMES OF 2027 (23 Nov 2026) ----------------
# Editorial pick: new entries in major series or from major studios. Dates/platforms come from games.json only.
BIG_WHY = {
    "stranger-than-heaven": "A brand-new crime saga from the Like a Dragon studio, and it is in Xbox Game Pass.",
    "forza-horizon-6": "The Japan-set racer finally reaches PS5, after launching on Xbox and PC in May 2026.",
    "metroid-ravenous": "Nintendo's next 2D Metroid, from MercurySteam, the team that made Metroid Dread.",
    "until-dawn-2": "The sequel to the choice-driven horror hit, and a PS5 exclusive.",
    "metro-2039": "The next Metro shooter from 4A Games, out on PS5, Xbox and PC on the same day.",
    "tomb-raider-legacy-of-atlantis": "A ground-up remake of Lara Croft's first adventure, also coming to Switch 2.",
    "persona-4-revival": "A full remake of Persona 4 Golden, on every current console and in Game Pass.",
    "fable": "Playground Games' reboot of Fable. Xbox's headline game of early 2027, and also on PS5.",
    "wo-long-2": "Team Ninja's next hard-hitting action RPG, in Game Pass from day one.",
    "exodus": "A big new sci-fi RPG from a studio of veteran RPG makers, where space travel ages the world around you.",
    "final-fantasy-vii-revelation": "The last part of the Final Fantasy VII remake trilogy, now on Xbox and Switch 2 as well.",
    "lords-of-the-fallen-ii": "The sequel to the 2023 soulslike, now set for April 2027 after two delays, and coming to Switch 2 and Steam.",
    "spyro-a-realm-beyond": "A new Spyro the Dragon adventure, announced for Xbox Game Pass.",
    "god-of-war-laufey": "The next main God of War, with Faye as the hero for the first time. PS5 only.",
    "squadron-42": "The single-player Star Citizen campaign with Mark Hamill and Gary Oldman, delayed from 2026 to dodge GTA 6. PC only.",
    "kingdom-hearts-iv": "The next main Kingdom Hearts game, aiming for late 2027.",
    "kirby-and-the-world-beyond": "A new Kirby adventure made for Switch 2.",
    "pokemon-winds-and-waves": "The Generation 10 main Pokémon games, only on Switch 2.",
    "xenoblade-genesis": "A new Xenoblade role-playing game for Switch 2.",
    "resident-evil-veronica": "Capcom's remake of Resident Evil Code: Veronica, on every current console including Switch 2.",
}
_gbs = {g["slug"]: g for g in GAMES}
assert set(BIG_WHY) == BIG_WHY_SLUGS
_bg = [_gbs[s] for s in BIG_WHY if s in _gbs]
_bg.sort(key=lambda g: (g["month"], g["date"] or "9999"))
_bg_dated = [g for g in _bg if g["date"]]
_bg_open = [g for g in _bg if not g["date"]]
_bg_delay = [g for g in _bg if g["status"] == "delayed"]
def _bq(g):
    return (g["month"] - 1) // 3 + 1
_bg_q = {}
for _g in _bg:
    _bg_q.setdefault((_bq(_g) if _g["window"] != "2027" else 5), []).append(_g)
_bg_qlab = {1: "January to March 2027 (Q1)", 2: "April to June 2027 (Q2)", 3: "July to September 2027 (Q3)", 4: "October to December 2027 (Q4)", 5: "Sometime in 2027 (no month yet)"}
_bg_cnt = {p: [g for g in _bg if p in g["platforms"]] for p in PLATS}
_bg_pslug = {p2: s2 for p2, s2, l2 in PLAT_PAGES_FOOT}
_bg_plab = {p2: l2 for p2, s2, l2 in PLAT_PAGES_FOOT}
def _bgrow(g, i=None):
    plats = ", ".join(g["platforms"]) or "Platforms TBC"
    flag = ' <span class="muted">(delayed)</span>' if g["status"] == "delayed" else ""
    if g["slug"] in TGA_ANTICIPATED: flag += ' <span class="muted">· Game Awards nominee</span>'
    return (f'<div class="row" data-plat="{e("|".join(g["platforms"]))}"><span><strong>{_gname(g)}</strong>{flag}'
            f'<br><span class="muted">{e(BIG_WHY[g["slug"]])}</span><br><span class="muted">{e(plats)}</span></span><b>{e(nice_date(g))}</b></div>')
_bg_secs = "".join(
    f'<div class="sec-head"><h3 style="margin:0;font-size:1.2rem">{e(_bg_qlab[q])}</h3><span class="muted">{len(_bg_q[q])}</span></div>'
    f'<div class="out" style="margin-bottom:22px">{"".join(_bgrow(g) for g in _bg_q[q])}</div>' for q in sorted(_bg_q))
_bg_q1 = len(_bg_q.get(1, []))
_bg_quick = (f"The biggest games of 2027 include Persona 4 Revival ({nice_date(_gbs['persona-4-revival'])}), Fable ({nice_date(_gbs['fable'])}), "
             f"Final Fantasy VII Revelation ({nice_date(_gbs['final-fantasy-vii-revelation'])}), God of War Laufey ({nice_date(_gbs['god-of-war-laufey'])}) "
             f"and Pokémon Winds and Waves (2027, no date yet). {_bg_q1} of our {len(_bg)} picks land in January to March, so the first quarter is the most crowded. "
             f"Four of them are up for Most Anticipated Game at The Game Awards on 10 December 2026.")
_bg_tga = [_gbs[x] for x in TGA_ANTICIPATED if x in _gbs]
_bg_tga_html = (f'<div class="sec-head"><h2>Which 2027 games are up for Most Anticipated Game at The Game Awards 2026?</h2><span class="muted">{len(_bg_tga)} of 5</span></div>'
    f'<div class="out" style="margin-bottom:12px">' + "".join(f'<div class="row"><span>{_gname(g)}<br><span class="muted">{e(", ".join(g["platforms"]))}</span></span><b>{e(nice_date(g))}</b></div>' for g in _bg_tga)
    + f'<div class="row"><span>The Witcher 4<br><span class="muted">{e(TGA_EXTRA["the-witcher-4"]["note"])}</span></span><b>2028</b></div></div>'
    f'<p class="muted" style="margin-bottom:28px">The winner is named on 10 December 2026. See every nominee and pick your winner on our <a href="{href("game-awards-2026.html", 0)}">Game Awards 2026 page</a>.</p>')
_bg_pick = "".join(f'<label class="clash-opt"><input type="checkbox" value="{e(g["slug"])}"> <span>{e(g["title"])}</span> <span class="muted mono">{e(short_date(g) if g["date"] else g["window"])}</span></label>' for g in _bg)
_bg_tool = f'''<div class="tool" id="top-tool"><h2 style="font-size:1.5rem;margin-top:0">Make your 2027 top list and share it</h2>
<p class="muted">Tick the games you are most excited for, in order (your first tick is number 1, up to 10). You get a ready-to-paste list with dates and a link that opens your picks for friends.</p>
<div class="out" id="top-shared" hidden style="margin-bottom:14px"><div class="row hot"><span><strong>Someone shared their 2027 top list with you.</strong> Their picks are ticked below. Change them to make your own.</span></div></div>
<div class="clash-list" role="group" aria-label="Pick your top 2027 games">{_bg_pick}</div>
<div class="btns" style="display:flex;gap:10px;flex-wrap:wrap;margin:14px 0"><button class="btn sm" type="button" id="top-copy">Copy my list</button><button class="btn line sm" type="button" id="top-link">Copy share link</button><button class="btn line sm" type="button" id="top-star">Use my ★ list</button><button class="btn line sm" type="button" id="top-clear">Clear</button></div>
<div class="out" id="top-out" aria-live="polite"><div class="empty">Tick a game to start your list.</div></div></div>'''
bg_body = (f'<header class="hero"><div class="wrap"><span class="kicker">Biggest games</span>'
           f'<h1>The biggest games of 2027:<br><span class="amber">{len(_bg)} launches to plan for.</span></h1>'
           f'<p class="lead">The 2027 games from the biggest series and studios, in release order, with the date, the consoles and one line on why each one matters. Then make your own top list and share it.</p>'
           f'<p class="muted" style="margin:0">Last checked {e(UPDATED)} · dates confirmed by publishers or two trusted outlets · our picks, not a sales forecast</p></div></header>'
           f'<section><div class="wrap"><div class="out" style="margin-bottom:24px"><div class="row"><span><strong>Quick answer:</strong> {e(_bg_quick)}</span></div></div>'
           f'<div class="sec-head"><h2>When do the biggest games of 2027 come out?</h2><span class="muted">{len(_bg_dated)} dated · {len(_bg_open)} season or year only</span></div>{_bg_secs}{_bg_tga_html}</div></section>'
           + AD.format("big-mid") +
           f'<section><div class="wrap">{_bg_tool}</div></section>'
           f'<section><div class="wrap">'
           f'<div class="sec-head"><h2>Which of the biggest 2027 games can I play on my console?</h2></div><div class="out" style="margin-bottom:28px">'
           + "".join(f'<div class="row"><span><a href="{href("platforms/" + _bg_pslug[p] + ".html", 0)}">{e(_bg_plab[p])}</a><br><span class="muted">Missing: {e(", ".join(g["title"] for g in _bg if p not in g["platforms"]) or "none")}</span></span><b>{len(_bg_cnt[p])} of {len(_bg)}</b></div>' for p in sorted(PLATS, key=lambda q: -len(_bg_cnt[q]))) +
           f'</div><div class="sec-head"><h2>Which big 2027 games still have no release date?</h2><span class="muted">{len(_bg_open)}</span></div><div class="out" style="margin-bottom:28px">'
           + "".join(f'<div class="row"><span>{_gname(g)}</span><b>{e(g["window"])}</b></div>' for g in _bg_open) +
           f'</div><div class="sec-head"><h2>Which big 2027 games have been delayed?</h2><span class="muted">{len(_bg_delay)}</span></div><div class="out" style="margin-bottom:28px">'
           + ("".join(f'<div class="row"><span>{_gname(g)}</span><b>{e(nice_date(g))}</b></div>' for g in _bg_delay) or '<div class="empty">None so far.</div>') +
           f'</div><div class="sec-head"><h2>How did we pick the biggest games of 2027?</h2></div>'
           f'<p>We picked new games from major series and big studios, plus long-awaited remakes and sequels, that are confirmed for 2027. It is our editorial list, not sales or wishlist data. Every date and console comes from the publisher or at least two trusted gaming news sites, and we update the list when a game is dated or delayed. Smaller launches are on the <a href="{href("games.html", 0)}">full 2027 games list</a>.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>Related pages and tools</h2></div><ul>'
           f'<li><a href="{href("backlog-planner-2027.html", 0)}">2027 backlog planner</a>: can you finish one big game before the next?</li>'
           f'<li><a href="{href("release-clashes-2027.html", 0)}">2027 release clashes</a>: which big games land the same week</li>'
           f'<li><a href="{href("rpgs-2027.html", 0)}">Every RPG of 2027</a> and <a href="{href("exclusives-2027.html", 0)}">2027 console exclusives</a></li></ul></div></section>')
bg_faq = [
    ("What are the biggest games coming out in 2027?", "Our picks, in release order: " + ", ".join(f"{g['title']} ({nice_date(g)})" for g in _bg) + "."),
    ("What is the first big game of 2027?", f"{_bg_dated[0]['title']}, on {nice_date(_bg_dated[0])}." if _bg_dated else "None are dated yet."),
    ("Is GTA 6 a 2027 game?", "No. Rockstar launched GTA 6 on 19 November 2026 for PS5 and Xbox Series X|S, so it is not on our 2027 list. See our page on what to play after GTA 6."),
    ("Which big 2027 games are on Switch 2?", f"{len(_bg_cnt['Switch 2'])} of our picks: " + ", ".join(g["title"] for g in _bg_cnt["Switch 2"]) + "."),
    ("Which big 2027 games are PS5 exclusives?", "From our picks: " + (", ".join(g["title"] for g in _bg if g["platforms"] == ["PS5"] and g["slug"] != "forza-horizon-6") or "none") + ". Forza Horizon 6 on PS5 is a late port, not an exclusive."),
    ("When does Pokémon Winds and Waves come out?", "Sometime in 2027 on Switch 2. No month or exact date has been announced yet."),
    ("Which 2027 games are nominated for Most Anticipated Game at The Game Awards 2026?", "Fable, Final Fantasy VII Revelation, God of War Laufey and Resident Evil Veronica. The fifth nominee, The Witcher 4, is targeting 2028. The winner is named on 10 December 2026."),
    ("When does Resident Evil Veronica come out?", "Sometime in 2027 on PS5, Xbox Series X|S, PC and Switch 2. Capcom has not announced a month or date yet."),
]
page("biggest-games-2027.html", f"The Biggest Games of 2027: Dates and Consoles ({len(_bg)} Games) | DayOneDrop"[:90],
     f"The {len(_bg)} biggest games of 2027 in release order: Fable, Final Fantasy VII Revelation, God of War Laufey, Resident Evil Veronica and more. Share your top list."[:160],
     bg_body, 0, bg_faq, crumbs=[("Home", DOMAIN + "/"), ("All games", canon("games.html")), ("Biggest games of 2027", canon("biggest-games-2027.html"))],
     extra_ld={"@context": "https://schema.org", "@type": "ItemList", "name": "The biggest games of 2027",
               "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": g["title"] + " (" + nice_date(g) + ")"} for i, g in enumerate(_bg)]})

# ---------------- THE GAME AWARDS 2026 PAGE (24 Nov 2026) ----------------
_tga_d = datetime.date.fromisoformat(TGA_DATE)
_tga_g = [_gbs[x] for x in TGA_ANTICIPATED if x in _gbs]
_tga_dated = sorted([g for g in _tga_g if g["date"]], key=lambda g: g["date"])
def _tga_after(g):
    return (datetime.date.fromisoformat(g["date"]) - _tga_d).days
_tga_first = _tga_dated[0] if _tga_dated else None
_tga_rows = "".join(
    f'<div class="row"><span><strong>{_gname(g)}</strong><br><span class="muted">{e(g["dev"] or "")} · {e(", ".join(g["platforms"]))}</span>'
    + (f'<br><span class="muted">Out {_tga_after(g)} days after the show</span>' if g["date"] else '<br><span class="muted">No month or day announced yet</span>')
    + f'</span><b>{e(nice_date(g))}</b></div>' for g in sorted(_tga_g, key=lambda g: g["date"] or "9999"))
_w4 = TGA_EXTRA["the-witcher-4"]
_tga_rows += f'<div class="row"><span><strong>The Witcher 4</strong><br><span class="muted">{e(_w4["dev"])} · {e(_w4["note"])}</span></span><b>{e(_w4["when"])}</b></div>'
_tga_names = [g["title"] for g in _tga_g]
_tga_quick = (f"The Game Awards 2026 starts at 7:30pm ET / 4:30pm PT on Thursday 10 December 2026 (12:30am UK time on Friday 11 December), live from the Peacock Theater in Los Angeles. "
              f"It streams free on YouTube and Twitch and, for the first time, on Disney+. "
              f"Four of the five Most Anticipated Game nominees are 2027 games: "
              + ", ".join(f"{g['title']} ({nice_date(g) if g['date'] else 'no date yet'})" for g in sorted(_tga_g, key=lambda g: g["date"] or "9999"))
              + ". The fifth, The Witcher 4, is targeting 2028. Grand Theft Auto 6 leads the nominations with 8, and fan voting closes on " + TGA_VOTE_END + ".")
_tga_plat = {p: [g["title"] for g in _tga_g if p in g["platforms"]] for p in PLATS}
_tga_opts_a = "".join(f'<label class="clash-opt"><input type="radio" name="tga-a" value="{e(n)}"> <span>{e(n)}</span></label>' for n in _tga_names + ["The Witcher 4"])
_tga_opts_g = "".join(f'<label class="clash-opt"><input type="radio" name="tga-g" value="{e(n)}"> <span>{e(n)}</span></label>' for n in TGA_GOTY)
_tga_tool = f'''<div class="tool" id="tga-tool"><h2 style="font-size:1.5rem;margin-top:0">Who do you think will win?</h2>
<p class="muted">Pick your winner in two categories. We save your picks on this device so you can check them on the night, and you can copy them or send a link to friends.</p>
<div class="out" id="tga-shared" hidden style="margin-bottom:14px"><div class="row hot"><span><strong>A friend shared their picks with you.</strong> They are ticked below. Change them to make your own.</span></div></div>
<div class="grid" style="grid-template-columns:repeat(auto-fit,minmax(min(260px,100%),1fr));gap:16px">
<div role="radiogroup" aria-label="Most Anticipated Game pick"><label>Most Anticipated Game</label>{_tga_opts_a}</div>
<div role="radiogroup" aria-label="Game of the Year pick"><label>Game of the Year</label>{_tga_opts_g}</div></div>
<div class="btns" style="display:flex;gap:10px;flex-wrap:wrap;margin:14px 0"><button class="btn sm" type="button" id="tga-copy">Copy my picks</button><button class="btn line sm" type="button" id="tga-link">Copy share link</button><button class="btn line sm" type="button" id="tga-clear">Clear</button></div>
<div class="out" id="tga-out" aria-live="polite"><div class="empty">Pick a game in each category.</div></div></div>'''
import re as _re
def _tga_key(n):
    m = _re.search(r"\(([^)]+)\)$", n)
    return m.group(1) if m and not n.startswith("Fallout") else n
_tga_count = collections.Counter(_tga_key(n) for _, ns in TGA_CATS for n in ns)
_tga_cats_of = collections.defaultdict(list)
for _c, _ns in TGA_CATS:
    for _n in _ns: _tga_cats_of[_tga_key(_n)].append(_c)
_tga_top = sorted(_tga_count.items(), key=lambda x: (-x[1], x[0]))
_tga_top = [x for x in _tga_top if x[1] >= 4]
_tga_2027 = {_gbs[k]["title"]: _gbs[k] for k in _gbs}
_tga_on_board = [(n, _tga_2027[n]) for n in _tga_count if n in _tga_2027]
_tga_top_rows = "".join(f'<div class="row"><span><strong>{e(n)}</strong><br><span class="muted">{e(", ".join(_tga_cats_of[n]))}</span></span><b>{c}</b></div>' for n, c in _tga_top)
_tga_all = "".join(
    f'<div class="tga-cat" data-names="{e(" | ".join(ns).lower())}"><h3 style="font-size:1.05rem;margin:18px 0 6px">{e(c)}</h3><div class="out">'
    + "".join(f'<div class="row" data-n="{e(n.lower())}"><span>{e(n)}</span><b>{_tga_count[_tga_key(n)]} nom{"s" if _tga_count[_tga_key(n)] != 1 else ""}</b></div>' for n in ns)
    + '</div></div>' for c, ns in TGA_CATS)
_tga_find = (f'<div class="tool" id="tga-find"><h2 style="font-size:1.5rem;margin-top:0">What is my favourite game nominated for?</h2>'
    f'<p class="muted">Type a game, actor or show. We show every category it is up for and hide the rest.</p>'
    f'<label for="tga-q">Search the nominees</label><input id="tga-q" type="search" placeholder="e.g. Forza, Big Walk, Wolverine" autocomplete="off" style="width:100%;max-width:420px">'
    f'<p class="muted" id="tga-find-out" aria-live="polite" style="margin:10px 0 0">{len(TGA_CATS)} categories · {sum(len(ns) for _, ns in TGA_CATS)} nominations</p>'
    f'<div id="tga-cats">{_tga_all}</div></div>')
tga_body = (f'<header class="hero"><div class="wrap"><span class="kicker">The Game Awards 2026</span>'
    f'<h1>The Game Awards 2026:<br><span class="amber">the 2027 games up for Most Anticipated.</span></h1>'
    f'<p class="lead">When the show is, how to watch it, and when every Most Anticipated Game nominee actually comes out. Then pick your winners and share them.</p>'
    f'<p class="muted" style="margin:0">Last checked {e(UPDATED)} · nominees from the official list announced 17 November 2026</p>'
    f'<div class="cdw" style="margin-top:18px;max-width:520px"><span class="lbl">Countdown to the show (7:30pm ET, 10 Dec 2026)</span><div class="cd" data-countdown-at="{TGA_START_UTC}">'
    f'<div class="cd-unit"><span class="flaps" data-u="0"></span><span>Days</span></div><div class="cd-unit"><span class="flaps" data-u="1"></span><span>Hrs</span></div>'
    f'<div class="cd-unit"><span class="flaps" data-u="2"></span><span>Min</span></div><div class="cd-unit"><span class="flaps" data-u="3"></span><span>Sec</span></div></div></div></div></header>'
    f'<section><div class="wrap"><div class="out" style="margin-bottom:24px"><div class="row"><span><strong>Quick answer:</strong> {e(_tga_quick)}</span></div></div>'
    f'<div class="sec-head"><h2>When is The Game Awards 2026 and how can I watch it?</h2></div><div class="out" style="margin-bottom:28px">'
    f'<div class="row"><span>Date</span><b>Thu 10 Dec 2026</b></div>'
    f'<div class="row"><span>Venue</span><b>Peacock Theater, Los Angeles</b></div>'
    f'<div class="row"><span>Start time</span><b>7:30pm ET / 4:30pm PT</b></div>'
    f'<div class="row"><span>UK start time</span><b>12:30am Fri 11 Dec</b></div>'
    f'<div class="row"><span>Free streams</span><b>YouTube, Twitch</b></div>'
    f'<div class="row"><span>Disney+<br><span class="muted">New this year. For Disney+ subscribers, in North America and some other countries.</span></span><b>Live</b></div>'
    f'<div class="row"><span>Roblox<br><span class="muted">Reported by Shacknews from the show\'s own post. 18 and over only.</span></span><b>Live</b></div>'
    f'<div class="row"><span>Nominees announced</span><b>17 Nov 2026</b></div>'
    f'<div class="row"><span>Fan voting closes<br><span class="muted">Vote in every category at thegameawards.com</span></span><b>9 Dec, 6pm PT</b></div></div>'
    f'<div class="tool" id="tga-tz" style="margin-bottom:28px"><h2 style="font-size:1.5rem;margin-top:0">What time is The Game Awards 2026 in my time zone?</h2>'
    f'<p class="muted">The show starts at 7:30pm ET on Thursday 10 December. Your device\'s clock converts it for you below, and the table covers the main time zones.</p>'
    f'<div class="out" id="tga-tz-out" aria-live="polite" style="margin-bottom:14px"><div class="row hot" style="flex-wrap:wrap;gap:6px"><span>Start time where you are</span><b style="white-space:normal;min-width:0" data-tga-local="{TGA_START_UTC}">7:30pm ET</b></div></div>'
    f'<div class="out">' + "".join(f'<div class="row"><span>{e(z)}</span><b>{e(t)}</b></div>' for z, t in TGA_ZONES) + '</div>'
    f'<div class="btns" style="margin-top:12px;display:flex;gap:8px;flex-wrap:wrap"><a class="btn sm" rel="noopener" target="_blank" href="https://calendar.google.com/calendar/render?action=TEMPLATE&amp;text=The%20Game%20Awards%202026&amp;dates=20261211T003000Z/20261211T040000Z&amp;details=Live%20on%20YouTube%2C%20Twitch%20and%20Disney%2B.%20Nominees%3A%20https%3A%2F%2Fgetdayonedrop.com%2Fgame-awards-2026&amp;location=Peacock%20Theater%2C%20Los%20Angeles">Add to Google Calendar</a></div>'
    f'<p class="muted" style="margin:10px 0 0">The calendar entry is 3.5 hours long as a placeholder. The show has not said how long it runs.</p></div>'
    f'<div class="sec-head"><h2>Do I need Disney+ to watch The Game Awards 2026?</h2></div>'
    f'<p style="margin-bottom:28px">No. Disney+ is an extra way to watch this year, not the only one. The show still streams free on YouTube and Twitch. Watching on Disney+ needs a Disney+ subscription, and Disney says it is available in North America and selected other markets. Disney also says to expect "major announcements and surprises" from its own upcoming games, but it has not named them.</p>'
    f'<div class="sec-head"><h2>Which game has the most nominations at The Game Awards 2026?</h2><span class="muted">4 or more</span></div>'
    f'<div class="out" style="margin-bottom:12px">{_tga_top_rows}</div>'
    f'<p class="muted" style="margin-bottom:28px">Grand Theft Auto 6 leads with 8. Control Resonant and Resident Evil Requiem have 6 each, and Phantom Blade Zero has 5. Acting nominations count for the actor\'s game. Esports and creator awards are not counted.</p>'
    f'<div class="sec-head"><h2>Which games are nominated for Most Anticipated Game?</h2><span class="muted">5 nominees · 4 in 2027</span></div>'
    f'<div class="out" style="margin-bottom:28px">{_tga_rows}</div>'
    f'<div class="sec-head"><h2>Which Most Anticipated nominee comes out first?</h2></div>'
    + (f'<p>{_gname(_tga_first)} on {e(nice_date(_tga_first))}, just {_tga_after(_tga_first)} days after the show. ' if _tga_first else '<p>')
    + f'Resident Evil Veronica has no month yet, so it could land anywhere in 2027. Add the dated ones to your calendar from each game\'s page.</p>'
    f'<div class="sec-head" style="margin-top:22px"><h2>Is The Witcher 4 coming out in 2027?</h2></div>'
    f'<p>No. CD Projekt said in August 2026 that it is targeting 2028 for The Witcher 4, so it is the only Most Anticipated nominee that is not a 2027 game. It is not on our 2027 board. If that changes, we will add it.</p></div></section>'
    + AD.format("tga-mid") +
    f'<section><div class="wrap">{_tga_tool}</div></section>'
    f'<section><div class="wrap">'
    f'<div class="sec-head"><h2>Which games are nominated for Game of the Year?</h2><span class="muted">{len(TGA_GOTY)}</span></div><div class="out" style="margin-bottom:12px">'
    + "".join(f'<div class="row"><span>{e(n)}</span><b>Nominee</b></div>' for n in TGA_GOTY) +
    f'</div><p class="muted" style="margin-bottom:28px">Game of the Year is for games released in 2026. Only 007 First Light has a 2027 date on our board: its delayed <a href="{href("games/007-first-light.html", 0)}">Switch 2 version</a>.</p>'
    f'{_tga_find}'
    f'<div class="sec-head" style="margin-top:28px"><h2>How do I vote at The Game Awards 2026?</h2></div>'
    f'<p style="margin-bottom:28px">Fans can vote in every category on the official site, thegameawards.com, until {e(TGA_VOTE_END)}. The fan vote counts for 10% of the result. The other 90% comes from a jury of more than 160 media and creator outlets.</p>'
    f'<div class="sec-head"><h2>Which Most Anticipated nominees can I play on my console?</h2></div><div class="out" style="margin-bottom:28px">'
    + "".join(f'<div class="row"><span><a href="{href("platforms/" + _bg_pslug[p] + ".html", 0)}">{e(_bg_plab[p])}</a><br><span class="muted">{e(", ".join(_tga_plat[p]) or "None of them")}</span></span><b>{len(_tga_plat[p])} of {len(_tga_g)}</b></div>' for p in sorted(PLATS, key=lambda q: -len(_tga_plat[q]))) +
    f'</div><div class="sec-head"><h2>Will 2027 games get new release dates at the show?</h2></div>'
    f'<p>The Game Awards is known for world premieres and release date news, but the show has not said which games will appear. Disney has promised announcements from its own games without naming them; some fans hope that means <a href="{href("games/kingdom-hearts-iv.html", 0)}">Kingdom Hearts 4</a> (due late 2027), but nobody has confirmed it. Many 2027 games still have only a season or a year, including '
    + ", ".join(_gname(g) for g in [x for x in GAMES if not x["date"] and x["slug"] in BIG_WHY_SLUGS][:5]) +
    f'. If any of them get a date on the night, we update the <a href="{href("index.html", 0)}">departures board</a> and the <a href="{href("calendar.html", 0)}">2027 calendar</a>.</p>'
    f'<div class="sec-head" style="margin-top:28px"><h2>Related pages and tools</h2></div><ul>'
    f'<li><a href="{href("biggest-games-2027.html", 0)}">The biggest games of 2027</a>, with a shareable top list maker</li>'
    f'<li><a href="{href("games/resident-evil-veronica.html", 0)}">Resident Evil Veronica</a> release date and remake details</li>'
    f'<li><a href="{href("release-clashes-2027.html", 0)}">2027 release clashes</a>: which nominees share a launch week with other games</li>'
    f'<li><a href="{href("games/forza-horizon-6.html", 0)}">Forza Horizon 6 on PS5</a>: a nominee with a 2027 release</li>'
    f'<li><a href="{href("fighting-games-2027.html", 0)}">Fighting games of 2027</a>: what comes after this year\'s Best Fighting Game nominees</li></ul></div></section>')
tga_faq = [
    ("When is The Game Awards 2026?", "Thursday 10 December 2026, live from the Peacock Theater in Los Angeles."),
    ("How can I watch The Game Awards 2026?", "It streams free on YouTube and Twitch, and for the first time on Disney+ (for subscribers, in North America and selected other markets). Shacknews also reports a Roblox stream for players 18 and over."),
    ("What time does The Game Awards 2026 start?", "7:30pm ET / 4:30pm PT on Thursday 10 December 2026. That is 12:30am UK time, 5:30am in Pakistan, 6am in India and 11:30am in Sydney on Friday 11 December."),
    ("What time is The Game Awards 2026 in the UK?", "12:30am GMT on Friday 11 December 2026 (7:30pm ET on 10 December)."),
    ("Is The Game Awards 2026 on Disney+?", "Yes, live, for the first time. You need a Disney+ subscription to watch there. It is still free on YouTube and Twitch."),
    ("What are the Most Anticipated Game nominees at The Game Awards 2026?", "Fable, Final Fantasy VII Revelation, God of War Laufey, Resident Evil Veronica and The Witcher 4."),
    ("When do the Most Anticipated nominees come out?", "; ".join(f"{g['title']}: {nice_date(g)}" for g in sorted(_tga_g, key=lambda g: g["date"] or "9999")) + "; The Witcher 4: targeting 2028."),
    ("What are the Game of the Year nominees for 2026?", ", ".join(TGA_GOTY[:-1]) + " and " + TGA_GOTY[-1] + "."),
    ("Which game has the most nominations at The Game Awards 2026?", "Grand Theft Auto 6, with 8. Control Resonant and Resident Evil Requiem have 6 each, and Phantom Blade Zero has 5."),
    ("How do I vote for The Game Awards 2026?", "Vote in every category on thegameawards.com until " + TGA_VOTE_END + ". Fans decide 10% of the result and a jury of more than 160 outlets decides 90%."),
    ("Is Forza Horizon 6 nominated at The Game Awards 2026?", "Yes, twice: Best Sports / Racing Game and Innovation in Accessibility. Its PS5 version comes out on " + nice_date(_gbs["forza-horizon-6"]) + "."),
]
page("game-awards-2026.html", "The Game Awards 2026 Start Time, Disney+ Stream and Nominees",
     "The Game Awards 2026 starts 7:30pm ET / 4:30pm PT on 10 Dec (12:30am UK). Your local time, Disney+, YouTube and Twitch, and every nominee (GTA 6 leads with 8).",
     tga_body, 0, tga_faq, crumbs=[("Home", DOMAIN + "/"), ("Biggest games of 2027", canon("biggest-games-2027.html")), ("The Game Awards 2026", canon("game-awards-2026.html"))])

# ---------------- ABOUT / PRIVACY / 404 ----------------
_ab_n = len(GAMES); _ab_d = sum(1 for g in GAMES if g["date"]); _ab_del = sum(1 for g in GAMES if g["status"] == "delayed")
page("about.html", "About DayOneDrop: How We Track 2027 Release Dates | DayOneDrop",
     f"DayOneDrop is an independent tracker of {_ab_n} games coming in 2027. How we check every release date, how fast we update delays, our sources and how to report a mistake.",
     f'''<section><div class="wrap" style="max-width:760px"><h1>About <span class="amber">DayOneDrop</span></h1>
<p>DayOneDrop is an independent website that tracks release dates for the games coming out in 2027. Right now we follow <strong>{_ab_n} games</strong>: {_ab_d} with an exact date, the rest with a season or year, and {_ab_del} that have already been delayed. Every game has its own page with the date, platforms, developer, a live countdown and its full date history.</p>
<h2>Who runs DayOneDrop</h2><p>DayOneDrop is a small independent publisher that also runs the GTA 6 guide <a href="https://neoncoast.org/" rel="noopener">NeonCoast</a>. We are not owned by, paid by or linked to any game publisher, platform holder or store.</p>
<h2 id="editorial">How we check every date (editorial policy)</h2>
<ul>
<li><strong>Two-source rule.</strong> A date goes on the site only when the publisher or developer announces it, or at least two trusted gaming news outlets report it.</li>
<li><strong>Official sources first.</strong> We check publisher announcements, the PlayStation Blog, Xbox Wire, Nintendo Directs, Steam pages and official social accounts. News outlets we use include IGN, GameSpot, Gematsu, Game Informer, Push Square and Eurogamer.</li>
<li><strong>No rumours as facts.</strong> Leaks and retailer listings are never shown as release dates. A game with only a year or season is marked as a window, not given a made-up day.</li>
<li><strong>Delays kept, not hidden.</strong> When a game slips we keep the old date in its history, with when and why it moved, so you can see how reliable each date has been.</li>
<li><strong>Checked daily.</strong> We re-check the list every day and after every big showcase. Each page shows when it was last checked.</li>
</ul>
<h2>Corrections</h2><p>If a date is wrong or out of date, email <a href="mailto:awaiskaramat@hotmail.com">awaiskaramat@hotmail.com</a> with a link to the announcement. We fix confirmed mistakes the same day and note the change in the game's history.</p>
<h2>How the site is funded</h2><p>DayOneDrop is free. Some pages may show ads, and some store buttons may be affiliate links, which can earn us a small fee at no cost to you. Ads and links never change a date, a ranking or what we say about a game. See our <a href="{href("privacy.html", 0)}">privacy policy</a>.</p>
<h2>Useful pages</h2><ul><li><a href="{href("games.html", 0)}">All 2027 games, month by month</a></li><li><a href="{href("calendar.html", 0)}">2027 release calendar</a></li><li><a href="{href("delayed-games-2027.html", 0)}">Every delayed 2027 game</a></li><li><a href="{href("new-games-this-week.html", 0)}">New games this week</a></li></ul>
<p class="muted">Game names and artwork belong to their owners. Last checked {UPDATED}.</p></div></section>''')
page("privacy.html", "Privacy Policy | DayOneDrop", "DayOneDrop privacy policy covering cookies, Google AdSense, Google Analytics and affiliate links.",
     f'''<section><div class="wrap" style="max-width:760px"><h1>Privacy policy</h1><p>Last updated: {e(UPDATED)}.</p>
<h2>What we collect</h2><p>Your launch list is saved only in your own browser. If you join our email list, we keep your email address with our email provider, Kit (kit.com), to send you the calendar and our updates. Every email has an unsubscribe link, and you can ask us to delete your address at any time.</p>
<h2>Analytics</h2><p>We use Google Analytics to count visits and see which pages are popular. It uses cookies and collects information like pages viewed, approximate location and device type.</p>
<h2>Advertising</h2><p>This site uses Google AdSense. Google and its partners use cookies to show ads based on your visits to this and other websites. You can turn off personalised ads at <a href="https://adssettings.google.com">Google Ads Settings</a>. Learn more at <a href="https://policies.google.com/technologies/partner-sites">policies.google.com/technologies/partner-sites</a>.</p>
<h2>Affiliate links</h2><p>Some links may be affiliate links. If you buy through them, we may earn a small fee at no extra cost to you. As an Amazon Associate we earn from qualifying purchases.</p>
<h2>Contact</h2><p>Email <a href="mailto:awaiskaramat@hotmail.com">awaiskaramat@hotmail.com</a>.</p></div></section>''')
page("404.html", "Page not found | DayOneDrop", "This page has moved or doesn't exist.",
     f'<section><div class="wrap"><h1>Flight <span class="amber">cancelled.</span></h1><p class="lead">This page doesn\'t exist. Head back to the departures board.</p><a class="btn" href="{href("index.html", 0)}">Go to the board</a></div></section>')



# ---------------- XBOX GAMES SHOWCASE 2027 (25 Nov 2026) ----------------
# Past show dates: Xbox Wire (2025, 2026), VGC, Gematsu, Windows Central, GamingBolt, Pure Xbox. 2023/2024 well reported (Xbox Wire recaps).
# 2027 show NOT announced as of the check date: the "likely" window is our estimate from the pattern, labelled as such.
XS_PAST = [("2026", "2026-06-07", "Gears of War: E-Day Direct"), ("2025", "2025-06-08", "The Outer Worlds 2 Direct"),
           ("2024", "2024-06-09", "Call of Duty: Black Ops 6 Direct"), ("2023", "2023-06-11", "Starfield Direct")]
XS_DEVDIRECT = [("2026", "2026-01-22"), ("2025", "2025-01-23")]
_WD = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
def _xs_day(d):
    x = datetime.date.fromisoformat(d)
    return f"{_WD[x.weekday()]} {x.day} {x.strftime('%B')} {x.year}"
_xs_sun = [datetime.date(2027, 6, d) for d in range(1, 15) if datetime.date(2027, 6, d).weekday() == 6]
_xs_sun_txt = " or ".join(f"Sunday {d.day} June 2027" for d in _xs_sun)
_xb = sorted([g for g in GAMES if "Xbox Series X|S" in g["platforms"]], key=lambda x: (x["month"], x["date"] or "9999"))
_xb_und = [g for g in _xb if not g["date"]]
_xb_dated = [g for g in _xb if g["date"]]
_xb_pre = [g for g in _xb_dated if g["date"] < "2027-06-06"]
_xb_pre_big = [g for g in _xb_pre if g["page"] or g["slug"] in GP_TRACKED_ALL]
_xb_gp = [g for g in _xb if g["slug"] in GP_TRACKED_ALL]
_xb_only = [g for g in _xb if g["platforms"] == ["Xbox Series X|S"] or set(g["platforms"]) <= {"Xbox Series X|S", "PC"}]
_xb_big_und = [g for g in _xb_und if g["page"]]
_xs_quick = (f"Microsoft has not announced the Xbox Games Showcase 2027 yet. The last four showcases (2023 to 2026) all aired on a Sunday in early June, between 7 and 11 June, "
             f"so {_xs_sun_txt} is the likely slot. That is our estimate, not a confirmed date. "
             f"{len(_xb_und)} of the {len(_xb)} Xbox games we track for 2027 still have no exact date.")
def _xsrow(g):
    gp = g["slug"] in GP_TRACKED_ALL
    tags = []
    if gp: tags.append("Game Pass day one" if g["slug"] in GP_DAY_ONE else "Announced for Game Pass")
    if "PS5" in g["platforms"]: tags.append("also on PS5")
    return (f'<div class="row" data-xsd="{1 if g["date"] else 0}" data-xsgp="{1 if gp else 0}" data-slug="{e(g["slug"])}"><span><strong>{_gname(g)}</strong>'
            f'<br><span class="muted">{e(g.get("genre") or "")} · {e(g.get("dev") or "Studio TBC")}' + (f' · {e(", ".join(tags))}' if tags else "") + f'</span></span><b>{e(nice_date(g))}</b></div>')
_xs_tbl = ('<div style="overflow-x:auto"><table class="gen-table" style="width:100%;border-collapse:collapse;font-size:.92rem"><thead><tr>'
           '<th style="text-align:left;padding:6px">Year</th><th style="text-align:left;padding:6px">Showcase date</th><th style="text-align:left;padding:6px">Followed by</th></tr></thead><tbody>'
           + "".join(f'<tr><td style="padding:6px;border-top:1px solid var(--rule)" class="mono">{y}</td><td style="padding:6px;border-top:1px solid var(--rule)">{e(_xs_day(d))}</td>'
                     f'<td style="padding:6px;border-top:1px solid var(--rule)">{e(dr)}</td></tr>' for y, d, dr in XS_PAST)
           + f'<tr><td style="padding:6px;border-top:1px solid var(--rule)" class="mono">2027</td><td style="padding:6px;border-top:1px solid var(--rule)">Not announced (likely early June)</td><td style="padding:6px;border-top:1px solid var(--rule)">Not announced</td></tr>'
           + '</tbody></table></div>')
_xs_chips = ('<div class="chips" role="group" aria-label="Date"><button class="chip" type="button" data-xs-d="0" aria-pressed="true">No exact date yet</button>'
             '<button class="chip" type="button" data-xs-d="1" aria-pressed="false">Already dated</button><button class="chip" type="button" data-xs-d="" aria-pressed="false">All</button></div>'
             '<div class="chips" role="group" aria-label="Game Pass" style="margin-top:10px"><button class="chip" type="button" data-xs-gp="" aria-pressed="true">Any</button>'
             '<button class="chip" type="button" data-xs-gp="1" aria-pressed="false">Game Pass only</button></div>')
xs_body = (f'<header class="hero"><div class="wrap"><span class="kicker">Xbox</span>'
           f'<h1>Xbox Games Showcase 2027:<br><span class="amber">when is it, and what still needs a date?</span></h1>'
           f'<p class="lead">The likely date of the June 2027 Xbox show, every past showcase date, and the Xbox games due in 2027 that are still waiting for a release date.</p>'
           f'<p class="muted" style="margin:0">Last checked {e(UPDATED)} · we update this page when Microsoft announces the show</p></div></header>'
           f'<section><div class="wrap"><div class="out" style="margin-bottom:24px"><div class="row"><span><strong>Quick answer:</strong> {e(_xs_quick)}</span></div></div>'
           f'<div class="tool" id="xs-tool"><h2 style="font-size:1.5rem;margin-top:0">Which 2027 Xbox games could get a date at the showcase?</h2>'
           f'<p class="muted">Games announced for Xbox Series X|S in 2027 without an exact day are the ones most likely to get one. Tap to switch the list, then save the games you care about to your ★ list. Your choice is remembered on this device.</p>{_xs_chips}'
           f'<p class="mono amber" id="xs-count" aria-live="polite" style="margin:12px 0 0">{len(_xb_und)} games</p>'
           f'<div class="out" id="xs-list" style="margin-top:12px">{"".join(_xsrow(g) for g in _xb)}</div><p class="empty" id="xs-none" hidden>No tracked Xbox games match that yet.</p>'
           f'<div class="btns" style="margin-top:10px;display:flex;gap:8px;flex-wrap:wrap"><button class="btn sm" type="button" id="xs-add">Add these to my ★ list</button>'
           f'<a class="btn line sm" href="{href("platforms/xbox-series.html", 0)}">All Xbox release dates</a></div></div></div></section>'
           + AD.format("xs-mid") +
           f'<section><div class="wrap"><div class="sec-head"><h2>When is the Xbox Games Showcase 2027?</h2></div>'
           f'<p>Not announced yet. Microsoft usually confirms the date in late March or early April: the 2026 show was announced on 30 March 2026 for 7 June. '
           f'Going by the last four years, the 2027 show will most likely air on {e(_xs_sun_txt)}. Treat any exact date you see before Microsoft posts it on Xbox Wire as a guess.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>When were the past Xbox Games Showcases?</h2></div>{_xs_tbl}'
           f'<p class="muted" style="margin-top:10px">Every show since 2023 aired on a Sunday, with a deep-dive Direct on one big game straight after. Sources: Xbox Wire, VGC, Gematsu, Windows Central.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>Will there be an Xbox Developer Direct in January 2027?</h2></div>'
           f'<p>Not announced yet. Xbox held a Developer Direct in late January in both 2025 ({e(_xs_day("2025-01-23"))}) and 2026 ({e(_xs_day("2026-01-22"))}), and announced the 2026 one in December 2025. If the pattern holds, expect news in December 2026, but nothing is confirmed.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>Which big Xbox games already have a date before June 2027?</h2><span class="muted">{len(_xb_pre_big)} of {len(_xb_pre)}</span></div>'
           f'<p class="muted">These launch before the likely showcase weekend, so they will already be out (or nearly out) when the show airs.</p>'
           f'<div class="out" style="margin-bottom:10px">' + "".join(_xsrow(g) for g in _xb_pre_big) + '</div>'
           f'<p class="muted">Showing the big ones and Game Pass games. See <a href="{href("platforms/xbox-series.html", 0)}">every Xbox Series X|S game of 2027</a> for all {len(_xb_dated)} dated games.</p>'
           + (f'<div class="sec-head" style="margin-top:28px"><h2>Which big 2027 Xbox games still have no release date?</h2><span class="muted">{len(_xb_big_und)}</span></div>'
              f'<div class="out" style="margin-bottom:10px">' + "".join(_xsrow(g) for g in _xb_big_und) + '</div>' if _xb_big_und else "")
           + f'<div class="sec-head" style="margin-top:28px"><h2>Which Game Pass games are due in 2027?</h2><span class="muted">{len(_xb_gp)} tracked</span></div>'
           f'<div class="out" style="margin-bottom:10px">' + "".join(_xsrow(g) for g in _xb_gp) + '</div>'
           f'<p class="muted">Also announced for Game Pass with only a window: {e(", ".join(f"{t} ({w})" for t, w in GP_OTHER))}. Full list on the <a href="{href("game-pass-2027.html", 0)}">Game Pass 2027 page</a>.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>Are Xbox games still coming to PS5 in 2027?</h2></div>'
           f'<p>Yes. Of the {len(_xb)} Xbox games we track for 2027, {sum(1 for g in _xb if "PS5" in g["platforms"])} are also announced for PS5, including Fable and State of Decay 3. '
           f'Only {len(_xb_only)} are on Xbox and PC only. See <a href="{href("exclusives-2027.html", 0)}">2027 console exclusives</a> for the full split.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>Related pages and tools</h2></div><ul>'
           f'<li><a href="{href("game-pass-2027.html", 0)}">Every Xbox Game Pass game of 2027</a>, with the next one to launch</li>'
           f'<li><a href="{href("platforms/xbox-series.html", 0)}">Xbox Series X|S release dates 2027</a>, month by month</li>'
           f'<li><a href="{href("release-clashes-2027.html", 0)}">2027 release clashes</a>: check your ★ list for games that land the same week</li>'
           f'<li><a href="{href("game-awards-2026.html", 0)}">The Game Awards 2026</a>: the next big show where 2027 dates could appear</li></ul></div></section>')
xs_faq = [
    ("When is the Xbox Games Showcase 2027?", f"Microsoft has not announced it. The 2023 to 2026 shows all aired on a Sunday between 7 and 11 June, so {_xs_sun_txt} is likely, but that is an estimate."),
    ("When was the Xbox Games Showcase 2026?", "Sunday 7 June 2026, followed by the Gears of War: E-Day Direct. Microsoft announced the date on 30 March 2026."),
    ("When does Microsoft announce the Xbox Games Showcase date?", "Usually in spring. The 2026 date was announced on 30 March 2026, about ten weeks before the show."),
    ("Will there be an Xbox Developer Direct in January 2027?", "Not announced. Xbox held one on 23 January 2025 and 22 January 2026."),
    ("Which 2027 Xbox games have no release date yet?", (", ".join(f"{g['title']} ({nice_date(g)})" for g in _xb_und) + ".") if _xb_und else "Every tracked Xbox game has a date."),
    ("Which 2027 Xbox games are on Game Pass?", ", ".join(f"{g['title']} ({nice_date(g)})" for g in _xb_gp) + "."),
]
page("xbox-games-showcase-2027.html", "Xbox Games Showcase 2027: Likely Date, Past Shows and Games Without a Date | DayOneDrop",
     f"When is the Xbox Games Showcase 2027? Not announced yet: likely early June. Every past show date, plus the {len(_xb_und)} Xbox 2027 games still without a date. Checked {UPDATED}."[:160],
     xs_body, 0, xs_faq, crumbs=[("Home", DOMAIN + "/"), ("Xbox Series X|S games", canon("platforms/xbox-series.html")), ("Xbox Games Showcase 2027", canon("xbox-games-showcase-2027.html"))])

# ---------------- PS PLUS MONTHLY GAMES (Keyword Planner worldwide 25 Nov 2026: "ps plus monthly games" 100k-1M, +900% 3-month, low comp) ----------------
PSP = [  # month, games (title, platforms), claim window. Sources: PlayStation Blog via Worthplaying 28 Oct 2026, Exputer, Tech Insider.
    ("December 2026", [("Tony Hawk's Pro Skater 3+4", "PS5, PS4"), ("Dragon Ball Xenoverse 2", "PS5, PS4"), ("Amnesia: The Bunker", "PS4 / PS5")], "1 December 2026 to 4 January 2027"),
    ("November 2026", [("Dead Island 2", "PS5, PS4"), ("Tomb Raider IV–VI Remastered", "PS5, PS4"), ("Monster Train 2", "PS5")], "3 to 30 November 2026"),
    ("October 2026", [("F1 25", "PS5"), ("Hunt: Showdown 1896", "PS5"), ("Earth Defense Force: World Brothers 2", "PS5, PS4")], "October to 2 November 2026"),
]
_psp_rows = "".join(f"<tr><td>{m}</td><td>{', '.join(f'{e(t)} <span class=muted>({pl})</span>' for t, pl in g) if g else '<strong>Revealed on Wednesday 25 November</strong> (usually about 4:30 pm UK, 9:30 pm PKT, 11:30 am ET)'}</td><td>{w}</td></tr>" for m, g, w in PSP)
psp_body = (f'<header class="hero"><div class="wrap"><span class="kicker">PlayStation Plus</span><h1>PS Plus December 2026:<br><span class="amber">Tony Hawk 3+4, Xenoverse 2, Amnesia.</span></h1>'
    f'<p class="lead">The free games every PS Plus member can claim each month, when the next ones are revealed, and how long you have to add them to your library.</p></div></header>'
    f'<section style="padding-top:10px"><div class="wrap"><div class="tool"><p><strong>Quick answer:</strong> December 2026\'s PS Plus monthly games are <strong>Tony Hawk\'s Pro Skater 3+4, Dragon Ball Xenoverse 2 and Amnesia: The Bunker</strong>, claimable from <strong>Tuesday 1 December 2026 to Monday 4 January 2027</strong>. PS Plus Extra also adds Dynasty Warriors: Origins in December. November\'s games, <strong>Dead Island 2, Tomb Raider IV–VI Remastered and Monster Train 2</strong>, can be added until <strong>Monday 30 November</strong>. Sony usually reveals the monthly games on the last Wednesday of the month and releases them on the first Tuesday of the next.</p>'
    f'<p id="psp-cd" class="muted" aria-live="polite"></p></div></div></section>'
    f'<script>(function(){{var t=Date.UTC(2026,11,1,0,0),el=document.getElementById("psp-cd");function f(){{var d=t-Date.now();if(d<=0){{el.textContent="December\'s monthly games unlock today or are already out: check the PlayStation Plus tab.";return}}var h=Math.floor(d/36e5);el.textContent=Math.ceil(h/24)+" day"+(Math.ceil(h/24)==1?"":"s")+" until December\'s games unlock on Tuesday 1 December (the exact hour varies by region).";}}f();setInterval(f,60000)}})();</script>'
    f'<section><div class="wrap"><div class="sec-head"><h2>PS Plus monthly games, month by month</h2></div>'
    f'<div class="table-wrap"><table><thead><tr><th>Month</th><th>Games</th><th>Claim window</th></tr></thead><tbody>{_psp_rows}</tbody></table></div>'
    f'<p class="muted">Monthly games come with every tier: Essential, Extra and Premium. Once claimed, a game stays in your library for as long as you keep a PS Plus subscription.</p></div></section>'
    + AD.format("psp-mid") +
    f'<section><div class="wrap"><div class="sec-head"><h2>How PS Plus monthly games work</h2></div>'
    f'<ul><li><strong>Reveal:</strong> usually on the PlayStation Blog on the last Wednesday of the month. Leaks sometimes appear a day or two earlier.</li>'
    f'<li><strong>Release:</strong> the first Tuesday of the month. The previous month\'s games leave the same day, so claim them before then.</li>'
    f'<li><strong>How to claim:</strong> on PS5 open PlayStation Plus, choose Monthly Games, then Add to Library. On PS4 open PlayStation Plus from the function screen. You can also add them from the PlayStation Store website or app and download later.</li>'
    f'<li><strong>Keep them:</strong> claimed games stay in your library while you subscribe. If your subscription lapses they lock, and unlock again when you re-subscribe.</li></ul>'
    f'<h2>PS Plus Essential vs Extra vs Premium</h2><p>Essential gives you the monthly games, online multiplayer and cloud saves. Extra adds the Game Catalog, a rotating library of hundreds of games: November 2026\'s catalog update was led by Death Stranding 2: On the Beach, Atomfall and Dragon Quest III HD-2D Remake, from 17 November. Premium adds classics, game trials and cloud streaming. Prices differ by region and Sony raised some US prices in May 2026, so check the PlayStation Store for yours.</p>'
    f'<div class="sec-head" style="margin-top:28px"><h2>Related</h2></div><ul>'
    f'<li><a href="{href("platforms/ps5.html", 0)}">Every PS5 game coming in 2027</a></li>'
    f'<li><a href="{href("game-pass-2027.html", 0)}">Xbox Game Pass 2027</a>: every confirmed game</li>'
    f'<li><a href="{href("games-december-2026.html", 0)}">Games coming out in December 2026</a></li>'
    f'<li><a href="{href("new-games-this-week.html", 0)}">New games this week</a></li></ul></div></section>')
psp_faq = [
    ("What are the PS Plus games for December 2026?", "Tony Hawk's Pro Skater 3+4, Dragon Ball Xenoverse 2 and Amnesia: The Bunker, announced on the PlayStation Blog on 25 November 2026. Claim them from 1 December 2026 to 4 January 2027."),
    ("What are the PS Plus games for November 2026?", "Dead Island 2 (PS5, PS4), Tomb Raider IV–VI Remastered (PS5, PS4) and Monster Train 2 (PS5), claimable from 3 to 30 November 2026."),
    ("When are PS Plus monthly games announced?", "Usually on the last Wednesday of the month, on the PlayStation Blog, often around 4:30 pm UK time."),
    ("When do new PS Plus games come out?", "On the first Tuesday of the month. The previous month's games can be claimed until then."),
    ("Do I keep PS Plus games forever?", "You keep claimed monthly games for as long as you have an active PS Plus subscription of any tier."),
]
page("ps-plus-monthly-games.html", "PS Plus December 2026 Games: Tony Hawk 3+4, Dragon Ball Xenoverse 2, Amnesia | DayOneDrop",
     "PS Plus December 2026 monthly games: Tony Hawk's Pro Skater 3+4, Dragon Ball Xenoverse 2 and Amnesia: The Bunker, 1 Dec to 4 Jan. November's games until 30 November.",
     psp_body, 0, psp_faq, crumbs=[("Home", DOMAIN + "/"), ("PS Plus monthly games", canon("ps-plus-monthly-games.html"))])

# ---------------- EPIC FREE GAMES (Keyword Planner worldwide 25 Nov 2026: "epic free games" 10k-100k, low comp). UPDATE EVERY THURSDAY after 16:00 UTC. ----------------
EPIC = [  # (from, to, games, status) Sources: SteamDB promo pages, NerdZap 13 Nov, GGRecon 12 Nov, Clouddosage, Kyber's Corner.
    ("26 Nov", "3 Dec 2026", "Bread & Fred (announced)", "next"),
    ("19 Nov", "26 Nov 2026", "Mark of the Deep, Alien: Isolation", "now"),
    ("12 Nov", "19 Nov 2026", "Knightica", "past"),
    ("5 Nov", "12 Nov 2026", "Flotsam (+ an Idle Champions pack)", "past"),
    ("29 Oct", "5 Nov 2026", "Sorry We're Closed", "past"),
]
_ep_rows = "".join(f"<tr{' style=\"font-weight:700\"' if st == 'now' else ''}><td>{a} – {b}</td><td>{e(g)}</td><td>{ {'now': 'Free now', 'next': 'Next', 'past': 'Ended'}[st] }</td></tr>" for a, b, g, st in EPIC)
_ep_now = [x for x in EPIC if x[3] == "now"][0]; _ep_next = [x for x in EPIC if x[3] == "next"]
ep_body = (f'<header class="hero"><div class="wrap"><span class="kicker">Epic Games Store</span><h1>Epic free games<br><span class="amber">this week.</span></h1>'
    f'<p class="lead">What\'s free to keep on the Epic Games Store right now, what\'s free next week, and every recent giveaway.</p></div></header>'
    f'<section style="padding-top:10px"><div class="wrap"><div class="tool"><p><strong>Free now:</strong> {e(_ep_now[2])}, until Thursday {_ep_now[1]} at 11 am ET (4 pm UK, 9 pm PKT).</p>'
    + (f'<p><strong>Next:</strong> {e(_ep_next[0][2])}, from {_ep_next[0][0]} to {_ep_next[0][1]}.</p>' if _ep_next else '')
    + '<p id="ep-cd" class="muted" aria-live="polite"></p></div></div></section>'
    '<script>(function(){var el=document.getElementById("ep-cd");function nx(){var n=new Date(),t=new Date(Date.UTC(n.getUTCFullYear(),n.getUTCMonth(),n.getUTCDate(),16,0));var d=(4-t.getUTCDay()+7)%7;t.setUTCDate(t.getUTCDate()+d);if(t<=n)t.setUTCDate(t.getUTCDate()+7);return t}'
    'function f(){var t=nx(),ms=t-Date.now(),h=Math.floor(ms/36e5),m=Math.floor(ms%36e5/6e4);el.textContent="The next swap is in "+Math.floor(h/24)+"d "+h%24+"h "+m+"m: "+t.toLocaleString([], {weekday:"long",hour:"numeric",minute:"2-digit"})+" your time."}f();setInterval(f,30000)})();</script>'
    f'<section><div class="wrap"><div class="sec-head"><h2>Every recent Epic free game</h2></div>'
    f'<div class="table-wrap"><table><thead><tr><th>Dates</th><th>Free games (PC)</th><th>Status</th></tr></thead><tbody>{_ep_rows}</tbody></table></div>'
    f'<p class="muted">Times are 16:00 UTC (11 am ET, 4 pm UK, 9 pm PKT). Epic sometimes adds mobile-only giveaways; this list covers the PC games. Always check the store says "Free" before claiming.</p></div></section>'
    + AD.format("ep-mid") +
    f'<section><div class="wrap"><div class="sec-head"><h2>How Epic\'s free games work</h2></div><ul>'
    f'<li><strong>Every Thursday at 11 am ET</strong> (4 pm UK) the free games change, and next week\'s are usually revealed at the same moment.</li>'
    f'<li><strong>Claim, keep forever:</strong> click Get on the store page during the week and the game stays in your Epic library, even after the offer ends. You don\'t have to download it straight away.</li>'
    f'<li><strong>Free account needed.</strong> No subscription, unlike PS Plus or Game Pass.</li>'
    f'<li><strong>December:</strong> in recent years Epic has run a holiday event with a new free game every day in late December. It hasn\'t been announced for 2026 yet; this page will list each one if it happens.</li></ul>'
    f'<div class="sec-head" style="margin-top:28px"><h2>More free and subscription games</h2></div><ul>'
    f'<li><a href="{href("ps-plus-monthly-games.html", 0)}">PS Plus monthly games</a>: December 2026</li>'
    f'<li><a href="{href("game-pass-2027.html", 0)}">Xbox Game Pass 2027</a></li>'
    f'<li><a href="{href("steam-sale-dates.html", 0)}">Steam sale dates</a>: Winter Sale 17 Dec to 4 Jan, with a countdown</li>'
    f'<li><a href="{href("platforms/pc.html", 0)}">Every PC game coming in 2027</a></li>'
    f'<li><a href="{href("new-games-this-week.html", 0)}">New games this week</a></li></ul></div></section>')
ep_faq = [
    ("What is the Epic free game this week?", f"{_ep_now[2]}, free to keep until {_ep_now[1]} at 11 am ET (4 pm UK)."),
    ("What is the next free game on Epic?", (f"{_ep_next[0][2]}, from {_ep_next[0][0]} to {_ep_next[0][1]}." if _ep_next else "Epic reveals it when the current week's games go live.")),
    ("What time do Epic free games change?", "Every Thursday at 11 am ET, which is 4 pm UK time, 9 pm in Pakistan and 9:30 pm in India."),
    ("Do you keep Epic free games forever?", "Yes. Once you claim a game during its free week it stays in your Epic library."),
    ("Does Epic do mystery games in December?", "In recent years Epic has given away a free game every day over the holidays. It hasn't announced the 2026 event yet."),
]
page("epic-free-games.html", "Epic Free Games This Week (and Next Week): Every Free Game, Updated Thursdays | DayOneDrop",
     f"Epic Games Store free games this week: {_ep_now[2]} until {_ep_now[1]}." + (f" Next: {_ep_next[0][2]}." if _ep_next else "") + " Plus the swap time in your time zone."[:160],
     ep_body, 0, ep_faq, crumbs=[("Home", DOMAIN + "/"), ("Epic free games", canon("epic-free-games.html"))])


# ---------------- STEAM SALE DATES (DEMAND.md G7: "steam sale dates" 1k-10k; 25 Nov 2026) ----------------
# Valve's Steamworks schedule (posted 15 Jul 2026, updated 6 Nov 2026) via PC Gamer (15 Jul 2026 + sale-dates guide), Notebookcheck and GamesRadar+.
# Second half of 2027 (Autumn + Winter Sale 2027) NOT announced yet: add when Valve posts it (2+ sources).
STEAM = [  # (name, start, end, kind) kind: sale | next | fest. End date = last day listed by Valve.
    ("Steam Winter Sale 2026", "2026-12-17", "2027-01-04", "sale"),
    ("Desktop Companion Fest", "2027-01-14", "2027-01-18", "fest"),
    ("Shop Keeper Fest", "2027-01-25", "2027-02-01", "fest"),
    ("Sheep Fest", "2027-02-04", "2027-02-08", "fest"),
    ("Couch Co-Op Fest", "2027-02-08", "2027-02-15", "fest"),
    ("Steam Next Fest: February 2027", "2027-02-22", "2027-03-01", "next"),
    ("Rhythm Fest", "2027-03-08", "2027-03-15", "fest"),
    ("Steam Spring Sale 2027", "2027-03-18", "2027-03-25", "sale"),
    ("Dinos vs. Robots Fest", "2027-03-29", "2027-04-05", "fest"),
    ("Racing Fest", "2027-04-12", "2027-04-19", "fest"),
    ("Witch Fest", "2027-04-22", "2027-04-26", "fest"),
    ("Fighting Fest", "2027-04-26", "2027-05-03", "fest"),
    ("Real-Time Strategy Fest", "2027-05-10", "2027-05-17", "fest"),
    ("Mountaineering Fest", "2027-05-31", "2027-06-03", "fest"),
    ("Steam Next Fest: June 2027", "2027-06-14", "2027-06-21", "next"),
    ("Steam Summer Sale 2027", "2027-06-24", "2027-07-08", "sale"),
]
STEAM_PAST = [("Steam Autumn Sale 2026", "2026-10-01", "2026-10-08", "sale"), ("Steam Scream V Fest", "2026-10-26", "2026-11-02", "fest"),
              ("Auto-Battler RPG Fest", "2026-11-16", "2026-11-23", "fest")]
_SS_KIND = {"sale": "Big seasonal sale", "next": "Next Fest (free demos)", "fest": "Themed fest"}
def _pt_utc_hour(d):
    """10 am Pacific in UTC: 17:00 during US daylight time (2nd Sun Mar to 1st Sun Nov), else 18:00."""
    mar = datetime.date(d.year, 3, 8); mar += datetime.timedelta(days=(6 - mar.weekday()) % 7)
    nov = datetime.date(d.year, 11, 1); nov += datetime.timedelta(days=(6 - nov.weekday()) % 7)
    return 17 if mar <= d < nov else 18
def _ss_iso(ds):
    d = datetime.date.fromisoformat(ds)
    return f"{ds}T{_pt_utc_hour(d):02d}:00:00Z"
def _ss_nice(ds):
    d = datetime.date.fromisoformat(ds)
    return f"{_WD[d.weekday()][:3]} {d.day} {d.strftime('%b')}" + ("" if d.year == 2027 else f" {d.year}")
def _ss_gcal(n, a, b):
    from urllib.parse import quote
    da, db = datetime.date.fromisoformat(a), datetime.date.fromisoformat(b) + datetime.timedelta(days=1)
    return ("https://calendar.google.com/calendar/render?action=TEMPLATE&text=" + quote(n) + f"&dates={da:%Y%m%d}/{db:%Y%m%d}&details="
            + quote("Steam event dates from Valve's schedule, via DayOneDrop (getdayonedrop.com/steam-sale-dates). Usually starts 10 am Pacific."))
_ss_today = datetime.date.fromisoformat(UPDATED)
_ss_up = [x for x in STEAM if datetime.date.fromisoformat(x[2]) >= _ss_today]
_ss_next_sale = [x for x in _ss_up if x[3] == "sale"][0]
_ss_sales = [x for x in STEAM if x[3] == "sale"]
_ss_nf = [x for x in STEAM if x[3] == "next"]
_ss_days = (datetime.date.fromisoformat(_ss_next_sale[1]) - _ss_today).days
_ss_len = lambda x: (datetime.date.fromisoformat(x[2]) - datetime.date.fromisoformat(x[1])).days + 1
_ss_pc = sorted([g for g in GAMES if "PC" in g["platforms"] and g["date"]], key=lambda g: g["date"])
_ss_clash = [(x, [g for g in _ss_pc if x[1] <= g["date"] <= x[2]]) for x in STEAM]
_ss_clash = [(x, gs) for x, gs in _ss_clash if gs]
_ss_quick = (f"The next big Steam sale is the {_ss_next_sale[0]}: {_ss_nice(_ss_next_sale[1])} to {_ss_nice(_ss_next_sale[2])} 2027 ({_ss_len(_ss_next_sale)} days). "
             f"In 2027 Valve has set the Spring Sale for 18 to 25 March and the Summer Sale for 24 June to 8 July, with Next Fest on 22 February and 14 June. "
             f"The 2027 Autumn and Winter Sale dates are not announced yet.")
def _ss_row(x, past=False):
    n, a, b, k = x
    return (f'<div class="row" data-ss-k="{k}" data-ss-s="{_ss_iso(a)}" data-ss-e="{_ss_iso(b)}"><span style="min-width:0"><strong>{e(n)}</strong><br>'
            f'<span class="muted">{e(_SS_KIND[k])} · {_ss_len(x)} days</span><br><span class="muted mono ss-st" style="font-size:.78rem">{"Ended" if past else ""}</span></span>'
            f'<span style="text-align:right;flex-shrink:0;max-width:48%"><b style="white-space:normal">{e(_ss_nice(a))} – {e(_ss_nice(b))}</b>'
            + ("" if past else f'<br><a class="muted" style="font-size:.8rem" href="{_ss_gcal(n, a, b)}" rel="nofollow noopener" target="_blank">+ Google Calendar</a>') + '</span></div>')
_ss_tcell = 'style="padding:6px;border-top:1px solid var(--rule)"'
_ss_tbl = ('<div style="overflow-x:auto"><table class="gen-table" style="width:100%;border-collapse:collapse;font-size:.92rem"><thead><tr>'
           '<th style="text-align:left;padding:6px">Event</th><th style="text-align:left;padding:6px">Starts</th><th style="text-align:left;padding:6px">Ends</th><th style="text-align:left;padding:6px">Type</th></tr></thead><tbody>'
           + "".join(f'<tr><td {_ss_tcell}>{e(n)}</td><td {_ss_tcell} class="mono">{e(_ss_nice(a))}</td><td {_ss_tcell} class="mono">{e(_ss_nice(b))}</td><td {_ss_tcell}>{e(_SS_KIND[k])}</td></tr>' for n, a, b, k in STEAM)
           + f'<tr><td {_ss_tcell}>Steam Autumn Sale 2027</td><td {_ss_tcell}>Not announced</td><td {_ss_tcell}>–</td><td {_ss_tcell}>Big seasonal sale</td></tr>'
           + f'<tr><td {_ss_tcell}>Steam Winter Sale 2027</td><td {_ss_tcell}>Not announced</td><td {_ss_tcell}>–</td><td {_ss_tcell}>Big seasonal sale</td></tr>'
           + '</tbody></table></div>')
_ss_chips = ('<div class="chips" role="group" aria-label="Event type"><button class="chip" type="button" data-ss-f="" aria-pressed="true">Everything</button>'
             '<button class="chip" type="button" data-ss-f="sale" aria-pressed="false">Big sales only</button>'
             '<button class="chip" type="button" data-ss-f="next" aria-pressed="false">Next Fest</button>'
             '<button class="chip" type="button" data-ss-f="fest" aria-pressed="false">Themed fests</button></div>')
ss_body = (f'<header class="hero"><div class="wrap"><span class="kicker">Steam</span>'
           f'<h1>Steam sale dates:<br><span class="amber">when is the next Steam sale?</span></h1>'
           f'<p class="lead">Every Steam sale and fest Valve has scheduled, from the Winter Sale 2026 to the Summer Sale 2027, with a live countdown in your time zone and calendar links.</p>'
           f'<p class="muted" style="margin:0">Last checked {e(UPDATED)} · dates from Valve\'s Steamworks schedule</p></div></header>'
           f'<section><div class="wrap"><div class="out" style="margin-bottom:24px"><div class="row"><span><strong>Quick answer:</strong> {e(_ss_quick)}</span></div></div>'
           f'<div class="tool" id="ss-tool"><h2 style="font-size:1.5rem;margin-top:0">How long until the next Steam sale?</h2>'
           f'<p class="mono amber" id="ss-cd" aria-live="polite" style="font-size:1.1rem;margin:0 0 4px">The {e(_ss_next_sale[0])} starts in {_ss_days} days.</p>'
           f'<p class="muted" id="ss-cd2" style="margin:0 0 14px"></p>'
           f'<p class="muted">Pick what you care about. Each event is marked on now, starting soon or ended as you read, and your choice is remembered on this device.</p>{_ss_chips}'
           f'<p class="mono amber" id="ss-count" aria-live="polite" style="margin:12px 0 0">{len(STEAM)} events</p>'
           f'<div class="out" id="ss-list" style="margin-top:12px">{"".join(_ss_row(x) for x in STEAM)}</div><p class="empty" id="ss-none" hidden>Nothing of that type is scheduled yet.</p></div></div></section>'
           + AD.format("ss-mid") +
           f'<section><div class="wrap"><div class="sec-head"><h2>When is the Steam Winter Sale 2026?</h2></div>'
           f'<p>Thursday 17 December 2026 to Monday 4 January 2027: {_ss_len(STEAM[0])} days. Steam sales usually start and end at 10 am Pacific (6 pm UK, 11 pm in Pakistan); Valve\'s schedule lists dates only, so the countdown above uses that usual time.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>What are all the Steam sale dates for 2027?</h2><span class="muted">January to July</span></div>{_ss_tbl}'
           f'<p class="muted" style="margin-top:10px">Valve publishes its schedule in halves. The January to July 2027 events were posted in July 2026; the second half of 2027 usually follows later. Sources: Steamworks via PC Gamer, Notebookcheck and GamesRadar+.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>When is the Steam Spring Sale 2027?</h2></div>'
           f'<p>Thursday 18 March to Thursday 25 March 2027 ({_ss_len(_ss_sales[1])} days).</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>When is the Steam Summer Sale 2027?</h2></div>'
           f'<p>Thursday 24 June to Thursday 8 July 2027 ({_ss_len(_ss_sales[2])} days), straight after the June Next Fest.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>When is Steam Next Fest 2027?</h2></div>'
           f'<p>Twice so far: 22 February to 1 March 2027, and 14 to 21 June 2027. Next Fest is a week of free demos for games that are not out yet, not a discount sale.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>When are the Steam Autumn Sale and Winter Sale 2027?</h2></div>'
           f'<p>Not announced. For reference, the 2026 Autumn Sale ran 1 to 8 October 2026 and the 2026 Winter Sale runs 17 December to 4 January. We add the 2027 dates as soon as Valve posts them.</p>'
           + (f'<div class="sec-head" style="margin-top:28px"><h2>Which new PC games launch during a Steam sale or fest?</h2><span class="muted">{sum(len(gs) for x, gs in _ss_clash)} games</span></div>'
              f'<p class="muted">Dated 2027 PC games from our tracker whose launch day falls inside a Steam event. New launches are rarely discounted in their first week, but they get extra store traffic.</p>'
              f'<div class="out" style="margin-bottom:10px">' + "".join(f'<div class="row"><span><strong>{_gname(g)}</strong><br><span class="muted">During {e(x[0])}</span></span><b>{e(nice_date(g))}</b></div>' for x, gs in _ss_clash for g in gs) + '</div>' if _ss_clash else "")
           + f'<div class="sec-head" style="margin-top:28px"><h2>Which Steam sales and fests already happened in late 2026?</h2></div>'
           f'<div class="out" style="margin-bottom:10px">{"".join(_ss_row(x, True) for x in STEAM_PAST)}</div>'
           f'<div class="sec-head" style="margin-top:28px"><h2>Related pages and tools</h2></div><ul>'
           f'<li><a href="{href("epic-free-games.html", 0)}">Epic free games this week</a>, updated every Thursday</li>'
           f'<li><a href="{href("platforms/pc.html", 0)}">Every PC game coming in 2027</a>, month by month</li>'
           f'<li><a href="{href("new-games-this-week.html", 0)}">New games this week</a></li>'
           f'<li><a href="{href("backlog-planner-2027.html", 0)}">2027 backlog planner</a>: what you can finish before each launch</li></ul></div></section>')
ss_faq = [
    ("When is the next Steam sale?", f"The {_ss_next_sale[0]}, from {_ss_nice(_ss_next_sale[1])} to {_ss_nice(_ss_next_sale[2])} 2027."),
    ("When is the Steam Winter Sale 2026?", "17 December 2026 to 4 January 2027. Steam sales usually start at 10 am Pacific (6 pm UK)."),
    ("When is the Steam Summer Sale 2027?", "24 June to 8 July 2027, according to Valve's published schedule."),
    ("When is the Steam Spring Sale 2027?", "18 to 25 March 2027."),
    ("When is Steam Next Fest 2027?", "22 February to 1 March 2027 and 14 to 21 June 2027."),
    ("When is the Steam Autumn Sale 2027?", "Valve has not announced it yet. The 2026 Autumn Sale ran 1 to 8 October 2026."),
    ("What time does the Steam sale start?", "Usually 10 am Pacific, which is 1 pm Eastern, 6 pm UK and 11 pm Pakistan time. Valve's schedule lists only the dates."),
]
page("steam-sale-dates.html", "Steam Sale Dates 2026-2027: Winter Sale, Spring Sale, Summer Sale and Next Fest | DayOneDrop",
     f"Next Steam sale: {_ss_next_sale[0]}, {_ss_nice(_ss_next_sale[1])} – {_ss_nice(_ss_next_sale[2])} 2027. Every 2027 Steam sale and fest date with a live countdown."[:160],
     ss_body, 0, ss_faq, crumbs=[("Home", DOMAIN + "/"), ("PC games", canon("platforms/pc.html")), ("Steam sale dates", canon("steam-sale-dates.html"))])

# ---------------- NINTENDO DIRECT (DEMAND.md G3: "nintendo direct" 100k-1M; 25 Nov 2026) ----------------
# Past Directs: Game Informer, GamesRadar+, GameSpot, Nintendo Life (Jun + Sep 2026); Pocket Tactics + Nintendo Life (Feb 2026 Partner Showcase).
# Only list 2027 games that are already in games.json (2-source checked). UPDATE when Nintendo announces the next Direct.
ND_NEXT = None  # e.g. ("2027-02-10", "Nintendo Direct", "about 40 minutes", "7 am PT") once Nintendo announces it
ND_PAST = [  # (date, type, length, 2027 slugs shown, other headline news)
    ("2026-09-09", "Nintendo Direct", "about 45 minutes",
     ["metroid-ravenous", "danganronpa-2x2", "tomb-raider-legacy-of-atlantis", "romancing-saga-3-destinies-united", "hyrule-warriors-age-of-calamity-definitive-edition",
      "eternal-anima", "final-fantasy-vii-revelation", "persona-4-revival", "kirby-and-the-world-beyond", "mega-man-dual-override"],
     "Also: Professor Layton and the New World of Steam dated for 10 December 2026 and a free Mario Kart World update. It came a day after the Zelda 40th anniversary Direct (8 September)."),
    ("2026-06-09", "Nintendo Direct", "about 50 minutes",
     ["xenoblade-genesis", "muramasa-revenant-blades", "atelier-karia", "kingdom-hearts-iv", "the-duskbloods"],
     "Also: the Legend of Zelda: Ocarina of Time remake for Switch 2, Fire Emblem: Fortune's Weave, Splatoon Raiders, Rhythm Heaven Groove and Star Fox."),
    ("2026-02-05", "Nintendo Direct Partner Showcase", "third-party games only", [],
     "Third-party news only, including Resident Evil Requiem, Pragmata and Final Fantasy VII Rebirth for Switch 2. No 2027 dates."),
]
_GBS = {g["slug"]: g for g in GAMES}
_sw = sorted([g for g in GAMES if "Switch 2" in g["platforms"]], key=lambda x: (x["month"], x["date"] or "9999"))
_sw_und = [g for g in _sw if not g["date"]]
_sw_big = [g for g in _sw if g["page"]]
_nd_last = ND_PAST[0]
_nd_full = [x for x in ND_PAST if x[1] == "Nintendo Direct"]
_nd_since = (datetime.date.fromisoformat(UPDATED) - datetime.date.fromisoformat(_nd_last[0])).days
_nd_quick = ((f"The next Nintendo Direct is on {_xs_day(ND_NEXT[0])} at {ND_NEXT[3]}." if ND_NEXT else
              "Nintendo has not announced the next Nintendo Direct. Nintendo usually confirms a Direct only a day or two before it airs. ")
             + f"The last full Direct was on {_xs_day(_nd_last[0])} ({_nd_since} days ago), and it dated Switch 2 games like Metroid: Ravenous (28 January 2027). "
             f"{len(_sw_und)} of the {len(_sw)} Switch 2 games we track for 2027 still have no exact date.")
def _ndrow(g):
    return (f'<div class="row" data-ndd="{1 if g["date"] else 0}" data-slug="{e(g["slug"])}"><span><strong>{_gname(g)}</strong>'
            f'<br><span class="muted">{e(g.get("genre") or "")} · {e(g.get("dev") or "Studio TBC")}' + (' · Switch 2 only' if g["platforms"] == ["Switch 2"] else "") + f'</span></span><b>{e(nice_date(g))}</b></div>')
_nd_tc = 'style="padding:6px;border-top:1px solid var(--rule);vertical-align:top"'
_nd_tbl = ('<div style="overflow-x:auto"><table class="gen-table" style="width:100%;border-collapse:collapse;font-size:.92rem"><thead><tr>'
           '<th style="text-align:left;padding:6px">Date</th><th style="text-align:left;padding:6px">Show</th><th style="text-align:left;padding:6px">2027 games shown</th></tr></thead><tbody>'
           + "".join(f'<tr><td {_nd_tc} class="mono">{e(_xs_day(d))}</td><td {_nd_tc}>{e(t)}<br><span class="muted">{e(ln)}</span></td>'
                     f'<td {_nd_tc}>{e(", ".join(_GBS[s]["title"] for s in sl if s in _GBS) or "None")}</td></tr>' for d, t, ln, sl, o in ND_PAST)
           + '</tbody></table></div>')
def _nd_sec(x):
    d, t, ln, sl, o = x
    gs = [_GBS[s] for s in sl if s in _GBS]
    mon = datetime.date.fromisoformat(d).strftime("%B %Y")
    return (f'<div class="sec-head" style="margin-top:28px"><h2>What 2027 games were shown at the {e(mon)} {e(t)}?</h2><span class="muted">{len(gs)}</span></div>'
            + (f'<div class="out" style="margin-bottom:10px">{"".join(_ndrow(g) for g in gs)}</div>' if gs else "")
            + f'<p class="muted">{e(o)} Dates shown are the current ones from our tracker.</p>')
_nd_chips = ('<div class="chips" role="group" aria-label="Date"><button class="chip" type="button" data-nd-d="0" aria-pressed="true">No exact date yet</button>'
             '<button class="chip" type="button" data-nd-d="1" aria-pressed="false">Already dated</button><button class="chip" type="button" data-nd-d="" aria-pressed="false">All</button></div>')
nd_body = (f'<header class="hero"><div class="wrap"><span class="kicker">Nintendo</span>'
           f'<h1>Nintendo Direct:<br><span class="amber">when is the next one?</span></h1>'
           f'<p class="lead">The next Nintendo Direct date (as soon as Nintendo confirms it), every 2026 Direct and what it showed, and the Switch 2 games of 2027 still waiting for a date.</p>'
           f'<p class="muted" style="margin:0">Last checked {e(UPDATED)} · we update this page the day a Direct is announced</p></div></header>'
           f'<section><div class="wrap"><div class="out" style="margin-bottom:24px"><div class="row"><span><strong>Quick answer:</strong> {e(_nd_quick)}</span></div></div>'
           f'<div class="tool" id="nd-tool"><h2 style="font-size:1.5rem;margin-top:0">Which Switch 2 games could get a date at the next Direct?</h2>'
           f'<p class="muted">Switch 2 games announced for 2027 without an exact day are the most likely to get one. Switch the list, then save the games you care about to your ★ list. Your choice is remembered on this device.</p>{_nd_chips}'
           f'<p class="mono amber" id="nd-count" aria-live="polite" style="margin:12px 0 0">{len(_sw_und)} games</p>'
           f'<div class="out" id="nd-list" style="margin-top:12px">{"".join(_ndrow(g) for g in _sw)}</div><p class="empty" id="nd-none" hidden>No tracked Switch 2 games match that yet.</p>'
           f'<div class="btns" style="margin-top:10px;display:flex;gap:8px;flex-wrap:wrap"><button class="btn sm" type="button" id="nd-add">Add these to my ★ list</button>'
           f'<a class="btn line sm" href="{href("platforms/switch-2.html", 0)}">All Switch 2 release dates</a></div></div></div></section>'
           + AD.format("nd-mid") +
           f'<section><div class="wrap"><div class="sec-head"><h2>When is the next Nintendo Direct?</h2></div>'
           + (f'<p><strong>{e(_xs_day(ND_NEXT[0]))}</strong>, {e(ND_NEXT[3])}: a {e(ND_NEXT[1])}, {e(ND_NEXT[2])}.</p>' if ND_NEXT else
              f'<p>Not announced. Nintendo normally reveals a Direct only a day or two ahead, on its social channels and the Nintendo Today app, so any date you see earlier is a rumour. '
              f'In 2026 the full Directs aired in June and September, with a third-party Partner Showcase in February.</p>')
           + f'<div class="sec-head" style="margin-top:28px"><h2>When was the last Nintendo Direct?</h2></div>'
           f'<p>{e(_xs_day(_nd_last[0]))}: a full {e(_nd_last[1])} lasting {e(_nd_last[2])}. Every big Direct of 2026:</p>{_nd_tbl}'
           f'<p class="muted" style="margin-top:10px">Smaller shows (Indie World, single-game Directs like Splatoon Raiders and the Zelda 40th anniversary Direct) are left out of the table. Sources: Game Informer, GamesRadar+, GameSpot, Nintendo Life.</p>'
           + "".join(_nd_sec(x) for x in ND_PAST[:2])
           + (f'<div class="sec-head" style="margin-top:28px"><h2>Which big Switch 2 games of 2027 have no release date yet?</h2><span class="muted">{len([g for g in _sw_und if g["page"]])}</span></div>'
              f'<div class="out" style="margin-bottom:10px">' + "".join(_ndrow(g) for g in _sw_und if g["page"]) + '</div>')
           + f'<div class="sec-head" style="margin-top:28px"><h2>Will there be a Nintendo Direct in December?</h2></div>'
           f'<p>Nothing is announced. The next confirmed showcase is The Game Awards on 10 December 2026, where Nintendo games often appear. See our <a href="{href("game-awards-2026.html", 0)}">Game Awards 2026 page</a> for the nominees and the 2027 games in Most Anticipated.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>Related pages and tools</h2></div><ul>'
           f'<li><a href="{href("platforms/switch-2.html", 0)}">Every Switch 2 game coming in 2027</a>, month by month</li>'
           f'<li><a href="{href("exclusives-2027.html", 0)}">2027 console exclusives</a>, including Switch 2 only games</li>'
           f'<li><a href="{href("xbox-games-showcase-2027.html", 0)}">Xbox Games Showcase 2027</a>: the likely date and past shows</li>'
           f'<li><a href="{href("last-gen-games-2027.html", 0)}">2027 games still coming to Switch 1</a></li></ul></div></section>')
nd_faq = [
    ("When is the next Nintendo Direct?", (f"{_xs_day(ND_NEXT[0])} at {ND_NEXT[3]}." if ND_NEXT else "Nintendo has not announced it. Nintendo usually confirms a Direct only a day or two before it airs.")),
    ("When was the last Nintendo Direct?", f"{_xs_day(_nd_last[0])}. It lasted {_nd_last[2]} and dated Switch 2 games including Metroid: Ravenous, Danganronpa 2x2 and Hyrule Warriors: Age of Calamity Definitive Edition."),
    ("How many Nintendo Directs were there in 2026?", "Two full Nintendo Directs (9 June and 9 September) and a Partner Showcase (5 February), plus smaller shows such as Indie World and single-game Directs."),
    ("What was announced at the September 2026 Nintendo Direct?", "2027 dates for Metroid: Ravenous (28 January), Danganronpa 2x2 (14 January), Tomb Raider: Legacy of Atlantis, Hyrule Warriors: Age of Calamity Definitive Edition (25 February), Final Fantasy VII Revelation (8 April) and the Switch 2 version of Persona 4 Revival (20 May), plus Kirby and the World Beyond for spring 2027."),
    ("Which Switch 2 games of 2027 have no date yet?", ", ".join(f"{g['title']} ({nice_date(g)})" for g in _sw_und) + "."),
    ("Is there a Nintendo Direct in December 2026?", "None is announced. The Game Awards on 10 December 2026 is the next confirmed show."),
]
page("nintendo-direct.html", "Next Nintendo Direct: Date, Last Direct and Switch 2 Games Still Without a Date | DayOneDrop",
     f"When is the next Nintendo Direct? Not announced yet. The last was {_xs_day(_nd_last[0])}. Every 2026 Direct, and the {len(_sw_und)} Switch 2 2027 games still without a date."[:160],
     nd_body, 0, nd_faq, crumbs=[("Home", DOMAIN + "/"), ("Switch 2 games", canon("platforms/switch-2.html")), ("Nintendo Direct", canon("nintendo-direct.html"))])

# ---------------- 2027 GAMES WITH NO RELEASE DATE (26 Nov 2026; competitor gap: GI + GamesRadar "TBC 2027" lists) ----------------
_TD = datetime.date.fromisoformat(UPDATED)
_nd_g = sorted([g for g in GAMES if not g["date"]], key=lambda g: (g["month"], g["title"]))
def _nd_bk(g):
    m = g["month"]
    if g.get("window", "").strip() == "2027": return "any"
    return "spring" if m <= 4 else ("mid" if m <= 8 else "late")
_NDBK = {"spring": "Jan to Apr 2027 (spring)", "mid": "May to Aug 2027 (mid-year)", "late": "Late 2027", "any": "Just “2027”"}
_nd_by = {k: [g for g in _nd_g if _nd_bk(g) == k] for k in _NDBK}
_nd_big = [g for g in _nd_g if g["page"]]
_nd_del = [g for g in _nd_g if g["status"] == "delayed"]
_nd_pc = {p: [g for g in _nd_g if p in g["platforms"]] for p in PLATS}
def _tbrow(g):
    return (f'<div class="row" data-plat="{e("|".join(g["platforms"]))}" data-bk="{_nd_bk(g)}" data-slug="{e(g["slug"])}"><span><strong>{_gname(g)}</strong>'
            f'<br><span class="muted">{e(", ".join(g["platforms"]))} · {e(g.get("genre") or "")} · {e(g.get("dev") or "Studio TBC")}'
            + (' · delayed' if g["status"] == "delayed" else "") + f'</span></span><b>{e(g.get("window") or "2027")}</b></div>')
_tb_quick = (f"{len(_nd_g)} of the {len(GAMES)} games we track for 2027 have no exact release date yet. "
             f"{len(_nd_by['spring'])} are due in spring (January to April), {len(_nd_by['mid'])} around mid-2027, {len(_nd_by['late'])} late in 2027 and {len(_nd_by['any'])} just say “2027”. "
             "The biggest without a day are Kingdom Hearts IV (late 2027), Pokémon Winds and Waves, Resident Evil Veronica, State of Decay 3, The Duskbloods and Xenoblade Genesis.")
_tb_chips = ('<div class="chips" role="group" aria-label="Console" style="margin-bottom:8px"><button class="chip" type="button" data-tb-p="" aria-pressed="true">All consoles</button>'
             + "".join(f'<button class="chip" type="button" data-tb-p="{e(p)}" aria-pressed="false">{e(p)}</button>' for p in PLATS) + '</div>'
             '<div class="chips" role="group" aria-label="Timing"><button class="chip" type="button" data-tb-b="" aria-pressed="true">Any time</button>'
             + "".join(f'<button class="chip" type="button" data-tb-b="{k}" aria-pressed="false">{e(v)}</button>' for k, v in _NDBK.items()) + '</div>')
_tc = 'style="padding:6px;border-top:1px solid var(--rule)"'
_tb_tbl = ('<div style="overflow-x:auto"><table class="gen-table" style="width:100%;border-collapse:collapse;font-size:.92rem"><thead><tr><th style="text-align:left;padding:6px">Console</th>'
           '<th style="padding:6px">No exact date</th><th style="text-align:left;padding:6px">Biggest one</th></tr></thead><tbody>'
           + "".join(f'<tr><td {_tc}>{e(p)}</td><td class="mono" {_tc[:-1]};text-align:center">{len(_nd_pc[p])}</td><td {_tc}>{e(next((g["title"] for g in _nd_pc[p] if g["page"]), "-"))}</td></tr>' for p in PLATS)
           + '</tbody></table></div>')
_tb_shows = [
    ("10 December 2026", "The Game Awards 2026", "Confirmed. Publishers often use the show to give 2027 dates."),
    ("December 2026", "Lords of the Fallen II exact date", "CI Games says the exact April 2027 day comes in December (via Gematsu, eTeknix)."),
    ("Late January 2027", "Xbox Developer Direct", "Not announced. The last two aired on 23 January 2025 and 22 January 2026."),
    ("Any time", "Nintendo Direct", "Not announced. Nintendo confirms a Direct a day or two ahead."),
    ("Early June 2027", "Xbox Games Showcase", "Not announced. Our estimate from 2023 to 2026, when every show aired on a Sunday between 7 and 11 June."),
]
_tb_stbl = ('<div style="overflow-x:auto"><table class="gen-table" style="width:100%;border-collapse:collapse;font-size:.92rem"><thead><tr><th style="text-align:left;padding:6px">When</th>'
            '<th style="text-align:left;padding:6px">Show or news</th><th style="text-align:left;padding:6px">Status</th></tr></thead><tbody>'
            + "".join(f'<tr><td {_tc} class="mono">{e(a)}</td><td {_tc}>{e(b)}</td><td {_tc}>{e(c)}</td></tr>' for a, b, c in _tb_shows) + '</tbody></table></div>')
def _tb_sec(k, h):
    gs = _nd_by[k]
    return (f'<div class="sec-head" style="margin-top:28px"><h2>{e(h)}</h2><span class="muted">{len(gs)}</span></div>'
            f'<div class="out" style="margin-bottom:10px">{"".join(_tbrow(g) for g in gs) or "<div class=empty>None right now.</div>"}</div>')
tb_body = (f'<header class="hero"><div class="wrap"><span class="kicker">No date yet</span>'
           f'<h1>2027 games with no release date:<br><span class="amber">{len(_nd_g)} still waiting.</span></h1>'
           f'<p class="lead">Every game confirmed for 2027 that still has no exact launch day, with the season or month the publisher has given, the consoles, and when each one could get its date.</p>'
           f'<p class="muted" style="margin:0">Last checked {e(UPDATED)} · a game moves to the main board the day its date is confirmed</p></div></header>'
           f'<section><div class="wrap"><div class="out" style="margin-bottom:24px"><div class="row"><span><strong>Quick answer:</strong> {e(_tb_quick)}</span></div></div>'
           f'<div class="tool" id="tb-tool"><h2 style="font-size:1.5rem;margin-top:0">Which undated 2027 games are coming to my console?</h2>'
           f'<p class="muted">Pick a console and a time of year, then save the games to your ★ list. When one of them gets a date, it shows up on your list with a countdown. Your choice is remembered on this device.</p>{_tb_chips}'
           f'<p class="mono amber" id="tb-count" aria-live="polite" style="margin:12px 0 0">{len(_nd_g)} games</p>'
           f'<div class="out" id="tb-list" style="margin-top:12px">{"".join(_tbrow(g) for g in _nd_g)}</div><p class="empty" id="tb-none" hidden>No undated 2027 games match that. Try another console or time.</p>'
           f'<div class="btns" style="margin-top:10px;display:flex;gap:8px;flex-wrap:wrap"><button class="btn sm" type="button" id="tb-add">Add these to my ★ list</button>'
           f'<a class="btn line sm" href="{href("calendar.html", 0)}">Games with a date: 2027 calendar</a></div></div></div></section>'
           + AD.format("tb-mid") +
           f'<section><div class="wrap"><div class="sec-head"><h2>Which big 2027 games have no release date yet?</h2><span class="muted">{len(_nd_big)}</span></div>'
           f'<div class="out" style="margin-bottom:10px">{"".join(_tbrow(g) for g in _nd_big)}</div>'
           f'<p class="muted">Each of these has a full guide with everything confirmed so far. Tap a name to open it.</p>'
           + _tb_sec("spring", "Which 2027 games are due in spring but have no day yet?")
           + _tb_sec("mid", "Which 2027 games are due around mid-2027?")
           + _tb_sec("late", "Which games are due late in 2027?")
           + _tb_sec("any", "Which games only say “2027”?")
           + f'<div class="sec-head" style="margin-top:28px"><h2>Which undated 2027 games have been delayed?</h2><span class="muted">{len(_nd_del)}</span></div>'
           f'<div class="out" style="margin-bottom:10px">{"".join(_tbrow(g) for g in _nd_del)}</div>'
           f'<p class="muted">Every slip, with dates and sources, is on the <a href="{href("delayed-games-2027.html", 0)}">delayed games of 2027</a> page.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>How many undated 2027 games are on each console?</h2></div>{_tb_tbl}'
           f'<div class="sec-head" style="margin-top:28px"><h2>When could these games get a release date?</h2></div>'
           f'<p>Most 2027 dates are announced at a showcase or in a publisher earnings report. These are the next chances:</p>{_tb_stbl}'
           f'<p class="muted" style="margin-top:10px">A season like “spring 2027” is the publisher’s own wording. We never guess a day: a game only gets one here when the publisher, or two trusted outlets, confirm it.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>Related pages and tools</h2></div><ul>'
           f'<li><a href="{href("calendar.html", 0)}">2027 release calendar</a>: every game that already has a date</li>'
           f'<li><a href="{href("later-2027.html", 0)}">Games later in 2027 (May to December)</a></li>'
           f'<li><a href="{href("countdown.html", 0)}">Game release countdown</a>: a live timer for any dated 2027 game</li>'
           f'<li><a href="{href("game-awards-2026.html", 0)}">The Game Awards 2026</a>, the next show where 2027 dates could drop</li></ul></div></section>')
tb_faq = [
    ("Which 2027 games don't have a release date yet?", _tb_quick),
    ("Does Kingdom Hearts 4 have a release date?", "No. Square Enix has said late 2027 but has not given a day."),
    ("Which 2027 Switch 2 games have no release date?", f"{len(_nd_pc['Switch 2'])}: " + ", ".join(f"{g['title']} ({g.get('window') or '2027'})" for g in _nd_pc["Switch 2"]) + "."),
    ("Which 2027 PS5 games have no release date?", f"{len(_nd_pc['PS5'])}: " + ", ".join(f"{g['title']} ({g.get('window') or '2027'})" for g in _nd_pc["PS5"]) + "."),
    ("When will undated 2027 games get release dates?", "The next chances are The Game Awards on 10 December 2026, an Xbox Developer Direct (usually late January), any Nintendo Direct, and the summer showcases in June 2027."),
    ("What does 'spring 2027' mean for a release date?", "It is the publisher's own window, usually March to May. The exact day is still to come, so it can still move."),
]
page("games-without-release-date-2027.html", f"2027 Games With No Release Date Yet: All {len(_nd_g)}, by Console and Season | DayOneDrop",
     f"{len(_nd_g)} games are confirmed for 2027 with no exact date: Kingdom Hearts 4, Pokémon Winds and Waves, RE Veronica and more. Filter by console and season."[:160],
     tb_body, 0, tb_faq, crumbs=[("Home", DOMAIN + "/"), ("2027 calendar", canon("calendar.html")), ("No release date yet", canon("games-without-release-date-2027.html"))])

# ---------------- GAME RELEASE COUNTDOWN TOOL (26 Nov 2026) ----------------
_cd_up = sorted([g for g in GAMES if g["date"] and g["date"] >= UPDATED], key=lambda g: (g["date"], g["title"]))
_cd_big = [g for g in _cd_up if g["page"]]
def _cd_days(g): return (datetime.date.fromisoformat(g["date"]) - _TD).days
_cd_first = _cd_up[0]
_cd_firstbig = _cd_big[0] if _cd_big else _cd_first
_cd_quick = (f"The next 2027 game on our board is {_cd_first['title']} on {nice_date(_cd_first)}, {_cd_days(_cd_first)} days from {nice_date({'date': UPDATED, 'window': ''})}. "
             f"The next big one is {_cd_firstbig['title']} on {nice_date(_cd_firstbig)} ({_cd_days(_cd_firstbig)} days). Pick any game below for a live timer to launch day in your own time zone.")
_cd_opts = "".join(f'<option value="{e(g["slug"])}">{e(g["title"])} ({e(short_date(g))})</option>' for g in _cd_up)
def _cdrow(g):
    return (f'<div class="row" data-cd-date="{g["date"]}"><span><strong>{_gname(g)}</strong><br><span class="muted">{e(nice_date(g))} · {e(", ".join(g["platforms"]))}</span></span>'
            f'<b class="cd-days">{_cd_days(g)} days</b></div>')
_cd_ms = collections.OrderedDict()
for g in _cd_up: _cd_ms.setdefault(g["date"][:7], []).append(g)
_cd_mtbl = ('<div style="overflow-x:auto"><table class="gen-table" style="width:100%;border-collapse:collapse;font-size:.92rem"><thead><tr><th style="text-align:left;padding:6px">Month</th>'
            '<th style="padding:6px">Games</th><th style="text-align:left;padding:6px">First launch</th><th style="padding:6px">Days to go</th></tr></thead><tbody>'
            + "".join(f'<tr><td {_tc}>{e(MONTHS[int(k[5:]) - 1])} {k[:4]}</td><td class="mono" {_tc[:-1]};text-align:center">{len(v)}</td><td {_tc}>{e(v[0]["title"])}</td><td class="mono" {_tc[:-1]};text-align:center">{_cd_days(v[0])}</td></tr>' for k, v in _cd_ms.items())
            + '</tbody></table></div>')
cd_body = (f'<header class="hero"><div class="wrap"><span class="kicker">Tool · live countdown</span>'
           f'<h1>Game release countdown:<br><span class="amber">how long until launch day?</span></h1>'
           f'<p class="lead">A live split-flap timer for any dated game of 2027, down to the second, in your own time zone. Pick a game, then copy the link to share that countdown.</p>'
           f'<p class="muted" style="margin:0">Last checked {e(UPDATED)} · {len(_cd_up)} dated games · timers count to midnight local time on release day</p></div></header>'
           f'<section><div class="wrap"><div class="out" style="margin-bottom:24px"><div class="row"><span><strong>Quick answer:</strong> {e(_cd_quick)}</span></div></div>'
           f'<div class="tool" id="cd-tool"><h2 style="font-size:1.5rem;margin-top:0">How many days until my game comes out?</h2>'
           f'<label for="cd-pick">Choose a game</label> <select id="cd-pick" style="max-width:100%">{_cd_opts}</select>'
           f'<div class="next-drop" style="margin-top:16px"><span class="next-label">Countdown to</span><div class="next-title"><span class="flaps" id="cd-title"></span></div>'
           f'<span class="muted" id="cd-date"></span><div class="cd" id="cd-cd" role="timer">'
           f'<div class="cd-unit"><span class="flaps" data-u="0"></span><span>Days</span></div><div class="cd-unit"><span class="flaps" data-u="1"></span><span>Hours</span></div>'
           f'<div class="cd-unit"><span class="flaps" data-u="2"></span><span>Mins</span></div><div class="cd-unit"><span class="flaps" data-u="3"></span><span>Secs</span></div></div>'
           f'<div class="btns" style="display:flex;gap:8px;flex-wrap:wrap"><button class="btn sm" type="button" id="cd-copy">Copy link to this countdown</button>'
           f'<a class="btn line sm" id="cd-gcal" href="#" rel="nofollow noopener" target="_blank">Add to Google Calendar</a>'
           f'<a class="btn line sm" id="cd-guide" href="#" hidden data-base="{"games/" if PREVIEW else "/games/"}" data-ext="{".html" if PREVIEW else ""}">Game guide</a>'
           f'<button class="btn line sm" type="button" id="cd-star">☆ Add to my list</button></div></div></div></div></section>'
           + AD.format("cd-mid") +
           f'<section><div class="wrap"><div class="sec-head"><h2>What is the next game coming out?</h2></div>'
           f'<div class="out" style="margin-bottom:10px">{"".join(_cdrow(g) for g in _cd_up[:8])}</div>'
           f'<div class="sec-head" style="margin-top:28px"><h2>How many days until the big games of 2027?</h2><span class="muted">{len(_cd_big)}</span></div>'
           f'<div class="out" style="margin-bottom:10px">{"".join(_cdrow(g) for g in _cd_big)}</div>'
           f'<p class="muted">Day counts update live on this page. Games with only a season or “2027” have no timer yet: see <a href="{href("games-without-release-date-2027.html", 0)}">2027 games with no release date</a>.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>How far away is each month of releases?</h2></div>{_cd_mtbl}'
           f'<div class="sec-head" style="margin-top:28px"><h2>What time does the countdown end?</h2></div>'
           f'<p>At midnight on release day in your own time zone, which is when most digital games unlock on console stores. Some PC games and global launches unlock at a fixed time instead (for example 6pm in the UK), so check the game guide for the exact unlock time when the publisher gives one.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>Can I share a countdown?</h2></div>'
           f'<p>Yes. Pick a game and tap “Copy link to this countdown”. The link opens this page with that game already selected, so friends see the same timer in their own time zone.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>Related pages and tools</h2></div><ul>'
           f'<li><a href="{href("release-clashes-2027.html", 0)}">Release clash finder</a>: are two of your games too close together?</li>'
           f'<li><a href="{href("backlog-planner-2027.html", 0)}">2027 backlog planner</a>: can you finish your games before the next one?</li>'
           f'<li><a href="{href("new-games-this-week.html", 0)}">New games this week</a> and the full <a href="{href("calendar.html", 0)}">2027 calendar</a></li>'
           f'<li><a href="{href("movies-2027.html", 0)}">Upcoming movies 2027</a>: Zelda, Shrek 5, Avengers: Secret Wars dates</li><li><a href="{href("tools.html", 0)}">Every DayOneDrop tool</a></li></ul></div></section>')
cd_faq = [
    ("What is the next game coming out?", f"{_cd_first['title']} on {nice_date(_cd_first)}."),
    ("How many days until the next big 2027 game?", f"{_cd_days(_cd_firstbig)} days from {nice_date({'date': UPDATED, 'window': ''})}: {_cd_firstbig['title']} launches on {nice_date(_cd_firstbig)}."),
    ("When does the countdown end?", "At midnight on release day in your own time zone. Some games unlock at a fixed global time instead; the game guide says when the publisher confirms one."),
    ("Can I share a game countdown?", "Yes. Pick the game and tap 'Copy link to this countdown'. The link opens with that game selected."),
    ("Is there a countdown for games without a date?", "No. A timer starts only when the publisher confirms an exact day. Undated 2027 games are listed on our 'no release date yet' page."),
]
page("countdown.html", "Game Release Countdown 2027: Live Timer to Launch Day for Every Upcoming Game | DayOneDrop",
     f"Live countdown to every dated 2027 game: days, hours and seconds to launch in your time zone. Next up: {_cd_first['title']} ({short_date(_cd_first)}). Share any timer."[:160],
     cd_body, 0, cd_faq, crumbs=[("Home", DOMAIN + "/"), ("Tools", canon("tools.html")), ("Release countdown", canon("countdown.html"))])

# ---------------- MOVIES 2027 (26 Nov 2026, DEMAND W1 "upcoming movies 2027") ----------------
# US cinema dates. Each from the studio or 2+ of Variety, THR, Deadline, TheWrap, Rotten Tomatoes, Box Office Mojo, GamesRadar, Nintendo Life, Gematsu (checked 26 Nov 2026).
# (title, date, studio, kind, note, where)  kind: hero | anim | game | horror | action | comedy
MOVIES = [
    ("Children of Blood and Bone", "2027-01-15", "Paramount", "action", "Fantasy epic from Tomi Adeyemi's novel, directed by Gina Prince-Bythewood, with Viola Davis.", "Cinemas"),
    ("Ice Age: Boiling Point", "2027-02-05", "20th Century Studios (Disney)", "anim", "The sixth Ice Age film, with Manny, Sid and Diego back.", "Cinemas"),
    ("Narnia: The Magician's Nephew", "2027-02-12", "Netflix", "action", "Greta Gerwig's Narnia. Moved from a November 2026 IMAX run to a wide cinema release with a 45-day window before Netflix.", "Cinemas, then Netflix"),
    ("The Exorcist (Mike Flanagan)", "2027-03-12", "Universal / Blumhouse", "horror", "A new Exorcist from Mike Flanagan, starring Scarlett Johansson.", "Cinemas"),
    ("Sonic the Hedgehog 4", "2027-03-19", "Paramount", "game", "Jeff Fowler directs again; Jim Carrey and Idris Elba return.", "Cinemas"),
    ("Godzilla x Kong: Supernova", "2027-03-26", "Warner Bros. / Legendary", "action", "The next MonsterVerse film, with Kaitlyn Dever and Dan Stevens.", "Cinemas"),
    ("Panic Carefully", "2027-04-09", "Warner Bros.", "comedy", "Sam Esmail thriller with Julia Roberts. Moved from 26 February 2027.", "Cinemas"),
    ("Spaceballs: The New One", "2027-04-23", "Amazon MGM", "comedy", "The Spaceballs sequel, with Mel Brooks back.", "Cinemas"),
    ("The Legend of Zelda", "2027-04-30", "Sony Pictures / Nintendo", "game", "Live-action Zelda from Wes Ball. Nintendo moved it a week earlier, from 7 May.", "Cinemas"),
    ("Star Wars: Starfighter", "2027-05-28", "Disney / Lucasfilm", "action", "Shawn Levy directs Ryan Gosling and Mia Goth in a new Star Wars story.", "Cinemas"),
    ("John Rambo", "2027-06-04", "Lionsgate", "action", "A Rambo prequel from Jalmari Helander, with Noah Centineo as the young Rambo.", "Cinemas"),
    ("How to Train Your Dragon 2", "2027-06-11", "Universal", "action", "The live-action sequel; Dean DeBlois and Mason Thames return.", "Cinemas"),
    ("Spider-Man: Beyond the Spider-Verse", "2027-06-18", "Sony Pictures Animation", "hero", "The end of Miles Morales' animated trilogy. Moved a week earlier, from 25 June.", "Cinemas"),
    ("Shrek 5", "2027-06-30", "Universal / DreamWorks", "anim", "Moved from December 2026. Zendaya joins the cast.", "Cinemas"),
    ("Man of Tomorrow", "2027-07-09", "Warner Bros. / DC Studios", "hero", "James Gunn's Superman sequel, with David Corenswet and Nicholas Hoult.", "Cinemas"),
    ("A Minecraft Movie Squared", "2027-07-23", "Warner Bros. / Legendary", "game", "The Minecraft sequel; Jared Hess directs, Jack Black returns.", "Cinemas"),
    ("A Quiet Place Part III", "2027-07-30", "Paramount", "horror", "John Krasinski's third film. Moved from 9 July so it does not open against Man of Tomorrow.", "Cinemas"),
    ("The Bluey Movie", "2027-08-06", "Disney / BBC Studios", "anim", "Bluey's first feature film, from creator Joe Brumm.", "Cinemas"),
    ("TMNT: Mutant Mayhem 2", "2027-08-13", "Paramount", "anim", "The animated Turtles sequel. Moved earlier, from 17 September.", "Cinemas"),
    ("The Simpsons Movie 2", "2027-09-03", "20th Century Studios", "anim", "The second Simpsons film, on Labor Day weekend. Moved from July 2027.", "Cinemas"),
    ("The Conjuring: First Communion", "2027-09-10", "Warner Bros. / New Line", "horror", "A new Conjuring story from Rodrigue Huart.", "Cinemas"),
    ("The Great Beyond", "2027-10-01", "Warner Bros.", "action", "J.J. Abrams' original film, now in the slot The Batman Part II left.", "Cinemas"),
    ("The Mummy: Book of the Dead", "2027-10-15", "Universal", "action", "Brendan Fraser and Rachel Weisz return. Moved earlier, from May 2028.", "Cinemas"),
    ("Treasure Island", "2027-11-11", "Sony Pictures", "action", "Ridley Scott directs Hugh Jackman.", "Cinemas"),
    ("Frozen III", "2027-11-24", "Disney", "anim", "Thanksgiving release; Kristen Bell and Idina Menzel return.", "Cinemas"),
    ("24 Jump Street", "2027-12-10", "Sony Pictures", "comedy", "Jonah Hill and Channing Tatum are back.", "Cinemas"),
    ("Avengers: Secret Wars", "2027-12-17", "Disney / Marvel Studios", "hero", "The Russo brothers' second Avengers film after Doomsday. Disney restated the date on 6 November 2026 after delay rumours.", "Cinemas"),
    ("The Lord of the Rings: The Hunt for Gollum", "2027-12-17", "Warner Bros.", "action", "Andy Serkis directs and plays Gollum. Moved from 2026.", "Cinemas"),
]
MV_OUT = [("The Batman Part II", "1 October 2027", "18 February 2028", "Warner Bros. moved it in July 2026 (Variety, Empire, Kotaku)."),
          ("Gremlins 3", "19 November 2027", "6 October 2028", "Warner Bros. moved it in September 2026 (Variety)."),
          ("Miami Vice '85", "6 August 2027", "19 May 2028", "Universal moved it (Variety).")]
MV_KIND = [("hero", "Marvel and DC"), ("anim", "Animated"), ("game", "Video game movies"), ("horror", "Horror"), ("action", "Action, fantasy and sci-fi"), ("comedy", "Comedy and thriller")]
_MVK = dict(MV_KIND)
def _mv_nice(d): return nice_date({"date": d, "window": ""})
def _mv_gcal(t, d):
    a = d.replace("-", ""); b = (datetime.date.fromisoformat(d) + datetime.timedelta(days=1)).isoformat().replace("-", "")
    return "https://calendar.google.com/calendar/render?action=TEMPLATE&text=" + _qp(t + " in cinemas") + f"&dates={a}/{b}&details=" + _qp("US release date via getdayonedrop.com/movies-2027")
def _mvrow(m):
    t, d, st, k, note, wh = m
    return (f'<div class="row" data-mk="{k}" data-mm="{int(d[5:7])}"><span><strong>{e(t)}</strong>'
            f'<br><span class="muted">{e(note)}</span><br><span class="muted">{e(st)} · {e(_MVK[k])} · {e(wh)} · '
            f'<a href="{e(_mv_gcal(t, d))}" rel="nofollow noopener" target="_blank">Add to Google Calendar</a></span></span><b>{e(_mv_nice(d))}</b></div>')
_mv_today = datetime.date.fromisoformat(UPDATED)
_mv_next = next((m for m in MOVIES if datetime.date.fromisoformat(m[1]) >= _mv_today), None)
_mv_by = {k: [m for m in MOVIES if m[3] == k] for k, _ in MV_KIND}
_mv_months = [(i + 1, [m for m in MOVIES if int(m[1][5:7]) == i + 1]) for i in range(12)]
_mv_busy = max(_mv_months, key=lambda x: len(x[1]))
# same-week crossover with the games board (big games with guide pages, +/- 3 days)
_mv_cross = []
for _m in MOVIES:
    _md = datetime.date.fromisoformat(_m[1])
    for _g in GAMES:
        if _g["page"] and _g["date"] and abs((datetime.date.fromisoformat(_g["date"]) - _md).days) <= 3:
            _mv_cross.append((_m, _g))
_mv_same = {}
for _m in MOVIES: _mv_same.setdefault(_m[1], []).append(_m[0])
_mv_clash = [(d, ts) for d, ts in _mv_same.items() if len(ts) > 1]
def _mvnames(k): return _and([f"{m[0]} ({_mv_nice(m[1])})" for m in _mv_by[k]])
_mv_quick = (f"We track {len(MOVIES)} big movies with a 2027 US release date. The first is {MOVIES[0][0]} on {_mv_nice(MOVIES[0][1])}; the biggest are "
             f"The Legend of Zelda (30 April), Star Wars: Starfighter (28 May), Spider-Man: Beyond the Spider-Verse (18 June), Shrek 5 (30 June), Man of Tomorrow (9 July), Frozen III (24 November) "
             f"and Avengers: Secret Wars (17 December). The Batman Part II is no longer a 2027 movie: it moved to 18 February 2028.")
_mvchips = ('<div class="chips" role="group" aria-label="Type"><button class="chip" type="button" data-mv-k="" aria-pressed="true">All movies</button>'
            + "".join(f'<button class="chip" type="button" data-mv-k="{k}" aria-pressed="false">{e(n)}</button>' for k, n in MV_KIND) + '</div>')
_mvmchips = ('<div class="chips" role="group" aria-label="Month" style="margin-top:8px"><button class="chip" type="button" data-mv-m="" aria-pressed="true">Any month</button>'
             + "".join(f'<button class="chip" type="button" data-mv-m="{i}" aria-pressed="false">{MONTHS[i-1][:3]}</button>' for i, ms in _mv_months if ms) + '</div>')
def _mvcd(m, lbl):
    return (f'<div class="cdw"><span class="lbl">{e(lbl)}</span><div class="cd" data-countdown="{m[1]}">'
            '<div class="cd-unit"><span class="flaps" data-u="0"></span><span>Days</span></div><div class="cd-unit"><span class="flaps" data-u="1"></span><span>Hrs</span></div>'
            '<div class="cd-unit"><span class="flaps" data-u="2"></span><span>Min</span></div><div class="cd-unit"><span class="flaps" data-u="3"></span><span>Sec</span></div></div></div>')
_mv_aw = next(m for m in MOVIES if m[0] == "Avengers: Secret Wars")
_mv_ze = next(m for m in MOVIES if m[0] == "The Legend of Zelda")
_mv_tbl = ('<div style="overflow-x:auto"><table class="gen-table" style="width:100%;border-collapse:collapse;font-size:.92rem"><thead><tr><th style="text-align:left;padding:6px">Month</th><th style="padding:6px">Movies</th><th style="text-align:left;padding:6px">Which ones</th></tr></thead><tbody>'
           + "".join(f'<tr><td style="padding:6px;border-top:1px solid var(--rule)">{MONTHS[i-1]} 2027</td><td style="padding:6px;text-align:center;border-top:1px solid var(--rule)" class="mono">{len(ms)}</td>'
                     f'<td style="padding:6px;border-top:1px solid var(--rule)">{e(", ".join(m[0] for m in ms) or "None dated yet")}</td></tr>' for i, ms in _mv_months)
           + '</tbody></table></div>')
_mv_body = (f'<header class="hero"><div class="wrap"><span class="kicker">Movies</span>'
            f'<h1>Upcoming movies 2027:<br><span class="amber">every big release date.</span></h1>'
            f'<p class="lead">Every big movie dated for 2027, from Sonic 4 and the live-action Zelda to Shrek 5, Man of Tomorrow and Avengers: Secret Wars, with filters, countdowns and calendar reminders.</p>'
            f'<p class="muted" style="margin:0">Last checked {e(UPDATED)} · {len(MOVIES)} movies · US cinema dates from the studios or two trade outlets</p></div></header>'
            f'<section><div class="wrap"><div class="out" style="margin-bottom:24px"><div class="row"><span><strong>Quick answer:</strong> {e(_mv_quick)}</span></div></div>'
            f'<div class="tool" id="mv-tool"><h2 style="font-size:1.5rem;margin-top:0">Which 2027 movies do I want to see?</h2>'
            f'<p class="muted">Pick a type and a month. The list below updates and your choice is remembered on this device. Every movie has an "Add to Google Calendar" link.</p>{_mvchips}{_mvmchips}'
            f'<p class="mono amber" id="mv-count" aria-live="polite" style="margin:12px 0 0">{len(MOVIES)} movies</p></div>'
            + (_mvcd(_mv_next, f"Next big movie: {_mv_next[0]}") if _mv_next else "") + '</div></section>'
            + AD.format("mv-mid") +
            f'<section><div class="wrap"><div class="sec-head"><h2>What movies are coming out in 2027?</h2><span class="muted">{len(MOVIES)} dated</span></div>'
            f'<p class="muted">In release order, US dates. UK and other dates are often the same week, sometimes a week or two apart.</p>'
            f'<div class="out" id="mv-list" style="margin-bottom:10px">{"".join(_mvrow(m) for m in MOVIES)}</div><p class="empty" id="mv-none" hidden>No dated 2027 movie matches that yet.</p>'
            f'<div class="sec-head" style="margin-top:28px"><h2>When does Avengers: Secret Wars come out?</h2></div>'
            f'<p>17 December 2027 in US cinemas. Marvel moved it there in 2025 along with Avengers: Doomsday (18 December 2026), and Disney restated the date on 6 November 2026 after rumours of another delay. It opens the same day as The Lord of the Rings: The Hunt for Gollum.</p>{_mvcd(_mv_aw, "Countdown to Avengers: Secret Wars")}'
            f'<div class="sec-head" style="margin-top:28px"><h2>Is The Batman Part II coming out in 2027?</h2></div>'
            f'<p>No. Warner Bros. moved The Batman Part II from 1 October 2027 to 18 February 2028 in July 2026, so it is now a 2028 movie. J.J. Abrams\' The Great Beyond took its October 2027 slot. These films also left 2027:</p>'
            f'<div class="out" style="margin-bottom:10px">' + "".join(f'<div class="row"><span><strong>{e(t)}</strong><br><span class="muted">Was {e(a)}. {e(why)}</span></span><b>{e(b)}</b></div>' for t, a, b, why in MV_OUT) + '</div>'
            f'<div class="sec-head" style="margin-top:28px"><h2>When does the Legend of Zelda movie come out?</h2></div>'
            f'<p>30 April 2027 worldwide. Nintendo and Sony first set 26 March 2027, then 7 May, and in May 2026 Shigeru Miyamoto said it would open a week sooner, on 30 April. Wes Ball directs, with Bo Bragason as Zelda and Benjamin Evan Ainsworth as Link. If you are planning a Zelda spring, see the <a href="{href("platforms/switch-2.html", 0)}">Switch 2 games of 2027</a>.</p>{_mvcd(_mv_ze, "Countdown to The Legend of Zelda movie")}'
            f'<div class="sec-head" style="margin-top:28px"><h2>What video game movies come out in 2027?</h2></div>'
            f'<p>Three are dated: {_mvnames("game")}. Fast X: Part 2 and other rumoured dates are left out until a studio confirms them.</p>'
            f'<div class="sec-head" style="margin-top:28px"><h2>What Marvel and DC movies come out in 2027?</h2></div>'
            f'<p>{_mvnames("hero")}. The Batman Part II is now February 2028.</p>'
            f'<div class="sec-head" style="margin-top:28px"><h2>What animated movies come out in 2027?</h2></div><p>{_mvnames("anim")}, plus the animated Spider-Man: Beyond the Spider-Verse (18 June).</p>'
            f'<div class="sec-head" style="margin-top:28px"><h2>What horror movies come out in 2027?</h2></div><p>{_mvnames("horror")}. For scary games, see <a href="{href("horror-games-2027.html", 0)}">horror games of 2027</a>.</p>'
            f'<div class="sec-head" style="margin-top:28px"><h2>Which 2027 movies open on the same day?</h2></div>'
            + ("".join(f'<p><strong>{e(_mv_nice(d))}:</strong> {e(_and(ts))}.</p>' for d, ts in _mv_clash) if _mv_clash else "<p>None so far.</p>")
            + f'<p>The busiest month is {MONTHS[_mv_busy[0]-1]} 2027 with {len(_mv_busy[1])} big releases.</p>{_mv_tbl}'
            f'<div class="sec-head" style="margin-top:28px"><h2>Which big games come out the same week as big 2027 movies?</h2></div>'
            f'<p class="muted">Movies within three days of a big game on our launch board, so you can plan the week.</p>'
            + ('<div class="out" style="margin-bottom:10px">' + "".join(f'<div class="row"><span><strong>{e(m[0])}</strong> ({e(_mv_nice(m[1]))}) and {_gname(g)} ({e(nice_date(g))})</span></div>' for m, g in _mv_cross) + '</div>' if _mv_cross else "<p>No big game lands within three days of a big movie yet.</p>")
            + f'<div class="sec-head" style="margin-top:28px"><h2>Related pages and tools</h2></div><ul>'
            f'<li><a href="{href("index.html", 0)}">2027 game release dates</a>: the live launch board</li>'
            f'<li><a href="{href("countdown.html", 0)}">Game release countdown</a> for any dated 2027 game</li>'
            f'<li><a href="{href("biggest-games-2027.html", 0)}">Biggest games of 2027</a></li>'
            f'<li><a href="{href("game-awards-2026.html", 0)}">The Game Awards 2026</a>: start time and nominees</li></ul></div></section>')
mv_faq = [("What movies are coming out in 2027?", f"We track {len(MOVIES)} dated big releases, including " + ", ".join(f"{m[0]} ({_mv_nice(m[1])})" for m in MOVIES[:10]) + " and more."),
          ("When does Avengers: Secret Wars come out?", "17 December 2027 in US cinemas. Disney restated the date in November 2026."),
          ("Is The Batman Part II delayed to 2028?", "Yes. Warner Bros. moved it from 1 October 2027 to 18 February 2028."),
          ("When does the Legend of Zelda movie come out?", "30 April 2027 worldwide, a week earlier than the 7 May date announced before."),
          ("When does Shrek 5 come out?", "30 June 2027 in US cinemas. It moved from December 2026."),
          ("When is Spider-Man: Beyond the Spider-Verse coming out?", "18 June 2027 in US cinemas."),
          ("When does Man of Tomorrow come out?", "9 July 2027. It is James Gunn's Superman sequel."),
          ("When does Frozen 3 come out?", "24 November 2027, Thanksgiving week in the US.")]
page("movies-2027.html", "Upcoming Movies 2027: Release Dates for Every Big Movie | DayOneDrop",
     f"Upcoming movies 2027 release dates: Zelda (30 April), Star Wars: Starfighter, Shrek 5, Man of Tomorrow, Frozen III and Avengers: Secret Wars (17 Dec). {len(MOVIES)} films.",
     _mv_body, 0, mv_faq, crumbs=[("Home", DOMAIN + "/"), ("Upcoming movies 2027", canon("movies-2027.html"))])


# ---------------- GAMES LIKE ELDEN RING (26 Nov 2026, demand: "games like elden ring", "upcoming soulslike games 2027") ----------------
# Out-now picks: platforms as sold today. Tarnished Edition date: Game Informer, VGC, Nintendo Life (4 Jun 2026). Memoria Wake: developer's Steam post via Gematsu (1 Jun 2026).
LIKE_ER = [
    # (title, platforms, why, platform tags, taste tags)
    ("Elden Ring Nightreign", "PS5, PS4, Xbox Series X|S, Xbox One, PC", "FromSoftware's 2025 spin-off: three players drop into a shrinking Limveld map and fight up to a night boss. Elden Ring's combat as a co-op roguelike.", "ps5 xbox pc ps4", "coop hard"),
    ("Dark Souls III", "PS4, Xbox One, PC (plays on PS5 and Xbox Series X|S)", "The game Elden Ring grew out of: tighter, linear levels and some of FromSoftware's best bosses.", "ps5 xbox pc ps4", "hard"),
    ("Dark Souls: Remastered", "Switch, PS4, Xbox One, PC", "Where it all started, with a world that loops back on itself. The easiest FromSoftware game to play on a Nintendo console.", "switch pc ps4 xbox", "hard open"),
    ("Sekiro: Shadows Die Twice", "PS4, Xbox One, PC (plays on PS5 and Xbox Series X|S)", "No builds, no co-op, just a sword, a grappling hook and parry-heavy duels. The hardest FromSoftware game for many players.", "ps5 xbox pc ps4", "hard fast"),
    ("Bloodborne", "PS4 (plays on PS5)", "Fast, aggressive gothic horror: you heal by hitting back. Still PlayStation only.", "ps5 ps4", "hard fast story"),
    ("Demon's Souls", "PS5", "Bluepoint's 2020 remake of the first Souls game. A good-looking PS5 showcase and a shorter run than Elden Ring.", "ps5", "hard"),
    ("Lies of P", "PS5, PS4, Xbox Series X|S, Xbox One, PC", "A dark take on Pinocchio with Bloodborne-style streets, a strong parry system and a clear story.", "ps5 xbox pc ps4", "hard story"),
    ("Black Myth: Wukong", "PS5, Xbox Series X|S, PC", "Journey to the West as an action game: big boss fights, transformations and no co-op. Less punishing than Elden Ring.", "ps5 xbox pc", "fast story"),
    ("Lords of the Fallen (2023)", "PS5, Xbox Series X|S, PC", "Two worlds at once, the living and the dead, and full co-op through the whole game. Its sequel is due in 2027.", "ps5 xbox pc", "coop open"),
    ("Wo Long: Fallen Dynasty", "PS5, PS4, Xbox Series X|S, Xbox One, PC", "Team Ninja's fast Three Kingdoms action RPG built on deflecting attacks. Wo Long 2 is dated for March 2027.", "ps5 xbox pc ps4", "fast coop"),
    ("Remnant II", "PS5, Xbox Series X|S, PC", "A soulslike with guns: hard bosses, random worlds and three-player co-op.", "ps5 xbox pc", "coop"),
    ("Hollow Knight: Silksong", "Switch 2, Switch, PS5, PS4, Xbox Series X|S, Xbox One, PC", "2D, but with the same tough bosses, hidden paths and lonely world. The best Souls fix on a Nintendo console.", "switch ps5 ps4 xbox pc", "hard open"),
]
_ER_LABEL = {"hard": "Tough bosses", "open": "Exploring", "story": "Strong story", "coop": "Co-op", "fast": "Fast combat"}
_er_rows = "".join(f'<div class="row" data-ep="{e(x[3])}" data-el="{e(x[4])}"><span><strong>{e(x[0])}</strong><br><span class="muted">{e(x[2])}</span><br><span class="muted">{e(x[1])}</span>'
                   f'<br><span class="muted mono" style="font-size:.78rem">{e(" · ".join(_ER_LABEL[k] for k in x[4].split()))}</span></span></div>' for x in LIKE_ER)
_er_chips = ('<div class="chips" role="group" aria-label="Platform"><button class="chip" type="button" data-er-p="" aria-pressed="true">Any platform</button>'
             + "".join(f'<button class="chip" type="button" data-er-p="{k}" aria-pressed="false">{l}</button>' for k, l in [("ps5", "PS5"), ("xbox", "Xbox"), ("pc", "PC"), ("switch", "Switch / Switch 2"), ("ps4", "PS4")]) + '</div>'
             '<div class="chips" role="group" aria-label="What you liked" style="margin-top:10px"><button class="chip" type="button" data-er-l="" aria-pressed="true">Anything</button>'
             + "".join(f'<button class="chip" type="button" data-er-l="{k}" aria-pressed="false">{e(l)}</button>' for k, l in _ER_LABEL.items()) + '</div>')
ER_SOON_SLUGS = ["wo-long-2", "no-rest-for-the-wicked", "lords-of-the-fallen-ii", "the-duskbloods"]
_er_soon = sorted([g for g in GAMES if g["slug"] in ER_SOON_SLUGS], key=lambda g: (g["month"] or 13, g["date"] or "9999"))
ER_EXTRA = [("Memoria Wake", "Team Crescendo", "A soulslike action adventure announced on Steam in June 2026.", "Xbox Series X|S, PC", "Early 2027")]
def _er_srow(g):
    return (f'<div class="row" data-slug="{e(g["slug"])}"><span><strong>{_gname(g)}</strong><br><span class="muted">{e(g.get("about") or "")}</span>'
            f'<br><span class="muted">{e(g.get("dev") or "Studio TBC")} · {e(", ".join(g["platforms"]))}</span></span><b>{e(nice_date(g))}</b></div>')
_er_first = next((g for g in _er_soon if g["date"]), None)
_er_dusk = next((g for g in GAMES if g["slug"] == "the-duskbloods"), None)
def _er_on(tag): return [x[0] for x in LIKE_ER if tag in x[3].split()]
_er_cd = (f'<div class="cdw"><span class="lbl">Countdown to {e(_er_first["title"])}</span><div class="cd" data-countdown="{_er_first["date"]}">'
          '<div class="cd-unit"><span class="flaps" data-u="0"></span><span>Days</span></div><div class="cd-unit"><span class="flaps" data-u="1"></span><span>Hrs</span></div>'
          '<div class="cd-unit"><span class="flaps" data-u="2"></span><span>Min</span></div><div class="cd-unit"><span class="flaps" data-u="3"></span><span>Sec</span></div></div></div>') if _er_first else ""
_er_quick = ("The best games like Elden Ring are FromSoftware's own Dark Souls III, Sekiro, Bloodborne and Elden Ring Nightreign, then Lies of P, Black Myth: Wukong and Lords of the Fallen. "
             f"The next soulslikes are {_and([g['title'] + ' (' + nice_date(g) + ')' for g in _er_soon])}. FromSoftware has not announced an Elden Ring 2.")
er_body = (f'<header class="hero"><div class="wrap"><span class="kicker">Games like Elden Ring</span>'
           f'<h1>Games like Elden Ring:<br><span class="amber">play now, and the 2027 soulslikes.</span></h1>'
           f'<p class="lead">Soulslike games you can play today on PS5, Xbox, PC and Switch 2, filtered by what you loved about Elden Ring, plus every soulslike with a 2027 date.</p>'
           f'<p class="muted" style="margin:0">Last checked {e(UPDATED)} · {len(LIKE_ER)} picks out now · {len(_er_soon) + len(ER_EXTRA)} coming in 2027</p></div></header>'
           f'<section><div class="wrap"><div class="out" style="margin-bottom:12px"><div class="row"><span><strong>Quick answer:</strong> {e(_er_quick)}</span></div></div>'
           f'<div class="tool" id="er-tool" style="margin-bottom:24px"><h2 style="font-size:1.5rem;margin-top:0">Which game like Elden Ring should I play?</h2>'
           f'<p class="muted">Pick your platform and what you liked most. Your choice is remembered on this device.</p>{_er_chips}'
           f'<p class="mono amber" id="er-count" aria-live="polite" style="margin:12px 0 0">{len(LIKE_ER)} games</p></div>'
           f'<div class="sec-head"><h2>What games are like Elden Ring?</h2><span class="muted">out now</span></div>'
           f'<div class="out" id="er-list" style="margin-bottom:10px">{_er_rows}</div><p class="empty" id="er-none" hidden>No pick matches both. Try "Anything".</p></div></section>'
           + AD.format("er-mid") +
           f'<section><div class="wrap"><div class="sec-head"><h2>What soulslike games are coming out in 2027?</h2><span class="muted">{len(_er_soon) + len(ER_EXTRA)}</span></div>'
           f'<div class="out" style="margin-bottom:10px">{"".join(_er_srow(g) for g in _er_soon)}'
           + "".join(f'<div class="row"><span><strong>{e(t)}</strong><br><span class="muted">{e(ab)}</span><br><span class="muted">{e(dv)} · {e(pl)}</span></span><b>{e(w)}</b></div>' for t, dv, ab, pl, w in ER_EXTRA)
           + f'</div>{_er_cd}'
           f'<div class="sec-head" style="margin-top:28px"><h2>Is there going to be an Elden Ring 2?</h2></div>'
           f'<p>Not announced. FromSoftware has not revealed an Elden Ring 2 or a new Elden Ring expansion beyond Shadow of the Erdtree and the Nightreign spin-off. Its next game is '
           + (f'{_gname(_er_dusk)}, an online action game for up to 8 players, coming only to Switch 2 ({e(nice_date(_er_dusk))}).' if _er_dusk else 'The Duskbloods on Switch 2.') + '</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>Can I play Elden Ring on Switch 2?</h2></div>'
           f'<p>Yes. Elden Ring: Tarnished Edition came to Switch 2 on 28 August 2026, after a delay from 2025. For more soulslikes on a Nintendo console, add Dark Souls: Remastered, Hollow Knight: Silksong and, in 2027, Lords of the Fallen II and The Duskbloods. See every <a href="{href("platforms/switch-2.html", 0)}">Switch 2 game of 2027</a>.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>What games are like Elden Ring on PS5?</h2></div><p>{e(_and(_er_on("ps5")))}. In 2027: {e(_and([g["title"] for g in _er_soon if "PS5" in g["platforms"]]))}.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>What games are like Elden Ring on Xbox and PC?</h2></div><p>Xbox: {e(_and(_er_on("xbox")))}. PC: {e(_and(_er_on("pc")))}.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>What is the hardest game like Elden Ring?</h2></div>'
           f'<p>Most players name Sekiro: Shadows Die Twice: there are no builds or summons to fall back on, so every boss is a straight duel. Bloodborne and Lies of P are close behind. If you want something gentler, Black Myth: Wukong and Lords of the Fallen (2023) give you more room for mistakes.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>Related pages and tools</h2></div><ul>'
           f'<li><a href="{href("games/lords-of-the-fallen-ii.html", 0)}">Lords of the Fallen 2 release date</a> and delay history</li>'
           f'<li><a href="{href("games/wo-long-2.html", 0)}">Wo Long 2 release date</a></li>'
           f'<li><a href="{href("rpgs-2027.html", 0)}">Every RPG of 2027</a></li>'
           f'<li><a href="{href("games-like-gta-6.html", 0)}">Games like GTA 6</a></li>'
           f'<li><a href="{href("countdown.html", 0)}">Game release countdown</a></li></ul></div></section>')
er_faq = [("What games are like Elden Ring?", "Dark Souls III, Sekiro, Bloodborne, Elden Ring Nightreign, Lies of P, Black Myth: Wukong, Lords of the Fallen, Wo Long: Fallen Dynasty, Remnant II and Hollow Knight: Silksong."),
          ("What soulslike games come out in 2027?", _and([g['title'] + ' (' + nice_date(g) + ')' for g in _er_soon] + [x[0] + ' (' + x[4] + ')' for x in ER_EXTRA]) + "."),
          ("Is Elden Ring 2 announced?", "No. FromSoftware's next game is The Duskbloods, a Switch 2 exclusive."),
          ("Is Elden Ring on Switch 2?", "Yes. Elden Ring: Tarnished Edition launched on Switch 2 on 28 August 2026."),
          ("When does Lords of the Fallen 2 come out?", "April 2027 on PS5, Xbox Series X|S, Switch 2 and PC. CI Games says the exact day is due in December 2026.")]
page("games-like-elden-ring.html", "Games Like Elden Ring: Best Soulslikes Now and in 2027 | DayOneDrop",
     "Games like Elden Ring on PS5, Xbox, PC and Switch 2: Lies of P, Sekiro, Wukong and more, plus 2027 soulslikes Wo Long 2, Lords of the Fallen II and The Duskbloods.",
     er_body, 0, er_faq, crumbs=[("Home", DOMAIN + "/"), ("2027 games by genre", canon("games-by-genre-2027.html")), ("Games like Elden Ring", canon("games-like-elden-ring.html"))])


# ---------------- SEO files ----------------
page("thanks.html", "Check your inbox | DayOneDrop", "Confirm your email to get the free 2027 release calendar.", NL_THANKS)
page("welcome.html", "Your 2027 release calendar | DayOneDrop", "Download your free 2027 game release calendar.", NL_WELCOME)

urls = ["index.html", "movies-2027.html", "games-like-elden-ring.html", "countdown.html", "games-without-release-date-2027.html", "steam-sale-dates.html", "nintendo-direct.html", "ps-plus-monthly-games.html", "epic-free-games.html", "after-gta-6.html", "games-like-gta-6.html", "delayed-games-2027.html", "release-clashes-2027.html", "exclusives-2027.html", "rpgs-2027.html", "game-pass-2027.html", "backlog-planner-2027.html", "biggest-games-2027.html", "game-awards-2026.html", "games-december-2026.html", "new-games-this-week.html", "last-gen-games-2027.html", "games-by-genre-2027.html", "horror-games-2027.html", "fighting-games-2027.html", "xbox-games-showcase-2027.html", "calendar.html", "later-2027.html", "games.html", "tools.html", "about.html", "privacy.html"] + ["games/" + g["slug"] + ".html" for g in featured] + plat_urls + month_urls
sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(
    f"  <url><loc>{canon(u)}</loc><lastmod>{UPDATED}</lastmod><changefreq>daily</changefreq><priority>{'1.0' if u == 'index.html' else '0.8'}</priority></url>\n" for u in urls) + "</urlset>\n"
(ROOT / "sitemap.xml").write_text(sm)
(ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nDisallow: /go/\n\nSitemap: {DOMAIN}/sitemap.xml\n")
if not (ROOT / "ads.txt").exists():
    (ROOT / "ads.txt").write_text("# Replace with the line AdSense gives you, e.g. google.com, pub-0000000000000000, DIRECT, f08c47fec0942fa0\n")
print("built", len(urls) + 1, "pages", "(preview)" if PREVIEW else "(live)")
write_redirects(ROOT)

# --- honest sitemap: every indexable page, lastmod only when content changes (seo_post.py, 26 Nov) ---
import subprocess as _sp, sys as _sys, pathlib as _pl
_sp.run([_sys.executable, str(_pl.Path(__file__).resolve().parent / "seo_post.py"), str(_pl.Path(__file__).resolve().parent), DOMAIN])
