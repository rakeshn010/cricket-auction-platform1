"""
Check players in database and their status.
"""
from database import db
import json

print("=" * 70)
print("PLAYERS IN DATABASE")
print("=" * 70)

players = list(db.players.find({}))

if not players:
    print("\n❌ No players found in database!")
else:
    print(f"\n✅ Found {len(players)} players\n")
    
    for i, player in enumerate(players, 1):
        print(f"{i}. {player.get('name', 'Unknown')}")
        print(f"   ID: {player.get('_id')}")
        print(f"   Status: {player.get('status', 'N/A')}")
        print(f"   Role: {player.get('role', 'N/A')}")
        print(f"   Base Price: {player.get('base_price', 0)}")
        print(f"   Category: {player.get('category', 'N/A')}")
        print(f"   Approval Status: {player.get('approval_status', 'N/A')}")
        if player.get('final_team'):
            print(f"   Team: {player.get('final_team')}")
        if player.get('final_bid'):
            print(f"   Final Bid: {player.get('final_bid')}")
        print()

# Check by status
print("\n" + "=" * 70)
print("PLAYERS BY STATUS")
print("=" * 70)

statuses = ['pending', 'approved', 'available', 'in_auction', 'sold', 'unsold']
for status in statuses:
    count = db.players.count_documents({"status": status})
    if count > 0:
        print(f"  {status.upper()}: {count}")

# Check approval status
print("\n" + "=" * 70)
print("PLAYERS BY APPROVAL STATUS")
print("=" * 70)

approval_statuses = ['pending', 'approved', 'rejected']
for approval_status in approval_statuses:
    count = db.players.count_documents({"approval_status": approval_status})
    if count > 0:
        print(f"  {approval_status.upper()}: {count}")
