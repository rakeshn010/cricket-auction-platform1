"""
Create admin account script.
Run this to create an admin account directly in the database.
"""
from pymongo import MongoClient
from datetime import datetime, timezone
import sys
import bcrypt

# Database connection
DATABASE_URL = "mongodb://localhost:27017"
DB_NAME = "cricket_auction"

def hash_password(password: str) -> str:
    """Hash password using bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def create_admin():
    """Create admin account."""
    print("=" * 50)
    print("🏏 Cricket Auction - Create Admin Account")
    print("=" * 50)
    print()
    
    # Admin credentials
    admin_email = "admin@cricket.com"
    admin_password = "admin123"
    admin_name = "Admin User"
    
    try:
        # Connect to database
        client = MongoClient(DATABASE_URL)
        db = client[DB_NAME]
        
        # Check if admin already exists
        existing = db.users.find_one({"email": admin_email})
        if existing:
            print(f"⚠️  Admin account already exists!")
            print(f"📧 Email: {admin_email}")
            print()
            print("To reset password, delete the user from database first:")
            print(f"   mongosh")
            print(f"   use {DB_NAME}")
            print(f"   db.users.deleteOne({{email: '{admin_email}'}})")
            return
        
        # Create admin user
        admin_doc = {
            "email": admin_email,
            "password_hash": hash_password(admin_password),
            "name": admin_name,
            "is_active": True,
            "is_admin": True,
            "role": "admin",
            "team_id": None,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        
        db.users.insert_one(admin_doc)
        
        print("✅ Admin account created successfully!")
        print()
        print("=" * 50)
        print("📧 Admin Credentials:")
        print("=" * 50)
        print(f"Email:    {admin_email}")
        print(f"Password: {admin_password}")
        print("=" * 50)
        print()
        print("⚠️  IMPORTANT: Change the password after first login!")
        print()
        print("🌐 Login at: http://localhost:8000")
        print("   1. Click 'Admin Login' tab")
        print("   2. Use the credentials above")
        print()
        
        client.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    create_admin()
