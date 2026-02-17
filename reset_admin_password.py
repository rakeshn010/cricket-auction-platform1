"""
Reset admin password
"""
from database import db
from core.security import hash_password
from bson import ObjectId

# Admin email
admin_email = "rakeshn9380@gmail.com"

# New password (change this to what you want)
new_password = "Admin@123"

# Find admin user
admin = db.users.find_one({"email": admin_email})

if not admin:
    print(f"\n❌ Admin user not found: {admin_email}\n")
    exit(1)

# Hash the new password
hashed_password = hash_password(new_password)

# Update password
result = db.users.update_one(
    {"_id": admin["_id"]},
    {"$set": {"password_hash": hashed_password}}
)

if result.modified_count > 0:
    print("\n✅ Admin password reset successfully!\n")
    print("=" * 50)
    print(f"Email:    {admin_email}")
    print(f"Password: {new_password}")
    print("=" * 50)
    print("\n⚠️  IMPORTANT: Change this password after logging in!")
    print("   Go to Admin Dashboard → Settings → Change Password\n")
else:
    print("\n❌ Failed to reset password\n")
