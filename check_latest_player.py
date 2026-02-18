"""
Check the latest registered player and their image
"""
from pymongo import MongoClient

# Railway MongoDB connection string
RAILWAY_DB_URL = "mongodb+srv://rakeshfivem_db_user:Rakesh9380@cricket-auction.jd5q5sg.mongodb.net/?appName=cricket-auction"

print(f"\n🔗 Connecting to Railway database...")

try:
    client = MongoClient(RAILWAY_DB_URL)
    db = client.cricket_auction
    
    # Get the latest player
    latest_player = db.players.find_one(sort=[("created_at", -1)])
    
    if latest_player:
        print(f"\n📊 Latest Player:")
        print(f"   Name: {latest_player.get('name')}")
        print(f"   ID: {latest_player.get('_id')}")
        print(f"   Role: {latest_player.get('role')}")
        print(f"   Category: {latest_player.get('category')}")
        print(f"   Status: {latest_player.get('status')}")
        print(f"   Approved: {latest_player.get('is_approved')}")
        print(f"   Created: {latest_player.get('created_at')}")
        
        image_path = latest_player.get('image_path')
        if image_path:
            print(f"\n✅ Image Path: {image_path}")
            if image_path.startswith('http'):
                print(f"   Type: Cloudinary URL")
            else:
                print(f"   Type: Local path (won't work on Railway!)")
        else:
            print(f"\n❌ No image uploaded")
    else:
        print("No players found")
    
    # Count total players
    total = db.players.count_documents({})
    print(f"\n📊 Total players: {total}")
    
    client.close()

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
