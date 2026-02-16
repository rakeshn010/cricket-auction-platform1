"""
Direct Team Creation Script
Creates teams directly in MongoDB without using the browser
"""
from pymongo import MongoClient
from datetime import datetime, timezone
import bcrypt

# Connect to MongoDB
MONGO_URL = "mongodb://localhost:27017"
client = MongoClient(MONGO_URL)
db = client["cricket_auction"]

def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def create_team(name, budget, username, password, logo_path=""):
    """Create a new team"""
    
    # Check if username already exists
    if db.teams.find_one({"username": username.lower()}):
        print(f"❌ Error: Username '{username}' already exists!")
        return False
    
    team_doc = {
        "name": name,
        "budget": budget,
        "logo_path": logo_path,
        "username": username.lower(),
        "hashed_password": hash_password(password),
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }
    
    result = db.teams.insert_one(team_doc)
    print(f"✅ Team '{name}' created successfully!")
    print(f"   Username: {username}")
    print(f"   Budget: ₹{budget:,}")
    return True

# Example: Create IPL-style teams
print("=" * 60)
print("🏏 CRICKET AUCTION - TEAM CREATION")
print("=" * 60)
print()

teams_to_create = [
    {
        "name": "Mumbai Indians",
        "budget": 100000,
        "username": "mumbai",
        "password": "mumbai123",
        "logo_path": ""
    },
    {
        "name": "Chennai Super Kings",
        "budget": 100000,
        "username": "chennai",
        "password": "chennai123",
        "logo_path": ""
    },
    {
        "name": "Royal Challengers Bangalore",
        "budget": 100000,
        "username": "rcb",
        "password": "rcb123",
        "logo_path": ""
    },
    {
        "name": "Kolkata Knight Riders",
        "budget": 100000,
        "username": "kkr",
        "password": "kkr123",
        "logo_path": ""
    },
    {
        "name": "Delhi Capitals",
        "budget": 100000,
        "username": "delhi",
        "password": "delhi123",
        "logo_path": ""
    },
    {
        "name": "Rajasthan Royals",
        "budget": 100000,
        "username": "rajasthan",
        "password": "rajasthan123",
        "logo_path": ""
    }
]

print("Creating 6 IPL-style teams...")
print()

created_count = 0
for team in teams_to_create:
    if create_team(**team):
        created_count += 1
    print()

print("=" * 60)
print(f"✅ Created {created_count} teams successfully!")
print("=" * 60)
print()
print("Teams can now login at http://localhost:8000/")
print("Use the 'Team Login' tab with their username and password")
print()
print("Example:")
print("  Username: mumbai")
print("  Password: mumbai123")
print()
