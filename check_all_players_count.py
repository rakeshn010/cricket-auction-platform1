"""
Check all players and show the newest ones
"""
from database import db

# Get total count
total = db.players.count_documents({})
print(f"\n📊 Total Players: {total}")

# Get the 5 most recent players
recent = list(db.players.find().sort("created_at", -1).limit(5))

print(f"\n📋 5 Most Recent Players:\n")
for i, player in enumerate(recent, 1):
    print(f"{i}. {player.get('name')}")
    print(f"   ID: {player.get('_id')}")
    print(f"   Created: {player.get('created_at')}")
    print(f"   Image: {player.get('image_path', 'No image')}")
    print(f"   Approved: {player.get('is_approved')}")
    print()
