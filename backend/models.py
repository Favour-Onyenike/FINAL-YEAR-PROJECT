"""
DATABASE MODELS MODULE
======================
This file defines all the database tables (represented as Python classes).
Each class is a table, and each class attribute is a column in that table.

WHAT HAPPENS HERE:
- Defines the structure of every table in the database
- Defines relationships between tables (e.g., a User has many Products)
- Uses SQLAlchemy ORM which converts these classes to SQL tables
"""

from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, Enum, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database import Base
import enum

# =============================================================================
# ENUM DEFINITIONS (Fixed value lists)
# =============================================================================
# Enums are lists of allowed values. They prevent invalid data in the database.

class ProductStatus(str, enum.Enum):
    """
    Possible status values for a product.
    
    STATUS MEANINGS:
    - available: Product is for sale
    - sold: Product was sold
    - deleted: Product was deleted (soft delete - not really removed)
    """
    available = "available"
    sold = "sold"
    deleted = "deleted"

class ProductCondition(str, enum.Enum):
    """
    Possible condition values for a product (how used it is).
    
    CONDITION MEANINGS:
    - New: Never used, still in packaging
    - Like New: Used but looks new
    - Good: Used but in good shape
    - Fair: Used and shows wear
    """
    new = "New"
    like_new = "Like New"
    good = "Good"
    fair = "Fair"

# =============================================================================
# UNIVERSITY TABLE
# =============================================================================
class University(Base):
    """
    Represents a university in the system.
    Users register with universities to enforce email domain restrictions.
    
    COLUMNS:
    - id: Primary key (unique identifier)
    - name: University name (e.g., "Baze University")
    - domain: Email domain required to join (e.g., "@bazeuniversity.edu.ng")
    
    RELATIONSHIPS:
    - users: One university has many users (users who study there)
    """
    __tablename__ = "universities"
    
    # Primary key - unique identifier for each university
    id = Column(Integer, primary_key=True, index=True)
    
    # University name - required, max 255 characters
    name = Column(String(255), nullable=False)
    
    # Email domain - unique (no two universities can have same domain)
    # Users MUST have an email ending with this domain to join
    domain = Column(String(255), nullable=False, unique=True)
    
    # Relationship: One university has many users
    # back_populates="university" creates the reverse relationship (User.university)
    users = relationship("User", back_populates="university")

# =============================================================================
# USER TABLE (Students/Staff accounts)
# =============================================================================
class User(Base):
    """
    Represents a user account (student, staff member, etc.).
    Users can create products, buy products, and save favorites.
    
    COLUMNS:
    - id: Primary key
    - full_name: User's real name
    - username: Unique username for login
    - email: Unique email (must match university domain)
    - password_hash: Encrypted password (never stored in plain text)
    - university_id: Foreign key to universities table
    - bio: Optional user biography
    - profile_image: URL to profile picture
    - phone: Optional phone number
    - created_at: When account was created
    
    RELATIONSHIPS:
    - university: Which university they belong to
    - products: All products they've created
    - saved_items: All products they've saved/bookmarked
    """
    __tablename__ = "users"
    
    # Unique ID for each user
    id = Column(Integer, primary_key=True, index=True)
    
    # User's full name (required)
    full_name = Column(String(255), nullable=False)
    
    # Username must be unique (can't have two users with same username)
    # index=True makes it faster to look up users by username
    username = Column(String(100), unique=True, nullable=False, index=True)
    
    # Email must be unique (can't have two accounts with same email)
    # index=True makes it faster to look up users by email
    email = Column(String(255), unique=True, nullable=False, index=True)
    
    # Password stored as hash (encrypted) - never store plain text!
    password_hash = Column(String(255), nullable=False)
    
    # Foreign key: Points to universities.id
    # This user must belong to a university
    university_id = Column(Integer, ForeignKey("universities.id"), nullable=False)
    
    # Optional biography text (can be NULL)
    bio = Column(Text, nullable=True)
    
    # Optional profile picture URL (can be NULL)
    profile_image = Column(String(500), nullable=True)
    profile_image_data = Column(Text, nullable=True)  # Base64 encoded image data
    
    # Optional phone number (can be NULL)
    phone = Column(String(20), nullable=True)
    
    # Automatic timestamp: Set to current time when user is created
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship: This user belongs to one university
    university = relationship("University", back_populates="users")
    
    # Relationship: This user has created many products
    products = relationship("Product", back_populates="seller")
    
    # Relationship: This user has saved many products
    saved_items = relationship("SavedItem", back_populates="user")
    
    # Relationship: This user has written many comments
    comments = relationship("Comment", back_populates="author")

# =============================================================================
# CATEGORY TABLE (Product categories)
# =============================================================================
class Category(Base):
    """
    Represents a product category (e.g., "Electronics", "Textbooks").
    Products are organized into categories for easier browsing.
    
    COLUMNS:
    - id: Primary key
    - name: Category name (unique)
    
    RELATIONSHIPS:
    - products: All products in this category
    """
    __tablename__ = "categories"
    
    # Unique ID for each category
    id = Column(Integer, primary_key=True, index=True)
    
    # Category name must be unique (no duplicate categories)
    # Can't have two "Electronics" categories
    name = Column(String(100), nullable=False, unique=True)
    
    # Relationship: This category has many products
    products = relationship("Product", back_populates="category")

# =============================================================================
# PRODUCT TABLE (Listings for sale)
# =============================================================================
class Product(Base):
    """
    Represents a product listing (something for sale).
    Contains all info about the item being sold.
    
    COLUMNS:
    - id: Primary key
    - name: Product name (searchable)
    - description: Full product description
    - price: Selling price
    - category_id: What category it's in
    - seller_id: Who's selling it
    - location: Where it's located
    - condition: How used/new it is
    - size: Optional size (for clothing)
    - color: Optional color
    - status: available/sold/deleted
    - created_at: When listed
    - updated_at: When last modified
    
    RELATIONSHIPS:
    - category: Which category this product is in
    - seller: Which user is selling it
    - images: All photos of the product
    - saved_by: Users who saved/bookmarked it
    """
    __tablename__ = "products"
    
    # Unique ID for each product
    id = Column(Integer, primary_key=True, index=True)
    
    # Product name (what you're selling)
    # index=True makes it faster to search by name
    name = Column(String(255), nullable=False, index=True)
    
    # Full product description (detailed info)
    description = Column(Text, nullable=False)
    
    # Price in dollars
    price = Column(Float, nullable=False)
    
    # Foreign key: Which category is this in?
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    
    # Foreign key: Who is selling this?
    seller_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Where the product is located (optional)
    location = Column(String(255), nullable=True)
    
    # Condition of the product (New, Like New, Good, Fair)
    condition = Column(String(50), nullable=True)
    
    # Size (for clothing) - optional
    size = Column(String(50), nullable=True)
    
    # Color - optional
    color = Column(String(50), nullable=True)
    
    # Current status of the product
    # Default is "available" (for sale)
    status = Column(String(50), default="available")
    
    # When product was first listed
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # When product was last updated
    # Automatically updates to current time when product is modified
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship: This product belongs to one category
    category = relationship("Category", back_populates="products")
    
    # Relationship: This product has one seller (user)
    seller = relationship("User", back_populates="products")
    
    # Relationship: This product has many images
    # cascade="all, delete-orphan" means if product is deleted, images are too
    images = relationship("ProductImage", back_populates="product", cascade="all, delete-orphan")
    
    # Relationship: This product is saved by many users
    saved_by = relationship("SavedItem", back_populates="product")
    
    # Relationship: This product has many comments
    comments = relationship("Comment", back_populates="product", cascade="all, delete-orphan")

# =============================================================================
# PRODUCT IMAGE TABLE (Photos of products)
# =============================================================================
class ProductImage(Base):
    """
    Represents a photo of a product.
    Products can have multiple images (up to 5).
    
    COLUMNS:
    - id: Primary key
    - product_id: Which product this image belongs to
    - image_url: URL where the image is stored
    - is_primary: Whether this is the main/cover image
    - created_at: When image was uploaded
    
    RELATIONSHIPS:
    - product: Which product owns this image
    """
    __tablename__ = "product_images"
    
    # Unique ID for each image
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign key: Which product does this image belong to?
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    
    # URL where image is stored
    # Can be a local path like "/uploads/products/image123.jpg"
    # Or external URL like "https://example.com/image.jpg"
    image_url = Column(String(500), nullable=False)
    
    # Is this the main/primary image? (0 = no, 1 = yes)
    # The first image is usually the primary one shown in product list
    is_primary = Column(Integer, default=0)
    
    # When image was uploaded
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship: This image belongs to one product
    product = relationship("Product", back_populates="images")
    
    # Store the actual image data (Base64 encoded string)
    image_data = Column(Text, nullable=True)

# =============================================================================
# SAVED ITEMS TABLE (Bookmarks/Wishlist)
# =============================================================================
class SavedItem(Base):
    """
    Represents a product that a user has saved/bookmarked.
    Users can save products they want to remember/buy later.
    
    COLUMNS:
    - id: Primary key
    - user_id: Which user saved it
    - product_id: Which product was saved
    - created_at: When it was saved
    
    RELATIONSHIPS:
    - user: Which user saved it
    - product: Which product was saved
    """
    __tablename__ = "saved_items"
    
    # Unique ID for each saved item
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign key: Which user saved this product?
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Foreign key: Which product was saved?
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    
    # When the item was saved
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship: This saved item belongs to one user
    user = relationship("User", back_populates="saved_items")
    
    # Relationship: This saved item points to one product
    product = relationship("Product", back_populates="saved_by")

# =============================================================================
# MESSAGE TABLE (Real-time Chat)
# =============================================================================
class Message(Base):
    """
    Represents a message between two users in a chat conversation.
    Stores message content, sender, receiver, and timestamps.
    
    COLUMNS:
    - id: Primary key
    - sender_id: User who sent the message
    - receiver_id: User who received the message
    - content: Message text
    - created_at: When the message was sent
    - is_read: Whether the receiver has read it
    
    RELATIONSHIPS:
    - sender: The user who sent the message
    - receiver: The user who received the message
    """
    __tablename__ = "messages"
    __table_args__ = (
        Index('idx_messages_sender_receiver', 'sender_id', 'receiver_id'),
        Index('idx_messages_receiver_id', 'receiver_id'),
        Index('idx_messages_is_read', 'is_read'),
    )
    
    # Unique ID for each message
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign key: Who sent this message?
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Foreign key: Who received this message?
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Message content
    content = Column(Text, nullable=False)
    
    # Whether the receiver has read it
    is_read = Column(Integer, default=0)  # 0 = unread, 1 = read
    
    # Timestamp of when message was created
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationship: Sender user
    sender = relationship("User", foreign_keys=[sender_id])
    
    # Relationship: Receiver user
    receiver = relationship("User", foreign_keys=[receiver_id])

# =============================================================================
# COMMENT TABLE (Product Comments/Questions)
# =============================================================================
class Comment(Base):
    """
    Represents a comment on a product listing.
    Users can ask questions or leave comments on product listings.
    
    COLUMNS:
    - id: Primary key
    - product_id: Which product is being commented on
    - author_id: Who wrote the comment
    - content: The comment text
    - created_at: When the comment was posted
    
    RELATIONSHIPS:
    - product: The product this comment is on
    - author: The user who wrote the comment
    """
    __tablename__ = "comments"
    
    # Unique ID for each comment
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign key: Which product is this comment on?
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    
    # Foreign key: Who wrote this comment?
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # The comment text content
    content = Column(Text, nullable=False)
    
    # When the comment was created
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationship: This comment belongs to one product
    product = relationship("Product", back_populates="comments")
    
    # Relationship: This comment was written by one user
    author = relationship("User", back_populates="comments")
