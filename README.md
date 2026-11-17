# DayOneDrop (getdayonedrop.com)

2027 video game release board: departures board, 2027 calendar, game guides and tools.

- Data: `assets/games.json` (one place for every game, date, platform and status).
- Build: `python3 build.py` makes the live site (clean URLs for Cloudflare Pages). `python3 build.py --preview` makes a local copy you can open as files.
- Hosting: Cloudflare Pages, deployed from the `main` branch. Build command: none. Output directory: `/`.
- Settings at the top of build.py: `DOMAIN` (https://getdayonedrop.com) and `GA_ID` (Google Analytics ID, empty until set).
- `ads.txt`: replace the placeholder with the AdSense line once approved. build.py never overwrites it.
