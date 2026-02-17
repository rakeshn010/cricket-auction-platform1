"""
Check player image paths in detail
"""
from database import db
from bson import ObjectId

# Get all players
players = list(db.players.find({}))

print(f"\n📊 Total players in database: {len(players)}\n")

# Check image fields
has_image_path = 0
has_photo = 0
has_image = 0
no_image = 0

for player in players:
    name = player.get('name', 'Unknown')
    player_id = str(player.get('_id', ''))
    
    image_path = player.get('image_path')
    photo = player.get('photo')
    image = player.get('image')
    
    if image_path:
        print(f"✅ {name}: image_path = {image_path}")
        has_image_path += 1
    elif photo:
        print(f"📷 {name}: photo = {photo}")
        has_photo += 1
    elif image:
        print(f"🖼️ {name}: image = {image}")
        has_image += 1
    else:
        print(f"❌ {name}: No image field")
        no_image += 1

print(f"\n📊 Summary:")
print(f"   Has image_path: {has_image_path}")
print(f"   Has photo: {has_photo}")
print(f"   Has image: {has_image}")
print(f"   No image: {no_image}")
print(f"   Total: {len(players)}")

# Check for the specific missing images from console
missing_images = [
    "player_8343656ca0074021bf79f9b8e2676361.jpg",
    "player_36c2560c5ba14fe4a66688dde39ad195.jpeg",
    "player_c230ae625b3c40f29b6f18eeb8d43a8b.jpg"
]

print(f"\n🔍 Checking for specific missing images from console:")
for img in missing_images:
    found = False
    for player in players:
        image_path = player.get('image_path', '')
        if img in image_path:
            print(f"   {img} -> Found in player: {player.get('name')}")
            found = True
            break
    if not found:
        print(f"   {img} -> NOT FOUND in any player")
