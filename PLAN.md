# Run to the Moon and Back — Plan

## In Progress

- [ ] **feature/strava-sync** — GitHub Actions sync from Strava club (this PR)

---

## Upcoming

- [ ] UI: "Synced from Strava" badge on hero showing last sync timestamp
- [ ] Playwright: add test for Strava sync workflow (mock state.json with strava fields)

---

## Done

- [x] Initial site build (hero, leaderboard, journey, feed) — single index.html
- [x] Sample state.json with 30 runners
- [x] Playwright test suite (9 tests, all passing)
- [x] Deployed to GitHub Pages
- [x] SPEC.md, RECIPE.md (with Technical UI Tester skill)
- [x] fix/mobile-leaderboard — runner names truncating on iPhone (PR #1, merged)
- [x] SPEC.md: Strava integration v2 spec
- [x] scripts/strava-auth.py — one-time OAuth flow
- [x] scripts/list-clubs.py — list athlete clubs
- [x] scripts/init-members.py — initialize runners from club members
- [x] scripts/sync-strava.py — sync script used by GH Action
- [x] .github/workflows/sync-strava.yml — runs every 3 hours
- [x] GitHub Secrets set: STRAVA_CLIENT_ID, STRAVA_CLIENT_SECRET, STRAVA_REFRESH_TOKEN, STRAVA_CLUB_ID
- [x] Initial sync: 19 real activities from Fit 156 (club 1287260)
