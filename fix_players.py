"""
Fix existing players by adding missing fields.
"""
from database import db

print("=" * 70)
print("FIXING PLAYER RECORDS")
print("=" * 70)

# Update all players to have required fields
result = db.players.update_many(
    {},  # All players
    {
        "$set": {
            "is_approved": True,  # Mark existing players as approved
            "approval_status": "approved",
            "base_price_status": "approved"
        }
    }
)

print(f"\n✅ Updated {result.modified_count} players")

# Set base_price to 1000 for players without it
result2 = db.players.update_many(
    {"base_price": None},
    {"$set": {"base_price": 1000.0}}
)

print(f"✅ Set base price for {result2.modified_count} players")

# Show updated players
print("\n" + "=" * 70)
print("UPDATED PLAYERS")
print("=" * 70)

players = list(db.players.find({}))
for i, player in enumerate(players, 1):
    print(f"\n{i}. {player.get('name')}")
    print(f"   Status: {player.get('status')}")
    print(f"   Base Price: {player.get('base_price')}")
    print(f"   Approved: {player.get('is_approved')}")
    print(f"   Approval Status: {player.get('approval_status')}")

print("\n" + "=" * 70)
print("✅ ALL PLAYERS FIXED!")
print("=" * 70)
print("\nPlayers should now appear in admin panel and team dashboard.")
