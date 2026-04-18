#!/usr/bin/env python3
"""
List all Strava clubs for the authenticated athlete.
Run this after strava-auth.py to find your club ID.

Usage: python3 scripts/list-clubs.py <access_token>
"""

import json
import sys
import urllib.request

if len(sys.argv) < 2:
    raise SystemExit("Usage: python3 scripts/list-clubs.py <access_token>")

ACCESS_TOKEN = sys.argv[1]

req = urllib.request.Request("https://www.strava.com/api/v3/athlete/clubs?per_page=100")
req.add_header("Authorization", f"Bearer {ACCESS_TOKEN}")
with urllib.request.urlopen(req) as resp:
    clubs = json.loads(resp.read())

if not clubs:
    print("No clubs found for this athlete.")
    sys.exit(0)

print(f"\nYour Strava clubs ({len(clubs)} found):\n")
print(f"  {'ID':<12} {'Members':<10} Name")
print(f"  {'─'*10:<12} {'─'*7:<10} {'─'*30}")
for club in clubs:
    print(f"  {club['id']:<12} {club['member_count']:<10} {club['name']}")

print(f"\nNext step: python3 scripts/init-members.py <access_token> <club_id>")
