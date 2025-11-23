from sqlalchemy import create_engine, text
import os

# Setup DB connection
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(PROJECT_ROOT, "unimarket.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

def optimize_database():
    print(f"Connecting to database at {DB_PATH}...")
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        print("1. Deleting all chat messages...")
        conn.execute(text("DELETE FROM messages"))
        conn.commit()
        print("   - Messages deleted.")
        
        print("2. Creating indexes...")
        try:
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_messages_sender_receiver ON messages (sender_id, receiver_id)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_messages_receiver_id ON messages (receiver_id)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_messages_is_read ON messages (is_read)"))
            print("   - Indexes created successfully.")
        except Exception as e:
            print(f"   - Error creating indexes: {e}")
            
    print("\nDatabase optimization complete!")

if __name__ == "__main__":
    optimize_database()
