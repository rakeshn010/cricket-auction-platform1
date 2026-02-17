"""
Clear the current player from auction config.
"""
from database import db

def clear_current_player():
    """Clear current_player_id from auction config."""
    
    # Get current config from the config collection
    config = db.config.find_one({"key": "auction"})
    
    if config:
        print(f"Current player ID: {config.get('current_player_id')}")
        print(f"Current player name: {config.get('current_player_name')}")
        
        # Update to clear current player
        result = db.config.update_one(
            {"key": "auction"},
            {"$set": {
                "current_player_id": None,
                "current_player_name": None
            }}
        )
        
        print(f"\n✅ Updated {result.modified_count} document(s)")
        
        # Verify
        config = db.config.find_one({"key": "auction"})
        print(f"\nAfter update:")
        print(f"Current player ID: {config.get('current_player_id')}")
        print(f"Current player name: {config.get('current_player_name')}")
    else:
        print("No auction config found")

if __name__ == "__main__":
    clear_current_player()
