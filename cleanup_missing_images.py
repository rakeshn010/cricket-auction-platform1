"""
Clean up player records with missing image files.
Sets image_path to None for players whose image files don't exist.
"""
import os
from pathlib import Path
from database import db

def cleanup_missing_images():
    """Remove image_path from players where the image file doesn't exist."""
    
    # Get all players with image paths
    players_with_images = list(db.players.find({"image_path": {"$ne": None, "$exists": True}}))
    
    print(f"Found {len(players_with_images)} players with image paths")
    
    updated_count = 0
    
    for player in players_with_images:
        image_path = player.get('image_path', '')
        
        if not image_path:
            continue
        
        # Extract the file path from the URL
        # Format: /static/uploads/players/player_xxx.jpg
        if image_path.startswith('/static/'):
            file_path = image_path.replace('/static/', 'static/')
        else:
            file_path = image_path
        
        # Check if file exists
        if not os.path.exists(file_path):
            print(f"❌ Missing image for {player['name']}: {image_path}")
            
            # Update player to remove image_path
            result = db.players.update_one(
                {"_id": player["_id"]},
                {"$set": {"image_path": None}}
            )
            
            if result.modified_count > 0:
                updated_count += 1
                print(f"   ✅ Cleared image_path for {player['name']}")
        else:
            print(f"✅ Image exists for {player['name']}: {image_path}")
    
    print(f"\n📊 Summary:")
    print(f"   Total players checked: {len(players_with_images)}")
    print(f"   Players updated: {updated_count}")
    print(f"   Players with valid images: {len(players_with_images) - updated_count}")

if __name__ == "__main__":
    cleanup_missing_images()
