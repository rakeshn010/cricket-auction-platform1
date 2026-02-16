from database import db

# Make rakeshn9380@gmail.com an admin
result = db.users.update_one(
    {'email': 'rakeshn9380@gmail.com'},
    {'$set': {'is_admin': True, 'role': 'admin'}}
)

print(f'Updated: {result.modified_count} user(s)')

# Verify
user = db.users.find_one({'email': 'rakeshn9380@gmail.com'})
if user:
    print(f"User: {user['email']}")
    print(f"Is Admin: {user.get('is_admin')}")
    print(f"Role: {user.get('role')}")
