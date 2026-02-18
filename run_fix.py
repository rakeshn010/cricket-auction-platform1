"""
Fix broken image paths in Railway's production database
"""
from pymongo import MongoClient

# Railway MongoDB connection string
RAILWAY_DB_URL = "mongodb+srv://rakeshfivem_db_user:Rakesh9380@cricket-auction.jd5q5sg.mongodb.net/?appName=cricket-auction"

print(f"\n🔗 Connecting to Railway database...")

try:
    client = MongoClient(RAILWAY_DB_URL)
    db = client.cricket_auction
    
    # Test connection
    db.command('ping')
    print("✅ Connected successfully!")
    
    # Count total players
    total_players = db.players.count_documents({})
    print(f"📊 Total players in database: {total_players}")
    
    # The 3 images showing 404 errors
    missing_images = [
        "player_8343656ca0074021bf79f9b8e2676361.jpg",
        "player_36c2560c5ba14fe4a66688dde39ad195.jpeg",
        "player_c230ae625b3c40f29b6f18eeb8d43a8b.jpg"
    ]
    
    print(f"\n🔍 Searching for players with broken images...\n")
    
    fixed_count = 0
    
    for img in missing_images:
        # Search for this image in database
        players = list(db.players.find({"image_path": {"$regex": img}}))
        
        if players:
            print(f"❌ Found {len(players)} player(s) with {img}:")
            for p in players:
                print(f"   - {p.get('name')} (ID: {p.get('_id')})")
                print(f"     Status: {p.get('status')}")
                print(f"     Image: {p.get('image_path')}")
                
                # Remove the image_path
                result = db.players.update_one(
                    {"_id": p["_id"]},
                    {"$unset": {"image_path": ""}}
                )
                
                if result.modified_count > 0:
                    print(f"     ✅ Removed image_path from database")
                    fixed_count += 1
                else:
                    print(f"     ⚠️ Failed to update")
        else:
            print(f"✅ No players found with {img}")
    
    print(f"\n📊 Summary:")
    print(f"   Total players: {total_players}")
    print(f"   Fixed: {fixed_count} players")
    print(f"\n✅ Done! Refresh your browser (Ctrl+Shift+R) - no more 404 errors!")
    
    client.close()

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
