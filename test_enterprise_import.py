"""Test if enterprise modules can be imported"""
try:
    from enterprise.integration import enterprise
    print("✅ Enterprise modules available")
    print(f"Enterprise object: {enterprise}")
except ImportError as e:
    print(f"❌ Enterprise import failed: {e}")
