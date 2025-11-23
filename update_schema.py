import sqlite3
import os

# Setup DB connection
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(PROJECT_ROOT, "unimarket.db")

def update_schema():
    print("=== UPDATING DATABASE SCHEMA ===")
    
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Add image_data to product_images
    try:
        print("Adding image_data column to product_images...")
        cursor.execute("ALTER TABLE product_images ADD COLUMN image_data TEXT")
        print("✅ Added image_data column")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("ℹ️ Column image_data already exists")
        else:
            print(f"❌ Error: {e}")

    # 2. Add profile_image_data to users
    try:
        print("Adding profile_image_data column to users...")
        cursor.execute("ALTER TABLE users ADD COLUMN profile_image_data TEXT")
        print("✅ Added profile_image_data column")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("ℹ️ Column profile_image_data already exists")
        else:
            print(f"❌ Error: {e}")
            
    conn.commit()
    conn.close()
    print("\n=== SCHEMA UPDATE COMPLETE ===")

if __name__ == "__main__":
    update_schema()
