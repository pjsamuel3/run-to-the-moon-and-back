/**
 * Moon & Back — Cloudflare Worker
 *
 * GET /        → returns cached state JSON (refreshes from Strava if stale)
 * Cron every 3 hours → proactive refresh
 *
 * Secrets (set via `wrangler secret put`):
 *   STRAVA_CLIENT_ID, STRAVA_CLIENT_SECRET, STRAVA_REFRESH_TOKEN, STRAVA_CLUB_ID
 *
 * KV binding: STATE
 *   Keys: "state" (full state JSON), "refresh_token" (rotated token)
 */

const CACHE_TTL_MS  = 3 * 60 * 60 * 1000;  // 3 hours
const MAX_RUNS      = 10;                    // runs kept per runner
const GOAL_KM       = 768800;

const CORS = {
  'Access-Control-Allow-Origin':  '*',
  'Access-Control-Allow-Methods': 'GET, OPTIONS',
  'Content-Type':                 'application/json',
};

// ── Entry points ─────────────────────────────────────────────────────────────

export default {
  async fetch(req, env) {
    if (req.method === 'OPTIONS') return new Response(null, { headers: CORS });

    const state = await getOrRefresh(env);
    return new Response(JSON.stringify(state), { headers: CORS });
  },

  async scheduled(_event, env) {
    await syncStrava(env);
  },
};

// ── Core logic ────────────────────────────────────────────────────────────────

async function getOrRefresh(env) {
  const raw = await env.STATE.get('state');
  if (raw) {
    const state = JSON.parse(raw);
    const age   = Date.now() - new Date(state.last_strava_sync || 0).getTime();
    if (age < CACHE_TTL_MS) return state;
  }
  return syncStrava(env);
}

async function syncStrava(env) {
  const clientId     = env.STRAVA_CLIENT_ID;
  const clientSecret = env.STRAVA_CLIENT_SECRET;
  const clubId       = env.STRAVA_CLUB_ID;

  // Use rotated token from KV if available, else fall back to seed secret
  const storedToken  = await env.STATE.get('refresh_token');
  const refreshToken = storedToken || env.STRAVA_REFRESH_TOKEN;

  // 1. Refresh access token
  const tokenRes = await fetch('https://www.strava.com/api/v3/oauth/token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({
      client_id:     clientId,
      client_secret: clientSecret,
      refresh_token: refreshToken,
      grant_type:    'refresh_token',
    }),
  });
  const tokens = await tokenRes.json();
  if (!tokens.access_token) throw new Error(`Token refresh failed: ${JSON.stringify(tokens)}`);

  // Persist the rotated refresh token so it stays fresh
  await env.STATE.put('refresh_token', tokens.refresh_token);

  // 2. Fetch club activities (paginated)
  const activities = await fetchAllActivities(clubId, tokens.access_token);

  // 3. Load existing state from KV (or empty scaffold)
  const raw   = await env.STATE.get('state');
  const state = raw ? JSON.parse(raw) : emptyState(clubId);

  // 4. Merge new activities in
  merge(state, activities);

  // 5. Save and return
  const now = new Date().toISOString().replace('.000', '');
  state.last_updated     = now;
  state.last_strava_sync = now;

  await env.STATE.put('state', JSON.stringify(state));
  return state;
}

async function fetchAllActivities(clubId, token) {
  const all  = [];
  let   page = 1;
  while (page <= 5) {
    const url = `https://www.strava.com/api/v3/clubs/${clubId}/activities?per_page=200&page=${page}`;
    const res = await fetch(url, { headers: { Authorization: `Bearer ${token}` } });
    const batch = await res.json();
    if (!Array.isArray(batch) || !batch.length) break;
    all.push(...batch);
    if (batch.length < 200) break;
    page++;
  }
  return all;
}

// ── Merge logic ───────────────────────────────────────────────────────────────

function merge(state, activities) {
  const byKey = Object.fromEntries(
    state.runners.map(r => [r.strava_name_key, r])
  );

  // Build dedup set from existing runs
  const seen = new Set();
  for (const r of state.runners) {
    for (const run of r.runs ?? []) {
      seen.add(fingerprint(r.strava_name_key, run));
    }
  }

  // Process oldest-first so totals accumulate correctly
  for (const act of [...activities].reverse()) {
    const athlete = act.athlete ?? {};
    const key     = nameKey(athlete.firstname ?? '', athlete.lastname ?? '');
    const runner  = byKey[key];
    if (!runner) continue;

    const distKm = Math.round((act.distance ?? 0) / 1000 * 100) / 100;
    if (distKm < 0.1) continue;

    // Strava club feed omits start_date for privacy — use start_date_local if
    // present, otherwise fall back to elapsed_time-derived estimate is not
    // possible; we store empty string and display gracefully.
    const date = (act.start_date_local ?? act.start_date ?? '').slice(0, 10);

    const run = {
      date,
      distance_km:  distKm,
      activity:     act.sport_type ?? act.type ?? 'Run',
      name:         act.name ?? act.type ?? 'Run',
    };

    const fp = fingerprint(key, run);
    if (seen.has(fp)) continue;
    seen.add(fp);

    runner.total_km = Math.round((runner.total_km ?? 0 + distKm) * 100) / 100;
    runner.runs     = [run, ...(runner.runs ?? [])].slice(0, MAX_RUNS);
  }
}

function fingerprint(key, run) {
  return `${run.date}:${key}:${run.distance_km}`;
}

function nameKey(firstname, lastname) {
  const initial = (lastname ?? '').replace('.', '').trim().slice(0, 1).toUpperCase();
  return `${(firstname ?? '').trim()}_${initial}`;
}

function emptyState(clubId) {
  return {
    goal_km:        GOAL_KM,
    strava_club_id: Number(clubId),
    runners:        [],
    last_updated:   null,
    last_strava_sync: null,
  };
}
