from sqlalchemy import create_engine, text
import os

# Setup DB connection
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(PROJECT_ROOT, "unimarket.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"
engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    print("\n=== USERS ===")
    result = conn.execute(text("SELECT id, username, full_name FROM users"))
    for row in result:
        print(f"ID: {row.id}, Username: {row.username}, Name: {row.full_name}")

    print("\n=== MESSAGES ===")
    result = conn.execute(text("SELECT id, sender_id, receiver_id, content FROM messages ORDER BY created_at DESC LIMIT 10"))
    for row in result:
        print(f"ID: {row.id}, Sender: {row.sender_id} -> Receiver: {row.receiver_id}, Content: {row.content}")
