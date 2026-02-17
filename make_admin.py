"""Make user admin on Railway"""
from database import db

email = "rakeshn9380@gmail.com"
result = db.users.update_one(
    {"email": email},
    {"$set": {"role": "admin"}}
)

if result.modified_count > 0:
    print(f"✅ User {email} is now admin!")
else:
    print(f"⚠️ User {email} not found or already admin")
