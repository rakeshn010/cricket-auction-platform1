"""
Complete fix for all player fields.
"""
from database import db

print("=" * 70)
print("COMPLETE PLAYER FIX")
print("=" * 70)

# Update all players with all required fields
result = db.players.update_many(
    {},
    {
        "$set": {
            "is_approved": True,
            "is_live": False,
            "approval_status": "approved",
            "base_price_status": "approved"
        }
    }
)

print(f"\n✅ Updated {result.modified_count} players")

# Verify
players = list(db.players.find({}))
print(f"\n📊 Total players: {len(players)}")
print(f"   Available: {db.players.count_documents({'status': 'available'})}")
print(f"   In Auction: {db.players.count_documents({'status': 'in_auction'})}")
print(f"   Approved: {db.players.count_documents({'is_approved': True})}")
print(f"   Live: {db.players.count_documents({'is_live': True})}")

print("\n" + "=" * 70)
print("✅ PLAYERS READY!")
print("=" * 70)
print("\nPlayers should now appear in:")
print("  - Admin Player Management")
print("  - Team Dashboard")
print("  - Eligible Players List")
