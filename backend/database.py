from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./unimarket.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    from backend.models import User, University, Category, Product, ProductImage, SavedItem
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        if db.query(University).count() == 0:
            baze = University(id=1, name="Baze University", domain="bazeuniversity.edu.ng")
            db.add(baze)
            db.commit()
        
        if db.query(Category).count() == 0:
            categories = [
                Category(name="Textbooks"),
                Category(name="Electronics"),
                Category(name="Clothing"),
                Category(name="Furniture"),
                Category(name="Other")
            ]
            db.add_all(categories)
            db.commit()
    finally:
        db.close()
