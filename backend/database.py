"""
DATABASE SETUP AND CONNECTION MODULE
=====================================
This file handles all database connection and initialization logic.
It's the central place where the database connection is configured.

WHAT HAPPENS HERE:
1. Creates a database engine (either SQLite or PostgreSQL based on DATABASE_URL)
2. Sets up session management for database operations
3. Creates all database tables on startup
4. Seeds the database with initial data (universities and categories)
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# =============================================================================
# DATABASE URL CONFIGURATION
# =============================================================================
# This reads the DATABASE_URL from environment variables
# If not set, defaults to SQLite (unimarket.db file in project root)
# 
# Examples:
# - SQLite: "sqlite:///./unimarket.db"
# - PostgreSQL: "postgresql://user:password@localhost/unimarket"
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./unimarket.db")

# =============================================================================
# CREATE DATABASE ENGINE
# =============================================================================
# The engine is what actually manages the connection to the database
# 
# Parameters explained:
# - DATABASE_URL: Connection string (tells it which database to use)
# - connect_args: Additional settings for the driver
#   * check_same_thread=False: SQLite specific - allows multiple threads to access DB
#   * This is only used for SQLite, not PostgreSQL
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# =============================================================================
# SESSION FACTORY
# =============================================================================
# SessionLocal is a factory that creates new database sessions
# Each request gets its own session to avoid conflicts
# 
# Parameters:
# - autocommit=False: Don't auto-save changes (we explicitly call commit)
# - autoflush=False: Don't auto-flush pending changes (we control when changes are sent to DB)
# - bind=engine: Connect this session factory to our database engine
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# =============================================================================
# BASE CLASS FOR ALL MODELS
# =============================================================================
# This is the parent class that all database models inherit from
# It's used by SQLAlchemy to know how to create tables
# (See backend/models.py for examples of models using this Base)
Base = declarative_base()

# =============================================================================
# GET DATABASE FUNCTION
# =============================================================================
# This function is used by FastAPI endpoints to get a database session
# 
# WHY A GENERATOR FUNCTION?
# - The 'yield' keyword makes this a generator function
# - yield db: Provides the database session to the endpoint
# - finally db.close(): Ensures the connection is closed after the endpoint finishes
# - This is called "dependency injection" in FastAPI
# 
# USAGE IN ENDPOINTS:
# def some_endpoint(db: Session = Depends(get_db)):
#     # db is automatically provided by FastAPI
#     user = db.query(User).filter(...).first()
def get_db():
    """
    Provides a database session to FastAPI endpoints.
    Automatically closes the session when done.
    """
    db = SessionLocal()  # Create a new session
    try:
        yield db  # Give it to the endpoint
    finally:
        db.close()  # Always close it when done

# =============================================================================
# INITIALIZE DATABASE
# =============================================================================
# This function runs when the app starts up
# It creates all tables and adds initial data if needed
def init_db():
    """
    Initialize the database by:
    1. Creating all tables (based on models defined in backend/models.py)
    2. Adding initial data (universities and product categories)
    """
    
    # Import models - these define what tables to create
    from backend.models import User, University, Category, Product, ProductImage, SavedItem
    
    # Create all tables in the database
    # This checks the Base class and all models that inherit from it
    # and creates corresponding tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    # Create a new database session for seeding data
    db = SessionLocal()
    try:
        # ===== SEED: Add Universities if they don't exist =====
        # Check if any universities already exist
        if db.query(University).count() == 0:
            # If no universities, create Baze University
            baze = University(
                id=1,
                name="Baze University",
                domain="bazeuniversity.edu.ng"  # Users must use this domain to register
            )
            db.add(baze)  # Add to session (not in database yet)
            db.commit()  # Save to database
        
        # ===== SEED: Add Product Categories if they don't exist =====
        # Check if any categories already exist
        if db.query(Category).count() == 0:
            # If no categories, create default ones
            categories = [
                Category(name="Textbooks"),      # For school books
                Category(name="Electronics"),    # For laptops, phones, etc.
                Category(name="Clothing"),       # For clothes
                Category(name="Furniture"),      # For desks, chairs, etc.
                Category(name="Other")           # For miscellaneous items
            ]
            db.add_all(categories)  # Add all categories to session
            db.commit()  # Save to database
        
        # ===== UPDATE: Set all existing products location to "Baze University" =====
        # For existing products that may have different locations, update them
        # Since only Baze University students can sell, all products are at Baze
        existing_products = db.query(Product).all()
        for product in existing_products:
            if not product.location or product.location != "Baze University":
                product.location = "Baze University"
        if existing_products:
            db.commit()
    finally:
        # Always close the session when done
        db.close()
