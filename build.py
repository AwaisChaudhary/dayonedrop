#!/usr/bin/env python3
"""Builds DayOneDrop. Run `python3 build.py` for the live site (clean URLs) or `python3 build.py --preview` for local files."""
import json, html, pathlib, sys, hashlib, datetime

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
    return [m for m in range(1, 13) if sum(1 for g in GAMES if g["month"] == m) >= 3]


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
    (root / "_redirects").write_text(lines)


def page(file, title, desc, body, depth=0, faqs=None, crumbs=None, extra_ld=None):
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
<meta name="twitter:card" content="summary">
<meta name="theme-color" content="#0c0d10">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='6' fill='%230c0d10'/%3E%3Crect x='5' y='7' width='9' height='18' rx='2' fill='%2323272f'/%3E%3Crect x='18' y='7' width='9' height='18' rx='2' fill='%23ffc629'/%3E%3Crect x='4' y='15.5' width='24' height='1' fill='%23000'/%3E%3C/svg%3E">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;700;800;900&family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{asset("style.css", depth)}">
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
<div><strong>Site</strong><ul><li><a href="{href("after-gta-6.html", depth)}">What to play after GTA 6</a></li><li><a href="https://neoncoast.org" rel="noopener">GTA 6 map and guides (NeonCoast)</a></li><li><a href="{href("about.html", depth)}">About and contact</a></li><li><a href="{href("privacy.html", depth)}">Privacy policy</a></li></ul></div>
</div>
<p class="legal">DayOneDrop is an independent fan site and is not linked to any game publisher. Game names belong to their owners. Release dates can change; we update this site as soon as publishers announce changes. Last checked {e(UPDATED)}.</p>
</div></footer>
<script>window.DOD={json.dumps({"games": GAMES})};</script>
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
<section><div class="wrap">
<div class="sec-head"><h2>2027 departures</h2><p class="muted">Tap ☆ to save a game. Filter by your console.</p></div>
{board(0)}
<div class="btns" style="margin-top:14px"><button class="btn line sm" type="button" id="share-list">Share my list</button></div>
</div></section>
{AD.format("home-mid")}
<section><div class="wrap">
<div class="sec-head"><h2>Biggest launches</h2><p class="muted">Full guides for the games everyone is waiting for.</p></div>
<div class="grid">{"".join(pass_card(g, 0) for g in featured)}</div>
</div></section>'''
home_faq = [
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

cal = f'''<header class="hero"><div class="wrap"><span class="kicker">2027 calendar</span><h1>The 2027 game<br><span class="amber">release calendar.</span></h1>
<p class="lead">Every confirmed date, month by month. Highlighted days have a launch. Games with only a season or year are listed in their likely month.</p></div></header>
<section><div class="wrap"><div class="months">{"".join(month_html(m) for m in range(1, 13))}</div></div></section>
{AD.format("cal-mid")}
<section><div class="wrap"><div class="sec-head"><h2>Add launches to your calendar</h2><p class="muted">One tap, and your phone reminds you on launch day.</p></div>
<div class="out">{"".join(f'<div class="row"><span>{e(g["title"])} · <span class="muted">{e(nice_date(g))}</span></span><span class="btns"><a class="btn sm" href="{gcal(g)}" rel="nofollow noopener" target="_blank">Google Calendar</a><a class="btn line sm" href="{ics(g)}" download="{g["slug"]}.ics">Apple / Outlook</a></span></div>' for g in GAMES if g["date"])}</div></div></section>'''
cal_faq = [
    ("Which month has the most game releases in 2027?", "February 2027 is the busiest month so far, with several big launches within three weeks."),
    ("How do I get a reminder for a release date?", "Use the Google Calendar or Apple / Outlook buttons on this page. They add the launch day to your calendar for free."),
    ("Why do some games show TBC?", "Some publishers have only shared a season or a year. We add the exact day as soon as it's announced."),
]
page("calendar.html", "2027 Video Game Release Calendar, Month by Month | DayOneDrop",
     "The full 2027 video game release calendar, month by month. See every confirmed launch date and add games to Google, Apple or Outlook calendar in one tap.",
     cal, 0, cal_faq, crumbs=[("Home", DOMAIN + "/"), ("2027 Calendar", canon("calendar.html"))])

# ---------------- GAMES INDEX ----------------
others = [g for g in GAMES if not g["page"]]
gi = f'''<header class="hero"><div class="wrap"><span class="kicker">All games</span><h1>Every 2027 launch<br><span class="amber">we're tracking.</span></h1>
<p class="lead">Full guides for the biggest games, plus every other confirmed launch.</p></div></header>
<section><div class="wrap"><div class="grid">{"".join(pass_card(g, 0) for g in featured)}</div></div></section>
<section><div class="wrap"><div class="sec-head"><h2>More 2027 games</h2></div><div class="out">{"".join(f'<div class="row"><span><strong>{e(g["title"])}</strong><br><span class="muted">{e(g["about"])}</span></span><b>{e(nice_date(g))}</b></div>' for g in others)}</div></div></section>'''
page("games.html", "All 2027 Games With Release Dates | DayOneDrop",
     "Every 2027 game we track, with release dates, platforms and status. Guides for Fable, God of War Laufey, Final Fantasy VII Revelation, Exodus and more.",
     gi, 0, None, crumbs=[("Home", DOMAIN + "/"), ("All games", canon("games.html"))])

# ---------------- GAME PAGES ----------------
for g in featured:
    f = "games/" + g["slug"] + ".html"
    same_month = [x for x in GAMES if x["month"] == g["month"] and x["slug"] != g["slug"]]
    cd = ""
    if g["date"]:
        cd = f'''<div class="cdw"><span class="lbl">Countdown to launch</span><div class="cd" data-countdown="{g["date"]}">
<div class="cd-unit"><span class="flaps" data-u="0"></span><span>Days</span></div><div class="cd-unit"><span class="flaps" data-u="1"></span><span>Hrs</span></div>
<div class="cd-unit"><span class="flaps" data-u="2"></span><span>Min</span></div><div class="cd-unit"><span class="flaps" data-u="3"></span><span>Sec</span></div></div></div>'''
    acts = ""
    if g["date"]:
        acts += f'<a class="btn sm" href="{gcal(g)}" rel="nofollow noopener" target="_blank">Add to Google Calendar</a><a class="btn line sm" href="{ics(g)}" download="{g["slug"]}.ics">Apple / Outlook</a>'
    acts += f'<a class="btn sm" href="{go(amz_slug(g))}" {AFF_ATTR}>Pre-order on Amazon</a>'
    acts += f'<button class="btn line sm star" type="button" data-slug="{g["slug"]}" data-name="{e(g["title"])}" aria-pressed="false">☆</button><button class="btn line sm" type="button" data-copy-link>Copy link</button>'
    from urllib.parse import quote
    share = canon(f)
    shares = (f'<a class="btn line sm" href="https://www.reddit.com/submit?url={quote(share)}&title={quote(g["title"] + " release date and countdown")}" target="_blank" rel="noopener">Share on Reddit</a>'
              f'<a class="btn line sm" href="https://wa.me/?text={quote(g["title"] + " release date: " + share)}" target="_blank" rel="noopener">WhatsApp</a>'
              f'<a class="btn line sm" href="https://twitter.com/intent/tweet?text={quote(g["title"] + " launches " + nice_date(g))}&url={quote(share)}" target="_blank" rel="noopener">Post on X</a>')
    body = f'''<header class="hero"><div class="wrap"><span class="kicker">Release guide</span>
<div class="gp-head"><div><h1>{e(g["title"])}<br><span class="amber">release date</span></h1>
<p class="lead">{e(g["about"])}</p><p class="muted" style="margin:0">Last checked {e(UPDATED)}</p></div>
<div class="ticket">
<div class="ticket-row"><div><span class="lbl">Launch</span><span class="val">{e(nice_date(g))}</span></div><div><span class="lbl">Status</span>{status_html(g)}</div></div>
<div class="ticket-row"><div><span class="lbl">Platforms</span><span class="val">{e(plat_text(g))}</span></div><div><span class="lbl">Made by</span><span class="val">{e(g["dev"] or "TBC")}</span></div></div>
{cd}<div class="acts">{acts}</div>{AFF_NOTE}</div>
</div></div></header>
<section><div class="wrap cols">
<div><h2>What we know</h2><ul class="facts-list">{"".join(f"<li>{e(x)}</li>" for x in g["facts"])}</ul></div>
<div><h2>Release date history</h2><div class="hist">{"".join(f"<div><small>{e(h['when'])}</small>{e(h['text'])}</div>" for h in g["history"])}</div>
<h3 style="margin-top:26px">Tell your friends</h3><div class="btns">{shares}</div></div>
</div></section>
{AD.format(g["slug"] + "-mid")}
<section><div class="wrap"><div class="sec-head"><h2>Also launching in {MONTHS[g["month"] - 1]}</h2><a class="btn line sm" href="{href("calendar.html", 1)}">Full calendar</a></div>
<div class="out">{"".join(f'<div class="row"><span>{e(x["title"])}</span><b>{e(nice_date(x))}</b></div>' for x in same_month) or '<div class="empty">No other launches that month yet.</div>'}</div></div></section>'''
    faqs = [
        (f"When does {g['title']} come out?", f"{g['title']} is set for {nice_date(g)}." + (" It was delayed once, so we track any further changes." if g["status"] == "delayed" else " We update this page if the date changes.")),
        (f"What platforms is {g['title']} on?", (f"It's confirmed for {plat_text(g)}." if g["platforms"] else "The full platform list hasn't been confirmed yet. We add it as soon as it is.")),
        (f"Who is making {g['title']}?", f"{g['title']} is made by {g['dev']}." if g["dev"] else "The developer will be listed once confirmed."),
        (f"How can I get a reminder for {g['title']}?", "Use the Add to Google Calendar or Apple / Outlook button on this page. Your calendar will remind you on launch day."),
    ]
    short = g["title"].split(":")[0]
    page(f, f"{g['title']} Release Date, Platforms and Countdown | DayOneDrop"[:90],
         f"{g['title']} launches {nice_date(g)}. Platforms, developer, release date history and a live countdown, plus one-tap calendar reminders."[:160],
         body, 1, faqs, crumbs=[("Home", DOMAIN + "/"), ("All games", canon("games.html")), (g["title"], canon(f))])

# ---------------- PLATFORM PAGES ----------------
PLAT_PAGES = PLAT_PAGES_FOOT
plat_urls = []


def plat_row(g, depth, plat):
    t = f'<a href="{href("games/" + g["slug"] + ".html", depth)}">{e(g["title"])}</a>' if g["page"] else e(g["title"])
    others = [x for x in g["platforms"] if x != plat]
    also = ("Only on " + plat) if not others else ("Also on " + ", ".join(others))
    genre = (e(g["genre"]) + " · ") if g["genre"] else ""
    return f'<div class="row"><span><strong>{t}</strong><br><span class="muted">{genre}{e(also)}</span></span><b>{e(nice_date(g))}</b></div>'


for plat, slug, long in PLAT_PAGES:
    f = "platforms/" + slug + ".html"
    plat_urls.append(f)
    games = [g for g in GAMES if plat in g["platforms"]]
    dated = [g for g in games if g["date"]]
    excl = [g for g in games if g["platforms"] == [plat]]
    by_month = {}
    for g in games:
        by_month.setdefault(g["month"] if g["date"] else 13, []).append(g)
    blocks = ""
    for m, gs in sorted(by_month.items()):
        head = "Date to be announced" if m == 13 else MONTHS[m - 1] + " 2027"
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
            f'<section><div class="wrap">{blocks}'
            f'<p class="muted">Star games on the <a href="{href("index.html", 1)}#board">departures board</a> to build your launch list, '
            f'and every guide has one-tap calendar reminders.</p></div></section>')
    first = dated[0] if dated else None
    if excl:
        ex = ", ".join(g["title"] for g in excl) + (" is" if len(excl) == 1 else " are") + f" only confirmed for {long} so far."
    else:
        ex = f"None of the 2027 games we track are {long} exclusives right now."
    faqs = [
        (f"How many {long} games are coming in 2027?", f"We track {len(games)} confirmed {long} games for 2027 so far. This list grows as publishers announce dates and platforms."),
        (f"What is the next big {long} game in 2027?", (f"{first['title']} is the first dated {long} game on our list, launching {nice_date(first)}." if first else "No exact dates are confirmed yet.")),
        (f"Which 2027 games are only on {long}?", ex),
    ]
    page(f, f"Every {long} Game Coming in 2027 (Release Dates) | DayOneDrop"[:90],
         f"All {len(games)} confirmed {long} games launching in 2027, sorted by release date, with countdowns, delays and links to full guides."[:160],
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
        return f'<div class="row"><span><strong>{t}</strong>{flag}<br><span class="muted">{genre}{e(plats)}</span></span><b>{e(nice_date(g))}</b></div>'
    weeks = {}
    for g in dated:
        d = datetime.date.fromisoformat(g["date"])
        weeks.setdefault(d.isocalendar()[1], []).append(g)
    busiest = max(weeks.values(), key=len) if weeks else []
    blocks = f'<div class="sec-head"><h2>Every {mname} 2027 release date</h2><span class="muted">{len(dated)} dated</span></div><div class="out" style="margin-bottom:28px">{"".join(mrow(g) for g in dated) or "<div class=empty>No exact dates yet.</div>"}</div>'
    if loose:
        blocks += f'<div class="sec-head"><h2>Expected in {mname}, no exact date</h2><span class="muted">{len(loose)}</span></div><div class="out" style="margin-bottom:28px">{"".join(mrow(g) for g in loose)}</div>'
    pc = {pl: sum(1 for g in games if pl in g["platforms"]) for pl, _, _ in PLAT_PAGES}
    platline = " · ".join(f'<a href="{href("platforms/" + s2 + ".html", 1)}">{e(l2)}</a>: {pc[p2]}' for p2, s2, l2 in PLAT_PAGES)
    prev_next = []
    ml = month_pages_list(); i = ml.index(m)
    if i > 0: prev_next.append(f'<a class="btn line sm" href="{href("months/" + MONTH_SLUGS[ml[i-1] - 1] + ".html", 1)}">← {MONTHS[ml[i-1] - 1]} 2027</a>')
    if i < len(ml) - 1: prev_next.append(f'<a class="btn line sm" href="{href("months/" + MONTH_SLUGS[ml[i+1] - 1] + ".html", 1)}">{MONTHS[ml[i+1] - 1]} 2027 →</a>')
    body = (f'<header class="hero"><div class="wrap"><span class="kicker">{mname} 2027</span>'
            f'<h1>{mname} 2027 game releases<br><span class="amber">{len(games)} games on the board.</span></h1>'
            f'<p class="lead">Every video game launching in {mname} 2027 on PS5, Xbox Series X|S, PC and Switch 2, in date order. '
            f'Each date is checked against the publisher or two trusted outlets, and we mark delays as they happen.</p>'
            f'<p class="muted" style="margin:0">Last checked {e(UPDATED)} · Games per console: {platline}</p></div></header>'
            f'<section><div class="wrap">{blocks}'
            f'<p class="muted">Add any date to your calendar from the <a href="{href("calendar.html", 1)}">2027 calendar</a>, or star games on the <a href="{href("index.html", 1)}#board">departures board</a>.</p>'
            f'<div class="btns" style="display:flex;gap:10px;flex-wrap:wrap">{"".join(prev_next)}</div></div></section>')
    first = dated[0] if dated else None
    big_week = (f"The busiest week has {len(busiest)} launches: " + ", ".join(g["title"] for g in busiest) + ".") if len(busiest) > 1 else f"Launches are spread across {mname}."
    faqs = [
        (f"What games come out in {mname} 2027?", f"{len(games)} games are on our list for {mname} 2027, including " + ", ".join(g["title"] for g in games[:5]) + ". The full list with dates and consoles is above."),
        (f"What is the first game out in {mname} 2027?", (f"{first['title']}, on {nice_date(first)}." if first else "No exact dates are confirmed yet.")),
        (f"What is the busiest week of {mname} 2027?", big_week),
    ]
    page(f, f"{mname} 2027 Game Releases: Every Date ({len(games)} Games) | DayOneDrop"[:90],
         f"All {len(games)} video games releasing in {mname} 2027 on PS5, Xbox, PC and Switch 2, in date order with platforms and delays. Checked {UPDATED}."[:160],
         body, 1, faqs, crumbs=[("Home", DOMAIN + "/"), ("2027 calendar", canon("calendar.html")), (f"{mname} 2027", canon(f))])

# ---------------- TOOLS ----------------
plat_links0 = " · ".join(f'<a href="{href("platforms/" + s2 + ".html", 0)}">{e(l2)} games</a>' for p2, s2, l2 in PLAT_PAGES)
tools = f'''<header class="hero"><div class="wrap"><span class="kicker">Tools</span><h1>Plan your<br><span class="amber">2027 gaming year.</span></h1>
<p class="lead">Free tools to see what's coming to your console, keep track of the games you want, and spot the busiest months.</p>
<p class="muted" style="margin:0">Full lists: {plat_links0}</p></div></header>
<section><div class="wrap grid" style="grid-template-columns:repeat(auto-fit,minmax(320px,1fr))">
<div class="tool"><h2 style="font-size:1.5rem">What's coming to my console?</h2><label for="console-pick">Your console</label>
<select id="console-pick">{"".join(f'<option>{e(p)}</option>' for p in PLATS)}</select><div class="out" id="console-out"></div></div>
<div class="tool"><h2 style="font-size:1.5rem">My launch list</h2><p class="muted">Games you've starred, with days left. Saved on this device.</p><div class="out" id="watch-out"></div>
<div class="btns" style="margin-top:12px"><a class="btn sm" href="{href("index.html", 0)}#board">Add games</a><button class="btn line sm" type="button" id="share-list">Share my list</button></div></div>
<div class="tool"><h2 style="font-size:1.5rem">Busiest months of 2027</h2><p class="muted">Number of tracked launches each month.</p><div id="month-load"></div></div>
</div></section>'''
sw2 = [g["title"] for g in GAMES if "Switch 2" in g["platforms"]]
both = [g["title"] for g in GAMES if "PS5" in g["platforms"] and "Xbox Series X|S" in g["platforms"]]
tools_faq = [
    ("Which 2027 games are coming to Switch 2?", f"{len(sw2)} tracked 2027 games are confirmed for Switch 2, including {', '.join(sw2[:4])}. See the full Switch 2 list or use the console tool above."),
    ("Which 2027 games are on PS5 and Xbox?", f"{len(both)} tracked games are confirmed for both, including {', '.join(both[:4])}. The platform pages list them all."),
    ("Is my launch list saved?", "Yes, on this device and browser. Use Share my list to send it to a friend or open it on another device."),
]
page("tools.html", "2027 Game Release Tools: Console Lineup and Launch List | DayOneDrop",
     "Free 2027 gaming tools: see every game coming to PS5, Xbox, PC or Switch 2, build a launch list with countdowns, and find the busiest release months.",
     tools, 0, tools_faq, crumbs=[("Home", DOMAIN + "/"), ("Tools", canon("tools.html"))])


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
              f'. The busiest stretch is February 2027.</span></div></div>'
              f'<div class="sec-head"><h2>The next big games, in date order</h2><span class="muted">{len(_picks)} picks</span></div>'
              f'<div class="out" style="margin-bottom:28px">{"".join(_arow(g, w) for g, w in _picks)}</div>'
              f'<div class="sec-head"><h2>Still playing GTA 6?</h2></div>'
              f'<p>Our sister site <a href="https://neoncoast.org/map" rel="noopener">NeonCoast</a> has an interactive GTA 6 map, a mission tracker, '
              f'every cheat code and a "Can my PC run GTA 6?" checker. There is no GTA 6 PC release date yet.</p>'
              f'<p class="muted">See every 2027 date on the <a href="{href("calendar.html", 0)}">2027 calendar</a> or star games on the <a href="{href("index.html", 0)}#board">departures board</a> to get countdowns.</p></div></section>')
after_faq = [
    ("What should I play after GTA 6?", "If you liked the crime story, look at Stranger Than Heaven from the makers of Like a Dragon. For open-world driving, Forza Horizon 6 comes to PS5. For a huge world full of choices, Fable. The full list with dates is above."),
    ("What is the next big game after GTA 6?", (f"{_first['title']}, on {nice_date(_first)}, is the first big release on our list." if _first else "See the list above for dates.")),
    ("Is GTA 6 coming to PC?", "Not yet. Rockstar has not announced a PC version or date. GTA 6 launched on PS5 and Xbox Series X|S on 19 November 2026."),
]
page("after-gta-6.html", "What to Play After GTA 6: The Biggest Games of 2027 | DayOneDrop",
     "Finished GTA 6? The biggest confirmed games coming next, in release order: Stranger Than Heaven, Forza Horizon 6, Fable, Final Fantasy VII Revelation and more.",
     after_body, 0, after_faq, crumbs=[("Home", DOMAIN + "/"), ("After GTA 6", canon("after-gta-6.html"))])

# ---------------- ABOUT / PRIVACY / 404 ----------------
page("about.html", "About DayOneDrop", "About DayOneDrop, an independent tracker of 2027 game release dates, and how to contact us.",
     '''<section><div class="wrap" style="max-width:760px"><h1>About <span class="amber">DayOneDrop</span></h1>
<p>DayOneDrop tracks the release dates of the biggest games of 2027 in one simple board, with countdowns, delay tracking and calendar reminders.</p>
<h2>How we check dates</h2><p>We only list a date when publishers or at least two trusted gaming news sites confirm it. Games with only a season or year are marked as scheduled, and delays are marked clearly.</p>
<h2>Contact</h2><p>Spotted a wrong date? Email <strong>[your email address]</strong>.</p></div></section>''')
page("privacy.html", "Privacy Policy | DayOneDrop", "DayOneDrop privacy policy covering cookies, Google AdSense, Google Analytics and affiliate links.",
     f'''<section><div class="wrap" style="max-width:760px"><h1>Privacy policy</h1><p>Last updated: {e(UPDATED)}.</p>
<h2>What we collect</h2><p>Your launch list is saved only in your own browser. If you join our email list, we keep your email address with our email provider, Kit (kit.com), to send you the calendar and our updates. Every email has an unsubscribe link, and you can ask us to delete your address at any time.</p>
<h2>Analytics</h2><p>We use Google Analytics to count visits and see which pages are popular. It uses cookies and collects information like pages viewed, approximate location and device type.</p>
<h2>Advertising</h2><p>This site uses Google AdSense. Google and its partners use cookies to show ads based on your visits to this and other websites. You can turn off personalised ads at <a href="https://adssettings.google.com">Google Ads Settings</a>. Learn more at <a href="https://policies.google.com/technologies/partner-sites">policies.google.com/technologies/partner-sites</a>.</p>
<h2>Affiliate links</h2><p>Some links may be affiliate links. If you buy through them, we may earn a small fee at no extra cost to you. As an Amazon Associate we earn from qualifying purchases.</p>
<h2>Contact</h2><p>Email <strong>[your email address]</strong>.</p></div></section>''')
page("404.html", "Page not found | DayOneDrop", "This page has moved or doesn't exist.",
     f'<section><div class="wrap"><h1>Flight <span class="amber">cancelled.</span></h1><p class="lead">This page doesn\'t exist. Head back to the departures board.</p><a class="btn" href="{href("index.html", 0)}">Go to the board</a></div></section>')

# ---------------- SEO files ----------------
page("thanks.html", "Check your inbox | DayOneDrop", "Confirm your email to get the free 2027 release calendar.", NL_THANKS)
page("welcome.html", "Your 2027 release calendar | DayOneDrop", "Download your free 2027 game release calendar.", NL_WELCOME)

urls = ["index.html", "after-gta-6.html", "calendar.html", "games.html", "tools.html", "about.html", "privacy.html"] + ["games/" + g["slug"] + ".html" for g in featured] + plat_urls + month_urls
sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(
    f"  <url><loc>{canon(u)}</loc><lastmod>{UPDATED}</lastmod><changefreq>daily</changefreq><priority>{'1.0' if u == 'index.html' else '0.8'}</priority></url>\n" for u in urls) + "</urlset>\n"
(ROOT / "sitemap.xml").write_text(sm)
(ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nDisallow: /go/\n\nSitemap: {DOMAIN}/sitemap.xml\n")
if not (ROOT / "ads.txt").exists():
    (ROOT / "ads.txt").write_text("# Replace with the line AdSense gives you, e.g. google.com, pub-0000000000000000, DIRECT, f08c47fec0942fa0\n")
print("built", len(urls) + 1, "pages", "(preview)" if PREVIEW else "(live)")
write_redirects(ROOT)
