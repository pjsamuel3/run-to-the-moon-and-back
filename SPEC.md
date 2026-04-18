# Run to the Moon and Back — Site Spec

## Audience
30 mates doing a group running challenge together. Mixed fitness levels. Primarily mobile (checking after a run, trash-talking friends). Light-hearted, competitive energy.

## The one job of this page
Show the group how far they've collectively run toward the moon and back, make each runner feel seen and ranked, and drive the "I need to get out there" competitive instinct.

## Goal distance
**768,800 km** — the moon and back (384,400 km × 2).

---

## Sections

- `#hero` — Big dramatic progress visualization. How far have we travelled? Where are we in the journey?
- `#leaderboard` — Individual runners ranked by total distance with rank/level badge
- `#milestones` — Journey milestone markers (ISS, Geostationary orbit, The Moon, Home)
- `#feed` — Recent activity log (latest runs across the group)

---

## Data architecture

### `state.json` — source of truth (committed to repo, updated manually or via future GitHub Action)

```json
{
  "last_updated": "2026-04-18T10:00:00Z",
  "goal_km": 768800,
  "runners": [
    {
      "name": "Pete Samuel",
      "strava_handle": "petesamuel",
      "avatar_url": "",
      "total_km": 0,
      "runs": [
        { "date": "2026-04-18", "distance_km": 10.5, "activity": "Run", "name": "Morning 10k" }
      ]
    }
  ]
}
```

The site fetches `state.json` at page load via `fetch('./state.json')` — no backend needed.

### Computed values (JS, client-side)
- `total_km` = sum of all `runs[].distance_km` across all runners
- `progress_pct` = `total_km / 768800 * 100`
- Per-runner rank = sorted by `total_km` descending
- Per-runner level = derived from `total_km` (see gamification below)

---

## Gamification

### Collective journey milestones
These appear as markers on the progress track:

| Milestone | Distance (km) | Label |
|-----------|--------------|-------|
| 🚀 Launch Pad | 0 | We begin |
| 🛸 ISS Altitude | 400 | Low Earth Orbit |
| 🌐 Geostationary Belt | 35,786 | Communications zone |
| 🌑 Lunar Transfer | 100,000 | Escape trajectory |
| 🌕 The Moon | 384,400 | Halfway! |
| 🔄 Return Journey | 500,000 | Heading home |
| 🏠 Back on Earth | 768,800 | DONE |

### Individual runner levels (by total km)
| Level | km range | Title | Emoji |
|-------|---------|-------|-------|
| 1 | 0–9 | Cadet | 🌱 |
| 2 | 10–49 | Cosmonaut | 🧑‍🚀 |
| 3 | 50–149 | Astronaut | 🚀 |
| 4 | 150–399 | Space Walker | 🌌 |
| 5 | 400–999 | Lunar Pioneer | 🌕 |
| 6 | 1000+ | Moon Runner | 🏆 |

---

## Aesthetic direction

**Vibe:** A sports app that got a NASA internship. Fast, bold, data-forward — but with personality. Light-hearted banter energy.

**Reference:** Strava meets a mission control dashboard. Clean whites and deep space navy, punched up with electric accent.

**Palette:**
- Background: `#0a0e1a` — deep space navy
- Card surface: `#141929` — slightly lighter navy
- Primary text: `#f0f4ff` — cool white
- Accent: `#00d4ff` — electric cyan (the "thrust" colour)
- Accent warm: `#ff6b35` — rocket orange (secondary actions, warnings, fun)
- Muted: `#5a6a8a` — grey-blue for metadata

**Fonts (Google Fonts):**
- Display/headings: `Exo 2` — sporty, geometric, slightly futuristic
- Body: `Inter` — readable, modern
- Labels/metadata/numbers: `JetBrains Mono` — data readout feel

**Mood:** Fast. Numbers feel alive. Progress bar has thrust. Leaderboard positions feel earned. Micro-animations on load and state change.

---

## Component patterns

### Progress bar (hero)
- Thick horizontal track showing total progress
- Rocket emoji 🚀 that sits at current position, with a subtle glow trail behind it
- Milestone markers as dots with tooltip labels
- Large stat: "X,XXX km" in display font, animated counter on load

### Runner card (leaderboard)
- Rank number (large, muted)
- Name + Strava handle
- Level badge (emoji + title, coloured by level)
- Total km (bold, mono font)
- Mini bar showing their % of total group distance
- Subtle card hover: lift + border glow in accent colour

### Activity feed item
- Runner name + activity type
- Distance in bold
- Relative date ("2h ago", "yesterday")
- Stacked list, newest first

---

## Micro-animations
- Counter roll-up on number stats (0 → actual value, 800ms, ease-out)
- `.fade-up` stagger on leaderboard cards (75ms offset per card)
- Rocket emoji on progress bar has a subtle `pulse` keyframe glow
- Level badge does a quick `pop` scale animation on first render
- Cards lift on hover with `transform: translateY(-3px)` + box-shadow transition

---

## Technical requirements
- Single `index.html` — CSS in `<style>`, JS in `<script>`
- Loads `state.json` via `fetch()` — no backend
- Google Fonts only as external dependency
- No frameworks, no build tools
- Mobile-first (375px baseline)
- GitHub Pages compatible
- Graceful empty state: site renders meaningfully with zero runs logged

---

## GitHub Pages setup
- Repo: `run-to-the-moon-and-back`
- Live URL: `https://[username].github.io/run-to-the-moon-and-back/`
- Deploy from: `main` branch, `/` root

---

## Out of scope (v1)
- ~~Live Strava API sync~~ → **now v2, see below**
- Authentication / runner self-service logging
- Comments or social features
- Historical charts / graphs

---

## Strava Integration — v2 spec

### Architecture: GitHub Actions sync (Option A)

A scheduled GitHub Action runs every 3 hours:
1. Refreshes the Strava access token using a stored refresh token
2. Fetches recent activities from the Strava club feed (`/clubs/{id}/activities`)
3. Merges new activities into `state.json` (deduplicates by `strava_activity_id`)
4. Updates each runner's `total_km` and recent `runs[]`
5. Commits the updated `state.json` to `main` → triggers GitHub Pages redeploy

No backend needed. No user-facing auth. Admin sets up once via a one-time local OAuth script.

### Secrets (stored in GitHub repo Settings → Secrets)

| Secret | Description |
|--------|-------------|
| `STRAVA_CLIENT_ID` | Strava API app Client ID |
| `STRAVA_CLIENT_SECRET` | Strava API app Client Secret |
| `STRAVA_REFRESH_TOKEN` | Long-lived refresh token (from one-time auth flow) |
| `STRAVA_CLUB_ID` | Strava Club ID for the challenge group |

### state.json schema additions

```json
{
  "strava_club_id": 12345,
  "last_strava_sync": "2026-04-18T10:00:00Z",
  "runners": [
    {
      "strava_athlete_id": 3382216,
      "runs": [
        { "strava_activity_id": 99999, ... }
      ]
    }
  ]
}
```

- `strava_athlete_id` — links a runner to their Strava account for activity matching
- `strava_activity_id` — used for deduplication (activities are never double-counted)
- Runner `total_km` is **accumulated** (added to, never recalculated from scratch) so historical activities outside the API window are preserved

### Scripts

| Script | Purpose | When to run |
|--------|---------|-------------|
| `scripts/strava-auth.py` | One-time OAuth flow → prints refresh token | Once, by admin |
| `scripts/list-clubs.py` | Lists athlete's Strava clubs with IDs | Once, to find club ID |
| `scripts/init-members.py` | Replaces runners with real club members | Once, after club chosen |
| `scripts/sync-strava.py` | Fetches new activities, updates state.json | By GitHub Action |

### GitHub Actions schedule

- Every 3 hours via cron (`0 */3 * * *`)
- Manually dispatchable via `workflow_dispatch`
- Commit message: `chore: sync Strava data [skip ci]` (prevents re-trigger loop)

### Matching logic

Activities are matched to runners by `athlete.id` (Strava athlete ID), NOT by name. This is robust — Strava abbreviates last names in club feeds (e.g. "Pete S.") so name matching is unreliable.

### Privacy

Only activities visible to the club are synced. Runners with "Only Me" privacy won't contribute — this is intentional and documented.
