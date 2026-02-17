"""
Show admin user information
"""
from database import db

# Find admin user
admin = db.users.find_one({"is_admin": True})

if admin:
    print("\n🔐 ADMIN CREDENTIALS\n")
    print("=" * 50)
    print(f"Email:    {admin.get('email')}")
    print(f"Role:     {admin.get('role')}")
    print(f"Is Admin: {admin.get('is_admin')}")
    print(f"User ID:  {admin.get('_id')}")
    print("=" * 50)
    print("\n⚠️  Password is hashed in database (cannot be shown)")
    print("💡 If you forgot password, you can reset it\n")
else:
    print("\n❌ No admin user found in database\n")
