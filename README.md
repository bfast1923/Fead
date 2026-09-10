# Signal — a self-tuning newsfeed

A static webpage that pulls from a curated set of RSS feeds daily, and
re-ranks itself based on what you actually click and how long you stay away
reading it. No server, no database — just GitHub Pages + GitHub Actions.

## What's here

```
sources.json                       curated RSS feeds, grouped by topic — edit freely
fetch_feeds.py                     pulls the feeds, writes docs/articles.json
requirements.txt                   one dependency (feedparser)
.github/workflows/update-feed.yml  runs fetch_feeds.py on a daily schedule
docs/index.html                    the webpage itself
docs/articles.json                 placeholder until the first run
```

## Deploy it (about 10 minutes)

1. **Create a new GitHub repo** (public — needed for free GitHub Pages on a
   personal account). Push all the files in this folder to it, keeping the
   folder structure exactly as-is (`.github/workflows/...`, `docs/...`).

2. **Turn on write access for Actions.**
   Repo → *Settings* → *Actions* → *General* → scroll to "Workflow
   permissions" → select **Read and write permissions** → Save.
   (This lets the daily job commit the refreshed `articles.json`.)

3. **Turn on GitHub Pages.**
   Repo → *Settings* → *Pages* → under "Build and deployment", set Source to
   **Deploy from a branch**, branch `main`, folder `/docs` → Save.
   GitHub will give you a URL like `https://yourname.github.io/signal-feed/`.

4. **Run the workflow once manually** so you don't have to wait for the
   first scheduled run.
   Repo → *Actions* tab → "Refresh feed" workflow → *Run workflow*.
   Give it a minute, then check that `docs/articles.json` has real content.

5. **Visit the Pages URL from your phone.** Add it to your home screen
   (Safari: Share → Add to Home Screen; Chrome: menu → Add to Home screen)
   so it opens like an app.

From then on, the workflow refreshes the article pool once a day (default:
noon UTC — edit the `cron` line in the workflow file to change the time).

## How the learning works

- Tapping a headline opens the source in a new tab and gives its topic and
  source a small immediate boost.
- When you come back to the Signal tab, the time you were away is used as a
  dwell-time proxy — longer away = bigger boost, capped so one long session
  can't dominate.
- Returning to the same topic repeatedly adds a smaller compounding boost.
- All of this is stored in your browser's local storage, not a server — so
  it's specific to whichever browser you use it in. If you want it to learn
  the same profile across your phone and laptop, that needs a small backend
  and database instead of local storage; say the word and I'll build that
  version next.

## Tuning it further

- **Sources**: add, remove, or re-categorize feeds in `sources.json`. Any
  standard RSS/Atom feed works.
- **Refresh time**: change the `cron` schedule in
  `.github/workflows/update-feed.yml` (it's in UTC).
   
- **How far back articles are kept / how many per source**: `MAX_AGE_HOURS`
  and `MAX_PER_SOURCE` at the top of `fetch_feeds.py`.
- **How fast it learns**: the boost sizes in the `<script>` block of
  `docs/index.html` (look for `0.05`, `dwellBoost`, `freqBoost`).
