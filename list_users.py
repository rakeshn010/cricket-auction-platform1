"""
List all registered users in the database.
"""
from database import db

print("=" * 60)
print("REGISTERED USERS")
print("=" * 60)

users = list(db.users.find({}, {"email": 1, "name": 1, "role": 1, "is_admin": 1, "created_at": 1}))

if not users:
    print("No users found in database.")
else:
    print(f"\nTotal users: {len(users)}\n")
    
    for i, user in enumerate(users, 1):
        print(f"{i}. Email: {user.get('email')}")
        print(f"   Name: {user.get('name', 'N/A')}")
        print(f"   Role: {user.get('role', 'N/A')}")
        print(f"   Admin: {user.get('is_admin', False)}")
        print(f"   Created: {user.get('created_at', 'N/A')}")
        print()

print("=" * 60)
print("\nTo register a new user, use a different email address.")
print("If you need to delete a user, contact the admin.")
