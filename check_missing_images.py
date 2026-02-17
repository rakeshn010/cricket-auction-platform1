"""
Check for players with missing image files
"""
from database import db
import os

# Get all players with image_path
players = list(db.players.find({"image_path": {"$exists": True, "$ne": None, "$ne": ""}}))

print(f"\n📊 Found {len(players)} players with image_path in database\n")

missing_count = 0
existing_count = 0

for player in players:
    image_path = player.get("image_path", "")
    
    if not image_path:
        continue
    
    # Extract filename from path
    if "/static/uploads/players/" in image_path:
        filename = image_path.split("/static/uploads/players/")[-1]
        full_path = os.path.join("static", "uploads", "players", filename)
    else:
        full_path = image_path.replace("/", os.sep)
    
    # Check if file exists
    if os.path.exists(full_path):
        print(f"✅ {player['name']}: {image_path}")
        existing_count += 1
    else:
        print(f"❌ {player['name']}: {image_path} (MISSING)")
        print(f"   Player ID: {player['_id']}")
        missing_count += 1

print(f"\n📊 Summary:")
print(f"   Total: {len(players)}")
print(f"   Existing: {existing_count}")
print(f"   Missing: {missing_count}")

if missing_count > 0:
    print(f"\n🔧 To fix: Run cleanup script or manually remove image_path from these players")
