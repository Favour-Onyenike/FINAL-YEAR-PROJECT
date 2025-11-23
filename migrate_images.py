import sqlite3
import os
import base64
import sys

# Setup DB connection
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(PROJECT_ROOT, "unimarket.db")
UPLOADS_DIR = os.path.join(PROJECT_ROOT, "backend", "uploads", "products")

def migrate_images():
    print("=== STARTING IMAGE MIGRATION TO DATABASE ===")
    
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Migrate Product Images
    print("\n--- Migrating Product Images ---")
    cursor.execute("SELECT id, image_url FROM product_images WHERE image_data IS NULL")
    rows = cursor.fetchall()
    
    migrated_count = 0
    missing_count = 0
    
    for row in rows:
        img_id, image_url = row
        
        # Extract filename from URL
        # URL format: /uploads/products/filename.jpg
        if "/uploads/products/" in image_url:
            filename = image_url.split("/uploads/products/")[-1]
            file_path = os.path.join(UPLOADS_DIR, filename)
            
            if os.path.exists(file_path):
                try:
                    with open(file_path, "rb") as image_file:
                        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                        
                    # Update DB
                    cursor.execute("UPDATE product_images SET image_data = ? WHERE id = ?", (encoded_string, img_id))
                    migrated_count += 1
                    print(f"✅ Migrated: {filename} (ID: {img_id})")
                except Exception as e:
                    print(f"❌ Error reading {filename}: {e}")
            else:
                print(f"⚠️ Missing file: {filename} (ID: {img_id})")
                missing_count += 1
    
    print(f"Product Images: {migrated_count} migrated, {missing_count} missing.")

    # 2. Migrate User Profile Images
    print("\n--- Migrating User Profile Images ---")
    cursor.execute("SELECT id, profile_image FROM users WHERE profile_image IS NOT NULL AND profile_image_data IS NULL")
    rows = cursor.fetchall()
    
    user_migrated_count = 0
    
    for row in rows:
        user_id, profile_image = row
        
        if "/uploads/products/" in profile_image:
            filename = profile_image.split("/uploads/products/")[-1]
            file_path = os.path.join(UPLOADS_DIR, filename)
            
            if os.path.exists(file_path):
                try:
                    with open(file_path, "rb") as image_file:
                        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                        
                    # Update DB
                    cursor.execute("UPDATE users SET profile_image_data = ? WHERE id = ?", (encoded_string, user_id))
                    user_migrated_count += 1
                    print(f"✅ Migrated User {user_id} profile: {filename}")
                except Exception as e:
                    print(f"❌ Error reading {filename}: {e}")
    
    print(f"User Profiles: {user_migrated_count} migrated.")
    
    conn.commit()
    conn.close()
    print("\n=== MIGRATION COMPLETE ===")

if __name__ == "__main__":
    migrate_images()
