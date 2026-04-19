# Run to the Moon and Back — Plan

## Upcoming

- [ ] UI: "Synced from Strava" badge on hero showing last sync timestamp
- [ ] Playwright: add test for Strava sync workflow (mock Worker response)

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
- [x] scripts/sync-strava.py — local sync script (superseded by Worker)
- [x] .github/workflows/sync-strava.yml — GitHub Actions sync (retired, replaced by Worker cron)
- [x] GitHub Secrets retired — secrets now live in Cloudflare Worker
- [x] Initial sync: 19 real activities from Fit 156 (club 1287260)
- [x] feature/3d-moon — CSS moon with horizontal globe-spin (PR #3, merged)
- [x] Cloudflare Worker (moon-strava-sync) — replaces GitHub Actions
  - KV cache, 3-hour cron, auto-rotating refresh token
  - URL: https://moon-strava-sync.pjsamuel3.workers.dev
- [x] chore/retire-github-actions — remove Actions workflow + GitHub Secrets (this PR)
