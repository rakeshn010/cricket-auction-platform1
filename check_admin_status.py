"""
Check admin user status after reset
"""
from database import db

# Find admin user
admin = db.users.find_one({"email": "rakeshn9380@gmail.com"})

if admin:
    print("\n✅ Admin user exists in database\n")
    print("=" * 60)
    print(f"Email:        {admin.get('email')}")
    print(f"Role:         {admin.get('role')}")
    print(f"Is Admin:     {admin.get('is_admin')}")
    print(f"User ID:      {admin.get('_id')}")
    print(f"Has Password: {'Yes' if admin.get('password_hash') else 'No'}")
    print("=" * 60)
    
    # Check if password hash exists
    if not admin.get('password_hash'):
        print("\n❌ ERROR: Password hash is missing!")
        print("   This might have been cleared during reset\n")
    else:
        print("\n✅ Password hash exists - login should work")
        print("\n💡 If login still fails, try:")
        print("   1. Clear browser cache (Ctrl + Shift + R)")
        print("   2. Try incognito/private window")
        print("   3. Check browser console for errors\n")
else:
    print("\n❌ Admin user not found in database!")
    print("   The reset might have deleted the user\n")
