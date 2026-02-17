"""
Test what image URLs are being generated
"""
from database import db

# Get the one player
player = db.players.find_one({})

if player:
    print(f"\n📊 Player: {player.get('name')}")
    print(f"   _id: {player.get('_id')}")
    print(f"   image_path: {player.get('image_path')}")
    print(f"   photo: {player.get('photo')}")
    print(f"   image: {player.get('image')}")
    
    # Test URL construction
    image_path = player.get('image_path', '')
    if image_path:
        print(f"\n🔗 Image URL that should be used:")
        print(f"   {image_path}")
        
        # Check if it's absolute or relative
        if image_path.startswith('http'):
            print(f"   Type: Absolute URL")
        elif image_path.startswith('/'):
            print(f"   Type: Relative URL (from root)")
        else:
            print(f"   Type: Relative URL")
            
        # What the browser will request
        print(f"\n🌐 Browser will request:")
        print(f"   https://cricket-auction-platform1-production.up.railway.app{image_path}")
else:
    print("No players found!")
