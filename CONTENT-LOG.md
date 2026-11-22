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
