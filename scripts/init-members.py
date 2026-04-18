#!/usr/bin/env python3
"""
Replace state.json runners with real Strava club members.
Run once after choosing your club. Resets all totals to 0.

Usage: python3 scripts/init-members.py <access_token> <club_id>

Note: Strava's club endpoints don't expose athlete IDs for privacy.
Runners are matched by Firstname_LastInitial (e.g. "Peter_S").
"""

import json
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone


def strava_get(path, token, params=None):
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


if len(sys.argv) < 3:
    raise SystemExit("Usage: python3 scripts/init-members.py <access_token> <club_id>")

ACCESS_TOKEN = sys.argv[1]
CLUB_ID      = int(sys.argv[2])

# Fetch club info
print(f"Fetching club {CLUB_ID}...")
club = strava_get(f"/clubs/{CLUB_ID}", ACCESS_TOKEN)
print(f"Club: {club['name']} ({club['member_count']} members)")

# Fetch all members (paginated)
members, page = [], 1
while True:
    batch = strava_get(f"/clubs/{CLUB_ID}/members", ACCESS_TOKEN,
                       {"per_page": 200, "page": page})
    if not batch:
        break
    members.extend(batch)
    if len(batch) < 200:
        break
    page += 1

print(f"Found {len(members)} members\n")

# Load existing state
with open("state.json") as f:
    state = json.load(f)

runners = []
for m in members:
    firstname = m.get("firstname", "")
    lastname  = m.get("lastname", "")
    key       = name_key(firstname, lastname)
    # Display name: use abbreviated form Strava gives us
    display   = f"{firstname} {lastname}".strip().rstrip(".")
    handle    = key.lower().replace("_", ".")

    runners.append({
        "name":            display,
        "strava_handle":   handle,
        "strava_name_key": key,
        "total_km":        0,
        "runs":            [],
    })
    print(f"  {display} → key: {key}")

state["runners"]          = runners
state["strava_club_id"]   = CLUB_ID
state["last_updated"]     = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
state["last_strava_sync"] = None

with open("state.json", "w") as f:
    json.dump(state, f, indent=2)

print(f"\n✅  state.json updated with {len(runners)} runners from '{club['name']}'")
print("Next step: set GitHub Secrets, then trigger the sync workflow.")
