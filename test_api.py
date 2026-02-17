"""
Test the eligible players API endpoint.
"""
from database import db

print("=" * 70)
print("TESTING ELIGIBLE PLAYERS QUERY")
print("=" * 70)

# This is the exact query used by the API
players = list(db.players.find({
    "is_approved": True,
    "is_live": False,
    "status": {"$in": ["available", "unsold"]}
}).sort("name", 1))

print(f"\n✅ Found {len(players)} eligible players\n")

if players:
    for i, p in enumerate(players, 1):
        print(f"{i}. {p.get('name')}")
        print(f"   ID: {p['_id']}")
        print(f"   Status: {p.get('status')}")
        print(f"   Base Price: {p.get('base_price')}")
        print(f"   Is Approved: {p.get('is_approved')}")
        print(f"   Is Live: {p.get('is_live')}")
        print()
else:
    print("❌ No players found!")
    print("\nChecking what's wrong...")
    
    total = db.players.count_documents({})
    approved = db.players.count_documents({"is_approved": True})
    not_live = db.players.count_documents({"is_live": False})
    available = db.players.count_documents({"status": {"$in": ["available", "unsold"]}})
    
    print(f"\n  Total players: {total}")
    print(f"  Approved: {approved}")
    print(f"  Not live: {not_live}")
    print(f"  Available/Unsold: {available}")
    
    # Show all players
    print("\n  All players:")
    all_players = list(db.players.find({}))
    for p in all_players:
        print(f"    - {p.get('name')}: status={p.get('status')}, approved={p.get('is_approved')}, live={p.get('is_live')}")
