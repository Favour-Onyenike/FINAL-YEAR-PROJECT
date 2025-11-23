import sqlite3
import os

# Setup DB connection
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(PROJECT_ROOT, "unimarket.db")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("\n=== PRODUCT IMAGES ===")
cursor.execute("SELECT id, product_id, image_url FROM product_images")

missing_images = []
for row in cursor.fetchall():
    img_id, product_id, image_url = row
    
    # Extract filename from URL like /uploads/products/abc.jpeg
    if image_url.startswith("/uploads/products/"):
        filename = image_url.replace("/uploads/products/", "")
        filepath = os.path.join(PROJECT_ROOT, "backend", "uploads", "products", filename)
        
        if not os.path.exists(filepath):
            missing_images.append({
                'id': img_id,
                'product_id': product_id,
                'image_url': image_url,
                'filename': filename
            })
            print(f"❌ MISSING: Product {product_id}, Image ID {img_id}, File: {filename}")
        else:
            print(f"✅ EXISTS: Product {product_id}, Image ID {img_id}, File: {filename}")

print(f"\n\n=== SUMMARY ===")
print(f"Total missing images: {len(missing_images)}")

if missing_images:
    print("\nMissing image filenames:")
    for img in missing_images:
        print(f"  - {img['filename']} (Product ID: {img['product_id']})")

conn.close()
