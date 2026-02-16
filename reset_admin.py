"""
Reset admin account - Delete and recreate
"""
from pymongo import MongoClient
from datetime import datetime, timezone
import bcrypt

# Database connection
DATABASE_URL = "mongodb://localhost:27017"
DB_NAME = "cricket_auction"

def hash_password(password: str) -> str:
    """Hash password using bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def reset_admin():
    """Delete and recreate admin account."""
    print("=" * 50)
    print("🏏 Cricket Auction - Reset Admin Account")
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
        
        # Delete existing admin
        result = db.users.delete_one({"email": admin_email})
        if result.deleted_count > 0:
            print(f"✅ Deleted existing admin account")
        else:
            print(f"ℹ️  No existing admin account found")
        
        # Create new admin user
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
        print("🌐 Login at: http://localhost:8000")
        print()
        
        # Verify password works
        user = db.users.find_one({"email": admin_email})
        is_valid = bcrypt.checkpw(admin_password.encode('utf-8'), user["password_hash"].encode('utf-8'))
        
        if is_valid:
            print("✅ Password verification: SUCCESS")
        else:
            print("❌ Password verification: FAILED")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    reset_admin()
