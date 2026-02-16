"""
Clear rate limits - Use this if you get locked out
"""
import requests

print("=" * 50)
print("🔓 Clear Rate Limits")
print("=" * 50)
print()

# This will clear rate limits by restarting the server
# Or you can add an admin endpoint to clear them

print("To clear rate limits, you have 2 options:")
print()
print("Option 1: Restart the server")
print("  - Stop the server (Ctrl+C)")
print("  - Start it again: venv\\Scripts\\python main_new.py")
print()
print("Option 2: Wait 5 minutes")
print("  - Rate limits automatically expire after 5 minutes")
print()
print("Option 3: Disable rate limiting temporarily")
print("  - Edit .env file")
print("  - Set: ENABLE_RATE_LIMITING=false")
print("  - Restart server")
print()

# Check current status
try:
    response = requests.get("http://localhost:8000/health", timeout=2)
    if response.status_code == 200:
        print("✅ Server is running")
        print("   URL: http://localhost:8000")
    else:
        print("⚠️  Server returned status:", response.status_code)
except Exception as e:
    print("❌ Server is not running or not accessible")
    print(f"   Error: {e}")

print()
print("=" * 50)
