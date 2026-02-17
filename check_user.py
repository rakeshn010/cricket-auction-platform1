"""Check user role on Railway"""
from database import db

email = "rakeshn9380@gmail.com"
user = db.users.find_one({"email": email})

if user:
    print(f"User: {email}")
    print(f"Role: {user.get('role', 'NO ROLE')}")
    print(f"User ID: {user.get('_id')}")
else:
    print(f"User {email} not found!")
