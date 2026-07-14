# ConsumerSignal — a momentum tracker for consumer startups

*A small end-to-end data product that answers one question: which early-stage
consumer startups are gaining momentum right now — and why?*

---

## TL;DR

- **Problem:** Momentum in consumer startups shows up in weak signals (search,
  news, social buzz) long before it shows up in revenue or headlines. Those
  signals are scattered and noisy.
- **What I built:** A pipeline that pulls live search + news signals for 25
  consumer/AI startups, normalizes them into a comparable **Momentum Score
  (0–100)**, and serves a ranked dashboard with a per-startup breakdown.
- **Stack:** Python data pipeline → SQLite → Flask API → single-page dashboard
  (light/dark, responsive).
- **What I'm most proud of:** not the score — the *judgment about the data*. I
  found where the signal is real and where it's garbage, and designed the
  product around that honestly (see [Limitations](#what-the-data-taught-me)).

---

## The question, framed as a product

"Track startups" is not a product. The sharper question is:

> **If you had to bet on which consumer startups will break out in the next 6–12
> months, what early signals would you watch — and could you make them
> comparable across very different companies?**

That reframing drove every decision:

- **Comparable, not absolute.** A raw news count says nothing on its own — 40
  articles is huge for a seed-stage app and tiny for a category leader. So every
  signal is **normalized 0–100 relative to the tracked set**. The output is a
  ranking, not a vanity metric.
- **Explainable, not a black box.** A single score is useless to a decision-maker
  who can't see inside it. Each startup breaks down into four visible components
  (Awareness, Growth, Engagement, Media) shown as bars — you see *why* something
  ranks where it does in one glance.
- **Honest about confidence.** Every startup carries a High / Medium / Low
  confidence flag based on how many independent sources actually returned data.
  A high score built on one thin signal should *look* less trustworthy than one
  corroborated by three.

## What it does

- Ranks 25 consumer/AI startups on a **Momentum Leaderboard**, top-to-bottom.
- Opens any startup into a breakdown: the four score components, the raw source
  signals behind them (search interest, 30-day growth, news volume), and its
  peers in the same category.
- Filters by category and search; recomputes cleanly as the dataset changes.
- Summary KPIs up top: average momentum, current leader, category spread.

## How momentum is scored

Momentum is a weighted blend of four normalized components:

| Component      | Weight | What it proxies                         |
|----------------|:------:|-----------------------------------------|
| **Growth**     | 30%    | Velocity — is attention *accelerating*? |
| **Awareness**  | 25%    | Absolute search interest                |
| **Engagement** | 25%    | Social/community engagement             |
| **Media**      | 20%    | Recent news coverage volume             |

Growth carries the most weight on purpose: for early-stage bets, *rate of change*
is a better tell than current size. A tiny company accelerating fast is more
interesting than a bigger one that's flat.

## Architecture

```
data/startups.csv  →  Python pipeline  →  SQLite  →  scoring layer  →  Flask API  →  dashboard
                      (search + news        (single         (min-max        (JSON)       (HTML/JS,
                       signals, live)        file DB)         normalize)                  no framework)
```

Deliberately lightweight: no framework on the frontend, no external database, a
committed read-only dataset so the live demo deploys in one step. The point was
to ship the whole loop — ingestion to interface — not to over-engineer any layer.

## What the data taught me

This is the part I'd want a product person to read.

I started with a naïve approach: search each startup by name. It "worked" and
returned real, live data — which was exactly the trap. The results were
**real but wrong**:

- "Friend" (an AI wearable) pulled 92 articles — almost all about the generic
  word *friend*.
- "Pie" (a friend-making app) scored maximum awareness — because of the food.
- "Bolt" caught Usain Bolt and a European ride-hailing app.

**Real data that's measuring the wrong entity is worse than no data**, because it
looks credible. The fix was disambiguation — querying `Bolt.new`, `Friend AI
wearable`, etc. — and that surfaced the deeper truth: for genuinely early-stage
companies, free public signal (Google News RSS) is *sparse*. Some real companies
have near-zero recent coverage. That's not a bug to paper over; it's a real
finding about the ceiling of free data, and the confidence flags exist to make it
visible instead of hiding it.

Known limitations, stated plainly:

- **Engagement is a placeholder.** The Reddit/social signal isn't wired up yet,
  so engagement is currently a constant — which is exactly why no startup can
  earn "High" confidence. That gap is honest and visible in the UI, not swept
  under the rug.
- **Free signals are noisy and shallow** for pre-breakout companies. A production
  version needs a real news API with entity resolution.
- **The set is small and hand-picked** (25 startups) — enough to prove the loop,
  not a market census.

## What I'd build next

1. **Wire up the engagement signal** (Reddit/social) so confidence can actually
   reach High and the fourth component stops being a placeholder.
2. **Entity-resolved data source** — swap free RSS for a news/API with proper
   company disambiguation, killing the "Bolt = Usain Bolt" problem structurally.
3. **History and trend lines** — momentum is only meaningful over time. Store
   daily snapshots and show whether a startup is climbing or fading.
4. **Alerting** — the real product isn't a dashboard you check; it's a "X just
   started accelerating" signal that finds *you*.

## Why this matters (and why I'm sending it to 8sleep)

The instinct behind a great consumer product and the instinct behind this tool
are the same one: **reading weak signals early and acting before they're
obvious.** This project is me practicing that instinct in code — taking an
ambiguous question, deciding what's actually worth measuring, being ruthless
about signal vs. noise, and shipping something someone can click and understand
in ten seconds.

It's small on purpose. What I hope it shows is how I think: product framing
first, honest about the data, and biased toward shipping the whole loop.

---

*Built by Michelle Mai. Code: `<GitHub URL>` · Live demo: `<deployed URL>`*
