import os
import sqlalchemy
from sqlalchemy import create_engine, text
from backend.database import SQLALCHEMY_DATABASE_URL

def upgrade_database():
    print("=== UPGRADING DATABASE SCHEMA ===")
    print(f"Connecting to: {SQLALCHEMY_DATABASE_URL}")
    
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    
    with engine.connect() as connection:
        # 1. Add image_data to product_images
        try:
            print("Checking product_images table...")
            # Postgres syntax to add column if not exists is tricky in one line without PL/SQL
            # So we just try to add it and catch the error if it exists
            connection.execute(text("ALTER TABLE product_images ADD COLUMN image_data TEXT;"))
            print("✅ Added image_data column to product_images")
        except Exception as e:
            if "duplicate column" in str(e) or "already exists" in str(e):
                print("ℹ️ Column image_data already exists in product_images")
            else:
                print(f"❌ Error adding column to product_images: {e}")

        # 2. Add profile_image_data to users
        try:
            print("Checking users table...")
            connection.execute(text("ALTER TABLE users ADD COLUMN profile_image_data TEXT;"))
            print("✅ Added profile_image_data column to users")
        except Exception as e:
            if "duplicate column" in str(e) or "already exists" in str(e):
                print("ℹ️ Column profile_image_data already exists in users")
            else:
                print(f"❌ Error adding column to users: {e}")
                
        connection.commit()
    
    print("\n=== UPGRADE COMPLETE ===")

if __name__ == "__main__":
    upgrade_database()
