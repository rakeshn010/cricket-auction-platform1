"""
Find players with the specific 404 images
"""
from database import db

# The images showing 404
missing_images = [
    "player_8343656ca0074021bf79f9b8e2676361.jpg",
    "player_36c2560c5ba14fe4a66688dde39ad195.jpeg",
    "player_c230ae625b3c40f29b6f18eeb8d43a8b.jpg"
]

print("\n🔍 Searching for players with these images:\n")

for img in missing_images:
    # Search for this image in database
    players = list(db.players.find({"image_path": {"$regex": img}}))
    
    if players:
        print(f"❌ Found {len(players)} player(s) with {img}:")
        for p in players:
            print(f"   - {p.get('name')} (ID: {p.get('_id')})")
            print(f"     Status: {p.get('status')}")
            print(f"     Approved: {p.get('is_approved')}")
            print(f"     Image: {p.get('image_path')}")
            
            # Remove the image_path
            db.players.update_one(
                {"_id": p["_id"]},
                {"$unset": {"image_path": ""}}
            )
            print(f"     ✅ Removed image_path")
    else:
        print(f"✅ No players found with {img}")

print("\n✅ Done! Refresh your browser.")
