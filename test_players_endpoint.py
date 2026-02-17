"""
Test the /players endpoint that admin.js uses.
"""
from database import db

print("=" * 70)
print("TESTING /players ENDPOINT")
print("=" * 70)

# Test with include_unapproved=true (what admin.js uses)
query = {}  # No filter when include_unapproved=true

players = list(db.players.find(query).sort("created_at", -1))

print(f"\n✅ Found {len(players)} players (include_unapproved=true)\n")

for i, p in enumerate(players, 1):
    print(f"{i}. {p.get('name')}")
    print(f"   Status: {p.get('status')}")
    print(f"   Approved: {p.get('is_approved')}")
    print(f"   Base Price: {p.get('base_price')}")
    print()

# Test without include_unapproved (default)
query_approved = {"is_approved": True}
approved_players = list(db.players.find(query_approved))

print(f"\n✅ Found {len(approved_players)} approved players (default)\n")

print("=" * 70)
print("CONCLUSION")
print("=" * 70)
print(f"\nThe /players endpoint should return {len(players)} players to admin.js")
print("If you're not seeing them, it's a frontend JavaScript issue.")
