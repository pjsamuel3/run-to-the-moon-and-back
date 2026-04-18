#!/usr/bin/env python3
"""
Strava sync script — run by GitHub Actions every 3 hours.
Fetches new club activities and merges them into state.json.

Required env vars:
  STRAVA_CLIENT_ID, STRAVA_CLIENT_SECRET, STRAVA_REFRESH_TOKEN, STRAVA_CLUB_ID

Note: Strava's club endpoints don't expose athlete IDs for privacy.
Runners are matched by Firstname_LastInitial (e.g. "Peter_S").
"""

import json
import os
import urllib.parse
import urllib.request
from datetime import datetime, timezone


def _post(url, data):
    body = urllib.parse.urlencode(data).encode()
    req  = urllib.request.Request(url, data=body, method="POST",
                                   headers={"Content-Type": "application/x-www-form-urlencoded"})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def _get(path, token, params=None):
    url = f"https://www.strava.com/api/v3{path}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def name_key(firstname, lastname):
    """Stable match key from Strava's abbreviated name fields."""
    initial = (lastname or "").replace(".", "").strip()[:1].upper()
    return f"{firstname.strip()}_{initial}"


def refresh_access_token(client_id, client_secret, refresh_tok):
    data = _post("https://www.strava.com/api/v3/oauth/token", {
        "client_id":     client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_tok,
        "grant_type":    "refresh_token",
    })
    print(f"Token refreshed (expires in {data.get('expires_in', '?')}s)")
    return data["access_token"]


def fetch_club_activities(club_id, token, max_pages=5):
    activities, page = [], 1
    while page <= max_pages:
        batch = _get(f"/clubs/{club_id}/activities", token,
                     {"per_page": 200, "page": page})
        if not batch:
            break
        activities.extend(batch)
        if len(batch) < 200:
            break
        page += 1
    return activities


def main():
    client_id     = os.environ["STRAVA_CLIENT_ID"]
    client_secret = os.environ["STRAVA_CLIENT_SECRET"]
    refresh_tok   = os.environ["STRAVA_REFRESH_TOKEN"]
    club_id       = int(os.environ["STRAVA_CLUB_ID"])

    with open("state.json") as f:
        state = json.load(f)

    print("Refreshing Strava access token...")
    access_token = refresh_access_token(client_id, client_secret, refresh_tok)

    # Index runners by name_key
    runner_by_key = {
        r["strava_name_key"]: r
        for r in state["runners"]
        if r.get("strava_name_key")
    }

    # Build set of already-processed activity fingerprints
    # Fingerprint = date + name_key + distance (no ID available from club feed)
    seen: set = set()
    for runner in state["runners"]:
        key = runner.get("strava_name_key", "")
        for run in runner.get("runs", []):
            fp = f"{run.get('date')}:{key}:{run.get('distance_km')}"
            seen.add(fp)

    print(f"Fetching activities for club {club_id}...")
    activities = fetch_club_activities(club_id, access_token)
    print(f"Fetched {len(activities)} activities from Strava")

    # Process oldest-first so totals accumulate chronologically
    new_count = 0
    for activity in reversed(activities):
        athlete    = activity.get("athlete", {})
        firstname  = athlete.get("firstname", "")
        lastname   = athlete.get("lastname", "")
        key        = name_key(firstname, lastname)
        runner     = runner_by_key.get(key)
        if not runner:
            continue

        distance_km  = round(activity.get("distance", 0) / 1000, 2)
        if distance_km < 0.1:
            continue

        start_date   = (activity.get("start_date") or "")[:10]
        activity_type = activity.get("type", "Run")
        activity_name = activity.get("name") or activity_type

        fingerprint = f"{start_date}:{key}:{distance_km}"
        if fingerprint in seen:
            continue
        seen.add(fingerprint)

        runner["total_km"] = round(runner.get("total_km", 0) + distance_km, 2)
        runner.setdefault("runs", []).insert(0, {
            "date":        start_date,
            "distance_km": distance_km,
            "activity":    activity_type,
            "name":        activity_name,
        })
        runner["runs"] = runner["runs"][:10]
        new_count += 1

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    state["last_updated"]     = now
    state["last_strava_sync"] = now

    with open("state.json", "w") as f:
        json.dump(state, f, indent=2)

    print(f"✅  Synced {new_count} new activities — state.json updated")


if __name__ == "__main__":
    main()
