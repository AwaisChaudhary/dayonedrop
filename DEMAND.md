## SEO PLAYBOOK — standing rules for every run (Awais 26 Nov 01:35: "do SEO like the best SEO guy in the world for all sites")

## EVENING RADAR 26 Nov 18:45 PKT (Google autocomplete US + Trends past 24h)
- R1 DONE 26 Nov (H2 on /platforms/switch-2, auto-drops 5 Dec) 'switch 2 games black friday deals' / 'switch 2 games on sale' (autocomplete #1/#3): time-limited H2 on the Switch 2 page linking official store sales (no prices unless 2 sources), remove after Cyber Monday.
- R2 OPEN 'new movies to stream / in theaters now' (#1/#4) supports the E1 movies category; start with 'movies coming out 2027'.

## NEW CATEGORY EXPANSION (Awais 26 Nov: when traffic plateaus, open new categories backed by Trends/searches; don't wait for input)
Evidence = Google autocomplete 26 Nov 18:10 PKT. Each is a CATEGORY: build a hub page first, then 1-2 child pages per run. Skip if it already exists.
- E1 OPEN Movies category: /movies-2027 hub, 'movies coming out 2027 in theaters', '... for kids', '... january' month pages (3+ dated films each; studio-confirmed dates).
- E2 OPEN Anime 2027: 'anime 2027 upcoming|lineup|winter|calendar' season hub (winter/spring/summer/fall 2027).
- E3 OPEN TV shows 2027 hub after E1-E2 prove out. Keep the departures-board look for all.
Tools in this repo: `seo_post.py` (runs at the end of build.py: sitemap = every indexable page; lastmod changes ONLY when visible content changes; image sitemap entries) and `seo_audit.py` (`python3 seo_audit.py . <https://domain>`: titles, descriptions, canonicals, H1, JSON-LD, broken links, orphans, sitemap gaps, thin pages).
1. EVERY NEW PAGE: one main query (Keyword Planner / autocomplete / People Also Ask). Title: the query first, under ~60 characters where possible. Meta description 140-160 chars that contains the answer. One H1. A quick answer to the query in the first 100 words. FAQ from real PAA questions. Link IN from at least 3 relevant existing pages (not just nav) and OUT to 3+ related pages. An original image where it helps (our own diagrams/maps/screens, descriptive alt text). Then run seo_audit.py and fix anything it flags for that page.
2. AFTER DEPLOY: IndexNow ping (key in README/OPERATIONS) + Search Console URL Inspection > Request indexing for the 2-5 most important new URLs (max ~10/day per property; account ocrial@gmail.com = authuser=1).
3. WEEKLY (Monday run): Search Console > Performance > 28 days > Pages + Queries (500 rows). (a) Pages at position 5-15 with 200+ impressions: rework them first: answer the exact top queries word-for-word in the quick answer/H2s, add the missing sub-topics the queries show, refresh facts and "last checked" dates, add FAQ entries for question-type queries, strengthen internal links to the page. (b) Pages with CTR under 1% at position under 10: rewrite title/description to match the dominant query wording and promise the specific answer (numbers, "all N locations", year). (c) Queries with impressions but no matching page: new page or section. Log every change with before/after position in CONTENT-LOG.md, and don't touch a page again for 14 days so the effect can be measured.
4. NEVER: stamp fake lastmod/"updated" dates, change URLs of pages that get traffic (if unavoidable, 301 in _redirects), keyword-stuff, mass-produce thin pages, buy links, swap links, or copy competitors' text/data.
5. Links: only real editorial links via outreach batches Awais approves; build "linkable assets" (original data, free tools, maps) and list pitch targets in DEMAND for approval.
6. Monthly: run seo_audit.py on the whole site and fix broken links, orphans, duplicate titles/descriptions, missing schema.

## DEMAND RUN 27 Nov 2026 (scheduled, demand-first; second pass)
Evidence: "games like pokemon" (GamesRadar+ US/UK/AU, GameSpot gallery, Game Rant Metacritic list, Insider Gaming, Windows Central, TheGamer, ComicBook "Pokemon rivals 2026"); "upcoming creature collector 2027": Cassette Beasts 2002 March 2027 (Gematsu, RPG Site, VGChartz, Niche Gamer, RPGamer, Automaton); "games like minecraft" (GamesRadar+, PCGamesN, games.gg, Beebom, SVG, ComicBook "Minecraft replacement"); Minecraft Switch 2 native edition 27 Oct 2026 (Windows Central, Neowin, Thurrott).
N35. DONE 27 Nov https://getdayonedrop.com/games-like-pokemon : 10 picks + platform/taste filter, 2027 monster tamers (Winds and Waves, Cassette Beasts 2002, Honkai: Nexus Anima), DQM Withered World countdown.
N36. DONE 27 Nov https://getdayonedrop.com/games-like-minecraft : 11 picks + filter, 2027 survival/building games, Minecraft movie 2 (23 Jul 2027) countdown, Minecraft 2 / Switch 2 / free H2s.
N37. DONE 27 Nov /rpgs-2027 refresh: "What monster-taming RPGs come out in 2027?" H2 + FAQ. Data: Cassette Beasts 2002 added to games.json (March 2027).
N38. OPEN single-source creature/survival 2027: Navinosuke the Yo-kai Buster revival (Automaton, Steam 2027); "Monster Hunter meets Valheim" 2027 RPG (OpenCritic only); Tamer Town (Switch 2, ComicBook). Next games-like: "games like Animal Crossing", "games like Fortnite", "cozy games Switch 2".

## DEMAND RUN 27 Nov 2026 (scheduled, demand-first; Black Friday)
Evidence: "games like stardew valley" (GamesRadar+ x3 regions, PC Gamer, Dot Esports, games.gg, Medium lists; PC Gamer "39 Stardew-shaped farm sims"; games.gg "best upcoming cozy games Switch 2"); "Stardew Valley 1.7 2027" (GamesRadar+, PC Gamer guide, GosuGamers, PowerUp, pcgames.de, Nov 2026); "games like zelda" / "games like breath of the wild" (GamesRadar+, Push Square, Pocket Tactics, G2A, T3, Windows Central, Den of Geek); "zelda 2027" SERP mixes movie + Hyrule Warriors news. Football Manager 27 already out 10 Nov 2026 (Gematsu, gamespress). "movies coming out february 2027": SERP is BOM / The Numbers / Movie Insider only.
N31. DONE 27 Nov https://getdayonedrop.com/games-like-stardew-valley : 11 picks + platform/taste filter, 2027 cozy games (Emberville, Witchbrook, Atelier Karia, Grave Seasons, Neverway), Witchbrook countdown, Stardew 1.7 H2.
N32. DONE 27 Nov https://getdayonedrop.com/games-like-zelda : 10 picks + filter, 2027 Zelda-likes, "is there a new Zelda in 2027", Zelda movie H2.
N33. DONE 27 Nov /games-by-genre-2027 refresh: "What cozy games come out in 2027?" H2 + FAQ; sports H2 corrected (Super Battle Golf 25 Mar + GWYF2 were on the board but text said "no sports game").
N34. OPEN /movies-february-2027 still thin: only Ice Age: Boiling Point (5 Feb) and K-Pop: The Debut (26 Feb) match on The Numbers + BOM; Narnia 12 Feb (in MOVIES). Conflicts: The Nightingale (BOM 12 Feb vs TN 19 Mar), Live Like That (26 vs 27 Feb), Panic Carefully (BOM 26 Feb vs TN 9 Apr). Retry when Movie Insider loads or a 3rd film matches. Next games-like: "games like Pokémon" (Winds and Waves), "games like Minecraft", "cozy games Switch 2".

## DEMAND RUN 26 Nov 2026 (scheduled, seventh pass, night)
Evidence: "movies coming out january 2027" SERP = only BOM / The Numbers / Movie Insider calendars (no editorial page = gap); "games like hollow knight silksong" / "upcoming metroidvania" lists on GamesRadar+, ComicBook (x3), ScreenRant, Inverse, G2A; "switch 2 games black friday" (R1).
N27. DONE 26 Nov https://getdayonedrop.com/movies-january-2027 (N26 next step): 6 two-schedule films, filter, countdown.
N28. DONE 26 Nov https://getdayonedrop.com/games-like-hollow-knight : 11 picks + 2027 metroidvanias, platform/taste filter.
N29. DONE 26 Nov R1 as an H2 on https://getdayonedrop.com/platforms/switch-2 (auto-removed after 5 Dec).
N30. PARTLY DONE 27 Nov (Zelda + Stardew pages live; Feb movies see N34) /movies-february-2027 (Ice Age 5 Feb, Narnia 12 Feb already in MOVIES; check The Numbers + BOM for a 3rd+); "games like Zelda" / "games like Stardew Valley" (Witchbrook, Grave Seasons on board) next in the games-like series.

## DEMAND RUN 26 Nov 2026 (scheduled, sixth pass, demand-first; evening)
Evidence: "movies coming out december 2026" (N11 open; Box Office Mojo / The Numbers / GamesRadar+ December calendars all live; TheWrap + Bleeding Cool on Jumanji 3 moving to 25 Dec; "Dunesday" 18 Dec coverage). "winter 2027 anime" / "anime 2027 upcoming" (E2 open; winter 2027 season lists now up on Crank-in, Anime Eiga, Anime Corner, ComicBook.com 'returning anime winter 2027', GamesRadar+ anime schedule, giga.de, animotaku.fr).
N23. DONE 26 Nov https://getdayonedrop.com/movies-december-2026 (N11): 10 US cinema releases (2+ schedules), type + week filter (mv-tool, stale saved filters now reset), Doomsday/Dune countdown, Christmas Day H2, "moved out of December" table (Shrek 5, Ice Age, Narnia). Refreshed /movies-2027 with a December 2026 H2 + FAQ.
N24. DONE 26 Nov https://getdayonedrop.com/winter-2027-anime (E2 hub): 21 shows in 2+ season lists, new/returning + Netflix filter (tv-tool), Sakamoto Days S2 / One-Punch Man S3P2 / Sekiro anime / The One Piece H2s.
N25. OPEN winter 2027 anime upkeep: add exact days + simulcast service (Crunchyroll/Netflix/HIDIVE usually announce in December) once 2 sources agree; then /spring-2027-anime (April) when season lists appear (~Feb). Single-source winter titles left out: Blue Eye Samurai S2 (GR), Bakemonogatari-series 'Karen Ogre' (CI), Shaft etc.
N26. PARTLY DONE (/movies-january-2027 live 26 Nov) December 2026 streaming movies (In a Holidaze 2 Dec Netflix, The Man with the Bag 2 Dec Prime Video, Bad Day 11 Dec, Give Me Some Sugah 16 Dec, Ink, Ray Gunn) need a 2nd schedule before joining MV_DEC. /movies-january-2027 next (Children of Blood and Bone 15 Jan, Beekeeper 2 15 Jan already 2-source).

## DEMAND RUN 26 Nov 2026 (scheduled, fifth pass, demand-first; Thanksgiving, Black Friday tomorrow)
Evidence: Black Friday week: "ps store black friday sale end date", "xbox black friday sale 2026", "nintendo eshop black friday 2026", "steam black friday sale", "epic black friday sale" (dozens of fresh explainers 13-25 Nov: Push Square, Pure Xbox, Insider Gaming, Windows Report, My Nintendo News, Digital Citizen, Beebom, games.gg). "new tv shows january 2027" / "midseason 2027 premiere dates": TVLine (ABC 6 Nov, Fox 11 Nov), TV Guide (13 Nov), TV Insider, Laughing Place all published midseason schedules. Horizon Steel Frontiers "release date": GamesRadar, GamingBolt, PSU, Wccftech say first half of 2027.
N18. DONE 26 Nov https://getdayonedrop.com/black-friday-game-sales-2026 : quick answer, live "ends in" timers per store in reader's time zone, US / UK-EU region filter, all-dates table, per-store H2s, Steam (no BF sale), Cyber Monday, buy-now-or-wait, after-BF sales (Epic Holiday 10 Dec, Steam Winter 17 Dec). Refresh yearly (Nov 2027 -> new URL /black-friday-game-sales-2027, 301 not needed).
N19. DONE 26 Nov https://getdayonedrop.com/new-tv-shows-january-2027 (N16).
N20. DONE 26 Nov data: Horizon Steel Frontiers added (first half 2027, PC + mobile; board 86).
N21. OPEN streaming January 2027 premieres single-source so far (pogdesign): 3 Body Problem S2 (14 Jan, Netflix), Ahsoka S2 (20 Jan, Disney+), The Traitors US (14 Jan, Peacock), Blue Eye Samurai S2 (19 Jan), Spider-Man animated S2 (13 Jan), Mayor of Kingstown (15 Jan), Matlock (21 Jan, CBS), NCIS: Sydney (26 Jan), When Calls the Heart (3 Jan, Hallmark). Add each to TV_JAN in build.py when a 2nd schedule confirms.
N22. OPEN /holiday-game-sales-2026 or a December H2 once PS Store / eShop announce their holiday sales (usually mid-December); Epic mystery free games if announced.

## DEMAND RUN 26 Nov 2026 (scheduled, fourth pass, demand-first)
Evidence: GTA 6 launched 19 Nov 2026 on PS5/Xbox Series X|S only (Dexerto, Vice, VGC 20 Nov); "gta 6 pc release date" / "is gta 6 on pc" is now the top GTA question: VGC, Vice, Yahoo Tech, Windows Forum, Shattered (25 Nov GameGPU "March 2027" claim) all published PC-date explainers this week; Take-Two CEO GTA 7 / next-project quotes (Dexerto, Tribune, IBTimes, ComicBook, Notebookcheck 19-22 Nov). W2/R4 "new tv shows december 2026" (100k-1M head term): RT (18 Nov), Deadline/Yahoo, ScreenRant, Dexerto, TVChart, OTTweek all run December 2026 premiere pages.
N13. DONE 26 Nov https://getdayonedrop.com/gta-6-pc-release-date : quick answer (no PC date), status table, live "days PC players have waited", PC-date estimator tool (GTA IV / RDR2 / GTA V gaps + GamesBeat Q1 2027 report) with countdown, rumour table (labelled), GTA 6 Online + GTA 7 H2s, PC games to play meanwhile.
N14. DONE 26 Nov https://getdayonedrop.com/new-tv-shows-december-2026 (W2/R4 first step): 18 premieres listed by 2+ schedules, service + type filter, Google Calendar per show, Harry Potter countdown, Netflix / other-service / final-season / week-by-week H2s. Single-source shows left out: Collect & Praise, It's Florida Man S3, Sunshine Girls, The Chosen: The Three Kings, Who the Hell is Hamish?, Fixer Upper special, NYRE.
N15. DONE 26 Nov (refresh) https://getdayonedrop.com/after-gta-6 : R3 "rockstar next game" answered with Zelnick's launch-day GTA 7 quote, Nov earnings "next project" line, new "When does GTA 6 Online come out?" H2 + FAQ, link to PC estimator.
R1/R2 NOTE 26 Nov: already covered. Month pages Jan-Apr 2027 exist with "Games Coming Out in <Month> 2027" titles; /platforms/switch-2 has "Which 2027 games are only on Switch 2?" exclusives section. Mark DONE.
N16. DONE 26 Nov https://getdayonedrop.com/new-tv-shows-january-2027 (17 ABC + Fox premieres; streaming dates still need a 2nd source) (next month, same format) and keep the December page fresh (add shows once a 2nd schedule confirms).
N17. OPEN GTA 6 follow-ups: update /gta-6-pc-release-date the day Rockstar announces PC or Online; Take-Two Q3 earnings (early Feb 2027) is the next likely official mention.

## COMPETITOR WATCH 26 Nov 2026 (vs Game Informer /2026 + /2027 lists, GamesRadar release dates upd. 25 Nov)
We have 85 games in assets/games.json (was 79), 30 game pages, month pages Jan-Apr 2027 + Dec 2026 (DEC26 list had 21 games).
1. DONE 26 Nov (competitor watch): /games-december-2026 was missing 8 games that Game Informer and GamesRadar both date the same: Apple Crumble, Dumpster Gang, The Journey Home (3 Dec), Acts of Blood, A Game About Digging A Hole Together, Petit Planet (4 Dec), Don't Fret (8 Dec), Hookeye (9 Dec). Added (platforms = what both agree on).
2. GAP: every 2027 game both lists date is now in games.json (63/63). Remaining GI-only/GR-only dated games need a 2nd source: GI-only Jan: BrokenLore: Ascend (7 Jan), Terranigma (14 Jan), Titan Quest II (19 Jan), Demon Tides + Wandering Sword (21 Jan), Fate/Extra Record, Nioh 3 Complete, Tropico 7 (28 Jan); Feb: He-Man Dragon Pearl (4 Feb), Atelier Karia (25 Feb); Mar: Trine 6 (4 Mar); Apr: Melty Blood: Twi-Lumina (22 Apr); Oct: Showa American Story (28 Oct). GR-only: Forza Horizon 6 PS5 (26 Jan), Rockbeasts (29 Jan), There Are No Ghosts at the Grand (16 Dec 2026). Plan: check publisher/Gematsu for each, add the ones confirmed.
3. DATE CONFLICTS to watch (show both until settled): Romancing SaGa 3: Destinies United (GI 4 Feb vs GR 16 Feb 2027); The Road of Dust and Sorrow (GR 3 Dec 2026 vs GI 19 Feb 2027).
4. GAP: still no May-Dec 2027 month pages; GI + GR already date God of War Laufey + Persona 4 Revival Switch 2 (20 May). Plan: /may-2027 + /june-2027 next (open since 25 Nov).
5. GAP: GamesRadar has 'TBC 2027' through 'TBC 2030' sections; we stop at 2027. Plan: /games-2028 'announced for 2028 and later' list (trackable, low competition).
6. BETTER-THAN-THEM: neither list has filters; both are one long page. Ours: 'This week's drops' email/RSS digest generated from games.json every Monday + per-platform RSS feeds (/feeds/ps5.xml etc.), so players and Discord bots subscribe. Nobody in the top 3 offers a feed.

## DEMAND RUN 26 Nov 2026 (scheduled, third pass, demand-first)
Evidence: W1 "upcoming movies 2027" (Keyword Planner 10k-100k, +900% YoY); Rotten Tomatoes "Most Anticipated Movies of 2027" updated 23 Nov; Disney restated Avengers: Secret Wars 17 Dec 2027 on 6 Nov (GamesRadar, ComicBookMovie); The Batman Part II moved to Feb 2028 (Variety, Empire, Kotaku) so "batman part 2 release date" now has a non-obvious answer. "games like elden ring" (evergreen, very high volume) + "upcoming soulslike games 2027" (Gematsu: Memoria Wake early 2027; Windows Central: LotF II delayed to 2027); Elden Ring Tarnished Edition on Switch 2 28 Aug 2026 (Game Informer, VGC, Nintendo Life).
N9. DONE 26 Nov https://getdayonedrop.com/movies-2027 : 28 dated 2027 films (studio or 2+ trade outlets), type + month filter, countdowns (next film, Secret Wars, Zelda), Google Calendar per film, "moved out of 2027" table (Batman II, Gremlins 3, Miami Vice '85), same-day clashes, big games the same week as big movies.
N10. DONE 26 Nov https://getdayonedrop.com/games-like-elden-ring : 12 out-now picks with platform + taste filter, 2027 soulslikes (Wo Long 2, No Rest for the Wicked 1.0, LotF II, The Duskbloods, Memoria Wake), Elden Ring 2 / Switch 2 / PS5 / Xbox+PC / hardest H2s. Linked from footer, LotF II, Wo Long 2, Duskbloods pages, genre page, after-gta-6, games-like-gta-6.
N11. OPEN /movies-december-2026 + /new-tv-shows (W2): next film/TV step. Weaker-sourced 2027 films to verify before adding to MOVIES in build.py: Beekeeper 2 (15 Jan), Animal Friends (22 Jan), Thomas Crown Affair (5 Mar), Not Alone (16 Apr), Beach Read (7 May), Charlie vs the Chocolate Factory (5 Nov), Paranormal Activity 8 (22 Oct; moved from 21 May per Dread Central + The Numbers only), Fast X Part 2 (Diesel says Mar 2028).
N12. OPEN data: Memoria Wake (early 2027, Xbox Series/PC, Team Crescendo) needs a 2nd outlet before it joins games.json; Lies of P sequel / Code Vein 2 / Phantom Blade Zero timing unchecked.
R1/R2/R3 (radar 26 Nov 06:45) CHECKED 26 Nov: already covered by /months/february-2027 (title "Games Coming Out in February 2027"), /platforms/switch-2 (H2 "Which 2027 games are only on Nintendo Switch 2?") and /after-gta-6 (H2 "What is Rockstar making after GTA 6?"); no duplicate URLs built.

## DEMAND RADAR 26 Nov 06:45 (Google autocomplete US)
R1. DONE (month pages exist) /games-coming-out-february-2027 (autocomplete "games coming out in 2027 february") and monthly pages for Jan-Mar 2027 if missing.
R2. DONE (covered by /platforms/switch-2) /switch-2-games-2027 ("switch 2 games 2027", "switch 2 exclusive games 2027") with release dates + exclusives filter.
R3. DONE 26 Nov as H2s on https://getdayonedrop.com/after-gta-6 /rockstar-next-game ("after gta 6 what is rockstar's next game": confirmed facts only, clearly label rumours) + "games like gta 6 on roblox / for android / for pc" sections on /games-like-gta-6.
R4. OPEN /new-tv-shows-december-2026 ("new tv shows december 2026") and /movies-2027 (W1) - both already queued as W-items; do W1/W2 first.

## TOP PRIORITY: WIDER CATEGORIES (Awais 26 Nov 01:02: "DayOneDrop doesn't mean games only or PS5 only, we have plenty of room to add more stuff")
DayOneDrop = "what's coming out and when". Build release-date hubs beyond console games, each with a calendar/table, countdowns and FAQ (facts from studios/platforms + 2 trusted outlets):
W1. DONE 26 Nov https://getdayonedrop.com/movies-2027 (movies-december-2026 still OPEN): upcoming movies 2027 ("upcoming movies 2027" 10k-100k, +900% YoY): dated big releases by month, where to watch (cinema/streaming), countdowns; then /movies-december-2026 for this month.
W2. PARTLY DONE 26 Nov https://getdayonedrop.com/new-tv-shows-december-2026 ; OPEN /new-tv-shows ("new tv shows" 100k-1M): shows premiering this month and next on Netflix, Disney+, Prime Video, HBO Max, Apple TV+; season dates for big returning shows.
W3. OPEN /anime-release-dates (winter 2027 season, 1k-10k) and /new-on-netflix-this-week style pages ONLY if they can be kept fresh by the data runs.
W4. OPEN game-adjacent: /nintendo-direct (100k-1M), /game-pass-this-month, /steam-sale-dates, /mobile-games-2027, /vr-games-2027, /board-games-2027 ("tabletop release"), /game-awards-2026 (11 Dec: nominees, how to watch, time in your zone).
W5. OPEN tech releases people track: /gaming-hardware-2027 (consoles, handhelds, GPUs with announced dates), /iphone-release-date style pages only with official/2-source facts.
W6. OPEN tools across categories: "release calendar" with filters (games / movies / TV), .ics calendar export, "what's out this weekend" page.
Weekly (Mondays) the demand radar checks Keyword Planner volumes for new categories; build those with 10k+ searches first.

## DEMAND RUN 26 Nov 2026 (scheduled, second pass)
Evidence: "fighting games 2027" (queue item 3 / R3) + Virtua Fighter Crossroads, Xenoverse 3, DCKO, Toshinden all announced for 2027 (VGC, Gematsu, PS Blog, Bandai Namco, Kotaku, Gamereactor); "injustice 3" PAA/rumour searches (PC Gamer, GamesRadar reports). "what time does the game awards start" / "game awards disney plus": Disney press release 12 Nov gave 7:30pm ET (GamingTrend, GGRecon, Pocket Tactics); show is 14 days away so this query peaks now.
N4. DONE 26 Nov https://getdayonedrop.com/fighting-games-2027 : console filter tool, countdown, Xenoverse 3 / Virtua Fighter / Injustice 3 / Toshinden H2s. Added Dragon Ball Xenoverse 3 + Toshinden Collection to games.json (board 83).
N5. DONE 26 Nov (refresh) https://getdayonedrop.com/game-awards-2026 : start time 7:30pm ET, "what time in my time zone" tool + 9-zone table, exact-time countdown, Google Calendar, Disney+ H2.
N6. OPEN /sports-games-2027: still thin (only Super Battle Golf + racing dated). Wait for MLB The Show 27 / EA Sports 2027 announcements (usually Jan-Mar); add Golf With Your Friends 2 if dated 2027 by 2 sources.
N7. OPEN data: Acts of Blood delayed to spring 2027 (Niche Gamer only so far) - needs 2nd trusted source. Netcode Warriors PS5 2027 (Gematsu 11/2026) - check genre/platforms.
N8. OPEN after TGA (11 Dec): /game-awards-2026 winners + every 2027 date/premiere announced on the night (same-night update; highest-traffic day of the month).

## DEMAND RUN 26 Nov 2026 (scheduled, demand-first)
Evidence: GI + GamesRadar both keep "TBC 2027 / no date" lists of ~150 titles (competitor gap 3, 25 Nov); "<game> countdown" / "how many days until <game>" is a standing query pattern for every dated game (our game pages have timers but no single shareable tool); "games coming out december 2026" (radar R1) peaks now, a week before December.
N1. DONE 26 Nov https://getdayonedrop.com/games-without-release-date-2027 : every 2027 game with no exact day, console + season filter, add to list, "when could they get a date" table.
N2. DONE 26 Nov https://getdayonedrop.com/countdown : live shareable countdown tool (?g=slug) for every dated game, days-to-go lists, month table.
N3. DONE 26 Nov (refresh) https://getdayonedrop.com/games-december-2026 : first-week H2, PS4/Xbox One/Switch 1 versions, free-to-play, Steam Winter Sale.
G4 NOTE 26 Nov: Game Pass monthly lists checked (Pure Xbox 3 Nov, 14 Nov, 17 Nov; GGRecon 2 Nov). Single-source and conflicting tiers (FM27 Premium yes/no; 14 leaving "15 Nov" vs "early November"); wave 2 article could not be read. Build /game-pass-this-month right after Xbox Wire posts December wave 1 (~1-2 Dec) with Pure Xbox + Windows Central/Xbox Wire. Pure Xbox "confirmed so far" for December: Hela (1 Dec), Dumpster Gang (PC 3 Dec), Freestyle Football 2 (3 Dec), A Game About Digging A Hole Together (4 Dec), There Are No Ghosts At The Grand (PC EA, Dec TBD) - needs 2nd source.

## NEW CATEGORIES (Keyword Planner, worldwide, 25 Nov 2026; Awais: "do the same for DayOneDrop")
DayOneDrop is a release-date site, so expand to every "what's new / when is it out" calendar gamers search:
G1. DONE 25 Nov /ps-plus-monthly-games — RECURRING: after the last-Wednesday reveal each month, update PSP in build.py (2+ sources). ("ps plus monthly games" 100k-1M, +900%). UPDATE monthly: last Wednesday reveal, first Tuesday release; keep a month-by-month archive table.
G2. DONE 25 Nov /epic-free-games — RECURRING: the first DayOneDrop run after 16:00 UTC every Thursday must update the EPIC list in build.py (now->past, next->now, add the newly announced next week; 2+ sources) and IndexNow the page. ("epic free games" 10k-100k): this week's free game + next week's, every Thursday 4 pm UK; December mystery games. Update weekly.
G3. DONE 25 Nov https://getdayonedrop.com/nintendo-direct (RECURRING: set ND_NEXT in build.py the day Nintendo announces a Direct; add each new Direct to ND_PAST) /nintendo-direct ("nintendo direct" 100k-1M): next Direct (only when Nintendo announces), every past Direct with what it revealed, linked to Switch 2 2027 games.
G4. OPEN /game-pass-this-month (complements /game-pass-2027, "game pass games" 10k-100k): games joining and leaving this month.
G5. OPEN NEW VERTICAL /movies-2027 ("upcoming movies 2027" 10k-100k, +900% YoY) + /new-tv-shows ("new tv shows" 100k-1M): only after G2-G4; same calendar format (title, date, where to watch), facts from studio/streamer announcements only.
G6. OPEN /anime-release-dates ("anime release dates" 1k-10k): winter 2027 season. Lower priority.
G7. DONE 25 Nov https://getdayonedrop.com/steam-sale-dates (RECURRING: add Autumn/Winter Sale 2027 + H2 2027 fests to STEAM in build.py when Valve posts them) /steam-sale-dates ("steam sale dates" 1k-10k): Winter Sale + 2027 sale/fest calendar from Steamworks' published dates.

## COMPETITOR WATCH 25 Nov 2026 (vs gameinformer.com/2027 + /2026, GamesRadar release dates upd. 23 Nov)
We have 79 games in data (was 74), 28 game pages, 4 month pages for 2027 (Jan-Apr) + Dec 2026, 4 platforms, ~20 list pages.
1. DONE 25 Nov (competitor watch): added 5 dated games both Game Informer and GamesRadar list: Usual June (20 Jan), Everything is Crab (26 Jan, Switch 2), Prison of Husks (27 Jan), My Arms Are Longer Now (11 Mar), Super Battle Golf (25 Mar, Switch 2). Platforms = only those both lists agree on.
2. GAP: Game Informer-only dated 2027 games (need a 2nd source before adding): Calx (21 Jan), Lelu (21 Jan), Temtem: Swarm (21 Jan, Switch 1), Sovereign Tower (14 Jan), Polyaris (19 Jan), Grindworm (18 Jan), Trainwatch (10 Mar), ReVamp (25 Mar), Rustown (30 Jun), The Road of Dust and Sorrow (19 Feb; GamesRadar has it as 3 Dec 2026: conflict, check publisher).
3. GAP: month pages stop at April 2027; GI already has dated May (God of War Laufey 20 May, Persona 4 Revival Switch 2 20 May) and June (Rustown 30 Jun). Plan: build May-Dec 2027 month pages now (thin months show 'TBC' block + count), GamesRadar/GI both have 'TBC 2027' lists of ~150 titles: add a /tbc-2027 'no date yet' page from our data.
4. GAP: GI and GamesRadar both mark Early Access and DLC/ports separately ([Early Access], Switch 2 ports like 007 First Light). Plan: 'type' tag (new game / early access / port / DLC) + filter chip on /games and month pages.
5. BETTER-THAN-THEM: neither list is filterable or personal (GI = plain list, GamesRadar = one long article). Ours: 'My 2027' watchlist with per-game .ics reminders + delay alerts ('this game moved' badge from history), filter by platform+type+month. Ship the type chip and a 'moved since you saved it' badge on /backlog-planner-2027.

## RADAR 25 Nov 06:45 PKT (Google autocomplete, US)
D1. DONE 25 Nov https://getdayonedrop.com/xbox-games-showcase-2027 'xbox games showcase 2027' (xbox games 2027 #5) -> /xbox-games-showcase-2027 (date window, what to expect, games confirmed so far; update live in June).
D2. OPEN 'ps5 sports games 2027' / 'ps5 soccer games 2027' -> /sports-games-2027 (genre page; also a competitor gap).
D3. DONE 25 Nov (month titles now 'Games Coming Out in <Month> 2027') 'games coming out in 2027 february' -> ensure /months/february-2027 title leads with 'Games Coming Out in February 2027'.
D4. DONE (already covered: H2s 'What games are like GTA 6 on PS5?' + 'Is there a game better than GTA 6?' on https://getdayonedrop.com/games-like-gta-6) 'games like gta 6 for ps5' / 'games better than gta 6' -> H2s on /games-like-gta-6.
D5. DONE (GTA 7 FAQ + section already on https://getdayonedrop.com/after-gta-6) 'after gta 6 will there be gta 7' -> FAQ + H2 on /after-gta-6.
Covered: exclusives-2027 (PS5/Xbox/Switch 2 exclusives), games-like-gta-6, platform pages, later-2027.

## COMPETITOR WATCH 24 Nov 2026 (vs GamesRadar release-dates hub upd. 23 Nov; gameinformer.com/2027 and GameSpot did not load this run)
We have 25 game pages, 7 month pages (Jan-Jun, Dec 2027), 4 platforms, 12 list pages.
1. GAP: dated Q1 2027 games GamesRadar lists that we have NO entry for: Outward 2 (early access 8 Feb), Among Us Story: On Guard (17 Feb), Pony Island 2: Panda Circus (27 Apr). Plan: add to data with 2-source dates. (Armatus, Ananta, Elta, Muramasa, Romancing SaGa 3, Tag Force GX, Gundam Rogue Orbit, Grave Seasons, Apothecary Diaries are in data but have no game page: give the biggest 3 pages.)
2. GAP: "2027, no date" games missing from our data: Marvel 1943: Rise of Hydra, The Wolf Among Us 2, Guild Wars 3, Dragon Ball Xenoverse 3, Monster Hunter Wilds expansion, Witcher 3 expansion, WoW: The Last Titan, Virtua Fighter (new), Kena: Scars of Kosmora, Heroes of Might and Magic 3 remake. Plan: verify each "2027" with publisher + 1 outlet; add with "2027 (no date)" confidence; skip if only rumour.
3. GAP: month pages Jul-Nov 2027 + a "2027 TBC" page and 2028 page. Plan: build.py month pages for every month 2027 (thin months: show TBC block + link); /games-2028.
4. GAP: per-platform dates (e.g. a game later on Switch 2). Plan: add optional per-platform date field; show on game + platform pages.
5. BETTER-THAN-THEM: GamesRadar is one long unfilterable article with no history. Ours: filter by platform/genre/date confidence (dated/month/window/TBC) + a "delay history" line per game (every slip with date) + per-game .ics reminder. We already have delayed-games-2027 and calendar; join them.

# DayOneDrop demand queue (Google autocomplete, 24 Nov 2026)
## RADAR 24 Nov 06:45 PKT — NEW top OPEN items
R1. DONE 24 Nov https://getdayonedrop.com/games-december-2026 (scheduled run). 'games coming out december 2026' (+ps5/xbox/switch 2 variants, 'big games coming out in december 2026', 'what games come out in december'): high demand NOW. Page /games-december-2026 (confirmed dates only, 2+ sources) linking into the 2027 board ('what's next in January 2027').
R2. OPEN Month pages: 'games coming out in january 2027', 'february 2027' (check build.py month pages exist and are titled 'Games coming out in January 2027').
R3. OPEN Sports games 2027 (ps5 soccer / golf / sports games 2027) and horror games 2027 -> genre pages (games-by-genre has filter; give sports + horror their own URLs).
R4. OPEN Xbox Games Showcase 2027 (date expectations, labelled unconfirmed until Microsoft announces) + 'xbox exclusive games 2027' (exclusives-2027 covers? make sure title says Xbox).
R5. DONE 24 Nov https://getdayonedrop.com/after-gta-6 (sections added). 'will there be gta 7', 'rockstar after gta 6', 'rdr3 after gta 6' -> sections on /after-gta-6 (facts only, rumours labelled).
R6. DONE 24 Nov https://getdayonedrop.com/games-like-gta-6 (scheduled run). 'games better than gta 6', 'upcoming games like gta 6' -> FAQs on /games-like-gta-6.

Build top-down; mark DONE + URL. Facts: publisher or 2+ trusted outlets.
1. DONE 24 Nov 02:20 https://getdayonedrop.com/games-like-gta-6 (main session). /games-like-gta-6 (HUGE: 'games like gta 6', 'for ps5', 'for pc', 'for android', 'roblox games like gta 6', 'coming out', 'better than gta 6', 'similar games'): open-world crime/action games out now + coming 2027, platform filter chips, why each is similar. Link from neoncoast.org (ask NeonCoast run to add a link in its footer/ending page).
2. OPEN /after-gta-6 refresh: 'rdr3 after gta 6', 'rockstar after gta 6', 'ttwo after gta 6' (only confirmed/officially said facts; label rumours).
3. OPEN genre x platform 2027 lists: ps5 sports games 2027 (soccer, golf, racing), xbox racing games 2027, fighting games 2027, marvel games 2027, switch 2 mario games 2027, rumored switch 2 games 2027 (clearly labelled).
4. OPEN 'xbox games showcase 2027' (date if announced, what to expect, past showcases).
5. OPEN 'anticipated ps5 games 2027' / 'top xbox games 2027' ranked list pages.

## Keyword Planner (US, 25 Nov 2026) — Google Ads acct 877-540-2315, ads paused, $0 spend
Seeds: upcoming games 2027, ps5 games 2027, game release dates. Volumes are ranges (no spend).
- ps5 game release dates 1k–10k, Low comp -> /platforms/ps5 (already pos 8.8)
- ps5 new releases / ps5 releases 1k–10k -> /platforms/ps5
- new xbox releases 1k–10k -> /platforms/xbox-series
- video game release dates 1k–10k, game release dates 100–1k -> home /games
- nintendo switch 2 release date 10k–100k (hardware, out of scope)
