"""
Verify and fix user role in database.
This script checks the user's role and updates both 'role' and 'is_admin' fields.
"""
from database import db
from bson import ObjectId

# User email
email = "rakeshn9380@gmail.com"

# Find user
user = db.users.find_one({"email": email})

if not user:
    print(f"❌ User not found: {email}")
    exit(1)

print(f"✅ User found: {email}")
print(f"   User ID: {user['_id']}")
print(f"   Current role: {user.get('role', 'NOT SET')}")
print(f"   Current is_admin: {user.get('is_admin', 'NOT SET')}")

# Update both fields to ensure consistency
result = db.users.update_one(
    {"_id": user["_id"]},
    {
        "$set": {
            "role": "admin",
            "is_admin": True
        }
    }
)

print(f"\n✅ Update result: {result.modified_count} document(s) modified")

# Verify the update
user_after = db.users.find_one({"_id": user["_id"]})
print(f"\n✅ After update:")
print(f"   Role: {user_after.get('role')}")
print(f"   is_admin: {user_after.get('is_admin')}")

# Also check if there are any indexes that might be causing issues
indexes = list(db.users.list_indexes())
print(f"\n📋 User collection indexes:")
for idx in indexes:
    print(f"   - {idx['name']}: {idx.get('key', {})}")
