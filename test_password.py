"""
Test password validation with different passwords.
"""
from core.password_validator import PasswordValidator

# Test passwords
test_passwords = [
    "password123",      # Common pattern
    "Password",         # Too short, no number
    "PASSWORD123",      # No lowercase
    "password123",      # No uppercase
    "Pass123",          # Too short
    "Password123",      # Should work!
    "MyPass2024",       # Should work!
    "Welcome99",        # Should work!
    "Test1234",         # Should work!
]

print("=" * 70)
print("PASSWORD VALIDATION TEST")
print("=" * 70)

for password in test_passwords:
    print(f"\nTesting: '{password}'")
    is_valid, errors = PasswordValidator.validate(password, raise_exception=False)
    
    if is_valid:
        print("  ✅ VALID")
    else:
        print("  ❌ INVALID")
        for error in errors:
            print(f"     - {error}")

print("\n" + "=" * 70)
