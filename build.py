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
_RM_KIND = {"danganronpa-2x2": "Remake", "terranigma": "Re-release", "fate-extra-record": "Remake", "romancing-saga-3-destinies-united": "Remake",
            "tomb-raider-legacy-of-atlantis": "Remake", "astonishia-story": "Remake", "persona-4-revival": "Remake", "psikyo-memories": "Collection",
            "hyrule-warriors-age-of-calamity-definitive-edition": "Enhanced edition", "final-fantasy-vii-revelation": "Remake (part 3)",
            "resident-evil-veronica": "Remake", "toshinden-collection": "Collection", "hitman-classic-trilogy-remastered": "Remaster",
            "frostpunk-1886": "Remake", "professor-layton-and-the-curious-village-remake": "Remake", "heroes-of-might-and-magic-iii-remake": "Remake"}
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
    if len(t) > 60:
        t = f"{g['title']} Release Date: {_us_date(g)}"
    if len(t) > 60:
        t = f"{g['title']} Release Date"
    return t


def _ctr_desc(g):
    lead = (f"{g['title']} comes out {nice_date(g)}" + (f" on {plat_text(g)}" if g.get("platforms") else "") + ".")
    # SEO audit 27 Nov 2026: descriptions aim for 120-160 chars, cut only at sentence ends.
    tails = [" Delayed once: see the full date history." if g["status"] == "delayed" else " Live countdown, date history and a free calendar reminder."]
    if g["status"] == "delayed":
        tails.append(" Live countdown and a free calendar reminder.")
    if g.get("dev"):
        tails.append(f" Made by {g['dev']}.")
    tails += [" Every date is checked against two official sources.", " Updated the day anything changes."]
    out = lead
    for t in tails:
        if len(out + t) <= 160:
            out += t
        if len(out) >= 120:
            break
    return out

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
    # SEO audit 27 Nov 2026: keep titles within 60 chars; drop the brand suffix when it would push past that.
    if len(title) > 60 and title.endswith(" | DayOneDrop"):
        title = title[:-len(" | DayOneDrop")]
    if file not in NOINDEX and file not in ("404.html",) and not crumbs:
        crumbs = [("Home", DOMAIN + "/"), (title.split(":")[0].split(" | ")[0], canon(file))] if file != "index.html" else None
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
<div><strong>Site</strong><ul><li><a href="{href("new-games-this-week.html", depth)}">New games this week</a></li><li><a href="{href("later-2027.html", depth)}">Games later in 2027 (May–Dec)</a></li><li><a href="{href("games-without-release-date-2027.html", depth)}">2027 games with no release date</a></li><li><a href="{href("countdown.html", depth)}">Game release countdown</a></li><li><a href="{href("games-december-2026.html", depth)}">Games coming out in December 2026</a></li><li><a href="{href("biggest-games-2027.html", depth)}">Biggest games of 2027</a></li><li><a href="{href("after-gta-6.html", depth)}">What to play after GTA 6</a></li><li><a href="{href("games-like-gta-6.html", depth)}">Games like GTA 6</a></li><li><a href="{href("gta-6-pc-release-date.html", depth)}">GTA 6 PC release date</a></li><li><a href="{href("games-like-elden-ring.html", depth)}">Games like Elden Ring</a></li><li><a href="{href("games-like-hollow-knight.html", depth)}">Games like Hollow Knight</a></li><li><a href="{href("games-like-zelda.html", depth)}">Games like Zelda</a></li><li><a href="{href("games-like-stardew-valley.html", depth)}">Games like Stardew Valley</a></li><li><a href="{href("games-like-pokemon.html", depth)}">Games like Pokémon</a></li><li><a href="{href("games-like-minecraft.html", depth)}">Games like Minecraft</a></li><li><a href="{href("games-like-animal-crossing.html", depth)}">Games like Animal Crossing</a></li><li><a href="{href("games-like-fortnite.html", depth)}">Games like Fortnite</a></li><li><a href="{href("games-like-baldurs-gate-3.html", depth)}">Games like Baldur's Gate 3</a></li><li><a href="{href("games-like-palworld.html", depth)}">Games like Palworld</a></li><li><a href="{href("games-like-skyrim.html", depth)}">Games like Skyrim</a></li><li><a href="{href("games-like-hades.html", depth)}">Games like Hades</a></li><li><a href="{href("games-like-the-witcher-3.html", depth)}">Games like The Witcher 3</a></li><li><a href="{href("games-like-red-dead-redemption-2.html", depth)}">Games like Red Dead Redemption 2</a></li><li><a href="{href("games-like-cyberpunk-2077.html", depth)}">Games like Cyberpunk 2077</a></li><li><a href="{href("games-like-persona.html", depth)}">Games like Persona 5</a></li><li><a href="{href("games-like-final-fantasy.html", depth)}">Games like Final Fantasy</a></li><li><a href="{href("games-like-resident-evil.html", depth)}">Games like Resident Evil</a></li><li><a href="{href("games-like-silent-hill.html", depth)}">Games like Silent Hill</a></li><li><a href="{href("games-like-mass-effect.html", depth)}">Games like Mass Effect</a></li><li><a href="{href("games-like-god-of-war.html", depth)}">Games like God of War</a></li><li><a href="{href("games-like-ghost-of-tsushima.html", depth)}">Games like Ghost of Tsushima</a></li><li><a href="{href("games-like-monster-hunter.html", depth)}">Games like Monster Hunter</a></li><li><a href="{href("games-like-assassins-creed.html", depth)}">Games like Assassin's Creed</a></li><li><a href="{href("games-like-hitman.html", depth)}">Games like Hitman</a></li><li><a href="{href("games/monster-hunter-wilds-ascendance.html", depth)}">Monster Hunter Wilds: Ascendance</a></li><li><a href="{href("games/game-of-thrones-war-for-westeros.html", depth)}">Game of Thrones: War for Westeros</a></li><li><a href="{href("delayed-games-2027.html", depth)}">Delayed games of 2027</a></li><li><a href="{href("release-clashes-2027.html", depth)}">2027 release clashes</a></li><li><a href="{href("exclusives-2027.html", depth)}">2027 console exclusives</a></li><li><a href="{href("rpgs-2027.html", depth)}">Every RPG of 2027</a></li><li><a href="{href("games-by-genre-2027.html", depth)}">2027 games by genre</a></li><li><a href="{href("horror-games-2027.html", depth)}">Horror games of 2027</a></li><li><a href="{href("fighting-games-2027.html", depth)}">Fighting games of 2027</a></li><li><a href="{href("strategy-games-2027.html", depth)}">Strategy games of 2027</a></li><li><a href="{href("shooter-games-2027.html", depth)}">Shooter games of 2027</a></li><li><a href="{href("games-2028.html", depth)}">Games coming out in 2028</a></li><li><a href="{href("remakes-2027.html", depth)}">Game remakes of 2027</a></li><li><a href="{href("dlc-2027.html", depth)}">DLC and expansions 2027</a></li><li><a href="{href("game-awards-2026.html", depth)}">Game Awards 2026: 2027 nominees</a></li><li><a href="{href("games/resident-evil-veronica.html", depth)}">Resident Evil Veronica</a></li><li><a href="{href("games/kirby-and-the-world-beyond.html", depth)}">Kirby and the World Beyond</a></li><li><a href="{href("games/xenoblade-genesis.html", depth)}">Xenoblade Genesis</a></li><li><a href="{href("games/the-duskbloods.html", depth)}">The Duskbloods</a></li><li><a href="{href("games/state-of-decay-3.html", depth)}">State of Decay 3</a></li><li><a href="{href("games/lords-of-the-fallen-ii.html", depth)}">Lords of the Fallen 2</a></li><li><a href="{href("games/squadron-42.html", depth)}">Squadron 42</a></li><li><a href="{href("games/ananta.html", depth)}">Ananta (free-to-play)</a></li><li><a href="{href("games/titan-quest-ii.html", depth)}">Titan Quest II</a></li><li><a href="{href("games/warhammer-40-000-dark-heresy.html", depth)}">Warhammer 40K: Dark Heresy</a></li><li><a href="{href("game-pass-2027.html", depth)}">Xbox Game Pass 2027</a></li><li><a href="{href("ps-plus-monthly-games.html", depth)}">PS Plus monthly games</a></li><li><a href="{href("epic-free-games.html", depth)}">Epic free games this week</a></li><li><a href="{href("steam-sale-dates.html", depth)}">Steam sale dates 2026-2027</a></li><li><a href="{href("black-friday-game-sales-2026.html", depth)}">Black Friday 2026 game sales</a></li><li><a href="{href("movies-2027.html", depth)}">Upcoming movies 2027</a></li><li><a href="{href("new-tv-shows-december-2026.html", depth)}">New TV shows December 2026</a></li><li><a href="{href("new-tv-shows-january-2027.html", depth)}">New TV shows January 2027</a></li><li><a href="{href("movies-december-2026.html", depth)}">Movies coming out in December 2026</a></li><li><a href="{href("winter-2027-anime.html", depth)}">Winter 2027 anime</a></li><li><a href="{href("movies-january-2027.html", depth)}">Movies coming out in January 2027</a></li><li><a href="{href("nintendo-direct.html", depth)}">Next Nintendo Direct</a></li><li><a href="{href("xbox-games-showcase-2027.html", depth)}">Xbox Games Showcase 2027</a></li><li><a href="{href("backlog-planner-2027.html", depth)}">2027 backlog planner</a></li><li><a href="{href("last-gen-games-2027.html", depth)}">2027 games on PS4 and Switch 1</a></li><li><a href="{href("games/hyrule-warriors-age-of-calamity-definitive-edition.html", depth)}">Hyrule Warriors: Age of Calamity DE</a></li><li><a href="{href("games/final-fantasy-xiv-evercold.html", depth)}">FFXIV Evercold</a></li><li><a href="{href("games/spyro-a-realm-beyond.html", depth)}">Spyro: A Realm Beyond</a></li><li><a href="{href("games/007-first-light.html", depth)}">007 First Light on Switch 2</a></li><li><a href="{href("games/kingdom-hearts-iv.html", depth)}">Kingdom Hearts 4</a></li><li><a href="{href("games/danganronpa-2x2.html", depth)}">Danganronpa 2x2</a></li><li><a href="{href("games/pokemon-winds-and-waves.html", depth)}">Pokémon Winds and Waves</a></li><li><a href="{href("games/stranger-than-heaven.html", depth)}">Stranger Than Heaven</a></li><li><a href="https://neoncoast.org" rel="noopener">GTA 6 map and guides (NeonCoast)</a></li><li><a href="{href("about.html", depth)}">About and contact</a></li><li><a href="{href("privacy.html", depth)}">Privacy policy</a></li></ul></div>
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
GP_TRACKED_ALL = {"stranger-than-heaven", "persona-4-revival", "fable", "wo-long-2", "spyro-a-realm-beyond", "the-expanse-osiris-reborn", "state-of-decay-3", "at-fates-end", "clockwork-revolution"}
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
    if g["slug"] in ("metroid-ravenous", "bloodstained-the-scarlet-engagement", "blighted", "mariachi-legends"): rel.insert(1, ("games-like-hollow-knight.html", "Games like Hollow Knight and every 2027 metroidvania"))
    if g["slug"] in ("witchbrook", "grave-seasons", "emberville", "atelier-karia", "neverway"): rel.insert(1, ("games-like-stardew-valley.html", "Games like Stardew Valley and every 2027 cozy game"))
    if g["slug"] in ("pokemon-winds-and-waves", "cassette-beasts-2002", "honkai-nexus-anima"): rel.insert(1, ("games-like-pokemon.html", "Games like Pokémon and every 2027 monster tamer"))
    if g["slug"] in ("outward-2", "tropico-7", "into-the-dead-our-darkest-days", "state-of-decay-3"): rel.insert(1, ("games-like-minecraft.html", "Games like Minecraft and 2027 survival games"))
    if g["slug"] in ("hyrule-warriors-age-of-calamity-definitive-edition", "kirby-and-the-world-beyond", "xenoblade-genesis", "fable", "terranigma", "demi-and-the-fractured-dream"): rel.insert(1, ("games-like-zelda.html", "Games like Zelda, and Zelda in 2027"))
    if g["slug"] in ("warhammer-40-000-dark-heresy", "shadow-of-the-road", "exodus"): rel.insert(1, ("games-like-baldurs-gate-3.html", "Games like Baldur's Gate 3 and the 2027 CRPGs"))
    if g["slug"] in ("fable", "exodus", "the-expanse-osiris-reborn"): rel.insert(1, ("games-like-skyrim.html", "Games like Skyrim and the 2027 open-world RPGs"))
    if g["slug"] in ("the-witcher-3-songs-of-the-past", "fable", "exodus", "lords-of-the-fallen-ii"): rel.insert(1, ("games-like-the-witcher-3.html", "Games like The Witcher 3, Songs of the Past and The Witcher 4 date"))
    if g["slug"] in ("persona-4-revival", "fate-extra-record", "danganronpa-2x2", "eternal-anima", "romancing-saga-3-destinies-united"): rel.insert(1, ("games-like-persona.html", "Games like Persona 5 and every 2027 JRPG"))
    if g["slug"] in ("exodus", "metro-2039", "the-expanse-osiris-reborn", "squadron-42", "ontos"): rel.insert(1, ("games-like-cyberpunk-2077.html", "Games like Cyberpunk 2077 and 2027 sci-fi games"))
    if g["slug"] in ("resident-evil-veronica", "until-dawn-2", "brokenlore-ascend", "trainwatch", "baptiste", "psycho-dead", "becrowned"): rel.insert(1, ("games-like-resident-evil.html", "Games like Resident Evil and every 2027 survival horror game"))
    if g["slug"] in ("exodus", "the-expanse-osiris-reborn", "squadron-42"): rel.insert(1, ("games-like-mass-effect.html", "Games like Mass Effect and the 2027 space RPGs"))
    if g["slug"] in ("becrowned", "brokenlore-ascend", "trainwatch", "neverway"): rel.insert(1, ("games-like-silent-hill.html", "Games like Silent Hill and 2027 psychological horror"))
    if g["slug"] in ("god-of-war-laufey", "wo-long-2", "tomb-raider-legacy-of-atlantis", "elta-defy-all-gods", "muramasa-revenant-blades", "stranger-than-heaven"): rel.insert(1, ("games-like-god-of-war.html", "Games like God of War and the Laufey countdown"))
    if g["slug"] in ("wo-long-2", "muramasa-revenant-blades", "stranger-than-heaven", "wandering-sword", "showa-american-story"): rel.insert(1, ("games-like-ghost-of-tsushima.html", "Games like Ghost of Tsushima and 2027 samurai games"))
    if g["slug"] in ("monster-hunter-wilds-ascendance", "horizon-steel-frontiers", "the-duskbloods", "wo-long-2", "lords-of-the-fallen-ii"): rel.insert(1, ("games-like-monster-hunter.html", "Games like Monster Hunter and 2027 hunting games"))
    if g["slug"] in ("final-fantasy-vii-revelation", "kingdom-hearts-iv", "final-fantasy-xiv-evercold", "xenoblade-genesis", "terranigma"): rel.insert(1, ("games-like-final-fantasy.html", "Games like Final Fantasy and the FF7 Revelation countdown"))
    if g["slug"] in ("showa-american-story", "stranger-than-heaven"): rel.insert(1, ("games-like-red-dead-redemption-2.html", "Games like Red Dead Redemption 2"))
    if g["slug"] in ("spyder-agent-8", "stranger-than-heaven", "tomb-raider-legacy-of-atlantis", "007-first-light"): rel.insert(1, ("games-like-assassins-creed.html", "Games like Assassin's Creed and 2027 stealth games"))
    if any(k in (g.get("genre") or "").lower() for k in ("strategy", "tactical", "city builder")): rel.insert(1, ("strategy-games-2027.html", "Every strategy and tactics game of 2027"))
    if "shooter" in (g.get("genre") or "").lower(): rel.insert(1, ("shooter-games-2027.html", "Every shooter coming in 2027"))
    if g["slug"] in _RM_KIND: rel.insert(1, ("remakes-2027.html", "Every game remake and remaster of 2027"))
    if g["slug"] in ("final-fantasy-xiv-evercold", "the-witcher-3-songs-of-the-past", "monster-hunter-wilds-ascendance"): rel.insert(1, ("dlc-2027.html", "Every DLC and expansion coming in 2027"))
    if g["slug"] in ("hitman-classic-trilogy-remastered", "007-first-light", "spyder-agent-8"): rel.insert(1, ("games-like-hitman.html", "Games like Hitman and 2027 stealth games"))
    if g["slug"] in ("armatus", "everything-is-crab", "mr-magpies-harmless-card-game"): rel.insert(1, ("games-like-hades.html", "Games like Hades and the 2027 roguelites"))
    if g["slug"] in ("cassette-beasts-2002", "pokemon-winds-and-waves", "state-of-decay-3"): rel.insert(1, ("games-like-palworld.html", "Games like Palworld and the 2027 creature games"))
    if g["slug"] in ("the-duskbloods", "golf-with-your-friends-2", "super-battle-golf"): rel.insert(1, ("games-like-fortnite.html", "Games like Fortnite and 2027 multiplayer games"))
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
    if plat == "Switch 2" and datetime.date.today() <= datetime.date(2026, 12, 5):  # time-limited (DEMAND R1 'switch 2 games black friday deals'); drops out after 5 Dec
        out += (f'<div class="sec-head"><h2>Are Switch 2 games on sale for Black Friday?</h2></div>'
                f'<p>Yes. In the US, Nintendo\'s Black Friday eShop sale on Switch and Switch 2 games runs until 2 December 2026, and the Switch 2 + Mario Kart World bundle is $50 off ($499) at retailers until 5 December. '
                f'In the UK and Europe the main eShop sale ends on 29 November at 23:59, with a second batch of games on sale until 2 December. Discounts vary by game and change daily, so check the eShop. '
                f'See <a href="{href("black-friday-game-sales-2026.html", 1)}">Black Friday 2026 game sales</a> for live "ends in" timers.</p>')
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
        blocks += f'<div class="sec-head" id="m{m}"><h2>{head}</h2><span class="muted">{n}</span></div><div class="out" style="margin-bottom:28px">{rows}</div>'
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
            f'<h1>Upcoming {e(long)} games 2027:<br><span class="amber">every release date.</span></h1>'
            f'<p class="lead">{len(games)} confirmed {e(long)} launches so far, {len(dated)} with an exact date. '
            f'Sorted by release date and checked against official announcements.</p>'
            f'<p class="muted" style="margin:0">Last checked {e(UPDATED)} · Other consoles: {other_links}</p>{cd}</div></header>'
            f'<section><div class="wrap"><div class="out" style="margin-bottom:24px"><div class="row"><span><strong>Quick answer:</strong> {len(games)} confirmed 2027 games are coming to {e(long)}'
            + (f', and the next one is {e(dated[0]["title"])} on {e(nice_date(dated[0]))}' if dated else '')
            + (f'. Only on {e(long)}: {e(", ".join(g["title"] for g in excl))}.' if excl else f'. None of them are {e(long)} exclusives right now.')
            + f'</span></div></div>'
            + ('<nav class="chips" aria-label="Jump to month" style="margin-bottom:22px">' + "".join(f'<a class="chip" style="text-decoration:none" href="#m{m}">{"No date yet" if m == 13 else MONTHS[m - 1][:3] + " 2027"}</a>' for m in sorted(by_month)) + '</nav>')
            + f'{blocks}'
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
    page(f, f"{long} Game Release Dates 2027: All {len(games)} Games | DayOneDrop",
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
    page(f, f"Games Coming Out in {mname} 2027: All {len(games)} Release Dates | DayOneDrop",
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
             f'<div class="sec-head" style="margin-top:28px"><h2>Will 2027 PS5 exclusives come to PC later?</h2></div>'
             f'<p>Do not count on it. Sony used to bring its big single-player games to PC a year or more after PS5, but in March 2026 Bloomberg reported that it has stopped planning those ports, naming Ghost of Yotei and Saros; online games such as Marathon still come to PC. Sony declined to comment (Kotaku, Engadget), so this could change. For 2027 that matters most for God of War: Laufey and Until Dawn 2. More on the <a href="{href("games-like-ghost-of-tsushima.html", 0)}">Ghost of Yotei PC page</a>.</p>'
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
    ("Will PS5 exclusives like God of War Laufey come to PC?", "Not announced. Bloomberg reported in March 2026 that Sony no longer plans PC ports of its big single-player games, naming Ghost of Yotei and Saros. Sony did not comment, so this could change."),
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
_rpg_mt = sorted([g for g in GAMES if g["slug"] in ("pokemon-winds-and-waves", "cassette-beasts-2002", "honkai-nexus-anima")], key=lambda g: (g["month"] or 13, g["date"] or "9999"))
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
            f'<div class="sec-head" style="margin-top:28px"><h2>What monster-taming RPGs come out in 2027?</h2><span class="muted">{len(_rpg_mt)}</span></div>'
            f'<div class="out" style="margin-bottom:10px">' + "".join(f'<div class="row"><span>{_gname(g)}<br><span class="muted">{e(", ".join(g["platforms"]))}</span></span><b>{e(nice_date(g))}</b></div>' for g in _rpg_mt) + '</div>'
            f'<p>Pokémon Winds and Waves has no month yet, so Cassette Beasts 2002 (March) is the first dated creature collector of 2027. Dragon Quest Monsters: The Withered World arrives before them, on 3 December 2026. For ones to play now, see <a href="{href("games-like-pokemon.html", 0)}">games like Pokémon</a>. For party CRPGs like Baldur\'s Gate 3, see <a href="{href("games-like-baldurs-gate-3.html", 0)}">games like Baldur\'s Gate 3</a>.</p>'
            f'<div class="sec-head" style="margin-top:28px"><h2>Related pages and tools</h2></div><ul>'
            f'<li><a href="{href("games-by-genre-2027.html", 0)}">2027 games by genre</a>: horror, shooters, platformers and more</li>'
            f'<li><a href="{href("backlog-planner-2027.html", 0)}">2027 backlog planner</a>: can you finish one RPG before the next?</li>'
            f'<li><a href="{href("games-like-final-fantasy.html", 0)}">Games like Final Fantasy</a> and <a href="{href("games-like-persona.html", 0)}">games like Persona 5</a>: JRPGs to play now</li>'
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
rpg_faq.append(("What monster-taming games come out in 2027?", ", ".join(f"{g['title']} ({nice_date(g)})" for g in _rpg_mt) + ". Dragon Quest Monsters: The Withered World comes first, on 3 December 2026."))
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
_gen_quick += f" No yearly sports series (FC, Madden, NBA 2K) has a 2027 date yet."
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
            f'<p>Only party golf so far: Super Battle Golf comes to Switch 2 on 25 March 2027, and Golf With Your Friends 2 is due in 2027 with no date. No yearly sports series (football, soccer, basketball) has a 2027 edition dated yet. Football Manager 27 already came out on 10 November 2026. EA\'s current editions came out in 2026: College Football 27 on 9 July 2026 (PS5, Xbox Series X|S, PC) and EA Sports FC 27 on 25 September 2026 (also on Switch 2). The yearly 2027 editions are normally revealed a few months before launch, so expect news in spring and summer 2027.</p>'
            f'<p>For racing and driving games, {_sport_race}</p>'
            f'<div class="sec-head" style="margin-top:28px"><h2>What cozy games come out in 2027?</h2></div>'
            f'<p>Emberville (7 January, PC Early Access), Witchbrook (28 January, every platform and Game Pass), Atelier Karia (25 February) and Grave Seasons (9 March), with the horror life sim Neverway later in 2027. Stardew Valley\'s 1.7 update is expected in 2027 with no date. See <a href="{href("games-like-stardew-valley.html", 0)}">games like Stardew Valley</a> for a cozy game finder.</p>'
            f'<div class="sec-head" style="margin-top:28px"><h2>Related pages and tools</h2></div><ul>'
            f'<li><a href="{href("horror-games-2027.html", 0)}">Every horror game of 2027</a>, with a console filter and countdown</li>'
            f'<li><a href="{href("fighting-games-2027.html", 0)}">Every fighting game of 2027</a>: Melty Blood, Xenoverse 3, Virtua Fighter</li>'
            f'<li><a href="{href("strategy-games-2027.html", 0)}">Every strategy game of 2027</a>: Tropico 7, War for Westeros, Humankind II</li>'
            f'<li><a href="{href("shooter-games-2027.html", 0)}">Every shooter of 2027</a>: Metro 2039, Turok: Origins, Squadron 42</li>'
            f'<li><a href="{href("remakes-2027.html", 0)}">Every game remake and remaster of 2027</a>: Persona 4 Revival, Tomb Raider, RE Veronica</li>'
            f'<li><a href="{href("dlc-2027.html", 0)}">DLC and expansions coming in 2027</a>: Witcher 3, Monster Hunter Wilds, Starfield</li>'
            f'<li><a href="{href("xbox-games-showcase-2027.html", 0)}">Xbox Games Showcase 2027</a>: which Xbox games still need a date</li>'
            f'<li><a href="{href("rpgs-2027.html", 0)}">Every RPG coming in 2027</a>, with action RPG and JRPG filters</li>'
            f'<li><a href="{href("games-like-elden-ring.html", 0)}">Games like Elden Ring</a>: soulslikes out now and in 2027</li>'
            f'<li><a href="{href("games-like-hollow-knight.html", 0)}">Games like Hollow Knight</a>: metroidvanias out now and in 2027</li>'
            f'<li><a href="{href("games-like-stardew-valley.html", 0)}">Games like Stardew Valley</a>: cozy and farming games now and in 2027</li>'
            f'<li><a href="{href("games-like-animal-crossing.html", 0)}">Games like Animal Crossing</a>: cozy life sims, and Pokopia</li>'
            f'<li><a href="{href("games-like-fortnite.html", 0)}">Games like Fortnite</a>: free battle royales and shooters</li>'
            f'<li><a href="{href("games-like-baldurs-gate-3.html", 0)}">Games like Baldur\'s Gate 3</a>: CRPGs now, Dark Heresy and Divinity next</li>'
            f'<li><a href="{href("games-like-skyrim.html", 0)}">Games like Skyrim</a>: open-world RPGs now, Fable next</li>'
            f'<li><a href="{href("games-like-the-witcher-3.html", 0)}">Games like The Witcher 3</a>: story RPGs, Songs of the Past in 2027</li>'
            f'<li><a href="{href("games-like-hades.html", 0)}">Games like Hades</a>: roguelites now and in 2027</li>'
            f'<li><a href="{href("games-like-red-dead-redemption-2.html", 0)}">Games like Red Dead Redemption 2</a> and <a href="{href("games-like-cyberpunk-2077.html", 0)}">games like Cyberpunk 2077</a></li>'
            f'<li><a href="{href("games-like-persona.html", 0)}">Games like Persona 5</a>: JRPGs now and in 2027</li>'
            f'<li><a href="{href("games-like-final-fantasy.html", 0)}">Games like Final Fantasy</a>: JRPGs, plus the FF7 Revelation countdown</li>'
            f'<li><a href="{href("games-like-resident-evil.html", 0)}">Games like Resident Evil</a>: survival horror now and in 2027</li>'
            f'<li><a href="{href("games-like-silent-hill.html", 0)}">Games like Silent Hill</a>: psychological horror, and <a href="{href("games-like-mass-effect.html", 0)}">games like Mass Effect</a>: space RPGs</li>'
            f'<li><a href="{href("games-like-god-of-war.html", 0)}">Games like God of War</a>: mythic action games and the Laufey countdown</li>'
            f'<li><a href="{href("games-like-ghost-of-tsushima.html", 0)}">Games like Ghost of Tsushima</a>: samurai games now and in 2027</li>'
            f'<li><a href="{href("games-like-monster-hunter.html", 0)}">Games like Monster Hunter</a>: hunting games and the Wilds Ascendance expansion</li>'
            f'<li><a href="{href("games-like-palworld.html", 0)}">Games like Palworld</a>: creature survival games now and in 2027</li>'
            f'<li><a href="{href("games-like-zelda.html", 0)}">Games like Zelda</a>: adventures now and in 2027</li>'
            f'<li><a href="{href("games-like-pokemon.html", 0)}">Games like Pokémon</a>: monster tamers now and in 2027, and <a href="{href("games-like-minecraft.html", 0)}">games like Minecraft</a></li>'
            f'<li><a href="{href("biggest-games-2027.html", 0)}">The biggest games of 2027</a> and a shareable top list maker</li>'
            f'<li><a href="{href("release-clashes-2027.html", 0)}">2027 release clashes</a>: do your picks land the same week?</li>'
            f'<li><a href="{href("backlog-planner-2027.html", 0)}">2027 backlog planner</a>: finish one before the next arrives</li></ul></div></section>')
gen_faq = [("What genre has the most games in 2027?", _gen_quick)]
for _k in _gen:
    _n, _low = _gen_meta[_k]
    gen_faq.append((f"What {_low} are coming out in 2027?", f"We track {len(_gen[_k])}: " + ", ".join(f"{g['title']} ({nice_date(g)})" for g in _gen[_k]) + "."))
gen_faq.append(("Are there any sports games coming out in 2027?", "Only party golf so far: Super Battle Golf (25 March 2027, Switch 2) and Golf With Your Friends 2 (2027). The 2027 editions of EA Sports FC, Madden and NBA 2K have not been announced."))
gen_faq.append(("What cozy games come out in 2027?", "Emberville (7 January, PC Early Access), Witchbrook (28 January), Atelier Karia (25 February), Grave Seasons (9 March) and Neverway (2027)."))
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
             f'<div class="sec-head" style="margin-top:28px"><h2>Is there a new Silent Hill game in 2027?</h2></div>'
             f'<p>Not one with a date. Silent Hill: Townfall came out on 24 September 2026 on PS5 and PC, and Bloober Team is remaking the first Silent Hill, but Konami has not given it a year or platforms. Reports of a 2027 launch are leaks. Until then, see <a href="{href("games-like-silent-hill.html", 0)}">games like Silent Hill</a> to play now.</p>'
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
             f'<li><a href="{href("games-like-resident-evil.html", 0)}">Games like Resident Evil</a>: survival horror to play now, by console</li>'
             f'<li><a href="{href("games-like-silent-hill.html", 0)}">Games like Silent Hill</a>: psychological horror to play now, and the Silent Hill 1 remake</li>'
             f'<li><a href="{href("games/resident-evil-veronica.html", 0)}">Resident Evil Veronica release date and platforms</a></li>'
             f'<li><a href="{href("biggest-games-2027.html", 0)}">The biggest games of 2027</a></li></ul></div></section>')
hor_faq = [("What horror games are coming out in 2027?", f"We track {len(_hor)}: " + ", ".join(f"{g['title']} ({nice_date(g)})" for g in _hor) + "."), ("Is there a new Silent Hill game in 2027?", "None is dated. Silent Hill: Townfall came out on 24 September 2026, and the Silent Hill 1 remake from Bloober Team has no release date yet.")]
if _hor_next:
    hor_faq.append(("What is the first horror game of 2027?", f"{_hor_next['title']}, on {nice_date(_hor_next)} for {', '.join(_hor_next['platforms'])}."))
for _p in PLATS:
    hor_faq.append((f"What horror games are coming to {_lab[_p]} in 2027?", (f"{len(_hor_p[_p])}: " + ", ".join(f"{g['title']} ({nice_date(g)})" for g in _hor_p[_p]) + ".") if _hor_p[_p] else "None confirmed yet."))
hor_faq.append(("Is Resident Evil Veronica out in 2027?", "Yes, Capcom says 2027 on PS5, Xbox Series X|S, Switch 2 and PC. No month or day has been announced."))
if _hor_delayed:
    hor_faq.append(("Which horror games were delayed to 2027?", ", ".join(g["title"] for g in _hor_delayed) + "."))
page("horror-games-2027.html", f"Horror Games Coming Out in 2027: All {len(_hor)} Dates and Consoles | DayOneDrop",
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
            f'<li><a href="{href("strategy-games-2027.html", 0)}">Strategy games of 2027</a>: RTS, 4X and tactics</li>'
            f'<li><a href="{href("shooter-games-2027.html", 0)}">Shooter games of 2027</a>: Metro 2039, Turok and more</li>'
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


# ---------------- STRATEGY GAMES 2027 (28 Nov 2026, demand: "strategy games 2027", "upcoming strategy games 2027", "rts games 2027", "tactics games 2027", DEMAND N74) ----------------
# Built from games.json: genre contains strategy / tactical / city builder. Reuses the fighting-games console filter JS (#fg-tool, data-noun).
# Facts: Calame Feb 2027 (Gematsu + RPG Site + RPGamer), Kingdom III 2027 (Gematsu + PC Games DE), Humankind II 2027 PC (Gematsu + PCGamesN + Worthplaying),
# Dawn of War IV 3 Dec 2026 PC, delayed from 17 Sep (Gematsu + KitGuru + Deep Silver press release).
_st = sorted([g for g in GAMES if any(k in (g.get("genre") or "").lower() for k in ("strategy", "tactical", "city builder", "4x"))], key=lambda x: (x["month"], x["date"] or "9999"))
_st_dated = [g for g in _st if g["date"]]
_st_next = _st_dated[0] if _st_dated else None
_st_p = {p: [g for g in _st if p in g["platforms"]] for p in PLATS}
_st_tac = [g for g in _st if "tactical" in g["genre"].lower()]
_st_quick = (f"We track {len(_st)} strategy and tactics games for 2027. "
             + (f"First up is {_st_next['title']} on {nice_date(_st_next)}, " if _st_next else "")
             + f"then {_and([g['title'] + ' (' + nice_date(g) + ')' for g in _st if g is not _st_next][:5])}. "
             "Warhammer 40,000: Dawn of War IV lands even sooner, on 3 December 2026 on PC.")
_st_tbl = ('<div style="overflow-x:auto"><table class="gen-table" style="width:100%;border-collapse:collapse;font-size:.92rem"><thead><tr><th style="text-align:left;padding:6px">Console</th><th style="padding:6px">Strategy games</th><th style="text-align:left;padding:6px">Which ones</th></tr></thead><tbody>'
           + "".join(f'<tr><td style="padding:6px;border-top:1px solid var(--rule)"><a href="{href("platforms/" + _pslug[p] + ".html", 0)}">{e(_lab[p])}</a></td>'
                     f'<td style="padding:6px;text-align:center;border-top:1px solid var(--rule)" class="mono">{len(_st_p[p])}</td>'
                     f'<td style="padding:6px;border-top:1px solid var(--rule)">{e(", ".join(g["title"] for g in _st_p[p]) or "None confirmed yet")}</td></tr>' for p in PLATS)
           + '</tbody></table></div>')
_st_cd = (f'<div class="cdw"><span class="lbl">Countdown to {e(_st_next["title"])}</span><div class="cd" data-countdown="{_st_next["date"]}">'
          '<div class="cd-unit"><span class="flaps" data-u="0"></span><span>Days</span></div><div class="cd-unit"><span class="flaps" data-u="1"></span><span>Hrs</span></div>'
          '<div class="cd-unit"><span class="flaps" data-u="2"></span><span>Min</span></div><div class="cd-unit"><span class="flaps" data-u="3"></span><span>Sec</span></div></div></div>') if _st_next else ""
_st_body = (f'<header class="hero"><div class="wrap"><span class="kicker">Strategy games</span>'
            f'<h1>Strategy games coming in 2027:<br><span class="amber">RTS, 4X, tactics, every date.</span></h1>'
            f'<p class="lead">Every strategy, city-builder and tactical RPG confirmed for 2027, from Tropico 7 and Game of Thrones: War for Westeros to Humankind II, with a console filter and a countdown.</p>'
            f'<p class="muted" style="margin:0">Last checked {e(UPDATED)} · {len(_st)} games · dates and platforms from publishers or two trusted outlets</p></div></header>'
            f'<section><div class="wrap"><div class="out" style="margin-bottom:24px"><div class="row"><span><strong>Quick answer:</strong> {e(_st_quick)}</span></div></div>'
            f'<div class="tool" id="fg-tool" data-noun="strategy game"><h2 style="font-size:1.5rem;margin-top:0">Which 2027 strategy games can I play on my console?</h2>'
            f'<p class="muted">Tap your console. The list below updates, and your choice is remembered on this device.</p>{_fchips}'
            f'<p class="mono amber" id="fg-count" aria-live="polite" style="margin:12px 0 0">{len(_st)} games</p>'
            f'<div class="btns" style="margin-top:10px;display:flex;gap:8px;flex-wrap:wrap"><button class="btn sm" type="button" id="fg-add">Add these to my ★ list</button>'
            f'<a class="btn line sm" href="{href("release-clashes-2027.html", 0)}">Check release clashes</a></div></div></div></section>'
            + AD.format("st-mid") +
            f'<section><div class="wrap"><div class="sec-head"><h2>What strategy games come out in 2027?</h2><span class="muted">{len(_st)}</span></div>'
            f'<p class="muted">In release order. Games with only a month or a year sit after the dated ones.</p>'
            f'<div class="out" id="fg-list" style="margin-bottom:10px">{"".join(_fgrow(g) for g in _st)}</div><p class="empty" id="fg-none" hidden>No tracked 2027 strategy game is confirmed for that console yet.</p>{_st_cd}'
            f'<div class="sec-head" style="margin-top:28px"><h2>What is the next big strategy game?</h2></div>'
            f'<p><strong>Warhammer 40,000: Dawn of War IV</strong> comes out on <strong>3 December 2026</strong> on PC. It was due on 17 September 2026 and was pushed back to December (Gematsu, KitGuru). '
            + (f'In 2027, {_gname(_st_next)} is first, on {e(nice_date(_st_next))} for {e(", ".join(_st_next["platforms"]))}.' if _st_next else "") + '</p>'
            f'<div class="sec-head" style="margin-top:28px"><h2>When does Tropico 7 come out?</h2></div>'
            f'<p>On 28 January 2027, on PS5, Xbox Series X|S and PC. You run your own island nation again as El Presidente.</p>'
            f'<div class="sec-head" style="margin-top:28px"><h2>Is there a new real-time strategy (RTS) game in 2027?</h2></div>'
            f'<p>Yes: <a href="{href("games/game-of-thrones-war-for-westeros.html", 0)}">Game of Thrones: War for Westeros</a>, a classic squad-based RTS from PlaySide, is due in early 2027 on PC after a delay from 2026. Dawn of War IV, the other big RTS, arrives just before, in December 2026.</p>'
            f'<div class="sec-head" style="margin-top:28px"><h2>Is there a new Civilization-style 4X game in 2027?</h2></div>'
            f'<p>Humankind II from Amplitude Studios is due on PC (Steam) in 2027, with no month yet. Each era you take on a new culture, and the climate changes over a campaign. Civilization VII came out in February 2025; its first paid expansion, Earthrise, is due in 2027 (see <a href="{href("dlc-2027.html", 0)}">DLC coming in 2027</a>), but no new Civilization game is announced.</p>'
            f'<div class="sec-head" style="margin-top:28px"><h2>What tactics games and tactical RPGs come out in 2027?</h2></div>'
            f'<p>{e(_and([g["title"] + " (" + nice_date(g) + ", " + ", ".join(g["platforms"]) + ")" for g in _st_tac]))}. Calame lets you reshape the battlefield mid-fight; Shadow of the Road is set in a steampunk feudal Japan and published by Owlcat. For bigger party RPGs, see <a href="{href("games-like-baldurs-gate-3.html", 0)}">games like Baldur\'s Gate 3</a>.</p>'
            f'<div class="sec-head" style="margin-top:28px"><h2>Are there strategy games for Switch 2 in 2027?</h2></div>'
            f'<p>{e(_and([g["title"] + " (" + nice_date(g) + ")" for g in _st_p["Switch 2"]])) if _st_p["Switch 2"] else "None confirmed yet"}. Kingdom III is a side-scrolling build-and-defend game you can play in co-op.</p>'
            f'<div class="sec-head" style="margin-top:28px"><h2>How many 2027 strategy games are on PS5, Xbox, PC and Switch 2?</h2></div>{_st_tbl}'
            f'<div class="sec-head" style="margin-top:28px"><h2>Related pages and tools</h2></div><ul>'
            f'<li><a href="{href("games-by-genre-2027.html", 0)}">2027 games by genre</a>: horror, shooters, RPGs and more</li>'
            f'<li><a href="{href("rpgs-2027.html", 0)}">Every RPG of 2027</a>, with a console filter</li>'
            f'<li><a href="{href("platforms/pc.html", 0)}">Every PC game coming in 2027</a></li>'
            f'<li><a href="{href("steam-sale-dates.html", 0)}">Steam sale dates</a>: when to buy the strategy games you missed</li>'
            f'<li><a href="{href("countdown.html", 0)}">Game release countdown</a> for any dated 2027 game</li></ul></div></section>')
st_faq = [("What strategy games are coming out in 2027?", f"We track {len(_st)}: " + ", ".join(f"{g['title']} ({nice_date(g)})" for g in _st) + "."),
          ("When does Tropico 7 come out?", "On 28 January 2027 on PS5, Xbox Series X|S and PC."),
          ("When does Game of Thrones: War for Westeros come out?", "In early 2027 on PC. PlaySide has not given an exact day."),
          ("When does Humankind 2 come out?", "In 2027 on PC (Steam). Amplitude has not given a month yet."),
          ("When does Dawn of War 4 come out?", "On 3 December 2026 on PC. It was delayed from 17 September 2026.")]
if _st_p["Switch 2"]:
    st_faq.append(("What strategy games are coming to Switch 2 in 2027?", ", ".join(f"{g['title']} ({nice_date(g)})" for g in _st_p["Switch 2"]) + "."))
page("strategy-games-2027.html", "Strategy Games 2027: Every RTS, 4X and Tactics Release",
     f"Every strategy game coming in 2027: Tropico 7 (28 Jan), War for Westeros, Calame, Humankind II, Kingdom III and more, with a console filter and countdown.",
     _st_body, 0, st_faq, crumbs=[("Home", DOMAIN + "/"), ("2027 games by genre", canon("games-by-genre-2027.html")), ("Strategy games 2027", canon("strategy-games-2027.html"))])


# ---------------- SHOOTER GAMES 2027 (28 Nov 2026, demand: "upcoming shooter games 2027", "fps games 2027", "new shooters 2027", DEMAND N83 Valorant/Overwatch) ----------------
# Built from games.json: genre contains "shooter". Reuses the #fg-tool console filter JS.
# Facts: Turok: Origins spring 2027 (Gematsu 25 Aug 2026 + Nintendo Life + GamesBeat), Clockwork Revolution 2027 Xbox Series/PC, Xbox console exclusive (Gematsu + GamesRadar+ + Xbox Wire).
# Call of Duty 2027 / new hero shooters: nothing announced, said plainly.
_sh = sorted([g for g in GAMES if "shooter" in (g.get("genre") or "").lower()], key=lambda x: (x["month"], x["date"] or "9999"))
_sh_dated = [g for g in _sh if g["date"]]
_sh_next = _sh_dated[0] if _sh_dated else None
_sh_p = {p: [g for g in _sh if p in g["platforms"]] for p in PLATS}
_sh_shmup = [g for g in GAMES if "shoot 'em up" in (g.get("genre") or "").lower()]
_sh_quick = (f"We track {len(_sh)} shooters for 2027. "
             + (f"First up is {_sh_next['title']} on {nice_date(_sh_next)}, " if _sh_next else "")
             + f"then {_and([g['title'] + ' (' + nice_date(g) + ')' for g in _sh if g is not _sh_next])}. "
             "Call of Duty 2027 has not been announced yet.")
_sh_tbl = ('<div style="overflow-x:auto"><table class="gen-table" style="width:100%;border-collapse:collapse;font-size:.92rem"><thead><tr><th style="text-align:left;padding:6px">Console</th><th style="padding:6px">Shooters</th><th style="text-align:left;padding:6px">Which ones</th></tr></thead><tbody>'
           + "".join(f'<tr><td style="padding:6px;border-top:1px solid var(--rule)"><a href="{href("platforms/" + _pslug[p] + ".html", 0)}">{e(_lab[p])}</a></td>'
                     f'<td style="padding:6px;text-align:center;border-top:1px solid var(--rule)" class="mono">{len(_sh_p[p])}</td>'
                     f'<td style="padding:6px;border-top:1px solid var(--rule)">{e(", ".join(g["title"] for g in _sh_p[p]) or "None confirmed yet")}</td></tr>' for p in PLATS)
           + '</tbody></table></div>')
_sh_cd = (f'<div class="cdw"><span class="lbl">Countdown to {e(_sh_next["title"])}</span><div class="cd" data-countdown="{_sh_next["date"]}">'
          '<div class="cd-unit"><span class="flaps" data-u="0"></span><span>Days</span></div><div class="cd-unit"><span class="flaps" data-u="1"></span><span>Hrs</span></div>'
          '<div class="cd-unit"><span class="flaps" data-u="2"></span><span>Min</span></div><div class="cd-unit"><span class="flaps" data-u="3"></span><span>Sec</span></div></div></div>') if _sh_next else ""
_sh_body = (f'<header class="hero"><div class="wrap"><span class="kicker">Shooters</span>'
            f'<h1>Shooter games coming in 2027:<br><span class="amber">every FPS and TPS date.</span></h1>'
            f'<p class="lead">Every first- and third-person shooter confirmed for 2027, from Metro 2039 and Turok: Origins to Squadron 42 and Clockwork Revolution, with a console filter and a countdown to the next one.</p>'
            f'<p class="muted" style="margin:0">Last checked {e(UPDATED)} · {len(_sh)} shooters · dates and platforms from publishers or two trusted outlets</p></div></header>'
            f'<section><div class="wrap"><div class="out" style="margin-bottom:24px"><div class="row"><span><strong>Quick answer:</strong> {e(_sh_quick)}</span></div></div>'
            f'<div class="tool" id="fg-tool" data-noun="shooter"><h2 style="font-size:1.5rem;margin-top:0">Which 2027 shooters can I play on my console?</h2>'
            f'<p class="muted">Tap your console. The list below updates, and your choice is remembered on this device.</p>{_fchips}'
            f'<p class="mono amber" id="fg-count" aria-live="polite" style="margin:12px 0 0">{len(_sh)} shooters</p>'
            f'<div class="btns" style="margin-top:10px;display:flex;gap:8px;flex-wrap:wrap"><button class="btn sm" type="button" id="fg-add">Add these to my ★ list</button>'
            f'<a class="btn line sm" href="{href("release-clashes-2027.html", 0)}">Check release clashes</a></div></div></div></section>'
            + AD.format("sh-mid") +
            f'<section><div class="wrap"><div class="sec-head"><h2>What shooter games come out in 2027?</h2><span class="muted">{len(_sh)}</span></div>'
            f'<p class="muted">In release order. Games with only a season or a year sit after the dated ones.</p>'
            f'<div class="out" id="fg-list" style="margin-bottom:10px">{"".join(_fgrow(g) for g in _sh)}</div><p class="empty" id="fg-none" hidden>No tracked 2027 shooter is confirmed for that console yet.</p>{_sh_cd}'
            f'<div class="sec-head" style="margin-top:28px"><h2>What is the next big shooter?</h2></div>'
            + (f'<p>{_gname(_sh_next)} is first, on {e(nice_date(_sh_next))} for {e(", ".join(_sh_next["platforms"]))}. The biggest early-2027 shooter is <a href="{href("games/metro-2039.html", 0)}">Metro 2039</a> on 4 February.</p>' if _sh_next else "")
            + f'<div class="sec-head" style="margin-top:28px"><h2>When does Metro 2039 come out?</h2></div>'
            f'<p>On 4 February 2027, on PS5, Xbox Series X|S and PC (Steam and Epic) on the same day. 4A Games is making it and Deep Silver is publishing it. It moved from winter 2026, and the date was revealed at a PlayStation State of Play in September 2026.</p>'
            f'<div class="sec-head" style="margin-top:28px"><h2>When does Turok: Origins come out?</h2></div>'
            f'<p>In spring 2027, on PS5, Xbox Series X|S, Switch 2 and PC (Steam). Saber Interactive delayed it from fall 2026 at gamescom in August 2026 (Gematsu, Nintendo Life). You fight dinosaurs and an alien threat across the Lost Lands and steal enemy DNA to unlock suit powers. No exact day yet.</p>'
            f'<div class="sec-head" style="margin-top:28px"><h2>Is Clockwork Revolution coming to PS5?</h2></div>'
            f'<p>No. Clockwork Revolution is an Xbox console exclusive, coming in 2027 to Xbox Series X|S and PC (Steam and Microsoft Store), and it is on <a href="{href("game-pass-2027.html", 0)}">Game Pass</a>. It is a first-person action RPG from inXile (Wasteland) set in Avalon, a Victorian steampunk city, where you go back in time and change the past.</p>'
            f'<div class="sec-head" style="margin-top:28px"><h2>When does Squadron 42 come out?</h2></div>'
            f'<p>In Q2 2027 (April to June) on PC only. Cloud Imperium moved it out of 2026 and named GTA 6 as the reason. Full details are in our <a href="{href("games/squadron-42.html", 0)}">Squadron 42 release guide</a>.</p>'
            f'<div class="sec-head" style="margin-top:28px"><h2>Is there a new Call of Duty in 2027?</h2></div>'
            f'<p>Not announced yet. A new Call of Duty has come out every autumn for two decades, but Activision has not named, dated or shown the 2027 game. It usually reveals each year\'s game in the summer. We will add it the day it is official.</p>'
            f'<div class="sec-head" style="margin-top:28px"><h2>Is there a new hero shooter like Overwatch or Valorant in 2027?</h2></div>'
            f'<p>No new hero or tactical team shooter has a 2027 date on our board yet. If you want one to play now, Marvel Rivals and Overwatch 2 are free on PS5, Xbox and PC; see <a href="{href("games-like-fortnite.html", 0)}">games like Fortnite</a> for a finder of free shooters and battle royales by console.</p>'
            f'<div class="sec-head" style="margin-top:28px"><h2>Are there shoot \'em ups (shmups) in 2027?</h2></div>'
            f'<p>{e(_and([g["title"] + " (" + nice_date(g) + ", " + ", ".join(g["platforms"]) + ")" for g in _sh_shmup])) if _sh_shmup else "None on our board yet"}. They are arcade-style scrolling shooters, so we keep them out of the list above.</p>'
            f'<div class="sec-head" style="margin-top:28px"><h2>How many 2027 shooters are on PS5, Xbox, PC and Switch 2?</h2></div>{_sh_tbl}'
            f'<div class="sec-head" style="margin-top:28px"><h2>Related pages and tools</h2></div><ul>'
            f'<li><a href="{href("games-by-genre-2027.html", 0)}">2027 games by genre</a>: horror, RPGs, platformers and more</li>'
            f'<li><a href="{href("horror-games-2027.html", 0)}">Horror games of 2027</a>, for survival shooters</li>'
            f'<li><a href="{href("games-2028.html", 0)}">Games coming out in 2028</a>: what has already moved past 2027</li>'
            f'<li><a href="{href("countdown.html", 0)}">Game release countdown</a> for any dated 2027 game</li></ul></div></section>')
sh_faq = [("What shooter games are coming out in 2027?", f"We track {len(_sh)}: " + ", ".join(f"{g['title']} ({nice_date(g)})" for g in _sh) + "."),
          ("When does Metro 2039 come out?", "On 4 February 2027 on PS5, Xbox Series X|S and PC."),
          ("When does Turok: Origins come out?", "In spring 2027 on PS5, Xbox Series X|S, Switch 2 and PC. It was delayed from fall 2026. No exact day yet."),
          ("Is Clockwork Revolution on PS5?", "No. It is an Xbox console exclusive, coming in 2027 to Xbox Series X|S and PC, and it is on Game Pass."),
          ("Is Call of Duty 2027 announced?", "No. Activision has not named or dated the 2027 Call of Duty yet.")]
if _sh_p["Switch 2"]:
    sh_faq.append(("What shooters are coming to Switch 2 in 2027?", ", ".join(f"{g['title']} ({nice_date(g)})" for g in _sh_p["Switch 2"]) + "."))
page("shooter-games-2027.html", "Upcoming Shooter Games 2027: Every FPS Release Date",
     f"Every shooter coming in 2027: Metro 2039 (4 Feb), Turok: Origins (spring), Squadron 42, Clockwork Revolution and more, with a console filter and countdown."[:160],
     _sh_body, 0, sh_faq, crumbs=[("Home", DOMAIN + "/"), ("2027 games by genre", canon("games-by-genre-2027.html")), ("Shooter games 2027", canon("shooter-games-2027.html"))])


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
page("backlog-planner-2027.html", "2027 Backlog Planner: Finish Before the Next Big Game?",
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
<li><a href="{href("new-tv-shows-december-2026.html", 0)}">New TV shows December 2026</a>: every premiere with a streaming-service filter</li>
<li><a href="{href("new-tv-shows-january-2027.html", 0)}">New TV shows January 2027</a>: ABC and Fox midseason premieres with times and reminders</li>
<li><a href="{href("movies-december-2026.html", 0)}">Movies coming out in December 2026</a>: filter by type and week, countdown to Avengers: Doomsday</li>
<li><a href="{href("movies-january-2027.html", 0)}">Movies coming out in January 2027</a>: Children of Blood and Bone, The Beekeeper 2, Animal Friends</li>
<li><a href="{href("games-like-hollow-knight.html", 0)}">Games like Hollow Knight</a>: metroidvania finder by platform, plus the 2027 metroidvanias</li>
<li><a href="{href("games-like-stardew-valley.html", 0)}">Games like Stardew Valley</a>: cozy game finder by platform, plus Witchbrook and the 2027 farm sims</li>
<li><a href="{href("games-like-animal-crossing.html", 0)}">Games like Animal Crossing</a>: cozy life-sim finder by platform</li>
<li><a href="{href("games-like-fortnite.html", 0)}">Games like Fortnite</a>: battle royale and shooter finder by platform, most free</li>
<li><a href="{href("games-like-baldurs-gate-3.html", 0)}">Games like Baldur's Gate 3</a>: CRPG finder by platform, plus Dark Heresy and Larian's Divinity</li>
<li><a href="{href("games-like-zelda.html", 0)}">Games like Zelda</a>: adventure finder by platform, plus Hyrule Warriors and the Zelda movie in 2027</li>
<li><a href="{href("games-like-pokemon.html", 0)}">Games like Pokémon</a>: creature-collector finder by platform, plus Winds and Waves and Cassette Beasts 2002</li>
<li><a href="{href("games-like-minecraft.html", 0)}">Games like Minecraft</a>: sandbox and survival finder, plus the Minecraft movie 2 countdown</li>
<li><a href="{href("games-like-palworld.html", 0)}">Games like Palworld</a>: creature survival finder by platform, plus the 2027 creature collectors</li>
<li><a href="{href("games-like-skyrim.html", 0)}">Games like Skyrim</a>: open-world RPG finder by platform, plus Fable and the Elder Scrolls 6 news</li>
<li><a href="{href("games-like-the-witcher-3.html", 0)}">Games like The Witcher 3</a>: story RPG finder by platform, plus Songs of the Past and The Witcher 4 dates</li>
<li><a href="{href("games-like-hades.html", 0)}">Games like Hades</a>: roguelite finder by platform, plus the 2027 roguelites and Hades 3 news</li>
<li><a href="{href("games-like-red-dead-redemption-2.html", 0)}">Games like Red Dead Redemption 2</a>: open-world finder by platform, plus RDR3 news</li>
<li><a href="{href("games-like-cyberpunk-2077.html", 0)}">Games like Cyberpunk 2077</a>: sci-fi RPG finder, plus 2027 sci-fi games and the Cyberpunk 2 timeline</li>
<li><a href="{href("games-like-persona.html", 0)}">Games like Persona 5</a>: JRPG finder, plus the Persona 4 Revival countdown</li>
<li><a href="{href("games-like-final-fantasy.html", 0)}">Games like Final Fantasy</a>: JRPG finder by battle style, plus the FF7 Revelation countdown</li>
<li><a href="{href("games-like-resident-evil.html", 0)}">Games like Resident Evil</a>: survival horror finder, plus Resident Evil Veronica and RE10 news</li>
<li><a href="{href("games-like-silent-hill.html", 0)}">Games like Silent Hill</a>: psychological horror finder, plus the Silent Hill 1 remake news</li>
<li><a href="{href("games-like-mass-effect.html", 0)}">Games like Mass Effect</a>: space RPG finder, plus the Exodus countdown and Mass Effect 5 news</li>
<li><a href="{href("games-like-god-of-war.html", 0)}">Games like God of War</a>: action game finder, plus the God of War Laufey countdown</li>
<li><a href="{href("games-like-ghost-of-tsushima.html", 0)}">Games like Ghost of Tsushima</a>: samurai game finder, plus 2027 sword games and Ghost of Yotei on PC</li>
<li><a href="{href("games-like-assassins-creed.html", 0)}">Games like Assassin's Creed</a>: stealth and parkour finder, 2027 stealth games and the Hexe date</li>
<li><a href="{href("strategy-games-2027.html", 0)}">Strategy games of 2027</a>: RTS, 4X and tactics list with a console filter</li>
<li><a href="{href("shooter-games-2027.html", 0)}">Shooter games of 2027</a>: every FPS and TPS with a console filter and countdown</li>
<li><a href="{href("games-2028.html", 0)}">Games coming out in 2028</a>: what has already moved past 2027</li>
<li><a href="{href("remakes-2027.html", 0)}">Remakes and remasters of 2027</a>: every remake with a console filter, plus the undated ones</li>
<li><a href="{href("dlc-2027.html", 0)}">DLC coming in 2027</a>: every announced expansion with a console filter</li>
<li><a href="{href("games-like-hitman.html", 0)}">Games like Hitman</a>: stealth sandbox finder, plus the Hitman trilogy remaster and Hitman 4 news</li>
<li><a href="{href("games-like-monster-hunter.html", 0)}">Games like Monster Hunter</a>: hunting game finder, plus the Wilds Ascendance expansion and 2027 co-op games</li>
<li><a href="{href("winter-2027-anime.html", 0)}">Winter 2027 anime</a>: new shows and new seasons, Netflix filter</li>
<li><a href="{href("black-friday-game-sales-2026.html", 0)}">Black Friday 2026 game sales</a>: live "ends in" timers for PS Store, Xbox, Nintendo and Epic</li>
<li><a href="{href("gta-6-pc-release-date.html", 0)}">GTA 6 PC release date estimator</a>: when GTA 6 could reach PC, based on Rockstar's past games</li>
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
    # 26 Nov 2026 competitor watch: dated the same on both Game Informer's 2026 list and GamesRadar+ (upd. 25 Nov); platforms = both agree.
    ("2026-12-03", "Apple Crumble", ["PC"], "", "", "", False, "new"),
    ("2026-12-03", "Dumpster Gang", ["PC"], "", "", "", False, "new"),
    ("2026-12-03", "The Journey Home", ["PC"], "", "", "", False, "new"),
    ("2026-12-04", "Acts of Blood", ["PC"], "", "", "", False, "new"),
    ("2026-12-04", "A Game About Digging A Hole Together", ["PS5", "Xbox Series X|S", "PC", "Switch 2"], "", "", "", False, "new"),
    ("2026-12-04", "Petit Planet", ["PC"], "", "", "", False, "new"),
    ("2026-12-08", "Don't Fret", ["PS5", "Xbox Series X|S", "PC"], "", "", "", False, "new"),
    ("2026-12-09", "Hookeye", ["PC"], "", "", "", False, "new"),
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
            f'<p>17 December 2026 to 4 January 2027, per Valve\'s published schedule, so most December PC releases will get their first discount within weeks. Live timer on our <a href="{href("steam-sale-dates.html", 0)}">Steam sale dates</a> page Before that, the console Black Friday sales end between 29 November and 5 December: <a href="{href("black-friday-game-sales-2026.html", 0)}">every end date</a>.</p>'
            f'<div class="sec-head" style="margin-top:28px"><h2>Are there any big games out at Christmas 2026?</h2></div>'
            f'<p>No big confirmed launches land between {e(_dnice(_dlast[0])[:-5])} and the end of the year in the release calendars we checked. Publishers rarely launch in the last two weeks of December, '
            f'so the Christmas gap is the time to catch up on GTA 6 (out since 19 November 2026) and the early-December releases above.</p>'
            f'<div class="sec-head" style="margin-top:28px"><h2>What comes out next, in January 2027?</h2><span class="muted">{len(_jan)} dated</span></div>'
            f'<div class="out" style="margin-bottom:12px">' + "".join(f'<div class="row"><span>{_gname(g)}<br><span class="muted">{e(", ".join(g["platforms"]))}</span></span><b>{e(nice_date(g))}</b></div>' for g in _jan[:6]) + '</div>'
            f'<p class="muted"><a href="{href("months/january-2027.html", 0)}">See every January 2027 game →</a></p>'
            f'<p class="muted">Not on the list? We only add a December game once two trusted calendars agree on the date or the publisher confirms it. Smaller PC and mobile releases are left out.</p>'
            f'<div class="sec-head" style="margin-top:28px"><h2>Related pages and tools</h2></div><ul>'
            f'<li><a href="{href("new-games-this-week.html", 0)}">New games this week</a>: the same launches grouped Monday to Sunday</li>'
            f'<li><a href="{href("new-tv-shows-december-2026.html", 0)}">New TV shows in December 2026</a>: every premiere by streaming service</li>'
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
page("games-december-2026.html", f"Games Coming Out in December 2026: All {len(DEC26)} Releases",
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
              f'Asked about GTA 7 on GTA 6\'s launch day (19 November 2026), Take-Two boss Strauss Zelnick said: "Once you get through several hundred hours of the most incredible fun you\'ve ever heard, ask the question again." '
              f'Anything you read about GTA 7 right now is a rumour.</p>'
              f'<div class="sec-head" style="margin-top:28px"><h2>What is Rockstar making after GTA 6?</h2></div>'
              f'<p>Rockstar has not announced its next game. There is no confirmed Red Dead Redemption 3, Bully 2 or L.A. Noire sequel. For now its focus is GTA 6 and its online mode. '
              f'On Take-Two\'s November 2026 earnings call Zelnick only said Rockstar moves on to its next project after GTA 6, with no name. The most likely next release is GTA 6\'s online mode, which Rockstar has not announced; Bloomberg reported it is expected in 2027. '
              f'We will add Rockstar\'s next game to the board the day it is announced with a date.</p>'
              f'<div class="sec-head" style="margin-top:28px"><h2>When does GTA 6 Online come out?</h2></div>'
              f'<p>Not announced. Rockstar sold GTA 6 as a single-player game; Bloomberg and Twitch CEO Dan Clancy both point to multiplayer arriving in 2027. Until then, GTA Online (from GTA 5) keeps running.</p>'
              f'<div class="sec-head" style="margin-top:28px"><h2>Can you still play GTA 5 and GTA Online after GTA 6?</h2></div>'
              f'<p>Yes. GTA 5 is still sold and GTA Online is still running on PS5, Xbox Series X|S and PC. Take-Two has said GTA Online will keep being supported after GTA 6 launches, for as long as players stay engaged (TechRadar, GamesRadar+, PCGamesN). '
              f'Rockstar has not announced a shutdown date for GTA Online. Your GTA Online characters do not carry over to GTA 6, because GTA 6 has no online mode yet.</p>'
              f'<div class="sec-head" style="margin-top:28px"><h2>Is GTA 6 coming to PC?</h2></div>'
              f'<p>No PC version has been announced. GTA 6 launched on PS5 and Xbox Series X|S on 19 November 2026, and Take-Two did not give a PC date in its November 2026 earnings. '
              f'Past Rockstar games reached PC later: GTA 5 (2013) reached PC in April 2015, and Red Dead Redemption 2 (October 2018) in November 2019. '
              f'Estimate it yourself with our <a href="{href("gta-6-pc-release-date.html", 0)}">GTA 6 PC release date</a> tool.</p>'
              f'<div class="sec-head" style="margin-top:28px"><h2>Still playing GTA 6?</h2></div>'
              f'<p>Our sister site <a href="https://neoncoast.org/map" rel="noopener">NeonCoast</a> has an interactive GTA 6 map, a mission tracker, '
              f'every cheat code and a "Can my PC run GTA 6?" checker. There is no GTA 6 PC release date yet.</p>'
              f'<div class="sec-head" style="margin-top:28px"><h2>Related pages and tools</h2></div><ul>'
              f'<li><a href="{href("games-like-gta-6.html", 0)}">Games like GTA 6</a> you can play right now, on every platform</li>'
              f'<li><a href="{href("gta-6-pc-release-date.html", 0)}">GTA 6 PC release date</a>: what Rockstar said and a PC date estimator</li>'
              f'<li><a href="{href("biggest-games-2027.html", 0)}">The biggest games of 2027</a>: the full list, plus a top list you can share</li>'
              f'<li><a href="{href("rpgs-2027.html", 0)}">Every RPG coming in 2027</a>, with a console filter</li>'
              f'<li><a href="{href("games-like-elden-ring.html", 0)}">Games like Elden Ring</a> and the 2027 soulslikes</li>'
              f'<li><a href="{href("games-like-baldurs-gate-3.html", 0)}">Games like Baldur\'s Gate 3</a> and the 2027 CRPGs</li>'
              f'<li><a href="{href("release-clashes-2027.html", 0)}">2027 release clashes</a>: which of these land the same week</li>'
              f'<li><a href="{href("calendar.html", 0)}">2027 release calendar</a> and the <a href="{href("index.html", 0)}#board">departures board</a> for countdowns</li></ul></div></section>')
after_faq = [
    ("What should I play after GTA 6?", "If you liked the crime story, look at Stranger Than Heaven from the makers of Like a Dragon. For open-world driving, Forza Horizon 6 comes to PS5. For a huge world full of choices, Fable. The full list with dates is above."),
    ("What is the next big game after GTA 6?", (f"{_first['title']}, on {nice_date(_first)}, is the first big release on our list." if _first else "See the list above for dates.")),
    ("Which games after GTA 6 are coming to PS5?", ", ".join(f"{g['title']} ({nice_date(g)})" for g, _ in _picks if "PS5" in g["platforms"]) + "."),
    ("Is there a crime game like GTA coming in 2027?", "Stranger Than Heaven, from the Like a Dragon studio, is a crime drama dated " + (nice_date(_gby["stranger-than-heaven"]) if "stranger-than-heaven" in _gby else "for 2027") + ". It is the closest story match to GTA on our 2027 list."),
    ("Will there be a GTA 7?", "Rockstar has not announced GTA 7. There is no date, setting or official confirmation, so any GTA 7 news right now is a rumour."),
    ("What is Rockstar's next game after GTA 6?", "Rockstar has not announced one. Red Dead Redemption 3 and other sequels are unconfirmed. GTA 6's online mode is not announced either; Bloomberg reported it is expected in 2027."),
    ("When does GTA 6 Online come out?", "Rockstar has not announced GTA 6 Online. Bloomberg reported that multiplayer is expected in 2027."),
    ("What games come out after GTA 6 in December 2026?", f"{len(DEC26)} confirmed games, including Dragon Quest Monsters: The Withered World (3 December), Monster Hunter Wilds on Switch 2 (4 December), Professor Layton and the New World of Steam (10 December) and the Path of Exile 2 1.0 launch (11 December)."),
    ("Is GTA 6 coming to PC?", "Not yet. Rockstar has not announced a PC version or date. GTA 6 launched on PS5 and Xbox Series X|S on 19 November 2026."),
    ("Can you still play GTA 5 after GTA 6 comes out?", "Yes. GTA 5 is still on sale and GTA Online is still online. Take-Two has said it will keep supporting GTA Online after GTA 6, and no shutdown date has been announced."),
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
             f'<li><a href="{href("gta-6-pc-release-date.html", 0)}">GTA 6 PC release date</a>: what is known and a PC date estimator</li>'
             f'<li><a href="{href("new-games-this-week.html", 0)}">New games this week</a>, week by week</li>'
             f'<li><a href="{href("games-december-2026.html", 0)}">Games coming out in December 2026</a>, with a console filter</li>'
             f'<li><a href="{href("games-like-elden-ring.html", 0)}">Games like Elden Ring and Dark Souls</a>: soulslikes to play now and in 2027</li>'
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
# Competitor-watch gap 3 (27 Nov 2026): "date changes this month", built automatically from games.json history entries dated this month.
_dc_mon = datetime.date.fromisoformat(UPDATED)
_dc_keys = (f"{MONTHS[_dc_mon.month - 1][:3]} {_dc_mon.year}", f"{MONTHS[_dc_mon.month - 1]} {_dc_mon.year}")
_dc_rows = [(g, h) for g in GAMES for h in g.get("history", []) if any(k.lower() in h.get("when", "").lower() for k in _dc_keys)
            and not h.get("text", "").lower().startswith("still") and any(w in h.get("text", "").lower() for w in ("delay", "date", "moved", "set for", "dated"))]
_dc_rows.sort(key=lambda gh: (gh[0]["month"] or 13, gh[0]["date"] or "9999"))
_dc_html = ((f'<div class="sec-head"><h2>Which 2027 release dates changed in {MONTHS[_dc_mon.month - 1]} {_dc_mon.year}?</h2><span class="muted">{len(_dc_rows)}</span></div>'
             f'<p class="muted">Every date set, moved or delayed this month on our board, in release order. Built from each game\'s date history, so it updates on every data check.</p>'
             f'<div class="out" style="margin-bottom:28px">' + "".join(f'<div class="row"><span><strong>{_gname(g)}</strong><br><span class="muted">{e(h["when"])}: {e(h["text"])}</span></span><b>{e(nice_date(g))}</b></div>' for g, h in _dc_rows) + '</div>') if _dc_rows else "")
delays_body = (f'<header class="hero"><div class="wrap"><span class="kicker">Delay tracker</span>'
               f'<h1>Games delayed to 2027<br><span class="amber">{len(_delayed)} on our board.</span></h1>'
               f'<p class="lead">Every tracked game that has slipped into 2027 or moved to a later date, with its new date and what changed. We add each delay as soon as the publisher or two trusted outlets confirm it.</p>'
               f'<p class="muted" style="margin:0">Last checked {e(UPDATED)}</p></div></header>'
               f'<section><div class="wrap"><div class="out" style="margin-bottom:12px"><div class="row"><span><strong>Quick answer:</strong> {len(_delayed)} games on our 2027 board have been delayed' + (f", and {_dl_next['title']} ({nice_date(_dl_next)}) is the next to launch" if _dl_next else "") + '. The full list: '
               + (", ".join(f"{g['title']} (now {nice_date(g)})" for g in _delayed) if _delayed else "no tracked games are delayed right now") +
               '.' + (f' {len(_dl_multi)} have slipped more than once: ' + ", ".join(g["title"] for g in _dl_multi) + '.' if _dl_multi else '') +
               (f' {_dl_gta6[0][0]["title"]} is the clearest GTA 6 delay: its developer named GTA 6 as the reason.' if _dl_gta6 else '') + f'</span></div></div><div class="sec-head"><h2>Which games have been delayed to 2027?</h2><span class="muted">{len(_delayed)}</span></div>'
               f'<div class="out" style="margin-bottom:28px">{"".join(_drow(g) for g in _delayed)}</div>'
               + _dc_html +
               f'<div class="sec-head"><h2>Which delayed games are on my console?</h2></div><div class="out" style="margin-bottom:28px">'
               + "".join(f'<div class="row"><span><a href="{href("platforms/" + s2 + ".html", 0)}">{e(l2)}</a><br><span class="muted">{e(", ".join(g["title"] for g in _delayed if p2 in g["platforms"]) or "None right now")}</span></span>'
                         f'<b>{sum(1 for g in _delayed if p2 in g["platforms"])} delayed</b></div>' for p2, s2, l2 in PLAT_PAGES_FOOT) +
               f'</div>' + _dl_next_html + _dl_loose_html + _dl_multi_html + _dl_gta6_html + _dl_early_html + f'<div class="sec-head"><h2>Which 2027 games were delayed to 2028?</h2></div>'
               f'<p>Tomb Raider: Catalyst is the big one: announced for 2027, it now follows in 2028, per Amazon Games (July 2026). The Witcher 4 was never a 2027 game; CD Projekt is targeting 2028. See every game aimed at 2028 on <a href="{href("games-2028.html", 0)}">games coming out in 2028</a>.</p>'
               f'<div class="sec-head"><h2>Which month do most delayed games land in?</h2></div>'
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
    (f"Which release dates changed in {MONTHS[_dc_mon.month - 1]} {_dc_mon.year}?", ("; ".join(f"{g['title']}: {h['text'].rstrip('.')}" for g, h in _dc_rows) + ".") if _dc_rows else "No tracked date changed this month yet."),
    ("Which 2027 games were delayed to 2028?", "Tomb Raider: Catalyst. It was announced for 2027 and Amazon Games now says 2028."),
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
GP_OTHER = [("Bad Magpie", "Early 2027"), ("Join Us", "March 2027"),
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
    f'<p>No. CD Projekt said in August 2026 that it is targeting 2028 for The Witcher 4, so it is the only Most Anticipated nominee that is not a 2027 game. It is not on our 2027 board. If that changes, we will add it. The next new Witcher story is <a href="{href("games/the-witcher-3-songs-of-the-past.html", 0)}">Songs of the Past</a>, a Witcher 3 expansion due in 2027; see <a href="{href("games-like-the-witcher-3.html", 0)}">games like The Witcher 3</a> for what to play until then.</p>'
    f'<div class="sec-head" style="margin-top:22px"><h2>Who will win Game of the Year at The Game Awards 2026?</h2><span class="muted">our opinion</span></div>'
    f'<p>Our prediction (an opinion, not news): Grand Theft Auto 6. It leads the nominations with 8, it launched on 19 November 2026, and betting and prediction markets such as OLBG, Covers and Polymarket all list it as the clear favourite. The likeliest upset is Resident Evil Requiem, which has 6 nominations including Game of the Year. The jury decides 90% of the result, so fan buzz alone will not settle it. Make your own picks in the predictor below.</p></div></section>'
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
    ("Who will win Game of the Year at The Game Awards 2026?", "Nobody knows until 10 December. Our opinion: Grand Theft Auto 6, which leads with 8 nominations and is the favourite in betting and prediction markets. Resident Evil Requiem is the likeliest upset."),
    ("Is Forza Horizon 6 nominated at The Game Awards 2026?", "Yes, twice: Best Sports / Racing Game and Innovation in Accessibility. Its PS5 version comes out on " + nice_date(_gbs["forza-horizon-6"]) + "."),
]
page("game-awards-2026.html", "The Game Awards 2026 Start Time, Disney+ Stream and Nominees",
     "The Game Awards 2026 starts 7:30pm ET / 4:30pm PT on 10 Dec (12:30am UK). Your local time, Disney+, YouTube and Twitch, and every nominee (GTA 6 leads with 8).",
     tga_body, 0, tga_faq, crumbs=[("Home", DOMAIN + "/"), ("Biggest games of 2027", canon("biggest-games-2027.html")), ("The Game Awards 2026", canon("game-awards-2026.html"))])

# ---------------- ABOUT / PRIVACY / 404 ----------------
_ab_n = len(GAMES); _ab_d = sum(1 for g in GAMES if g["date"]); _ab_del = sum(1 for g in GAMES if g["status"] == "delayed")
page("about.html", "About DayOneDrop: How We Track 2027 Release Dates | DayOneDrop",
     f"DayOneDrop is an independent tracker of {_ab_n} games coming in 2027. How we check every date, update delays, pick sources and fix mistakes.",
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
page("privacy.html", "Privacy Policy | DayOneDrop", "DayOneDrop privacy policy: what we collect, how cookies, Google AdSense, Google Analytics and affiliate links work, and how to delete your email.",
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
page("xbox-games-showcase-2027.html", "Xbox Games Showcase 2027: Likely Date and Past Shows",
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
    f'<li><a href="{href("black-friday-game-sales-2026.html", 0)}">PS Store Black Friday sale</a>: ends 30 November, with a live timer</li>'
    f'<li><a href="{href("new-games-this-week.html", 0)}">New games this week</a></li></ul></div></section>')
psp_faq = [
    ("What are the PS Plus games for December 2026?", "Tony Hawk's Pro Skater 3+4, Dragon Ball Xenoverse 2 and Amnesia: The Bunker, announced on the PlayStation Blog on 25 November 2026. Claim them from 1 December 2026 to 4 January 2027."),
    ("What are the PS Plus games for November 2026?", "Dead Island 2 (PS5, PS4), Tomb Raider IV–VI Remastered (PS5, PS4) and Monster Train 2 (PS5), claimable from 3 to 30 November 2026."),
    ("When are PS Plus monthly games announced?", "Usually on the last Wednesday of the month, on the PlayStation Blog, often around 4:30 pm UK time."),
    ("When do new PS Plus games come out?", "On the first Tuesday of the month. The previous month's games can be claimed until then."),
    ("Do I keep PS Plus games forever?", "You keep claimed monthly games for as long as you have an active PS Plus subscription of any tier."),
]
page("ps-plus-monthly-games.html", "PS Plus December 2026 Games: Tony Hawk 3+4, Xenoverse 2",
     "PS Plus December 2026 monthly games: Tony Hawk's Pro Skater 3+4, Dragon Ball Xenoverse 2 and Amnesia: The Bunker, 1 Dec to 4 Jan. November's games end 30 Nov.",
     psp_body, 0, psp_faq, crumbs=[("Home", DOMAIN + "/"), ("PS Plus monthly games", canon("ps-plus-monthly-games.html"))])

# ---------------- EPIC FREE GAMES (Keyword Planner worldwide 25 Nov 2026: "epic free games" 10k-100k, low comp). UPDATE EVERY THURSDAY after 16:00 UTC. ----------------
EPIC = [  # (from, to, games, status) Sources: SteamDB promo pages, NerdZap 13 Nov, GGRecon 12 Nov, Clouddosage, Kyber's Corner.
    ("26 Nov", "3 Dec 2026", "Bread & Fred (+ A Tiny Sticker Tale on mobile, a Firestone Online Idle RPG bundle)", "now"),  # Kyber's Corner, GameGrin, The Freebie Guy, Out of Games 26 Nov
    ("19 Nov", "26 Nov 2026", "Mark of the Deep, Alien: Isolation", "past"),
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
    f'<li><a href="{href("black-friday-game-sales-2026.html", 0)}">Black Friday 2026 game sales</a>: Epic\'s Premium Editions Sale ends 1 December</li>'
    f'<li><a href="{href("platforms/pc.html", 0)}">Every PC game coming in 2027</a></li>'
    f'<li><a href="{href("new-games-this-week.html", 0)}">New games this week</a></li></ul></div></section>')
ep_faq = [
    ("What is the Epic free game this week?", f"{_ep_now[2]}, free to keep until {_ep_now[1]} at 11 am ET (4 pm UK)."),
    ("What is the next free game on Epic?", (f"{_ep_next[0][2]}, from {_ep_next[0][0]} to {_ep_next[0][1]}." if _ep_next else "Not confirmed yet: Epic usually reveals it when the current week's games go live, and this page adds it once two sources list it.")),
    ("What time do Epic free games change?", "Every Thursday at 11 am ET, which is 4 pm UK time, 9 pm in Pakistan and 9:30 pm in India."),
    ("Do you keep Epic free games forever?", "Yes. Once you claim a game during its free week it stays in your Epic library."),
    ("Does Epic do mystery games in December?", "In recent years Epic has given away a free game every day over the holidays. It hasn't announced the 2026 event yet."),
]
page("epic-free-games.html", "Epic Free Games This Week and Next: Every Free Game",
     f"Epic Games Store free games this week: {_ep_now[2]} until {_ep_now[1]}." + (f" Next: {_ep_next[0][2]}." if _ep_next else "") + (" Plus the swap time in your time zone." if len(f"Epic Games Store free games this week: {_ep_now[2]} until {_ep_now[1]}." + (f" Next: {_ep_next[0][2]}." if _ep_next else "")) <= 122 else ""),
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
           f'<div class="sec-head" style="margin-top:28px"><h2>Is there a Steam Black Friday sale?</h2></div>'
           f'<p>No. Valve does not hold a Black Friday sale, and the 2026 Autumn Sale already ran on 1 to 8 October. Some publishers discount their own games on Steam over Black Friday week, but the next storewide sale is the Winter Sale on 17 December. The console and Epic Black Friday sales end between 29 November and 5 December: see <a href="{href("black-friday-game-sales-2026.html", 0)}">every Black Friday 2026 game sale end date</a>.</p>'
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
    ("Is there a Steam Black Friday sale in 2026?", "No. Valve's Autumn Sale ran 1 to 8 October 2026 and the next storewide sale is the Winter Sale from 17 December. Only some publishers discount their own games for Black Friday."),
    ("What time does the Steam sale start?", "Usually 10 am Pacific, which is 1 pm Eastern, 6 pm UK and 11 pm Pakistan time. Valve's schedule lists only the dates."),
]
page("steam-sale-dates.html", "Steam Sale Dates 2026-2027: Winter, Spring and Summer Sales",
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
page("nintendo-direct.html", "Next Nintendo Direct: Date, Last Direct and Switch 2 Games",
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
           f'<li><a href="{href("games-2028.html", 0)}">Games coming out in 2028</a>: The Witcher 4, Tomb Raider: Catalyst, ARK 2</li>'
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
page("games-without-release-date-2027.html", f"2027 Games With No Release Date Yet: All {len(_nd_g)} by Console",
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
page("countdown.html", "Game Release Countdown 2027: Live Timers for Every Game",
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
            + f'<div class="sec-head" style="margin-top:28px"><h2>What movies come out before 2027, in December 2026?</h2></div>'
            f'<p>Avengers: Doomsday and Dune: Part Three both open on 18 December 2026, and Jumanji 3 and Werwulf on Christmas Day. See every film, with a week filter, on <a href="{href("movies-december-2026.html", 0)}">movies coming out in December 2026</a>.</p>'
            f'<div class="sec-head" style="margin-top:28px"><h2>Related pages and tools</h2></div><ul>'
            f'<li><a href="{href("movies-december-2026.html", 0)}">Movies coming out in December 2026</a>: Avengers: Doomsday, Dune: Part Three, Jumanji 3</li>'
            f'<li><a href="{href("movies-january-2027.html", 0)}">Movies coming out in January 2027</a>: Children of Blood and Bone, Animal Friends</li>'
            f'<li><a href="{href("winter-2027-anime.html", 0)}">Winter 2027 anime</a>: Sakamoto Days S2, One-Punch Man, The One Piece</li>'
            f'<li><a href="{href("new-tv-shows-december-2026.html", 0)}">New TV shows in December 2026</a>: Harry Potter, Emily in Paris and more</li>'
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
          ("When does Frozen 3 come out?", "24 November 2027, Thanksgiving week in the US."),
          ("What big movies come out in December 2026?", "Avengers: Doomsday and Dune: Part Three (18 December 2026), The Angry Birds Movie 3 (23 December), Jumanji 3 and Werwulf (25 December).")]
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
           f'<div class="sec-head" style="margin-top:28px"><h2>What games are like Dark Souls?</h2></div>'
           f'<p>The same list works: Dark Souls III, Bloodborne, Sekiro, Lies of P, Lords of the Fallen and Wo Long: Fallen Dynasty are the closest, because they keep Dark Souls\' tight, linear levels and shortcut-filled maps rather than Elden Ring\'s open world. In 2027, Lords of the Fallen II (April) and Wo Long 2 (4 March) are the big new soulslikes. For 2D, try <a href="{href("games-like-hollow-knight.html", 0)}">games like Hollow Knight</a>; for big action without the punishing difficulty, see <a href="{href("games-like-god-of-war.html", 0)}">games like God of War</a>.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>Will there be a Dark Souls 4?</h2></div>'
           f'<p>Not announced. FromSoftware has released no new Dark Souls since Dark Souls III (2016) and has not revealed a fourth game. Its next release is The Duskbloods on Switch 2 in 2027.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>What is the hardest game like Elden Ring?</h2></div>'
           f'<p>Most players name Sekiro: Shadows Die Twice: there are no builds or summons to fall back on, so every boss is a straight duel. Bloodborne and Lies of P are close behind. If you want something gentler, Black Myth: Wukong and Lords of the Fallen (2023) give you more room for mistakes.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>Related pages and tools</h2></div><ul>'
           f'<li><a href="{href("games/lords-of-the-fallen-ii.html", 0)}">Lords of the Fallen 2 release date</a> and delay history</li>'
           f'<li><a href="{href("games/wo-long-2.html", 0)}">Wo Long 2 release date</a></li>'
           f'<li><a href="{href("rpgs-2027.html", 0)}">Every RPG of 2027</a></li>'
           f'<li><a href="{href("games-like-gta-6.html", 0)}">Games like GTA 6</a></li>'
           f'<li><a href="{href("games-like-hollow-knight.html", 0)}">Games like Hollow Knight and Silksong</a>: metroidvanias now and in 2027</li>'
           f'<li><a href="{href("games-like-hades.html", 0)}">Games like Hades</a>: roguelites now and in 2027</li>'
           f'<li><a href="{href("games-like-zelda.html", 0)}">Games like Zelda</a>: open worlds and dungeons, now and in 2027</li>'
           f'<li><a href="{href("winter-2027-anime.html", 0)}">Winter 2027 anime</a>, including the Sekiro anime, Sekiro: No Defeat</li>'
           f'<li><a href="{href("countdown.html", 0)}">Game release countdown</a></li></ul></div></section>')
er_faq = [("What games are like Elden Ring?", "Dark Souls III, Sekiro, Bloodborne, Elden Ring Nightreign, Lies of P, Black Myth: Wukong, Lords of the Fallen, Wo Long: Fallen Dynasty, Remnant II and Hollow Knight: Silksong."),
          ("What soulslike games come out in 2027?", _and([g['title'] + ' (' + nice_date(g) + ')' for g in _er_soon] + [x[0] + ' (' + x[4] + ')' for x in ER_EXTRA]) + "."),
          ("Is Elden Ring 2 announced?", "No. FromSoftware's next game is The Duskbloods, a Switch 2 exclusive."),
          ("What games are like Dark Souls?", "Dark Souls III, Bloodborne, Sekiro, Lies of P, Lords of the Fallen and Wo Long: Fallen Dynasty. In 2027, Lords of the Fallen II and Wo Long 2."),
          ("Will there be a Dark Souls 4?", "Not announced. FromSoftware has not revealed a new Dark Souls game since Dark Souls III in 2016."),
          ("Is Elden Ring on Switch 2?", "Yes. Elden Ring: Tarnished Edition launched on Switch 2 on 28 August 2026."),
          ("When does Lords of the Fallen 2 come out?", "April 2027 on PS5, Xbox Series X|S, Switch 2 and PC. CI Games says the exact day is due in December 2026.")]
page("games-like-elden-ring.html", "Games Like Elden Ring: Best Soulslikes Now and in 2027 | DayOneDrop",
     "Games like Elden Ring on PS5, Xbox, PC and Switch 2: Lies of P, Sekiro, Wukong and more, plus 2027 soulslikes Wo Long 2, Lords of the Fallen II, Duskbloods.",
     er_body, 0, er_faq, crumbs=[("Home", DOMAIN + "/"), ("2027 games by genre", canon("games-by-genre-2027.html")), ("Games like Elden Ring", canon("games-like-elden-ring.html"))])


# ---------------- GTA 6 PC RELEASE DATE (26 Nov 2026, demand: "gta 6 pc release date", "is gta 6 on pc", "gta 6 online release date") ----------------
# Facts: GTA 6 out 19 Nov 2026 on PS5 + Xbox Series X|S (Dexerto, Vice, VGC 20 Nov 2026). No PC version announced (VGC, Vice 20 Nov; ComicBook 11 Nov).
# Reports: GamesBeat (4 industry sources) Q1 2027 PC target, via Vice; GameGPU March 2027 claim (Shattered 25 Nov: unconfirmed). Online: Rockstar has not announced;
# Twitch CEO Dan Clancy to Bloomberg "next year" (GTA Base 22 Nov). Zelnick TBPN quote 19 Nov via Dexerto. Past gaps: GTA V (VGC), RDR2 (Vice, Shattered), GTA IV (Rockstar 2008).
GTA6_OUT = datetime.date(2026, 11, 19)
GTA_PAST = [  # (game, console date, PC date, note)
    ("Grand Theft Auto IV", datetime.date(2008, 4, 29), datetime.date(2008, 12, 2), "PS3 and Xbox 360 first, PC seven months later."),
    ("Red Dead Redemption 2", datetime.date(2018, 10, 26), datetime.date(2019, 11, 5), "PS4 and Xbox One first, PC just over a year later."),
    ("Grand Theft Auto V", datetime.date(2013, 9, 17), datetime.date(2015, 4, 14), "PS3 and Xbox 360 first, then PS4 and Xbox One (18 Nov 2014), then PC."),
]
def _gp_nice(d): return nice_date({"date": d.isoformat(), "window": ""})
_gp_est = [(t, (p - c).days, GTA6_OUT + datetime.timedelta(days=(p - c).days), n, c, p) for t, c, p, n in GTA_PAST]
_gp_rows = "".join(f'<div class="row"><span><strong>{e(t)}</strong><br><span class="muted">Console {e(_gp_nice(c))} · PC {e(_gp_nice(p))} · {e(n)}</span></span><b>{gap} days</b></div>' for t, gap, est, n, c, p in _gp_est)
_gp_chips = ('<div class="chips" role="group" aria-label="Follow which past Rockstar game">'
             + "".join(f'<button class="chip" type="button" data-g6="{est.isoformat()}" data-g6-t="{e(t)}" data-g6-g="{gap}" aria-pressed="{"true" if i == 1 else "false"}">Like {e(t.replace("Grand Theft Auto", "GTA").replace("Red Dead Redemption", "RDR"))}</button>' for i, (t, gap, est, n, c, p) in enumerate(_gp_est))
             + '<button class="chip" type="button" data-g6="2027-03-31" data-g6-t="the GamesBeat report (first quarter of 2027)" data-g6-g="0" aria-pressed="false">Like the Q1 2027 report</button></div>')
_gp_pc = [x for x in LIKE_GTA if "pc" in x[3].split()]
_gp_quick = ("GTA 6 has no PC release date. It came out on PS5 and Xbox Series X|S on 19 November 2026, and Rockstar has not announced a PC version. "
             f"If it follows Red Dead Redemption 2's gap, PC would land around {_gp_nice(_gp_est[1][2])}; a GamesBeat report says Rockstar is aiming for early 2027, but that is not confirmed.")
_gp_body = (f'<header class="hero"><div class="wrap"><span class="kicker">GTA 6 on PC</span>'
            f'<h1>GTA 6 PC release date:<br><span class="amber">not announced yet.</span></h1>'
            f'<p class="lead">What Rockstar has said, what the reports claim, and a tool that estimates when GTA 6 could reach PC based on Rockstar\'s past games.</p>'
            f'<p class="muted" style="margin:0">Last checked {e(UPDATED)} · GTA 6 on console since {e(_gp_nice(GTA6_OUT))}</p></div></header>'
            f'<section><div class="wrap"><div class="out" style="margin-bottom:12px"><div class="row"><span><strong>Quick answer:</strong> {e(_gp_quick)}</span></div></div>'
            f'<div class="out" style="margin-bottom:24px">'
            f'<div class="row"><span>Is GTA 6 out on PC?</span><b>No</b></div>'
            f'<div class="row"><span>PC version announced?</span><b>No</b></div>'
            f'<div class="row"><span>Out on PS5 and Xbox Series X|S</span><b>{e(_gp_nice(GTA6_OUT))}</b></div>'
            f'<div class="row"><span>GTA 6 Online announced?</span><b>No</b></div>'
            f'<div class="row"><span>PC players have waited</span><b class="mono" data-since="{GTA6_OUT.isoformat()}">{(_TD - GTA6_OUT).days} days</b></div></div>'
            f'<div class="tool" id="g6-tool" style="margin-bottom:24px"><h2 style="font-size:1.5rem;margin-top:0">When could GTA 6 come to PC?</h2>'
            f'<p class="muted">Pick a past Rockstar launch. We add its console-to-PC gap to GTA 6\'s console date. This is an estimate, not a release date.</p>{_gp_chips}'
            f'<p class="mono amber" id="g6-out" aria-live="polite" style="margin:12px 0 6px">If GTA 6 follows Red Dead Redemption 2: about {e(_gp_nice(_gp_est[1][2]))}</p>'
            f'<div class="cdw"><span class="lbl" id="g6-lbl">Countdown to the estimate</span><div class="cd" id="g6-cd" data-countdown="{_gp_est[1][2].isoformat()}">'
            '<div class="cd-unit"><span class="flaps" data-u="0"></span><span>Days</span></div><div class="cd-unit"><span class="flaps" data-u="1"></span><span>Hrs</span></div>'
            '<div class="cd-unit"><span class="flaps" data-u="2"></span><span>Min</span></div><div class="cd-unit"><span class="flaps" data-u="3"></span><span>Sec</span></div></div></div></div>'
            f'<div class="sec-head"><h2>How long did Rockstar games take to reach PC?</h2><span class="muted">{len(GTA_PAST)} games</span></div>'
            f'<div class="out" style="margin-bottom:28px">{_gp_rows}</div>'
            f'<div class="sec-head"><h2>Has Rockstar said anything about GTA 6 on PC?</h2></div>'
            f'<p>No. Rockstar\'s launch announcement and Take-Two\'s November 2026 earnings named only PS5 and Xbox Series X|S. Take-Two boss Strauss Zelnick has said Rockstar launches on console first because that is where the core GTA audience is. '
            f'Rockstar has brought every big game since GTA IV to PC later, so a PC version is likely, but there is no official word.</p>'
            f'<div class="sec-head" style="margin-top:28px"><h2>What do the GTA 6 PC rumours say?</h2></div><div class="out" style="margin-bottom:12px">'
            f'<div class="row"><span><strong>First quarter of 2027</strong><br><span class="muted">GamesBeat, citing four industry sources (October 2026, reported by Vice). A report, not a confirmation.</span></span><b>Report</b></div>'
            f'<div class="row"><span><strong>March 2027, with GTA 6 Online the same day</strong><br><span class="muted">A GameGPU post on 25 November 2026. It reads Take-Two financial reports and names no insider source.</span></span><b>Weak</b></div></div>'
            f'<p class="muted" style="margin-bottom:28px">We will put the real date on the <a href="{href("index.html", 0)}#board">departures board</a> the day Rockstar announces it.</p>'
            f'<div class="sec-head"><h2>When does GTA 6 Online come out?</h2></div>'
            f'<p>Rockstar has not announced it. Its pre-order announcement called GTA 6 a single-player experience. Bloomberg reported that multiplayer is expected in 2027, and Twitch CEO Dan Clancy told Bloomberg he expects "an even bigger" bump "next year when they launch multiplayer". GTA Online (the GTA 5 version) is still running on PC and consoles.</p>'
            f'<div class="sec-head" style="margin-top:28px"><h2>Will there be a GTA 7?</h2></div>'
            f'<p>Not announced. Asked about GTA 7 on GTA 6\'s launch day, Zelnick said: "Once you get through several hundred hours of the most incredible fun you\'ve ever heard, ask the question again." See <a href="{href("after-gta-6.html", 0)}">what Rockstar does after GTA 6</a>.</p>'
            f'<div class="sec-head" style="margin-top:28px"><h2>What can I play on PC while I wait for GTA 6?</h2><span class="muted">{len(_gp_pc)}</span></div>'
            f'<div class="out" style="margin-bottom:12px">' + "".join(f'<div class="row"><span><strong>{e(x[0])}</strong><br><span class="muted">{e(x[2])}</span></span></div>' for x in _gp_pc[:6]) + '</div>'
            f'<p class="muted">More picks with a platform filter: <a href="{href("games-like-gta-6.html", 0)}">games like GTA 6</a>. Want to know if your PC will cope? <a href="https://neoncoast.org" rel="noopener">NeonCoast</a> has a "Can my PC run GTA 6?" checker.</p>'
            f'<div class="sec-head" style="margin-top:28px"><h2>Related pages and tools</h2></div><ul>'
            f'<li><a href="{href("after-gta-6.html", 0)}">What to play after GTA 6</a>: the big games of 2027</li>'
            f'<li><a href="{href("platforms/pc.html", 0)}">Every PC game coming in 2027</a></li>'
            f'<li><a href="{href("steam-sale-dates.html", 0)}">Steam sale dates</a>: the Winter Sale starts 17 December</li>'
            f'<li><a href="{href("countdown.html", 0)}">Game release countdown</a></li></ul></div></section>')
gp_faq = [("Is GTA 6 out on PC?", "No. GTA 6 came out on 19 November 2026 on PS5 and Xbox Series X|S only. Rockstar has not announced a PC version."),
          ("When is the GTA 6 PC release date?", f"There is no date. A GamesBeat report says Rockstar is aiming for the first quarter of 2027. If it follows Red Dead Redemption 2's gap of just over a year, PC would arrive around {_gp_nice(_gp_est[1][2])}."),
          ("Will GTA 6 come to PC?", "Rockstar has not confirmed it, but every big Rockstar game since GTA IV has reached PC later: GTA IV after 7 months, Red Dead Redemption 2 after just over a year and GTA V after about 19 months."),
          ("When does GTA 6 Online come out?", "Rockstar has not announced GTA 6 Online. Bloomberg reported that multiplayer is expected in 2027."),
          ("Is the GTA 6 March 2027 PC date real?", "No source has confirmed it. It comes from a GameGPU post that reads Take-Two's financial reports and names no insider.")]
page("gta-6-pc-release-date.html", "GTA 6 PC Release Date: Is GTA 6 on PC? (Nov 2026) | DayOneDrop",
     f"GTA 6 has no PC release date: it is out on PS5 and Xbox Series X|S since 19 Nov 2026. What Rockstar said, the Q1 2027 report, and a PC date estimator.",
     _gp_body, 0, gp_faq, crumbs=[("Home", DOMAIN + "/"), ("After GTA 6", canon("after-gta-6.html")), ("GTA 6 PC release date", canon("gta-6-pc-release-date.html"))])


# ---------------- NEW TV SHOWS DECEMBER 2026 (26 Nov 2026, demand W2/R4: "new tv shows december 2026", "new tv shows" 100k-1M) ----------------
# Only shows that 2+ of Rotten Tomatoes (18 Nov), Deadline/Yahoo premiere list (4 Nov), ScreenRant (11 Nov), Dexerto (9 Nov), Popverse list with the same date.
TV_DEC = [  # (title, date, service key, kind, note)
    ("Trinity", "2026-12-01", "netflix", "new", "New series."),
    ("Bad Monkey, Season 2", "2026-12-02", "apple", "ret", "Vince Vaughn's Florida crime comedy returns."),
    ("Pride and Prejudice", "2026-12-03", "netflix", "new", "New limited series of the Jane Austen novel."),
    ("P-Valley, Season 3", "2026-12-04", "starz", "ret", "Final season."),
    ("Only Murders in the Building, Season 6", "2026-12-08", "hulu", "ret", "The mystery comedy heads to London. One list says 6 December; three say 8 December."),
    ("Maxton Hall: The World Between Us, Season 3", "2026-12-09", "prime", "ret", "Final season."),
    ("Lil Kev, Season 2", "2026-12-09", "paramount", "ret", "Adult animated comedy."),
    ("The Murder of JonBenét Ramsey", "2026-12-10", "netflix", "new", "Limited series."),
    ("Ghosts: holiday special", "2026-12-10", "cbs", "special", "Christmas special, not a new season."),
    ("Ted: The Animated Series", "2026-12-17", "peacock", "new", "Animated series from Seth MacFarlane's Ted."),
    ("Unaccustomed Earth", "2026-12-17", "netflix", "new", "New drama series."),
    ("Quiztopia", "2026-12-17", "netflix", "new", "New series."),
    ("Beyond Society", "2026-12-18", "netflix", "new", "New docuseries."),
    ("Frisco King", "2026-12-18", "paramount", "new", "Tulsa King spin-off."),
    ("Emily in Paris, Season 6", "2026-12-24", "netflix", "ret", "Final season."),
    ("Harry Potter (HBO series), Season 1", "2026-12-25", "hbo", "new", "The new TV adaptation starts with Philosopher's Stone."),
    ("Beyond the Gates, Season 3", "2026-12-29", "cbs", "ret", "Daytime drama."),
    ("Mayfair Witches, Season 3", "2026-12-30", "amc", "ret", "Anne Rice's witches return."),
]
TV_SVC = [("netflix", "Netflix"), ("hbo", "HBO Max"), ("hulu", "Hulu / Disney+"), ("prime", "Prime Video"), ("apple", "Apple TV"), ("paramount", "Paramount+"), ("peacock", "Peacock"), ("cbs", "CBS"), ("starz", "Starz"), ("amc", "AMC")]
_TVS = dict(TV_SVC)
_TVK = {"new": "New series", "ret": "New season", "special": "Special"}
def _tv_gcal(t, d, s):
    a = d.replace("-", ""); b = (datetime.date.fromisoformat(d) + datetime.timedelta(days=1)).isoformat().replace("-", "")
    return "https://calendar.google.com/calendar/render?action=TEMPLATE&text=" + _qp(t + " on " + s) + f"&dates={a}/{b}&details=" + _qp("Premiere date via getdayonedrop.com/new-tv-shows-december-2026")
def _tvrow(x):
    t, d, s, k, n = x
    return (f'<div class="row" data-ts="{s}" data-tk="{k}"><span><strong>{e(t)}</strong><br><span class="muted">{e(n)}</span><br><span class="muted">{e(_TVS[s])} · {e(_TVK[k])} · '
            f'<a href="{e(_tv_gcal(t, d, _TVS[s]))}" rel="nofollow noopener" target="_blank">Add to Google Calendar</a></span></span><b>{e(_mv_nice(d))}</b></div>')
_tv_used = [(k, l) for k, l in TV_SVC if any(x[2] == k for x in TV_DEC)]
_tv_chips = ('<div class="chips" role="group" aria-label="Service"><button class="chip" type="button" data-tv-s="" aria-pressed="true">Every service</button>'
             + "".join(f'<button class="chip" type="button" data-tv-s="{k}" aria-pressed="false">{e(l)}</button>' for k, l in _tv_used) + '</div>'
             '<div class="chips" role="group" aria-label="Type" style="margin-top:8px"><button class="chip" type="button" data-tv-k="" aria-pressed="true">Everything</button>'
             + "".join(f'<button class="chip" type="button" data-tv-k="{k}" aria-pressed="false">{e(l)}</button>' for k, l in _TVK.items()) + '</div>')
def _tv_on(s): return [x for x in TV_DEC if x[2] == s]
def _tv_names(xs): return _and([f"{x[0]} ({_mv_nice(x[1])})" for x in xs])
_tv_hp = next(x for x in TV_DEC if x[0].startswith("Harry Potter"))
_tv_quick = ("The biggest new TV shows in December 2026 are HBO's Harry Potter series (25 December, HBO Max), the final season of Emily in Paris (24 December, Netflix), "
             "Netflix's Pride and Prejudice (3 December), Only Murders in the Building season 6 (8 December, Hulu) and Ted: The Animated Series (17 December, Peacock). "
             f"We list {len(TV_DEC)} premieres in total.")
_tv_weeks = [("1 to 7 December", "2026-12-01", "2026-12-07"), ("8 to 14 December", "2026-12-08", "2026-12-14"), ("15 to 21 December", "2026-12-15", "2026-12-21"), ("22 to 31 December", "2026-12-22", "2026-12-31")]
_tv_body = (f'<header class="hero"><div class="wrap"><span class="kicker">TV · December 2026</span>'
            f'<h1>New TV shows in December 2026:<br><span class="amber">every premiere date.</span></h1>'
            f'<p class="lead">New series and returning seasons on Netflix, HBO Max, Hulu, Prime Video, Apple TV, Paramount+ and Peacock, with a filter by service and a calendar reminder for each show.</p>'
            f'<p class="muted" style="margin:0">Last checked {e(UPDATED)} · {len(TV_DEC)} premieres</p></div></header>'
            f'<section><div class="wrap"><div class="out" style="margin-bottom:12px"><div class="row"><span><strong>Quick answer:</strong> {e(_tv_quick)}</span></div></div>'
            f'<div class="tool" id="tv-tool" style="margin-bottom:24px"><h2 style="font-size:1.5rem;margin-top:0">What is new on my streaming service in December?</h2>'
            f'<p class="muted">Pick a streaming service and a type. Your choice is remembered on this device.</p>{_tv_chips}'
            f'<p class="mono amber" id="tv-count" aria-live="polite" style="margin:12px 0 0">{len(TV_DEC)} shows</p></div>'
            f'<div class="sec-head"><h2>What new TV shows come out in December 2026?</h2><span class="muted">in date order</span></div>'
            f'<div class="out" id="tv-list" style="margin-bottom:10px">{"".join(_tvrow(x) for x in TV_DEC)}</div><p class="empty" id="tv-none" hidden>Nothing matches. Try "Every service".</p>'
            f'<div class="cdw" style="margin-top:18px"><span class="lbl">Countdown to Harry Potter on HBO Max</span><div class="cd" data-countdown="{_tv_hp[1]}">'
            '<div class="cd-unit"><span class="flaps" data-u="0"></span><span>Days</span></div><div class="cd-unit"><span class="flaps" data-u="1"></span><span>Hrs</span></div>'
            '<div class="cd-unit"><span class="flaps" data-u="2"></span><span>Min</span></div><div class="cd-unit"><span class="flaps" data-u="3"></span><span>Sec</span></div></div></div></div></section>'
            + AD.format("tv-mid") +
            f'<section><div class="wrap"><div class="sec-head"><h2>When does the Harry Potter TV series come out?</h2></div>'
            f'<p>25 December 2026 (Christmas Day) on HBO Max. The first season adapts Harry Potter and the Philosopher\'s Stone, with one book per season planned.</p>'
            f'<div class="sec-head" style="margin-top:28px"><h2>What is new on Netflix in December 2026?</h2><span class="muted">{len(_tv_on("netflix"))}</span></div><p>{e(_tv_names(_tv_on("netflix")))}.</p>'
            f'<div class="sec-head" style="margin-top:28px"><h2>What is new on Hulu, Prime Video, Apple TV, Paramount+ and Peacock?</h2></div><ul>'
            + "".join(f'<li><strong>{e(l)}:</strong> {e(_tv_names(_tv_on(k)))}</li>' for k, l in _tv_used if k not in ("netflix", "cbs", "starz", "amc")) +
            f'</ul><div class="sec-head" style="margin-top:28px"><h2>Which shows end in December 2026?</h2></div>'
            f'<p>Final seasons: Emily in Paris season 6 (24 December), Maxton Hall season 3 (9 December) and P-Valley season 3 (4 December).</p>'
            f'<div class="sec-head" style="margin-top:28px"><h2>What is premiering each week?</h2></div><div class="out" style="margin-bottom:28px">'
            + "".join(f'<div class="row"><span><strong>{e(w)}</strong><br><span class="muted">{e(_and([x[0] for x in TV_DEC if a <= x[1] <= b]))}</span></span><b>{sum(1 for x in TV_DEC if a <= x[1] <= b)}</b></div>' for w, a, b in _tv_weeks) +
            f'</div><div class="sec-head"><h2>What games and movies are out in December too?</h2></div>'
            f'<p>December 2026 also has {len(DEC26)} game launches, including Monster Hunter Wilds on Switch 2 (4 December), and The Game Awards on 10 December. See <a href="{href("games-december-2026.html", 0)}">games coming out in December 2026</a> and <a href="{href("game-awards-2026.html", 0)}">The Game Awards 2026</a>.</p>'
            f'<p class="muted">Dates are US premiere dates. We only list a show when at least two premiere schedules (Rotten Tomatoes, Deadline, ScreenRant, Dexerto, Popverse) give the same date. Specials are marked.</p>'
            f'<div class="sec-head" style="margin-top:28px"><h2>Related pages and tools</h2></div><ul>'
            f'<li><a href="{href("new-tv-shows-january-2027.html", 0)}">New TV shows January 2027</a>: The Rookie, Baywatch, Grey\'s Anatomy</li>'
            f'<li><a href="{href("movies-2027.html", 0)}">Upcoming movies 2027</a>: Zelda, Shrek 5, Avengers: Secret Wars</li>'
            f'<li><a href="{href("movies-december-2026.html", 0)}">Movies coming out in December 2026</a>: Avengers: Doomsday, Dune: Part Three</li>'
            f'<li><a href="{href("games-december-2026.html", 0)}">Games coming out in December 2026</a></li>'
            f'<li><a href="{href("steam-sale-dates.html", 0)}">Steam Winter Sale dates</a></li>'
            f'<li><a href="{href("tools.html", 0)}">Every DayOneDrop tool</a></li></ul></div></section>')
tv_faq = [("What new TV shows come out in December 2026?", _tv_quick),
          ("When does the Harry Potter TV show come out?", "25 December 2026 on HBO Max."),
          ("When does Emily in Paris season 6 come out?", "24 December 2026 on Netflix. It is the final season."),
          ("When is Only Murders in the Building season 6?", "8 December 2026 on Hulu (Disney+ outside the US)."),
          ("What is new on Netflix in December 2026?", _tv_names(_tv_on("netflix")) + ".")]
page("new-tv-shows-december-2026.html", "New TV Shows December 2026: Every Premiere Date | DayOneDrop",
     "New TV shows in December 2026: Harry Potter (25 Dec, HBO Max), Emily in Paris S6 (24 Dec), Pride and Prejudice (3 Dec), Only Murders S6 and more by service.",
     _tv_body, 0, tv_faq, crumbs=[("Home", DOMAIN + "/"), ("New TV shows December 2026", canon("new-tv-shows-december-2026.html"))])


# ---------------- NEW TV SHOWS JANUARY 2027 (26 Nov 2026, DEMAND N16: "new tv shows january 2027", "midseason 2027 premiere dates") ----------------
# ABC: TVLine (6 Nov 2026) + Laughing Place (6 Nov 2026) from ABC's midseason announcement; Fox: TVLine (11 Nov 2026) + TV Guide (13 Nov 2026).
# The Rookie / Rookie: North / Baywatch also on TV Insider. Streaming dates on only one schedule (pogdesign) left out until a 2nd source lists them:
# 3 Body Problem S2 (14 Jan, Netflix), Ahsoka S2 (20 Jan, Disney+), The Traitors US (14 Jan, Peacock), Blue Eye Samurai S2 (19 Jan), Your Friendly Neighborhood Spider-Man S2 (13 Jan), Mayor of Kingstown (15 Jan), Matlock (21 Jan, CBS), NCIS: Sydney (26 Jan).
TV_JAN = [  # (title, date, network, kind, time ET, note)
    ("Best Medicine, Season 2", "2027-01-05", "fox", "ret", "8 pm", "Josh Charles' small-town doctor comedy-drama."),
    ("Will Trent, Season 5", "2027-01-05", "abc", "ret", "8 pm", "The GBI detective drama returns."),
    ("Doc, Season 3", "2027-01-05", "fox", "ret", "9 pm", "Medical drama."),
    ("High Potential, Season 3", "2027-01-05", "abc", "ret", "9 pm", "Kaitlin Olson's crime-solving single mum."),
    ("Surviving a Scandal", "2027-01-05", "abc", "new", "10 pm", "New series."),
    ("The Masked Singer, Season 15", "2027-01-06", "fox", "ret", "8 pm", "Reality singing contest."),
    ("Shifting Gears, Season 3", "2027-01-06", "abc", "ret", "8 pm", "Tim Allen sitcom, two-episode premiere."),
    ("Baywatch", "2027-01-06", "fox", "new", "9 pm", "New series: a reboot of the lifeguard drama."),
    ("The Rookie, Season 9", "2027-01-06", "abc", "ret", "9 pm", "Nathan Fillion's police drama."),
    ("The Rookie: North", "2027-01-06", "abc", "new", "10 pm", "New spin-off of The Rookie."),
    ("Extracted, Season 3", "2027-01-07", "fox", "ret", "8 pm", "Two-hour survival reality premiere; moves to 9 pm from 14 January."),
    ("9-1-1, Season 10 (midseason return)", "2027-01-07", "abc", "mid", "8 pm", "Back from the winter break."),
    ("9-1-1: Nashville, Season 2 (midseason return)", "2027-01-07", "abc", "mid", "9 pm", "Back from the winter break."),
    ("Grey's Anatomy, Season 23 (midseason return)", "2027-01-07", "abc", "mid", "10 pm", "Back from the winter break."),
    ("Abbott Elementary, Season 6 (midseason return)", "2027-01-13", "abc", "mid", "8:31 pm", "Back from the winter break."),
    ("Hell's Kitchen (new episodes)", "2027-01-14", "fox", "mid", "8 pm", "New episodes."),
    ("Celebrity Jeopardy!, Season 5", "2027-01-29", "abc", "ret", "8 pm", "Celebrity quiz."),
]
_TVJS = {"abc": "ABC (Hulu next day)", "fox": "Fox (Hulu next day)"}
_TVJK = {"new": "New series", "ret": "New season", "mid": "Midseason return"}
def _tvj_gcal(t, d, s, tm):
    a = d.replace("-", ""); b = (datetime.date.fromisoformat(d) + datetime.timedelta(days=1)).isoformat().replace("-", "")
    return "https://calendar.google.com/calendar/render?action=TEMPLATE&text=" + _qp(t + " on " + s) + f"&dates={a}/{b}&details=" + _qp(f"{tm} ET. Premiere date via getdayonedrop.com/new-tv-shows-january-2027")
def _tvjrow(x):
    t, d, s, k, tm, n = x
    return (f'<div class="row" data-ts="{s}" data-tk="{k}"><span><strong>{e(t)}</strong><br><span class="muted">{e(n)}</span><br><span class="muted">{e(_TVJS[s])} · {e(_TVJK[k])} · {e(tm)} ET · '
            f'<a href="{e(_tvj_gcal(t, d, s.upper(), tm))}" rel="nofollow noopener" target="_blank">Add to Google Calendar</a></span></span><b>{e(_mv_nice(d))}</b></div>')
_tvj_chips = ('<div class="chips" role="group" aria-label="Network"><button class="chip" type="button" data-tv-s="" aria-pressed="true">Every network</button>'
              '<button class="chip" type="button" data-tv-s="abc" aria-pressed="false">ABC</button><button class="chip" type="button" data-tv-s="fox" aria-pressed="false">Fox</button></div>'
              '<div class="chips" role="group" aria-label="Type" style="margin-top:8px"><button class="chip" type="button" data-tv-k="" aria-pressed="true">Everything</button>'
              + "".join(f'<button class="chip" type="button" data-tv-k="{k}" aria-pressed="false">{e(l)}</button>' for k, l in _TVJK.items()) + '</div>')
_tvj_new = [x for x in TV_JAN if x[3] == "new"]
_tvj_quick = ("The first big week of January 2027 TV is 5 to 7 January: Will Trent, High Potential and Doc return on 5 January, The Rookie season 9, the new spin-off The Rookie: North and Fox's new Baywatch start on 6 January, "
              "and 9-1-1 and Grey's Anatomy come back on 7 January. " + f"We list {len(TV_JAN)} network premieres so far, including {len(_tvj_new)} new series.")
_tvj_days = sorted(set(x[1] for x in TV_JAN))
_tvj_body = (f'<header class="hero"><div class="wrap"><span class="kicker">TV · January 2027</span>'
             f'<h1>New TV shows in January 2027:<br><span class="amber">every premiere date so far.</span></h1>'
             f'<p class="lead">Midseason premieres and returns on ABC and Fox with times, a network and type filter, and a calendar reminder for each show. Streaming dates are added once two schedules agree.</p>'
             f'<p class="muted" style="margin:0">Last checked {e(UPDATED)} · {len(TV_JAN)} premieres</p></div></header>'
             f'<section><div class="wrap"><div class="out" style="margin-bottom:12px"><div class="row"><span><strong>Quick answer:</strong> {e(_tvj_quick)}</span></div></div>'
             f'<div class="tool" id="tv-tool" style="margin-bottom:24px"><h2 style="font-size:1.5rem;margin-top:0">What is back on my channel in January?</h2>'
             f'<p class="muted">Pick a network and a type. All times are Eastern; shows stream on Hulu the next day. Your choice is remembered on this device.</p>{_tvj_chips}'
             f'<p class="mono amber" id="tv-count" aria-live="polite" style="margin:12px 0 0">{len(TV_JAN)} shows</p></div>'
             f'<div class="sec-head"><h2>What new TV shows come out in January 2027?</h2><span class="muted">in date order</span></div>'
             f'<div class="out" id="tv-list" style="margin-bottom:10px">{"".join(_tvjrow(x) for x in TV_JAN)}</div><p class="empty" id="tv-none" hidden>Nothing matches. Try "Every network".</p>'
             f'<div class="cdw" style="margin-top:18px"><span class="lbl">Countdown to The Rookie season 9 and The Rookie: North</span><div class="cd" data-countdown="2027-01-06">'
             '<div class="cd-unit"><span class="flaps" data-u="0"></span><span>Days</span></div><div class="cd-unit"><span class="flaps" data-u="1"></span><span>Hrs</span></div>'
             '<div class="cd-unit"><span class="flaps" data-u="2"></span><span>Min</span></div><div class="cd-unit"><span class="flaps" data-u="3"></span><span>Sec</span></div></div></div></div></section>'
             + AD.format("tvj-mid") +
             f'<section><div class="wrap"><div class="sec-head"><h2>When does The Rookie season 9 come out?</h2></div>'
             f'<p>Wednesday 6 January 2027 at 9 pm ET on ABC, followed at 10 pm by the series premiere of the spin-off The Rookie: North. Both stream on Hulu the next day.</p>'
             f'<div class="sec-head" style="margin-top:28px"><h2>When does the new Baywatch come out?</h2></div>'
             f'<p>Wednesday 6 January 2027 at 9 pm ET on Fox, straight after the season 15 premiere of The Masked Singer.</p>'
             f'<div class="sec-head" style="margin-top:28px"><h2>When do Grey\'s Anatomy and 9-1-1 come back?</h2></div>'
             f'<p>Thursday 7 January 2027 on ABC: 9-1-1 at 8 pm, 9-1-1: Nashville at 9 pm and Grey\'s Anatomy at 10 pm ET. Abbott Elementary follows on 13 January at 8:31 pm.</p>'
             f'<div class="sec-head" style="margin-top:28px"><h2>When does High Potential season 3 start?</h2></div>'
             f'<p>Tuesday 5 January 2027 at 9 pm ET on ABC, after Will Trent season 5 at 8 pm. ABC\'s new drama Surviving a Scandal follows at 10 pm.</p>'
             f'<div class="sec-head" style="margin-top:28px"><h2>What new series start in January 2027?</h2><span class="muted">{len(_tvj_new)}</span></div>'
             f'<div class="out" style="margin-bottom:10px">{"".join(_tvjrow(x) for x in _tvj_new)}</div>'
             f'<div class="sec-head" style="margin-top:28px"><h2>What is premiering each night?</h2></div><div class="out" style="margin-bottom:28px">'
             + "".join(f'<div class="row"><span><strong>{e(_mv_nice(d))}</strong><br><span class="muted">{e(_and([x[0] for x in TV_JAN if x[1] == d]))}</span></span><b>{sum(1 for x in TV_JAN if x[1] == d)}</b></div>' for d in _tvj_days) +
             f'</div><div class="sec-head"><h2>What about Netflix, Disney+ and Peacock in January 2027?</h2></div>'
             f'<p>Streaming services usually confirm January dates in December. We add a show once two premiere schedules give the same date, so check back. December\'s streaming premieres, including HBO Max\'s Harry Potter on 25 December, are on <a href="{href("new-tv-shows-december-2026.html", 0)}">new TV shows in December 2026</a>.</p>'
             f'<div class="sec-head" style="margin-top:28px"><h2>What games and movies are out in January 2027?</h2></div>'
             f'<p>January 2027 is also busy for games, with Forza Horizon 6 on PS5 (26 January) and Metroid: Ravenous (28 January). See <a href="{href("months/january-2027.html", 0)}">games coming out in January 2027</a> and <a href="{href("movies-2027.html", 0)}">upcoming movies 2027</a>.</p>'
             f'<p class="muted">Dates and times are US Eastern, from ABC\'s and Fox\'s midseason schedules as published by TVLine, Laughing Place and TV Guide (November 2026). Networks can still move a premiere.</p>'
             f'<div class="sec-head" style="margin-top:28px"><h2>Related pages and tools</h2></div><ul>'
             f'<li><a href="{href("new-tv-shows-december-2026.html", 0)}">New TV shows December 2026</a></li>'
             f'<li><a href="{href("movies-2027.html", 0)}">Upcoming movies 2027</a> with countdowns</li>'
             f'<li><a href="{href("winter-2027-anime.html", 0)}">Winter 2027 anime</a>: every January anime premiere</li>'
             f'<li><a href="{href("months/january-2027.html", 0)}">Games coming out in January 2027</a></li>'
             f'<li><a href="{href("tools.html", 0)}">Every DayOneDrop tool</a></li></ul></div></section>')
tvj_faq = [("What new TV shows come out in January 2027?", _tvj_quick),
           ("When does The Rookie season 9 premiere?", "Wednesday 6 January 2027 at 9 pm ET on ABC, with The Rookie: North at 10 pm."),
           ("When does the Baywatch reboot premiere?", "Wednesday 6 January 2027 at 9 pm ET on Fox."),
           ("When does Grey's Anatomy come back in 2027?", "Thursday 7 January 2027 at 10 pm ET on ABC."),
           ("When does High Potential season 3 come out?", "Tuesday 5 January 2027 at 9 pm ET on ABC."),
           ("When does The Masked Singer season 15 start?", "Wednesday 6 January 2027 at 8 pm ET on Fox.")]
page("new-tv-shows-january-2027.html", "New TV Shows January 2027: Premiere Dates and Times | DayOneDrop",
     "New TV shows January 2027: The Rookie S9 + The Rookie: North and Baywatch (6 Jan), High Potential S3 (5 Jan), Grey's Anatomy (7 Jan). Times, filter, reminders.",
     _tvj_body, 0, tvj_faq, crumbs=[("Home", DOMAIN + "/"), ("New TV shows January 2027", canon("new-tv-shows-january-2027.html"))])


# ---------------- BLACK FRIDAY GAME SALES 2026 (demand run 26 Nov 2026: "ps store black friday sale end date", "xbox black friday sale 2026", "nintendo eshop black friday 2026", "steam black friday sale") ----------------
# Sources: PlayStation.com Black Friday page + Insider Gaming + God is a Geek + Push Square (PS Store 4-30 Nov, up to 75%, refresh 16 Nov, first wave ended 20 Nov);
# Pure Xbox (19 Nov 2026, ends 2 Dec, 2,000+ games) + Windows Report + games.gg + Twisted Voxel (starts 19 Nov, up to 80%);
# Nintendo US: Day One/playday (13 Nov) + Windows Report + Otakukart (digital 19 Nov - 2 Dec, wider sale 22 Nov - 5 Dec, $50 off Switch 2 + Mario Kart World bundle, $20 off select physical games);
# Nintendo Europe: Nintendo UK via My Nintendo News (17 Nov 2026) + Notebookcheck DE (eShop sale ends 29 Nov 23:59 local; extra titles 19 Nov 09:00 - 2 Dec 23:59 local);
# Epic: Epic Games Store Black Friday buyer's guide (17 Nov 2026: 17 Nov 11am ET - 1 Dec 11am ET, Premium Editions) + Digital Citizen; Epic Holiday Sale 10 Dec - 7 Jan from Epic's Q4 developer promo guide.
# Steam: no Valve Black Friday sale (Autumn Sale ran 1-8 Oct 2026, Winter Sale 17 Dec from STEAM above). Steam Awards nomination dates single-source: left out.
# Times: "Z" = exact UTC time given by the store; no Z = end time not given, we count to 23:59 in the reader's own time zone (store-local).
BF = [  # (id, store, region us|eu|all, start, end, what, discount)
    ("ps", "PlayStation Store Black Friday sale", "all", "2026-11-04T08:00:00Z", "2026-11-30T23:59:00", "PS5 and PS4 games, add-ons and PS Plus", "Up to 75% off; PS Plus 12 months up to 33% off"),
    ("epic", "Epic Games Store Black Friday: Premium Editions Sale", "all", "2026-11-17T16:00:00Z", "2026-12-01T16:00:00Z", "Deluxe, Gold and other premium editions of PC games only", "Set by each publisher"),
    ("nseu", "Nintendo eShop Black Friday sale (UK and Europe)", "eu", "2026-11-17T00:00:00", "2026-11-29T23:59:00", "Switch and Switch 2 games", "Varies by game"),
    ("nseu2", "Nintendo eShop extra Black Friday titles (UK and Europe)", "eu", "2026-11-19T09:00:00", "2026-12-02T23:59:00", "A second batch of discounted eShop games", "Varies by game"),
    ("nsus", "Nintendo Black Friday digital sale (US)", "us", "2026-11-19T00:00:00", "2026-12-02T23:59:00", "Switch and Switch 2 games on the eShop", "Varies by game"),
    ("xbox", "Xbox Black Friday sale", "all", "2026-11-19T00:00:00", "2026-12-02T23:59:00", "2,000+ Xbox Series X|S, Xbox One and PC games and add-ons", "Up to 80% off (a few older games 90%)"),
    ("nsus2", "Nintendo Black Friday hardware and physical game deals (US)", "us", "2026-11-22T00:00:00", "2026-12-05T23:59:00", "Switch 2 + Mario Kart World bundle and selected physical games at retailers", "$50 off the bundle ($499); $20 off selected games"),
]
BF_NEXT = [  # what comes after Black Friday (same format)
    ("epichol", "Epic Games Store Holiday Sale", "all", "2026-12-10T16:00:00Z", "2027-01-07T16:00:00Z", "Base games and DLC on PC (plus the daily mystery free games)", "Set by each publisher"),
    ("steamw", "Steam Winter Sale 2026", "all", "2026-12-17T18:00:00Z", "2027-01-04T18:00:00Z", "Storewide PC sale on Steam", "Set by each publisher"),
]
_bf_reg = {"all": "US, UK and Europe", "us": "US", "eu": "UK and Europe"}
def _bf_d(s):
    return datetime.date.fromisoformat(s[:10])
def _bf_nice(s):
    d = _bf_d(s); return f"{_WD[d.weekday()][:3]} {d.day} {d.strftime('%b')}" + ("" if d.year == 2026 else f" {d.year}")
def _bf_time(s):
    if not s.endswith("Z"): return "end time not given"
    return {"16:00": "11 am Eastern", "18:00": "10 am Pacific", "08:00": "midnight Pacific"}.get(s[11:16], s[11:16] + " UTC")
def _bf_row(x):
    i, n, r, a, b, what, disc = x
    return (f'<div class="row" data-bf-r="{r}" data-bf-s="{a}" data-bf-e="{b}"><span style="min-width:0"><strong>{e(n)}</strong><br>'
            f'<span class="muted">{e(what)} · {e(_bf_reg[r])}</span><br><span class="muted">{e(disc)}</span><br>'
            f'<span class="mono amber bf-st" style="font-size:.8rem"></span></span>'
            f'<span style="text-align:right;flex-shrink:0;max-width:44%"><b style="white-space:normal">Ends {e(_bf_nice(b))}</b><br>'
            f'<span class="muted" style="font-size:.8rem">{e(_bf_time(b))}</span></span></div>')
_bf_today = datetime.date.fromisoformat(UPDATED)
_bf_sorted = sorted(BF, key=lambda x: x[4][:10])
_bf_tc = 'style="padding:6px;border-top:1px solid var(--rule);vertical-align:top"'
_bf_tbl = ('<div style="overflow-x:auto"><table class="gen-table" style="width:100%;border-collapse:collapse;font-size:.92rem"><thead><tr>'
           '<th style="text-align:left;padding:6px">Sale</th><th style="text-align:left;padding:6px">Started</th><th style="text-align:left;padding:6px">Ends</th><th style="text-align:left;padding:6px">Discount</th></tr></thead><tbody>'
           + "".join(f'<tr><td {_bf_tc}>{e(n)}</td><td {_bf_tc} class="mono">{e(_bf_nice(a))}</td><td {_bf_tc} class="mono">{e(_bf_nice(b))}</td><td {_bf_tc}>{e(d)}</td></tr>' for i, n, r, a, b, w, d in _bf_sorted)
           + '</tbody></table></div>')
_bf_quick = ("The PlayStation Store Black Friday sale ends on Monday 30 November 2026 (Cyber Monday). The Epic Games Store sale ends 1 December at 11 am Eastern, and the Xbox and US Nintendo eShop sales run until 2 December. "
             "In the UK and Europe the main Nintendo eShop sale ends sooner, on Sunday 29 November at 23:59. Steam has no Black Friday sale: its next big sale is the Winter Sale from 17 December.")
_bf_dec = sorted([g for g in GAMES if g["date"] and g["date"] <= "2027-01-31"], key=lambda g: g["date"])[:6]
_bf_chips = ('<div class="chips" role="group" aria-label="Your region"><button class="chip" type="button" data-bf-f="" aria-pressed="true">All regions</button>'
             '<button class="chip" type="button" data-bf-f="us" aria-pressed="false">I\'m in the US</button>'
             '<button class="chip" type="button" data-bf-f="eu" aria-pressed="false">I\'m in the UK or Europe</button></div>')
_bf_body = (f'<header class="hero"><div class="wrap"><span class="kicker">Black Friday 2026</span>'
            f'<h1>Black Friday 2026 game sales:<br><span class="amber">when does each one end?</span></h1>'
            f'<p class="lead">PlayStation Store, Xbox, Nintendo eShop, Epic and Steam: start and end dates for every console and PC Black Friday sale, with a live "ends in" timer for each one in your time zone.</p>'
            f'<p class="muted" style="margin:0">Last checked {e(UPDATED)} · dates from the stores\' own announcements, checked against 2+ outlets</p></div></header>'
            f'<section><div class="wrap"><div class="out" style="margin-bottom:24px"><div class="row"><span><strong>Quick answer:</strong> {e(_bf_quick)}</span></div></div>'
            f'<div class="tool" id="bf-tool"><h2 style="font-size:1.5rem;margin-top:0">Which Black Friday game sale ends next?</h2>'
            f'<p class="mono amber" id="bf-next" aria-live="polite" style="font-size:1.1rem;margin:0 0 6px">The PlayStation Store sale ends 30 November.</p>'
            f'<p class="muted">Pick your region. Sales are sorted by end date, and each one shows a live "ends in" timer. Where a store gives no end time we count to 23:59 on the last day in your own time zone. Your choice is remembered on this device.</p>{_bf_chips}'
            f'<p class="mono amber" id="bf-count" aria-live="polite" style="margin:12px 0 0">{len(BF)} sales</p>'
            f'<div class="out" id="bf-list" style="margin-top:12px">{"".join(_bf_row(x) for x in _bf_sorted)}</div>'
            f'<p class="empty" id="bf-none" hidden>Every Black Friday sale in your region has ended. The next ones are below.</p>'
            f'<h3 style="margin-top:20px">What comes after Black Friday?</h3><div class="out" id="bf-after">{"".join(_bf_row(x) for x in BF_NEXT)}</div></div></div></section>'
            + AD.format("bf-mid") +
            f'<section><div class="wrap"><div class="sec-head"><h2>What are all the Black Friday 2026 game sale dates?</h2><span class="muted">{len(BF)} sales</span></div>{_bf_tbl}'
            f'<p class="muted" style="margin-top:10px">Dates are as announced by Sony, Microsoft, Nintendo and Epic, and confirmed by at least two outlets (Push Square, Insider Gaming, God is a Geek, Pure Xbox, Windows Report, My Nintendo News, Notebookcheck, Digital Citizen). Individual game deals can end earlier than the sale itself.</p>'
            f'<div class="sec-head" style="margin-top:28px"><h2>When does the PlayStation Store Black Friday sale end?</h2></div>'
            f'<p>Monday 30 November 2026. The sale started on 4 November with up to 75% off PS5 and PS4 games. Sony refreshed it on 16 November, and the first batch of deals ended on 20 November, so check the end date on each game\'s store page. PS Plus 12-month memberships are up to 33% off. PlayStation\'s hardware deals (PS5 bundles up to $100 off, PS Portal $20 off) began on 21 November at PlayStation Direct and retailers.</p>'
            f'<div class="sec-head" style="margin-top:28px"><h2>When does the Xbox Black Friday sale end?</h2></div>'
            f'<p>Wednesday 2 December 2026. It started on 19 November with more than 2,000 games and add-ons for Xbox Series X|S, Xbox One and PC, up to 80% off (Pure Xbox found a few older games at 90%). There are no console price cuts in Microsoft\'s own sale.</p>'
            f'<div class="sec-head" style="margin-top:28px"><h2>When does the Nintendo eShop Black Friday sale end?</h2></div>'
            f'<p>It depends where you live. <strong>US:</strong> the digital sale runs 19 November to 2 December, and the wider sale (the Switch 2 + Mario Kart World bundle at $499, $50 off, and $20 off selected physical games such as Donkey Kong Bananza and Metroid Prime 4: Beyond) runs 22 November to 5 December. '
            f'<strong>UK and Europe:</strong> the main eShop sale ends Sunday 29 November at 23:59 local time, and a second batch of games is discounted from 19 November (09:00) to 2 December (23:59).</p>'
            f'<div class="sec-head" style="margin-top:28px"><h2>What are the Switch 2 Black Friday deals?</h2></div>'
            f'<p>In the US, Nintendo\'s own Black Friday offer is the Switch 2 + Mario Kart World bundle at $499.99, $50 off and the same price as the console on its own, plus $20 off selected physical Switch 2 and Switch games such as Donkey Kong Bananza and Metroid Prime 4: Beyond, at retailers from 22 November to 5 December. Switch and Switch 2 eShop games are discounted in the digital sale until 2 December. In the UK and Europe the main eShop sale ends on 29 November. Prices vary by store, so check the retailer before you buy. Planning what to buy for next year? See <a href="{href("platforms/switch-2.html", 0)}">every Switch 2 game coming in 2027</a>.</p>'
            f'<div class="sec-head" style="margin-top:28px"><h2>Is there a Steam Black Friday sale in 2026?</h2></div>'
            f'<p>No. Valve does not run a Black Friday sale. This year\'s Steam Autumn Sale was earlier, 1 to 8 October 2026, and the next storewide sale is the Steam Winter Sale from 17 December 2026 to 4 January 2027. Some publishers still put their own discounts on Steam this week. See <a href="{href("steam-sale-dates.html", 0)}">every Steam sale date</a> with a countdown.</p>'
            f'<div class="sec-head" style="margin-top:28px"><h2>When does the Epic Games Store Black Friday sale end?</h2></div>'
            f'<p>Tuesday 1 December 2026 at 11 am Eastern (4 pm UK). It started on 17 November and only covers premium editions (Deluxe, Gold and similar), not base games. Epic\'s Holiday Sale for base games and DLC follows from 10 December to 7 January. Epic\'s weekly freebie keeps running too: <a href="{href("epic-free-games.html", 0)}">this week\'s Epic free game</a>.</p>'
            f'<div class="sec-head" style="margin-top:28px"><h2>Are the Black Friday sales still on for Cyber Monday?</h2></div>'
            f'<p>Yes, all of them except Nintendo\'s main UK and Europe eShop sale. Cyber Monday is 30 November 2026, which is also the last day of the PlayStation Store sale. Xbox, Epic and Nintendo US run past it; there is no separate Cyber Monday sale on any console store.</p>'
            f'<div class="sec-head" style="margin-top:28px"><h2>Should I buy now or wait for the Christmas sales?</h2></div>'
            f'<p>For PC, the Steam Winter Sale (17 December) and Epic Holiday Sale (10 December) are both coming, so there is little reason to rush. For PS5 and Switch, there is usually a smaller holiday sale in late December, but nothing has been announced yet, so treat today\'s price as the one you know. Brand-new games rarely get big Black Friday cuts: it is the best week for games from 2024 and 2025.</p>'
            f'<div class="sec-head" style="margin-top:28px"><h2>What new games come out right after Black Friday?</h2></div>'
            f'<p>December 2026 is busy with smaller launches (see <a href="{href("games-december-2026.html", 0)}">every December 2026 game</a>), and the first big 2027 games arrive in January:</p>'
            f'<div class="out" style="margin-bottom:10px">' + "".join(f'<div class="row"><span><strong>{_gname(g)}</strong><br><span class="muted">{e(plat_text(g))}</span></span><b>{e(nice_date(g))}</b></div>' for g in _bf_dec) + '</div>'
            f'<div class="sec-head" style="margin-top:28px"><h2>Related pages and tools</h2></div><ul>'
            f'<li><a href="{href("steam-sale-dates.html", 0)}">Steam sale dates</a>: countdown to the Winter Sale and every 2027 sale</li>'
            f'<li><a href="{href("ps-plus-monthly-games.html", 0)}">PS Plus monthly games</a>: what you get free this month</li>'
            f'<li><a href="{href("epic-free-games.html", 0)}">Epic free games this week</a></li>'
            f'<li><a href="{href("backlog-planner-2027.html", 0)}">2027 backlog planner</a>: how much of your sale haul you can finish before the big 2027 games</li></ul></div></section>')
bf_faq = [("When does the PlayStation Store Black Friday sale end?", "Monday 30 November 2026. It started on 4 November with up to 75% off, and some deals ended earlier, on 20 November."),
          ("When does the Xbox Black Friday sale end?", "Wednesday 2 December 2026. It started on 19 November with 2,000+ games up to 80% off."),
          ("When does the Nintendo eShop Black Friday sale end?", "In the US the digital sale ends 2 December 2026 (hardware and physical deals to 5 December). In the UK and Europe the main eShop sale ends 29 November at 23:59, with a second batch to 2 December."),
          ("What are the Switch 2 Black Friday deals?", "In the US: the Switch 2 + Mario Kart World bundle for $499.99 ($50 off) and $20 off selected physical games such as Donkey Kong Bananza, 22 November to 5 December, plus eShop discounts until 2 December. The UK and Europe eShop sale ends 29 November."),
          ("Is there a Steam Black Friday sale?", "No. Valve's Autumn Sale ran 1 to 8 October 2026. The next storewide Steam sale is the Winter Sale, 17 December 2026 to 4 January 2027."),
          ("When does the Epic Games Store Black Friday sale end?", "1 December 2026 at 11 am Eastern. It covers premium editions only. The Epic Holiday Sale runs 10 December to 7 January."),
          ("Is there a Cyber Monday game sale?", "Not a separate one. Cyber Monday (30 November 2026) is the last day of the PlayStation Store sale; the Xbox, Epic and US Nintendo sales continue after it.")]
page("black-friday-game-sales-2026.html", "Black Friday 2026 Game Sales: Every End Date | DayOneDrop",
     "PS Store Black Friday 2026 sale ends 30 Nov, Epic 1 Dec, Xbox and Nintendo US 2 Dec (Nintendo UK/EU 29 Nov). No Steam Black Friday sale. Live end timers.",
     _bf_body, 0, bf_faq, crumbs=[("Home", DOMAIN + "/"), ("Black Friday 2026 game sales", canon("black-friday-game-sales-2026.html"))])


# ---------------- MOVIES DECEMBER 2026 (26 Nov 2026, DEMAND N11 "movies coming out december 2026") ----------------
# US cinema dates checked 26 Nov 2026 on Box Office Mojo, The Numbers and GamesRadar+ (2+ agree); Jumanji move to 25 Dec: TheWrap + Bleeding Cool;
# Artificial (Neon, Oscar-qualifying run): Screen Daily + TheWrap; Mr. Irrelevant (Paramount, Christmas): TheWrap + Box Office Mojo.
# Streaming-only titles listed by one schedule (In a Holidaze, The Man with the Bag, Bad Day, Give Me Some Sugah, Ink, Ray Gunn) left out.
MV_DEC = [  # (title, date, studio, kind, note, where, week)
    ("Violent Night 2", "2026-12-04", "Universal", "action", "David Harbour's action Santa is back.", "Cinemas", 1),
    ("The Debut", "2026-12-11", "A24", "drama", "Limited release on 11 December, expanding wide on 25 December.", "Cinemas (limited)", 2),
    ("Clarissa", "2026-12-11", "Neon", "drama", "Oscar-qualifying run in a few cinemas.", "Cinemas (limited)", 2),
    ("Avengers: Doomsday", "2026-12-18", "Disney / Marvel Studios", "hero", "Robert Downey Jr. returns as Doctor Doom. The Russo brothers direct; Avengers: Secret Wars follows on 17 December 2027.", "Cinemas", 3),
    ("Dune: Part Three", "2026-12-18", "Warner Bros. / Legendary", "action", "Denis Villeneuve's final Dune film (Dune Messiah), the same day as Avengers: Doomsday.", "Cinemas and IMAX", 3),
    ("The Angry Birds Movie 3", "2026-12-23", "Paramount", "anim", "The family pick for the Christmas holidays.", "Cinemas", 4),
    ("Jumanji 3", "2026-12-25", "Sony Pictures", "action", "Dwayne Johnson, Kevin Hart, Jack Black and Karen Gillan return. Sony moved it from 11 December to Christmas Day.", "Cinemas and IMAX", 4),
    ("Werwulf", "2026-12-25", "Focus Features", "horror", "Robert Eggers' werewolf horror set in 13th-century England.", "Cinemas", 4),
    ("Mr. Irrelevant", "2026-12-25", "Paramount", "drama", "David Corenswet plays NFL quarterback John Tuggle, the last pick of the 1983 draft.", "Cinemas", 4),
    ("Artificial", "2026-12-25", "Neon", "drama", "Luca Guadagnino's OpenAI drama with Andrew Garfield. A short Oscar-qualifying run first; the full release is in 2027.", "Cinemas (limited)", 4),
]
MVD_KIND = [("hero", "Marvel"), ("action", "Action and sci-fi"), ("anim", "Family and animated"), ("horror", "Horror"), ("drama", "Drama and awards films")]
_MVDK = dict(MVD_KIND)
MVD_WEEKS = [(1, "1-6 Dec"), (2, "7-13 Dec"), (3, "14-20 Dec"), (4, "21-31 Dec")]
MVD_OUT = [("Shrek 5", "23 December 2026", "30 June 2027"), ("Ice Age: Boiling Point", "18 December 2026", "5 February 2027"),
           ("Narnia: The Magician's Nephew", "26 November 2026 (IMAX)", "12 February 2027")]
def _mvd_gcal(t, d):
    a = d.replace("-", ""); b = (datetime.date.fromisoformat(d) + datetime.timedelta(days=1)).isoformat().replace("-", "")
    return "https://calendar.google.com/calendar/render?action=TEMPLATE&text=" + _qp(t + " in cinemas") + f"&dates={a}/{b}&details=" + _qp("US release date via getdayonedrop.com/movies-december-2026")
def _mvdrow(m):
    t, d, st, k, note, wh, wk = m
    return (f'<div class="row" data-mk="{k}" data-mm="{wk}"><span><strong>{e(t)}</strong>'
            f'<br><span class="muted">{e(note)}</span><br><span class="muted">{e(st)} · {e(_MVDK[k])} · {e(wh)} · '
            f'<a href="{e(_mvd_gcal(t, d))}" rel="nofollow noopener" target="_blank">Add to Google Calendar</a></span></span><b>{e(_mv_nice(d))}</b></div>')
_mvd_av = next(m for m in MV_DEC if m[0] == "Avengers: Doomsday")
_mvd_xmas = [m for m in MV_DEC if m[1] == "2026-12-25"]
_mvd_quick = ("The biggest movies coming out in December 2026 are Avengers: Doomsday and Dune: Part Three, both on 18 December, then Jumanji 3 on Christmas Day. "
              f"Also out: Violent Night 2 (4 December), The Angry Birds Movie 3 (23 December) and Robert Eggers' Werwulf (25 December). We list {len(MV_DEC)} US cinema releases. Shrek 5 is not one of them: it moved to 30 June 2027.")
_mvd_chips = ('<div class="chips" role="group" aria-label="Type"><button class="chip" type="button" data-mv-k="" aria-pressed="true">All movies</button>'
              + "".join(f'<button class="chip" type="button" data-mv-k="{k}" aria-pressed="false">{e(n)}</button>' for k, n in MVD_KIND) + '</div>'
              '<div class="chips" role="group" aria-label="Week" style="margin-top:8px"><button class="chip" type="button" data-mv-m="" aria-pressed="true">Any week</button>'
              + "".join(f'<button class="chip" type="button" data-mv-m="{w}" aria-pressed="false">{e(l)}</button>' for w, l in MVD_WEEKS) + '</div>')
_mvd_dec_games = [g for g in GAMES if g["date"] and "2026-12-01" <= g["date"] <= "2026-12-31"]
_mvd_body = (f'<header class="hero"><div class="wrap"><span class="kicker">Movies · December 2026</span>'
             f'<h1>Movies coming out in December 2026:<br><span class="amber">every big release date.</span></h1>'
             f'<p class="lead">Avengers: Doomsday, Dune: Part Three, Jumanji 3 and every other big December cinema release, with a type and week filter, a countdown and a calendar reminder for each film.</p>'
             f'<p class="muted" style="margin:0">Last checked {e(UPDATED)} · {len(MV_DEC)} movies · US cinema dates from the studios or two release schedules</p></div></header>'
             f'<section><div class="wrap"><div class="out" style="margin-bottom:24px"><div class="row"><span><strong>Quick answer:</strong> {e(_mvd_quick)}</span></div></div>'
             f'<div class="tool" id="mv-tool"><h2 style="font-size:1.5rem;margin-top:0">What should I see at the cinema in December?</h2>'
             f'<p class="muted">Pick a type and a week. The list below updates and your choice is remembered on this device.</p>{_mvd_chips}'
             f'<p class="mono amber" id="mv-count" aria-live="polite" style="margin:12px 0 0">{len(MV_DEC)} movies</p></div>'
             + _mvcd(_mvd_av, "Countdown to Avengers: Doomsday and Dune: Part Three") + '</div></section>'
             + AD.format("mvd-mid") +
             f'<section><div class="wrap"><div class="sec-head"><h2>What movies are coming out in December 2026?</h2><span class="muted">{len(MV_DEC)} in cinemas</span></div>'
             f'<p class="muted">In release order, US dates. UK dates are usually the same week; check your local cinema for limited releases.</p>'
             f'<div class="out" id="mv-list" style="margin-bottom:10px">{"".join(_mvdrow(m) for m in MV_DEC)}</div><p class="empty" id="mv-none" hidden>Nothing matches. Try "All movies" and "Any week".</p>'
             f'<div class="sec-head" style="margin-top:28px"><h2>When does Avengers: Doomsday come out?</h2></div>'
             f'<p>Friday 18 December 2026 in US cinemas, with most countries opening the same week. Marvel moved it there from May 2026. It is the first of two Russo brothers Avengers films; Avengers: Secret Wars follows a year later, on 17 December 2027 (see <a href="{href("movies-2027.html", 0)}">upcoming movies 2027</a>).</p>'
             f'<div class="sec-head" style="margin-top:28px"><h2>Are Avengers: Doomsday and Dune: Part Three out on the same day?</h2></div>'
             f'<p>Yes. Both open on 18 December 2026, a double bill people call "Dunesday". Dune: Part Three adapts Dune Messiah and is Denis Villeneuve\'s last Dune film. Sony moved Jumanji 3 a week later, to 25 December, to stay clear of both.</p>'
             f'<div class="sec-head" style="margin-top:28px"><h2>What movies come out on Christmas Day 2026?</h2><span class="muted">{len(_mvd_xmas)}</span></div>'
             f'<p>{e(_and([m[0] + " (" + m[2] + ")" for m in _mvd_xmas]))}. The Debut also goes wide that day after its 11 December limited start.</p>'
             f'<div class="sec-head" style="margin-top:28px"><h2>Which movies moved out of December 2026?</h2></div>'
             f'<p>These were once dated for this December and now open in 2027:</p><div class="out" style="margin-bottom:10px">'
             + "".join(f'<div class="row"><span><strong>{e(t)}</strong><br><span class="muted">Was {e(a)}</span></span><b>{e(b)}</b></div>' for t, a, b in MVD_OUT) + '</div>'
             f'<div class="sec-head" style="margin-top:28px"><h2>What family movies are out over Christmas 2026?</h2></div>'
             f'<p>The Angry Birds Movie 3 (23 December) is the main animated film, and Jumanji 3 (25 December) is the family action pick. Shrek 5 and the new Ice Age are no longer in December.</p>'
             f'<div class="sec-head" style="margin-top:28px"><h2>What else is out in December 2026?</h2></div>'
             f'<p>{len(_mvd_dec_games)} games on our board launch in December, The Game Awards are on 10 December, and HBO\'s Harry Potter series starts on 25 December. See <a href="{href("games-december-2026.html", 0)}">games coming out in December 2026</a> and <a href="{href("new-tv-shows-december-2026.html", 0)}">new TV shows in December 2026</a>.</p>'
             f'<p class="muted">We list a film when the studio or at least two release schedules (Box Office Mojo, The Numbers, GamesRadar+, TheWrap, Screen Daily) give the same US date. Streaming-only films are left out until two schedules agree.</p>'
             f'<div class="sec-head" style="margin-top:28px"><h2>Related pages and tools</h2></div><ul>'
             f'<li><a href="{href("movies-2027.html", 0)}">Upcoming movies 2027</a>: Zelda, Shrek 5, Avengers: Secret Wars</li>'
             f'<li><a href="{href("new-tv-shows-december-2026.html", 0)}">New TV shows December 2026</a>: Harry Potter, Emily in Paris</li>'
             f'<li><a href="{href("movies-january-2027.html", 0)}">Movies coming out in January 2027</a>: Children of Blood and Bone, Animal Friends</li>'
             f'<li><a href="{href("winter-2027-anime.html", 0)}">Winter 2027 anime</a>: every January premiere</li>'
             f'<li><a href="{href("game-awards-2026.html", 0)}">The Game Awards 2026</a>: start time in your time zone</li></ul></div></section>')
mvd_faq = [("What movies are coming out in December 2026?", _mvd_quick),
           ("When does Avengers: Doomsday come out?", "18 December 2026 in US cinemas."),
           ("When does Dune: Part Three come out?", "18 December 2026, the same day as Avengers: Doomsday."),
           ("When does Jumanji 3 come out?", "25 December 2026. Sony moved it from 11 December."),
           ("Is Shrek 5 coming out in December 2026?", "No. Shrek 5 moved to 30 June 2027."),
           ("What movies come out on Christmas Day 2026?", _and([m[0] for m in _mvd_xmas]) + ".")]
page("movies-december-2026.html", "Movies Coming Out in December 2026: Release Dates | DayOneDrop",
     "Movies coming out in December 2026: Avengers: Doomsday and Dune: Part Three (18 Dec), Angry Birds 3 (23 Dec), Jumanji 3 and Werwulf (25 Dec). Filter by week.",
     _mvd_body, 0, mvd_faq, crumbs=[("Home", DOMAIN + "/"), ("Movies December 2026", canon("movies-december-2026.html"))])


# ---------------- WINTER 2027 ANIME (26 Nov 2026, DEMAND E2 "anime 2027 upcoming", "winter 2027 anime") ----------------
# Each title listed for winter 2027 by 2+ of: Crank-in (season list), Anime Eiga (season list), Anime Corner, ComicBook.com, GamesRadar+ (checked 26 Nov 2026).
# Exact days only where Crank-in and Anime Eiga both give them; Netflix only where a source names it.
AN_W27 = [  # (title, date or "", studio, kind new|ret, service key, note)
    ("Sakamoto Days, Season 2", "", "TMS Entertainment", "ret", "netflix", "The retired hitman action-comedy returns in January."),
    ("One-Punch Man, Season 3 Part 2", "", "J.C.Staff", "ret", "tba", "The second half of season 3."),
    ("Mashle: Magic and Muscles, Season 3", "", "A-1 Pictures", "ret", "tba", "The Divine Visionary final exam arc."),
    ("Shangri-La Frontier, Season 3", "", "C2C", "ret", "tba", "The VR game anime continues."),
    ("Golden Kamuy: final chapter", "", "Brain's Base", "ret", "tba", "The final arc, the runaway train."),
    ("The Fable, Season 2", "2027-01-09", "Tezuka Productions", "ret", "tba", "The hitman-in-hiding story returns."),
    ("Yaiba: Samurai Legend, Season 2", "", "WIT Studio", "ret", "tba", "The Kaguya arc."),
    ("Akane-banashi, Season 2", "", "Zexcs", "ret", "tba", "The rakugo storyteller anime continues."),
    ("Red Cat Ramen (Ramen Akaneko), Season 2", "", "E&H production", "ret", "tba", "The cat-run ramen shop is back."),
    ("Marriagetoxin, Season 2", "", "Bones Film", "ret", "tba", "The assassin rom-com returns."),
    ("Medaka Kuroiwa Is Impervious to My Charms, Season 2", "", "SynergySP", "ret", "tba", "Second season of the school rom-com."),
    ("BanG Dream! It's MyGO!!!!! / Ave Mujica sequel", "", "TBA", "ret", "tba", "The next band story."),
    ("The One Piece", "", "WIT Studio", "new", "netflix", "The new remake of One Piece from the start, made for Netflix."),
    ("Sekiro: No Defeat", "", "Qzil.la", "new", "tba", "The anime of FromSoftware's Sekiro: Shadows Die Twice."),
    ("Historie", "", "Liden Films", "new", "tba", "Hitoshi Iwaaki's (Parasyte) historical manga about Eumenes."),
    ("Hirayasumi", "", "Production +h.", "new", "tba", "Slice-of-life manga about a laid-back man in Tokyo."),
    ("Charisma", "2027-01-07", "Pierrot Films", "new", "tba", "New series on TBS."),
    ("The Guy She Was Interested In Wasn't a Guy at All", "2027-01-08", "CloverWorks", "new", "tba", "Yuri rom-com from the web manga."),
    ("Love Live! Hasunosora Girls' High School Idol Club", "", "Sublimation", "new", "tba", "Love Live! idol series."),
    ("Spirit Circle", "", "NAGOMI × EOTA", "new", "tba", "Satoshi Mizukami's reincarnation manga."),
    ("Mairimashita! Iruma-kun IF: Episode of Mafia", "", "NHK Enterprises", "new", "tba", "A side story of Welcome to Demon School! Iruma-kun."),
]
AN_SVC = [("netflix", "Netflix"), ("tba", "Streaming not announced")]
_ANS = dict(AN_SVC)
_ANK = {"new": "New anime", "ret": "New season"}
def _an_gcal(t, d):
    a = d.replace("-", ""); b = (datetime.date.fromisoformat(d) + datetime.timedelta(days=1)).isoformat().replace("-", "")
    return "https://calendar.google.com/calendar/render?action=TEMPLATE&text=" + _qp(t + " premiere") + f"&dates={a}/{b}&details=" + _qp("Japan premiere date via getdayonedrop.com/winter-2027-anime")
def _anrow(x):
    t, d, st, k, s, n = x
    cal = f' · <a href="{e(_an_gcal(t, d))}" rel="nofollow noopener" target="_blank">Add to Google Calendar</a>' if d else ""
    return (f'<div class="row" data-ts="{s}" data-tk="{k}"><span><strong>{e(t)}</strong><br><span class="muted">{e(n)}</span><br><span class="muted">{e(st)} · {e(_ANK[k])} · {e(_ANS[s])}{cal}</span></span>'
            f'<b>{e(_mv_nice(d)) if d else "January 2027"}</b></div>')
_an_sorted = sorted(AN_W27, key=lambda x: (x[1] or "2027-01-99"))
_an_dated = [x for x in AN_W27 if x[1]]
_an_ret = [x for x in AN_W27 if x[3] == "ret"]
_an_new = [x for x in AN_W27 if x[3] == "new"]
_an_chips = ('<div class="chips" role="group" aria-label="Type"><button class="chip" type="button" data-tv-k="" aria-pressed="true">Everything</button>'
             + "".join(f'<button class="chip" type="button" data-tv-k="{k}" aria-pressed="false">{e(l)}</button>' for k, l in _ANK.items()) + '</div>'
             '<div class="chips" role="group" aria-label="Streaming" style="margin-top:8px"><button class="chip" type="button" data-tv-s="" aria-pressed="true">Any service</button>'
             + "".join(f'<button class="chip" type="button" data-tv-s="{k}" aria-pressed="false">{e(l)}</button>' for k, l in AN_SVC) + '</div>')
_an_quick = ("The biggest winter 2027 anime are Sakamoto Days season 2 (Netflix), One-Punch Man season 3 part 2, Mashle season 3, Shangri-La Frontier season 3 and the final chapter of Golden Kamuy. "
             f"New shows include Netflix's One Piece remake, The One Piece, and Sekiro: No Defeat. The season starts in early January 2027; we list {len(AN_W27)} shows.")
_an_body = (f'<header class="hero"><div class="wrap"><span class="kicker">Anime · Winter 2027</span>'
            f'<h1>Winter 2027 anime:<br><span class="amber">every January premiere.</span></h1>'
            f'<p class="lead">New anime and returning seasons starting in January 2027, from Sakamoto Days season 2 and One-Punch Man to The One Piece and the Sekiro anime, with a filter and calendar reminders.</p>'
            f'<p class="muted" style="margin:0">Last checked {e(UPDATED)} · {len(AN_W27)} shows · {len(_an_ret)} returning, {len(_an_new)} new</p></div></header>'
            f'<section><div class="wrap"><div class="out" style="margin-bottom:12px"><div class="row"><span><strong>Quick answer:</strong> {e(_an_quick)}</span></div></div>'
            f'<div class="tool" id="tv-tool" style="margin-bottom:24px"><h2 style="font-size:1.5rem;margin-top:0">Which winter 2027 anime should I watch?</h2>'
            f'<p class="muted">Pick new shows or new seasons, and Netflix or the rest. Your choice is remembered on this device.</p>{_an_chips}'
            f'<p class="mono amber" id="tv-count" aria-live="polite" style="margin:12px 0 0">{len(AN_W27)} shows</p></div>'
            f'<div class="sec-head"><h2>What anime is coming out in winter 2027?</h2><span class="muted">dated first</span></div>'
            f'<div class="out" id="tv-list" style="margin-bottom:10px">{"".join(_anrow(x) for x in _an_sorted)}</div><p class="empty" id="tv-none" hidden>Nothing matches. Try "Everything".</p></div></section>'
            + AD.format("an-mid") +
            f'<section><div class="wrap"><div class="sec-head"><h2>When does the winter 2027 anime season start?</h2></div>'
            f'<p>The first week of January 2027 in Japan. The earliest confirmed days so far: {e(_and([x[0] + " (" + _mv_nice(x[1]) + ")" for x in sorted(_an_dated, key=lambda x: x[1])]))}. Most big shows only say "January 2027" for now; we add the day once two season lists agree.</p>'
            f'<div class="sec-head" style="margin-top:28px"><h2>When does Sakamoto Days season 2 come out?</h2></div>'
            f'<p>January 2027, on Netflix worldwide, from TMS Entertainment again. No exact day yet. Season 1 aired in two parts in 2025.</p>'
            f'<div class="sec-head" style="margin-top:28px"><h2>When does One-Punch Man season 3 part 2 come out?</h2></div>'
            f'<p>January 2027, from J.C.Staff. It continues season 3 after its 2025 first half.</p>'
            f'<div class="sec-head" style="margin-top:28px"><h2>Is there a Sekiro anime?</h2></div>'
            f'<p>Yes. Sekiro: No Defeat, from studio Qzil.la, is listed for winter 2027. It is based on FromSoftware\'s 2019 game. Fans of the game can also see <a href="{href("games-like-elden-ring.html", 0)}">games like Elden Ring</a> and the soulslikes coming in 2027.</p>'
            f'<div class="sec-head" style="margin-top:28px"><h2>When does The One Piece remake come out?</h2></div>'
            f'<p>The season lists put Netflix\'s The One Piece, a new adaptation from WIT Studio, in winter 2027, with no exact day yet. It retells the story from the East Blue saga.</p>'
            f'<div class="sec-head" style="margin-top:28px"><h2>Which anime return with a new season in winter 2027?</h2><span class="muted">{len(_an_ret)}</span></div>'
            f'<p>{e(_and([x[0] for x in _an_ret]))}.</p>'
            f'<div class="sec-head" style="margin-top:28px"><h2>Where can I watch winter 2027 anime?</h2></div>'
            f'<p>Netflix has confirmed Sakamoto Days season 2 and The One Piece. For the rest, Crunchyroll, Netflix, HIDIVE and Prime Video usually announce their simulcasts in December. We will add each one when it is announced.</p>'
            f'<p class="muted">We list a show when at least two winter 2027 season lists (Crank-in, Anime Eiga, Anime Corner, ComicBook.com, GamesRadar+) include it. Dates are Japan TV premieres; simulcasts are usually the same day.</p>'
            f'<div class="sec-head" style="margin-top:28px"><h2>Related pages and tools</h2></div><ul>'
            f'<li><a href="{href("new-tv-shows-january-2027.html", 0)}">New TV shows January 2027</a>: premiere dates and times</li>'
            f'<li><a href="{href("movies-december-2026.html", 0)}">Movies coming out in December 2026</a></li>'
            f'<li><a href="{href("movies-january-2027.html", 0)}">Movies coming out in January 2027</a>: Children of Blood and Bone, Animal Friends</li>'
            f'<li><a href="{href("months/january-2027.html", 0)}">Games coming out in January 2027</a></li>'
            f'<li><a href="{href("countdown.html", 0)}">Release countdown</a> for any dated 2027 game</li></ul></div></section>')
an_faq = [("What anime is coming out in winter 2027?", _an_quick),
          ("When does the winter 2027 anime season start?", "The first week of January 2027 in Japan."),
          ("When does Sakamoto Days season 2 come out?", "January 2027 on Netflix. No exact day yet."),
          ("When does One-Punch Man season 3 part 2 come out?", "January 2027."),
          ("Is there a Sekiro anime?", "Yes. Sekiro: No Defeat from Qzil.la is listed for winter 2027.")]
page("winter-2027-anime.html", "Winter 2027 Anime: Every January 2027 Premiere | DayOneDrop",
     "Winter 2027 anime: Sakamoto Days S2 (Netflix), One-Punch Man S3 part 2, Mashle S3, Shangri-La Frontier S3, The One Piece and Sekiro: No Defeat, by date.",
     _an_body, 0, an_faq, crumbs=[("Home", DOMAIN + "/"), ("Winter 2027 anime", canon("winter-2027-anime.html"))])


# ---------------- MOVIES JANUARY 2027 (26 Nov 2026, DEMAND N26 "movies coming out january 2027") ----------------
# US dates checked 26 Nov 2026: The Numbers 2027 schedule + Box Office Mojo calendars (2027-01-01/15/22/29) agree on each date below.
# Animal Friends 22 Jan also TheWrap ("pushed back 7 months to Jan 2027"); The Rescue = Brandon Sklenar western (TheWrap trailer + release-date story).
# Karoshi: Lionsgate 29 Jan on both, but wide (The Numbers) vs limited (BOM): labelled. Angry Birds 3 shows on BOM 29 Jan but opens 23 Dec 2026 per MV_DEC: left out.
# One schedule only (left out): Bunker, River, Fing!, Slayground, Witch on the Holy Night, Drag, Lords of War, The Third Parent, Pendulum, Cloud Girl.
MV_JAN = [  # (title, date, studio, kind, note, where, week)
    ("Children of Blood and Bone", "2027-01-15", "Paramount", "action", "Fantasy epic from Tomi Adeyemi's novel, directed by Gina Prince-Bythewood, with Viola Davis. Also in IMAX.", "Cinemas and IMAX", 3),
    ("The Beekeeper 2", "2027-01-15", "Amazon MGM Studios", "action", "Jason Statham's action sequel to The Beekeeper (2024).", "Cinemas", 3),
    ("Animal Friends", "2027-01-22", "Warner Bros.", "comedy", "Ryan Reynolds and Jason Momoa in an R-rated comedy that mixes live action and animation. Moved from June 2026.", "Cinemas", 4),
    ("Air Bud Returns", "2027-01-22", "Cineverse", "family", "A new Air Bud film about the basketball-playing golden retriever.", "Cinemas", 4),
    ("The Rescue", "2027-01-29", "Paramount", "action", "A modern western starring Brandon Sklenar (1923, It Ends with Us).", "Cinemas", 5),
    ("Karoshi", "2027-01-29", "Lionsgate", "drama", "Lionsgate release. The schedules differ on size: The Numbers says wide, Box Office Mojo says limited.", "Cinemas", 5),
]
MVJ_KIND = [("action", "Action and fantasy"), ("comedy", "Comedy"), ("family", "Family"), ("drama", "Drama and thriller")]
_MVJK = dict(MVJ_KIND)
MVJ_WEEKS = [(3, "15 Jan"), (4, "22 Jan"), (5, "29 Jan")]
def _mvj_gcal(t, d):
    a = d.replace("-", ""); b = (datetime.date.fromisoformat(d) + datetime.timedelta(days=1)).isoformat().replace("-", "")
    return "https://calendar.google.com/calendar/render?action=TEMPLATE&text=" + _qp(t + " in cinemas") + f"&dates={a}/{b}&details=" + _qp("US release date via getdayonedrop.com/movies-january-2027")
def _mvjrow(m):
    t, d, st, k, note, wh, wk = m
    return (f'<div class="row" data-mk="{k}" data-mm="{wk}"><span><strong>{e(t)}</strong>'
            f'<br><span class="muted">{e(note)}</span><br><span class="muted">{e(st)} · {e(_MVJK[k])} · {e(wh)} · '
            f'<a href="{e(_mvj_gcal(t, d))}" rel="nofollow noopener" target="_blank">Add to Google Calendar</a></span></span><b>{e(_mv_nice(d))}</b></div>')
_mvj_cb = MV_JAN[0]
_mvj_jan_games = [g for g in GAMES if g["date"] and "2027-01-01" <= g["date"] <= "2027-01-31"]
_mvj_feb = [m for m in MOVIES if m[1].startswith("2027-02")]
_mvj_quick = ("The biggest movies coming out in January 2027 are Children of Blood and Bone and The Beekeeper 2, both on 15 January. "
              "Then Animal Friends (Ryan Reynolds and Jason Momoa) and Air Bud Returns on 22 January, and The Rescue and Karoshi on 29 January. "
              f"We list {len(MV_JAN)} US cinema releases that two release schedules date the same; no big film is dated for the first two weekends.")
_mvj_chips = ('<div class="chips" role="group" aria-label="Type"><button class="chip" type="button" data-mv-k="" aria-pressed="true">All movies</button>'
              + "".join(f'<button class="chip" type="button" data-mv-k="{k}" aria-pressed="false">{e(n)}</button>' for k, n in MVJ_KIND) + '</div>'
              '<div class="chips" role="group" aria-label="Week" style="margin-top:8px"><button class="chip" type="button" data-mv-m="" aria-pressed="true">Any week</button>'
              + "".join(f'<button class="chip" type="button" data-mv-m="{w}" aria-pressed="false">{e(l)}</button>' for w, l in MVJ_WEEKS) + '</div>')
_mvj_tbl = ('<div style="overflow-x:auto"><table class="gen-table" style="width:100%;border-collapse:collapse;font-size:.92rem"><thead><tr><th style="text-align:left;padding:6px">Friday</th><th style="text-align:left;padding:6px">Movies opening</th></tr></thead><tbody>'
            + "".join(f'<tr><td style="padding:6px;border-top:1px solid var(--rule)" class="mono">{e(d)}</td><td style="padding:6px;border-top:1px solid var(--rule)">{e(", ".join(m[0] for m in MV_JAN if m[1] == iso) or "No big release dated")}</td></tr>'
                      for d, iso in [("1 Jan", "2027-01-01"), ("8 Jan", "2027-01-08"), ("15 Jan", "2027-01-15"), ("22 Jan", "2027-01-22"), ("29 Jan", "2027-01-29")])
            + '</tbody></table></div>')
_mvj_body = (f'<header class="hero"><div class="wrap"><span class="kicker">Movies · January 2027</span>'
             f'<h1>Movies coming out in January 2027:<br><span class="amber">every cinema release date.</span></h1>'
             f'<p class="lead">Children of Blood and Bone, The Beekeeper 2, Animal Friends and every other January 2027 cinema release, with a type and week filter, a countdown and a calendar reminder for each film.</p>'
             f'<p class="muted" style="margin:0">Last checked {e(UPDATED)} · {len(MV_JAN)} movies · US dates that two release schedules agree on</p></div></header>'
             f'<section><div class="wrap"><div class="out" style="margin-bottom:24px"><div class="row"><span><strong>Quick answer:</strong> {e(_mvj_quick)}</span></div></div>'
             f'<div class="tool" id="mv-tool"><h2 style="font-size:1.5rem;margin-top:0">What should I see at the cinema in January?</h2>'
             f'<p class="muted">Pick a type and a week. The list below updates and your choice is remembered on this device.</p>{_mvj_chips}'
             f'<p class="mono amber" id="mv-count" aria-live="polite" style="margin:12px 0 0">{len(MV_JAN)} movies</p></div>'
             + _mvcd(_mvj_cb, "Countdown to Children of Blood and Bone and The Beekeeper 2") + '</div></section>'
             + AD.format("mvj-mid") +
             f'<section><div class="wrap"><div class="sec-head"><h2>What movies are coming out in January 2027?</h2><span class="muted">{len(MV_JAN)} in cinemas</span></div>'
             f'<p class="muted">In release order, US dates. UK dates can be a week or two different; check your local cinema.</p>'
             f'<div class="out" id="mv-list" style="margin-bottom:10px">{"".join(_mvjrow(m) for m in MV_JAN)}</div><p class="empty" id="mv-none" hidden>Nothing matches. Try "All movies" and "Any week".</p>'
             f'<div class="sec-head" style="margin-top:28px"><h2>When does Children of Blood and Bone come out?</h2></div>'
             f'<p>Friday 15 January 2027 in US cinemas, including IMAX, from Paramount. It adapts Tomi Adeyemi\'s 2018 young adult fantasy novel. Gina Prince-Bythewood (The Woman King) directs and Viola Davis is in the cast.</p>'
             f'<div class="sec-head" style="margin-top:28px"><h2>When does The Beekeeper 2 come out?</h2></div>'
             f'<p>Also Friday 15 January 2027, from Amazon MGM Studios, so it opens against Children of Blood and Bone. Jason Statham returns from the 2024 original.</p>'
             f'<div class="sec-head" style="margin-top:28px"><h2>When does Animal Friends come out?</h2></div>'
             f'<p>22 January 2027, from Warner Bros. It stars Ryan Reynolds and Jason Momoa and mixes live action with animated animals. Warner moved it seven months, out of June 2026.</p>'
             f'<div class="sec-head" style="margin-top:28px"><h2>What family movies come out in January 2027?</h2></div>'
             f'<p>Air Bud Returns (22 January, Cineverse) is the only family film dated so far. Animal Friends looks like a family film but is rated R. The next big animated film is Ice Age: Boiling Point on 5 February 2027.</p>'
             f'<div class="sec-head" style="margin-top:28px"><h2>Which movies open each weekend in January 2027?</h2></div>{_mvj_tbl}'
             f'<div class="sec-head" style="margin-top:28px"><h2>What big movies come after January 2027?</h2></div>'
             f'<p>February 2027 brings {e(_and([m[0] + " (" + _mv_nice(m[1]) + ")" for m in _mvj_feb]) if _mvj_feb else "more big releases")}. Every dated 2027 film is on <a href="{href("movies-2027.html", 0)}">upcoming movies 2027</a>.</p>'
             f'<div class="sec-head" style="margin-top:28px"><h2>What else is out in January 2027?</h2></div>'
             f'<p>{len(_mvj_jan_games)} games on our board launch in January, including Metroid Ravenous and Forza Horizon 6 on PS5. The winter anime season and the network TV midseason premieres also start. See <a href="{href("months/january-2027.html", 0)}">games coming out in January 2027</a>, <a href="{href("new-tv-shows-january-2027.html", 0)}">new TV shows in January 2027</a> and <a href="{href("winter-2027-anime.html", 0)}">winter 2027 anime</a>.</p>'
             f'<p class="muted">We list a film when the studio or at least two release schedules (The Numbers, Box Office Mojo, TheWrap) give the same US date. Films on one schedule only (for example Bunker, River, Slayground and Witch on the Holy Night) are left out until a second one agrees.</p>'
             f'<div class="sec-head" style="margin-top:28px"><h2>Related pages and tools</h2></div><ul>'
             f'<li><a href="{href("movies-december-2026.html", 0)}">Movies coming out in December 2026</a>: Avengers: Doomsday, Dune: Part Three</li>'
             f'<li><a href="{href("movies-2027.html", 0)}">Upcoming movies 2027</a>: Zelda, Shrek 5, Avengers: Secret Wars</li>'
             f'<li><a href="{href("new-tv-shows-january-2027.html", 0)}">New TV shows January 2027</a>: premiere dates and times</li>'
             f'<li><a href="{href("countdown.html", 0)}">Release countdown</a> for any dated 2027 game</li></ul></div></section>')
mvj_faq = [("What movies are coming out in January 2027?", _mvj_quick),
           ("When does Children of Blood and Bone come out?", "15 January 2027 in US cinemas and IMAX, from Paramount."),
           ("When does The Beekeeper 2 come out?", "15 January 2027, from Amazon MGM Studios."),
           ("When does Animal Friends come out?", "22 January 2027, from Warner Bros. It moved from June 2026."),
           ("When does Air Bud Returns come out?", "22 January 2027 in US cinemas, from Cineverse."),
           ("Are there any big movies on 1 January 2027?", "No big studio film is dated for New Year's Day 2027. The first big weekend is 15 January.")]
page("movies-january-2027.html", "Movies Coming Out in January 2027: Release Dates | DayOneDrop",
     "Movies coming out in January 2027: Children of Blood and Bone and The Beekeeper 2 (15 Jan), Animal Friends and Air Bud Returns (22 Jan), The Rescue (29 Jan).",
     _mvj_body, 0, mvj_faq, crumbs=[("Home", DOMAIN + "/"), ("Upcoming movies 2027", canon("movies-2027.html")), ("Movies January 2027", canon("movies-january-2027.html"))])


# ---------------- GAMES LIKE HOLLOW KNIGHT (26 Nov 2026, demand: "games like hollow knight", "games like silksong", "upcoming metroidvania 2027") ----------------
# Evidence: GamesRadar+ "best games like Hollow Knight", ComicBook "metroidvania games to play after Silksong" / "upcoming metroidvanias", ScreenRant, Inverse lists.
# Out-now picks: platforms as sold (backward compatible plays noted). 2027 metroidvanias from games.json.
LIKE_HK = [
    # (title, platforms, why, platform tags, taste tags)
    ("Hollow Knight: Silksong", "Switch 2, Switch, PS5, PS4, Xbox Series X|S, Xbox One, PC", "Team Cherry's 2025 sequel: faster, with Hornet's needle and silk skills, quests and an even bigger kingdom.", "switch ps5 ps4 xbox pc", "hard open fast"),
    ("Hollow Knight", "Switch, PS4, Xbox One, PC (plays on Switch 2, PS5 and Xbox Series X|S)", "Where it started. If you came to Silksong first, the original is still one of the best maps in the genre.", "switch ps5 ps4 xbox pc", "hard open"),
    ("Nine Sols", "PS5, PS4, Xbox Series X|S, Xbox One, Switch, PC", "A hand-drawn 'taopunk' game built on Sekiro-style parries, with tough bosses and a strong story.", "switch ps5 ps4 xbox pc", "hard fast story"),
    ("Prince of Persia: The Lost Crown", "PS5, PS4, Xbox Series X|S, Xbox One, Switch, PC", "Ubisoft Montpellier's 2024 metroidvania: tight combat, time powers and a map you can pin screenshots to.", "switch ps5 ps4 xbox pc", "fast open"),
    ("Metroid Dread", "Switch (plays on Switch 2)", "The 2021 2D Metroid from MercurySteam, the same studio making Metroid Ravenous for January 2027.", "switch", "fast open"),
    ("Ori and the Will of the Wisps", "Xbox Series X|S, Xbox One, Switch, PC", "Beautiful, emotional and lighter on difficulty, with great movement and chase sequences.", "switch xbox pc", "story open"),
    ("Blasphemous 2", "PS5, Xbox Series X|S, Switch, PC", "Dark religious art, hard bosses and three weapons to switch between.", "switch ps5 xbox pc", "hard"),
    ("Ender Magnolia: Bloom in the Mist", "PS5, PS4, Xbox Series X|S, Switch, PC", "A sad, beautiful fantasy where you fight with spirits you free along the way.", "switch ps5 ps4 xbox pc", "story open"),
    ("Animal Well", "PS5, Xbox Series X|S, Switch, PC", "No combat at all, just a dense pixel world full of secrets and puzzles.", "switch ps5 xbox pc", "open"),
    ("Dead Cells", "PS4, Xbox One, Switch, PC (plays on PS5, Xbox Series X|S and Switch 2)", "Fast roguelite metroidvania: you lose everything when you die, but every run teaches you more.", "switch ps5 ps4 xbox pc", "hard fast"),
    ("Bloodstained: Ritual of the Night", "PS4, Xbox One, Switch, PC (plays on PS5 and Xbox Series X|S)", "Koji Igarashi's Castlevania-style castle crawl. Its follow-up, The Scarlet Engagement, is due in 2027.", "switch ps5 ps4 xbox pc", "open story"),
]
_HK_LABEL = {"hard": "Tough bosses", "open": "Exploring", "story": "Strong story", "fast": "Fast combat"}
_hk_rows = "".join(f'<div class="row" data-ep="{e(x[3])}" data-el="{e(x[4])}"><span><strong>{e(x[0])}</strong><br><span class="muted">{e(x[2])}</span><br><span class="muted">{e(x[1])}</span>'
                   f'<br><span class="muted mono" style="font-size:.78rem">{e(" · ".join(_HK_LABEL[k] for k in x[4].split()))}</span></span></div>' for x in LIKE_HK)
_hk_chips = ('<div class="chips" role="group" aria-label="Platform"><button class="chip" type="button" data-er-p="" aria-pressed="true">Any platform</button>'
             + "".join(f'<button class="chip" type="button" data-er-p="{k}" aria-pressed="false">{l}</button>' for k, l in [("switch", "Switch / Switch 2"), ("ps5", "PS5"), ("xbox", "Xbox"), ("pc", "PC"), ("ps4", "PS4")]) + '</div>'
             '<div class="chips" role="group" aria-label="What you liked" style="margin-top:10px"><button class="chip" type="button" data-er-l="" aria-pressed="true">Anything</button>'
             + "".join(f'<button class="chip" type="button" data-er-l="{k}" aria-pressed="false">{e(l)}</button>' for k, l in _HK_LABEL.items()) + '</div>')
HK_SOON_SLUGS = ["metroid-ravenous", "mariachi-legends", "bloodstained-the-scarlet-engagement", "blighted"]
_hk_soon = sorted([g for g in GAMES if g["slug"] in HK_SOON_SLUGS], key=lambda g: (g["month"] or 13, g["date"] or "9999"))
_hk_first = next((g for g in _hk_soon if g["date"]), None)
_hk_mr = next((g for g in GAMES if g["slug"] == "metroid-ravenous"), None)
def _hk_on(tag): return [x[0] for x in LIKE_HK if tag in x[3].split()]
_hk_cd = (f'<div class="cdw"><span class="lbl">Countdown to {e(_hk_first["title"])}</span><div class="cd" data-countdown="{_hk_first["date"]}">'
          '<div class="cd-unit"><span class="flaps" data-u="0"></span><span>Days</span></div><div class="cd-unit"><span class="flaps" data-u="1"></span><span>Hrs</span></div>'
          '<div class="cd-unit"><span class="flaps" data-u="2"></span><span>Min</span></div><div class="cd-unit"><span class="flaps" data-u="3"></span><span>Sec</span></div></div></div>') if _hk_first else ""
_hk_quick = ("The best games like Hollow Knight and Silksong are Nine Sols, Prince of Persia: The Lost Crown, Metroid Dread, Ori and the Will of the Wisps, Blasphemous 2 and Ender Magnolia. "
             f"The next metroidvanias are {_and([g['title'] + ' (' + nice_date(g) + ')' for g in _hk_soon])}.")
hk_body = (f'<header class="hero"><div class="wrap"><span class="kicker">Games like Hollow Knight</span>'
           f'<h1>Games like Hollow Knight and Silksong:<br><span class="amber">play now, and the 2027 metroidvanias.</span></h1>'
           f'<p class="lead">Metroidvanias you can play today on Switch 2, PS5, Xbox and PC, filtered by what you loved about Hollow Knight, plus every metroidvania due in 2027.</p>'
           f'<p class="muted" style="margin:0">Last checked {e(UPDATED)} · {len(LIKE_HK)} picks out now · {len(_hk_soon)} coming in 2027</p></div></header>'
           f'<section><div class="wrap"><div class="out" style="margin-bottom:12px"><div class="row"><span><strong>Quick answer:</strong> {e(_hk_quick)}</span></div></div>'
           f'<div class="tool" id="er-tool" style="margin-bottom:24px"><h2 style="font-size:1.5rem;margin-top:0">Which game like Hollow Knight should I play?</h2>'
           f'<p class="muted">Pick your platform and what you liked most. Your choice is remembered on this device.</p>{_hk_chips}'
           f'<p class="mono amber" id="er-count" aria-live="polite" style="margin:12px 0 0">{len(LIKE_HK)} games</p></div>'
           f'<div class="sec-head"><h2>What games are like Hollow Knight?</h2><span class="muted">out now</span></div>'
           f'<div class="out" id="er-list" style="margin-bottom:10px">{_hk_rows}</div><p class="empty" id="er-none" hidden>No pick matches both. Try "Anything".</p></div></section>'
           + AD.format("hk-mid") +
           f'<section><div class="wrap"><div class="sec-head"><h2>What metroidvania games are coming out in 2027?</h2><span class="muted">{len(_hk_soon)}</span></div>'
           f'<div class="out" style="margin-bottom:10px">{"".join(_er_srow(g) for g in _hk_soon)}</div>{_hk_cd}'
           f'<div class="sec-head" style="margin-top:28px"><h2>When does Metroid Ravenous come out?</h2></div>'
           + (f'<p>{e(nice_date(_hk_mr))}, only on Nintendo Switch 2. It is a new side-scrolling Metroid from MercurySteam, the studio behind Metroid Dread, so it is the closest 2027 game to Hollow Knight on a Nintendo console. See the <a href="{href("games/metroid-ravenous.html", 0)}">Metroid Ravenous release date page</a>.</p>' if _hk_mr else '<p>See the Switch 2 page.</p>')
           + f'<div class="sec-head" style="margin-top:28px"><h2>Is there a new Bloodstained game?</h2></div>'
           f'<p>Yes. Bloodstained: The Scarlet Engagement, from Koji Igarashi\'s studio ArtPlay and 505 Games, is coming to PS5, Xbox Series X|S and PC in 2027. It was delayed from 2026 in August 2026 and has no month yet.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>Is there a co-op game like Hollow Knight?</h2></div>'
           f'<p>Blighted, from Guacamelee! studio DrinkBox, is a metroidvania action RPG you can play alone or in co-op. It moved from fall 2026 to 2027 and is coming to Switch 2 and PC.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>What games are like Hollow Knight on Switch 2?</h2></div>'
           f'<p>{e(_and(_hk_on("switch")))}. Switch 1 games play on Switch 2. In 2027: {e(_and([g["title"] for g in _hk_soon if "Switch 2" in g["platforms"]]))}. See every <a href="{href("platforms/switch-2.html", 0)}">Switch 2 game of 2027</a>.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>What games are like Hollow Knight on PS5 and Xbox?</h2></div>'
           f'<p>PS5: {e(_and(_hk_on("ps5")))}. Xbox: {e(_and(_hk_on("xbox")))}. In 2027 on PS5 and Xbox: {e(_and([g["title"] for g in _hk_soon if "PS5" in g["platforms"]]))}.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>What is the hardest game like Hollow Knight?</h2></div>'
           f'<p>Silksong itself is harder than the first game. After that, Nine Sols and Blasphemous 2 have the toughest bosses. If you want something gentler, Ori and the Will of the Wisps and Animal Well are kinder, and Animal Well has no fights at all. For 3D bosses, see <a href="{href("games-like-elden-ring.html", 0)}">games like Elden Ring</a>.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>Related pages and tools</h2></div><ul>'
           f'<li><a href="{href("games-like-elden-ring.html", 0)}">Games like Elden Ring</a>: soulslikes now and in 2027</li>'
           f'<li><a href="{href("games/metroid-ravenous.html", 0)}">Metroid Ravenous release date</a></li>'
           f'<li><a href="{href("games-like-zelda.html", 0)}">Games like Zelda</a>: dungeons and open worlds</li>'
           f'<li><a href="{href("games-by-genre-2027.html", 0)}">2027 games by genre</a></li>'
           f'<li><a href="{href("countdown.html", 0)}">Game release countdown</a></li></ul></div></section>')
hk_faq = [("What games are like Hollow Knight?", "Hollow Knight: Silksong, Nine Sols, Prince of Persia: The Lost Crown, Metroid Dread, Ori and the Will of the Wisps, Blasphemous 2, Ender Magnolia, Animal Well, Dead Cells and Bloodstained: Ritual of the Night."),
          ("What metroidvania games come out in 2027?", _and([g['title'] + ' (' + nice_date(g) + ')' for g in _hk_soon]) + "."),
          ("When does Metroid Ravenous come out?", (nice_date(_hk_mr) + ", only on Nintendo Switch 2.") if _hk_mr else "2027 on Switch 2."),
          ("Is there a co-op metroidvania coming in 2027?", "Yes. Blighted from DrinkBox Studios can be played solo or in co-op; it is due in 2027 on Switch 2 and PC."),
          ("What is a good game like Hollow Knight on Switch 2?", "Silksong, Nine Sols, Metroid Dread and Prince of Persia: The Lost Crown, then Metroid Ravenous in 2027.")]
page("games-like-hollow-knight.html", "Games Like Hollow Knight & Silksong: 2027 Picks | DayOneDrop",
     "Games like Hollow Knight and Silksong on Switch 2, PS5, Xbox and PC: Nine Sols, Lost Crown, Metroid Dread, Ori, plus 2027's Metroid Ravenous and Bloodstained.",
     hk_body, 0, hk_faq, crumbs=[("Home", DOMAIN + "/"), ("2027 games by genre", canon("games-by-genre-2027.html")), ("Games like Hollow Knight", canon("games-like-hollow-knight.html"))])

# ---------------- GAMES LIKE STARDEW VALLEY (27 Nov 2026, demand: "games like stardew valley", "cozy games 2027", "upcoming farming games") ----------------
# Evidence: GamesRadar+ / PC Gamer / Dot Esports / games.gg "games like Stardew Valley" lists, PC Gamer "39 Stardew-shaped farm sims", games.gg upcoming cozy games.
# Stardew 1.7: ConcernedApe says it will probably arrive in 2027 (GamesRadar+, PC Gamer guide). No date. 2027 picks from games.json.
LIKE_SV = [
    ("Stardew Valley", "PS4, Xbox One, Switch, PC, mobile (plays on PS5, Xbox Series X|S and Switch 2)", "Still the one to beat. Its biggest update yet, 1.7, is expected some time in 2027 (no date yet), so now is a good time to start a new farm.", "switch ps5 ps4 xbox pc", "farm town coop"),
    ("Coral Island", "PS5, Xbox Series X|S, PC", "A tropical-island Stardew with a big cast, diving, a coral reef to restore and lots to romance.", "ps5 xbox pc", "farm town"),
    ("Rune Factory: Guardians of Azuma", "Switch 2, Switch, PC", "Farming plus real-time combat in a Japanese-inspired world. Pick this if you liked Stardew's mines most.", "switch pc", "farm town"),
    ("Story of Seasons: Grand Bazaar", "Switch 2, Switch, PC", "The 2025 remake of a fan-favourite Harvest Moon-style game: farm all week, then sell at the weekly market.", "switch pc", "farm town relax"),
    ("Animal Crossing: New Horizons", "Switch (Switch 2 Edition too)", "No farm and no deadlines: build up an island at your own pace and visit friends' islands.", "switch", "town coop relax"),
    ("Disney Dreamlight Valley", "PS5, PS4, Xbox Series X|S, Xbox One, Switch, PC", "Gardening, cooking and friendships with Disney and Pixar characters, with quests to follow.", "switch ps5 ps4 xbox pc", "farm town relax"),
    ("Palia", "PS5, Xbox Series X|S, Switch, PC", "A free-to-play online life sim: farm, cook, fish and decorate your plot next to other players.", "switch ps5 xbox pc", "farm town coop relax"),
    ("Fae Farm", "PS5, Xbox Series X|S, Switch, PC", "A bright, magical farm sim built for up to four players together.", "switch ps5 xbox pc", "farm town coop"),
    ("My Time at Sandrock", "PS5, PS4, Xbox Series X|S, Xbox One, Switch, PC", "Less farming, more crafting: run a workshop and rebuild a desert town, with online co-op.", "switch ps5 ps4 xbox pc", "town coop"),
    ("Slime Rancher 2", "PS5, Xbox Series X|S, PC", "Ranch cute slimes on a colourful island. No combat, just collecting and building.", "ps5 xbox pc", "farm relax"),
    ("Spiritfarer", "PS4, Xbox One, Switch, PC (plays on PS5, Xbox Series X|S and Switch 2)", "A gentle boat-management game about saying goodbye, from Thunder Lotus, whose At Fate's End is due in 2027.", "switch ps5 ps4 xbox pc", "coop relax"),
]
_SV_LABEL = {"farm": "Farming", "town": "Town and romance", "coop": "Play together", "relax": "No pressure"}
SV_SOON = ["emberville", "witchbrook", "atelier-karia", "grave-seasons", "neverway"]
_sv_soon = sorted([g for g in GAMES if g["slug"] in SV_SOON], key=lambda g: (g["month"] or 13, g["date"] or "9999"))
_sv_wb = next((g for g in GAMES if g["slug"] == "witchbrook"), None)
_sv_gs = next((g for g in GAMES if g["slug"] == "grave-seasons"), None)
def _sv_on(tag): return [x[0] for x in LIKE_SV if tag in x[3].split()]
def _like_rows(lst, lab):
    return "".join(f'<div class="row" data-ep="{e(x[3])}" data-el="{e(x[4])}"><span><strong>{e(x[0])}</strong><br><span class="muted">{e(x[2])}</span><br><span class="muted">{e(x[1])}</span>'
                   f'<br><span class="muted mono" style="font-size:.78rem">{e(" · ".join(lab[k] for k in x[4].split()))}</span></span></div>' for x in lst)
def _like_chips(lab, likes="What you liked"):
    return ('<div class="chips" role="group" aria-label="Platform"><button class="chip" type="button" data-er-p="" aria-pressed="true">Any platform</button>'
            + "".join(f'<button class="chip" type="button" data-er-p="{k}" aria-pressed="false">{l}</button>' for k, l in [("switch", "Switch / Switch 2"), ("ps5", "PS5"), ("xbox", "Xbox"), ("pc", "PC"), ("ps4", "PS4")]) + '</div>'
            f'<div class="chips" role="group" aria-label="{e(likes)}" style="margin-top:10px"><button class="chip" type="button" data-er-l="" aria-pressed="true">Anything</button>'
            + "".join(f'<button class="chip" type="button" data-er-l="{k}" aria-pressed="false">{e(l)}</button>' for k, l in lab.items()) + '</div>')
def _like_cd(g):
    return (f'<div class="cdw"><span class="lbl">Countdown to {e(g["title"])}</span><div class="cd" data-countdown="{g["date"]}">'
            '<div class="cd-unit"><span class="flaps" data-u="0"></span><span>Days</span></div><div class="cd-unit"><span class="flaps" data-u="1"></span><span>Hrs</span></div>'
            '<div class="cd-unit"><span class="flaps" data-u="2"></span><span>Min</span></div><div class="cd-unit"><span class="flaps" data-u="3"></span><span>Sec</span></div></div></div>') if g and g.get("date") else ""
_sv_quick = ("The best games like Stardew Valley right now are Coral Island, Rune Factory: Guardians of Azuma, Story of Seasons: Grand Bazaar, Fae Farm, Palia and Disney Dreamlight Valley. "
             f"The next big ones are {_and([g['title'] + ' (' + nice_date(g) + ')' for g in _sv_soon])}. Stardew's own 1.7 update is expected in 2027, with no date yet.")
sv_body = (f'<header class="hero"><div class="wrap"><span class="kicker">Games like Stardew Valley</span>'
           f'<h1>Games like Stardew Valley:<br><span class="amber">cozy farm sims now, and the 2027 ones.</span></h1>'
           f'<p class="lead">Farming and life sims to play today on Switch 2, PS5, Xbox and PC, filtered by what you love about Stardew, plus every cozy game dated for 2027.</p>'
           f'<p class="muted" style="margin:0">Last checked {e(UPDATED)} · {len(LIKE_SV)} picks out now · {len(_sv_soon)} coming in 2027</p></div></header>'
           f'<section><div class="wrap"><div class="out" style="margin-bottom:12px"><div class="row"><span><strong>Quick answer:</strong> {e(_sv_quick)}</span></div></div>'
           f'<div class="tool" id="er-tool" style="margin-bottom:24px"><h2 style="font-size:1.5rem;margin-top:0">Which game like Stardew Valley should I play?</h2>'
           f'<p class="muted">Pick your platform and what you love most. Your choice is remembered on this device.</p>{_like_chips(_SV_LABEL, "What you love")}'
           f'<p class="mono amber" id="er-count" aria-live="polite" style="margin:12px 0 0">{len(LIKE_SV)} games</p></div>'
           f'<div class="sec-head"><h2>What games are like Stardew Valley?</h2><span class="muted">out now</span></div>'
           f'<div class="out" id="er-list" style="margin-bottom:10px">{_like_rows(LIKE_SV, _SV_LABEL)}</div><p class="empty" id="er-none" hidden>No pick matches both. Try "Anything".</p></div></section>'
           + AD.format("sv-mid") +
           f'<section><div class="wrap"><div class="sec-head"><h2>What cozy games are coming out in 2027?</h2><span class="muted">{len(_sv_soon)}</span></div>'
           f'<div class="out" style="margin-bottom:10px">{"".join(_er_srow(g) for g in _sv_soon)}</div>{_like_cd(_sv_wb)}'
           f'<div class="sec-head" style="margin-top:28px"><h2>When does Witchbrook come out?</h2></div>'
           + (f'<p>{e(nice_date(_sv_wb))} on PS5, Xbox Series X|S, PC, Switch and Switch 2 on the same day, and on Xbox Game Pass from day one. Chucklefish, who published Stardew Valley on consoles, is behind it: you study magic at a college in a seaside town, with up to four players online. It slipped from 2025 and then 2026. See the <a href="{href("games/witchbrook.html", 0)}">Witchbrook release date page</a>.</p>' if _sv_wb else '')
           + f'<div class="sec-head" style="margin-top:28px"><h2>When does Grave Seasons come out?</h2></div>'
           + (f'<p>{e(nice_date(_sv_gs))} on PS5, Xbox Series X|S, PC and Switch, and on Game Pass (Gematsu, VGChartz). Blumhouse Games publishes it. It looks like Stardew, but a killer is loose in the village and you have to work out who it is between harvests. If that sounds fun, see <a href="{href("horror-games-2027.html", 0)}">every horror game of 2027</a>.</p>' if _sv_gs else '')
           + f'<div class="sec-head" style="margin-top:28px"><h2>When is the Stardew Valley 1.7 update coming out?</h2></div>'
           f'<p>There is no date. ConcernedApe (Eric Barone) has said 1.7 will be the biggest update yet and will probably come out in 2027 (GamesRadar+, PC Gamer). Haunted Chocolatier, his next game, also has no release date. We will add both to the board the day a date is announced.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>What games are like Stardew Valley on Switch 2?</h2></div>'
           f'<p>{e(_and(_sv_on("switch")))}. Switch 1 games play on Switch 2. In 2027: {e(_and([g["title"] for g in _sv_soon if "Switch 2" in g["platforms"]]) or "Witchbrook")}. See every <a href="{href("platforms/switch-2.html", 0)}">Switch 2 game of 2027</a>.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>What games are like Stardew Valley on PS5 and Xbox?</h2></div>'
           f'<p>PS5: {e(_and(_sv_on("ps5")))}. Xbox: {e(_and(_sv_on("xbox")))}. In 2027 on PS5 and Xbox: {e(_and([g["title"] for g in _sv_soon if "PS5" in g["platforms"]]))}.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>What is a good multiplayer game like Stardew Valley?</h2></div>'
           f'<p>{e(_and([x[0] for x in LIKE_SV if "coop" in x[4].split()]))} all let you play with friends. Witchbrook adds online play for up to four in January 2027.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>Related pages and tools</h2></div><ul>'
           f'<li><a href="{href("games/witchbrook.html", 0)}">Witchbrook release date</a> and countdown</li>'
           f'<li><a href="{href("games-like-zelda.html", 0)}">Games like Zelda</a>: adventures now and in 2027</li>'
           f'<li><a href="{href("games-like-minecraft.html", 0)}">Games like Minecraft</a>: building and survival, now and in 2027</li>'
           f'<li><a href="{href("games-by-genre-2027.html", 0)}">2027 games by genre</a></li>'
           f'<li><a href="{href("backlog-planner-2027.html", 0)}">2027 backlog planner</a>: finish your farm before the next one lands</li></ul></div></section>')
sv_faq = [("What games are like Stardew Valley?", "Coral Island, Rune Factory: Guardians of Azuma, Story of Seasons: Grand Bazaar, Animal Crossing: New Horizons, Disney Dreamlight Valley, Palia, Fae Farm, My Time at Sandrock, Slime Rancher 2 and Spiritfarer."),
          ("What cozy games come out in 2027?", _and([g['title'] + ' (' + nice_date(g) + ')' for g in _sv_soon]) + "."),
          ("When does Witchbrook come out?", (nice_date(_sv_wb) + " on PS5, Xbox Series X|S, PC, Switch and Switch 2, and on Game Pass day one.") if _sv_wb else "2027."),
          ("When is Stardew Valley 1.7 coming out?", "No date yet. ConcernedApe says it will probably arrive in 2027 and will be the biggest update so far."),
          ("What is a game like Stardew Valley but with a mystery?", (f"Grave Seasons ({nice_date(_sv_gs)}): a farming life sim with a serial killer loose in the village.") if _sv_gs else "Grave Seasons, due in 2027.")]
page("games-like-stardew-valley.html", "Games Like Stardew Valley: Cozy Picks & 2027 Farm Sims | DayOneDrop",
     "Games like Stardew Valley on Switch 2, PS5, Xbox and PC: Coral Island, Rune Factory, Fae Farm, Palia, plus 2027's Witchbrook, Grave Seasons and Stardew 1.7.",
     sv_body, 0, sv_faq, crumbs=[("Home", DOMAIN + "/"), ("2027 games by genre", canon("games-by-genre-2027.html")), ("Games like Stardew Valley", canon("games-like-stardew-valley.html"))])


# ---------------- GAMES LIKE ZELDA (27 Nov 2026, demand: "games like zelda", "games like breath of the wild", "zelda 2027") ----------------
# Evidence: GamesRadar+ "games like Zelda", Push Square "best PS5 games like Zelda", Pocket Tactics, G2A, T3, Windows Central lists; Zelda movie date already 2-source on /movies-2027.
LIKE_ZE = [
    ("The Legend of Zelda: Echoes of Wisdom", "Switch (plays on Switch 2)", "The 2024 top-down Zelda where you play as Zelda and solve problems by copying objects and monsters.", "switch", "puzzle"),
    ("Immortals Fenyx Rising", "PS5, PS4, Xbox Series X|S, Xbox One, Switch, PC", "The closest thing to Breath of the Wild on PlayStation and Xbox: gliding, climbing and puzzle vaults across a Greek-myth island.", "switch ps5 ps4 xbox pc", "open puzzle"),
    ("Genshin Impact", "PS5, PS4, Xbox Series X|S, PC, mobile", "Free-to-play open world with climbing, gliding and elemental puzzles everywhere.", "ps5 ps4 xbox pc", "open combat"),
    ("Tunic", "PS5, PS4, Xbox Series X|S, Xbox One, Switch, PC", "A tiny fox in a classic-Zelda world, with secrets hidden in an in-game manual you piece together.", "switch ps5 ps4 xbox pc", "puzzle combat"),
    ("Death's Door", "PS5, PS4, Xbox Series X|S, Xbox One, Switch, PC", "Short, sharp dungeon crawling as a crow, with real Zelda-style dungeons and bosses.", "switch ps5 ps4 xbox pc", "puzzle combat"),
    ("Okami HD", "PS4, Xbox One, Switch, PC (plays on PS5, Xbox Series X|S and Switch 2)", "Capcom's painted adventure: dungeons, items and a celestial brush to draw your powers.", "switch ps5 ps4 xbox pc", "puzzle story"),
    ("Elden Ring", "PS5, PS4, Xbox Series X|S, Xbox One, PC", "If Breath of the Wild's freedom is what you loved, this is that world with much harder fights.", "ps5 ps4 xbox pc", "open combat"),
    ("Kena: Bridge of Spirits", "PS5, PS4, Xbox Series X|S, Xbox One, PC", "Pixar-like looks, Zelda-like temples and tiny Rot helpers that solve puzzles with you.", "ps5 ps4 xbox pc", "puzzle story combat"),
    ("Sable", "PS5, Xbox Series X|S, Xbox One, Switch, PC", "A calm desert open world with no combat: climb, glide and explore at your own pace.", "switch ps5 xbox pc", "open story"),
    ("Xenoblade Chronicles X: Definitive Edition", "Switch (plays on Switch 2)", "A huge alien world to explore on foot and later by mech, from the studio making Xenoblade Genesis for 2027.", "switch", "open story combat"),
]
_ZE_LABEL = {"open": "Open world", "puzzle": "Dungeons and puzzles", "combat": "Combat", "story": "Story"}
ZE_SOON = ["terranigma", "fable", "hyrule-warriors-age-of-calamity-definitive-edition", "demi-and-the-fractured-dream", "kirby-and-the-world-beyond", "xenoblade-genesis", "pokemon-winds-and-waves"]
_ze_soon = sorted([g for g in GAMES if g["slug"] in ZE_SOON], key=lambda g: (g["month"] or 13, g["date"] or "9999"))
_ze_hw = next((g for g in GAMES if g["slug"] == "hyrule-warriors-age-of-calamity-definitive-edition"), None)
_ze_mov = next((m for m in MOVIES if m[0] == "The Legend of Zelda"), None)
_ze_mov_d = nice_date({"date": _ze_mov[1], "window": ""}) if _ze_mov else "2027"
def _ze_on(tag): return [x[0] for x in LIKE_ZE if tag in x[3].split()]
_ze_quick = ("The best games like Zelda are Immortals Fenyx Rising, Genshin Impact, Tunic, Death's Door, Okami HD and Sable, and Elden Ring if you want Breath of the Wild's freedom with harder fights. "
             f"In 2027, Hyrule Warriors: Age of Calamity comes to Switch 2 on {nice_date(_ze_hw) if _ze_hw else '25 February'}, and the live-action Zelda movie opens on {_ze_mov_d}. No new main Zelda game has been announced.")
ze_body = (f'<header class="hero"><div class="wrap"><span class="kicker">Games like Zelda</span>'
           f'<h1>Games like Zelda:<br><span class="amber">adventures to play now, and Zelda in 2027.</span></h1>'
           f'<p class="lead">Zelda-style adventures you can play on PS5, Xbox, PC and Switch 2, filtered by what you love about Breath of the Wild or the classic dungeons, plus every 2027 game and date a Zelda fan needs.</p>'
           f'<p class="muted" style="margin:0">Last checked {e(UPDATED)} · {len(LIKE_ZE)} picks out now · {len(_ze_soon)} coming in 2027</p></div></header>'
           f'<section><div class="wrap"><div class="out" style="margin-bottom:12px"><div class="row"><span><strong>Quick answer:</strong> {e(_ze_quick)}</span></div></div>'
           f'<div class="tool" id="er-tool" style="margin-bottom:24px"><h2 style="font-size:1.5rem;margin-top:0">Which game like Zelda should I play?</h2>'
           f'<p class="muted">Pick your platform and what you love most. Your choice is remembered on this device.</p>{_like_chips(_ZE_LABEL, "What you love")}'
           f'<p class="mono amber" id="er-count" aria-live="polite" style="margin:12px 0 0">{len(LIKE_ZE)} games</p></div>'
           f'<div class="sec-head"><h2>What games are like Zelda?</h2><span class="muted">out now</span></div>'
           f'<div class="out" id="er-list" style="margin-bottom:10px">{_like_rows(LIKE_ZE, _ZE_LABEL)}</div><p class="empty" id="er-none" hidden>No pick matches both. Try "Anything".</p></div></section>'
           + AD.format("ze-mid") +
           f'<section><div class="wrap"><div class="sec-head"><h2>What games like Zelda are coming out in 2027?</h2><span class="muted">{len(_ze_soon)}</span></div>'
           f'<div class="out" style="margin-bottom:10px">{"".join(_er_srow(g) for g in _ze_soon)}</div>{_like_cd(_ze_hw)}'
           f'<div class="sec-head" style="margin-top:28px"><h2>Is there a new Zelda game in 2027?</h2></div>'
           f'<p>No new main Zelda game has been announced for 2027. The Zelda release on the 2027 calendar is Hyrule Warriors: Age of Calamity for Switch 2 ({e(nice_date(_ze_hw)) if _ze_hw else "25 February 2027"}), a 60fps version of the action spin-off set 100 years before Breath of the Wild, with all its DLC. The Switch 2 Ocarina of Time remake is already out and nominated for Game of the Year at The Game Awards 2026. See the <a href="{href("games/hyrule-warriors-age-of-calamity-definitive-edition.html", 0)}">Hyrule Warriors release date page</a>.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>When does the Legend of Zelda movie come out?</h2></div>'
           f'<p>{e(_ze_mov_d)}, in cinemas worldwide. It is a live-action film from Sony Pictures and Nintendo, directed by Wes Ball, with Bo Bragason as Zelda and Benjamin Evan Ainsworth as Link. It was first set for 26 March 2027, then 7 May, before moving a week earlier. More 2027 film dates are on <a href="{href("movies-2027.html", 0)}">upcoming movies 2027</a>.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>What 2027 game is most like old-school top-down Zelda?</h2></div>'
           f'<p>Demi and the Fractured Dream (27 February 2027, from Yarn Owl and Annapurna Interactive) is a top-down action adventure, and Terranigma (14 January 2027) brings back a 1995 Super Nintendo action RPG that never had an official North American release. For 3D exploration on Switch 2, Kirby and the World Beyond (spring 2027) lets you roam a large open world.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>What games are like Zelda on PS5 and Xbox?</h2></div>'
           f'<p>PS5: {e(_and(_ze_on("ps5")))}. Xbox: {e(_and(_ze_on("xbox")))}. In 2027, Fable (fairy-tale action RPG, {e(nice_date(next((g for g in _ze_soon if g["slug"] == "fable"), {"date": "2027-02-23", "window": ""})))}) is the big one on both.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>What games are like Zelda on Switch 2?</h2></div>'
           f'<p>{e(_and(_ze_on("switch")))}. Switch 1 games play on Switch 2. In 2027: {e(_and([g["title"] for g in _ze_soon if "Switch 2" in g["platforms"]]))}. See every <a href="{href("platforms/switch-2.html", 0)}">Switch 2 game of 2027</a>.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>Related pages and tools</h2></div><ul>'
           f'<li><a href="{href("games-like-elden-ring.html", 0)}">Games like Elden Ring</a>: open worlds with harder bosses</li>'
           f'<li><a href="{href("games-like-stardew-valley.html", 0)}">Games like Stardew Valley</a>: cozy picks and 2027 farm sims</li>'
           f'<li><a href="{href("games-like-animal-crossing.html", 0)}">Games like Animal Crossing</a>: island life and villagers</li>'
           f'<li><a href="{href("nintendo-direct.html", 0)}">Next Nintendo Direct</a>: where a new Zelda would be announced</li>'
           f'<li><a href="{href("countdown.html", 0)}">Game release countdown</a></li></ul></div></section>')
ze_faq = [("What games are like Zelda?", "Immortals Fenyx Rising, Genshin Impact, Tunic, Death's Door, Okami HD, Elden Ring, Kena: Bridge of Spirits, Sable, Xenoblade Chronicles X and Zelda: Echoes of Wisdom."),
          ("Is there a new Zelda game coming out in 2027?", f"No new main Zelda game has been announced. Hyrule Warriors: Age of Calamity comes to Switch 2 on {nice_date(_ze_hw) if _ze_hw else '25 February 2027'}."),
          ("When does the Zelda movie come out?", f"{_ze_mov_d}, in cinemas worldwide."),
          ("What is a game like Breath of the Wild on PS5?", "Immortals Fenyx Rising is the closest, with Genshin Impact, Sable and Elden Ring for open-world exploration."),
          ("What games like Zelda come out in 2027?", _and([g['title'] + ' (' + nice_date(g) + ')' for g in _ze_soon]) + ".")]
page("games-like-zelda.html", "Games Like Zelda: Best Picks & Zelda in 2027 | DayOneDrop",
     "Games like Zelda and Breath of the Wild on PS5, Xbox, PC and Switch 2: Immortals, Tunic, Okami, Genshin, plus Hyrule Warriors and the Zelda movie in 2027.",
     ze_body, 0, ze_faq, crumbs=[("Home", DOMAIN + "/"), ("2027 games by genre", canon("games-by-genre-2027.html")), ("Games like Zelda", canon("games-like-zelda.html"))])


# ---------------- GAMES LIKE POKEMON (27 Nov 2026, demand: "games like pokemon", "monster taming games", "creature collector 2027") ----------------
# Evidence: GamesRadar+ (US/UK/AU), GameSpot gallery, Game Rant, Insider Gaming, Windows Central, TheGamer, ComicBook "Pokemon rivals 2026" lists.
# 2027: Pokémon Winds and Waves (Nintendo, Engadget, TechRadar: 2027, Switch 2), Cassette Beasts 2002 (Gematsu, RPG Site, VGChartz: March 2027), Honkai: Nexus Anima (spring 2027).
LIKE_PK = [
    ("Pokémon Legends: Z-A", "Switch (Switch 2 Edition too)", "The newest Pokémon game, out since October 2025: real-time battles across Lumiose City. Play this first while you wait for Winds and Waves.", "switch", "catch battle"),
    ("Palworld", "PS5, Xbox Series X|S, PC", "Catch creatures, then put them to work building and defending your base. Pokémon meets survival crafting.", "ps5 xbox pc", "catch open"),
    ("Temtem", "PS5, Xbox Series X|S, Switch, PC", "The closest thing to a main Pokémon game on PlayStation and Xbox: catch, breed and battle in two-on-two fights, online with friends.", "switch ps5 xbox pc", "catch battle"),
    ("Cassette Beasts", "Xbox Series X|S, Xbox One, Switch, PC", "Record monsters on cassettes, then turn into them and fuse two together mid-battle. Its sequel, Cassette Beasts 2002, is due in March 2027.", "switch xbox pc", "catch battle story"),
    ("Digimon Story: Time Stranger", "PS5, Xbox Series X|S, PC", "A 2025 Digimon RPG with hundreds of Digimon to raise and digivolve and a time-travel story.", "ps5 xbox pc", "catch battle story"),
    ("Monster Hunter Stories 3: Twisted Reflection", "PS5, Xbox Series X|S, Switch 2, PC", "Collect monster eggs, hatch them and ride them into turn-based fights in the Monster Hunter world.", "switch ps5 xbox pc", "catch battle story"),
    ("Dragon Quest Monsters: The Dark Prince", "Switch, PC, mobile", "Recruit and breed hundreds of Dragon Quest monsters. Its follow-up, The Withered World, lands on 3 December 2026.", "switch pc", "catch battle story"),
    ("Shin Megami Tensei V: Vengeance", "PS5, PS4, Xbox Series X|S, Xbox One, Switch, PC", "Talk demons into joining you and fuse them into stronger ones. A darker, harder take on collecting.", "switch ps5 ps4 xbox pc", "catch battle story"),
    ("Ni no Kuni: Wrath of the White Witch Remastered", "PS4, Xbox One, Switch, PC (plays on PS5, Xbox Series X|S and Switch 2)", "A Studio Ghibli-styled RPG where you raise familiars that fight for you.", "switch ps5 ps4 xbox pc", "catch story"),
    ("Coromon", "Switch, PC, mobile", "A classic Game Boy-style creature collector with puzzles and tougher difficulty options.", "switch pc", "catch battle"),
]
_PK_LABEL = {"catch": "Catching and collecting", "battle": "Turn-based battles", "open": "Open world and crafting", "story": "Story"}
PK_SOON = ["pokemon-winds-and-waves", "cassette-beasts-2002", "honkai-nexus-anima"]
_pk_soon = sorted([g for g in GAMES if g["slug"] in PK_SOON], key=lambda g: (g["month"] or 13, g["date"] or "9999"))
_pk_ww = next((g for g in GAMES if g["slug"] == "pokemon-winds-and-waves"), None)
_pk_cb = next((g for g in GAMES if g["slug"] == "cassette-beasts-2002"), None)
_pk_hk = next((g for g in GAMES if g["slug"] == "honkai-nexus-anima"), None)
_pk_dqm = {"title": "Dragon Quest Monsters: The Withered World", "date": "2026-12-03"}
def _pk_on(tag): return [x[0] for x in LIKE_PK if tag in x[3].split()]
_pk_quick = ("The best games like Pokémon are Temtem, Palworld, Cassette Beasts, Digimon Story: Time Stranger, Monster Hunter Stories 3 and Dragon Quest Monsters, with Temtem and Palworld the picks on PS5 and Xbox. "
             "The next ones are Dragon Quest Monsters: The Withered World (3 December 2026), Cassette Beasts 2002 (March 2027), Honkai: Nexus Anima (spring 2027) and Pokémon Winds and Waves (2027 on Switch 2, no date yet).")
pk_body = (f'<header class="hero"><div class="wrap"><span class="kicker">Games like Pokémon</span>'
           f'<h1>Games like Pokémon:<br><span class="amber">monster tamers now, and the 2027 ones.</span></h1>'
           f'<p class="lead">Creature collectors you can play today on PS5, Xbox, PC and Switch 2, filtered by what you love about Pokémon, plus every monster-taming game coming in 2027.</p>'
           f'<p class="muted" style="margin:0">Last checked {e(UPDATED)} · {len(LIKE_PK)} picks out now · {len(_pk_soon)} coming in 2027</p></div></header>'
           f'<section><div class="wrap"><div class="out" style="margin-bottom:12px"><div class="row"><span><strong>Quick answer:</strong> {e(_pk_quick)}</span></div></div>'
           f'<div class="tool" id="er-tool" style="margin-bottom:24px"><h2 style="font-size:1.5rem;margin-top:0">Which game like Pokémon should I play?</h2>'
           f'<p class="muted">Pick your platform and what you love most. Your choice is remembered on this device.</p>{_like_chips(_PK_LABEL, "What you love")}'
           f'<p class="mono amber" id="er-count" aria-live="polite" style="margin:12px 0 0">{len(LIKE_PK)} games</p></div>'
           f'<div class="sec-head"><h2>What games are like Pokémon?</h2><span class="muted">out now</span></div>'
           f'<div class="out" id="er-list" style="margin-bottom:10px">{_like_rows(LIKE_PK, _PK_LABEL)}</div><p class="empty" id="er-none" hidden>No pick matches both. Try "Anything".</p></div></section>'
           + AD.format("pk-mid") +
           f'<section><div class="wrap"><div class="sec-head"><h2>What monster-taming games are coming out in 2027?</h2><span class="muted">{len(_pk_soon)}</span></div>'
           f'<div class="out" style="margin-bottom:10px">{"".join(_er_srow(g) for g in _pk_soon)}</div>{_like_cd(_pk_dqm)}'
           f'<div class="sec-head" style="margin-top:28px"><h2>When does Pokémon Winds and Waves come out?</h2></div>'
           f'<p>Some time in 2027, only on Switch 2. Nintendo and The Pokémon Company have not given a month or day. These are the Generation 10 games, set on windswept islands and a wide ocean, with Browt, Pombon and Gecqua as the starters. A leaker has claimed late 2027, but that is a rumour, not an announcement. See the <a href="{href("games/pokemon-winds-and-waves.html", 0)}">Pokémon Winds and Waves release date page</a>.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>When does Cassette Beasts 2002 come out?</h2></div>'
           + (f'<p>{e(nice_date(_pk_cb))} on PS5, Xbox Series X|S, Switch 2 and PC, with no exact day yet (Gematsu, RPG Site, VGChartz). Bytten Studio moves the series to Nodnol, a remixed 2000s London, with roughly twice as many monsters as the first game. You still record beasts on tapes, turn into them and fuse two together in battle.</p>' if _pk_cb else '')
           + f'<div class="sec-head" style="margin-top:28px"><h2>What is Honkai: Nexus Anima?</h2></div>'
           + (f'<p>HoYoverse\'s open-world creature-collecting game, due in {e(nice_date(_pk_hk))} on PC and mobile. Console versions have not been confirmed. Like Genshin Impact, it is expected to be free to play.</p>' if _pk_hk else '')
           + f'<div class="sec-head" style="margin-top:28px"><h2>What games are like Pokémon on PS5 and Xbox?</h2></div>'
           f'<p>There are no main Pokémon games on PlayStation or Xbox. PS5: {e(_and(_pk_on("ps5")))}. Xbox: {e(_and(_pk_on("xbox")))}. In 2027, Cassette Beasts 2002 comes to both, and Dragon Quest Monsters: The Withered World arrives on PS5 and Xbox on 3 December 2026.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>What games are like Pokémon on Switch 2?</h2></div>'
           f'<p>{e(_and(_pk_on("switch")))}. Switch 1 games play on Switch 2. In 2027: {e(_and([g["title"] for g in _pk_soon if "Switch 2" in g["platforms"]]))}. See every <a href="{href("platforms/switch-2.html", 0)}">Switch 2 game of 2027</a>.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>What is a game like Pokémon for PC?</h2></div>'
           f'<p>{e(_and(_pk_on("pc")))}. Palworld and Temtem are the most popular online; Coromon and Cassette Beasts are the best single-player picks.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>Related pages and tools</h2></div><ul>'
           f'<li><a href="{href("games/pokemon-winds-and-waves.html", 0)}">Pokémon Winds and Waves release date</a></li>'
           f'<li><a href="{href("games-like-palworld.html", 0)}">Games like Palworld</a>: creature catching with survival and base building</li>'
           f'<li><a href="{href("rpgs-2027.html", 0)}">Every RPG coming in 2027</a>, with a console filter</li>'
           f'<li><a href="{href("games-december-2026.html", 0)}">Games coming out in December 2026</a>: Dragon Quest Monsters first</li>'
           f'<li><a href="{href("games-like-zelda.html", 0)}">Games like Zelda</a> and <a href="{href("games-like-stardew-valley.html", 0)}">games like Stardew Valley</a></li>'
           f'<li><a href="{href("nintendo-direct.html", 0)}">Next Nintendo Direct</a>: where a Winds and Waves date would appear</li></ul></div></section>')
pk_faq = [("What games are like Pokémon?", "Temtem, Palworld, Cassette Beasts, Digimon Story: Time Stranger, Monster Hunter Stories 3, Dragon Quest Monsters: The Dark Prince, Shin Megami Tensei V: Vengeance, Ni no Kuni and Coromon, plus Pokémon Legends: Z-A."),
          ("When does Pokémon Winds and Waves come out?", "In 2027 on Switch 2. No month or exact date has been announced."),
          ("What creature-collecting games come out in 2027?", _and([g['title'] + ' (' + nice_date(g) + ')' for g in _pk_soon]) + "."),
          ("Is there a Pokémon-like game on PS5?", "Yes: Temtem, Palworld, Digimon Story: Time Stranger, Monster Hunter Stories 3 and Shin Megami Tensei V: Vengeance. Cassette Beasts 2002 comes to PS5 in March 2027."),
          ("When does Cassette Beasts 2002 come out?", "March 2027 on PS5, Xbox Series X|S, Switch 2 and PC. No exact day yet.")]
page("games-like-pokemon.html", "Games Like Pokémon: Monster Tamers & 2027 Releases | DayOneDrop",
     "Games like Pokémon on PS5, Xbox, PC and Switch 2: Temtem, Palworld, Cassette Beasts, Digimon, plus 2027's Pokémon Winds and Waves and Cassette Beasts 2002.",
     pk_body, 0, pk_faq, crumbs=[("Home", DOMAIN + "/"), ("2027 games by genre", canon("games-by-genre-2027.html")), ("Games like Pokémon", canon("games-like-pokemon.html"))])


# ---------------- GAMES LIKE MINECRAFT (27 Nov 2026, demand: "games like minecraft", "minecraft alternatives", "sandbox survival games 2027") ----------------
# Evidence: GamesRadar+, PCGamesN, games.gg, Beebom, SVG, ComicBook "Minecraft replacement" lists. Minecraft Switch 2 edition 27 Oct 2026 (Windows Central, Neowin, Thurrott).
# Minecraft movie sequel date from MOVIES (2-source).
LIKE_MC = [
    ("Terraria", "PS4, Xbox One, Switch, PC, mobile (plays on PS5, Xbox Series X|S and Switch 2)", "Minecraft in 2D: dig, build, craft and fight dozens of bosses. Huge, cheap and great with friends.", "switch ps5 ps4 xbox pc", "build survive coop"),
    ("Hytale", "PC", "The block-building game made by former Minecraft server creators, in early access on PC since January 2026.", "pc", "build survive coop"),
    ("Dragon Quest Builders 2", "PS4, Xbox One, Switch, PC (plays on PS5, Xbox Series X|S and Switch 2)", "Block building with a full RPG story and quests. Best if you want Minecraft with a goal.", "switch ps5 ps4 xbox pc", "build story"),
    ("Valheim", "PC, Xbox Series X|S, Xbox One", "Viking survival: build longhouses, sail, and fight bosses with up to 10 friends.", "xbox pc", "build survive coop"),
    ("Core Keeper", "PS5, PS4, Xbox Series X|S, Xbox One, Switch, PC", "Top-down mining, farming and boss fights underground, with up to eight players.", "switch ps5 ps4 xbox pc", "build survive coop"),
    ("LEGO Fortnite Odyssey", "PS5, PS4, Xbox Series X|S, Xbox One, Switch, Switch 2, PC", "Free inside Fortnite: survival building with LEGO pieces and villagers.", "switch ps5 ps4 xbox pc", "build survive coop"),
    ("Roblox", "PS5, PS4, Xbox Series X|S, Xbox One, PC, mobile", "Free, and full of player-made worlds, including lots of Minecraft-style survival and building games.", "ps5 ps4 xbox pc", "build coop"),
    ("Palworld", "PS5, Xbox Series X|S, PC", "Survival crafting where captured creatures build and farm your base for you.", "ps5 xbox pc", "build survive coop"),
    ("No Man's Sky", "PS5, PS4, Xbox Series X|S, Xbox One, Switch, Switch 2, PC", "Build bases on endless planets, then fly off to the next one.", "switch ps5 ps4 xbox pc", "build survive coop"),
    ("Grounded 2", "Xbox Series X|S, PC", "Shrunk to insect size in a park: survive, craft and build with up to four friends. In early access.", "xbox pc", "build survive coop"),
    ("Astroneer", "PS4, Xbox One, Switch, PC (plays on PS5, Xbox Series X|S and Switch 2)", "Reshape whole planets with a terrain tool, build bases and research tech. Calm and friendly.", "switch ps5 ps4 xbox pc", "build coop"),
]
_MC_LABEL = {"build": "Building", "survive": "Survival", "coop": "Play together", "story": "Quests and story"}
MC_SOON = ["outward-2", "tropico-7", "into-the-dead-our-darkest-days", "state-of-decay-3"]
_mc_soon = sorted([g for g in GAMES if g["slug"] in MC_SOON], key=lambda g: (g["month"] or 13, g["date"] or "9999"))
_mc_mov = next((m for m in MOVIES if m[0].startswith("A Minecraft Movie")), None)
_mc_mov_d = nice_date({"date": _mc_mov[1], "window": ""}) if _mc_mov else "2027"
def _mc_on(tag): return [x[0] for x in LIKE_MC if tag in x[3].split()]
_mc_quick = ("The best games like Minecraft are Terraria, Hytale, Dragon Quest Builders 2, Valheim, Core Keeper and LEGO Fortnite Odyssey, with Core Keeper and No Man's Sky on every console. "
             f"In 2027 the survival and building games to watch are {_and([g['title'] + ' (' + nice_date(g) + ')' for g in _mc_soon])}, and {(_mc_mov[0] if _mc_mov else 'the Minecraft movie sequel')} opens on {_mc_mov_d}. No Minecraft 2 has been announced.")
mc_body = (f'<header class="hero"><div class="wrap"><span class="kicker">Games like Minecraft</span>'
           f'<h1>Games like Minecraft:<br><span class="amber">build and survive now, and in 2027.</span></h1>'
           f'<p class="lead">Sandbox, building and survival games to play today on PS5, Xbox, PC and Switch 2, filtered by what you love about Minecraft, plus the 2027 survival games and the Minecraft movie sequel.</p>'
           f'<p class="muted" style="margin:0">Last checked {e(UPDATED)} · {len(LIKE_MC)} picks out now · {len(_mc_soon)} coming in 2027</p></div></header>'
           f'<section><div class="wrap"><div class="out" style="margin-bottom:12px"><div class="row"><span><strong>Quick answer:</strong> {e(_mc_quick)}</span></div></div>'
           f'<div class="tool" id="er-tool" style="margin-bottom:24px"><h2 style="font-size:1.5rem;margin-top:0">Which game like Minecraft should I play?</h2>'
           f'<p class="muted">Pick your platform and what you love most. Your choice is remembered on this device.</p>{_like_chips(_MC_LABEL, "What you love")}'
           f'<p class="mono amber" id="er-count" aria-live="polite" style="margin:12px 0 0">{len(LIKE_MC)} games</p></div>'
           f'<div class="sec-head"><h2>What games are like Minecraft?</h2><span class="muted">out now</span></div>'
           f'<div class="out" id="er-list" style="margin-bottom:10px">{_like_rows(LIKE_MC, _MC_LABEL)}</div><p class="empty" id="er-none" hidden>No pick matches both. Try "Anything".</p></div></section>'
           + AD.format("mc-mid") +
           f'<section><div class="wrap"><div class="sec-head"><h2>What survival and building games come out in 2027?</h2><span class="muted">{len(_mc_soon)}</span></div>'
           f'<div class="out" style="margin-bottom:10px">{"".join(_er_srow(g) for g in _mc_soon)}</div>'
           + (_like_cd({"title": _mc_mov[0], "date": _mc_mov[1]}) if _mc_mov else "") +
           f'<div class="sec-head" style="margin-top:28px"><h2>When does the Minecraft movie 2 come out?</h2></div>'
           + (f'<p>{e(_mc_mov[0])} opens in cinemas on {e(_mc_mov_d)}, from {e(_mc_mov[2])}. {e(_mc_mov[4])} More film dates are on <a href="{href("movies-2027.html", 0)}">upcoming movies 2027</a>.</p>' if _mc_mov else '')
           + f'<div class="sec-head" style="margin-top:28px"><h2>Is there a Minecraft 2?</h2></div>'
           f'<p>No. Mojang has not announced a Minecraft 2. It keeps updating the original with free "game drops" through the year. The closest new game is Hytale, a separate block game in early access on PC.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>Is Minecraft on Switch 2?</h2></div>'
           f'<p>Yes. A native Switch 2 version came out on 27 October 2026 with Vibrant Visuals graphics, and Switch owners can upgrade and keep their worlds (Windows Central, Neowin, Thurrott). Other Minecraft-like games on Switch 2: {e(_and(_mc_on("switch")))}. See every <a href="{href("platforms/switch-2.html", 0)}">Switch 2 game of 2027</a>.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>What games are like Minecraft on PS5 and Xbox?</h2></div>'
           f'<p>PS5: {e(_and(_mc_on("ps5")))}. Xbox: {e(_and(_mc_on("xbox")))}. Valheim and Grounded 2 are on Xbox and PC but not PlayStation.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>What is a free game like Minecraft?</h2></div>'
           f'<p>LEGO Fortnite Odyssey (inside Fortnite) and Roblox are both free to play on PS5, Xbox and PC. Minecraft itself has a free classic version in a browser, but the full game is paid.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>Related pages and tools</h2></div><ul>'
           f'<li><a href="{href("games-like-palworld.html", 0)}">Games like Palworld</a>: survival crafting with creatures</li>'
           f'<li><a href="{href("games-like-stardew-valley.html", 0)}">Games like Stardew Valley</a>: cozy building and farming</li>'
           f'<li><a href="{href("games-like-animal-crossing.html", 0)}">Games like Animal Crossing</a>: cozy island life</li>'
           f'<li><a href="{href("games-like-fortnite.html", 0)}">Games like Fortnite</a>: battle royales and Roblox</li>'
           f'<li><a href="{href("games-like-pokemon.html", 0)}">Games like Pokémon</a>: Palworld and other monster tamers</li>'
           f'<li><a href="{href("games-by-genre-2027.html", 0)}">2027 games by genre</a></li>'
           f'<li><a href="{href("backlog-planner-2027.html", 0)}">2027 backlog planner</a></li></ul></div></section>')
mc_faq = [("What games are like Minecraft?", _and([x[0] for x in LIKE_MC]) + "."),
          ("Is there a Minecraft 2?", "No. Mojang has not announced one; Minecraft keeps getting free updates instead."),
          ("When does the Minecraft movie sequel come out?", (f"{_mc_mov[0]} opens in cinemas on {_mc_mov_d}.") if _mc_mov else "2027."),
          ("What is a free game like Minecraft?", "LEGO Fortnite Odyssey and Roblox, both free on PS5, Xbox and PC."),
          ("What survival games come out in 2027?", _and([g['title'] + ' (' + nice_date(g) + ')' for g in _mc_soon]) + ".")]
page("games-like-minecraft.html", "Games Like Minecraft: Sandbox Picks & 2027 Survival | DayOneDrop",
     "Games like Minecraft on PS5, Xbox, PC and Switch 2: Terraria, Hytale, Valheim, Core Keeper, LEGO Fortnite, plus 2027 survival games and the Minecraft movie 2.",
     mc_body, 0, mc_faq, crumbs=[("Home", DOMAIN + "/"), ("2027 games by genre", canon("games-by-genre-2027.html")), ("Games like Minecraft", canon("games-like-minecraft.html"))])


# ---------------- GAMES LIKE ANIMAL CROSSING (27 Nov 2026, demand: "games like animal crossing", "cozy games switch 2", "games like pokopia") ----------------
# Evidence: GamesRadar+ "games like Animal Crossing", ComicBook, Twinfinite "upcoming games like Animal Crossing", Vice "games like Pokopia", games.gg cozy Switch 2 lists, Epic Store AC-style list.
# Facts: ACNH Switch 2 Edition + free 3.0 update out 15 Jan 2026 (VGC, Nintendo Life, Press Start). Pokopia 5 Mar 2026 Switch 2 (Engadget, GamesRadar+). Tomodachi Life: Living the Dream 16 Apr 2026 (TechRadar, NintendoSoup).
LIKE_AC = [
    ("Pokémon Pokopia", "Switch 2", "The closest thing to a new Animal Crossing: rebuild a world as a Ditto, befriend Pokémon and decorate at your own pace. Out since 5 March 2026.", "switch", "decorate villagers relax"),
    ("Tomodachi Life: Living the Dream", "Switch (plays on Switch 2)", "Make Mii islanders and watch their friendships, fights and romances play out. Out since 16 April 2026.", "switch", "villagers relax"),
    ("Disney Dreamlight Valley", "PS5, PS4, Xbox Series X|S, Xbox One, Switch, PC", "The pick on PlayStation and Xbox: restore a village, decorate your home and befriend Disney and Pixar characters.", "switch ps5 ps4 xbox pc", "decorate villagers relax"),
    ("Hello Kitty Island Adventure", "Switch, PC", "Sanrio friends on a tropical island: crafting, gifts, visits and lots of furniture, with online co-op.", "switch pc", "decorate villagers coop relax"),
    ("Palia", "PS5, Xbox Series X|S, Switch, PC", "Free to play and online: build a home plot, fish, cook and catch bugs next to other players.", "switch ps5 xbox pc", "decorate coop relax"),
    ("Cozy Grove", "PS4, Xbox One, Switch, PC, mobile (plays on PS5, Xbox Series X|S and Switch 2)", "Help ghost bears on a haunted island a little each day, the same short daily rhythm as Animal Crossing.", "switch ps5 ps4 xbox pc", "villagers relax"),
    ("Dinkum", "PC, Switch", "An Australian-outback take on the formula: build a town, invite residents, farm and fish, with friends online.", "switch pc", "decorate villagers coop"),
    ("Fae Farm", "PS5, Xbox Series X|S, Switch, PC", "A magical island to farm, decorate and explore, with up to four players together.", "switch ps5 xbox pc", "decorate coop"),
    ("Ooblets", "Switch, PC, Xbox One (plays on Xbox Series X|S)", "Grow tiny creatures, run a farm and win dance-offs instead of battles. Silly and very relaxed.", "switch xbox pc", "villagers relax"),
    ("Stardew Valley", "PS4, Xbox One, Switch, PC, mobile (plays on PS5, Xbox Series X|S and Switch 2)", "More farming and goals than Animal Crossing, but the same small-town friendships and seasons.", "switch ps5 ps4 xbox pc", "villagers coop"),
]
_AC_LABEL = {"decorate": "Decorating", "villagers": "Villagers and friends", "coop": "Play together", "relax": "No pressure"}
AC_SOON = ["witchbrook", "atelier-karia", "grave-seasons", "kirby-and-the-world-beyond"]
_ac_soon = sorted([g for g in GAMES if g["slug"] in AC_SOON and g["slug"] != "kirby-and-the-world-beyond"], key=lambda g: (g["month"] or 13, g["date"] or "9999"))
_ac_sw = sorted([g for g in GAMES if g["slug"] in AC_SOON and "Switch 2" in g["platforms"]], key=lambda g: (g["month"] or 13, g["date"] or "9999"))
_ac_wb = next((g for g in GAMES if g["slug"] == "witchbrook"), None)
def _ac_on(tag): return [x[0] for x in LIKE_AC if tag in x[3].split()]
_ac_quick = ("The best games like Animal Crossing are Pokémon Pokopia, Tomodachi Life: Living the Dream, Disney Dreamlight Valley, Hello Kitty Island Adventure, Palia and Cozy Grove; on PS5 and Xbox, start with Disney Dreamlight Valley or Palia. "
             f"Nintendo has not announced a new Animal Crossing. The next cozy games are {_and([g['title'] + ' (' + nice_date(g) + ')' for g in _ac_soon])}.")
ac_body = (f'<header class="hero"><div class="wrap"><span class="kicker">Games like Animal Crossing</span>'
           f'<h1>Games like Animal Crossing:<br><span class="amber">cozy island life now, and in 2027.</span></h1>'
           f'<p class="lead">Relaxing life sims to play today on Switch 2, PS5, Xbox and PC, filtered by what you love about Animal Crossing, plus the cozy games dated for 2027.</p>'
           f'<p class="muted" style="margin:0">Last checked {e(UPDATED)} · {len(LIKE_AC)} picks out now · {len(_ac_soon)} coming in 2027</p></div></header>'
           f'<section><div class="wrap"><div class="out" style="margin-bottom:12px"><div class="row"><span><strong>Quick answer:</strong> {e(_ac_quick)}</span></div></div>'
           f'<div class="tool" id="er-tool" style="margin-bottom:24px"><h2 style="font-size:1.5rem;margin-top:0">Which game like Animal Crossing should I play?</h2>'
           f'<p class="muted">Pick your platform and what you love most. Your choice is remembered on this device.</p>{_like_chips(_AC_LABEL, "What you love")}'
           f'<p class="mono amber" id="er-count" aria-live="polite" style="margin:12px 0 0">{len(LIKE_AC)} games</p></div>'
           f'<div class="sec-head"><h2>What games are like Animal Crossing?</h2><span class="muted">out now</span></div>'
           f'<div class="out" id="er-list" style="margin-bottom:10px">{_like_rows(LIKE_AC, _AC_LABEL)}</div><p class="empty" id="er-none" hidden>No pick matches both. Try "Anything".</p></div></section>'
           + AD.format("ac-mid") +
           f'<section><div class="wrap"><div class="sec-head"><h2>What cozy games come out in 2027?</h2><span class="muted">{len(_ac_soon)}</span></div>'
           f'<div class="out" style="margin-bottom:10px">{"".join(_er_srow(g) for g in _ac_soon)}</div>{_like_cd(_ac_wb)}'
           f'<div class="sec-head" style="margin-top:28px"><h2>Is there a new Animal Crossing coming?</h2></div>'
           f'<p>Not officially. Nintendo has not announced a new Animal Crossing game. Instead, New Horizons got a Nintendo Switch 2 Edition and a free 3.0 update on 15 January 2026, with sharper visuals, a new resort hotel to decorate and bigger island-building options (VGC, Nintendo Life). Any reveal would most likely come in a <a href="{href("nintendo-direct.html", 0)}">Nintendo Direct</a>.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>What cozy games are coming to Switch 2 in 2027?</h2></div>'
           f'<p>{e(_and([g["title"] + " (" + nice_date(g) + ")" for g in _ac_sw]))}. Kirby is a gentle platformer rather than a life sim, but it is the calmest big Nintendo game dated so far. See every <a href="{href("platforms/switch-2.html", 0)}">Switch 2 game of 2027</a>.</p>'
           + (f'<div class="sec-head" style="margin-top:28px"><h2>When does Witchbrook come out?</h2></div>'
              f'<p>{e(nice_date(_ac_wb))} on {e(_and(_ac_wb["platforms"]))}. It is a life sim about studying magic at a college in a seaside town, with friendships and town life at its heart. Full details: <a href="{href("games/witchbrook.html", 0) if _ac_wb.get("page") else href("games-like-stardew-valley.html", 0)}">Witchbrook</a>.</p>' if _ac_wb else '')
           + f'<div class="sec-head" style="margin-top:28px"><h2>What games are like Animal Crossing on PS5 and Xbox?</h2></div>'
           f'<p>Animal Crossing is only on Nintendo consoles. PS5: {e(_and(_ac_on("ps5")))}. Xbox: {e(_and(_ac_on("xbox")))}. In 2027, Witchbrook, Atelier Karia and Grave Seasons all come to PS5 and Xbox.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>What is a free game like Animal Crossing?</h2></div>'
           f'<p>Palia is free to play on PS5, Xbox, Switch and PC. Everything else on this list is paid, though Cozy Grove and Stardew Valley often drop below $10 in sales: see <a href="{href("steam-sale-dates.html", 0)}">Steam sale dates</a>.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>Related pages and tools</h2></div><ul>'
           f'<li><a href="{href("games-like-stardew-valley.html", 0)}">Games like Stardew Valley</a>: farming sims now and in 2027</li>'
           f'<li><a href="{href("games-like-pokemon.html", 0)}">Games like Pokémon</a>: monster tamers, including Pokémon Winds and Waves</li>'
           f'<li><a href="{href("games-like-minecraft.html", 0)}">Games like Minecraft</a>: building and survival</li>'
           f'<li><a href="{href("backlog-planner-2027.html", 0)}">2027 backlog planner</a></li></ul></div></section>')
ac_faq = [("What games are like Animal Crossing?", _and([x[0] for x in LIKE_AC]) + "."),
          ("Is there a new Animal Crossing game coming?", "Nintendo has not announced one. New Horizons got a Switch 2 Edition and a free 3.0 update on 15 January 2026."),
          ("What is the best game like Animal Crossing on PS5?", "Disney Dreamlight Valley, then Palia (free) and Fae Farm. Witchbrook arrives on PS5 on 28 January 2027."),
          ("Is Pokémon Pokopia like Animal Crossing?", "Yes. It is a Switch 2 life sim, out since 5 March 2026, where you rebuild a world, befriend Pokémon and decorate at your own pace."),
          ("What cozy games come out in 2027?", _and([g['title'] + ' (' + nice_date(g) + ')' for g in _ac_soon]) + ".")]
page("games-like-animal-crossing.html", "Games Like Animal Crossing: Cozy Picks & 2027 Sims | DayOneDrop",
     "Games like Animal Crossing on Switch 2, PS5, Xbox and PC: Pokopia, Tomodachi Life, Disney Dreamlight Valley, Palia, plus 2027 cozy games like Witchbrook.",
     ac_body, 0, ac_faq, crumbs=[("Home", DOMAIN + "/"), ("2027 games by genre", canon("games-by-genre-2027.html")), ("Games like Animal Crossing", canon("games-like-animal-crossing.html"))])


# ---------------- GAMES LIKE FORTNITE (27 Nov 2026, demand: "games like fortnite", "free games like fortnite", DEMAND N41) ----------------
# Evidence: GamesRadar+ US/UK/AU "games like Fortnite", GameSpot, Pocket Tactics, Pocket Gamer, GGRecon, VideoGamer, Digital Trends, Eneba, ExitLag 2026 guide, Escapist/G2A battle royale lists.
LIKE_FN = [
    ("Apex Legends", "PS5, PS4, Xbox Series X|S, Xbox One, Switch, PC", "Free squad battle royale with hero abilities, fast movement and great gunplay. The closest match for Fortnite's competitive side.", "switch ps5 ps4 xbox pc", "br squad"),
    ("Call of Duty: Warzone", "PS5, PS4, Xbox Series X|S, Xbox One, PC", "Free, big-map battle royale with realistic guns, loadout drops and the Gulag second chance.", "ps5 ps4 xbox pc", "br squad"),
    ("Battlefield 6: REDSEC", "PS5, Xbox Series X|S, PC", "Battlefield's free battle royale (October 2025): squads, vehicles and buildings you can blow apart.", "ps5 xbox pc", "br squad"),
    ("PUBG: Battlegrounds", "PS5, PS4, Xbox Series X|S, Xbox One, PC", "The game that made battle royale big. Free to play since 2022, slower and more tactical than Fortnite.", "ps5 ps4 xbox pc", "br"),
    ("Fall Guys", "PS5, PS4, Xbox Series X|S, Xbox One, Switch, PC", "Free party battle royale from Epic: up to 60 jelly-bean players race through obstacle rounds. No guns at all.", "switch ps5 ps4 xbox pc", "br party"),
    ("Super Animal Royale", "PS5, PS4, Xbox Series X|S, Xbox One, Switch, PC", "Free top-down battle royale with 64 cartoon animals. Bright and silly like Fortnite, but in 2D.", "switch ps5 ps4 xbox pc", "br party"),
    ("Marvel Rivals", "PS5, Xbox Series X|S, PC", "Free 6v6 hero shooter with Marvel characters and destructible maps. Colourful and team-based.", "ps5 xbox pc", "squad"),
    ("Overwatch 2", "PS5, PS4, Xbox Series X|S, Xbox One, Switch, PC", "Free 5v5 hero shooter from Blizzard. Bright cartoon style and short rounds.", "switch ps5 ps4 xbox pc", "squad"),
    ("Splatoon 3", "Switch (plays on Switch 2)", "Nintendo's paint shooter: cover the map in ink in 4v4 Turf War. The most kid-friendly shooter here.", "switch", "squad party"),
    ("Roblox", "PS5, PS4, Xbox Series X|S, Xbox One, PC, mobile", "Free and full of player-made games, close to Fortnite's Creative and UEFN islands.", "ps5 ps4 xbox pc", "build party"),
    ("Minecraft", "PS5, PS4, Xbox Series X|S, Xbox One, Switch, Switch 2, PC", "For the building side of Fortnite: build anything, alone or on servers with friends.", "switch ps5 ps4 xbox pc", "build"),
    ("Rocket League", "PS4, Xbox One, Switch, PC (plays on PS5 and Xbox Series X|S)", "Free car football from Epic, with the same item shop and seasons style as Fortnite.", "switch ps5 ps4 xbox pc", "party"),
]
_FN_LABEL = {"br": "Battle royale", "squad": "Team shooter", "build": "Building and creating", "party": "Casual and party"}
FN_SOON = ["the-duskbloods", "golf-with-your-friends-2", "super-battle-golf"]
_fn_soon = sorted([g for g in GAMES if g["slug"] in FN_SOON], key=lambda g: (g["month"] or 13, g["date"] or "9999"))
_fn_cdg = next((g for g in _fn_soon if g.get("date")), None)
def _fn_on(tag): return [x[0] for x in LIKE_FN if tag in x[3].split()]
_fn_free = [x[0] for x in LIKE_FN if x[0] not in ("Splatoon 3", "Minecraft")]
_fn_quick = ("The best games like Fortnite are Apex Legends, Call of Duty: Warzone, Battlefield 6: REDSEC and PUBG: Battlegrounds for battle royale, Fall Guys for party fun, Marvel Rivals and Overwatch 2 for team shooting, and Roblox or Minecraft for building. "
             f"All except Splatoon 3 and Minecraft are free. The multiplayer games coming in 2027 are {_and([g['title'] + ' (' + nice_date(g) + ')' for g in _fn_soon])}.")
fn_body = (f'<header class="hero"><div class="wrap"><span class="kicker">Games like Fortnite</span>'
           f'<h1>Games like Fortnite:<br><span class="amber">free battle royales, shooters and builders.</span></h1>'
           f'<p class="lead">The best alternatives to Fortnite on PS5, Xbox, Switch 2 and PC, filtered by the part of Fortnite you love, plus the multiplayer games coming in 2027.</p>'
           f'<p class="muted" style="margin:0">Last checked {e(UPDATED)} · {len(LIKE_FN)} picks out now · {len(_fn_free)} free to play</p></div></header>'
           f'<section><div class="wrap"><div class="out" style="margin-bottom:12px"><div class="row"><span><strong>Quick answer:</strong> {e(_fn_quick)}</span></div></div>'
           f'<div class="tool" id="er-tool" style="margin-bottom:24px"><h2 style="font-size:1.5rem;margin-top:0">Which game like Fortnite should I play?</h2>'
           f'<p class="muted">Pick your platform and what you love most about Fortnite. Your choice is remembered on this device.</p>{_like_chips(_FN_LABEL, "What you love")}'
           f'<p class="mono amber" id="er-count" aria-live="polite" style="margin:12px 0 0">{len(LIKE_FN)} games</p></div>'
           f'<div class="sec-head"><h2>What games are like Fortnite?</h2><span class="muted">out now</span></div>'
           f'<div class="out" id="er-list" style="margin-bottom:10px">{_like_rows(LIKE_FN, _FN_LABEL)}</div><p class="empty" id="er-none" hidden>No pick matches both. Try "Anything".</p></div></section>'
           + AD.format("fn-mid") +
           f'<section><div class="wrap"><div class="sec-head"><h2>What multiplayer games come out in 2027?</h2><span class="muted">{len(_fn_soon)}</span></div>'
           f'<div class="out" style="margin-bottom:10px">{"".join(_er_srow(g) for g in _fn_soon)}</div>{_like_cd(_fn_cdg)}'
           f'<p class="muted">No new battle royale has a confirmed 2027 date yet. We add them to the <a href="{href("calendar.html", 0)}">2027 release calendar</a> as soon as a publisher gives one.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>What is a free game like Fortnite?</h2></div>'
           f'<p>{e(_and(_fn_free))} are all free to play. Apex Legends is the best free pick if you want the same squad battle royale; Fall Guys (also made by Epic) is the best free pick for younger players because it has no guns.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>What games are like Fortnite on Switch 2?</h2></div>'
           f'<p>Fortnite itself is free on Switch 2. Other picks that play on Switch 2: {e(_and(_fn_on("switch")))}. Warzone, REDSEC, PUBG and Marvel Rivals are not on Nintendo consoles. In 2027, FromSoftware\'s 8-player online game The Duskbloods is a Switch 2 exclusive. See every <a href="{href("platforms/switch-2.html", 0)}">Switch 2 game of 2027</a>.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>What games are like Fortnite on PS5 and Xbox?</h2></div>'
           f'<p>PS5: {e(_and(_fn_on("ps5")))}. Xbox: {e(_and(_fn_on("xbox")))}. For battle royale specifically, start with Apex Legends, Warzone or Battlefield 6: REDSEC.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>What game is like Fortnite with building?</h2></div>'
           f'<p>No other big battle royale has Fortnite-style building in fights. For building outside combat, Roblox and Minecraft are the closest, and LEGO Fortnite sits inside Fortnite itself. More building and survival picks: <a href="{href("games-like-minecraft.html", 0)}">games like Minecraft</a>.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>What game is like Fortnite for kids?</h2></div>'
           f'<p>Fall Guys, Splatoon 3, Super Animal Royale, Rocket League and Minecraft are the gentlest picks here: bright, cartoon style and little or no realistic violence. Check each game\'s age rating and chat settings first.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>Related pages and tools</h2></div><ul>'
           f'<li><a href="{href("games-like-minecraft.html", 0)}">Games like Minecraft</a>: building and survival</li>'
           f'<li><a href="{href("games-like-gta-6.html", 0)}">Games like GTA 6</a>: open-world crime and driving</li>'
           f'<li><a href="{href("epic-free-games.html", 0)}">Epic free games this week</a>: the free PC game in the Epic store right now</li>'
           f'<li><a href="{href("countdown.html", 0)}">Game release countdown</a> for every dated 2027 game</li></ul></div></section>')
fn_faq = [("What games are like Fortnite?", _and([x[0] for x in LIKE_FN]) + "."),
          ("What is the best free game like Fortnite?", "Apex Legends for squad battle royale, Fall Guys for party fun with no guns, and Marvel Rivals for a colourful team shooter. All three are free."),
          ("Is there a battle royale like Fortnite on Switch 2?", "Apex Legends, Fall Guys and Super Animal Royale all play on Switch 2, and Fortnite itself is free there."),
          ("What game is like Fortnite but with building?", "No other big battle royale has Fortnite-style building in fights. Roblox and Minecraft are the closest building games."),
          ("What multiplayer games come out in 2027?", _and([g['title'] + ' (' + nice_date(g) + ')' for g in _fn_soon]) + ".")]
page("games-like-fortnite.html", "Games Like Fortnite: Free Battle Royales & More (2027)",
     "Games like Fortnite on PS5, Xbox, Switch 2 and PC: Apex Legends, Warzone, REDSEC, Fall Guys, Marvel Rivals and Roblox, most free, plus 2027 multiplayer games.",
     fn_body, 0, fn_faq, crumbs=[("Home", DOMAIN + "/"), ("2027 games by genre", canon("games-by-genre-2027.html")), ("Games like Fortnite", canon("games-like-fortnite.html"))])


# ---------------- GAMES LIKE BALDUR'S GATE 3 (27 Nov 2026, demand: "games like baldur's gate 3", "upcoming crpg 2027", "larian divinity release date", DEMAND N41) ----------------
# Evidence: PC Gamer "11 upcoming RPGs that might pull me away from BG3", ComicBook "4 upcoming CRPGs that could rival BG3", TurnBasedLovers "upcoming isometric turn-based RPGs 2027", Eneba list.
# Facts: Larian revealed Divinity at The Game Awards 2025 (PC Gamer, GamesRadar+, Kotaku); Larian confirmed it is turn-based (Game Informer 16 Dec 2025); no date or platforms (PC Gamer, PCGamesN guides).
LIKE_BG = [
    ("Divinity: Original Sin 2", "PC, PS4, Xbox One, Switch (plays on PS5, Xbox Series X|S and Switch 2)", "Larian's game before BG3: the same turn-based combat with elements, wild freedom and four-player co-op.", "switch ps5 ps4 xbox pc", "turn story coop"),
    ("Warhammer 40,000: Rogue Trader", "PC, PS5, Xbox Series X|S", "Owlcat's turn-based CRPG: run a starship dynasty, pick companions and make huge choices. Dark Heresy is its 2027 follow-up.", "ps5 xbox pc", "turn story romance"),
    ("Pathfinder: Wrath of the Righteous", "PC, PS4, Xbox One (plays on PS5 and Xbox Series X|S)", "A giant tabletop-rules RPG with real-time or turn-based combat, mythic paths and many romances.", "ps5 ps4 xbox pc", "turn story romance"),
    ("Clair Obscur: Expedition 33", "PS5, Xbox Series X|S, PC", "Turn-based combat with timed dodges and parries, and a story that hits as hard as BG3's. Game of the Year at The Game Awards 2025.", "ps5 xbox pc", "turn story"),
    ("Pillars of Eternity II: Deadfire", "PC, PS4, Xbox One (plays on PS5 and Xbox Series X|S)", "Obsidian's pirate CRPG with a turn-based mode, a big crew and a sea to explore.", "ps5 ps4 xbox pc", "turn story romance"),
    ("Baldur's Gate and Baldur's Gate II: Enhanced Editions", "PC, PS4, Xbox One, Switch (plays on PS5, Xbox Series X|S and Switch 2)", "The classics BG3 follows: the same Forgotten Realms, real-time with pause, and the original Minsc and Jaheira.", "switch ps5 ps4 xbox pc", "story romance coop"),
    ("Disco Elysium: The Final Cut", "PC, PS4, PS5, Xbox One, Xbox Series X|S, Switch", "No combat at all, but the best dialogue and skill checks in any RPG. For players who loved BG3's conversations.", "switch ps5 ps4 xbox pc", "story"),
    ("Dragon Age: The Veilguard", "PS5, Xbox Series X|S, PC", "Real-time action instead of turns, but a full companion party and romances in BioWare style.", "ps5 xbox pc", "romance"),
    ("Mass Effect Legendary Edition", "PS4, Xbox One, PC (plays on PS5 and Xbox Series X|S)", "The trilogy with the most famous companions and romances in RPGs, in a sci-fi shooter shell.", "ps5 ps4 xbox pc", "story romance"),
    ("Divinity: Original Sin Enhanced Edition", "PC, PS4, Xbox One, Switch (plays on PS5, Xbox Series X|S and Switch 2)", "Larian's first big turn-based hit, built for two-player co-op from the start.", "switch ps5 ps4 xbox pc", "turn coop"),
]
_BG_LABEL = {"turn": "Turn-based combat", "story": "Choices that matter", "romance": "Companions and romance", "coop": "Co-op"}
BG_SOON = ["warhammer-40-000-dark-heresy", "shadow-of-the-road", "exodus", "fable"]
_bg_soon = sorted([g for g in GAMES if g["slug"] in BG_SOON], key=lambda g: (g["month"] or 13, g["date"] or "9999"))
_bg_dh = next((g for g in GAMES if g["slug"] == "warhammer-40-000-dark-heresy"), None)
def _bg_on(tag): return [x[0] for x in LIKE_BG if tag in x[3].split()]
_bg_quick = ("The best games like Baldur's Gate 3 are Divinity: Original Sin 2, Warhammer 40,000: Rogue Trader, Pathfinder: Wrath of the Righteous, Clair Obscur: Expedition 33 and Pillars of Eternity II. "
             f"The next ones are {_and([g['title'] + ' (' + nice_date(g) + ')' for g in _bg_soon])}. Larian's own next game, Divinity, has no release date.")
bg_body = (f'<header class="hero"><div class="wrap"><span class="kicker">Games like Baldur\'s Gate 3</span>'
           f'<h1>Games like Baldur\'s Gate 3:<br><span class="amber">party RPGs now, and the 2027 ones.</span></h1>'
           f'<p class="lead">Turn-based CRPGs and story RPGs to play today on PS5, Xbox, Switch 2 and PC, filtered by what you loved about BG3, plus every similar RPG dated for 2027.</p>'
           f'<p class="muted" style="margin:0">Last checked {e(UPDATED)} · {len(LIKE_BG)} picks out now · {len(_bg_soon)} coming in 2027</p></div></header>'
           f'<section><div class="wrap"><div class="out" style="margin-bottom:12px"><div class="row"><span><strong>Quick answer:</strong> {e(_bg_quick)}</span></div></div>'
           f'<div class="tool" id="er-tool" style="margin-bottom:24px"><h2 style="font-size:1.5rem;margin-top:0">Which game like Baldur\'s Gate 3 should I play?</h2>'
           f'<p class="muted">Pick your platform and what you loved most. Your choice is remembered on this device.</p>{_like_chips(_BG_LABEL, "What you loved")}'
           f'<p class="mono amber" id="er-count" aria-live="polite" style="margin:12px 0 0">{len(LIKE_BG)} games</p></div>'
           f'<div class="sec-head"><h2>What games are like Baldur\'s Gate 3?</h2><span class="muted">out now</span></div>'
           f'<div class="out" id="er-list" style="margin-bottom:10px">{_like_rows(LIKE_BG, _BG_LABEL)}</div><p class="empty" id="er-none" hidden>No pick matches both. Try "Anything".</p></div></section>'
           + AD.format("bg-mid") +
           f'<section><div class="wrap"><div class="sec-head"><h2>What RPGs like Baldur\'s Gate 3 come out in 2027?</h2><span class="muted">{len(_bg_soon)}</span></div>'
           f'<div class="out" style="margin-bottom:10px">{"".join(_er_srow(g) for g in _bg_soon)}</div>{_like_cd(_bg_dh)}'
           f'<p class="muted">Dark Heresy is the closest match: a party-based, turn-based CRPG from Owlcat, the Rogue Trader studio. Shadow of the Road is turn-based tactics (also published by Owlcat); Exodus and Fable are story RPGs with real-time combat.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>When does Larian\'s Divinity come out?</h2></div>'
           f'<p>No release date yet. Larian revealed Divinity at The Game Awards 2025 and calls it its biggest game ever, larger than Baldur\'s Gate 3 (PC Gamer, GamesRadar+). Larian has confirmed it is turn-based (Game Informer), but has not named platforms or a year. We add it to the board the day it gets a date; the most likely place for news is <a href="{href("game-awards-2026.html", 0)}">The Game Awards 2026</a> or a Larian showcase.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>Will there be a Baldur\'s Gate 4?</h2></div>'
           f'<p>Larian has said it is not making Baldur\'s Gate 4 and has moved on to Divinity. The Baldur\'s Gate name belongs to Wizards of the Coast, so another studio could make one in the future, but none is announced.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>What games are like Baldur\'s Gate 3 on PS5 and Xbox?</h2></div>'
           f'<p>PS5: {e(_and(_bg_on("ps5")))}. Xbox: {e(_and(_bg_on("xbox")))}. In 2027, Dark Heresy comes to PS5, Xbox Series X|S and PC on {e(nice_date(_bg_dh)) if _bg_dh else "its release date"}.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>What games are like Baldur\'s Gate 3 on Switch 2?</h2></div>'
           f'<p>Baldur\'s Gate 3 is not on Switch or Switch 2. Picks that play there: {e(_and(_bg_on("switch")))}. For turn-based RPGs coming to Switch 2 in 2027, see <a href="{href("rpgs-2027.html", 0)}">every RPG of 2027</a>.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>What games are like Baldur\'s Gate 3 with co-op?</h2></div>'
           f'<p>Divinity: Original Sin 2 (up to four players) and Divinity: Original Sin Enhanced Edition (two players) are the best, because Larian built them the same way. The Baldur\'s Gate Enhanced Editions also have online multiplayer.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>Related pages and tools</h2></div><ul>'
           f'<li><a href="{href("rpgs-2027.html", 0)}">Every RPG coming in 2027</a>, with action RPG and JRPG filters</li>'
           f'<li><a href="{href("games-like-elden-ring.html", 0)}">Games like Elden Ring</a>: soulslikes now and in 2027</li>'
           f'<li><a href="{href("games-like-skyrim.html", 0)}">Games like Skyrim</a>: open-world RPGs and the Elder Scrolls 6 news</li>'
           f'<li><a href="{href("games-like-zelda.html", 0)}">Games like Zelda</a>: fantasy adventures</li>'
           f'<li><a href="{href("backlog-planner-2027.html", 0)}">2027 backlog planner</a>: fit long RPGs around the new releases</li></ul></div></section>')
bg_faq = [("What games are like Baldur's Gate 3?", _and([x[0] for x in LIKE_BG]) + "."),
          ("What is the closest game to Baldur's Gate 3?", "Divinity: Original Sin 2, made by Larian before BG3, with the same turn-based combat and co-op. Warhammer 40,000: Rogue Trader is the closest from another studio."),
          ("When does Larian's Divinity come out?", "Larian has not given a release date or platforms. It was revealed at The Game Awards 2025 and is turn-based."),
          ("Will there be a Baldur's Gate 4?", "Larian says it is not making one. No other studio has announced Baldur's Gate 4."),
          ("What CRPGs come out in 2027?", _and([g['title'] + ' (' + nice_date(g) + ')' for g in _bg_soon]) + ".")]
page("games-like-baldurs-gate-3.html", "Games Like Baldur's Gate 3: CRPG Picks & 2027 RPGs",
     "Games like Baldur's Gate 3 on PS5, Xbox, Switch 2 and PC: Divinity: Original Sin 2, Rogue Trader, Pathfinder, Expedition 33, plus 2027 CRPGs and Divinity.",
     bg_body, 0, bg_faq, crumbs=[("Home", DOMAIN + "/"), ("Every RPG of 2027", canon("rpgs-2027.html")), ("Games like Baldur's Gate 3", canon("games-like-baldurs-gate-3.html"))])


# ---------------- GAMES LIKE PALWORLD (27 Nov 2026, demand: "games like palworld", DEMAND N41/N45) ----------------
# Evidence: GamesRadar+ "10 games like Palworld", ComicBook "best games like Palworld", Gfinity, Player.One "10 survival crafting games like Palworld 2026", PC Gamer Next Fest Palworld-likes.
# Facts: Palworld 1.0 set for 10 July 2026 on Steam, PS5, Xbox Series X|S and Game Pass, free for existing owners (TechTimes 1 Jul 2026, Insider Gaming).
LIKE_PW = [
    ("Craftopia", "PC, Xbox Series X|S, Xbox One", "Pocketpair's game before Palworld: survival crafting, automation and capturing creatures in one sandbox.", "xbox pc", "creature craft coop"),
    ("ARK: Survival Ascended", "PS5, Xbox Series X|S, PC", "Tame dinosaurs, ride them, build a base and survive. The game Palworld is most often compared to.", "ps5 xbox pc", "creature craft survive coop"),
    ("Temtem", "PS5, Xbox Series X|S, Switch, PC", "A Pokémon-style creature MMO with harder two-on-two battles and online co-op.", "switch ps5 xbox pc", "creature coop"),
    ("Cassette Beasts", "PC, Switch, Xbox Series X|S, Xbox One", "Record monsters onto tapes and fuse them in battle. Its sequel, Cassette Beasts 2002, is due in 2027.", "switch xbox pc", "creature coop"),
    ("Pokémon Legends: Z-A", "Switch 2, Switch", "Pokémon with real-time battles in a city you explore freely. The closest Nintendo gets to Palworld's open catching.", "switch", "creature"),
    ("Pokémon Scarlet and Violet", "Switch (plays on Switch 2)", "Open-world Pokémon with four-player online exploring.", "switch", "creature coop"),
    ("Valheim", "PC, Xbox Series X|S", "Viking survival crafting for up to ten friends: build, sail and fight bosses. No creature catching, but the same base-building loop.", "xbox pc", "craft survive coop"),
    ("Enshrouded", "PC", "Voxel building and action-RPG combat in a fog-covered world, with up to 16 players.", "pc", "craft survive coop"),
    ("Slime Rancher 2", "PC, Xbox Series X|S", "Catch and farm cute slimes on an alien island. Palworld's ranch side, without the guns.", "xbox pc", "creature craft"),
    ("Monster Hunter Stories 2: Wings of Ruin", "Switch, PS4, PC (plays on Switch 2 and PS5)", "Steal monster eggs, hatch them and ride them in turn-based battles.", "switch ps4 ps5 pc", "creature"),
]
_PW_LABEL = {"creature": "Catching creatures", "craft": "Building and crafting", "survive": "Survival", "coop": "Co-op"}
PW_SOON = ["cassette-beasts-2002", "honkai-nexus-anima", "pokemon-winds-and-waves", "outward-2", "state-of-decay-3", "into-the-dead-our-darkest-days"]
_pw_soon = sorted([g for g in GAMES if g["slug"] in PW_SOON], key=lambda g: (g["month"] or 13, g["date"] or "9999"))
_pw_dated = next((g for g in _pw_soon if g.get("date")), None)
def _pw_on(tag): return [x[0] for x in LIKE_PW if tag in x[3].split()]
_pw_cre = [g["title"] + " (" + nice_date(g) + ")" for g in _pw_soon if "reature" in g["genre"] or g["slug"] == "pokemon-winds-and-waves"]
_pw_quick = ("The best games like Palworld are ARK: Survival Ascended, Craftopia, Temtem, Cassette Beasts and Pokémon Legends: Z-A, plus Valheim and Enshrouded if you mostly loved the base building. "
             f"The next creature collectors are {_and(_pw_cre)}." if _pw_cre else "The best games like Palworld are ARK: Survival Ascended, Craftopia, Temtem and Cassette Beasts.")
pw_body = (f'<header class="hero"><div class="wrap"><span class="kicker">Games like Palworld</span>'
           f'<h1>Games like Palworld:<br><span class="amber">creature survival now, and the 2027 ones.</span></h1>'
           f'<p class="lead">Monster catching, base building and survival games to play today on PS5, Xbox, Switch 2 and PC, filtered by what you loved about Palworld, plus every similar game dated for 2027.</p>'
           f'<p class="muted" style="margin:0">Last checked {e(UPDATED)} · {len(LIKE_PW)} picks out now · {len(_pw_soon)} coming in 2027</p></div></header>'
           f'<section><div class="wrap"><div class="out" style="margin-bottom:12px"><div class="row"><span><strong>Quick answer:</strong> {e(_pw_quick)}</span></div></div>'
           f'<div class="tool" id="er-tool" style="margin-bottom:24px"><h2 style="font-size:1.5rem;margin-top:0">Which game like Palworld should I play?</h2>'
           f'<p class="muted">Pick your platform and what you loved most. Your choice is remembered on this device.</p>{_like_chips(_PW_LABEL, "What you loved")}'
           f'<p class="mono amber" id="er-count" aria-live="polite" style="margin:12px 0 0">{len(LIKE_PW)} games</p></div>'
           f'<div class="sec-head"><h2>What games are like Palworld?</h2><span class="muted">out now</span></div>'
           f'<div class="out" id="er-list" style="margin-bottom:10px">{_like_rows(LIKE_PW, _PW_LABEL)}</div><p class="empty" id="er-none" hidden>No pick matches both. Try "Anything".</p></div></section>'
           + AD.format("pw-mid") +
           f'<section><div class="wrap"><div class="sec-head"><h2>What games like Palworld come out in 2027?</h2><span class="muted">{len(_pw_soon)}</span></div>'
           f'<div class="out" style="margin-bottom:10px">{"".join(_er_srow(g) for g in _pw_soon)}</div>{_like_cd(_pw_dated)}'
           f'<p class="muted">Cassette Beasts 2002, Honkai: Nexus Anima and Pokémon Winds and Waves are the creature collectors. Outward 2, State of Decay 3 and Into the Dead: Our Darkest Days are survival games without monster catching.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>Is Palworld out of early access?</h2></div>'
           f'<p>Pocketpair set Palworld\'s 1.0 full release for 10 July 2026 on Steam, PS5, Xbox Series X|S and Game Pass, as a free update for people who already owned it, after about two and a half years in early access (TechTimes, Insider Gaming). So if you are looking for "the next Palworld", the full version is the place to start again.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>Is Palworld on Switch 2?</h2></div>'
           f'<p>Palworld has not been announced for Switch or Switch 2. On Nintendo consoles the closest picks are {e(_and(_pw_on("switch")))}. In 2027, Pokémon Winds and Waves is a Switch 2 exclusive and Cassette Beasts 2002 also comes to Switch 2.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>What games are like Palworld on PS5 and Xbox?</h2></div>'
           f'<p>PS5: {e(_and(_pw_on("ps5")))}. Xbox: {e(_and(_pw_on("xbox")))}. Palworld itself is on Xbox Game Pass; see <a href="{href("game-pass-2027.html", 0)}">every 2027 game on Game Pass</a> for what joins next.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>What are games like Palworld with co-op?</h2></div>'
           f'<p>{e(_and([x[0] for x in LIKE_PW if "coop" in x[4].split()]))} all let you play with friends.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>Related pages and tools</h2></div><ul>'
           f'<li><a href="{href("games-like-pokemon.html", 0)}">Games like Pokémon</a>: turn-based monster tamers now and in 2027</li>'
           f'<li><a href="{href("games-like-minecraft.html", 0)}">Games like Minecraft</a>: building and survival</li>'
           f'<li><a href="{href("games-like-fortnite.html", 0)}">Games like Fortnite</a>: more games to play with friends</li>'
           f'<li><a href="{href("backlog-planner-2027.html", 0)}">2027 backlog planner</a>: fit long survival games around new releases</li></ul></div></section>')
pw_faq = [("What games are like Palworld?", _and([x[0] for x in LIKE_PW]) + "."),
          ("What is the closest game to Palworld?", "ARK: Survival Ascended for taming and survival, and Craftopia, made by Palworld's studio Pocketpair before Palworld."),
          ("Is Palworld out of early access?", "Pocketpair set the 1.0 full release for 10 July 2026 on Steam, PS5, Xbox Series X|S and Game Pass, free for existing owners."),
          ("Is Palworld coming to Switch 2?", "Not announced. Pokémon Legends: Z-A, Temtem and Cassette Beasts are the closest picks on Switch 2."),
          ("What creature collecting games come out in 2027?", _and([g['title'] + ' (' + nice_date(g) + ')' for g in _pw_soon if g["slug"] in ("cassette-beasts-2002", "honkai-nexus-anima", "pokemon-winds-and-waves")]) + ".")]
page("games-like-palworld.html", "Games Like Palworld: 10 Picks & 2027 Creature Games",
     "Games like Palworld on PS5, Xbox, Switch 2 and PC: ARK, Craftopia, Temtem, Cassette Beasts, Pokémon Legends: Z-A, plus the 2027 creature and survival games.",
     pw_body, 0, pw_faq, crumbs=[("Home", DOMAIN + "/"), ("2027 games by genre", canon("games-by-genre-2027.html")), ("Games like Palworld", canon("games-like-palworld.html"))])


# ---------------- GAMES LIKE SKYRIM (27 Nov 2026, demand: "games like skyrim", "elder scrolls 6 release date", DEMAND N45) ----------------
# Evidence: GamesRadar+ "best games like Skyrim 2026", VGTimes "38 best games like Skyrim 2026", Plarium, gaming.net; TES6 news (GamesRadar+, ScreenRant 4 Nov 2026, GameRant 1 Nov 2026).
# Facts: TES6 has no date or platforms from Bethesda; The Verge reported the title Sentinel (via GameRant); Jason Schreier said "more than 2 years away" (via ScreenRant).
# Skyrim Anniversary Edition on Switch 2 10 Dec 2025 (Gematsu, RPG Site). Avowed on PS5 17 Feb 2026 (Gematsu, Windows Central). Starfield on PS5 Apr 2026 (GamesRadar+).
LIKE_SK = [
    ("The Elder Scrolls IV: Oblivion Remastered", "PS5, Xbox Series X|S, PC", "Skyrim's older sibling rebuilt with modern graphics: the same freedom, guilds and side quests in Cyrodiil.", "ps5 xbox pc", "open guild magic"),
    ("The Witcher 3: Wild Hunt", "PS5, Xbox Series X|S, PC, Switch", "A huge fantasy world with the best side quests in RPGs. Third person, with a set hero instead of your own.", "switch ps5 xbox pc", "open story"),
    ("Kingdom Come: Deliverance II", "PS5, Xbox Series X|S, PC", "First-person medieval RPG with no magic but deep sword fights, crime and a living world.", "ps5 xbox pc", "open story"),
    ("Avowed", "Xbox Series X|S, PC, PS5", "Obsidian's first-person fantasy RPG: swords and spells in each hand, like Skyrim's dual wielding.", "ps5 xbox pc", "magic story"),
    ("Elden Ring", "PS5, Xbox Series X|S, PC", "An open fantasy world full of secrets, with much harder combat. See our games like Elden Ring list for more.", "ps5 xbox pc", "open magic"),
    ("Dragon's Dogma 2", "PS5, Xbox Series X|S, PC", "Wander a dangerous open world with AI companions and climb on giant monsters.", "ps5 xbox pc", "open magic"),
    ("Starfield", "Xbox Series X|S, PC, PS5", "Bethesda's own space RPG: factions, ship building and the same pick-up-everything design as Skyrim.", "ps5 xbox pc", "guild story"),
    ("The Elder Scrolls Online", "PS5, Xbox Series X|S, PC", "The whole of Tamriel, including Skyrim itself, as an online RPG you can play solo or with friends.", "ps5 xbox pc", "open guild magic coop"),
    ("Fallout 4", "PS4, Xbox One, PC (plays on PS5 and Xbox Series X|S)", "Bethesda's open-world RPG after Skyrim, with settlement building in a post-apocalyptic Boston.", "ps5 ps4 xbox pc", "open guild"),
    ("Dragon Age: Inquisition", "PS4, Xbox One, PC (plays on PS5 and Xbox Series X|S)", "Big open zones, companions, romance and a fantasy war to lead.", "ps5 ps4 xbox pc", "story magic"),
]
_SK_LABEL = {"open": "Open world to explore", "guild": "Factions and guilds", "magic": "Magic and dragons", "story": "Story and quests", "coop": "Co-op"}
SK_SOON = ["fable", "exodus", "outward-2", "the-expanse-osiris-reborn", "kingdom-hearts-iv"]
_sk_soon = sorted([g for g in GAMES if g["slug"] in SK_SOON and g["slug"] != "kingdom-hearts-iv"], key=lambda g: (g["month"] or 13, g["date"] or "9999"))
_sk_fable = next((g for g in GAMES if g["slug"] == "fable"), None)
def _sk_on(tag): return [x[0] for x in LIKE_SK if tag in x[3].split()]
_sk_quick = ("The best games like Skyrim are Oblivion Remastered, The Witcher 3, Kingdom Come: Deliverance II, Avowed and Elden Ring. "
             f"The next big fantasy RPG is {_sk_fable['title']} on {nice_date(_sk_fable)}. " if _sk_fable else "The best games like Skyrim are Oblivion Remastered, The Witcher 3, Kingdom Come: Deliverance II, Avowed and Elden Ring. ") + \
            "The Elder Scrolls 6 has no release date, and it is not expected in 2027."
sk_body = (f'<header class="hero"><div class="wrap"><span class="kicker">Games like Skyrim</span>'
           f'<h1>Games like Skyrim:<br><span class="amber">open-world RPGs now, and the 2027 ones.</span></h1>'
           f'<p class="lead">Fantasy RPGs to play today on PS5, Xbox, Switch 2 and PC, filtered by what you loved about Skyrim, plus every similar RPG dated for 2027 and the latest on The Elder Scrolls 6.</p>'
           f'<p class="muted" style="margin:0">Last checked {e(UPDATED)} · {len(LIKE_SK)} picks out now · {len(_sk_soon)} coming in 2027</p></div></header>'
           f'<section><div class="wrap"><div class="out" style="margin-bottom:12px"><div class="row"><span><strong>Quick answer:</strong> {e(_sk_quick)}</span></div></div>'
           f'<div class="tool" id="er-tool" style="margin-bottom:24px"><h2 style="font-size:1.5rem;margin-top:0">Which game like Skyrim should I play?</h2>'
           f'<p class="muted">Pick your platform and what you loved most. Your choice is remembered on this device.</p>{_like_chips(_SK_LABEL, "What you loved")}'
           f'<p class="mono amber" id="er-count" aria-live="polite" style="margin:12px 0 0">{len(LIKE_SK)} games</p></div>'
           f'<div class="sec-head"><h2>What games are like Skyrim?</h2><span class="muted">out now</span></div>'
           f'<div class="out" id="er-list" style="margin-bottom:10px">{_like_rows(LIKE_SK, _SK_LABEL)}</div><p class="empty" id="er-none" hidden>No pick matches both. Try "Anything".</p></div></section>'
           + AD.format("sk-mid") +
           f'<section><div class="wrap"><div class="sec-head"><h2>What games like Skyrim come out in 2027?</h2><span class="muted">{len(_sk_soon)}</span></div>'
           f'<div class="out" style="margin-bottom:10px">{"".join(_er_srow(g) for g in _sk_soon)}</div>{_like_cd(_sk_fable)}'
           f'<p class="muted">Fable is the closest: a big fantasy world from Playground Games, also on PS5. Outward 2 is the most hardcore, an open-world survival RPG starting in Steam Early Access. See <a href="{href("rpgs-2027.html", 0)}">every RPG of 2027</a> for the full list.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>When does The Elder Scrolls 6 come out?</h2></div>'
           f'<p>There is no release date, window or platform list from Bethesda. The Verge reported that the game is called The Elder Scrolls 6: Sentinel, and Bloomberg\'s Jason Schreier said in November 2026 that it is "still more than 2 years away" (via GameRant and ScreenRant). Todd Howard has said most of Bethesda Game Studios now works on it, but "no one is in a hurry" (GamesRadar+). So do not expect it in 2027. We will add it to the board the day Bethesda gives a year.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>Will The Elder Scrolls 6 be on PS5?</h2></div>'
           f'<p>Not confirmed. Microsoft owns Bethesda, and some of its games have come to PS5 later: Starfield reached PS5 in April 2026 and Avowed in February 2026. Bethesda has not said anything about The Elder Scrolls 6 platforms.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>Is Skyrim on Switch 2?</h2></div>'
           f'<p>Yes. Skyrim Anniversary Edition came out on Switch 2 on 10 December 2025 (Gematsu, RPG Site). Other picks above that play on Switch 2: {e(_and([x[0] for x in LIKE_SK if "switch" in x[3].split()]))}. For new RPGs coming to Switch 2, see the <a href="{href("platforms/switch-2.html", 0)}">Switch 2 games of 2027</a>.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>What games are like Skyrim on PS5 and Xbox?</h2></div>'
           f'<p>PS5: {e(_and(_sk_on("ps5")))}. Xbox: {e(_and(_sk_on("xbox")))}. In 2027, Fable comes to both, and to Game Pass on day one; see <a href="{href("game-pass-2027.html", 0)}">every 2027 game on Game Pass</a>.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>Is there a game like Skyrim you can play with friends?</h2></div>'
           f'<p>The Elder Scrolls Online is the only one on this list built for co-op, and it includes Skyrim\'s own map. For more multiplayer, see <a href="{href("games-like-fortnite.html", 0)}">games like Fortnite</a>.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>Related pages and tools</h2></div><ul>'
           f'<li><a href="{href("games/fable.html", 0)}">Fable release date</a> and countdown</li>'
           f'<li><a href="{href("games-like-elden-ring.html", 0)}">Games like Elden Ring</a>: soulslikes now and in 2027</li>'
           f'<li><a href="{href("games-like-baldurs-gate-3.html", 0)}">Games like Baldur\'s Gate 3</a>: party RPGs</li>'
           f'<li><a href="{href("games-like-the-witcher-3.html", 0)}">Games like The Witcher 3</a>: story RPGs and Songs of the Past</li>'
           f'<li><a href="{href("games-like-zelda.html", 0)}">Games like Zelda</a>: fantasy adventures</li>'
           f'<li><a href="{href("backlog-planner-2027.html", 0)}">2027 backlog planner</a>: fit long RPGs around the new releases</li></ul></div></section>')
sk_faq = [("What games are like Skyrim?", _and([x[0] for x in LIKE_SK]) + "."),
          ("What is the closest game to Skyrim?", "The Elder Scrolls IV: Oblivion Remastered, Bethesda's earlier Elder Scrolls game rebuilt in 2025. Avowed is the closest first-person fantasy RPG from another studio."),
          ("When does The Elder Scrolls 6 come out?", "Bethesda has not given a date or year. Jason Schreier said in November 2026 that it is more than two years away."),
          ("Is Skyrim on Switch 2?", "Yes. Skyrim Anniversary Edition launched on Switch 2 on 10 December 2025."),
          ("What open-world RPGs come out in 2027?", _and([g['title'] + ' (' + nice_date(g) + ')' for g in _sk_soon]) + ".")]
page("games-like-skyrim.html", "Games Like Skyrim: 10 RPG Picks, 2027 RPGs & TES 6 Date",
     "Games like Skyrim on PS5, Xbox, Switch 2 and PC: Oblivion Remastered, Witcher 3, Kingdom Come 2, Avowed, plus 2027 RPGs like Fable and the Elder Scrolls 6 news.",
     sk_body, 0, sk_faq, crumbs=[("Home", DOMAIN + "/"), ("Every RPG of 2027", canon("rpgs-2027.html")), ("Games like Skyrim", canon("games-like-skyrim.html"))])


# ---------------- GAMES LIKE HADES (27 Nov 2026, demand: "games like hades", DEMAND N49) ----------------
# Evidence: GamesRadar+ "25 best roguelikes", G2A "best games like Hades", Eneba hub, SummerEngine "13 games like Hades 2026", premiumcdkeys "games like Hades II 2026".
# Facts: Hades II on PS5 + Xbox Series X|S 14 Apr 2026 (Supergiant blog, Gematsu, RPG Site, VGC). Supergiant hiring for next project, "Hades 3 is not preordained" (GamesRadar+, PC Gamer).
# Rogue Fortune: Glowmade, PS5/Xbox/Switch 2/PC, no date (Gematsu, Niche Gamer, Rogueliker, Aug 2026).
LIKE_HD = [
    ("Hades II", "PC, Switch, Switch 2, PS5, Xbox Series X|S", "The sequel: play as Melinoë, Hades' daughter, with new weapons, magick and an even bigger cast between runs.", "switch ps5 xbox pc", "action build story"),
    ("Hades", "PC, Switch, PS5, PS4, Xbox Series X|S, Xbox One", "Still one of the best: escape the underworld as Zagreus, with Olympian boons and a story that moves on every time you die.", "switch ps5 ps4 xbox pc", "action build story"),
    ("Dead Cells", "PC, Switch, PS4, Xbox One (plays on PS5 and Xbox Series X|S)", "Fast 2D runs through a changing castle. Huge weapon list and tight dodge-roll combat.", "switch ps5 ps4 xbox pc", "action build"),
    ("Children of Morta", "PC, Switch, PS4, Xbox One (plays on PS5 and Xbox Series X|S)", "Top-down runs as members of one family, with a warm story told between dungeons. Local co-op.", "switch ps5 ps4 xbox pc", "action story coop"),
    ("Ravenswatch", "PC, Switch, PS5, PS4, Xbox Series X|S, Xbox One", "Top-down fairy-tale heroes with Hades-style talents, playable solo or online with up to four.", "switch ps5 ps4 xbox pc", "action build coop"),
    ("Curse of the Dead Gods", "PC, Switch, PS4, Xbox One (plays on PS5 and Xbox Series X|S)", "The closest in feel: isometric temple runs with combos, relics and curses that stack up.", "switch ps5 ps4 xbox pc", "action build"),
    ("Rogue Legacy 2", "PC, Switch, PS5, PS4, Xbox Series X|S, Xbox One", "Each death hands the castle to an heir with odd traits. Gold buys permanent upgrades.", "switch ps5 ps4 xbox pc", "build story"),
    ("Cult of the Lamb", "PC, Switch, PS5, PS4, Xbox Series X|S, Xbox One", "Short dungeon runs mixed with running your own cute, creepy cult between them. Co-op too.", "switch ps5 ps4 xbox pc", "action build coop"),
    ("Enter the Gungeon", "PC, Switch, PS4, Xbox One (plays on PS5 and Xbox Series X|S)", "A bullet-hell dungeon crawler with hundreds of silly guns and a two-player mode.", "switch ps5 ps4 xbox pc", "action build coop"),
    ("Returnal", "PS5, PC", "Third-person bullet-hell runs on an alien planet, with a mystery that unfolds as you loop.", "ps5 pc", "action story"),
    ("Bastion", "PC, Switch, PS4, Xbox One (plays on PS5 and Xbox Series X|S)", "Supergiant's first game: not a roguelike, but the same narrator-led style, art and music.", "switch ps5 ps4 xbox pc", "story"),
]
_HD_LABEL = {"action": "Fast combat", "build": "Builds and boons", "story": "Story between runs", "coop": "Co-op"}
HD_SOON = ["armatus", "everything-is-crab", "mr-magpies-harmless-card-game"]
_hd_soon = sorted([g for g in GAMES if g["slug"] in HD_SOON], key=lambda g: (g["month"] or 13, g["date"] or "9999"))
_hd_first = next((g for g in _hd_soon if g.get("date")), None)
def _hd_on(tag): return [x[0] for x in LIKE_HD if tag in x[3].split()]
_hd_quick = ("The best games like Hades are Hades II, Dead Cells, Curse of the Dead Gods, Children of Morta, Ravenswatch and Cult of the Lamb. "
             "Hades II is now on every platform, including PS5 and Xbox since 14 April 2026. Supergiant has not announced Hades 3 or its next game.")
hd_body = (f'<header class="hero"><div class="wrap"><span class="kicker">Games like Hades</span>'
           f'<h1>Games like Hades:<br><span class="amber">roguelites to play now, and in 2027.</span></h1>'
           f'<p class="lead">Run-based action games on Switch 2, PS5, Xbox and PC, filtered by what hooked you in Hades, plus the roguelites dated for 2027 and the latest on Hades 3.</p>'
           f'<p class="muted" style="margin:0">Last checked {e(UPDATED)} · {len(LIKE_HD)} picks out now · {len(_hd_soon)} coming in 2027</p></div></header>'
           f'<section><div class="wrap"><div class="out" style="margin-bottom:12px"><div class="row"><span><strong>Quick answer:</strong> {e(_hd_quick)}</span></div></div>'
           f'<div class="tool" id="er-tool" style="margin-bottom:24px"><h2 style="font-size:1.5rem;margin-top:0">Which game like Hades should I play?</h2>'
           f'<p class="muted">Pick your platform and what you loved most. Your choice is remembered on this device.</p>{_like_chips(_HD_LABEL, "What you loved")}'
           f'<p class="mono amber" id="er-count" aria-live="polite" style="margin:12px 0 0">{len(LIKE_HD)} games</p></div>'
           f'<div class="sec-head"><h2>What games are like Hades?</h2><span class="muted">out now</span></div>'
           f'<div class="out" id="er-list" style="margin-bottom:10px">{_like_rows(LIKE_HD, _HD_LABEL)}</div><p class="empty" id="er-none" hidden>No pick matches both. Try "Anything".</p></div></section>'
           + AD.format("hd-mid") +
           f'<section><div class="wrap"><div class="sec-head"><h2>What roguelites come out in 2027?</h2><span class="muted">{len(_hd_soon)} dated</span></div>'
           f'<div class="out" style="margin-bottom:10px">{"".join(_er_srow(g) for g in _hd_soon)}</div>{_like_cd(_hd_first)}'
           f'<p class="muted">Armatus is a third-person roguelite shooter, Everything Is Crab is an evolution roguelite on Switch 2, and Mr. Magpie\'s Harmless Card Game is a run-based deckbuilder. Rogue Fortune, a fast action roguelite from Glowmade that its makers pitch as Hades meets temple raiding, is coming to PS5, Xbox Series X|S, Switch 2 and PC but has no date yet (Gematsu, Niche Gamer). See <a href="{href("games-by-genre-2027.html", 0)}">2027 games by genre</a> for more.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>Is Hades 2 on PS5 and Xbox?</h2></div>'
           f'<p>Yes. Hades II came to PS5 and Xbox Series X|S on 14 April 2026, after its 1.0 launch on PC, Switch and Switch 2 in September 2025 (Supergiant Games, Gematsu, RPG Site). Other picks on PS5: {e(_and(_hd_on("ps5")))}.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>Will there be a Hades 3?</h2></div>'
           f'<p>Nothing is announced. Supergiant\'s studio director said a third Hades is "not preordained", and the studio is now hiring for its next project without saying what it is (PC Gamer, GamesRadar+). Supergiant has always made a new kind of game after each release, and Hades II was its first sequel. We will add its next game to the board when it gets a year.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>What games like Hades are on Switch 2?</h2></div>'
           f'<p>{e(_and(_hd_on("switch")))} all play on Switch 2. Hades II also has its own Switch 2 version. In 2027, Everything Is Crab comes only to Switch 2. See all <a href="{href("platforms/switch-2.html", 0)}">Switch 2 games of 2027</a>.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>Is there a game like Hades I can play with friends?</h2></div>'
           f'<p>Hades and Hades II are single player. For co-op, try {e(_and([x[0] for x in LIKE_HD if "coop" in x[4].split()]))}. Ravenswatch is the closest, with Hades-style talent picks for up to four players online.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>Related pages and tools</h2></div><ul>'
           f'<li><a href="{href("games-like-hollow-knight.html", 0)}">Games like Hollow Knight</a>: metroidvanias now and in 2027</li>'
           f'<li><a href="{href("games-like-elden-ring.html", 0)}">Games like Elden Ring</a>: hard action games</li>'
           f'<li><a href="{href("countdown.html", 0)}">Game release countdown</a>: build a countdown to any 2027 game</li>'
           f'<li><a href="{href("backlog-planner-2027.html", 0)}">2027 backlog planner</a>: fit short runs between big releases</li></ul></div></section>')
hd_faq = [("What games are like Hades?", _and([x[0] for x in LIKE_HD]) + "."),
          ("What is the closest game to Hades?", "Hades II, its sequel. From other studios, Curse of the Dead Gods is closest in feel, and Ravenswatch is closest with friends."),
          ("Is Hades 2 on PS5 and Xbox?", "Yes, since 14 April 2026. It launched on PC, Switch and Switch 2 in September 2025."),
          ("Will there be a Hades 3?", "Not announced. Supergiant says a third game is not preordained and is hiring for its next, unnamed project."),
          ("What roguelites come out in 2027?", _and([g['title'] + ' (' + nice_date(g) + ')' for g in _hd_soon]) + ". Rogue Fortune has no date yet.")]
page("games-like-hades.html", "Games Like Hades: 11 Roguelite Picks & 2027 Releases",
     "Games like Hades on Switch 2, PS5, Xbox and PC: Hades II, Dead Cells, Curse of the Dead Gods, Ravenswatch, Cult of the Lamb, plus 2027 roguelites.",
     hd_body, 0, hd_faq, crumbs=[("Home", DOMAIN + "/"), ("2027 games by genre", canon("games-by-genre-2027.html")), ("Games like Hades", canon("games-like-hades.html"))])


# ---------------- GAMES LIKE THE WITCHER 3 (27 Nov 2026, demand: "games like witcher 3", "witcher 4 release date", "songs of the past release date", DEMAND N49) ----------------
# Evidence: GamesRadar+ "games like Witcher 3" (US/UK/AU), Eneba, Kinguin "best games like Witcher 3 to play in 2026", SVG, G2A; Ranker "games like Blood of Dawnwalker".
# Facts: Songs of the Past 2027, paid, PC/PS5/Xbox/Switch 2, CDPR + Fool's Theory (CDPR press 25 Aug 2026, Gematsu, RPG Site, TechRadar).
# Witcher 3 Remastered 29 Sep 2026 free upgrade incl. Switch 2 (CDPR press, Nintendo Life, RPG Site). Witcher 4 targeting 2028 (PC Gamer, GamesRadar+, Game Informer, Push Square).
# The Blood of Dawnwalker 3 Sep 2026 (Shacknews, GamesRadar+, GamingBolt).
LIKE_W3 = [
    ("The Blood of Dawnwalker", "PS5, Xbox Series X|S, PC", "From the director of The Witcher 3 at Rebel Wolves: a dark fantasy RPG where you hunt as a human by day and a vampire by night. Out since 3 September 2026.", "ps5 xbox pc", "monster story dark"),
    ("Cyberpunk 2077", "PS5, Xbox Series X|S, PC, Switch 2", "CD Projekt Red's other RPG: the same deep side quests and choices, in a neon future city.", "switch ps5 xbox pc", "story open"),
    ("Kingdom Come: Deliverance II", "PS5, Xbox Series X|S, PC", "Grounded medieval RPG with a strong story, real sword fights and a living world. No magic.", "ps5 xbox pc", "story open"),
    ("Red Dead Redemption 2", "PS4, Xbox One, PC (plays on PS5 and Xbox Series X|S)", "A slow, detailed open world with the best-written story in the genre. Westerns instead of monsters.", "ps5 ps4 xbox pc", "story open"),
    ("Baldur's Gate 3", "PS5, Xbox Series X|S, PC", "Choices that matter, great companions and romance, with turn-based fights instead of action.", "ps5 xbox pc", "story dark"),
    ("Dragon's Dogma 2", "PS5, Xbox Series X|S, PC", "Climb onto griffins and cyclopes in an open fantasy world, with hired AI companions.", "ps5 xbox pc", "monster open"),
    ("Elden Ring", "PS5, Xbox Series X|S, PC", "A dark open fantasy world full of monsters, with much harder combat and less story up front.", "ps5 xbox pc", "monster open dark"),
    ("Dragon Age: Inquisition", "PS4, Xbox One, PC (plays on PS5 and Xbox Series X|S)", "Big zones, companions, romance and political choices across a fantasy war.", "ps5 ps4 xbox pc", "story dark"),
    ("Ghost of Yotei", "PS5", "A revenge story across an open Japan, with clean sword combat and side tales worth doing.", "ps5", "story open"),
    ("The Elder Scrolls IV: Oblivion Remastered", "PS5, Xbox Series X|S, PC", "A classic open fantasy world rebuilt in 2025, with guild quests that rival Witcher side stories.", "ps5 xbox pc", "open monster"),
]
_W3_LABEL = {"monster": "Monster hunting", "story": "Story and choices", "open": "Open world", "dark": "Dark fantasy"}
W3_SOON = ["the-witcher-3-songs-of-the-past", "fable", "exodus", "lords-of-the-fallen-ii", "the-expanse-osiris-reborn"]
_w3_soon = sorted([g for g in GAMES if g["slug"] in W3_SOON], key=lambda g: (g["month"] or 13, g["date"] or "9999"))
_w3_fable = next((g for g in GAMES if g["slug"] == "fable"), None)
def _w3_on(tag): return [x[0] for x in LIKE_W3 if tag in x[3].split()]
_w3_quick = ("The best games like The Witcher 3 are The Blood of Dawnwalker (from the Witcher 3 director), Cyberpunk 2077, Kingdom Come: Deliverance II, Red Dead Redemption 2 and Baldur's Gate 3. "
             "The next new Witcher content is the Songs of the Past expansion in 2027; The Witcher 4 is targeting 2028.")
w3_body = (f'<header class="hero"><div class="wrap"><span class="kicker">Games like The Witcher 3</span>'
           f'<h1>Games like The Witcher 3:<br><span class="amber">story RPGs now, and what is next for Geralt.</span></h1>'
           f'<p class="lead">RPGs with Witcher-level quests on PS5, Xbox, Switch 2 and PC, filtered by what you loved, plus the 2027 RPGs, the Songs of the Past expansion and The Witcher 4 date.</p>'
           f'<p class="muted" style="margin:0">Last checked {e(UPDATED)} · {len(LIKE_W3)} picks out now · {len(_w3_soon)} coming in 2027</p></div></header>'
           f'<section><div class="wrap"><div class="out" style="margin-bottom:12px"><div class="row"><span><strong>Quick answer:</strong> {e(_w3_quick)}</span></div></div>'
           f'<div class="tool" id="er-tool" style="margin-bottom:24px"><h2 style="font-size:1.5rem;margin-top:0">Which game like The Witcher 3 should I play?</h2>'
           f'<p class="muted">Pick your platform and what you loved most. Your choice is remembered on this device.</p>{_like_chips(_W3_LABEL, "What you loved")}'
           f'<p class="mono amber" id="er-count" aria-live="polite" style="margin:12px 0 0">{len(LIKE_W3)} games</p></div>'
           f'<div class="sec-head"><h2>What games are like The Witcher 3?</h2><span class="muted">out now</span></div>'
           f'<div class="out" id="er-list" style="margin-bottom:10px">{_like_rows(LIKE_W3, _W3_LABEL)}</div><p class="empty" id="er-none" hidden>No pick matches both. Try "Anything".</p></div></section>'
           + AD.format("w3-mid") +
           f'<section><div class="wrap"><div class="sec-head"><h2>What RPGs like The Witcher 3 come out in 2027?</h2><span class="muted">{len(_w3_soon)}</span></div>'
           f'<div class="out" style="margin-bottom:10px">{"".join(_er_srow(g) for g in _w3_soon)}</div>{_like_cd(_w3_fable)}'
           f'<p class="muted">Fable is the biggest dated one, from Playground Games, also on PS5. For every RPG of the year, see <a href="{href("rpgs-2027.html", 0)}">every RPG of 2027</a>.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>When does The Witcher 3: Songs of the Past come out?</h2></div>'
           f'<p>In 2027, with no month or day yet. It is a paid story expansion, the first since Blood and Wine in 2016, made by CD Projekt Red with Fool\'s Theory. You play Geralt in a new region called Letten, with a new chain weapon. It comes to PS5, Xbox Series X|S, PC and Switch 2 (CD Projekt Red, Gematsu, RPG Site). See our <a href="{href("games/the-witcher-3-songs-of-the-past.html", 0)}">Songs of the Past page</a> for every confirmed detail.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>When does The Witcher 4 come out?</h2></div>'
           f'<p>CD Projekt Red is targeting 2028. Its joint CEO said so in August 2026 (PC Gamer, GamesRadar+, Game Informer). There is no exact date and no platform list yet, so it is not on our 2027 board. It is nominated for Most Anticipated Game at <a href="{href("game-awards-2026.html", 0)}">The Game Awards 2026</a>.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>Is The Witcher 3 on Switch 2?</h2></div>'
           f'<p>Yes. The Witcher 3: Wild Hunt Remastered launched on 29 September 2026 with a native Switch 2 version, as a free upgrade for existing owners (CD Projekt Red, Nintendo Life). Hearts of Stone and Blood and Wine were made free for owners in August 2026. Other picks on Switch 2: {e(_and(_w3_on("switch")))}.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>What games are like The Witcher 3 on PS5 and Xbox?</h2></div>'
           f'<p>PS5: {e(_and(_w3_on("ps5")))}. Xbox: {e(_and(_w3_on("xbox")))}.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>Related pages and tools</h2></div><ul>'
           f'<li><a href="{href("games-like-skyrim.html", 0)}">Games like Skyrim</a>: open-world RPGs and Elder Scrolls 6 news</li>'
           f'<li><a href="{href("games-like-baldurs-gate-3.html", 0)}">Games like Baldur\'s Gate 3</a>: party RPGs</li>'
           f'<li><a href="{href("games/fable.html", 0)}">Fable release date</a> and countdown</li>'
           f'<li><a href="{href("games-like-cyberpunk-2077.html", 0)}">Games like Cyberpunk 2077</a> and <a href="{href("games-like-red-dead-redemption-2.html", 0)}">games like Red Dead Redemption 2</a></li>'
           f'<li><a href="{href("backlog-planner-2027.html", 0)}">2027 backlog planner</a>: fit long RPGs around new releases</li></ul></div></section>')
w3_faq = [("What games are like The Witcher 3?", _and([x[0] for x in LIKE_W3]) + "."),
          ("What is the closest game to The Witcher 3?", "The Blood of Dawnwalker, made by Rebel Wolves and directed by The Witcher 3's game director, out since 3 September 2026."),
          ("When does The Witcher 3: Songs of the Past come out?", "In 2027 on PS5, Xbox Series X|S, PC and Switch 2. No month or day has been announced."),
          ("When does The Witcher 4 come out?", "CD Projekt Red is targeting 2028. No exact date or platforms have been announced."),
          ("Is The Witcher 3 Remastered free?", "Yes for existing owners on qualifying platforms. It launched on 29 September 2026, including on Switch 2.")]
page("games-like-the-witcher-3.html", "Games Like The Witcher 3: 10 RPGs & Witcher in 2027",
     "Games like The Witcher 3 on PS5, Xbox, Switch 2 and PC: Blood of Dawnwalker, Cyberpunk 2077, Kingdom Come 2, plus the 2027 Songs of the Past DLC and Witcher 4.",
     w3_body, 0, w3_faq, crumbs=[("Home", DOMAIN + "/"), ("Every RPG of 2027", canon("rpgs-2027.html")), ("Games like The Witcher 3", canon("games-like-the-witcher-3.html"))])


# ---------------- GAMES LIKE RED DEAD REDEMPTION 2 (27 Nov 2026, demand: "games like red dead redemption 2", "red dead redemption 3 release date", DEMAND N54) ----------------
# Evidence: GamesRadar+ US/UK "games like Red Dead Redemption 2", Twinfinite, Game Rant "story heavy games like RDR2", GGRecon, PowerUp "games like RDR2 on PS5" (Aug 2026), G2A, Eneba.
# Facts: RDR3 not announced (win.gg, NoobFeed, EGW); RDR2 next-gen upgrade only rumoured (VideoGamer, Notebookcheck); Red Dead Redemption (2010) native PS5/Xbox Series/Switch 2 versions announced Nov 2025 (Rockstar, Final Weapon).
LIKE_RD = [
    ("Ghost of Yotei", "PS5", "A slow-burn revenge story across an open Japan, with horse riding, camps and side tales that rival Red Dead's.", "ps5", "story open"),
    ("Kingdom Come: Deliverance II", "PS5, Xbox Series X|S, PC", "The closest in feel: grounded, detailed and unhurried, with a strong story and chores that make the world feel real.", "ps5 xbox pc", "story open real"),
    ("The Witcher 3: Wild Hunt", "PS5, Xbox Series X|S, PC, Switch 2", "Huge open world, a horse called Roach and some of the best-written side quests in games.", "switch ps5 xbox pc", "story open"),
    ("Mafia: The Old Country", "PS5, Xbox Series X|S, PC", "A tight, cinematic crime story set in 1900s Sicily, from the Mafia series. Linear, but with Red Dead-level period detail.", "ps5 xbox pc", "story real"),
    ("Grand Theft Auto 6", "PS5, Xbox Series X|S", "Rockstar's newest open world, out since 19 November 2026: the same studio, the same attention to detail, in modern Leonida.", "ps5 xbox", "open story"),
    ("Days Gone", "PS5, PS4, PC", "Ride a motorbike through an open Oregon wilderness, with camps, a slow story and hordes instead of bounty hunters.", "ps5 ps4 pc", "open story"),
    ("Hunt: Showdown 1896", "PS5, Xbox Series X|S, PC", "Online western-era shooter: 1890s guns, bounties and monsters in the swamps and mountains. Tense and slow.", "ps5 xbox pc", "west online"),
    ("Desperados III", "PS4, Xbox One, PC (plays on PS5 and Xbox Series X|S)", "A western tactics game: plan ambushes with a gang of outlaws, top down. Great if you loved the gang.", "ps5 ps4 xbox pc", "west"),
    ("Weird West", "PS4, Xbox One, PC (plays on PS5 and Xbox Series X|S)", "A dark-fantasy western RPG from Arkane veterans, with five linked outlaw stories and real choices.", "ps5 ps4 xbox pc", "west story"),
    ("Red Dead Redemption", "PS5, Xbox Series X|S, Switch 2, PS4, Switch, PC", "The 2010 original, the story that comes after RDR2. Native PS5, Xbox Series X|S and Switch 2 versions were announced by Rockstar in November 2025.", "switch ps5 ps4 xbox pc", "west story open"),
]
_RD_LABEL = {"west": "Wild West", "story": "Story", "open": "Open world", "real": "Realistic", "online": "Online"}
RD_SOON = ["showa-american-story", "stranger-than-heaven", "007-first-light", "god-of-war-laufey", "state-of-decay-3"]
_rd_soon = sorted([g for g in GAMES if g["slug"] in RD_SOON], key=lambda g: (g["month"] or 13, g["date"] or "9999"))
_rd_cd = next((g for g in GAMES if g["slug"] == "stranger-than-heaven"), None)
def _rd_on(tag): return [x[0] for x in LIKE_RD if tag in x[3].split()]
_rd_quick = ("The best games like Red Dead Redemption 2 are Ghost of Yotei, Kingdom Come: Deliverance II, The Witcher 3, Mafia: The Old Country and Rockstar's own GTA 6. "
             "Red Dead Redemption 3 has not been announced, and Rockstar has not confirmed a PS5 or Xbox Series X|S upgrade for RDR2.")
rd_body = (f'<header class="hero"><div class="wrap"><span class="kicker">Games like Red Dead Redemption 2</span>'
           f'<h1>Games like Red Dead Redemption 2:<br><span class="amber">slow, story-rich open worlds.</span></h1>'
           f'<p class="lead">Westerns and Red Dead-style open worlds on PS5, Xbox, Switch 2 and PC, filtered by what you loved, plus the 2027 games to watch and the latest on Red Dead Redemption 3.</p>'
           f'<p class="muted" style="margin:0">Last checked {e(UPDATED)} · {len(LIKE_RD)} picks out now · {len(_rd_soon)} coming in 2027</p></div></header>'
           f'<section><div class="wrap"><div class="out" style="margin-bottom:12px"><div class="row"><span><strong>Quick answer:</strong> {e(_rd_quick)}</span></div></div>'
           f'<div class="tool" id="er-tool" style="margin-bottom:24px"><h2 style="font-size:1.5rem;margin-top:0">Which game like Red Dead Redemption 2 should I play?</h2>'
           f'<p class="muted">Pick your platform and what you loved most. Your choice is remembered on this device.</p>{_like_chips(_RD_LABEL, "What you loved")}'
           f'<p class="mono amber" id="er-count" aria-live="polite" style="margin:12px 0 0">{len(LIKE_RD)} games</p></div>'
           f'<div class="sec-head"><h2>What games are like Red Dead Redemption 2?</h2><span class="muted">out now</span></div>'
           f'<div class="out" id="er-list" style="margin-bottom:10px">{_like_rows(LIKE_RD, _RD_LABEL)}</div><p class="empty" id="er-none" hidden>No pick matches both. Try "Anything".</p></div></section>'
           + AD.format("rd-mid") +
           f'<section><div class="wrap"><div class="sec-head"><h2>What games like Red Dead Redemption 2 come out in 2027?</h2><span class="muted">{len(_rd_soon)}</span></div>'
           f'<div class="out" style="margin-bottom:10px">{"".join(_er_srow(g) for g in _rd_soon)}</div>{_like_cd(_rd_cd)}'
           f'<p class="muted">No western is dated for 2027 yet. The closest picks are period crime stories and big story-led action games. Browse everything on the <a href="{href("calendar.html", 0)}">2027 release calendar</a>.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>When does Red Dead Redemption 3 come out?</h2></div>'
           f'<p>There is no date because Rockstar has not announced it. Rockstar spent the last few years on GTA 6, which launched on 19 November 2026, and has not named its next game. Reports that a third Red Dead is planned are speculation for now (win.gg, NoobFeed). See <a href="{href("after-gta-6.html", 0)}">what comes after GTA 6</a> for everything Rockstar and Take-Two have actually said.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>Is there a PS5 version of Red Dead Redemption 2?</h2></div>'
           f'<p>Not officially. RDR2 runs on PS5 and Xbox Series X|S through backwards compatibility, at its PS4 and Xbox One settings. A native upgrade has been reported by insiders but not confirmed by Rockstar (VideoGamer, Notebookcheck). The first game did get native PS5, Xbox Series X|S and Switch 2 versions, announced in November 2025.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>What games are like Red Dead Redemption 2 on PS5 and Xbox?</h2></div>'
           f'<p>PS5: {e(_and(_rd_on("ps5")))}. Xbox: {e(_and(_rd_on("xbox")))}. On Switch 2: {e(_and(_rd_on("switch")))}.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>Related pages and tools</h2></div><ul>'
           f'<li><a href="{href("games-like-gta-6.html", 0)}">Games like GTA 6</a>: open-world crime games</li>'
           f'<li><a href="{href("games-like-the-witcher-3.html", 0)}">Games like The Witcher 3</a>: story RPGs</li>'
           f'<li><a href="{href("after-gta-6.html", 0)}">What to play after GTA 6</a>, and Rockstar\'s next game</li>'
           f'<li><a href="{href("backlog-planner-2027.html", 0)}">2027 backlog planner</a>: fit a 60-hour game around new releases</li></ul></div></section>')
rd_faq = [("What games are like Red Dead Redemption 2?", _and([x[0] for x in LIKE_RD]) + "."),
          ("Is Red Dead Redemption 3 coming out?", "Rockstar has not announced Red Dead Redemption 3, so there is no release date or platform list."),
          ("Is there a PS5 version of Red Dead Redemption 2?", "Not officially. RDR2 plays on PS5 and Xbox Series X|S through backwards compatibility; a native upgrade has been rumoured but not confirmed by Rockstar."),
          ("What is the closest game to Red Dead Redemption 2?", "Kingdom Come: Deliverance II for its slow, realistic open world, and Ghost of Yotei for its riding and revenge story. For Wild West settings, Hunt: Showdown 1896 and Weird West."),
          ("Is there a western game coming in 2027?", "Not one with a confirmed 2027 date yet. We add any western to the 2027 board as soon as a publisher dates it.")]
page("games-like-red-dead-redemption-2.html", "Games Like Red Dead Redemption 2: 10 Picks & RDR3 News",
     "Games like Red Dead Redemption 2 on PS5, Xbox, Switch 2 and PC: Ghost of Yotei, Kingdom Come 2, Witcher 3, GTA 6, plus RDR3 and RDR2 PS5 upgrade news.",
     rd_body, 0, rd_faq, crumbs=[("Home", DOMAIN + "/"), ("2027 games by genre", canon("games-by-genre-2027.html")), ("Games like Red Dead Redemption 2", canon("games-like-red-dead-redemption-2.html"))])

# ---------------- GAMES LIKE CYBERPUNK 2077 (27 Nov 2026, demand: "games like cyberpunk 2077", "cyberpunk 2 release date", DEMAND N54) ----------------
# Evidence: GamesRadar+ US/UK/AU "games like Cyberpunk", Eneba, Driffle "Top 10 games like Cyberpunk 2026", GameGeeker.
# Facts: Cyberpunk 2 in pre-production, no date; CDPR says pre-production to release takes 4-5 years on average (GamesRadar+, TechSpot, TweakTown); not before 2028 (LevelUp); analysts guess 2029-2030 (TechPowerUp, Wccftech).
LIKE_CP = [
    ("Deus Ex: Mankind Divided", "PS4, Xbox One, PC (plays on PS5 and Xbox Series X|S)", "The classic cyberpunk RPG: augmentations, hacking and many ways through every mission.", "ps5 ps4 xbox pc", "rpg stealth"),
    ("The Outer Worlds 2", "PS5, Xbox Series X|S, PC", "Obsidian's first-person sci-fi RPG with companions, dark jokes and choices that change the story.", "ps5 xbox pc", "rpg story"),
    ("Ghostrunner 2", "PS5, Xbox Series X|S, PC", "Fast first-person parkour and katana fights in a neon cyberpunk tower. Pure action, no RPG.", "ps5 xbox pc", "action"),
    ("Mass Effect Legendary Edition", "PS4, Xbox One, PC (plays on PS5 and Xbox Series X|S)", "Three sci-fi RPGs with a crew you care about and romance, the series that inspired many Cyberpunk players.", "ps5 ps4 xbox pc", "rpg story"),
    ("The Witcher 3: Wild Hunt", "PS5, Xbox Series X|S, PC, Switch 2", "CD Projekt Red's previous RPG: the same quest writing, in a dark fantasy world.", "switch ps5 xbox pc", "rpg story"),
    ("Stray", "PS5, PS4, Xbox Series X|S, Xbox One, PC, Switch", "Play a cat in a neon robot city. Short, gentle and full of cyberpunk atmosphere.", "switch ps5 ps4 xbox pc", "story"),
    ("Watch Dogs: Legion", "PS5, PS4, Xbox Series X|S, Xbox One, PC", "Hack a near-future London and recruit anyone in the street. An open city like Night City.", "ps5 ps4 xbox pc", "open stealth"),
    ("Citizen Sleeper 2: Starward Vector", "PS5, Xbox Series X|S, PC, Switch", "A dice-driven narrative RPG about a runaway android crew. Gritty and very well written.", "switch ps5 xbox pc", "rpg story"),
    ("Observer: System Redux", "PS5, Xbox Series X|S, PC", "A cyberpunk detective horror game: hack into suspects' minds in a rundown apartment block.", "ps5 xbox pc", "story"),
    ("Grand Theft Auto 6", "PS5, Xbox Series X|S", "The big modern open city to explore right now, out since 19 November 2026. Less sci-fi, more crime.", "ps5 xbox", "open action"),
]
_CP_LABEL = {"rpg": "RPG and choices", "story": "Story", "open": "Open city", "action": "Action", "stealth": "Hacking and stealth"}
CP_SOON = ["exodus", "metro-2039", "the-expanse-osiris-reborn", "squadron-42", "ontos", "spyder-agent-8"]
_cp_soon = sorted([g for g in GAMES if g["slug"] in CP_SOON], key=lambda g: (g["month"] or 13, g["date"] or "9999"))
_cp_cd = next((g for g in GAMES if g["slug"] == "exodus"), None)
def _cp_on(tag): return [x[0] for x in LIKE_CP if tag in x[3].split()]
_cp_quick = ("The best games like Cyberpunk 2077 are Deus Ex: Mankind Divided, The Outer Worlds 2, Ghostrunner 2, Mass Effect Legendary Edition and The Witcher 3. "
             f"The biggest 2027 sci-fi RPG is Exodus ({nice_date(_cp_cd) if _cp_cd else '2027'}). Cyberpunk 2 has no date and is in pre-production.")
cp_body = (f'<header class="hero"><div class="wrap"><span class="kicker">Games like Cyberpunk 2077</span>'
           f'<h1>Games like Cyberpunk 2077:<br><span class="amber">neon RPGs now, sci-fi in 2027.</span></h1>'
           f'<p class="lead">Cyberpunk and sci-fi games on PS5, Xbox, Switch 2 and PC, filtered by what you loved about Night City, plus the 2027 sci-fi games and the Cyberpunk 2 timeline.</p>'
           f'<p class="muted" style="margin:0">Last checked {e(UPDATED)} · {len(LIKE_CP)} picks out now · {len(_cp_soon)} coming in 2027</p></div></header>'
           f'<section><div class="wrap"><div class="out" style="margin-bottom:12px"><div class="row"><span><strong>Quick answer:</strong> {e(_cp_quick)}</span></div></div>'
           f'<div class="tool" id="er-tool" style="margin-bottom:24px"><h2 style="font-size:1.5rem;margin-top:0">Which game like Cyberpunk 2077 should I play?</h2>'
           f'<p class="muted">Pick your platform and what you loved most. Your choice is remembered on this device.</p>{_like_chips(_CP_LABEL, "What you loved")}'
           f'<p class="mono amber" id="er-count" aria-live="polite" style="margin:12px 0 0">{len(LIKE_CP)} games</p></div>'
           f'<div class="sec-head"><h2>What games are like Cyberpunk 2077?</h2><span class="muted">out now</span></div>'
           f'<div class="out" id="er-list" style="margin-bottom:10px">{_like_rows(LIKE_CP, _CP_LABEL)}</div><p class="empty" id="er-none" hidden>No pick matches both. Try "Anything".</p></div></section>'
           + AD.format("cp-mid") +
           f'<section><div class="wrap"><div class="sec-head"><h2>What sci-fi games like Cyberpunk come out in 2027?</h2><span class="muted">{len(_cp_soon)}</span></div>'
           f'<div class="out" style="margin-bottom:10px">{"".join(_er_srow(g) for g in _cp_soon)}</div>{_like_cd(_cp_cd)}'
           f'<p class="muted">Exodus, from former Mass Effect developers at Archetype, is the one Cyberpunk RPG fans are watching most. See <a href="{href("rpgs-2027.html", 0)}">every RPG of 2027</a>.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>When does Cyberpunk 2 come out?</h2></div>'
           f'<p>There is no release date. CD Projekt Red says the sequel is in pre-production, and its boss has said the journey from pre-production to release takes four to five years on average (GamesRadar+, TechSpot). Outlets read that as not before 2028 at the earliest, and some analysts guess 2029 or 2030 (LevelUp, TechPowerUp). It is not on our 2027 board. CDPR\'s next new release is <a href="{href("games/the-witcher-3-songs-of-the-past.html", 0)}">The Witcher 3: Songs of the Past</a> in 2027.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>Is Cyberpunk 2077 on Switch 2?</h2></div>'
           f'<p>Yes. Cyberpunk 2077: Ultimate Edition, with the Phantom Liberty expansion, launched on Switch 2 on 5 June 2025, the console\'s launch day. Other picks on Switch 2 or Switch: {e(_and(_cp_on("switch")))}.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>What games are like Cyberpunk 2077 on PS5 and Xbox?</h2></div>'
           f'<p>PS5: {e(_and(_cp_on("ps5")))}. Xbox: {e(_and(_cp_on("xbox")))}.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>Related pages and tools</h2></div><ul>'
           f'<li><a href="{href("games-like-the-witcher-3.html", 0)}">Games like The Witcher 3</a>: CDPR\'s fantasy RPG and Witcher 4 date</li>'
           f'<li><a href="{href("games/exodus.html", 0)}">Exodus release date</a> and countdown</li>'
           f'<li><a href="{href("games-like-baldurs-gate-3.html", 0)}">Games like Baldur\'s Gate 3</a>: choice-heavy RPGs</li>'
           f'<li><a href="{href("games-like-mass-effect.html", 0)}">Games like Mass Effect</a>: squad-based space RPGs and Mass Effect 5 news</li>'
           f'<li><a href="{href("release-clashes-2027.html", 0)}">2027 release clash finder</a></li></ul></div></section>')
cp_faq = [("What games are like Cyberpunk 2077?", _and([x[0] for x in LIKE_CP]) + "."),
          ("When does Cyberpunk 2 come out?", "There is no date. CD Projekt Red says it is in pre-production and that pre-production to release takes four to five years on average, so it is not expected before 2028."),
          ("Is Cyberpunk 2077 on Switch 2?", "Yes. Cyberpunk 2077: Ultimate Edition launched on Switch 2 on 5 June 2025."),
          ("What is the closest game to Cyberpunk 2077?", "Deus Ex: Mankind Divided for augmentations and hacking, and The Outer Worlds 2 for a first-person RPG with choices."),
          ("What sci-fi RPGs come out in 2027?", _and([g["title"] + " (" + nice_date(g) + ")" for g in _cp_soon]) + ".")]
page("games-like-cyberpunk-2077.html", "Games Like Cyberpunk 2077: 10 Picks & Cyberpunk 2 Date",
     "Games like Cyberpunk 2077 on PS5, Xbox, Switch 2 and PC: Deus Ex, The Outer Worlds 2, Ghostrunner 2, plus 2027 sci-fi like Exodus and the Cyberpunk 2 timeline.",
     cp_body, 0, cp_faq, crumbs=[("Home", DOMAIN + "/"), ("Every RPG of 2027", canon("rpgs-2027.html")), ("Games like Cyberpunk 2077", canon("games-like-cyberpunk-2077.html"))])

# ---------------- GAMES LIKE PERSONA 5 (27 Nov 2026, demand: "games like persona 5", "persona 6 release date", "persona 4 revival release date", DEMAND N54) ----------------
# Evidence: GamesRadar+ "games like Persona 5", Gfinity "games to play while waiting for Persona 4 Revival", Wccftech "Persona 4 Revival, Fable... 2027 most stacked RPG year", RPG Site 2027 RPG list, TurnBasedLovers upcoming JRPGs 2026-2027.
# Facts: Persona 4 Revival date from games.json (Atlus). Persona 6 not announced by Atlus (OpenCritic teaser report = single source, not used).
LIKE_PS = [
    ("Metaphor: ReFantazio", "PS5, PS4, Xbox Series X|S, PC", "From the Persona team at Atlus: a fantasy election story with the same calendar, bonds and turn-based battles.", "ps5 ps4 xbox pc", "turn social story"),
    ("Persona 3 Reload", "PS5, PS4, Xbox Series X|S, Xbox One, PC, Switch 2", "The full remake of Persona 3: school days, the Dark Hour and a sharp modern look.", "switch ps5 ps4 xbox pc", "turn social story"),
    ("Persona 5 Royal", "PS5, PS4, Xbox Series X|S, Xbox One, Switch, PC", "If you only played the original, Royal adds a new semester, a new character and lots of fixes.", "switch ps5 ps4 xbox pc", "turn social story"),
    ("Shin Megami Tensei V: Vengeance", "PS5, PS4, Xbox Series X|S, Xbox One, Switch, PC", "Persona's darker parent series: demon fusing and harder turn-based fights, less school life.", "switch ps5 ps4 xbox pc", "turn"),
    ("Clair Obscur: Expedition 33", "PS5, Xbox Series X|S, PC", "A stylish turn-based RPG with timed dodges and parries, and a story that hits hard.", "ps5 xbox pc", "turn story"),
    ("Fire Emblem: Three Houses", "Switch (plays on Switch 2)", "Teach a class at a military academy, build bonds, then lead them in tactical battles.", "switch", "social turn story"),
    ("Like a Dragon: Infinite Wealth", "PS5, PS4, Xbox Series X|S, Xbox One, PC", "Turn-based fights, a lovable party and endless side activities, from the Yakuza team.", "ps5 ps4 xbox pc", "turn social story"),
    ("Persona 5 Tactica", "PS5, PS4, Xbox Series X|S, Xbox One, Switch, PC", "The Phantom Thieves in a shorter tactics game. Good for P5 fans who want more of the cast.", "switch ps5 ps4 xbox pc", "turn"),
    ("Danganronpa Decadence", "Switch (plays on Switch 2)", "School-set murder mysteries with class trials. All the story and style of Persona, no battles.", "switch", "story"),
    ("Tokyo Xanadu eX+", "PS4, PC (plays on PS5)", "Fast action RPG with Persona-style school days in Tokyo and dungeons in another world.", "ps5 ps4 pc", "social story"),
]
_PS_LABEL = {"turn": "Turn-based battles", "social": "School life and bonds", "story": "Story and style"}
PS_SOON = ["persona-4-revival", "danganronpa-2x2", "fate-extra-record", "romancing-saga-3-destinies-united", "eternal-anima", "atelier-karia", "stranger-than-heaven"]
_ps_soon = sorted([g for g in GAMES if g["slug"] in PS_SOON], key=lambda g: (g["month"] or 13, g["date"] or "9999"))
_ps_p4 = next((g for g in GAMES if g["slug"] == "persona-4-revival"), None)
def _ps_on(tag): return [x[0] for x in LIKE_PS if tag in x[3].split()]
_ps_p4d = nice_date(_ps_p4) if _ps_p4 else "2027"
_ps_quick = ("The best games like Persona 5 are Metaphor: ReFantazio (from the same team), Persona 3 Reload, Persona 5 Royal, Clair Obscur: Expedition 33 and Like a Dragon: Infinite Wealth. "
             f"The next Persona is Persona 4 Revival on {_ps_p4d}. Persona 6 has not been announced.")
ps_body = (f'<header class="hero"><div class="wrap"><span class="kicker">Games like Persona 5</span>'
           f'<h1>Games like Persona 5:<br><span class="amber">stylish JRPGs now, and Persona in 2027.</span></h1>'
           f'<p class="lead">Turn-based and school-life JRPGs on PS5, Xbox, Switch 2 and PC, filtered by what you loved about Persona, plus every 2027 JRPG and the Persona 4 Revival countdown.</p>'
           f'<p class="muted" style="margin:0">Last checked {e(UPDATED)} · {len(LIKE_PS)} picks out now · {len(_ps_soon)} coming in 2027</p></div></header>'
           f'<section><div class="wrap"><div class="out" style="margin-bottom:12px"><div class="row"><span><strong>Quick answer:</strong> {e(_ps_quick)}</span></div></div>'
           f'<div class="tool" id="er-tool" style="margin-bottom:24px"><h2 style="font-size:1.5rem;margin-top:0">Which game like Persona 5 should I play?</h2>'
           f'<p class="muted">Pick your platform and what you loved most. Your choice is remembered on this device.</p>{_like_chips(_PS_LABEL, "What you loved")}'
           f'<p class="mono amber" id="er-count" aria-live="polite" style="margin:12px 0 0">{len(LIKE_PS)} games</p></div>'
           f'<div class="sec-head"><h2>What games are like Persona 5?</h2><span class="muted">out now</span></div>'
           f'<div class="out" id="er-list" style="margin-bottom:10px">{_like_rows(LIKE_PS, _PS_LABEL)}</div><p class="empty" id="er-none" hidden>No pick matches both. Try "Anything".</p></div></section>'
           + AD.format("ps-mid") +
           f'<section><div class="wrap"><div class="sec-head"><h2>What JRPGs like Persona come out in 2027?</h2><span class="muted">{len(_ps_soon)}</span></div>'
           f'<div class="out" style="margin-bottom:10px">{"".join(_er_srow(g) for g in _ps_soon)}</div>{_like_cd(_ps_p4)}'
           f'<p class="muted">2027 is a huge JRPG year. See <a href="{href("rpgs-2027.html", 0)}">every RPG of 2027</a> for the full list.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>When does Persona 4 Revival come out?</h2></div>'
           f'<p>On {e(_ps_p4d)}, on {e(", ".join(_ps_p4["platforms"]) if _ps_p4 else "PS5, Xbox Series X|S, PC and Switch 2")}. It is a full remake of Persona 4 from Atlus. See our <a href="{href("games/persona-4-revival.html", 0)}">Persona 4 Revival page</a> for every confirmed detail and what else launches that week.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>When does Persona 6 come out?</h2></div>'
           f'<p>Atlus has not announced Persona 6, so there is no date or platform list. Its next Persona release is Persona 4 Revival. We will add Persona 6 to the board the day Atlus reveals it.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>What games are like Persona on Switch 2?</h2></div>'
           f'<p>Persona 3 Reload has a native Switch 2 version, and Persona 4 Revival is coming to Switch 2. These also play on Switch 2 through the Switch versions: {e(_and([x[0] for x in LIKE_PS if "Switch" in x[1] and "Switch 2" not in x[1]]))}.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>What games are like Persona on PS5 and Xbox?</h2></div>'
           f'<p>PS5: {e(_and(_ps_on("ps5")))}. Xbox: {e(_and(_ps_on("xbox")))}.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>Related pages and tools</h2></div><ul>'
           f'<li><a href="{href("games/persona-4-revival.html", 0)}">Persona 4 Revival release date</a> and countdown</li>'
           f'<li><a href="{href("games-like-final-fantasy.html", 0)}">Games like Final Fantasy</a>: JRPGs and the FF7 Revelation countdown</li>'
           f'<li><a href="{href("games-like-pokemon.html", 0)}">Games like Pokémon</a>: turn-based monster tamers</li>'
           f'<li><a href="{href("months/february-2027.html", 0)}">Games coming out in February 2027</a></li>'
           f'<li><a href="{href("backlog-planner-2027.html", 0)}">2027 backlog planner</a>: fit 80-hour JRPGs around new releases</li></ul></div></section>')
ps_faq = [("What games are like Persona 5?", _and([x[0] for x in LIKE_PS]) + "."),
          ("When does Persona 4 Revival come out?", f"{_ps_p4d}, on PS5, Xbox Series X|S, PC and Switch 2."),
          ("Is Persona 6 announced?", "No. Atlus has not announced Persona 6, so it has no release date."),
          ("What is the closest game to Persona 5?", "Metaphor: ReFantazio, made by the Persona 5 director and team at Atlus, with the same calendar, bonds and turn-based battles."),
          ("What JRPGs come out in 2027?", _and([g["title"] + " (" + nice_date(g) + ")" for g in _ps_soon]) + ".")]
page("games-like-persona.html", "Games Like Persona 5: 10 JRPGs & Persona in 2027",
     "Games like Persona 5 on PS5, Xbox, Switch 2 and PC: Metaphor: ReFantazio, Persona 3 Reload, Clair Obscur, plus Persona 4 Revival's 2027 date and Persona 6 news.",
     ps_body, 0, ps_faq, crumbs=[("Home", DOMAIN + "/"), ("Every RPG of 2027", canon("rpgs-2027.html")), ("Games like Persona 5", canon("games-like-persona.html"))])

# ---------------- GAMES LIKE RESIDENT EVIL (27 Nov 2026, demand: "games like resident evil", "games like resident evil requiem", "resident evil 10 release date", DEMAND N58) ----------------
# Evidence: GamesRadar+ "10 games like Resident Evil to scare you silly in 2026" (US/UK/AU), SVG + AOL "5 best games like Resident Evil Requiem", Eneba hub, Ranker survival horror 2020s.
# Facts: RE Requiem + RE7 + Village on Switch 2 27 Feb 2026 (VGC, Nintendo Life, Kotaku). RE Veronica 2027 PS5/Xbox/Switch 2/PC (Capcom IR 8 Jun 2026, Gematsu, Game Informer). RE10 not announced; 2029 target is a rumour (GamingBolt, PSU, NoobFeed).
LIKE_RE = [
    ("Resident Evil Requiem", "PS5, Xbox Series X|S, PC, Switch 2", "The newest main Resident Evil (February 2026): Grace Ashcroft's survival horror with Leon in the mix.", "switch ps5 xbox pc", "survival action"),
    ("Resident Evil 4", "PS5, PS4, Xbox Series X|S, PC", "Capcom's remake of the action-horror classic: Leon, the village and the castle, rebuilt in full.", "ps5 ps4 xbox pc", "action"),
    ("Resident Evil Village", "PS5, PS4, Xbox Series X|S, Xbox One, PC, Switch 2", "First-person gothic horror with a castle, a doll house and a lot of werewolves.", "switch ps5 ps4 xbox pc", "survival action"),
    ("Dead Space", "PS5, Xbox Series X|S, PC", "The 2023 remake: limb-cutting sci-fi horror on a dead mining ship, with no loading screens.", "ps5 xbox pc", "survival action"),
    ("Silent Hill f", "PS5, Xbox Series X|S, PC", "Konami's 2025 Silent Hill set in 1960s Japan: psychological horror with close-up melee fights.", "ps5 xbox pc", "psych"),
    ("Alan Wake 2", "PS5, Xbox Series X|S, PC", "Remedy's story-heavy survival horror split between an FBI agent and a writer trapped in a nightmare.", "ps5 xbox pc", "psych survival"),
    ("The Evil Within 2", "PS4, Xbox One, PC (plays on PS5 and Xbox Series X|S)", "From the creator of Resident Evil: a semi-open town, scarce ammo and stealth when you run dry.", "ps5 ps4 xbox pc", "survival"),
    ("Alien: Isolation", "PS4, Xbox One, Switch, PC (plays on PS5, Xbox Series X|S and Switch 2)", "One alien you cannot kill, hunting you through a space station. Pure tension.", "switch ps5 ps4 xbox pc", "psych"),
    ("Signalis", "PS4, Xbox One, Switch, PC (plays on PS5, Xbox Series X|S and Switch 2)", "An indie love letter to classic Resident Evil: tank-style exploring, tiny inventory, save rooms.", "switch ps5 ps4 xbox pc", "survival psych"),
    ("The Callisto Protocol", "PS5, PS4, Xbox Series X|S, Xbox One, PC", "Brutal space-prison horror from Dead Space's co-creator, heavy on melee.", "ps5 ps4 xbox pc", "action"),
]
_RE_LABEL = {"survival": "Classic survival horror", "action": "Action horror", "psych": "Psychological horror"}
RE_SOON = ["resident-evil-veronica", "until-dawn-2", "brokenlore-ascend", "trainwatch", "baptiste", "psycho-dead", "into-the-dead-our-darkest-days", "becrowned", "ontos"]
_re_soon = sorted([g for g in GAMES if g["slug"] in RE_SOON], key=lambda g: (g["month"] or 13, g["date"] or "9999"))
_re_ud = next((g for g in GAMES if g["slug"] == "until-dawn-2"), None)
_re_v = next((g for g in GAMES if g["slug"] == "resident-evil-veronica"), None)
def _re_on(tag): return [x[0] for x in LIKE_RE if tag in x[3].split()]
_re_quick = ("The best games like Resident Evil are Resident Evil Requiem, the Resident Evil 4 remake, Dead Space, Silent Hill f and Alan Wake 2. "
             "The next Resident Evil is Resident Evil Veronica, a Code: Veronica remake due in 2027 on PS5, Xbox Series X|S, Switch 2 and PC. Resident Evil 10 has not been announced.")
re_body = (f'<header class="hero"><div class="wrap"><span class="kicker">Games like Resident Evil</span>'
           f'<h1>Games like Resident Evil:<br><span class="amber">survival horror now, and Veronica in 2027.</span></h1>'
           f'<p class="lead">Survival horror games on PS5, Xbox, Switch 2 and PC, filtered by the kind of scare you like, plus every horror game dated for 2027 and what is next for Resident Evil.</p>'
           f'<p class="muted" style="margin:0">Last checked {e(UPDATED)} · {len(LIKE_RE)} picks out now · {len(_re_soon)} coming in 2027</p></div></header>'
           f'<section><div class="wrap"><div class="out" style="margin-bottom:12px"><div class="row"><span><strong>Quick answer:</strong> {e(_re_quick)}</span></div></div>'
           f'<div class="tool" id="er-tool" style="margin-bottom:24px"><h2 style="font-size:1.5rem;margin-top:0">Which game like Resident Evil should I play?</h2>'
           f'<p class="muted">Pick your platform and the kind of horror you want. Your choice is remembered on this device.</p>{_like_chips(_RE_LABEL, "Kind of horror")}'
           f'<p class="mono amber" id="er-count" aria-live="polite" style="margin:12px 0 0">{len(LIKE_RE)} games</p></div>'
           f'<div class="sec-head"><h2>What games are like Resident Evil?</h2><span class="muted">out now</span></div>'
           f'<div class="out" id="er-list" style="margin-bottom:10px">{_like_rows(LIKE_RE, _RE_LABEL)}</div><p class="empty" id="er-none" hidden>No pick matches both. Try "Anything".</p></div></section>'
           + AD.format("re-mid") +
           f'<section><div class="wrap"><div class="sec-head"><h2>What survival horror games come out in 2027?</h2><span class="muted">{len(_re_soon)}</span></div>'
           f'<div class="out" style="margin-bottom:10px">{"".join(_er_srow(g) for g in _re_soon)}</div>{_like_cd(_re_ud)}'
           f'<p class="muted">Until Dawn 2 is the first big horror game of 2027. See <a href="{href("horror-games-2027.html", 0)}">every horror game of 2027</a> with a console filter.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>When does Resident Evil Veronica come out?</h2></div>'
           f'<p>In {e(nice_date(_re_v) if _re_v else "2027")}, on PS5, Xbox Series X|S, Switch 2 and PC. Capcom announced it in June 2026 as a full remake of Resident Evil Code: Veronica, with Claire and Chris Redfield, but has not given a month or day. Treat any exact date you see as a guess until Capcom confirms it. Our <a href="{href("games/resident-evil-veronica.html", 0)}">Resident Evil Veronica page</a> has every confirmed detail.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>When does Resident Evil 10 come out?</h2></div>'
           f'<p>Capcom has not announced Resident Evil 10. Its producers have said Requiem closed one long-term plan for the series, and reports of a 2029 target come from leaks and rumours, not Capcom (GamingBolt, PSU). The next Resident Evil you can count on is Veronica in 2027.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>Which Resident Evil games are on Switch 2?</h2></div>'
           f'<p>Resident Evil 7, Resident Evil Village and Resident Evil Requiem all launched on Switch 2 on 27 February 2026, and Resident Evil Veronica is coming to Switch 2 in 2027. Other picks you can play on Switch or Switch 2: {e(_and([x for x in _re_on("switch") if "Resident" not in x]))}.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>What games are like Resident Evil on PS5 and Xbox?</h2></div>'
           f'<p>PS5: {e(_and(_re_on("ps5")))}. Xbox: {e(_and(_re_on("xbox")))}.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>Related pages and tools</h2></div><ul>'
           f'<li><a href="{href("horror-games-2027.html", 0)}">Every horror game of 2027</a>, with a console filter</li>'
           f'<li><a href="{href("games/until-dawn-2.html", 0)}">Until Dawn 2 release date</a> and countdown</li>'
           f'<li><a href="{href("games-like-silent-hill.html", 0)}">Games like Silent Hill</a>: psychological horror and the Silent Hill 1 remake</li>'
           f'<li><a href="{href("release-clashes-2027.html", 0)}">2027 release clash finder</a></li></ul></div></section>')
re_faq = [("What games are like Resident Evil?", _and([x[0] for x in LIKE_RE]) + "."),
          ("When does Resident Evil Veronica come out?", "In 2027, on PS5, Xbox Series X|S, Switch 2 and PC. Capcom has not given a month or day yet."),
          ("Is Resident Evil 10 announced?", "No. Capcom has not announced Resident Evil 10. A 2029 target has been reported only as a rumour."),
          ("Is Resident Evil Requiem on Switch 2?", "Yes. Resident Evil Requiem, Resident Evil 7 and Resident Evil Village all launched on Switch 2 on 27 February 2026."),
          ("What survival horror games come out in 2027?", _and([g["title"] + " (" + nice_date(g) + ")" for g in _re_soon]) + ".")]
page("games-like-resident-evil.html", "Games Like Resident Evil: 10 Horror Picks & RE in 2027",
     "Games like Resident Evil on PS5, Xbox, Switch 2 and PC: Requiem, RE4, Dead Space, Silent Hill f, plus 2027 horror like Until Dawn 2 and Resident Evil Veronica.",
     re_body, 0, re_faq, crumbs=[("Home", DOMAIN + "/"), ("Horror games of 2027", canon("horror-games-2027.html")), ("Games like Resident Evil", canon("games-like-resident-evil.html"))])

# ---------------- GAMES LIKE FINAL FANTASY (27 Nov 2026, demand: "games like final fantasy", "final fantasy 7 revelation release date", "final fantasy 17", DEMAND N58) ----------------
# Evidence: GamesRadar+ "10 games like Final Fantasy" (US/UK/AU), Digital Trends "best games like Final Fantasy", GamesRadar+/TechRadar best JRPGs 2026, Game Informer top RPGs Jul 2026.
# Facts: FF7 Revelation 8 Apr 2027 (PlayStation Blog, Game Informer, RPG Site). FF7 Remake Intergrade Switch 2/Xbox 22 Jan 2026 (Gematsu, RPG Site); Rebirth Switch 2/Xbox 3 Jun 2026 (Gematsu, RPG Site). FF17 not announced (only "teased" reports).
LIKE_FF = [
    ("Final Fantasy VII Rebirth", "PS5, Xbox Series X|S, PC, Switch 2", "Part two of the FF7 remake trilogy: a huge open world and real-time battles. Play it before Revelation.", "switch ps5 xbox pc", "action story open"),
    ("Final Fantasy VII Remake Intergrade", "PS5, Xbox Series X|S, PC, Switch 2", "Part one, set in Midgar, with the Yuffie episode. Out on Switch 2 and Xbox since January 2026.", "switch ps5 xbox pc", "action story"),
    ("Clair Obscur: Expedition 33", "PS5, Xbox Series X|S, PC", "A turn-based RPG with timed parries and a story fans compare to the best of classic Final Fantasy.", "ps5 xbox pc", "turn story"),
    ("Dragon Quest XI S: Echoes of an Elusive Age", "PS4, Xbox One, Switch, PC (plays on PS5, Xbox Series X|S and Switch 2)", "The classic JRPG at its warmest: turn-based fights and a 60-hour hero's journey.", "switch ps5 ps4 xbox pc", "turn story"),
    ("Final Fantasy Tactics: The Ivalice Chronicles", "PS5, PS4, Xbox Series X|S, Switch, Switch 2, PC", "The 2025 remaster of the tactics classic, with full voice acting and a new script option.", "switch ps5 ps4 xbox pc", "turn story"),
    ("Xenoblade Chronicles X: Definitive Edition", "Switch (plays on Switch 2)", "A giant open alien planet, mechs and real-time battles, from Monolith Soft, whose Xenoblade Genesis is due in 2027.", "switch", "action open"),
    ("Metaphor: ReFantazio", "PS5, PS4, Xbox Series X|S, PC", "From the Persona team: a fantasy kingdom, a royal election and press-turn battles.", "ps5 ps4 xbox pc", "turn story"),
    ("Octopath Traveler II", "PS5, PS4, Switch, PC", "Eight heroes, eight stories and a gorgeous pixel-art style, from the team that made Bravely Default.", "switch ps5 ps4 pc", "turn"),
    ("Tales of Arise", "PS5, PS4, Xbox Series X|S, Xbox One, PC", "Fast action combat and a close-knit party, the easy way into the Tales series.", "ps5 ps4 xbox pc", "action story"),
    ("Dragon Quest III HD-2D Remake", "PS5, Xbox Series X|S, Switch, PC", "The 1988 classic rebuilt in HD-2D: pick your party and go. Great for short sessions.", "switch ps5 xbox pc", "turn"),
]
_FF_LABEL = {"turn": "Turn-based", "action": "Action battles", "story": "Big story", "open": "Open world"}
FF_SOON = ["final-fantasy-vii-revelation", "kingdom-hearts-iv", "final-fantasy-xiv-evercold", "xenoblade-genesis", "romancing-saga-3-destinies-united", "terranigma", "eternal-anima", "persona-4-revival", "atelier-karia"]
_ff_soon = sorted([g for g in GAMES if g["slug"] in FF_SOON], key=lambda g: (g["month"] or 13, g["date"] or "9999"))
_ff_r = next((g for g in GAMES if g["slug"] == "final-fantasy-vii-revelation"), None)
_ff_kh = next((g for g in GAMES if g["slug"] == "kingdom-hearts-iv"), None)
def _ff_on(tag): return [x[0] for x in LIKE_FF if tag in x[3].split()]
_ff_rd = nice_date(_ff_r) if _ff_r else "8 April 2027"
_ff_quick = ("The best games like Final Fantasy are Final Fantasy VII Rebirth, Clair Obscur: Expedition 33, Dragon Quest XI S, Metaphor: ReFantazio and Octopath Traveler II. "
             f"The next big Final Fantasy is Final Fantasy VII Revelation on {_ff_rd}. Final Fantasy XVII has not been announced.")
ff_body = (f'<header class="hero"><div class="wrap"><span class="kicker">Games like Final Fantasy</span>'
           f'<h1>Games like Final Fantasy:<br><span class="amber">JRPGs now, FF7 Revelation in 2027.</span></h1>'
           f'<p class="lead">Final Fantasy-style RPGs on PS5, Xbox, Switch 2 and PC, filtered by battle style, plus every big JRPG dated for 2027 and the Final Fantasy VII Revelation countdown.</p>'
           f'<p class="muted" style="margin:0">Last checked {e(UPDATED)} · {len(LIKE_FF)} picks out now · {len(_ff_soon)} coming in 2027</p></div></header>'
           f'<section><div class="wrap"><div class="out" style="margin-bottom:12px"><div class="row"><span><strong>Quick answer:</strong> {e(_ff_quick)}</span></div></div>'
           f'<div class="tool" id="er-tool" style="margin-bottom:24px"><h2 style="font-size:1.5rem;margin-top:0">Which game like Final Fantasy should I play?</h2>'
           f'<p class="muted">Pick your platform and what you want most. Your choice is remembered on this device.</p>{_like_chips(_FF_LABEL, "What you want")}'
           f'<p class="mono amber" id="er-count" aria-live="polite" style="margin:12px 0 0">{len(LIKE_FF)} games</p></div>'
           f'<div class="sec-head"><h2>What games are like Final Fantasy?</h2><span class="muted">out now</span></div>'
           f'<div class="out" id="er-list" style="margin-bottom:10px">{_like_rows(LIKE_FF, _FF_LABEL)}</div><p class="empty" id="er-none" hidden>No pick matches both. Try "Anything".</p></div></section>'
           + AD.format("ff-mid") +
           f'<section><div class="wrap"><div class="sec-head"><h2>What JRPGs like Final Fantasy come out in 2027?</h2><span class="muted">{len(_ff_soon)}</span></div>'
           f'<div class="out" style="margin-bottom:10px">{"".join(_er_srow(g) for g in _ff_soon)}</div>{_like_cd(_ff_r)}'
           f'<p class="muted">See <a href="{href("rpgs-2027.html", 0)}">every RPG of 2027</a> for the full list, and <a href="{href("games-like-persona.html", 0)}">games like Persona 5</a> for school-life JRPGs.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>When does Final Fantasy VII Revelation come out?</h2></div>'
           f'<p>On {e(_ff_rd)}, on {e(", ".join(_ff_r["platforms"]) if _ff_r else "PS5, Xbox Series X|S, Switch 2 and PC")}, all on the same day. It is the third and final part of the Final Fantasy VII remake trilogy. Square Enix revealed the date at PlayStation\'s State of Play in September 2026. See our <a href="{href("games/final-fantasy-vii-revelation.html", 0)}">Final Fantasy VII Revelation page</a> for what else launches that week.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>Do I need to play Remake and Rebirth before Revelation?</h2></div>'
           f'<p>It is strongly recommended: Revelation continues the story straight from Rebirth. Both earlier parts are now on PS5, Xbox Series X|S, PC and Switch 2 (Remake Intergrade since 22 January 2026, Rebirth since 3 June 2026), so you can catch up on any of those before April.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>When does Final Fantasy XVII come out?</h2></div>'
           f'<p>Square Enix has not announced Final Fantasy XVII, so there is no date or platform list. Reports of teases are not an announcement. The next new Final Fantasy releases are Revelation and the Final Fantasy XIV expansion Evercold ({e(nice_date(next((g for g in GAMES if g["slug"] == "final-fantasy-xiv-evercold"), {"date": "2027-02-23", "window": "", "month": 2})) if any(g["slug"] == "final-fantasy-xiv-evercold" for g in GAMES) else "2027")}).</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>What games are like Final Fantasy on Switch 2?</h2></div>'
           f'<p>Switch 2 or Switch: {e(_and(_ff_on("switch")))}. Coming to Switch 2 in 2027: {e(_and([g["title"] for g in _ff_soon if "Switch 2" in g["platforms"]]))}.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>What games are like Final Fantasy on PS5 and Xbox?</h2></div>'
           f'<p>PS5: {e(_and(_ff_on("ps5")))}. Xbox: {e(_and(_ff_on("xbox")))}.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>Related pages and tools</h2></div><ul>'
           f'<li><a href="{href("games/final-fantasy-vii-revelation.html", 0)}">Final Fantasy VII Revelation release date</a> and countdown</li>'
           + (f'<li><a href="{href("games/kingdom-hearts-iv.html", 0)}">Kingdom Hearts 4 release window</a></li>' if _ff_kh else '') +
           f'<li><a href="{href("games-like-persona.html", 0)}">Games like Persona 5</a>: more JRPGs</li>'
           f'<li><a href="{href("backlog-planner-2027.html", 0)}">2027 backlog planner</a>: fit Rebirth in before Revelation</li></ul></div></section>')
ff_faq = [("What games are like Final Fantasy?", _and([x[0] for x in LIKE_FF]) + "."),
          ("When does Final Fantasy VII Revelation come out?", f"{_ff_rd}, on PS5, Xbox Series X|S, Switch 2 and PC."),
          ("Is Final Fantasy XVII announced?", "No. Square Enix has not announced Final Fantasy XVII, so it has no release date."),
          ("Do I need to play Rebirth before Revelation?", "Yes, it is recommended. Revelation continues straight from Rebirth, which is on PS5, Xbox Series X|S, PC and Switch 2."),
          ("What JRPGs come out in 2027?", _and([g["title"] + " (" + nice_date(g) + ")" for g in _ff_soon]) + ".")]
page("games-like-final-fantasy.html", "Games Like Final Fantasy: 10 JRPGs & FF7 Revelation Date",
     "Games like Final Fantasy on PS5, Xbox, Switch 2 and PC: FF7 Rebirth, Clair Obscur, Dragon Quest XI, plus 2027 JRPGs and the 8 April 2027 FF7 Revelation date.",
     ff_body, 0, ff_faq, crumbs=[("Home", DOMAIN + "/"), ("Every RPG of 2027", canon("rpgs-2027.html")), ("Games like Final Fantasy", canon("games-like-final-fantasy.html"))])

# ---------------- GAMES LIKE MASS EFFECT (28 Nov 2026, demand: "games like mass effect", "mass effect 5 release date", DEMAND N62) ----------------
# Evidence: GamesRadar+ "Games like Mass Effect" (US/UK/AU), Game Rant, G2A, Eneba "15 best games like Mass Effect", GamingBible "Every update on Mass Effect 5" (Mar 2026), PC Gamer (BioWare "not a lot of time for tease"), NoobFeed.
# Facts: Mass Effect 5 in development at BioWare, no date (PC Gamer, GamingBible, NoobFeed). Starfield PS5 7 Apr 2026 (Bethesda.net, RPG Site, GamesRadar+). Exodus 7 Apr 2027 (games.json; Archetype Entertainment, led by ex-BioWare Mass Effect veterans).
LIKE_ME = [
    ("Mass Effect Legendary Edition", "PS4, Xbox One, PC (plays on PS5 and Xbox Series X|S)", "The whole Shepard trilogy remastered in one pack. If you have only played one, start here.", "ps5 ps4 xbox pc", "squad story shooter"),
    ("Starfield", "Xbox Series X|S, PC, PS5", "Bethesda's huge space RPG: build a ship, join factions and land on hundreds of planets. On PS5 since 7 April 2026.", "ps5 xbox pc", "explore story"),
    ("Star Wars: Knights of the Old Republic", "Switch, PC, Xbox (plays on Xbox Series X|S and Switch 2)", "BioWare's earlier space RPG and the blueprint for Mass Effect: a party, a moral choice system and a famous twist.", "switch xbox pc", "squad story"),
    ("The Outer Worlds 2", "PS5, Xbox Series X|S, PC", "Obsidian's funny sci-fi RPG with companions, factions and lots of ways to talk your way out of trouble.", "ps5 xbox pc", "squad story shooter"),
    ("Cyberpunk 2077", "PS5, Xbox Series X|S, PC, Switch 2", "First-person sci-fi RPG in Night City with big story choices and a strong Phantom Liberty expansion.", "switch ps5 xbox pc", "story shooter"),
    ("Dragon Age: The Veilguard", "PS5, Xbox Series X|S, PC", "BioWare's latest RPG: a fantasy setting, but the same companion missions and loyalty system Mass Effect fans love.", "ps5 xbox pc", "squad story"),
    ("Star Wars Outlaws", "PS5, Xbox Series X|S, PC, Switch 2", "An open-world Star Wars adventure with a ship, planets to explore and a scoundrel's story.", "switch ps5 xbox pc", "explore"),
    ("No Man's Sky", "PS5, PS4, Xbox Series X|S, Xbox One, PC, Switch, Switch 2", "Endless planets, ship upgrades and base building. Less story, much more exploring.", "switch ps5 ps4 xbox pc", "explore"),
    ("Baldur's Gate 3", "PS5, Xbox Series X|S, PC", "Not sci-fi, but the best companion romances and party banter in years, with choices that change the ending.", "ps5 xbox pc", "squad story"),
    ("Mass Effect: Andromeda", "PS4, Xbox One, PC (plays on PS5 and Xbox Series X|S)", "The 2017 spin-off: weaker story, but the best combat and planet exploring in the series, and often very cheap.", "ps5 ps4 xbox pc", "squad explore shooter"),
]
_ME_LABEL = {"squad": "Squad and companions", "story": "Big story choices", "shooter": "Cover shooting", "explore": "Space exploring"}
ME_SOON = ["exodus", "the-expanse-osiris-reborn", "squadron-42", "metro-2039", "ontos", "armatus", "warhammer-40-000-dark-heresy"]
_me_soon = sorted([g for g in GAMES if g["slug"] in ME_SOON], key=lambda g: (g["month"] or 13, g["date"] or "9999"))
_me_ex = next((g for g in GAMES if g["slug"] == "exodus"), None)
def _me_on(tag): return [x[0] for x in LIKE_ME if tag in x[3].split()]
_me_exd = nice_date(_me_ex) if _me_ex else "7 April 2027"
_me_quick = ("The best games like Mass Effect are the Mass Effect Legendary Edition, Starfield, Knights of the Old Republic, The Outer Worlds 2 and Cyberpunk 2077. "
             f"Mass Effect 5 is in development at BioWare but has no release date. The closest new game is Exodus, from former Mass Effect developers, on {_me_exd}.")
me_body = (f'<header class="hero"><div class="wrap"><span class="kicker">Games like Mass Effect</span>'
           f'<h1>Games like Mass Effect:<br><span class="amber">space RPGs now, and Exodus in 2027.</span></h1>'
           f'<p class="lead">Sci-fi RPGs with squads, choices and space travel on PS5, Xbox, Switch 2 and PC, filtered by what you loved about Mass Effect, plus every 2027 sci-fi game and the latest on Mass Effect 5.</p>'
           f'<p class="muted" style="margin:0">Last checked {e(UPDATED)} · {len(LIKE_ME)} picks out now · {len(_me_soon)} coming in 2027</p></div></header>'
           f'<section><div class="wrap"><div class="out" style="margin-bottom:12px"><div class="row"><span><strong>Quick answer:</strong> {e(_me_quick)}</span></div></div>'
           f'<div class="tool" id="er-tool" style="margin-bottom:24px"><h2 style="font-size:1.5rem;margin-top:0">Which game like Mass Effect should I play?</h2>'
           f'<p class="muted">Pick your platform and the part of Mass Effect you miss most. Your choice is remembered on this device.</p>{_like_chips(_ME_LABEL, "What you loved")}'
           f'<p class="mono amber" id="er-count" aria-live="polite" style="margin:12px 0 0">{len(LIKE_ME)} games</p></div>'
           f'<div class="sec-head"><h2>What games are like Mass Effect?</h2><span class="muted">out now</span></div>'
           f'<div class="out" id="er-list" style="margin-bottom:10px">{_like_rows(LIKE_ME, _ME_LABEL)}</div><p class="empty" id="er-none" hidden>No pick matches both. Try "Anything".</p></div></section>'
           + AD.format("me-mid") +
           f'<section><div class="wrap"><div class="sec-head"><h2>What sci-fi games like Mass Effect come out in 2027?</h2><span class="muted">{len(_me_soon)}</span></div>'
           f'<div class="out" style="margin-bottom:10px">{"".join(_er_srow(g) for g in _me_soon)}</div>{_like_cd(_me_ex)}'
           f'<div class="sec-head" style="margin-top:28px"><h2>Is Exodus the new Mass Effect?</h2></div>'
           f'<p>It is the closest thing coming. <a href="{href("games/exodus.html", 0)}">Exodus</a> is a third-person sci-fi RPG from Archetype Entertainment, a studio led by former BioWare developers who worked on Mass Effect, and it comes out on {e(_me_exd)} on PS5, Xbox Series X|S and PC. You lead a crew, make choices that change the story and travel between stars, where the years lost to space travel change the worlds you come back to. It is a new universe, not a Mass Effect game.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>When does Mass Effect 5 come out?</h2></div>'
           f'<p>There is no release date. BioWare confirmed the next Mass Effect is in development and has shown only short teasers (December 2020 and November 2023); the studio has said it does not want to tease the game until it is ready (PC Gamer). No platforms, year or trailer with gameplay have been announced, so any 2027 or 2028 date you see is a guess. We will add it to the board the day BioWare gives a year.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>What is The Expanse: Osiris Reborn?</h2></div>'
           f'<p>An action RPG from Owlcat Games set in The Expanse universe, due in {e(nice_date(next((g for g in GAMES if g["slug"] == "the-expanse-osiris-reborn"), {"date": None, "window": "Spring 2027", "month": 4})))} on PS5, Xbox Series X|S and PC. Expect a squad of companions and story choices, the two things fans most often miss from Mass Effect. See our <a href="{href("games-like-cyberpunk-2077.html", 0)}">games like Cyberpunk 2077</a> page for more 2027 sci-fi.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>What games are like Mass Effect on PS5, Xbox and Switch 2?</h2></div>'
           f'<p>PS5: {e(_and(_me_on("ps5")))}. Xbox: {e(_and(_me_on("xbox")))}. Switch or Switch 2: {e(_and(_me_on("switch")))}. The Mass Effect trilogy itself is not on Switch or Switch 2.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>Related pages and tools</h2></div><ul>'
           f'<li><a href="{href("games/exodus.html", 0)}">Exodus release date</a> and countdown</li>'
           f'<li><a href="{href("games-like-cyberpunk-2077.html", 0)}">Games like Cyberpunk 2077</a>: more sci-fi RPGs</li>'
           f'<li><a href="{href("games-like-baldurs-gate-3.html", 0)}">Games like Baldur\'s Gate 3</a>: companion-heavy RPGs and 2027 CRPGs</li>'
           f'<li><a href="{href("rpgs-2027.html", 0)}">Every RPG of 2027</a></li></ul></div></section>')
me_faq = [("What games are like Mass Effect?", _and([x[0] for x in LIKE_ME]) + "."),
          ("When does Mass Effect 5 come out?", "There is no release date. BioWare says the next Mass Effect is in development, but no year or platforms have been announced."),
          ("Is Exodus made by Mass Effect developers?", f"Yes. Exodus is made by Archetype Entertainment, led by former BioWare Mass Effect developers. It comes out on {_me_exd} on PS5, Xbox Series X|S and PC."),
          ("Is Mass Effect on Switch 2?", "No. The Mass Effect trilogy is on PS4, Xbox One and PC, and plays on PS5 and Xbox Series X|S."),
          ("What sci-fi RPGs come out in 2027?", _and([g["title"] + " (" + nice_date(g) + ")" for g in _me_soon]) + ".")]
page("games-like-mass-effect.html", "Games Like Mass Effect: 10 Space RPGs & Exodus in 2027",
     "Games like Mass Effect on PS5, Xbox, Switch 2 and PC: Starfield, KOTOR, The Outer Worlds 2, plus 2027 sci-fi RPGs like Exodus and the latest on Mass Effect 5.",
     me_body, 0, me_faq, crumbs=[("Home", DOMAIN + "/"), ("Every RPG of 2027", canon("rpgs-2027.html")), ("Games like Mass Effect", canon("games-like-mass-effect.html"))])

# ---------------- GAMES LIKE SILENT HILL (28 Nov 2026, demand: "games like silent hill", "games like silent hill 2/f", "silent hill remake release date", DEMAND N62) ----------------
# Evidence: ComicBook "best horror games like Silent Hill 2", SVG, G2A (x3 incl. SH f / SH2 remake), Gfinity, gaming.net (SH f, SH2), GamingScan.
# Facts: Townfall 24 Sep 2026 PS5/PC (PlayStation Blog, Konami, GamesRadar+, GamingBolt). SH2 remake on Xbox Series X|S + Switch 2 Nov 2025 (Push Square, Pure Xbox). SH1 remake (Bloober) in development, 2027 = report/leak only (PSU, Notebookcheck, Beebom).
LIKE_SH = [
    ("Silent Hill 2", "PS5, PC, Xbox Series X|S, Switch 2", "Bloober Team's 2024 remake of the classic: fog, grief and Pyramid Head. On Xbox and Switch 2 since November 2025.", "switch ps5 xbox pc", "psych fog"),
    ("Silent Hill f", "PS5, Xbox Series X|S, PC", "Konami's 2025 Silent Hill in 1960s rural Japan: a beautiful, gory nightmare with close-up melee fights.", "ps5 xbox pc", "psych action"),
    ("Silent Hill: Townfall", "PS5, PC", "The newest Silent Hill (24 September 2026): a first-person story in a foggy Scottish town, from the makers of Observation.", "ps5 pc", "psych fog"),
    ("Alan Wake 2", "PS5, Xbox Series X|S, PC", "Remedy's surreal horror where a writer's story rewrites the world around him. The closest thing to Silent Hill's dream logic.", "ps5 xbox pc", "psych action"),
    ("Signalis", "PS4, Xbox One, Switch, PC (plays on PS5, Xbox Series X|S and Switch 2)", "Retro survival horror with Silent Hill-style puzzles, radio static and a story you piece together.", "switch ps5 ps4 xbox pc", "psych retro"),
    ("Cronos: The New Dawn", "PS5, Xbox Series X|S, PC", "Bloober Team's 2025 sci-fi survival horror, made by the team now remaking the first Silent Hill.", "ps5 xbox pc", "action"),
    ("The Medium", "PS5, Xbox Series X|S, PC", "Bloober Team again, with music by Silent Hill composer Akira Yamaoka. You explore two worlds at once.", "ps5 xbox pc", "psych"),
    ("Layers of Fear", "PS5, Xbox Series X|S, PC", "A walk through a painter's collapsing mind. Pure psychological horror with no combat.", "ps5 xbox pc", "psych"),
    ("Alien: Isolation", "PS4, Xbox One, Switch, PC (plays on PS5, Xbox Series X|S and Switch 2)", "One alien you cannot kill, hunting you through a space station. Hide, listen and run.", "switch ps5 ps4 xbox pc", "action"),
    ("Resident Evil Village", "PS5, PS4, Xbox Series X|S, Xbox One, PC, Switch 2", "More action than Silent Hill, but its doll-house section is one of the scariest things in modern horror.", "switch ps5 ps4 xbox pc", "action"),
]
_SH_LABEL = {"psych": "Psychological horror", "fog": "Fog and small towns", "action": "Fights back", "retro": "Retro style"}
SH_SOON = ["becrowned", "until-dawn-2", "brokenlore-ascend", "trainwatch", "baptiste", "psycho-dead", "resident-evil-veronica", "ontos", "neverway"]
_sh_soon = sorted([g for g in GAMES if g["slug"] in SH_SOON], key=lambda g: (g["month"] or 13, g["date"] or "9999"))
_sh_ud = next((g for g in GAMES if g["slug"] == "until-dawn-2"), None)
def _sh_on(tag): return [x[0] for x in LIKE_SH if tag in x[3].split()]
_sh_quick = ("The best games like Silent Hill are the Silent Hill 2 remake, Silent Hill f, Silent Hill: Townfall, Alan Wake 2 and Signalis. "
             "Bloober Team's remake of the first Silent Hill is in development but has no release date; reports of 2027 are not confirmed by Konami.")
sh_body = (f'<header class="hero"><div class="wrap"><span class="kicker">Games like Silent Hill</span>'
           f'<h1>Games like Silent Hill:<br><span class="amber">psychological horror now, and in 2027.</span></h1>'
           f'<p class="lead">Psychological horror games on PS5, Xbox, Switch 2 and PC, filtered by the kind of fear you want, plus every 2027 horror game and what is next for Silent Hill.</p>'
           f'<p class="muted" style="margin:0">Last checked {e(UPDATED)} · {len(LIKE_SH)} picks out now · {len(_sh_soon)} coming in 2027</p></div></header>'
           f'<section><div class="wrap"><div class="out" style="margin-bottom:12px"><div class="row"><span><strong>Quick answer:</strong> {e(_sh_quick)}</span></div></div>'
           f'<div class="tool" id="er-tool" style="margin-bottom:24px"><h2 style="font-size:1.5rem;margin-top:0">Which game like Silent Hill should I play?</h2>'
           f'<p class="muted">Pick your platform and the kind of horror you want. Your choice is remembered on this device.</p>{_like_chips(_SH_LABEL, "Kind of horror")}'
           f'<p class="mono amber" id="er-count" aria-live="polite" style="margin:12px 0 0">{len(LIKE_SH)} games</p></div>'
           f'<div class="sec-head"><h2>What games are like Silent Hill?</h2><span class="muted">out now</span></div>'
           f'<div class="out" id="er-list" style="margin-bottom:10px">{_like_rows(LIKE_SH, _SH_LABEL)}</div><p class="empty" id="er-none" hidden>No pick matches both. Try "Anything".</p></div></section>'
           + AD.format("sh-mid") +
           f'<section><div class="wrap"><div class="sec-head"><h2>What psychological horror games come out in 2027?</h2><span class="muted">{len(_sh_soon)}</span></div>'
           f'<div class="out" style="margin-bottom:10px">{"".join(_er_srow(g) for g in _sh_soon)}</div>{_like_cd(_sh_ud)}'
           f'<p class="muted">Baptiste and Becrowned are the two billed as psychological horror; Ontos is the next game from Frictional, the studio behind Amnesia and SOMA. See <a href="{href("horror-games-2027.html", 0)}">every horror game of 2027</a> with a console filter.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>When does the Silent Hill 1 remake come out?</h2></div>'
           f'<p>Konami has not given a date. Bloober Team, who made the Silent Hill 2 remake, confirmed it is remaking the first Silent Hill, but no year or platforms are official. Reports of a 2027 launch come from leaks and insiders (PSU, Notebookcheck), so treat 2027 as a guess. It goes on our board the day Konami announces a window.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>Is there a new Silent Hill game in 2027?</h2></div>'
           f'<p>None is dated yet. The latest releases are Silent Hill f (2025) and Silent Hill: Townfall, which came out on 24 September 2026 on PS5 and PC. The Silent Hill 1 remake is the next one announced, with no date.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>Is Silent Hill 2 on Xbox and Switch 2?</h2></div>'
           f'<p>Yes. The Silent Hill 2 remake left PlayStation exclusivity and launched on Xbox Series X|S and Switch 2 in November 2025 (Push Square, Pure Xbox). Other picks on Switch or Switch 2: {e(_and([x for x in _sh_on("switch") if x != "Silent Hill 2"]))}.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>What games are like Silent Hill on PS5 and Xbox?</h2></div>'
           f'<p>PS5: {e(_and(_sh_on("ps5")))}. Xbox: {e(_and(_sh_on("xbox")))}.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>Related pages and tools</h2></div><ul>'
           f'<li><a href="{href("horror-games-2027.html", 0)}">Every horror game of 2027</a>, with a console filter</li>'
           f'<li><a href="{href("games-like-resident-evil.html", 0)}">Games like Resident Evil</a>: survival horror, plus Resident Evil Veronica</li>'
           f'<li><a href="{href("games/until-dawn-2.html", 0)}">Until Dawn 2 release date</a> and countdown</li>'
           f'<li><a href="{href("release-clashes-2027.html", 0)}">2027 release clash finder</a></li></ul></div></section>')
sh_faq = [("What games are like Silent Hill?", _and([x[0] for x in LIKE_SH]) + "."),
          ("When does the Silent Hill 1 remake come out?", "Konami has not announced a date. Reports of 2027 come from leaks, not Konami or Bloober Team."),
          ("When did Silent Hill: Townfall come out?", "On 24 September 2026, on PS5 and PC."),
          ("Is Silent Hill 2 remake on Xbox and Switch 2?", "Yes. It launched on Xbox Series X|S and Switch 2 in November 2025, after PS5 and PC."),
          ("What psychological horror games come out in 2027?", _and([g["title"] + " (" + nice_date(g) + ")" for g in _sh_soon]) + ".")]
page("games-like-silent-hill.html", "Games Like Silent Hill: 10 Horror Picks & 2027 Releases",
     "Games like Silent Hill on PS5, Xbox, Switch 2 and PC: Silent Hill 2, Silent Hill f, Townfall, Alan Wake 2, plus 2027 horror and the Silent Hill 1 remake date.",
     sh_body, 0, sh_faq, crumbs=[("Home", DOMAIN + "/"), ("Horror games of 2027", canon("horror-games-2027.html")), ("Games like Silent Hill", canon("games-like-silent-hill.html"))])

# ---------------- GAMES LIKE GOD OF WAR (28 Nov 2026, demand: "games like god of war", "games like god of war ragnarok", "games to play while waiting for god of war laufey", "god of war laufey release date", DEMAND N66) ----------------
# Evidence: GamesRadar+ US/UK/AU "games like God of War", SVG "5 best games to play while waiting for God of War Laufey", GGRecon, One Esports, Eneba, Ranker, AOL, PremiumCDKeys 2026.
# Facts: Laufey 20 May 2027 PS5, delayed from 16 Feb (Santa Monica Studio 4 Nov 2026 via Game Informer + Kotaku, GamingBolt, God is a Geek). Reveal June 2026 State of Play (Kotaku, GI).
LIKE_GW = [
    ("God of War Ragnarök", "PS5, PS4, PC", "Kratos and Atreus across all nine Norse realms. The free Valhalla roguelite mode is a good warm-up for Laufey.", "ps5 ps4 pc", "myth story"),
    ("God of War (2018)", "PS4, PC (plays on PS5)", "The reboot that introduced Faye's story. Play it first: Laufey runs alongside it.", "ps5 ps4 pc", "myth story"),
    ("Black Myth: Wukong", "PS5, Xbox Series X|S, PC", "Chinese myth, huge boss fights and a staff that feels as heavy as the Leviathan Axe.", "ps5 xbox pc", "myth combat"),
    ("Senua's Saga: Hellblade II", "Xbox Series X|S, PS5, PC", "A short, cinematic Norse story with grounded sword fights and stunning sound.", "ps5 xbox pc", "myth story"),
    ("Star Wars Jedi: Survivor", "PS5, Xbox Series X|S, PC", "Metroid-style planets, puzzle rooms and parry-heavy fights, built a lot like modern God of War.", "ps5 xbox pc", "combat story"),
    ("Assassin's Creed Valhalla", "PS5, PS4, Xbox Series X|S, Xbox One, PC", "A huge Viking open world with Asgard and Jotunheim sections, if you want more Norse gods.", "ps5 ps4 xbox pc", "myth open"),
    ("Immortals Fenyx Rising", "Switch, PS5, PS4, Xbox Series X|S, Xbox One, PC", "A lighter open world full of Greek gods and puzzles: the closest thing to classic God of War on a Nintendo console.", "switch ps5 ps4 xbox pc", "myth open"),
    ("Devil May Cry 5", "PS5, PS4, Xbox Series X|S, Xbox One, PC", "Pure combo combat, for fans of the older, faster God of War games.", "ps5 ps4 xbox pc", "combat"),
    ("Bayonetta 3", "Switch (plays on Switch 2)", "Over-the-top demon fights and giant set pieces from PlatinumGames.", "switch", "combat"),
    ("Stellar Blade", "PS5, PC", "Tight parry-and-dodge boss fights with a strong action focus.", "ps5 pc", "combat"),
    ("Ghost of Yotei", "PS5", "Sony's 2025 open-world revenge story, with the same polish as God of War.", "ps5", "story open"),
]
_GW_LABEL = {"myth": "Gods and myths", "combat": "Big combat", "story": "Story first", "open": "Open world"}
GW_SOON = ["god-of-war-laufey", "wo-long-2", "tomb-raider-legacy-of-atlantis", "stranger-than-heaven", "elta-defy-all-gods", "muramasa-revenant-blades", "lords-of-the-fallen-ii", "hunter-the-reckoning-deathwish", "kingdom-hearts-iv"]
_gw_soon = sorted([g for g in GAMES if g["slug"] in GW_SOON], key=lambda g: (g["month"] or 13, g["date"] or "9999"))
_gw_l = next((g for g in GAMES if g["slug"] == "god-of-war-laufey"), None)
def _gw_on(tag): return [x[0] for x in LIKE_GW if tag in x[3].split()]
_gw_quick = ("The best games like God of War are God of War Ragnarök, Black Myth: Wukong, Hellblade II, Star Wars Jedi: Survivor and Assassin's Creed Valhalla. "
             f"The next God of War game, God of War: Laufey, comes out on {nice_date(_gw_l) if _gw_l else '20 May 2027'} on PS5, after a delay from 16 February.")
gw_body = (f'<header class="hero"><div class="wrap"><span class="kicker">Games like God of War</span>'
           f'<h1>Games like God of War:<br><span class="amber">play now, then Laufey in May 2027.</span></h1>'
           f'<p class="lead">Action games with gods, big bosses and a strong story on PS5, Xbox, Switch 2 and PC, filtered by what you loved, plus every 2027 action game and the God of War: Laufey countdown.</p>'
           f'<p class="muted" style="margin:0">Last checked {e(UPDATED)} · {len(LIKE_GW)} picks out now · {len(_gw_soon)} coming in 2027</p></div></header>'
           f'<section><div class="wrap"><div class="out" style="margin-bottom:12px"><div class="row"><span><strong>Quick answer:</strong> {e(_gw_quick)}</span></div></div>'
           f'<div class="tool" id="er-tool" style="margin-bottom:24px"><h2 style="font-size:1.5rem;margin-top:0">Which game like God of War should I play?</h2>'
           f'<p class="muted">Pick your platform and what you loved most. Your choice is remembered on this device.</p>{_like_chips(_GW_LABEL)}'
           f'<p class="mono amber" id="er-count" aria-live="polite" style="margin:12px 0 0">{len(LIKE_GW)} games</p></div>'
           f'<div class="sec-head"><h2>What games are like God of War?</h2><span class="muted">out now</span></div>'
           f'<div class="out" id="er-list" style="margin-bottom:10px">{_like_rows(LIKE_GW, _GW_LABEL)}</div><p class="empty" id="er-none" hidden>No pick matches both. Try "Anything".</p></div></section>'
           + AD.format("gw-mid") +
           f'<section><div class="wrap"><div class="sec-head"><h2>When does God of War Laufey come out?</h2></div>'
           f'<p>On <strong>20 May 2027</strong>, on PS5. Santa Monica Studio moved it from 16 February 2027 on 4 November 2026, saying it wanted time for finishing touches. You play as Faye (Laufey), Kratos\' wife, in the Everywhen, an afterlife realm full of creatures from several mythologies. Full details on the <a href="{href("games/god-of-war-laufey.html", 0)}">God of War: Laufey release date page</a>.</p>{_like_cd(_gw_l)}'
           f'<div class="sec-head" style="margin-top:28px"><h2>What action games like God of War come out in 2027?</h2><span class="muted">{len(_gw_soon)}</span></div>'
           f'<div class="out" style="margin-bottom:10px">{"".join(_er_srow(g) for g in _gw_soon)}</div>'
           f'<p class="muted">Wo Long 2 and Lords of the Fallen II are the hardest of these; Tomb Raider and Kingdom Hearts IV are the most story-led. Check which ones land in the same week with the <a href="{href("release-clashes-2027.html", 0)}">2027 release clash finder</a>.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>Is God of War Laufey coming to PC?</h2></div>'
           f'<p>Not announced. Only PS5 is confirmed. God of War (2018) and Ragnarök both came to PC later, but Sony has said nothing about a PC version of Laufey yet, and Bloomberg reported in March 2026 that Sony has stopped planning PC ports of its big single-player games (Sony did not comment). PC players can start with those two, Black Myth: Wukong and Hellblade II.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>What should I play before God of War Laufey?</h2></div>'
           f'<p>God of War (2018), then God of War Ragnarök. Laufey\'s story runs alongside both games, and Faye is the mother whose death starts the 2018 game. Ragnarök\'s free Valhalla mode is a short extra if you have time.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>What games are like God of War on Xbox and Switch 2?</h2></div>'
           f'<p>Xbox: {e(_and(_gw_on("xbox")))}. Switch and Switch 2: {e(_and(_gw_on("switch")))}. In 2027, {e(_and([g["title"] for g in _gw_soon if "Switch 2" in g["platforms"]]))} are coming to Switch 2.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>What games are like God of War on PS5?</h2></div>'
           f'<p>{e(_and(_gw_on("ps5")))}.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>Related pages and tools</h2></div><ul>'
           f'<li><a href="{href("games/god-of-war-laufey.html", 0)}">God of War: Laufey release date</a> and delay history</li>'
           f'<li><a href="{href("games-like-elden-ring.html", 0)}">Games like Elden Ring and Dark Souls</a>: soulslikes now and in 2027</li>'
           f'<li><a href="{href("games-like-ghost-of-tsushima.html", 0)}">Games like Ghost of Tsushima</a>: samurai games and Ghost of Yotei on PC</li>'
           f'<li><a href="{href("exclusives-2027.html", 0)}">2027 console exclusives</a></li>'
           f'<li><a href="{href("platforms/ps5.html", 0)}">Every PS5 game of 2027</a></li>'
           f'<li><a href="{href("countdown.html", 0)}">Game release countdown</a></li></ul></div></section>')
gw_faq = [("What games are like God of War?", _and([x[0] for x in LIKE_GW]) + "."),
          ("When does God of War Laufey come out?", "On 20 May 2027 on PS5. It was delayed from 16 February 2027."),
          ("Is God of War Laufey on PC?", "Not announced. Only PS5 is confirmed so far."),
          ("What should I play before God of War Laufey?", "God of War (2018) and God of War Ragnarök. Laufey's story runs alongside both."),
          ("What action games come out in 2027?", _and([g["title"] + " (" + nice_date(g) + ")" for g in _gw_soon]) + ".")]
page("games-like-god-of-war.html", "Games Like God of War: 11 Picks & the Laufey Countdown",
     "Games like God of War on PS5, Xbox, Switch 2 and PC: Ragnarök, Black Myth: Wukong, Hellblade II and more, plus God of War Laufey (20 May 2027).",
     gw_body, 0, gw_faq, crumbs=[("Home", DOMAIN + "/"), ("2027 games by genre", canon("games-by-genre-2027.html")), ("Games like God of War", canon("games-like-god-of-war.html"))])

# ---------------- GAMES LIKE GHOST OF TSUSHIMA (28 Nov 2026, demand: "games like ghost of tsushima", "games like ghost of yotei", "ghost of yotei pc release date", DEMAND N70) ----------------
# Evidence: GamesRadar+ US/UK/AU "10 games like Ghost of Tsushima", Tom's Guide, Beebom, Game Rant, Inverse, Sportskeeda x3, VideoGamer, GamingScan, Eneba; "ghost of yotei pc" (GameWatcher, Destructoid, Gamepressure, Sportskeeda, isitonpc).
# Facts: Ghost of Yotei PS5 2 Oct 2025 (VGC, TechRadar). Bloomberg 4 Mar 2026: Ghost of Yotei and Saros not planned for PC, Sony declined comment (Kotaku, Engadget). AC Hexe late 2027 = reports only (Beebom, TechPowerUp, Wccftech, PSU).
LIKE_GT = [
    ("Ghost of Yotei", "PS5", "Sucker Punch's 2025 sequel: Atsu's revenge story across 1600s Ezo, with the same wind-guided open world and standoffs.", "ps5", "samurai open story"),
    ("Sekiro: Shadows Die Twice", "PS4, Xbox One, PC (plays on PS5 and Xbox Series)", "FromSoftware's sword-clash duels in Sengoku Japan. Much harder, but the best parry combat around.", "ps5 ps4 xbox pc", "samurai combat"),
    ("Rise of the Ronin", "PS5, PC", "Team Ninja's open-world samurai RPG set as Japan opens up in the 1860s, with deep sword stances.", "ps5 pc", "samurai open combat"),
    ("Assassin's Creed Shadows", "PS5, Xbox Series X|S, PC, Switch 2", "Feudal Japan again, split between a shinobi and a samurai, with a huge map and seasons.", "ps5 xbox pc switch", "samurai open"),
    ("Nioh 3", "PS5, PC", "Team Ninja's 2026 yokai action RPG, now with open fields and switchable samurai and ninja styles.", "ps5 pc", "samurai combat"),
    ("Onimusha: Way of the Sword", "PS5, Xbox Series X|S, PC", "Capcom's return of the demon-slaying samurai series, set in Edo-period Kyoto.", "ps5 xbox pc", "samurai combat story"),
    ("Like a Dragon: Ishin!", "PS5, PS4, Xbox Series X|S, Xbox One, PC", "Ryu Ga Gotoku's samurai-era Kyoto story, with sword, gun and fist styles and lots of side stories.", "ps5 ps4 xbox pc", "samurai story"),
    ("Trek to Yomi", "PS5, PS4, Xbox Series X|S, Xbox One, PC, Switch", "A short black-and-white samurai film you play, with side-on sword fights.", "ps5 ps4 xbox pc switch", "samurai story"),
    ("Red Dead Redemption 2", "PS4, Xbox One, PC (plays on PS5 and Xbox Series)", "Not Japan, but the closest match for Ghost's slow, beautiful open world and lone-rider story.", "ps5 ps4 xbox pc", "open story"),
    ("Horizon Forbidden West", "PS5, PS4, PC", "Sony's other big open world: gorgeous to explore, with tactical fights against machines.", "ps5 ps4 pc", "open story"),
]
_GT_LABEL = {"samurai": "Samurai Japan", "combat": "Sword combat", "open": "Open world", "story": "Story first"}
GT_SOON = ["stranger-than-heaven", "wandering-sword", "muramasa-revenant-blades", "wo-long-2", "the-witcher-3-songs-of-the-past", "showa-american-story"]
_gt_soon = sorted([g for g in GAMES if g["slug"] in GT_SOON], key=lambda g: (g["month"] or 13, g["date"] or "9999"))
_gt_wl = next((g for g in GAMES if g["slug"] == "wo-long-2"), None)
def _gt_on(tag): return [x[0] for x in LIKE_GT if tag in x[3].split()]
_gt_quick = ("The best games like Ghost of Tsushima are Ghost of Yotei, Sekiro, Rise of the Ronin, Assassin's Creed Shadows and Nioh 3. "
             f"In 2027, the samurai and sword-fighting games to watch are {_and([g['title'] + ' (' + nice_date(g) + ')' for g in _gt_soon[:4]])}. Ghost of Yotei has no PC version announced.")
gt_body = (f'<header class="hero"><div class="wrap"><span class="kicker">Games like Ghost of Tsushima</span>'
           f'<h1>Games like Ghost of Tsushima:<br><span class="amber">samurai games now, and in 2027.</span></h1>'
           f'<p class="lead">Samurai, open-world and sword-fighting games on PS5, Xbox, Switch 2 and PC, filtered by what you loved about Ghost of Tsushima, plus the 2027 releases and the Ghost of Yotei PC answer.</p>'
           f'<p class="muted" style="margin:0">Last checked {e(UPDATED)} · {len(LIKE_GT)} picks out now · {len(_gt_soon)} coming in 2027</p></div></header>'
           f'<section><div class="wrap"><div class="out" style="margin-bottom:12px"><div class="row"><span><strong>Quick answer:</strong> {e(_gt_quick)}</span></div></div>'
           f'<div class="tool" id="er-tool" style="margin-bottom:24px"><h2 style="font-size:1.5rem;margin-top:0">Which game like Ghost of Tsushima should I play?</h2>'
           f'<p class="muted">Pick your platform and what you loved most. Your choice is remembered on this device.</p>{_like_chips(_GT_LABEL)}'
           f'<p class="mono amber" id="er-count" aria-live="polite" style="margin:12px 0 0">{len(LIKE_GT)} games</p></div>'
           f'<div class="sec-head"><h2>What games are like Ghost of Tsushima?</h2><span class="muted">out now</span></div>'
           f'<div class="out" id="er-list" style="margin-bottom:10px">{_like_rows(LIKE_GT, _GT_LABEL)}</div><p class="empty" id="er-none" hidden>No pick matches both. Try "Anything".</p></div></section>'
           + AD.format("gt-mid") +
           f'<section><div class="wrap"><div class="sec-head"><h2>What samurai and sword games come out in 2027?</h2><span class="muted">{len(_gt_soon)}</span></div>'
           f'<div class="out" style="margin-bottom:10px">{"".join(_er_srow(g) for g in _gt_soon)}</div>{_like_cd(_gt_wl)}'
           f'<p class="muted">Wo Long 2 is the hardest; Muramasa is a 2D hand-drawn sword game; Stranger Than Heaven comes from the Like a Dragon team. See them all with dates on the <a href="{href("calendar.html", 0)}">2027 release calendar</a>.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>Is Ghost of Yotei coming to PC?</h2></div>'
           f'<p>Not announced. Ghost of Yotei came out on PS5 on 2 October 2025, and Sony has not named a PC version. In March 2026 Bloomberg reported that Sony no longer plans PC ports of its big single-player games, naming Ghost of Yotei and Saros; Sony declined to comment (Kotaku, Engadget). Ghost of Tsushima itself did reach PC, about four years after its PS4 launch. On PC today, try Sekiro, Rise of the Ronin, Nioh 3 or Assassin\'s Creed Shadows.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>Is there a new Assassin\'s Creed in Japan or a new samurai game in 2027?</h2></div>'
           f'<p>Assassin\'s Creed Shadows already covers Japan. More picks on <a href="{href("games-like-assassins-creed.html", 0)}">games like Assassin\'s Creed</a>. The next Assassin\'s Creed, codenamed Hexe, is set in witch-hunt-era Europe; several outlets (Beebom, TechPowerUp, Wccftech, PSU) report it is aimed at late 2027, but Ubisoft has not confirmed a date. The dated samurai-style games for 2027 are Wo Long 2 and Muramasa: Revenant Blades.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>What games are like Ghost of Tsushima on Xbox and Switch 2?</h2></div>'
           f'<p>Xbox: {e(_and(_gt_on("xbox")))}. Switch and Switch 2: {e(_and(_gt_on("switch")))}. In 2027, {e(_and([g["title"] for g in _gt_soon if "Switch 2" in g["platforms"]]))} are coming to Switch 2.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>What games are like Ghost of Tsushima on PS5?</h2></div>'
           f'<p>{e(_and(_gt_on("ps5")))}.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>Related pages and tools</h2></div><ul>'
           f'<li><a href="{href("games-like-god-of-war.html", 0)}">Games like God of War</a>: big story action, plus the Laufey countdown</li>'
           f'<li><a href="{href("games-like-elden-ring.html", 0)}">Games like Elden Ring and Sekiro</a>: soulslikes now and in 2027</li>'
           f'<li><a href="{href("games/wo-long-2.html", 0)}">Wo Long 2 release date</a> and Game Pass details</li>'
           f'<li><a href="{href("exclusives-2027.html", 0)}">2027 console exclusives</a> and which PS5 games may reach PC</li>'
           f'<li><a href="{href("countdown.html", 0)}">Game release countdown</a></li></ul></div></section>')
gt_faq = [("What games are like Ghost of Tsushima?", _and([x[0] for x in LIKE_GT]) + "."),
          ("Is Ghost of Yotei coming to PC?", "Not announced. It is PS5-only so far, and Bloomberg reported in March 2026 that Sony no longer plans PC ports of big single-player games like Ghost of Yotei. Sony did not comment."),
          ("When did Ghost of Yotei come out?", "On 2 October 2025, on PS5."),
          ("What samurai games come out in 2027?", _and([g["title"] + " (" + nice_date(g) + ")" for g in _gt_soon]) + "."),
          ("Is Assassin's Creed Hexe coming in 2027?", "Ubisoft has not given a date. Several outlets report it is aimed at late 2027, so treat that as unconfirmed.")]
page("games-like-ghost-of-tsushima.html", "Games Like Ghost of Tsushima: 10 Samurai Picks & 2027",
     "Games like Ghost of Tsushima on PS5, Xbox, Switch 2 and PC: Ghost of Yotei, Sekiro, Rise of the Ronin, AC Shadows, plus 2027 samurai games and Yotei on PC.",
     gt_body, 0, gt_faq, crumbs=[("Home", DOMAIN + "/"), ("2027 games by genre", canon("games-by-genre-2027.html")), ("Games like Ghost of Tsushima", canon("games-like-ghost-of-tsushima.html"))])

# ---------------- GAMES LIKE MONSTER HUNTER (28 Nov 2026, demand: "games like monster hunter", "games like monster hunter wilds", "monster hunter wilds expansion release date", DEMAND N70) ----------------
# Evidence: Tom's Guide, PCGamesN, Digital Trends, Eneba, G2A (Apr 2026), gaming.net, hostedgg 2026, GamesRadar+ (Monster Fantasy, Jul 2026).
# Facts: Ascendance 2027 PS5/Xbox/PC (Capcom IR 8 Jun 2026; Gematsu, RPG Site, PC Gamer). Wilds Switch 2 4 Dec 2026 (already on the December page).
LIKE_MH = [
    ("Monster Hunter Rise: Sunbreak", "Switch, PS5, PS4, Xbox Series X|S, Xbox One, PC", "The fastest Monster Hunter, with the Wirebug and Palamute. The easiest one to play on Switch 2.", "switch ps5 ps4 xbox pc", "hunt coop craft"),
    ("Monster Hunter World: Iceborne", "PS4, Xbox One, PC (plays on PS5 and Xbox Series)", "Still one of the best: a huge Master Rank expansion and a long monster list.", "ps5 ps4 xbox pc", "hunt coop craft"),
    ("Wild Hearts", "PS5, Xbox Series X|S, PC", "Koei Tecmo and EA's nature-beast hunter, where you build walls, springs and traps mid-fight.", "ps5 xbox pc", "hunt coop craft"),
    ("Monster Hunter Stories 3: Twisted Reflection", "Switch 2, PS5, Xbox Series X|S, PC", "Capcom's 2026 turn-based spin-off: raise monsters instead of hunting them, with a full story.", "switch ps5 xbox pc", "story"),
    ("God Eater 3", "PS4, PC, Switch", "Anime-style hunts against Aragami with fast weapons that turn into guns.", "ps4 pc switch", "hunt coop"),
    ("Toukiden 2", "PS4, PC", "Ninja-era demon hunting in an open world, with limb-breaking and a friendly difficulty curve.", "ps4 pc", "hunt coop"),
    ("Granblue Fantasy: Relink", "PS5, PS4, PC", "Four-player anime action with huge raid bosses and a gear-and-sigil grind.", "ps5 ps4 pc", "coop story"),
    ("Eternal Strands", "PS5, Xbox Series X|S, PC", "Climb giant creatures and melt or freeze them with magic in a smaller, story-led adventure.", "ps5 xbox pc", "hunt story"),
    ("Dragon's Dogma 2", "PS5, Xbox Series X|S, PC", "Capcom's open-world RPG: grab onto griffins and cyclopes with your AI pawns.", "ps5 xbox pc", "hunt story"),
    ("Horizon Forbidden West", "PS5, PS4, PC", "Hunt robot dinosaurs, strip their parts and craft from them, solo, with a big story.", "ps5 ps4 pc", "hunt craft story"),
]
_MH_LABEL = {"hunt": "Big monster fights", "coop": "Co-op", "craft": "Gear grind", "story": "Story / solo"}
MH_SOON = ["monster-hunter-wilds-ascendance", "horizon-steel-frontiers", "the-duskbloods", "wo-long-2", "lords-of-the-fallen-ii", "cassette-beasts-2002"]
_mh_soon = sorted([g for g in GAMES if g["slug"] in MH_SOON], key=lambda g: (g["month"] or 13, g["date"] or "9999"))
_mh_wl = next((g for g in GAMES if g["slug"] == "wo-long-2"), None)
def _mh_on(tag): return [x[0] for x in LIKE_MH if tag in x[3].split()]
_mh_quick = ("The best games like Monster Hunter are Monster Hunter Rise: Sunbreak, World: Iceborne, Wild Hearts, God Eater 3 and Granblue Fantasy: Relink. "
             "The next Monster Hunter is Monster Hunter Wilds: Ascendance, a Master Rank expansion due in 2027 on PS5, Xbox Series X|S and PC (no day yet), and Wilds itself reaches Switch 2 on 4 December 2026.")
mh_body = (f'<header class="hero"><div class="wrap"><span class="kicker">Games like Monster Hunter</span>'
           f'<h1>Games like Monster Hunter:<br><span class="amber">hunt now, Ascendance in 2027.</span></h1>'
           f'<p class="lead">Monster-hunting and co-op boss games on PS5, Xbox, Switch 2 and PC, filtered by what you love about Monster Hunter, plus the Wilds expansion date and every 2027 hunting game.</p>'
           f'<p class="muted" style="margin:0">Last checked {e(UPDATED)} · {len(LIKE_MH)} picks out now · {len(_mh_soon)} coming in 2027</p></div></header>'
           f'<section><div class="wrap"><div class="out" style="margin-bottom:12px"><div class="row"><span><strong>Quick answer:</strong> {e(_mh_quick)}</span></div></div>'
           f'<div class="tool" id="er-tool" style="margin-bottom:24px"><h2 style="font-size:1.5rem;margin-top:0">Which game like Monster Hunter should I play?</h2>'
           f'<p class="muted">Pick your platform and what you love most. Your choice is remembered on this device.</p>{_like_chips(_MH_LABEL, "What you love")}'
           f'<p class="mono amber" id="er-count" aria-live="polite" style="margin:12px 0 0">{len(LIKE_MH)} games</p></div>'
           f'<div class="sec-head"><h2>What games are like Monster Hunter?</h2><span class="muted">out now</span></div>'
           f'<div class="out" id="er-list" style="margin-bottom:10px">{_like_rows(LIKE_MH, _MH_LABEL)}</div><p class="empty" id="er-none" hidden>No pick matches both. Try "Anything".</p></div></section>'
           + AD.format("mh-mid") +
           f'<section><div class="wrap"><div class="sec-head"><h2>When does the Monster Hunter Wilds expansion come out?</h2></div>'
           f'<p>In <strong>2027</strong>, with no month or day yet. Capcom revealed <a href="{href("games/monster-hunter-wilds-ascendance.html", 0)}">Monster Hunter Wilds: Ascendance</a> at Summer Game Fest on 5 June 2026 and confirmed 2027 on PS5, Xbox Series X|S and PC (Steam). It is a paid expansion like Iceborne and Sunbreak: Master Rank, returning Elder Dragons starting with Kushala Daora, new monsters, a new sky-island region called the Skybound Eyrie and new moves for all 14 weapons.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>Is Monster Hunter Wilds on Switch 2?</h2></div>'
           f'<p>Yes, from 4 December 2026, with local and cross-platform play (see <a href="{href("games-december-2026.html", 0)}">games coming out in December 2026</a>). Ascendance is not announced for Switch 2 yet. Monster Hunter Rise: Sunbreak and Monster Hunter Stories 3 also play on Switch 2.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>What monster-hunting and co-op boss games come out in 2027?</h2><span class="muted">{len(_mh_soon)}</span></div>'
           f'<div class="out" style="margin-bottom:10px">{"".join(_er_srow(g) for g in _mh_soon)}</div>{_like_cd(_mh_wl)}'
           f'<p class="muted">Horizon Steel Frontiers is NCSOFT\'s machine-hunting MMO; The Duskbloods is FromSoftware\'s 8-player Switch 2 game; Wo Long 2 and Lords of the Fallen II are co-op soulslikes. Check which ones land in the same week with the <a href="{href("release-clashes-2027.html", 0)}">2027 release clash finder</a>.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>Will there be a Monster Hunter 7 or Wilds 2?</h2></div>'
           f'<p>Not announced. Capcom\'s next Monster Hunter release is the Ascendance expansion in 2027. Monster Hunter Outlanders is a separate mobile game.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>What games are like Monster Hunter on PS5, Xbox and PC?</h2></div>'
           f'<p>PS5: {e(_and(_mh_on("ps5")))}. Xbox: {e(_and(_mh_on("xbox")))}. PC: {e(_and(_mh_on("pc")))}.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>Related pages and tools</h2></div><ul>'
           f'<li><a href="{href("games/monster-hunter-wilds-ascendance.html", 0)}">Monster Hunter Wilds: Ascendance release date</a></li>'
           f'<li><a href="{href("games-like-elden-ring.html", 0)}">Games like Elden Ring</a>: soulslikes now and in 2027</li>'
           f'<li><a href="{href("games-like-palworld.html", 0)}">Games like Palworld</a>: creature survival games</li>'
           f'<li><a href="{href("rpgs-2027.html", 0)}">Every RPG of 2027</a></li>'
           f'<li><a href="{href("backlog-planner-2027.html", 0)}">2027 backlog planner</a></li></ul></div></section>')
mh_faq = [("What games are like Monster Hunter?", _and([x[0] for x in LIKE_MH]) + "."),
          ("When does Monster Hunter Wilds Ascendance come out?", "In 2027 on PS5, Xbox Series X|S and PC. Capcom has not given a month or day."),
          ("Is Monster Hunter Wilds on Switch 2?", "Yes, from 4 December 2026. The Ascendance expansion is not announced for Switch 2 yet."),
          ("Is there a Monster Hunter 7?", "Not announced. The next release is the Wilds expansion, Ascendance, in 2027."),
          ("What hunting games come out in 2027?", _and([g["title"] + " (" + nice_date(g) + ")" for g in _mh_soon]) + ".")]
page("games-like-monster-hunter.html", "Games Like Monster Hunter: 10 Picks & Ascendance 2027",
     "Games like Monster Hunter on PS5, Xbox, Switch 2 and PC: Rise, World, Wild Hearts, God Eater 3, plus the Wilds Ascendance expansion (2027) and Wilds on Switch 2.",
     mh_body, 0, mh_faq, crumbs=[("Home", DOMAIN + "/"), ("2027 games by genre", canon("games-by-genre-2027.html")), ("Games like Monster Hunter", canon("games-like-monster-hunter.html"))])

# ---------------- GAMES LIKE ASSASSIN'S CREED (28 Nov 2026, demand: "games like assassin's creed", "assassin's creed hexe release date", "next assassin's creed", DEMAND N74) ----------------
# Evidence: GamesRadar+ US/UK/AU "games like Assassin's Creed", TechRadar best AC ranked; Hexe date searches (Beebom, ComicBook x2, Wccftech, Guru3D, TechPowerUp, PSU, Insider Gaming, MP1st, TweakTown).
# Facts: Black Flag Resynced 9 Jul 2026 PS5/Xbox Series/PC, no Switch 2 at launch (Ubisoft News, Gematsu, RPG Site, Gfinity). Hexe: no official date; reports say 2H 2027 at earliest (TechPowerUp, PSU, Insider Gaming), Wccftech leak June 2027 "could slip".
LIKE_AC = [
    ("Assassin's Creed Black Flag Resynced", "PS5, Xbox Series X|S, PC", "Ubisoft's 2026 rebuild of Black Flag: pirate Edward Kenway, ship battles and the Caribbean, with reworked combat and new quests.", "ps5 xbox pc", "parkour history open"),
    ("Ghost of Tsushima", "PS5, PS4, PC", "Feudal Japan with sneaky Ghost assassinations, standoffs and a wind-guided open world.", "ps5 ps4 pc", "stealth history open combat"),
    ("Ghost of Yotei", "PS5", "The 2025 sequel: a revenge story across 1600s Ezo, with the same stealth kills and duels.", "ps5", "stealth history open combat"),
    ("Kingdom Come: Deliverance II", "PS5, Xbox Series X|S, PC", "Realistic medieval Bohemia: sneak, pickpocket and sword-fight your way through a huge historical story.", "ps5 xbox pc", "stealth history open combat"),
    ("Hitman: World of Assassination", "PS5, PS4, Xbox Series X|S, Xbox One, PC", "Pure assassination: one target, a huge sandbox level and dozens of ways to get them.", "ps5 ps4 xbox pc", "stealth"),
    ("Dishonored 2", "PS4, Xbox One, PC (plays on PS5 and Xbox Series)", "Magic-powered stealth assassin in a city you can climb, blink across and clear without killing anyone.", "ps5 ps4 xbox pc", "stealth parkour"),
    ("Middle-earth: Shadow of War", "PS4, Xbox One, PC (plays on PS5 and Xbox Series)", "Assassin's Creed-style climbing and stealth in Mordor, with the Nemesis system of rival orc captains.", "ps5 ps4 xbox pc", "stealth parkour open combat"),
    ("Rise of the Ronin", "PS5, PC", "An open-world samurai RPG in 1860s Japan, with grappling hooks, gliders and real historical figures.", "ps5 pc", "history open combat"),
    ("007 First Light", "PS5, Xbox Series X|S, PC (Switch 2 on 18 March 2027)", "IO Interactive's young James Bond story: Hitman-style infiltration with more action.", "ps5 xbox pc switch", "stealth"),
    ("Prince of Persia: The Lost Crown", "PS5, PS4, Xbox Series X|S, Xbox One, Switch, PC", "Ubisoft's 2D take on the series that inspired Assassin's Creed: acrobatic platforming and fast combat.", "ps5 ps4 xbox pc switch", "parkour combat"),
    ("Star Wars Outlaws", "PS5, Xbox Series X|S, PC, Switch 2", "Ubisoft's open-world heist game: sneak through bases and shoot your way across Star Wars planets.", "ps5 xbox pc switch", "stealth open"),
]
_AC_LABEL = {"stealth": "Stealth kills", "parkour": "Climbing and parkour", "history": "Real history", "open": "Open world", "combat": "Sword combat"}
AC_SOON = ["stranger-than-heaven", "spyder-agent-8", "tomb-raider-legacy-of-atlantis", "fable", "wo-long-2", "007-first-light", "showa-american-story"]
_ac_soon = sorted([g for g in GAMES if g["slug"] in AC_SOON], key=lambda g: (g["month"] or 13, g["date"] or "9999"))
_ac_first = next((g for g in _ac_soon if g["date"]), None)
def _ac_on(tag): return [x[0] for x in LIKE_AC if tag in x[3].split()]
_ac_quick = ("The best games like Assassin's Creed are Ghost of Tsushima, Ghost of Yotei, Kingdom Come: Deliverance II, Hitman, Dishonored 2 and Middle-earth: Shadow of War; Black Flag Resynced (July 2026) is the newest Assassin's Creed. "
             "The next one, codenamed Hexe, has no official date: reports say late 2027 at the earliest.")
ac_body = (f'<header class="hero"><div class="wrap"><span class="kicker">Games like Assassin\'s Creed</span>'
           f'<h1>Games like Assassin\'s Creed:<br><span class="amber">stealth and history now, Hexe later.</span></h1>'
           f'<p class="lead">Stealth, parkour and historical open-world games on PS5, Xbox, Switch 2 and PC, filtered by what you love about Assassin\'s Creed, plus the 2027 releases and what we really know about Hexe.</p>'
           f'<p class="muted" style="margin:0">Last checked {e(UPDATED)} · {len(LIKE_AC)} picks out now · {len(_ac_soon)} coming in 2027</p></div></header>'
           f'<section><div class="wrap"><div class="out" style="margin-bottom:12px"><div class="row"><span><strong>Quick answer:</strong> {e(_ac_quick)}</span></div></div>'
           f'<div class="tool" id="er-tool" style="margin-bottom:24px"><h2 style="font-size:1.5rem;margin-top:0">Which game like Assassin\'s Creed should I play?</h2>'
           f'<p class="muted">Pick your platform and what you love most. Your choice is remembered on this device.</p>{_like_chips(_AC_LABEL, "What you love")}'
           f'<p class="mono amber" id="er-count" aria-live="polite" style="margin:12px 0 0">{len(LIKE_AC)} games</p></div>'
           f'<div class="sec-head"><h2>What games are like Assassin\'s Creed?</h2><span class="muted">out now</span></div>'
           f'<div class="out" id="er-list" style="margin-bottom:10px">{_like_rows(LIKE_AC, _AC_LABEL)}</div><p class="empty" id="er-none" hidden>No pick matches both. Try "Anything".</p></div></section>'
           + AD.format("ac-mid") +
           f'<section><div class="wrap"><div class="sec-head"><h2>When does the next Assassin\'s Creed come out?</h2></div>'
           f'<p>Ubisoft has not announced a date. The next main game is codenamed <strong>Assassin\'s Creed Hexe</strong>. In July 2026 several outlets (TechPowerUp, PSU, Insider Gaming) reported it will not launch before the second half of 2027, and a later leak covered by Wccftech pointed to June 2027 while warning the date could slip. Treat 2027 as a report, not a confirmed date. We add it to the board the day Ubisoft gives a year.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>Is Assassin\'s Creed Black Flag Resynced out?</h2></div>'
           f'<p>Yes. It came out on 9 July 2026 on PS5, Xbox Series X|S and PC. It is a ground-up rebuild of 2013\'s Black Flag with reworked combat and new quests. It did not launch on Switch 2.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>What stealth and action-adventure games come out in 2027?</h2><span class="muted">{len(_ac_soon)}</span></div>'
           f'<div class="out" style="margin-bottom:10px">{"".join(_er_srow(g) for g in _ac_soon)}</div>{_like_cd(_ac_first)}'
           f'<p class="muted">Spyder: Agent 8 is the pure stealth pick; Stranger Than Heaven is a period crime drama from the Like a Dragon team; Tomb Raider: Legacy of Atlantis is the closest for climbing and ruins. Plan them around each other with the <a href="{href("release-clashes-2027.html", 0)}">2027 release clash finder</a>.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>What games are like Assassin\'s Creed on Switch 2?</h2></div>'
           f'<p>{e(_and(_ac_on("switch")))}. In 2027, {e(_and([g["title"] for g in _ac_soon if "Switch 2" in g["platforms"]]))} are coming to Switch 2. Assassin\'s Creed Shadows is also on Switch 2.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>What games are like Assassin\'s Creed on PS5, Xbox and PC?</h2></div>'
           f'<p>PS5: {e(_and(_ac_on("ps5")))}. Xbox: {e(_and(_ac_on("xbox")))}. PC: {e(_and(_ac_on("pc")))}.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>Related pages and tools</h2></div><ul>'
           f'<li><a href="{href("games-like-ghost-of-tsushima.html", 0)}">Games like Ghost of Tsushima</a>: samurai games and Ghost of Yotei on PC</li>'
           f'<li><a href="{href("games-like-red-dead-redemption-2.html", 0)}">Games like Red Dead Redemption 2</a>: big story open worlds</li>'
           f'<li><a href="{href("games-like-god-of-war.html", 0)}">Games like God of War</a>, plus the Laufey countdown</li>'
           f'<li><a href="{href("biggest-games-2027.html", 0)}">The biggest games of 2027</a></li>'
           f'<li><a href="{href("countdown.html", 0)}">Game release countdown</a></li></ul></div></section>')
ac_faq = [("What games are like Assassin's Creed?", _and([x[0] for x in LIKE_AC]) + "."),
          ("When does Assassin's Creed Hexe come out?", "Ubisoft has not announced a date. Reports say the second half of 2027 at the earliest, so treat 2027 as unconfirmed."),
          ("When did Assassin's Creed Black Flag Resynced come out?", "On 9 July 2026 on PS5, Xbox Series X|S and PC."),
          ("Is Black Flag Resynced on Switch 2?", "No. It launched on PS5, Xbox Series X|S and PC only."),
          ("What stealth games come out in 2027?", _and([g["title"] + " (" + nice_date(g) + ")" for g in _ac_soon]) + ".")]
page("games-like-assassins-creed.html", "Games Like Assassin's Creed: 11 Picks & Hexe Release Date",
     "Games like Assassin's Creed on PS5, Xbox, Switch 2 and PC: Ghost of Tsushima, Kingdom Come II, Hitman, Dishonored 2, plus 2027 stealth games and AC Hexe news.",
     ac_body, 0, ac_faq, crumbs=[("Home", DOMAIN + "/"), ("2027 games by genre", canon("games-by-genre-2027.html")), ("Games like Assassin's Creed", canon("games-like-assassins-creed.html"))])


# ---------------- REMAKES AND REMASTERS 2027 (28 Nov 2026, demand: E5 "upcoming game remakes 2027", "video game remakes 2027", "silent hill 1 remake release date", "god of war trilogy remake release date") ----------------
# Board games tagged below come from games.json (each 2+ sources). Off-board rows: Rayman Legends Retold 3 Dec 2026 (Ubisoft News, Gematsu, Nintendo Life);
# Thief: The Dark Project Remastered 3 Dec 2026 (Shacknews, PSU, Gaming Trend); TBA remakes from Game Informer's big remake list (27 Nov 2026) + PlayStation Blog/Gematsu/Push Square (God of War Trilogy Remake, Feb 2026).
_rm = sorted([g for g in GAMES if g["slug"] in _RM_KIND], key=lambda g: (g["month"] or 13, g["date"] or "9999"))
_rm_dated = [g for g in _rm if g["date"]]
_rm_next = _rm_dated[0] if _rm_dated else None
_rm_win = [g for g in _rm if not g["date"]]
RM_SOON = [("Rayman Legends Retold", "Remake", "Ubisoft", ["PS5", "Xbox Series X|S", "PC", "Switch 2"], "3 Dec 2026", "A rebuilt Rayman Legends. It was due on 1 October and moved to 3 December 2026."),
           ("Thief: The Dark Project Remastered", "Remaster", "Nightdive Studios", ["PS5", "Xbox Series X|S", "PC"], "3 Dec 2026", "Nightdive's remaster of the 1998 stealth classic. Also on PS4 and Xbox One, with Switch versions announced.")]
RM_TBA = [("God of War Trilogy Remake", "Santa Monica Studio", ["PS5"], "A remake of the original Greek trilogy, announced at State of Play in February 2026, with TC Carson back as Kratos."),
          ("Silent Hill Remake", "Bloober Team / Konami", [], "A remake of the first Silent Hill from the team behind the Silent Hill 2 remake. The 2027 talk is a leak, not a date."),
          ("Max Payne 1 & 2 Remake", "Remedy (Rockstar publishing)", [], "Both Max Payne games remade in one package for current consoles and PC."),
          ("Star Wars: Knights of the Old Republic Remake", "Saber Interactive", ["PS5", "PC"], "The 2003 RPG rebuilt from scratch. Announced in 2021, still no date."),
          ("Splinter Cell Remake", "Ubisoft Toronto", [], "A remake of the first Splinter Cell, rebuilt in the Snowdrop engine."),
          ("The Witcher Remake", "Fool's Theory with CD Projekt Red", [], "The 2007 original remade in Unreal Engine 5. CD Projekt says it comes after The Witcher 4.")]
def _rmx(title, kind, dev, plats, when, note, slug=""):
    return (f'<div class="row" data-fplat="{e("|".join(plats))}" data-slug="{e(slug)}"><span><strong>{title}</strong> <span class="mono muted" style="font-size:.78rem">{e(kind.upper())}</span>'
            f'<br><span class="muted">{e(note)}</span><br><span class="muted">{e(dev)} · {e(", ".join(plats) or "Platforms not confirmed")}</span></span><b>{e(when)}</b></div>')
def _rmg(g): return _rmx(_gname(g), _RM_KIND[g["slug"]], g.get("dev") or "Studio TBC", g["platforms"], nice_date(g), g.get("about") or g["genre"], g["slug"])
_rm_p = {p: [g for g in _rm if p in g["platforms"]] for p in PLATS}
_rm_tbl = ('<div style="overflow-x:auto"><table class="gen-table" style="width:100%;border-collapse:collapse;font-size:.92rem"><thead><tr><th style="text-align:left;padding:6px">Console</th><th style="padding:6px">2027 remakes</th><th style="text-align:left;padding:6px">Which ones</th></tr></thead><tbody>'
           + "".join(f'<tr><td style="padding:6px;border-top:1px solid var(--rule)"><a href="{href("platforms/" + _pslug[p] + ".html", 0)}">{e(_lab[p])}</a></td>'
                     f'<td style="padding:6px;text-align:center;border-top:1px solid var(--rule)" class="mono">{len(_rm_p[p])}</td>'
                     f'<td style="padding:6px;border-top:1px solid var(--rule)">{e(", ".join(g["title"] for g in _rm_p[p]) or "None confirmed yet")}</td></tr>' for p in PLATS)
           + '</tbody></table></div>')
_rm_quick = (f"We track {len(_rm)} remakes, remasters and re-releases for 2027. The big dated ones are "
             + _and([g["title"] + " (" + nice_date(g) + ")" for g in _rm_dated if g["slug"] in ("persona-4-revival", "tomb-raider-legacy-of-atlantis", "final-fantasy-vii-revelation", "romancing-saga-3-destinies-united")])
             + "; Resident Evil Veronica, Hitman Classic Trilogy Remastered and Heroes of Might and Magic III are due in 2027 with no day yet. The God of War, Silent Hill and Max Payne remakes have no date.")
rm_body = (f'<header class="hero"><div class="wrap"><span class="kicker">Remakes and remasters</span>'
           f'<h1>Upcoming game remakes 2027:<br><span class="amber">every remake and remaster, every date.</span></h1>'
           f'<p class="lead">Every announced remake, remaster and classic collection for 2027 on PS5, Xbox, Switch 2 and PC, from Persona 4 Revival to Resident Evil Veronica, plus the big remakes that still have no date.</p>'
           f'<p class="muted" style="margin:0">Last checked {e(UPDATED)} · {len(_rm)} in 2027 · {len(RM_TBA)} with no date · dates from publishers or two trusted outlets</p></div></header>'
           f'<section><div class="wrap"><div class="out" style="margin-bottom:24px"><div class="row"><span><strong>Quick answer:</strong> {e(_rm_quick)}</span></div></div>'
           f'<div class="tool" id="fg-tool" data-noun="remake"><h2 style="font-size:1.5rem;margin-top:0">Which remakes can I play on my console?</h2>'
           f'<p class="muted">Tap your console. Every list on this page updates, and your choice is remembered on this device.</p>{_fchips}'
           f'<p class="mono amber" id="fg-count" aria-live="polite" style="margin:12px 0 0">{len(_rm)} remakes</p>'
           f'<div class="btns" style="margin-top:10px;display:flex;gap:8px;flex-wrap:wrap"><button class="btn sm" type="button" id="fg-add">Add the 2027 ones to my ★ list</button>'
           f'<a class="btn line sm" href="{href("release-clashes-2027.html", 0)}">Check release clashes</a></div></div></div></section>'
           + AD.format("rm-mid") +
           f'<section><div class="wrap"><div class="sec-head"><h2>What remakes come out in 2027?</h2><span class="muted">{len(_rm)}</span></div>'
           f'<p class="muted">In release order. Games with only a month or a year sit after the dated ones.</p>'
           f'<div class="out" id="fg-list" style="margin-bottom:10px">{"".join(_rmg(g) for g in _rm)}'
           f'<div class="row"><span class="mono amber">STILL TO COME IN DECEMBER 2026</span></div>{"".join(_rmx(e(x[0]), *x[1:]) for x in RM_SOON)}'
           f'<div class="row"><span class="mono amber">ANNOUNCED, NO RELEASE DATE</span></div>{"".join(_rmx(e(x[0]), "Remake", x[1], x[2], "TBA", x[3]) for x in RM_TBA)}</div>'
           f'<p class="empty" id="fg-none" hidden>No tracked remake is confirmed for that console yet.</p>'
           + (f'<div class="cdw"><span class="lbl">Countdown to {e(_rm_next["title"])}</span><div class="cd" data-countdown="{_rm_next["date"]}">'
              '<div class="cd-unit"><span class="flaps" data-u="0"></span><span>Days</span></div><div class="cd-unit"><span class="flaps" data-u="1"></span><span>Hrs</span></div>'
              '<div class="cd-unit"><span class="flaps" data-u="2"></span><span>Min</span></div><div class="cd-unit"><span class="flaps" data-u="3"></span><span>Sec</span></div></div></div>' if _rm_next else "") +
           f'<div class="sec-head" style="margin-top:28px"><h2>When does the Resident Evil Code: Veronica remake come out?</h2></div>'
           f'<p>In 2027. Capcom announced <a href="{href("games/resident-evil-veronica.html", 0)}">Resident Evil Veronica</a> at Summer Game Fest on 5 June 2026 for PS5, Xbox Series X|S, Switch 2 and PC, but has not given a month or day. It is nominated for Most Anticipated Game at The Game Awards on 10 December, a likely place for a date.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>When does Persona 4 Revival come out?</h2></div>'
           f'<p>On 18 February 2027 on PS5, Xbox Series X|S and PC. See <a href="{href("games/persona-4-revival.html", 0)}">the Persona 4 Revival page</a> for the Switch 2 version and the countdown.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>Is there a release date for the Silent Hill 1 remake?</h2></div>'
           f'<p>No. Bloober Team and Konami confirmed the remake of the first Silent Hill, but there is no date or platform list yet. Reports of 2027 come from a leak, so we treat it as unconfirmed. Horror fans can see what is dated on <a href="{href("horror-games-2027.html", 0)}">horror games of 2027</a>.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>When does the God of War Trilogy Remake come out?</h2></div>'
           f'<p>Sony has not given a date. Santa Monica Studio confirmed the remake of the original Greek trilogy for PS5 at State of Play in February 2026, with TC Carson returning as Kratos. The next dated God of War game is <a href="{href("games/god-of-war-laufey.html", 0)}">God of War: Laufey</a> on 20 May 2027.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>Is the Max Payne remake coming out in 2027?</h2></div>'
           f'<p>Not confirmed. Remedy is remaking Max Payne 1 and 2 as one game for current consoles and PC, funded and published by Rockstar, with no release date announced.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>When does Hitman Classic Trilogy Remastered come out?</h2></div>'
           f'<p>In 2027 on PS5, Xbox Series X|S and PC. Saber Interactive is remastering Codename 47, Silent Assassin and Contracts. More on <a href="{href("games-like-hitman.html", 0)}">games like Hitman</a>.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>What remakes are coming to Switch 2 in 2027?</h2></div>'
           f'<p>{e(_and([g["title"] + " (" + nice_date(g) + ")" for g in _rm_p["Switch 2"]]))}.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>What is the difference between a remake and a remaster?</h2></div>'
           f'<p>A <strong>remake</strong> is rebuilt from scratch: new graphics, often new combat, voice acting or story, like Persona 4 Revival or Tomb Raider: Legacy of Atlantis. A <strong>remaster</strong> keeps the original game and upgrades it: sharper graphics, higher frame rate, quality-of-life fixes, like Hitman Classic Trilogy Remastered. A collection bundles old games with light fixes.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>How many 2027 remakes are on PS5, Xbox, PC and Switch 2?</h2></div>{_rm_tbl}'
           f'<div class="sec-head" style="margin-top:28px"><h2>Related pages and tools</h2></div><ul>'
           f'<li><a href="{href("dlc-2027.html", 0)}">DLC and expansions coming in 2027</a></li>'
           f'<li><a href="{href("biggest-games-2027.html", 0)}">The biggest games of 2027</a></li>'
           f'<li><a href="{href("games-without-release-date-2027.html", 0)}">2027 games with no release date</a></li>'
           f'<li><a href="{href("backlog-planner-2027.html", 0)}">2027 backlog planner</a>: will you finish the old ones first?</li>'
           f'<li><a href="{href("countdown.html", 0)}">Game release countdown</a></li></ul></div></section>')
rm_faq = [("What game remakes are coming out in 2027?", _and([g["title"] + " (" + nice_date(g) + ")" for g in _rm]) + "."),
          ("When does the Resident Evil Code: Veronica remake come out?", "In 2027 on PS5, Xbox Series X|S, Switch 2 and PC. Capcom has not given a month or day."),
          ("Is there a release date for the Silent Hill 1 remake?", "No. Konami and Bloober Team have not announced a date or platforms."),
          ("When does the God of War Trilogy Remake come out?", "No date yet. It was announced for PS5 in February 2026."),
          ("When does Tomb Raider: Legacy of Atlantis come out?", "On 12 February 2027 on PS5, Xbox Series X|S, Switch 2 and PC."),
          ("What remakes come out in December 2026?", "Rayman Legends Retold and Thief: The Dark Project Remastered, both on 3 December 2026.")]
page("remakes-2027.html", "Upcoming Game Remakes 2027: Every Remake & Remaster Date",
     "Every game remake and remaster coming in 2027: Persona 4 Revival (18 Feb), Tomb Raider, FF7 Revelation, RE Veronica, Hitman trilogy, plus undated remakes.",
     rm_body, 0, rm_faq, crumbs=[("Home", DOMAIN + "/"), ("2027 games by genre", canon("games-by-genre-2027.html")), ("Remakes 2027", canon("remakes-2027.html"))])

# ---------------- DLC AND EXPANSIONS 2027 (28 Nov 2026, demand: E6 autocomplete "dlc 2027" -> witcher / starfield / cyberpunk / pokopia dlc 2027) ----------------
# Board: Witcher 3 Songs of the Past, MH Wilds Ascendance, FFXIV Evercold (games.json). Off-board: Guild Wars Afterlife 13 Jan 2027 (RPG Site, Massively OP, RPGamer, Worthplaying);
# Civ VII Earthrise 2027 (2K/Firaxis, Gematsu, Nintendo Life, Worthplaying); Pokopia Expansion Pass Part 2 9 Dec 2026 + Part 3 2027 (VGC 4 Nov 2026, ComicBook);
# Starfield new story content 2027 (Bethesda via GamingBolt, Insider Gaming). Cyberpunk: no new expansion announced; sequel in pre-production.
_DLC_SLUGS = ["final-fantasy-xiv-evercold", "the-witcher-3-songs-of-the-past", "monster-hunter-wilds-ascendance"]
_dlc_b = sorted([g for g in GAMES if g["slug"] in _DLC_SLUGS], key=lambda g: (g["month"] or 13, g["date"] or "9999"))
DLC_X = [("Guild Wars Afterlife", "Guild Wars Reforged", "ArenaNet", ["PC"], "13 Jan 2027", "2027-01-13", "The original Guild Wars' first paid DLC in nearly 20 years: a randomised roguelike dungeon mode in the Mists. Needs Guild Wars Reforged."),
         ("Civilization VII: Earthrise", "Sid Meier's Civilization VII", "Firaxis / 2K", [], "2027", "", "The first paid expansion: a space-race era. A free Arc of Tomorrow update adds the Atomic Age."),
         ("Pokopia Expansion Pass Part 3", "Pokémon Pokopia", "Nintendo / The Pokémon Company", ["Switch 2"], "2027", "", "The third and final part of the Expansion Pass. No name yet."),
         ("New Starfield story content", "Starfield", "Bethesda", ["Xbox Series X|S", "PC", "PS5"], "2027", "", "Bethesda says more story content is coming in 2027. No name or date beyond the year.")]
DLC_DEC = [("Pokopia Expansion Pass Part 2: Dazzling Decorations", "Pokémon Pokopia", "Nintendo / The Pokémon Company", ["Switch 2"], "9 Dec 2026", "2026-12-09", "Part 2 of the paid Expansion Pass. Part 1, Bubbly Basin, came out in August 2026.")]
def _dlcx(x): return _rmx(e(x[0]), "DLC for " + x[1], x[2], x[3], x[4], x[6])
def _dlcg(g): return _rmx(_gname(g), "Expansion", g.get("dev") or "Studio TBC", g["platforms"], nice_date(g), g.get("about") or g["genre"], g["slug"])
_dlc_rows = sorted([(g["month"] or 13, g["date"] or "9999", _dlcg(g)) for g in _dlc_b] + [((int(x[5][5:7]) if x[5] else 13), x[5] or "9999", _dlcx(x)) for x in DLC_X])
_dlc_n = len(_dlc_rows)
_dlc_quick = ("The DLC coming in 2027: Guild Wars Afterlife (13 January), Final Fantasy XIV: Evercold (23 February), The Witcher 3: Songs of the Past, Monster Hunter Wilds: Ascendance, "
              "Civilization VII: Earthrise, Pokopia's third Expansion Pass part and new Starfield story content (all 2027, no day yet). No new Cyberpunk 2077 expansion is announced.")
dlc_body = (f'<header class="hero"><div class="wrap"><span class="kicker">DLC and expansions</span>'
            f'<h1>DLC coming in 2027:<br><span class="amber">every expansion with a date.</span></h1>'
            f'<p class="lead">Every announced paid expansion and big DLC for 2027, from The Witcher 3 and Monster Hunter Wilds to Starfield and Pokémon Pokopia, with a console filter. Only announced DLC: no rumours.</p>'
            f'<p class="muted" style="margin:0">Last checked {e(UPDATED)} · {_dlc_n} expansions in 2027 · sources: publishers and two trusted outlets</p></div></header>'
            f'<section><div class="wrap"><div class="out" style="margin-bottom:24px"><div class="row"><span><strong>Quick answer:</strong> {e(_dlc_quick)}</span></div></div>'
            f'<div class="tool" id="fg-tool" data-noun="expansion"><h2 style="font-size:1.5rem;margin-top:0">Which 2027 DLC can I play on my console?</h2>'
            f'<p class="muted">Tap your console. The list updates, and your choice is remembered on this device.</p>{_fchips}'
            f'<p class="mono amber" id="fg-count" aria-live="polite" style="margin:12px 0 0">{_dlc_n} expansions</p>'
            f'<div class="btns" style="margin-top:10px;display:flex;gap:8px;flex-wrap:wrap"><button class="btn sm" type="button" id="fg-add">Add the tracked ones to my ★ list</button>'
            f'<a class="btn line sm" href="{href("backlog-planner-2027.html", 0)}">Plan my 2027 backlog</a></div></div></div></section>'
            + AD.format("dlc-mid") +
            f'<section><div class="wrap"><div class="sec-head"><h2>What DLC is coming out in 2027?</h2><span class="muted">{_dlc_n}</span></div>'
            f'<p class="muted">In release order. Expansions with only a year sit at the end.</p>'
            f'<div class="out" id="fg-list" style="margin-bottom:10px">{"".join(r[2] for r in _dlc_rows)}'
            f'<div class="row"><span class="mono amber">STILL TO COME IN DECEMBER 2026</span></div>{"".join(_dlcx(x) for x in DLC_DEC)}</div>'
            f'<p class="empty" id="fg-none" hidden>No tracked expansion is confirmed for that console yet.</p>'
            f'<div class="cdw"><span class="lbl">Countdown to Guild Wars Afterlife</span><div class="cd" data-countdown="2027-01-13">'
            '<div class="cd-unit"><span class="flaps" data-u="0"></span><span>Days</span></div><div class="cd-unit"><span class="flaps" data-u="1"></span><span>Hrs</span></div>'
            '<div class="cd-unit"><span class="flaps" data-u="2"></span><span>Min</span></div><div class="cd-unit"><span class="flaps" data-u="3"></span><span>Sec</span></div></div></div>'
            f'<div class="sec-head" style="margin-top:28px"><h2>When does the new Witcher 3 DLC come out?</h2></div>'
            f'<p>In 2027. <a href="{href("games/the-witcher-3-songs-of-the-past.html", 0)}">The Witcher 3: Songs of the Past</a> is a new paid expansion starring Geralt, made with Fool\'s Theory, for PS5, Xbox Series X|S, PC and Switch 2. CD Projekt has not given a month. The Witcher 4 is a separate game, not expected before 2028.</p>'
            f'<div class="sec-head" style="margin-top:28px"><h2>Is there new Starfield DLC in 2027?</h2></div>'
            f'<p>Yes, in a loose sense: Bethesda has said more Starfield story content is coming in 2027, after Shattered Space (2024) and the PS5 launch on 7 April 2026. It has no name or date beyond the year, so we will move it up the list when Bethesda gives one.</p>'
            f'<div class="sec-head" style="margin-top:28px"><h2>Is there Cyberpunk 2077 DLC in 2027?</h2></div>'
            f'<p>No. CD Projekt Red has not announced any expansion after Phantom Liberty (2023). Its team is on the sequel, Cyberpunk 2, which is in pre-production with no date. For similar games while you wait, see <a href="{href("games-like-cyberpunk-2077.html", 0)}">games like Cyberpunk 2077</a>.</p>'
            f'<div class="sec-head" style="margin-top:28px"><h2>When is the next Pokémon Pokopia DLC?</h2></div>'
            f'<p>Expansion Pass Part 2, Dazzling Decorations, arrives on <strong>9 December 2026</strong> on Switch 2. Part 3, the last one, is due in 2027 with no name or date yet.</p>'
            f'<div class="sec-head" style="margin-top:28px"><h2>When does the Monster Hunter Wilds expansion come out?</h2></div>'
            f'<p>In 2027 on PS5, Xbox Series X|S and PC. <a href="{href("games/monster-hunter-wilds-ascendance.html", 0)}">Monster Hunter Wilds: Ascendance</a> adds Master Rank and returning Elder Dragons. Capcom has not given a month.</p>'
            f'<div class="sec-head" style="margin-top:28px"><h2>When does the Final Fantasy XIV Evercold expansion come out?</h2></div>'
            f'<p>On 23 February 2027, with early access from 19 February, on PS5, Xbox Series X|S, PC and Switch 2. See <a href="{href("games/final-fantasy-xiv-evercold.html", 0)}">the Evercold page</a> for the delay history.</p>'
            f'<div class="sec-head" style="margin-top:28px"><h2>When does Civilization 7 Earthrise come out?</h2></div>'
            f'<p>In 2027. Firaxis announced Earthrise, Civilization VII\'s first paid expansion, in September 2026, alongside the free Arc of Tomorrow update that adds a fourth age, the Atomic Age. More on <a href="{href("strategy-games-2027.html", 0)}">strategy games of 2027</a>.</p>'
            f'<div class="sec-head" style="margin-top:28px"><h2>When does Guild Wars Afterlife come out?</h2></div>'
            f'<p>On 13 January 2027. It is the first new paid DLC for the original Guild Wars in nearly 20 years, adds a randomised dungeon mode and needs Guild Wars Reforged.</p>'
            f'<div class="sec-head" style="margin-top:28px"><h2>Related pages and tools</h2></div><ul>'
            f'<li><a href="{href("remakes-2027.html", 0)}">Upcoming remakes and remasters of 2027</a></li>'
            f'<li><a href="{href("rpgs-2027.html", 0)}">Every RPG of 2027</a></li>'
            f'<li><a href="{href("backlog-planner-2027.html", 0)}">2027 backlog planner</a></li>'
            f'<li><a href="{href("steam-sale-dates.html", 0)}">Steam sale dates</a>: when the base games go on sale</li>'
            f'<li><a href="{href("countdown.html", 0)}">Game release countdown</a></li></ul></div></section>')
dlc_faq = [("What DLC is coming out in 2027?", "Guild Wars Afterlife (13 Jan), Final Fantasy XIV: Evercold (23 Feb), The Witcher 3: Songs of the Past, Monster Hunter Wilds: Ascendance, Civilization VII: Earthrise, Pokopia Expansion Pass Part 3 and new Starfield story content (2027)."),
           ("When does the new Witcher 3 DLC come out?", "Songs of the Past is due in 2027 on PS5, Xbox Series X|S, PC and Switch 2. No month yet."),
           ("Is there new Starfield DLC in 2027?", "Bethesda says more Starfield story content is coming in 2027. No name or exact date yet."),
           ("Is there Cyberpunk 2077 DLC in 2027?", "No. No expansion after Phantom Liberty is announced; CD Projekt Red is working on Cyberpunk 2."),
           ("When is the next Pokopia DLC?", "Expansion Pass Part 2: Dazzling Decorations on 9 December 2026. Part 3 follows in 2027."),
           ("When does Civilization 7 Earthrise come out?", "In 2027. Firaxis has not given a month.")]
page("dlc-2027.html", "DLC 2027: Every Expansion Coming (Witcher 3, Starfield, More)",
     "Every DLC and expansion coming in 2027: Witcher 3 Songs of the Past, Monster Hunter Wilds Ascendance, FFXIV Evercold, Starfield, Civ VII Earthrise and Pokopia.",
     dlc_body, 0, dlc_faq, crumbs=[("Home", DOMAIN + "/"), ("2027 games by genre", canon("games-by-genre-2027.html")), ("DLC 2027", canon("dlc-2027.html"))])

# ---------------- GAMES LIKE HITMAN (28 Nov 2026, demand: "games like hitman", "hitman 4 release date", "hitman classic trilogy remastered release date", DEMAND N78) ----------------
# Evidence: GamesRadar+ US/UK/AU best stealth games, GameSpot "Best Stealth Games: Hitman, Splinter Cell", GamingScan "best games like Hitman", Beebom 2026.
# Facts: Hitman 4 confirmed to come after Bond, no date (PC Gamer, Push Square Dec 2025, Wccftech). Hitman Classic Trilogy Remastered 2027 (Xbox Wire, Gematsu, VGC).
LIKE_HM = [
    ("Hitman: World of Assassination", "PS5, PS4, Xbox Series X|S, Xbox One, PC", "All three modern Hitman games in one: huge sandbox levels, disguises and dozens of ways to reach each target.", "ps5 ps4 xbox pc", "sandbox disguise stealth"),
    ("007 First Light", "PS5, Xbox Series X|S, PC (Switch 2 on 18 March 2027)", "IO Interactive's young James Bond story: Hitman-style infiltration and disguises with more action and gadgets.", "ps5 xbox pc", "spy disguise stealth"),
    ("Dishonored 2", "PS4, Xbox One, PC (plays on PS5 and Xbox Series)", "Assassinate targets with magic powers in an open city, or clear every mission without killing anyone.", "ps5 ps4 xbox pc", "sandbox stealth"),
    ("Deus Ex: Mankind Divided", "PS4, Xbox One, PC (plays on PS5 and Xbox Series)", "Cyberpunk spy RPG with wide hub levels you can sneak, hack or talk your way through.", "ps5 ps4 xbox pc", "sandbox spy stealth"),
    ("Metal Gear Solid V: The Phantom Pain", "PS4, Xbox One, PC (plays on PS5 and Xbox Series)", "Open-world bases to infiltrate any way you like, with a huge toolbox of gadgets.", "ps5 ps4 xbox pc", "sandbox spy stealth"),
    ("Metal Gear Solid Delta: Snake Eater", "PS5, Xbox Series X|S, PC", "The 2025 remake of MGS3: jungle stealth, camouflage and a Cold War spy story.", "ps5 xbox pc", "spy stealth"),
    ("Metal Gear Solid: Master Collection Vol. 1", "PS5, PS4, Xbox Series X|S, Switch, PC", "The first three Metal Gear Solid games, including the original MGS3, in one package.", "ps5 ps4 xbox pc switch", "spy stealth"),
    ("Sniper Elite: Resistance", "PS5, PS4, Xbox Series X|S, Xbox One, PC", "Big open WWII maps with a main target to hunt, plus slow-motion sniper kill cams.", "ps5 ps4 xbox pc", "sandbox sniper stealth"),
    ("Shadow Tactics: Blades of the Shogun", "PS4, Xbox One, PC (plays on PS5 and Xbox Series)", "Top-down stealth tactics: plan assassinations with five ninja specialists.", "ps5 ps4 xbox pc", "sandbox stealth"),
    ("Splinter Cell: Blacklist", "PC, Xbox 360 (plays on Xbox Series and Xbox One)", "Sam Fisher's last outing: spy missions you can play as a ghost or a panther.", "xbox pc", "spy stealth"),
    ("Assassin's Creed Shadows", "PS5, Xbox Series X|S, PC, Switch 2", "Play as the shinobi Naoe for pure stealth: hide in shadows and pick off targets in feudal Japan.", "ps5 xbox pc switch", "stealth"),
]
_HM_LABEL = {"sandbox": "Sandbox levels", "disguise": "Disguises", "stealth": "Stealth kills", "spy": "Spy story", "sniper": "Sniping"}
HM_SOON = ["hitman-classic-trilogy-remastered", "007-first-light", "spyder-agent-8"]
_hm_soon = sorted([g for g in GAMES if g["slug"] in HM_SOON], key=lambda g: (g["month"] or 13, g["date"] or "9999"))
_hm_first = next((g for g in _hm_soon if g["date"]), None)
def _hm_on(tag): return [x[0] for x in LIKE_HM if tag in x[3].split()]
_hm_quick = ("The best games like Hitman are 007 First Light (from the same studio), Dishonored 2, Deus Ex: Mankind Divided, Metal Gear Solid V and Sniper Elite: Resistance. "
             "Hitman Classic Trilogy Remastered is due in 2027; Hitman 4 is confirmed to come after 007 First Light but has no date.")
hm_body = (f'<header class="hero"><div class="wrap"><span class="kicker">Games like Hitman</span>'
           f'<h1>Games like Hitman:<br><span class="amber">sandbox stealth now, Agent 47 in 2027.</span></h1>'
           f'<p class="lead">Assassination sandboxes, disguises and spy stealth on PS5, Xbox, Switch 2 and PC, filtered by what you love about Hitman, plus the 2027 Hitman remaster and the Hitman 4 news.</p>'
           f'<p class="muted" style="margin:0">Last checked {e(UPDATED)} · {len(LIKE_HM)} picks out now · {len(_hm_soon)} coming in 2027</p></div></header>'
           f'<section><div class="wrap"><div class="out" style="margin-bottom:12px"><div class="row"><span><strong>Quick answer:</strong> {e(_hm_quick)}</span></div></div>'
           f'<div class="tool" id="er-tool" style="margin-bottom:24px"><h2 style="font-size:1.5rem;margin-top:0">Which game like Hitman should I play?</h2>'
           f'<p class="muted">Pick your platform and what you love most. Your choice is remembered on this device.</p>{_like_chips(_HM_LABEL, "What you love")}'
           f'<p class="mono amber" id="er-count" aria-live="polite" style="margin:12px 0 0">{len(LIKE_HM)} games</p></div>'
           f'<div class="sec-head"><h2>What games are like Hitman?</h2><span class="muted">out now</span></div>'
           f'<div class="out" id="er-list" style="margin-bottom:10px">{_like_rows(LIKE_HM, _HM_LABEL)}</div><p class="empty" id="er-none" hidden>No pick matches both. Try "Anything".</p></div></section>'
           + AD.format("hm-mid") +
           f'<section><div class="wrap"><div class="sec-head"><h2>When does Hitman Classic Trilogy Remastered come out?</h2></div>'
           f'<p>In <strong>2027</strong> on PS5, Xbox Series X|S and PC, with no month yet. Saber Interactive is remastering the first three games, Codename 47, Silent Assassin and Contracts, with improved graphics. No Switch 2 version is announced. It is one of the <a href="{href("remakes-2027.html", 0)}">remakes and remasters of 2027</a>.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>Is there going to be a Hitman 4?</h2></div>'
           f'<p>Yes, but there is no date. IO Interactive\'s CEO has said "of course" there will be a next Hitman once 007 First Light is done (PC Gamer, Push Square). It is not announced as a game yet, so do not expect it in 2027.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>Is 007 First Light like Hitman?</h2></div>'
           f'<p>Yes, more than any other game. IO Interactive, the Hitman studio, made it, and missions mix disguises, social stealth and sandbox routes with louder Bond action. It is out on PS5, Xbox Series X|S and PC; the <a href="{href("games/007-first-light.html", 0)}">Switch 2 version</a> comes on 18 March 2027.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>What stealth games come out in 2027?</h2><span class="muted">{len(_hm_soon)}</span></div>'
           f'<div class="out" style="margin-bottom:10px">{"".join(_er_srow(g) for g in _hm_soon)}</div>{_like_cd(_hm_first)}'
           f'<p class="muted">Sooner than that, Nightdive\'s Thief: The Dark Project Remastered lands on 3 December 2026. More stealth and action picks on <a href="{href("games-like-assassins-creed.html", 0)}">games like Assassin\'s Creed</a>.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>What games are like Hitman on Switch and Switch 2?</h2></div>'
           f'<p>{e(_and(_hm_on("switch")))}. 007 First Light joins them on Switch 2 on 18 March 2027.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>What games are like Hitman on PS5, Xbox and PC?</h2></div>'
           f'<p>PS5: {e(_and(_hm_on("ps5")))}. Xbox: {e(_and(_hm_on("xbox")))}. PC: {e(_and(_hm_on("pc")))}.</p>'
           f'<div class="sec-head" style="margin-top:28px"><h2>Related pages and tools</h2></div><ul>'
           f'<li><a href="{href("games-like-assassins-creed.html", 0)}">Games like Assassin\'s Creed</a>: stealth and parkour</li>'
           f'<li><a href="{href("games/007-first-light.html", 0)}">007 First Light on Switch 2</a>: date and countdown</li>'
           f'<li><a href="{href("remakes-2027.html", 0)}">Remakes and remasters of 2027</a></li>'
           f'<li><a href="{href("release-clashes-2027.html", 0)}">2027 release clash finder</a></li>'
           f'<li><a href="{href("countdown.html", 0)}">Game release countdown</a></li></ul></div></section>')
hm_faq = [("What games are like Hitman?", _and([x[0] for x in LIKE_HM]) + "."),
          ("When does Hitman Classic Trilogy Remastered come out?", "In 2027 on PS5, Xbox Series X|S and PC. No month yet."),
          ("Is there going to be a Hitman 4?", "IO Interactive says there will be a next Hitman after 007 First Light, but it has not been announced and has no date."),
          ("Is 007 First Light like Hitman?", "Yes. It is made by IO Interactive and uses disguises and sandbox stealth, with more action."),
          ("What stealth games come out in 2027?", _and([g["title"] + " (" + nice_date(g) + ")" for g in _hm_soon]) + ".")]
page("games-like-hitman.html", "Games Like Hitman: 11 Picks & Hitman Trilogy Remaster 2027",
     "Games like Hitman on PS5, Xbox, Switch 2 and PC: 007 First Light, Dishonored 2, Deus Ex, MGS V, Sniper Elite, plus the Hitman trilogy remaster and Hitman 4 news",
     hm_body, 0, hm_faq, crumbs=[("Home", DOMAIN + "/"), ("2027 games by genre", canon("games-by-genre-2027.html")), ("Games like Hitman", canon("games-like-hitman.html"))])

# ---------------- SEO files ----------------
page("thanks.html", "Check your inbox | DayOneDrop", "Confirm your email to get the free 2027 release calendar.", NL_THANKS)
page("welcome.html", "Your 2027 release calendar | DayOneDrop", "Download your free 2027 game release calendar.", NL_WELCOME)


# ---------------- GAMES 2028 (28 Nov 2026, demand: "games coming out in 2028", "upcoming games 2028"; COMPETITOR WATCH 28 Nov gap 4: GamesRadar has 2028 sections) ----------------
# Only games whose maker (or its boss on record) has said 2028, each with 2+ trusted outlets:
# The Witcher 4: CD Projekt co-CEO, Aug 2026 (PC Gamer, GamesRadar+, Game Informer, Push Square).
# Tomb Raider: Catalyst: Amazon Games' Jeffrey Gattis, Jul 2026 (PC Gamer, VGC, Push Square, Pure Xbox, Kotaku).
# ARK 2: Studio Wildcard, Dec 2025 (VGC, PC Gamer, Pure Xbox, Kotaku).
# Next consoles: Microsoft's 2023 FTC filing named 2028 (GamesRadar+, TechRadar). Neither is announced.
G28 = [("The Witcher 4", "CD Projekt Red", "Open-world action RPG. Ciri leads a new Witcher saga. More than 500 developers work on it.",
        "Not announced", "2028 (target)", "CD Projekt's joint CEO said in August 2026 it is targeting 2028.", "games-like-the-witcher-3.html"),
       ("Tomb Raider: Catalyst", "Crystal Dynamics / Amazon Games", "The next new Lara Croft adventure, after the Legacy of Atlantis remake.",
        "PS5, Xbox Series X|S, PC", "2028", "Announced for 2027 at The Game Awards 2025. Amazon Games' Jeffrey Gattis said in July 2026 it will follow in 2028.", "games/tomb-raider-legacy-of-atlantis.html"),
       ("ARK 2", "Studio Wildcard", "Sci-fi dinosaur-taming survival sequel, first shown in 2020.",
        "Xbox Series X|S, PC", "2028", "Studio Wildcard moved it to 2028 in December 2025 and is testing new ideas in ARK: Survival Ascended first.", None)]
G28_MAYBE = [("The Elder Scrolls VI", "Bethesda", "No year announced. Not on our 2027 board."),
             ("Intergalactic: The Heretic Prophet", "Naughty Dog", "No year announced. Reports disagree on 2027 or later."),
             ("Cyberpunk 2", "CD Projekt Red", "In early development. No year announced."),
             ("Next Xbox and PlayStation 6", "Microsoft / Sony", "Not announced. Microsoft's 2023 court filing said it expected the next generation in 2028.")]
_g28_quick = ("Three games are officially aimed at 2028 so far: The Witcher 4 (CD Projekt's target), Tomb Raider: Catalyst (moved from 2027) and ARK 2. "
              "None has a month or day yet. The next Xbox and PlayStation 6 are also widely expected around 2028, but neither is announced.")
_g28_rows = "".join(f'<div class="row"><span><strong>' + (f'<a href="{href(lk, 0)}">{e(t)}</a>' if lk else e(t)) + f'</strong><br><span class="muted">{e(ab)}</span>'
                    f'<br><span class="muted">{e(dv)} · {e(pl)}</span><br><span class="muted">{e(why)}</span></span><b>{e(w)}</b></div>' for t, dv, ab, pl, w, why, lk in G28)
_g28_maybe = "".join(f'<div class="row"><span><strong>{e(t)}</strong><br><span class="muted">{e(dv)} · {e(n)}</span></span><b>TBA</b></div>' for t, dv, n in G28_MAYBE)
_g28_moved_mv = "".join(f'<div class="row"><span><strong>{e(t)}</strong><br><span class="muted">Film · was {e(a)}. {e(why)}</span></span><b>{e(b)}</b></div>' for t, a, b, why in MV_OUT)
_g28_tba27 = [g for g in GAMES if not g["date"] and g["window"] == "2027"]
_g28_cd = ('<div class="cdw"><span class="lbl">Countdown to 1 January 2028</span><div class="cd" data-countdown="2028-01-01">'
           '<div class="cd-unit"><span class="flaps" data-u="0"></span><span>Days</span></div><div class="cd-unit"><span class="flaps" data-u="1"></span><span>Hrs</span></div>'
           '<div class="cd-unit"><span class="flaps" data-u="2"></span><span>Min</span></div><div class="cd-unit"><span class="flaps" data-u="3"></span><span>Sec</span></div></div></div>')
_g28_body = (f'<header class="hero"><div class="wrap"><span class="kicker">2028 games</span>'
             f'<h1>Games coming out in 2028:<br><span class="amber">what is confirmed so far.</span></h1>'
             f'<p class="lead">The games their makers have already aimed at 2028, the 2027 games that moved there, and the big names with no year yet. We only list a 2028 game when the studio or publisher says so on record.</p>'
             f'<p class="muted" style="margin:0">Last checked {e(UPDATED)} · {len(G28)} games aimed at 2028 · each backed by the maker plus two trusted outlets</p></div></header>'
             f'<section><div class="wrap"><div class="out" style="margin-bottom:24px"><div class="row"><span><strong>Quick answer:</strong> {e(_g28_quick)}</span></div></div>'
             f'<div class="sec-head"><h2>What games are coming out in 2028?</h2><span class="muted">{len(G28)}</span></div>'
             f'<div class="out" style="margin-bottom:10px">{_g28_rows}</div>{_g28_cd}'
             + AD.format("g28-mid") +
             f'<div class="sec-head" style="margin-top:28px"><h2>When does The Witcher 4 come out?</h2></div>'
             f'<p>CD Projekt Red is targeting 2028. Joint CEO Michał Nowakowski said so in a video before gamescom in August 2026, calling it the studio\'s "biggest, boldest" game. There is no month, and no platforms have been confirmed. The next new Witcher content is the <a href="{href("games/the-witcher-3-songs-of-the-past.html", 0)}">Songs of the Past expansion</a> for The Witcher 3 in 2027.</p>'
             f'<div class="sec-head" style="margin-top:28px"><h2>Is Tomb Raider: Catalyst delayed to 2028?</h2></div>'
             f'<p>Yes. It was announced at The Game Awards 2025 for 2027. In July 2026, Amazon Games\' Jeffrey Gattis said the next Tomb Raider would "follow on in 2028" (PC Gamer, VGC, Push Square). The 2027 Tomb Raider is now <a href="{href("games/tomb-raider-legacy-of-atlantis.html", 0)}">Tomb Raider: Legacy of Atlantis</a>, a remake of the first game, on 12 February 2027.</p>'
             f'<div class="sec-head" style="margin-top:28px"><h2>When does ARK 2 come out?</h2></div>'
             f'<p>In 2028 on Xbox Series X|S and PC, after another delay announced in December 2025 (VGC, PC Gamer, Pure Xbox). It was first revealed in 2020. No PS5 version has been confirmed.</p>'
             f'<div class="sec-head" style="margin-top:28px"><h2>Will the PS6 and next Xbox come out in 2028?</h2></div>'
             f'<p>Possibly, but neither is announced. Microsoft told regulators in 2023 that it expected the next console generation in 2028 (GamesRadar+, TechRadar). Sony has not given a year. Until either is revealed, every game on this page is planned for today\'s consoles and PC.</p>'
             f'<div class="sec-head" style="margin-top:28px"><h2>Which big games have no year yet?</h2><span class="muted">{len(G28_MAYBE)}</span></div>'
             f'<p class="muted">Often searched as 2028 games, but nothing official says so. We move each one onto a board the day its maker gives a year.</p>'
             f'<div class="out" style="margin-bottom:10px">{_g28_maybe}</div>'
             f'<div class="sec-head" style="margin-top:28px"><h2>Which 2027 games could slip to 2028?</h2><span class="muted">{len(_g28_tba27)}</span></div>'
             f'<p>The ones most at risk are games with only "2027" and no month: {e(_and([g["title"] for g in _g28_tba27]))}. If one moves, it lands on this page and on our <a href="{href("delayed-games-2027.html", 0)}">delay tracker</a>.</p>'
             f'<div class="sec-head" style="margin-top:28px"><h2>Which 2027 movies moved to 2028?</h2><span class="muted">{len(MV_OUT)}</span></div>'
             f'<div class="out" style="margin-bottom:10px">{_g28_moved_mv}</div>'
             f'<div class="sec-head" style="margin-top:28px"><h2>Related pages and tools</h2></div><ul>'
             f'<li><a href="{href("biggest-games-2027.html", 0)}">Biggest games of 2027</a>: what you can play before 2028</li>'
             f'<li><a href="{href("games-without-release-date-2027.html", 0)}">2027 games with no release date yet</a></li>'
             f'<li><a href="{href("delayed-games-2027.html", 0)}">Every delayed game of 2027</a></li>'
             f'<li><a href="{href("calendar.html", 0)}">2027 release calendar</a></li></ul></div></section>')
g28_faq = [("What games are coming out in 2028?", "So far: The Witcher 4 (CD Projekt's 2028 target), Tomb Raider: Catalyst (moved from 2027) and ARK 2. None has an exact date."),
           ("When does The Witcher 4 come out?", "CD Projekt Red is targeting 2028. There is no month or platform list yet."),
           ("Is Tomb Raider Catalyst delayed?", "Yes. It was planned for 2027 and Amazon Games now says 2028. Tomb Raider: Legacy of Atlantis still comes out on 12 February 2027."),
           ("When does ARK 2 come out?", "In 2028 on Xbox Series X|S and PC, per Studio Wildcard."),
           ("Is The Elder Scrolls 6 coming out in 2028?", "Bethesda has not given a year, so nobody knows yet."),
           ("Will the PS6 come out in 2028?", "Sony has not announced it. Microsoft said in 2023 that it expected the next generation in 2028.")]
page("games-2028.html", "Games Coming Out in 2028: Every Confirmed Game So Far",
     "Games coming out in 2028: The Witcher 4 (2028 target), Tomb Raider: Catalyst (delayed from 2027) and ARK 2, plus big games with no year and PS6 news."[:160],
     _g28_body, 0, g28_faq, crumbs=[("Home", DOMAIN + "/"), ("All games", canon("games.html")), ("Games 2028", canon("games-2028.html"))])


urls = ["index.html", "shooter-games-2027.html", "games-2028.html", "remakes-2027.html", "dlc-2027.html", "games-like-hitman.html", "games-like-assassins-creed.html", "strategy-games-2027.html", "games-like-ghost-of-tsushima.html", "games-like-monster-hunter.html", "games-like-god-of-war.html", "games-like-mass-effect.html", "games-like-silent-hill.html", "games-like-resident-evil.html", "games-like-final-fantasy.html", "games-like-red-dead-redemption-2.html", "games-like-cyberpunk-2077.html", "games-like-persona.html", "games-like-hades.html", "games-like-the-witcher-3.html", "games-like-palworld.html", "games-like-skyrim.html", "games-like-fortnite.html", "games-like-baldurs-gate-3.html", "games-like-animal-crossing.html", "games-like-pokemon.html", "games-like-minecraft.html", "games-like-stardew-valley.html", "games-like-zelda.html", "movies-january-2027.html", "games-like-hollow-knight.html", "movies-december-2026.html", "winter-2027-anime.html", "new-tv-shows-january-2027.html", "black-friday-game-sales-2026.html", "gta-6-pc-release-date.html", "new-tv-shows-december-2026.html", "movies-2027.html", "games-like-elden-ring.html", "countdown.html", "games-without-release-date-2027.html", "steam-sale-dates.html", "nintendo-direct.html", "ps-plus-monthly-games.html", "epic-free-games.html", "after-gta-6.html", "games-like-gta-6.html", "delayed-games-2027.html", "release-clashes-2027.html", "exclusives-2027.html", "rpgs-2027.html", "game-pass-2027.html", "backlog-planner-2027.html", "biggest-games-2027.html", "game-awards-2026.html", "games-december-2026.html", "new-games-this-week.html", "last-gen-games-2027.html", "games-by-genre-2027.html", "horror-games-2027.html", "fighting-games-2027.html", "xbox-games-showcase-2027.html", "calendar.html", "later-2027.html", "games.html", "tools.html", "about.html", "privacy.html"] + ["games/" + g["slug"] + ".html" for g in featured] + plat_urls + month_urls
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
