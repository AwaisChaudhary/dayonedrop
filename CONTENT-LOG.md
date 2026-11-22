# DayOneDrop content log

## 2026-11-18 (launch)
- Built the site: home departures board (15 games), 2027 calendar with Google/Apple/Outlook reminders, all-games page, tools page (console lineup, my launch list, busiest months), about, privacy, 404.
- Game guides: Tomb Raider: Legacy of Atlantis, Persona 4 Revival, Fable, Exodus, Final Fantasy VII Revelation, God of War: Laufey.
- Dates use only facts confirmed by 2+ sources (release lists from PC Gamer, Startselect, Sportsdigest, Sortiraparis, FandomWire, Driffle, G2A). Metro 2039 kept as "February 2027" (exact day from one source only). Wo Long 2 kept as "Early 2027". Kingdom Hearts IV "Late 2027".
- Domain: https://getdayonedrop.com
- 2026-11-18: Added Google Analytics (G-2NJQ0RSMTP) to every page. Cloudflare Pages project dayonedrop live; domain getdayonedrop.com connected; sitemap submitted in Search Console.
- 2026-11-18: Added AdSense script (ca-pub-1558743317014653) to every page and real ads.txt line.

## 2026-11-19 (manual run; scheduled runs had not been saving since launch)
- Data: Metro 2039 dated 4 Feb 2027 (State of Play, Sep 2026; 80.lv, Gfinity, Insider Gaming). Wo Long 2 dated 4 Mar 2027 (Gematsu, RPG Site, Dexerto). Platforms filled for every game: Persona 4 Revival (PS5/Xbox/PC 18 Feb, Switch 2 20 May; RPG Site, Gematsu), Atelier Karia, Eternal Anima, Trine 6, Wo Long 2, Kingdom Hearts IV (all four platforms); Grave Seasons, Road Kings, Mariachi Legends (PS5/Xbox/PC); God of War Laufey (PS5 only). Sources: Gematsu, RPG Site, VGC, Push Square, Nintendo Life, Shacknews, publisher sites.
- New pages: /platforms/ps5, /platforms/xbox-series, /platforms/pc, /platforms/switch-2 ("every X game coming in 2027": grouped by month, next-launch countdown, exclusives FAQ). Linked from footer ("By console") and Tools page. Tools FAQ now generated from data.
- Fixed both DayOneDrop scheduled tasks so failures are reported instead of ending silently.

## 2026-11-19 21:10 PKT (manual data load)
- Board grew from 15 to 44 games. Added 22 dated launches (Jan-Mar 2027) and 7 confirmed-window games, each with date AND platforms matching on Game Informer's 2027 schedule plus at least one of GameSpot, GamesRadar, Shacknews, Game Rant, Loot Level Chill, Gaming Route, GameTechReport or Wikipedia. Highlights: Metroid Ravenous, Until Dawn 2, Witchbrook, Tropico 7, Warhammer 40,000: Dark Heresy, Forza Horizon 6 (PS5), Titan Quest II, Stranger Than Heaven, 007 First Light (Switch 2), Hyrule Warriors AoC DE, Pokémon Winds and Waves, Kirby and the World Beyond, Xenoblade Genesis, Spyro: A Realm Beyond, The Expanse: Osiris Reborn, Squadron 42.
- Left out where sources disagreed: Wandering Sword (20 vs 21 Jan), Fate/Extra Record (platforms), Romancing SaGa 3 (date), FF XIV Evercold (date), Melty Blood and Rustown (one source only).
- Platform pages, calendar, board and tools all regenerate from the data.
- 2026-11-19: diagnostic run, push test.

## 2026-11-20 09:15 PKT (manual data check; the 8:41 AM scheduled run finished without saving)
- Added Shadow of the Road: delayed from 12 Nov 2026 to 10 Mar 2027, PC (Steam/Epic/GOG). Sources: Gematsu, Windows Central, RPGamer, CGMagazine.
- Added Lords of the Fallen II: early 2027 (first quarter), PS5/Xbox Series X|S/PC/Switch 2. Sources: Game Informer (platforms, 2027), PC Gamer and Digital Citizen (Q1 2027).
- Left out: Warhammer Blood Bowl (sources split between "spring 2027" and "early 2027"); The Duskbloods, Blighted, Bloodstained: The Scarlet Engagement, Dragon Ball Xenoverse 3, Rev.Noir (only "2027", no month or window yet).
- Board: 46 games.

## 2026-11-20 17:00 PKT (manual traffic pass)
- New month pages: /months/january-2027 ... (every month with 3+ games: Jan, Feb, Mar, Apr, Jun, Dec). Each lists every release date in order, consoles, delays, busiest week, prev/next links. Linked from calendar month headings and a new "By month" footer column. Targets "january 2027 game releases", "games coming out february 2027" etc.
- New game guide pages: Until Dawn 2, Metroid Ravenous, Forza Horizon 6 (PS5), Witchbrook (facts from PlayStation Blog/Gematsu/Shacknews, Nintendo.com/Gematsu/GosuGamers, Playground via Gematsu/VGChartz/PSU, Chucklefish via Shacknews/Game Informer/VGChartz), plus Metro 2039 and Wo Long 2 (already had 3 facts).
- Forza Horizon 6 PS5 and Witchbrook marked delayed (both moved from 2026 windows).
- Bing Webmaster Tools: site verified, sitemap and 14 URLs submitted.

## 2026-11-21 19:55 PKT (main chat)
- New page /after-gta-6 "What to play after GTA 6: the big games of 2027" (10 picks from games.json, quick answer, FAQ), linked from the footer on every page. Rides the GTA 6 launch wave; NeonCoast (sister site, ~700+ visitors/day) links here from its ending, completion and footer.
- Note: the scheduled DayOneDrop SEO runs have pushed nothing since 20 Nov 17:00 PKT (runs report success but no commit). Investigating.
- New page /delayed-games-2027 (delay tracker built from games.json status/history; quick answer + FAQ), linked in footer and from /after-gta-6.

## 2026-11-22 (scheduled SEO run)
- New page /release-clashes-2027 "2027 release clashes: which games launch the same week?": quick answer, every Mon-Sun week with 2+ dated games (busiest first), same-day launches, busiest week per console, and an interactive "Do my games clash?" checker (tick games or load your ★ list, pick a 0/7/14/30-day gap; lists clashing pairs and days between launches). Built only from games.json dates. Targets "games releasing same day 2027", "busiest week for game releases 2027", "January 28 2027 games". Linked from footer (every page), Tools page and every month page.
- Refreshed /tools: quick answer box, "Last checked" date, question-style H2s, new clash finder card (top 3 crowded weeks), "More ways to plan" links, extra FAQ on the busiest week. Fixed tool grid min width for narrow phones.
- Researched but not added: Baptiste (delayed to 25 Mar 2027, Gematsu only so far, needs a second source); Fable Game Pass day one page (not enough confirmed day-one titles for a solid list yet).

## 2026-11-22 (scheduled SEO run, second pass)
- New page /exclusives-2027 "2027 console exclusives: which games are only on one console?": quick answer, PS5/Xbox/PC/Switch 2-only lists (question H2s), a "late ports, not exclusives" section (Forza Horizon 6 PS5, 007 First Light Switch 2), which games skip each console, games on every console, a full game-by-console matrix, and an interactive "Which 2027 games will I miss?" tool (tap the consoles you own: playable count, missed games, best extra console; remembered on the device). Targets "PS5 exclusives 2027", "Switch 2 exclusives 2027", "are there Xbox exclusives in 2027", "is Forza Horizon 6 a PS5 exclusive". Linked from footer, Tools page and every platform page. Built from games.json; Fable on Xbox/PS5/PC + Game Pass day one per Gematsu, RPG Site, VGChartz.
- Refreshed platform pages (/platforms/ps5, xbox-series, pc, switch-2): quick answer box, ports no longer shown as "Only on" (fixes Forza Horizon 6 PS5 and 007 First Light Switch 2 being implied exclusives), new "not coming to this console" FAQ, related-links section.
- Data: 007 First Light (Switch 2) marked delayed to 18 March 2027 with facts/history (Gematsu, Nintendo Life, VGC, Shacknews); dev IO Interactive.

## 2026-11-22 (scheduled SEO run, third pass)
- New page /rpgs-2027 "Every RPG coming in 2027": quick answer, all 18 tracked RPGs grouped by month (question H2s), interactive "Which 2027 RPGs can I play?" filter (console + action vs JRPG/tactical/classic), the busiest 30-day RPG crunch (28 Jan to 25 Feb 2027, 6 RPGs), RPG count per console with console-only RPGs, FAQ JSON-LD. Built only from games.json. Targets "upcoming RPGs 2027", "RPGs coming out 2027", "2027 JRPGs", "Switch 2 RPGs 2027" (RPG Site and Wccftech both run "RPGs of 2027" features, so demand is there). Linked from footer (every page), Tools page and /after-gta-6.
- Refreshed /after-gta-6: question-style H2s, new "Which of these can I play on my console?" breakdown per console, two new FAQs (PS5 picks, closest crime game), related pages/tools section.
- CSS: [hidden] now always hides (used by the RPG filter).

## 2026-11-22 (scheduled data check, morning)
- Re-checked earlier "left out" games. Added 6 (board now 52):
  - Wandering Sword (console versions): 21 Jan 2027, PS5/Xbox Series X|S/Switch 2 (PC out since 2023). Gematsu, RPG Site, VGChartz now agree on the 21st. Marked delayed (from May 2026).
  - Fate/Extra Record: 28 Jan 2027, PS5/Switch 2/PC, no Xbox. Gematsu, VGChartz, RPG Site, PlayStation Blog.
  - Romancing SaGa 3: Destinies United: 4 Feb 2027 (moved up from 16 Feb), PS5/Xbox/PC/Switch 2. RPG Site, RPGamer, Siliconera, Square Enix press release.
  - Final Fantasy XIV: Evercold: 23 Feb 2027 (delayed from January 2027; early access 19 Feb). GamesRadar, Shacknews, Siliconera.
  - Demi and the Fractured Dream: 27 Feb 2027, PS5/Xbox/PC/Switch 2. Gematsu, Essential Japan; Annapurna site says February 2027.
  - No Rest for the Wicked (1.0 + PS5): March 2027, PS5/PC (Xbox/Switch 2 unconfirmed). Game Informer, Gematsu, Push Square.
- Left out: Warhammer Blood Bowl (still split "early 2027" PC Gamer vs "spring 2027" God is a Geek; no Switch 2); Baptiste (no second source for a 2027 date yet); At Fate's End, The Duskbloods, Bloodstained: The Scarlet Engagement, Blighted, Outward 2, Ontos (only "2027"); BECROWNED (Q1 2027, one source checked).
- To re-check: Spyro: A Realm Beyond. GosuGamers (citing Xbox Wire) says spring 2027, but we list mid 2027. Needs a second source before changing.
- No date changes for tracked window games (Lords of the Fallen II, Kingdom Hearts IV, Pokémon Winds and Waves, Kirby, Xenoblade Genesis, Squadron 42, The Expanse, Hunter: The Reckoning).

## 2026-11-22 (scheduled SEO run, fourth pass)
- New page /game-pass-2027 "Every 2027 game coming to Xbox Game Pass": quick answer, the 5 tracked Game Pass games with dates (Persona 4 Revival, Fable, Wo Long 2, Spyro, The Expanse), 9 more announced for Game Pass without a date (Bad Magpie, Join Us, Clockwork Revolution, Alien Deathstorm, Moosa: Dirty Fate, Senua, State of Decay 3, Valor Mortis, Vivarium), an interactive "Game Pass or buy?" checker (tick games or load your ★ list), which Game Pass games are also on PS5, which Xbox/PC games are not on Game Pass, FAQ JSON-LD. Sources: Pure Xbox (14 Jun 2026 and 29 Mar 2026 roundups) and Digital Citizen's 2027 Game Pass table; "day one" wording only for Fable and Wo Long 2. Left out Magicians: The Devil's Deal (Pure Xbox only). Targets "game pass 2027", "is Fable on Game Pass", "Persona 4 Revival Game Pass". Linked from footer (every page), Tools page, Xbox and PC platform pages, delayed page.
- Data: Spyro: A Realm Beyond now "Spring 2027" (was Mid 2027; Xbox Wire, GamingBolt, Wccftech, Gamereactor, Variety). The Expanse: Osiris Reborn now "Spring 2027" (Xbox Wire, GamesRadar, Gematsu, Push Square); dev Owlcat Games. Both moved to the April slot.
- Refreshed /delayed-games-2027: question-style H2s, "Which delayed games are on my console?" breakdown, "Which month do most delayed games land in?", two new FAQs, related pages section.

## NOTE (2026-11-22, main chat): IndexNow key file
- Key file /4bb4752d9cd1f0324bbb35f6c8afb9db.txt is in the site root (Bing IndexNow; Awais approved IndexNow on 22 Nov). Never delete or rename it.
- Pinging api.indexnow.org from scheduled runs needs approval, so runs should NOT try it; the main chat pings new pages.

## STANDING RULE (22 Nov 2026 16:05 PKT, Awais: "You don't need my approval, just do it"): IndexNow after every push
- After every push that adds or changes pages, ping IndexNow for each new/changed page (up to 10 per run, clean URLs) with WebFetch:
  https://api.indexnow.org/indexnow?url=https%3A%2F%2Fgetdayonedrop.com%2F<page>&key=4bb4752d9cd1f0324bbb35f6c8afb9db
- Awais approved these pings for all runs. An empty/binary response means accepted. If WebFetch is unavailable or the call is blocked, skip silently (don't retry) and list the pages under "IndexNow pending" in your CONTENT-LOG entry so the main chat can send them.
- Key file /4bb4752d9cd1f0324bbb35f6c8afb9db.txt must stay in the site root (never delete or rename it).

## 2026-11-22 (scheduled SEO run, fifth pass)
- New guide /games/stranger-than-heaven: 15 Jan 2027, PS5/Xbox Series X|S/PC (Steam, Microsoft Store), RGG Studio/SEGA, in Game Pass + Play Anywhere, 1915-1965 across Kokura/Kure/Osaka/Atami/Tokyo, Makoto Daito, Tupac/Snoop Dogg/Tori Kelly cast, editions; history incl. Project Century (TGA 2023) and rename (Xbox Showcase June 2025). Sources: Gematsu, RPG Site, VGChartz, Notebookcheck, VGC, Pure Xbox. Added to /game-pass-2027 (now the first dated Game Pass game of 2027; not labelled "day one", only one source says so).
- New guide /games/pokemon-winds-and-waves (slug renamed from pok-mon-winds-and-waves): 2027, no date, Switch 2 only, Gen 10, Game Freak, starters Browt/Pombon/Gecqua, islands + ocean, announced 27 Feb 2026. Sources: Nintendo, Gematsu, RPG Site, Nintendo Life, Game Informer. Targets "pokemon winds and waves release date", "is pokemon winds and waves on switch 1".
- Both linked from footer (every page), board/games grid and month/related lists.
- Refreshed all 14 game guide pages (template): Quick answer box, question H2s ("What do we know about X?", "Has X been delayed?", "What else launches in <month> 2027?"), optional sources line, per-game extra FAQs (games.json "faq"), linked same-month games, "Related pages and tools" (calendar, month, platform, Game Pass, RPGs, delays, clashes). Undated games get a calendar-free reminder FAQ.
- IndexNow pending (no WebFetch in this run): /games/stranger-than-heaven, /games/pokemon-winds-and-waves, /game-pass-2027, /games/fable, /games/persona-4-revival

## 2026-11-22 (scheduled data check, evening)
- Checked: delays into 2027 (Game Informer, Gematsu, Shacknews, RPG Site, PC Gamer), the morning "left out" list, new 2027 window announcements.
- Added 2 (board now 54):
  - BECROWNED: Q1 2027 (delayed from fall 2026), PC + new PS5/Xbox Series X|S/Switch 2 versions. Gematsu, PSU; dev 13th Street Games.
  - Honkai: Nexus Anima: spring 2027, PC (plus mobile; consoles unconfirmed). Gematsu, Automaton, Siliconera; final closed beta 25 Nov 2026.
- Left out: Warhammer Blood Bowl (still "early 2027" PC Gamer/Wargamer vs "spring 2027" God is a Geek); Baptiste (still no second source for 25 Mar 2027; VGChartz said fall 2026); The Duskbloods, Blighted, Outward 2, Ontos (only "2027"); Anima: Song from the Abyss (only "2027").
- No date changes for tracked games.

## 2026-11-22 (scheduled SEO run, sixth pass)
- New tool page /backlog-planner-2027 "2027 backlog planner: will you finish before the next launch?": quick answer (gaps between the 14 big dated games, from games.json), interactive planner (tick games or load your ★ list, set hours per week and your own hours per game; shows start/finish date per game, where you fall behind, date the list is clear; saved on this device), "How much time is there between the big 2027 launches?" table with hours at 5/10/20 h/week, how-to steps, FAQ JSON-LD. No playtimes published (visitor enters their own; 30 h placeholder). Targets "gaming backlog planner", "can I finish X before Y", "2027 game release gaps". Linked from footer (every page), Tools page (new card + link), clash finder, calendar and every dated game guide.
- New guide /games/danganronpa-2x2: 14 Jan 2027 (NA/EU), PS5/Xbox Series X|S/Switch 2/Switch/PC (Steam, Epic), Gemdrops/Spike Chunsoft, Original + new Slayhem scenario, editions; marked delayed (out of 2026, Game Informer + Vandal). Sources: Spike Chunsoft press release, Gematsu, Push Square, Game Informer. Linked from footer, board/games grid, January page.
- Refreshed /calendar: quick answer (counts, busiest month, first game, all computed), "Last checked", question H2s, launches-per-month table, computed FAQs (old FAQ hard-coded February as busiest; January is), related pages section.
- Left out: Japan date for Danganronpa 2x2 (none found).
- IndexNow pending (no WebFetch in this run): /backlog-planner-2027, /games/danganronpa-2x2, /calendar, /tools

## 2026-11-23 (scheduled SEO run)
- New page /biggest-games-2027 "The biggest games of 2027": quick answer, 19 editorial picks (major series/studios, remakes, sequels) grouped by quarter with one own-words line each on why it matters, "Which can I play on my console?" (count + missing games per console), undated big games, delayed big games, how we picked, FAQ + ItemList JSON-LD. New interactive "Make your 2027 top list and share it" tool (tick up to 10 in order, copy a ready-to-paste ranked list with dates, share link ?top=slug,... opens the picks for friends with a "shared" banner, use ★ list, saved on device). Targets "biggest games of 2027", "most anticipated games 2027", "best games coming 2027" (G2A, gaming.net, games.gg, Wccftech all rank for this). Dates/platforms only from games.json. GTA 6 confirmed 19 Nov 2026 (Rockstar Newswire), so it is not on the list; FAQ says so. Linked from footer (every page), Tools page (new card + link), /after-gta-6 and every month page.
- Refreshed all month pages (Jan, Feb, Mar, Apr, Jun, Dec 2027): Quick answer box (count, first game, big games that month), question H2s, new "What is the busiest week?" and "Which games are on my console?" sections, related pages/tools, two new FAQs (PS5, Switch 2 per month).
- /after-gta-6 retitled "What to Play After GTA 6: The Next Big Games (2027)" so it no longer competes with /biggest-games-2027; links to the new page.
- IndexNow pending (no WebFetch in this run): /biggest-games-2027, /months/january-2027, /months/february-2027, /months/march-2027, /months/april-2027, /tools, /after-gta-6
