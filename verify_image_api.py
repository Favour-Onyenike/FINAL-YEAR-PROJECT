import urllib.request
import sys

def verify_image(image_id):
    url = f"http://localhost:8000/api/images/{image_id}"
    print(f"Checking {url}...")
    
    try:
        with urllib.request.urlopen(url) as response:
            status_code = response.getcode()
            content_type = response.info().get_content_type()
            content_length = response.length
            
            print(f"Status Code: {status_code}")
            print(f"Content-Type: {content_type}")
            print(f"Content-Length: {content_length} bytes")
            
            if status_code == 200 and content_type == 'image/jpeg':
                print("✅ SUCCESS: Image served correctly from DB!")
                return True
            else:
                print("❌ FAILURE: Image not served correctly.")
                return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    # Test with image ID 8 (which we saw migrated in the logs)
    verify_image(8)
