"""
Test login credentials
"""
from pymongo import MongoClient
from bson import ObjectId
import bcrypt

# Connect to database
client = MongoClient("mongodb://localhost:27017")
db = client["cricket_auction"]

# Get admin user
user = db.users.find_one({"email": "admin@cricket.com"})

if not user:
    print("❌ Admin user not found!")
else:
    print("✅ Admin user found!")
    print(f"Email: {user['email']}")
    print(f"Is Admin: {user.get('is_admin', False)}")
    print(f"Is Active: {user.get('is_active', True)}")
    
    # Test password
    test_password = "admin123"
    stored_hash = user["password_hash"]
    
    try:
        is_valid = bcrypt.checkpw(test_password.encode('utf-8'), stored_hash.encode('utf-8'))
        if is_valid:
            print(f"✅ Password 'admin123' is CORRECT")
        else:
            print(f"❌ Password 'admin123' is WRONG")
    except Exception as e:
        print(f"❌ Error checking password: {e}")

client.close()
