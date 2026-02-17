"""
Check all collections for player data
"""
from database import db

print("\n📊 Database Collections Status:\n")

# Players
players_count = db.players.count_documents({})
print(f"Players: {players_count}")

# Teams
teams_count = db.teams.count_documents({})
print(f"Teams: {teams_count}")

# Bids
bids_count = db.bids.count_documents({})
print(f"Bids: {bids_count}")

# Auction status
auction = db.auction_status.find_one({})
if auction:
    print(f"\nAuction Status:")
    print(f"  Active: {auction.get('active', False)}")
    print(f"  Current Player: {auction.get('current_player_id', 'None')}")
else:
    print(f"\nAuction Status: Not found")

# Check if there are any players with status='sold'
sold_players = list(db.players.find({"status": "sold"}))
print(f"\nSold Players: {len(sold_players)}")
for p in sold_players:
    print(f"  - {p.get('name')}: Team {p.get('final_team', 'Unknown')}")

# Check teams with players
teams = list(db.teams.find({}))
print(f"\nTeams with player counts:")
for team in teams:
    print(f"  - {team.get('name')}: {team.get('players_count', 0)} players")
