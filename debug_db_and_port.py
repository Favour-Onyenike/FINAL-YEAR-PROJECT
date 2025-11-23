import sqlite3
import os
import socket

# Setup DB connection
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(PROJECT_ROOT, "unimarket.db")

def check_db():
    print("\n=== CHECKING DATABASE ===")
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT id, image_url, length(image_data) FROM product_images WHERE id = 8")
        row = cursor.fetchone()
        if row:
            print(f"✅ Record found: ID={row[0]}, URL={row[1]}")
            print(f"   Image Data Length: {row[2]} bytes")
        else:
            print("❌ Record with ID 8 NOT FOUND")
            
        # Check total migrated
        cursor.execute("SELECT count(*) FROM product_images WHERE image_data IS NOT NULL")
        count = cursor.fetchone()[0]
        print(f"Total images with data: {count}")
        
    except Exception as e:
        print(f"❌ DB Error: {e}")
    finally:
        conn.close()

def check_port(port):
    print(f"\n=== CHECKING PORT {port} ===")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', port))
    if result == 0:
        print(f"✅ Port {port} is OPEN (Server is running)")
    else:
        print(f"❌ Port {port} is CLOSED (Server is NOT running)")
    sock.close()

if __name__ == "__main__":
    check_db()
    check_port(8000)
