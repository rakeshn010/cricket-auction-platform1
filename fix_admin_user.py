"""
Fix admin user - set is_admin flag to True
Run this once to grant admin access to your user
"""
from database import db
import sys

def fix_admin_user(email: str):
    """Set is_admin=True for the specified user."""
    
    print(f"Looking for user: {email}")
    
    user = db.users.find_one({"email": email})
    
    if not user:
        print(f"❌ User not found: {email}")
        return False
    
    print(f"✅ Found user: {user['email']}")
    print(f"   Current is_admin: {user.get('is_admin', False)}")
    print(f"   Current role: {user.get('role', 'viewer')}")
    
    # Update user to be admin
    result = db.users.update_one(
        {"email": email},
        {"$set": {
            "is_admin": True,
            "role": "admin"
        }}
    )
    
    if result.modified_count > 0:
        print(f"✅ Successfully set is_admin=True for {email}")
        
        # Verify
        updated_user = db.users.find_one({"email": email})
        print(f"   New is_admin: {updated_user.get('is_admin', False)}")
        print(f"   New role: {updated_user.get('role', 'viewer')}")
        return True
    else:
        print(f"⚠️  No changes made (already admin?)")
        return True


if __name__ == "__main__":
    # Your admin email
    admin_email = "rakeshn9380@gmail.com"
    
    print("🔧 Fixing admin user status...\n")
    
    success = fix_admin_user(admin_email)
    
    if success:
        print("\n✅ Admin user fixed!")
        print("   Please logout and login again for changes to take effect.")
        sys.exit(0)
    else:
        print("\n❌ Failed to fix admin user")
        sys.exit(1)
