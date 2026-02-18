"""
Test Cloudinary configuration
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Check environment variables
cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME", "")
api_key = os.getenv("CLOUDINARY_API_KEY", "")
api_secret = os.getenv("CLOUDINARY_API_SECRET", "")

print("\n🔍 Checking Cloudinary Configuration:\n")
print(f"CLOUDINARY_CLOUD_NAME: {cloud_name if cloud_name else '❌ NOT SET'}")
print(f"CLOUDINARY_API_KEY: {'✅ SET' if api_key else '❌ NOT SET'}")
print(f"CLOUDINARY_API_SECRET: {'✅ SET' if api_secret else '❌ NOT SET'}")

if cloud_name and api_key and api_secret and cloud_name != "your_cloud_name":
    print("\n✅ Cloudinary is configured!")
    
    # Try to import and test
    try:
        import cloudinary
        import cloudinary.uploader
        
        cloudinary.config(
            cloud_name=cloud_name,
            api_key=api_key,
            api_secret=api_secret,
            secure=True
        )
        
        print("\n🧪 Testing Cloudinary connection...")
        
        # Test with a simple text file
        test_content = b"Test upload"
        result = cloudinary.uploader.upload(
            test_content,
            folder="cricket_auction/test",
            resource_type="raw"
        )
        
        print(f"✅ Upload successful!")
        print(f"   URL: {result.get('secure_url')}")
        
        # Clean up test file
        cloudinary.uploader.destroy(result.get('public_id'), resource_type="raw")
        print(f"✅ Cleanup successful!")
        
    except ImportError:
        print("\n⚠️ Cloudinary package not installed!")
        print("   Run: pip install cloudinary")
    except Exception as e:
        print(f"\n❌ Cloudinary test failed: {e}")
else:
    print("\n❌ Cloudinary is NOT configured properly!")
    print("\nExpected in .env or Railway environment:")
    print("CLOUDINARY_CLOUD_NAME=de3rgl8gz")
    print("CLOUDINARY_API_KEY=your_key")
    print("CLOUDINARY_API_SECRET=your_secret")
