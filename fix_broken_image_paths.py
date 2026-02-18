"""
Fix broken image paths in database
Remove image_path for players whose images don't exist
"""
from database import db
import os

# Get all players with image_path
players = list(db.players.find({"image_path": {"$exists": True, "$ne": None, "$ne": ""}}))

print(f"\n📊 Found {len(players)} players with image_path\n")

fixed_count = 0

for player in players:
    image_path = player.get("image_path", "")
    
    if not image_path:
        continue
    
    # Check if it's a local path (not Cloudinary URL)
    if image_path.startswith("http"):
        print(f"✅ {player['name']}: Cloudinary URL - keeping")
        continue
    
    # Extract filename from path
    if "/static/uploads/players/" in image_path:
        filename = image_path.split("/static/uploads/players/")[-1]
        full_path = os.path.join("static", "uploads", "players", filename)
    else:
        full_path = image_path.replace("/", os.sep)
    
    # Check if file exists
    if not os.path.exists(full_path):
        print(f"❌ {player['name']}: {image_path} (MISSING - REMOVING)")
        
        # Remove image_path from database
        db.players.update_one(
            {"_id": player["_id"]},
            {"$unset": {"image_path": ""}}
        )
        fixed_count += 1
    else:
        print(f"✅ {player['name']}: {image_path} (EXISTS)")

print(f"\n📊 Summary:")
print(f"   Fixed: {fixed_count} players")
print(f"\n✅ Database cleaned! No more 404 errors for missing images.")
