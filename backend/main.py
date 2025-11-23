"""
================================================================================
UNIMARKET API - BACKEND MAIN SERVER
================================================================================

PURPOSE:
This is the main backend API server for UniMarket, a peer-to-peer campus
marketplace for Baze University students. It handles all HTTP requests from
the frontend and manages real-time messaging via Socket.IO.

WHAT THIS FILE DOES:
1. Initializes FastAPI web server (port 8000)
2. Sets up Socket.IO for real-time WebSocket communication
3. Handles user authentication (register, login, JWT tokens)
4. Manages product listings (create, edit, delete, view)
5. Implements messaging system (send, fetch, mark as read)
6. Handles image uploads and serving
7. Manages user profiles and saved items (wishlist)
8. Provides product categories and filtering

KEY FEATURES:
✓ Real-time Chat: Socket.IO handles instant message delivery
✓ Message Persistence: REST API saves messages to database
✓ User Authentication: JWT tokens with 7-day expiry
✓ Image Management: Upload, compress, and serve images
✓ Search & Filter: Find products by category, price, condition
✓ Notification System: Unread message tracking with badges

HOW IT WORKS:
1. Frontend (port 5000) sends HTTP requests to Backend (port 8000)
2. Backend validates request with authentication
3. Executes database queries
4. Returns JSON response
5. For real-time features: Uses Socket.IO WebSocket connection

FILE STRUCTURE:
- Socket.IO initialization and event handlers
- CORS middleware setup (allows frontend cross-origin requests)
- Authentication endpoints (register, login, profile)
- Product endpoints (list, create, edit, delete)
- Message endpoints (send, fetch, mark as read)
- Socket.IO real-time event handlers
- Image upload endpoints
- Database initialization

DATABASE INTEGRATION:
- Uses SQLAlchemy ORM
- SQLite for development, PostgreSQL for production
- Automatic database initialization on startup
- User, Product, Message, Category, SavedItem tables

WHEN YOU START THE SERVER:
1. Loads .env file for environment variables
2. Initializes database (creates tables if needed)
3. Sets up CORS to allow frontend requests
4. Mounts static file directory for image uploads
5. Starts listening on port 8000

COMMON ENDPOINTS:
- POST /api/register - Create new account
- POST /api/login - User login
- GET /api/products - List all products
- POST /api/products - Create product
- POST /api/messages - Send message
- GET /api/messages/{user_id} - Get conversation history
- PUT /api/messages/{user_id}/mark-read - Mark messages as read
- POST /api/images - Upload image

For detailed endpoint documentation, see:
- /docs (Swagger UI interactive docs)
- /redoc (ReDoc documentation)

================================================================================
"""

from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Query
from fastapi.responses import FileResponse  # Serve HTML files
from fastapi.middleware.cors import CORSMiddleware  # Allow cross-origin requests
from fastapi.staticfiles import StaticFiles  # Serve static files (images)
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func, desc  # SQL query helpers
from typing import List, Optional
import os
import shutil
import uuid  # Generate unique filenames
from datetime import datetime
import socketio  # Real-time websocket communication

# Import database and authentication functions
from backend.database import get_db, init_db
from backend.models import User, University, Product, ProductImage, SavedItem, Category, Message, Comment
from backend.schemas import (
    UserRegister, UserLogin, UserResponse, LoginResponse, UserUpdate,
    ProductCreate, ProductUpdate, ProductResponse, ProductListResponse,
    SavedItemToggle, SavedItemResponse, UploadResponse, MessageCreate, MessageResponse,
    SellerInfo, CategoryResponse, ProductImageResponse, CommentCreate, CommentResponse
)
from backend.auth import (
    get_password_hash, verify_password, create_access_token, get_current_user
)

# =============================================================================
# FASTAPI APP INITIALIZATION
# =============================================================================
# Create the FastAPI application instance
# This is the main app object that handles all requests
app = FastAPI(
    title="UniMarket API",
    version="1.0.0",
    # Swagger UI will be available at /docs
    # ReDoc will be available at /redoc
)

# Initialize Socket.IO for real-time messaging
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins=['*'],  # Allow all origins for development
    logger=False,
    engineio_logger=False
)

# Create ASGI app that combines FastAPI and Socket.IO
from socketio import ASGIApp
app_with_sio = ASGIApp(sio, app)

# =============================================================================
# CORS MIDDLEWARE
# =============================================================================
# CORS = Cross-Origin Resource Sharing
# Allows frontend (different domain/port) to call backend API
# Without this, browsers block requests for security
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (fine for development)
    allow_credentials=True,  # Allow cookies/credentials
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers
)

# =============================================================================
# STATIC FILE SETUP
# =============================================================================
# Create uploads directory if it doesn't exist
os.makedirs("backend/uploads/products", exist_ok=True)

# Mount /uploads to serve uploaded images
# When frontend requests: /uploads/products/image.jpg
# It serves from: backend/uploads/products/image.jpg
app.mount("/uploads", StaticFiles(directory="backend/uploads"), name="uploads")

# Mount static directories (CSS, JS, Images)
app.mount("/css", StaticFiles(directory="css"), name="css")
app.mount("/js", StaticFiles(directory="js"), name="js")
app.mount("/img", StaticFiles(directory="img"), name="img")

# =============================================================================
# STARTUP EVENT
# =============================================================================
# This function runs once when the server starts
@app.on_event("startup")
def startup_event():
    """Initialize the database on server startup"""
    init_db()  # Create tables, add default data

# =============================================================================
# HEALTH CHECK ENDPOINT
# =============================================================================
@app.get("/api/health")
def health_check():
    """
    Simple health check endpoint.
    
    Returns: {"status": "healthy"}
    Used by: Frontend or monitoring systems to check if API is running
    """
    return {"status": "healthy"}

# =============================================================================
# AUTHENTICATION ENDPOINTS
# =============================================================================

@app.post("/api/auth/register", status_code=status.HTTP_201_CREATED)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """
    Register a new user account.
    
    REQUEST DATA:
    {
        "fullName": "John Doe",
        "username": "johndoe",
        "email": "john@bazeuniversity.edu.ng",
        "password": "password123",
        "universityId": 1
    }
    
    RETURNS: {"message": "User registered successfully."}
    
    VALIDATION:
    1. Username must not already exist
    2. Email must not already exist
    3. University must exist in database
    4. Email must match university domain (e.g., @bazeuniversity.edu.ng)
    5. Password length validated by Pydantic (6-72 chars)
    
    WHAT IT DOES:
    1. Check if username/email already registered
    2. Get university and validate it exists
    3. Validate email domain matches university
    4. Hash password with bcrypt
    5. Create new User in database
    6. Return success message
    """
    # Check if username or email already exists
    existing_user = db.query(User).filter(
        or_(User.username == user_data.username, User.email == user_data.email)
    ).first()
    
    if existing_user:
        if existing_user.username == user_data.username:
            raise HTTPException(status_code=409, detail="Username already exists")
        if existing_user.email == user_data.email:
            raise HTTPException(status_code=409, detail="Email already exists")
    
    # Get university from database and validate it exists
    university = db.query(University).filter(University.id == user_data.universityId).first()
    if not university:
        raise HTTPException(status_code=400, detail="Invalid university")
    
    # Validate email domain matches university
    # For Baze University, email must end with @bazeuniversity.edu.ng
    if university.id == 1:
        if not user_data.email.endswith(f"@{university.domain}"):
            raise HTTPException(
                status_code=400,
                detail=f"Email must end with @{university.domain} for {university.name}"
            )
    
    # Hash the password using bcrypt (one-way encryption)
    hashed_password = get_password_hash(user_data.password)
    
    # Create new User object with hashed password
    new_user = User(
        full_name=user_data.fullName,
        username=user_data.username,
        email=user_data.email,
        password_hash=hashed_password,  # Store hash, not plain password!
        university_id=user_data.universityId
    )
    
    # Add to database and save
    db.add(new_user)
    db.commit()
    
    return {"message": "User registered successfully."}

@app.post("/api/auth/login", response_model=LoginResponse)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Login and get JWT token.
    
    REQUEST DATA:
    {
        "email": "john@bazeuniversity.edu.ng",
        "password": "password123"
    }
    
    RETURNS:
    {
        "token": "eyJhbGciOiJIUzI1NiIs...",  // JWT token
        "user": {  // Current user info
            "id": 1,
            "fullName": "John Doe",
            ...
        }
    }
    
    HOW IT WORKS:
    1. Find user by email in database
    2. Verify password with bcrypt
    3. If valid: Create JWT token (expires in 7 days)
    4. Return token + user info to frontend
    5. Frontend stores token in localStorage
    6. Frontend includes token in Authorization header for future requests
    """
    # Find user by email
    user = db.query(User).filter(User.email == login_data.email).first()
    
    # Check if user exists
    if not user:
        raise HTTPException(
            status_code=404,
            detail="Account does not exist"
        )
    
    # Check password
    if not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=401,
            detail="Incorrect password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create JWT token
    # Token contains userId and expires in 7 days
    access_token = create_access_token(data={"userId": user.id})
    
    # Return token + user info
    return {
        "token": access_token,
        "user": {
            "id": user.id,
            "fullName": user.full_name,
            "email": user.email,
            "username": user.username,
            "bio": user.bio,
            "profileImage": user.profile_image,
            "phone": user.phone
        }
    }

@app.get("/api/auth/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """
    Get current logged-in user profile.
    
    REQUIRES: Valid JWT token in Authorization header
    Format: Authorization: Bearer <token>
    
    RETURNS: Current user's profile data
    
    HOW IT WORKS:
    1. FastAPI calls get_current_user automatically
    2. get_current_user verifies the token
    3. Returns the User object
    4. This endpoint just formats and returns user data
    """
    return {
        "id": current_user.id,
        "fullName": current_user.full_name,
        "email": current_user.email,
        "username": current_user.username,
        "bio": current_user.bio,
        "profileImage": current_user.profile_image,
        "phone": current_user.phone
    }

@app.get("/api/users", response_model=List[UserResponse])
def get_all_users(db: Session = Depends(get_db)):
    """
    Get all users (for messaging conversations).
    
    RETURNS: List of all users (excluding password)
    """
    users = db.query(User).all()
    return [
        {
            "id": u.id,
            "fullName": u.full_name,
            "email": u.email,
            "username": u.username,
            "bio": u.bio,
            "profileImage": u.profile_image,
            "phone": u.phone
        }
        for u in users
    ]

@app.get("/api/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """
    Get user profile by ID.
    
    PARAMETERS:
    - user_id: The ID of the user to retrieve
    
    RETURNS: User's profile data
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "id": user.id,
        "fullName": user.full_name,
        "email": user.email,
        "username": user.username,
        "bio": user.bio,
        "profileImage": user.profile_image,
        "phone": user.phone
    }

@app.put("/api/users/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update user profile (own profile only).
    
    REQUIRES: Valid JWT token in Authorization header
    Format: Authorization: Bearer <token>
    
    PARAMETERS:
    - user_id: ID of the user to update (must match current user)
    
    REQUEST BODY:
    {
        "fullName": "New Full Name" (optional),
        "bio": "New biography" (optional),
        "avatarUrl": "/uploads/products/image.jpg" (optional)
    }
    
    RETURNS: Updated user profile
    
    SECURITY:
    - User can only update their own profile
    - Cannot update email or username
    """
    # Check if user is trying to update their own profile
    if current_user.id != user_id:
        raise HTTPException(
            status_code=403,
            detail="You can only update your own profile"
        )
    
    # Get the user to update
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update fields if provided
    if user_data.fullName is not None:
        user.full_name = user_data.fullName
    
    if user_data.bio is not None:
        user.bio = user_data.bio
    
    if user_data.avatarUrl is not None:
        user.profile_image = user_data.avatarUrl
    
    # Save changes to database
    db.commit()
    db.refresh(user)
    
    # Return updated user
    return {
        "id": user.id,
        "fullName": user.full_name,
        "email": user.email,
        "username": user.username,
        "bio": user.bio,
        "profileImage": user.profile_image,
        "phone": user.phone
    }

# =============================================================================
# PRODUCT SERIALIZATION HELPER
# =============================================================================
def serialize_product(product: Product) -> dict:
    """
    Convert a Product object from database to JSON-ready dictionary.
    
    This function takes all product data (including related images, seller, category)
    and formats it for the API response.
    
    WHY THIS FUNCTION?
    - Products have relationships (images, seller, category)
    - Need to convert these relationships to JSON
    - Avoid repeating this code in multiple endpoints
    """
    return {
        "id": product.id,
        "name": product.name,
        "description": product.description,
        "price": product.price,
        "location": product.location,
        "condition": product.condition,
        "size": product.size,
        "color": product.color,
        "status": product.status,
        "createdAt": product.created_at,
        "updatedAt": product.updated_at,
        # Convert images relationship to list of dicts
        "images": [
            {
                "id": img.id,
                "imageUrl": img.image_url,
                "isPrimary": img.is_primary
            } for img in product.images
        ],
        # Convert seller relationship to dict
        "seller": {
            "id": product.seller.id,
            "fullName": product.seller.full_name,
            "username": product.seller.username,
            "profileImage": product.seller.profile_image
        },
        # Convert category relationship to dict
        "category": {
            "id": product.category.id,
            "name": product.category.name
        }
    }

# =============================================================================
# PRODUCT ENDPOINTS
# =============================================================================

@app.get("/api/products", response_model=ProductListResponse)
def get_products(
    q: Optional[str] = Query(None),  # Search query
    category: Optional[str] = Query(None),  # Filter by category name
    minPrice: Optional[float] = Query(None),  # Minimum price
    maxPrice: Optional[float] = Query(None),  # Maximum price
    condition: Optional[str] = Query(None),  # Filter by condition (New, Like New, etc.)
    sortBy: Optional[str] = Query("newest"),  # Sort by: newest, price-asc, price-desc
    userId: Optional[int] = Query(None),  # Filter by seller ID (show only user's listings)
    page: int = Query(1, ge=1),  # Page number (starts at 1)
    limit: int = Query(20, ge=1, le=100),  # Results per page
    db: Session = Depends(get_db)
):
    """
    List all available products with filtering, sorting, and pagination.
    
    QUERY PARAMETERS (all optional):
    ?q=textbook&category=Textbooks&minPrice=10&maxPrice=100&condition=Like New&sortBy=price-asc&page=1&limit=20&userId=6
    
    SPECIAL PARAMETERS:
    ?userId=6 - Show only products from user ID 6 (for "My Listings")
    
    RETURNS:
    {
        "page": 1,
        "limit": 20,
        "totalPages": 5,
        "totalResults": 100,
        "products": [...]  // Array of product objects
    }
    
    HOW IT WORKS:
    1. Start with query: Get all products (or user's products if userId provided)
    2. Apply filters: Search text, category, price range, condition
    3. Apply sorting: newest, price ascending, or price descending
    4. Apply pagination: Skip to correct page, limit results
    5. Count total results and calculate total pages
    6. Return paginated results
    """
    # Start with all available products (not deleted/sold)
    # OR if userId is provided, show only that user's products (regardless of status)
    if userId:
        query = db.query(Product).filter(Product.seller_id == userId)
    else:
        query = db.query(Product).filter(Product.status == "available")
    
    # SEARCH FILTER: Search in name or description
    if q:
        search_term = f"%{q}%"  # Add wildcards for LIKE query
        query = query.filter(
            or_(
                Product.name.like(search_term),  # Search in name
                Product.description.like(search_term)  # Search in description
            )
        )
    
    # CATEGORY FILTER: Filter by category name
    if category:
        cat = db.query(Category).filter(Category.name == category).first()
        if cat:
            query = query.filter(Product.category_id == cat.id)
    
    # PRICE FILTER: Minimum price
    if minPrice is not None:
        query = query.filter(Product.price >= minPrice)
    
    # PRICE FILTER: Maximum price
    if maxPrice is not None:
        query = query.filter(Product.price <= maxPrice)
    
    # CONDITION FILTER: Product condition
    if condition:
        query = query.filter(Product.condition == condition)
    
    # SORTING
    if sortBy == "price-asc":
        query = query.order_by(Product.price.asc())  # Cheapest first
    elif sortBy == "price-desc":
        query = query.order_by(Product.price.desc())  # Most expensive first
    else:
        query = query.order_by(Product.created_at.desc())  # Newest first (default)
    
    # Count total results (before pagination)
    total = query.count()
    total_pages = (total + limit - 1) // limit  # Ceiling division
    
    # PAGINATION: Skip to correct page and limit results
    # Page 1: offset=0 (skip 0)
    # Page 2: offset=20 (skip 20)
    # Page 3: offset=40 (skip 40)
    products = query.offset((page - 1) * limit).limit(limit).all()
    
    # Return paginated results
    return {
        "page": page,
        "limit": limit,
        "totalPages": total_pages,
        "totalResults": total,
        "products": [serialize_product(p) for p in products]
    }

@app.get("/api/products/top-selling/featured")
def get_top_selling_products(db: Session = Depends(get_db)):
    """
    Get the 4 most saved products (Top Selling section)
    
    LOGIC:
    1. Join products with saved items
    2. Count how many times each product was saved
    3. Sort by save count (most saved first)
    4. Return top 4 products
    
    URL: /api/products/top-selling/featured
    
    RETURNS: Array of top 4 products with save counts
    [
        {
            "id": 1,
            "name": "Product Name",
            "price": 1500,
            "images": [...],
            "seller": {...},
            "saveCount": 12  // How many users saved this
        },
        ...
    ]
    
    WHY THIS WORKS:
    - Products with most saves = most popular/desired
    - Reflects user interest better than artificial rankings
    - Updates automatically as users save/unsave items
    """
    # Subquery: Count saves per product
    from sqlalchemy import func
    
    # Query: Get products with save counts
    # LEFT JOIN preserves products with 0 saves
    products_with_saves = db.query(
        Product,
        func.count(SavedItem.id).label('save_count')
    ).outerjoin(
        SavedItem,
        Product.id == SavedItem.product_id
    ).filter(
        Product.status == "available"  # Only show available products
    ).group_by(
        Product.id
    ).order_by(
        func.count(SavedItem.id).desc()  # Most saved first
    ).limit(4).all()
    
    # Format response with save counts
    result = []
    for product, save_count in products_with_saves:
        product_dict = serialize_product(product)
        product_dict["saveCount"] = save_count or 0
        result.append(product_dict)
    
    return result

@app.get("/api/products/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    """
    Get details for a single product.
    
    URL: /api/products/5
    RETURNS: Complete product object with images, seller, category
    
    ERROR: 404 if product doesn't exist
    """
    # Find product by ID
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return serialize_product(product)

@app.post("/api/products", status_code=status.HTTP_201_CREATED, response_model=ProductResponse)
def create_product(
    product_data: ProductCreate,
    current_user: User = Depends(get_current_user),  # Require login
    db: Session = Depends(get_db)
):
    """
    Create a new product listing.
    
    REQUIRES: Valid JWT token (must be logged in)
    
    REQUEST DATA:
    {
        "name": "Textbook",
        "description": "Used calculus textbook...",
        "price": 45.99,
        "categoryId": 1,
        "location": "Library Building",
        "condition": "Like New",
        "size": null,
        "color": null,
        "images": ["/uploads/products/image1.jpg", "/uploads/products/image2.jpg"]
    }
    
    RETURNS: Complete product object
    
    VALIDATION:
    1. Category must exist
    2. Must provide 1-5 images
    3. Images must be uploaded first (via /api/upload endpoint)
    
    HOW IT WORKS:
    1. Get current user from token
    2. Validate category exists
    3. Validate 1-5 images provided
    4. Create Product in database (seller_id = current_user.id)
    5. Add ProductImage records for each image
    6. First image is marked as primary
    7. Return created product
    """
    # Validate category exists
    category = db.query(Category).filter(Category.id == product_data.categoryId).first()
    if not category:
        raise HTTPException(status_code=400, detail="Invalid category")
    
    # Validate 1-5 images provided
    if len(product_data.images) < 1 or len(product_data.images) > 5:
        raise HTTPException(status_code=400, detail="Product must have between 1 and 5 images")
    
    # Create new Product object
    new_product = Product(
        name=product_data.name,
        description=product_data.description,
        price=product_data.price,
        category_id=product_data.categoryId,
        seller_id=current_user.id,  # Set seller to current user
        location="Baze University",  # All products are at Baze University (only sellers from Baze)
        condition=product_data.condition,
        size=product_data.size,
        color=product_data.color,
        status="available"  # New products are available for sale
    )
    
    # Save product to database
    db.add(new_product)
    db.commit()
    db.refresh(new_product)  # Refresh to get the ID
    
    # Add images to the product
    for idx, image_url in enumerate(product_data.images):
        product_image = ProductImage(
            product_id=new_product.id,
            image_url=image_url,
            is_primary=1 if idx == 0 else 0  # First image is primary
        )
        db.add(product_image)
    
    # Save images to database
    db.commit()
    db.refresh(new_product)
    
    return serialize_product(new_product)

@app.put("/api/products/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product_data: ProductUpdate,
    current_user: User = Depends(get_current_user),  # Require login
    db: Session = Depends(get_db)
):
    """
    Update a product listing.
    
    REQUIRES: Valid JWT token AND must be the product owner
    
    AUTHORIZATION: Only the seller can update their own products
    
    HOW IT WORKS:
    1. Find product by ID
    2. Check current user is the seller
    3. Update provided fields (others unchanged)
    4. If images provided: delete old ones, add new ones
    5. Update the updated_at timestamp
    6. Return updated product
    """
    # Find product
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Check authorization: user must be the seller
    if product.seller_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only edit your own products")
    
    # Get only the fields that were provided (not None)
    update_data = product_data.model_dump(exclude_unset=True)
    
    # Handle images if provided
    if "images" in update_data:
        images = update_data.pop("images")  # Remove from update_data
        
        # Validate image count
        if len(images) < 1 or len(images) > 5:
            raise HTTPException(status_code=400, detail="Product must have between 1 and 5 images")
        
        # Delete old images
        db.query(ProductImage).filter(ProductImage.product_id == product_id).delete()
        
        # Add new images
        for idx, image_url in enumerate(images):
            product_image = ProductImage(
                product_id=product_id,
                image_url=image_url,
                is_primary=1 if idx == 0 else 0
            )
            db.add(product_image)
    
    # Handle category if provided
    if "categoryId" in update_data:
        category = db.query(Category).filter(Category.id == update_data["categoryId"]).first()
        if not category:
            raise HTTPException(status_code=400, detail="Invalid category")
        product.category_id = update_data.pop("categoryId")
    
    # Update all other fields
    for key, value in update_data.items():
        setattr(product, key, value)
    
    # Update the updated_at timestamp
    product.updated_at = datetime.utcnow()
    
    # Save changes
    db.commit()
    db.refresh(product)
    
    return serialize_product(product)

@app.delete("/api/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int,
    current_user: User = Depends(get_current_user),  # Require login
    db: Session = Depends(get_db)
):
    """
    Delete a product listing (soft delete).
    
    REQUIRES: Valid JWT token AND must be the product owner
    
    SOFT DELETE: Product is marked as "deleted" (not permanently removed)
    This keeps history and allows potential recovery
    
    HOW IT WORKS:
    1. Find product by ID
    2. Check current user is the seller
    3. Set product.status = "deleted"
    4. Save to database
    5. Return 204 (No Content) - success with no response body
    
    RESULT: Product no longer appears in product listings
    """
    # Find product
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Check authorization
    if product.seller_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only delete your own products")
    
    # Soft delete: Mark as deleted instead of removing from database
    product.status = "deleted"
    db.commit()
    
    return None  # 204 response with no body

# =============================================================================
# SAVED ITEMS ENDPOINTS (Bookmarks/Wishlist)
# =============================================================================

@app.post("/api/saved-items", response_model=SavedItemResponse)
def toggle_saved_item(
    data: SavedItemToggle,
    current_user: User = Depends(get_current_user),  # Require login
    db: Session = Depends(get_db)
):
    """
    Toggle save/unsave a product (bookmark/wishlist).
    
    REQUIRES: Valid JWT token
    
    REQUEST DATA:
    {"productId": 5}
    
    RETURNS:
    {"isSaved": true}  // true if saved, false if unsaved
    
    HOW IT WORKS:
    1. Find if product exists
    2. Check if already saved by this user
    3. If saved: Delete SavedItem record (unsave)
    4. If not saved: Create SavedItem record (save)
    5. Return current state
    """
    # Validate product exists
    product = db.query(Product).filter(Product.id == data.productId).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Check if already saved
    saved_item = db.query(SavedItem).filter(
        and_(SavedItem.user_id == current_user.id, SavedItem.product_id == data.productId)
    ).first()
    
    if saved_item:
        # Already saved: Delete to unsave
        db.delete(saved_item)
        db.commit()
        return {"isSaved": False}
    else:
        # Not saved: Create new SavedItem
        new_saved_item = SavedItem(
            user_id=current_user.id,
            product_id=data.productId
        )
        db.add(new_saved_item)
        db.commit()
        return {"isSaved": True}

@app.get("/api/saved-items", response_model=List[ProductResponse])
def get_saved_items(
    current_user: User = Depends(get_current_user),  # Require login
    db: Session = Depends(get_db)
):
    """
    Get all products saved by current user.
    
    REQUIRES: Valid JWT token
    
    RETURNS: Array of product objects
    
    HOW IT WORKS:
    1. Query all SavedItem records for current user
    2. Extract product IDs from SavedItem records
    3. Query all Products with those IDs
    4. Return complete product objects
    """
    # Get all saved item records for this user
    saved_items = db.query(SavedItem).filter(SavedItem.user_id == current_user.id).all()
    
    # Extract product IDs
    product_ids = [item.product_id for item in saved_items]
    
    # Query products by IDs
    products = db.query(Product).filter(Product.id.in_(product_ids)).all()
    
    return [serialize_product(p) for p in products]

# =============================================================================
# IMAGE UPLOAD ENDPOINT
# =============================================================================

@app.post("/api/upload", response_model=UploadResponse)
async def upload_image(file: UploadFile = File(...)):
    """
    Upload a product image.
    
    MULTIPART FORM DATA:
    - file: Image file (JPG, PNG, etc.)
    
    RETURNS:
    {"imageUrl": "/uploads/products/uuid-here.jpg"}
    
    FILE VALIDATION:
    - Must be an image file (content-type starts with "image/")
    - Not validated: File size, dimensions, etc.
    
    HOW IT WORKS:
    1. Validate file is an image
    2. Generate unique filename (UUID + original extension)
    3. Save file to backend/uploads/products/
    4. Return URL to access the image
    5. Frontend uses returned URL when creating product
    
    FILE STORAGE:
    - Uploaded to: backend/uploads/products/{uuid}.{extension}
    - Accessible at: /uploads/products/{uuid}.{extension}
    - Not stored in database (only the URL is stored)
    """
    # Validate file is an image
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Generate unique filename to avoid conflicts
    # Use UUID (universally unique identifier) + original extension
    # Example: 3fa85f64-5717-4562-b3fc-2c963f66afa6.jpg
    file_extension = file.filename.split(".")[-1]
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = f"backend/uploads/products/{unique_filename}"
    
    # Save file to disk
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)  # Copy file contents
    
    # Return URL to access the uploaded image
    # Frontend will use this URL in the images array when creating product
    return {"imageUrl": f"/uploads/products/{unique_filename}"}

# =============================================================================
# CATEGORY ENDPOINT
# =============================================================================

@app.get("/api/categories")
def get_categories(db: Session = Depends(get_db)):
    """
    Get all product categories.
    
    RETURNS: Array of category objects
    [
        {"id": 1, "name": "Textbooks"},
        {"id": 2, "name": "Electronics"},
        {"id": 3, "name": "Clothing"},
        ...
    ]
    
    USED BY: Frontend to populate category dropdown filters
    """
    categories = db.query(Category).all()
    return [{"id": c.id, "name": c.name} for c in categories]

# =============================================================================
# REAL-TIME MESSAGING (Socket.IO)
# =============================================================================
# Socket.IO enables WebSocket communication for instant message delivery
# This works alongside REST API for message persistence
# 
# FLOW:
# 1. Frontend connects -> connect event fires
# 2. Frontend authenticates with user_id -> authenticate event fires
# 3. User A sends message -> Message saved via REST API + Socket.IO event emitted
# 4. If User B is online -> receive_message event fires immediately
# 5. If User B is offline -> message stays in database, fetched on next connect

# Dictionary to track which users are currently connected
# Format: {user_id: socket_id}
# Example: {1: "abc123xyz", 5: "def456uvw"}
# Used to know if a user is online and which WebSocket to send them messages to
connected_users = {}

@sio.event
async def connect(sid, environ):
    """
    Handle initial WebSocket connection from client
    
    This event fires when a user opens messages.html and establishes a WebSocket connection.
    The Socket.IO server automatically assigns a unique session ID (sid) to this connection.
    
    PARAMETERS:
    - sid: Socket.IO session ID (unique connection identifier)
    - environ: WSGI environment dict (connection metadata)
    
    WHY: Initial connection setup. Frontend will authenticate after this.
    """
    print(f"Client connected: {sid}")

@sio.event
async def disconnect(sid):
    """
    Handle WebSocket disconnection from client
    
    This event fires when a user closes the browser, loses connection, or navigates away.
    We clean up our tracking by removing them from connected_users dict.
    
    PARAMETERS:
    - sid: Socket.IO session ID being disconnected
    
    PURPOSE: When user goes offline, remove them from connected_users so we don't try
             to send them messages (they won't receive them anyway).
    """
    # Iterate through connected_users to find which user_id has this socket_id
    for user_id, socket_id in list(connected_users.items()):
        if socket_id == sid:
            # Found the user - remove them from connected list
            del connected_users[user_id]
    print(f"Client disconnected: {sid}")

@sio.event
async def authenticate(sid, data):
    """
    Map WebSocket connection to user ID
    
    After connecting, the frontend sends authenticate event with the user's ID.
    This allows us to know: "Socket abc123xyz belongs to User 5"
    
    PARAMETERS:
    - sid: The WebSocket connection ID (from connect event)
    - data: Object with userId {"userId": 5}
    
    WHAT HAPPENS:
    1. Frontend emits authenticate with user ID
    2. Backend stores: connected_users[5] = sid
    3. Now we know User 5 is online
    4. When someone sends User 5 a message, we can emit it to their socket
    
    EXAMPLE:
    User 5 opens browser:
    - connect event -> sid = "abc123xyz"
    - authenticate event -> connected_users[5] = "abc123xyz"
    - Now messages to User 5 are sent to socket "abc123xyz"
    """
    user_id = data.get('userId')  # Extract user_id from the event data
    if user_id:
        # Map this user to their WebSocket connection
        connected_users[user_id] = sid
        # Send confirmation back to client that authentication succeeded
        await sio.emit('authenticated', {'status': 'ok', 'userId': user_id}, to=sid)

@sio.event
async def send_message(sid, data):
    """
    Handle real-time message event from frontend (Socket.IO route)
    
    NOTE: This is only for REAL-TIME delivery when user is online.
    Actual message persistence is handled by send_message_api endpoint (REST API).
    
    PARAMETERS:
    - sid: Sender's socket ID
    - data: Message object with:
      {
        "senderId": 1,        // Who is sending
        "receiverId": 5,      // Who should receive
        "content": "Hi!",     // Message text
      }
    
    LOGIC:
    1. Check if receiver is in connected_users (online?)
    2. If YES: Send receive_message event to their socket immediately
    3. If NO: Do nothing - message is already saved to database via REST API
    
    WHY TWO METHODS?
    - Socket.IO: Instant delivery to online users (real-time)
    - REST API: Persistence for offline users (reliability)
    
    EXAMPLE FLOW:
    User 1 sends message to User 5:
    - send_message_api called first (saves to database)
    - Then send_message called (if User 5 online, emit event)
    - If User 5 offline: They fetch messages later from database
    """
    receiver_id = data.get('receiverId')  # Who to send to
    content = data.get('content')         # What message says
    sender_id = data.get('senderId')      # Who sent it
    
    # Check if receiver is currently connected (online)
    if receiver_id in connected_users:
        # Receiver is online! Get their socket ID
        receiver_sid = connected_users[receiver_id]
        # Send the message immediately via WebSocket
        await sio.emit('receive_message', {
            'senderId': sender_id,
            'content': content,
            'timestamp': datetime.utcnow().isoformat()
        }, to=receiver_sid)
    
    # Send confirmation back to sender that message was processed
    await sio.emit('message_sent', {'status': 'success'}, to=sid)

# =============================================================================
# MESSAGE REST API ENDPOINTS
# =============================================================================

@app.post("/api/messages", response_model=MessageResponse)
async def send_message_api(
    message_data: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    REST API endpoint to SEND AND PERSIST a message
    
    This is the PRIMARY way messages are saved to the database.
    Socket.IO handles real-time delivery, but this handles persistence.
    
    WORKFLOW:
    1. Frontend calls POST /api/messages with receiverId and content
    2. Backend verifies receiver exists
    3. Creates Message object and saves to database
    4. Commits transaction (message is now permanent)
    5. If receiver is online: Emits Socket.IO event for instant delivery
    6. Returns message object to frontend
    
    REQUEST BODY (JSON):
    {
        "receiverId": 5,              // Who to send message to
        "content": "Hi, available?"   // What message says
    }
    
    PARAMETERS:
    - message_data: MessageCreate schema from request body
    - current_user: Extracted from JWT token (who is sending)
    - db: Database session for queries
    
    RETURNS (JSON):
    {
        "id": 123,
        "senderId": 1,
        "receiverId": 5,
        "content": "Hi, available?",
        "createdAt": "2025-11-23T12:00:00",
        "isRead": 0
    }
    
    ERROR CASES:
    - 404: Receiver not found (invalid receiverId)
    - 401: Not authenticated (missing token)
    
    HYBRID APPROACH:
    Step 1: Save to database (REST API) - PERSISTENCE
    Step 2: Emit Socket.IO if online - REAL-TIME
    
    This ensures:
    - Message never gets lost (saved first)
    - Instant delivery if recipient is online (Socket.IO)
    - Fetch from database if recipient is offline
    """
    # Step 1: Verify the receiver exists before saving message
    # This prevents saving messages to non-existent users
    receiver = db.query(User).filter(User.id == message_data.receiverId).first()
    if not receiver:
        raise HTTPException(status_code=404, detail="Receiver not found")
    
    # Step 2: Create new Message object
    # Message is not saved yet - just created in Python
    new_message = Message(
        sender_id=current_user.id,        # Who is sending this
        receiver_id=message_data.receiverId,  # Who receives this
        content=message_data.content,     # What the message says
        # is_read defaults to 0 (unread) in the database model
    )
    
    # Step 3: Save message to database
    db.add(new_message)       # Add to session
    db.commit()               # Write to database (PERMANENT)
    db.refresh(new_message)   # Reload to get timestamp from database
    
    # Step 4: Send real-time notification via Socket.IO if receiver is online
    # Check if receiver is in connected_users dictionary
    if message_data.receiverId in connected_users:
        # Receiver is online! Get their socket connection ID
        receiver_socket_id = connected_users[message_data.receiverId]
        
        # Emit 'receive_message' event to their socket immediately
        # This makes message appear instantly if they're viewing chat
        await sio.emit('receive_message', {
            'senderId': current_user.id,
            'content': message_data.content,
            'timestamp': new_message.created_at.isoformat()
        }, to=receiver_socket_id)
    # If receiver is offline, do nothing - they'll fetch message later when they connect
    
    # Step 5: Return the saved message to frontend
    # Frontend uses this to display the message in the chat
    return {
        "id": new_message.id,
        "senderId": new_message.sender_id,
        "receiverId": new_message.receiver_id,
        "content": new_message.content,
        "createdAt": new_message.created_at,
        "isRead": new_message.is_read  # Will be 0 (unread)
    }

@app.get("/api/messages/{user_id}", response_model=List[MessageResponse])
def get_messages(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    REST API endpoint to FETCH all messages between two users
    
    Gets the complete conversation history between the current user and user_id.
    Returns messages in chronological order (oldest first).
    
    WORKFLOW:
    1. Frontend calls GET /api/messages/5 (to get messages with user 5)
    2. Backend queries database for all messages between current user and user 5
    3. Returns messages sorted by timestamp
    4. Frontend displays messages in the chat
    5. Frontend then calls mark-read endpoint to mark them as read
    
    URL PARAMETERS:
    - user_id: The other user in the conversation (whose ID appears in URL)
      Example: GET /api/messages/5 -> Get messages between me and user 5
    
    PARAMETERS:
    - user_id: Extracted from URL path
    - current_user: Extracted from JWT token (who is requesting)
    - db: Database session for queries
    
    RETURNS (JSON): Array of message objects
    [
        {
            "id": 1,
            "senderId": 1,
            "receiverId": 5,
            "content": "Hi, is this still available?",
            "createdAt": "2025-11-23T12:00:00",
            "isRead": 0
        },
        {
            "id": 2,
            "senderId": 5,
            "receiverId": 1,
            "content": "Yes, still available!",
            "createdAt": "2025-11-23T12:01:00",
            "isRead": 1
        }
    ]
    
    DATABASE QUERY:
    Finds messages where:
    - (sender_id = current_user.id AND receiver_id = user_id) OR
    - (sender_id = user_id AND receiver_id = current_user.id)
    
    Then sorts by created_at (chronological order)
    
    IMPORTANT NOTE:
    - This endpoint does NOT automatically mark messages as read
    - That's done separately via PUT /api/messages/{user_id}/mark-read
    - This keeps read status separate from message fetching
    """
    # Step 1: Query database for all messages between the two users
    # Use OR to get messages in both directions:
    # - Messages I sent to user_id
    # - Messages from user_id to me
    messages = db.query(Message).filter(
        or_(
            # Messages I (current_user) sent to user_id
            and_(Message.sender_id == current_user.id, Message.receiver_id == user_id),
            # Messages from user_id sent to me (current_user)
            and_(Message.sender_id == user_id, Message.receiver_id == current_user.id)
        )
    ).order_by(Message.created_at).all()  # Sort by timestamp (oldest first)
    
    # Step 2: Format messages as dictionaries with camelCase keys
    # (Frontend expects camelCase for consistency with other endpoints)
    return [
        {
            "id": m.id,              # Message ID
            "senderId": m.sender_id,      # Who sent this message
            "receiverId": m.receiver_id,  # Who received this message
            "content": m.content,         # Message text content
            "createdAt": m.created_at,    # When it was sent (timestamp)
            "isRead": m.is_read           # Read status: 0 = unread, 1 = read
        }
        for m in messages
    ]

@app.get("/api/conversations")
def get_conversations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all conversations for the current user.
    Returns a list of users with the last message and unread count.
    Optimized to avoid N+1 queries.
    """
    # Fetch all messages where current_user is sender or receiver
    # Ordered by newest first
    messages = db.query(Message).filter(
        or_(
            Message.sender_id == current_user.id,
            Message.receiver_id == current_user.id
        )
    ).order_by(Message.created_at.desc()).all()
    
    conversations = {}
    
    print(f"DEBUG: Current User ID: {current_user.id}")
    
    for msg in messages:
        other_user_id = msg.receiver_id if msg.sender_id == current_user.id else msg.sender_id
        
        print(f"DEBUG: Msg ID: {msg.id}, Sender: {msg.sender_id}, Receiver: {msg.receiver_id}, Other User ID: {other_user_id}")
        
        if other_user_id not in conversations:
            # Fetch user details (cache this if possible, but for now query is okay as it's per unique user)
            # To further optimize, we could fetch all relevant users in one query
            other_user = db.query(User).filter(User.id == other_user_id).first()
            if not other_user:
                print(f"DEBUG: User {other_user_id} not found")
                continue
                
            conversations[other_user_id] = {
                "id": other_user.id,
                "fullName": other_user.full_name,
                "username": other_user.username,
                "profileImage": other_user.profile_image,
                "lastMessage": msg.content,
                "lastMessageTime": msg.created_at,
                "unreadCount": 0
            }
            
        # Count unread messages (only if I am the receiver)
        if msg.receiver_id == current_user.id and msg.is_read == 0:
            conversations[other_user_id]["unreadCount"] += 1
            
    return list(conversations.values())

@app.put("/api/messages/{user_id}/mark-read")
def mark_messages_read(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    REST API endpoint to MARK MESSAGES AS READ
    
    When a user opens a conversation, this endpoint is called to mark all
    unread messages from that conversation as read. This makes the notification
    badge disappear for that conversation.
    
    WORKFLOW:
    1. User opens conversation with user_id
    2. Frontend calls selectConversation(user_id)
    3. selectConversation calls this endpoint
    4. All unread messages from user_id are marked as read
    5. Notification badge disappears (updateMessageBadge() hides it)
    
    URL PARAMETERS:
    - user_id: The conversation partner whose messages to mark as read
    
    PARAMETERS:
    - user_id: Extracted from URL path
    - current_user: Extracted from JWT token (who is marking as read)
    - db: Database session for queries
    
    RETURNS (JSON):
    {
        "status": "success",
        "message": "Marked 5 messages as read"
    }
    
    DATABASE QUERY:
    Finds all messages where:
    - sender_id = user_id (messages from that user)
    - receiver_id = current_user.id (addressed to me)
    - is_read = 0 (currently unread)
    
    Then sets is_read = 1 for all of them
    
    NOTIFICATION FLOW:
    BEFORE: User has unread message -> Badge shows red dot (●)
    CALL: PUT /api/messages/5/mark-read -> Marks them as read in database
    AFTER: updateMessageBadge() runs -> Counts unread -> Finds 0 -> Hides badge
    """
    # Step 1: Find all unread messages FROM user_id TO current_user
    # We only mark messages as read if:
    # - They came from user_id (sender_id = user_id)
    # - They're addressed to current_user (receiver_id = current_user.id)
    # - They're currently unread (is_read = 0)
    messages = db.query(Message).filter(
        and_(
            Message.sender_id == user_id,              # From this user
            Message.receiver_id == current_user.id,    # To me
            Message.is_read == 0                       # Currently unread
        )
    ).all()
    
    # Step 2: Mark each message as read (is_read = 1)
    for msg in messages:
        msg.is_read = 1  # 0 = unread, 1 = read
    
    # Step 3: Commit changes to database (PERMANENT)
    db.commit()
    
    # Step 4: Return success response
    return {
        "status": "success",
        "message": f"Marked {len(messages)} messages as read"
    }

# =============================================================================
# COMMENT ENDPOINTS (Product Comments/Questions)
# =============================================================================

@app.post("/api/products/{product_id}/comments", response_model=CommentResponse)
def create_comment(
    product_id: int,
    comment_data: CommentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new comment on a product"""
    # Check if product exists
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Create new comment
    new_comment = Comment(
        product_id=product_id,
        author_id=current_user.id,
        content=comment_data.content
    )
    
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    
    return {
        "id": new_comment.id,
        "productId": new_comment.product_id,
        "authorId": new_comment.author_id,
        "content": new_comment.content,
        "createdAt": new_comment.created_at,
        "author": {
            "id": current_user.id,
            "fullName": current_user.full_name,
            "username": current_user.username,
            "email": current_user.email,
            "bio": current_user.bio,
            "profileImage": current_user.profile_image,
            "phone": current_user.phone
        }
    }

@app.get("/api/products/{product_id}/comments", response_model=List[CommentResponse])
def get_comments(
    product_id: int,
    db: Session = Depends(get_db)
):
    """Get all comments for a product"""
    comments = db.query(Comment).filter(Comment.product_id == product_id).order_by(Comment.created_at.desc()).all()
    
    return [
        {
            "id": c.id,
            "productId": c.product_id,
            "authorId": c.author_id,
            "content": c.content,
            "createdAt": c.created_at,
            "author": {
                "id": c.author.id,
                "fullName": c.author.full_name,
                "username": c.author.username,
                "email": c.author.email,
                "bio": c.author.bio,
                "profileImage": c.author.profile_image,
                "phone": c.author.phone
            }
        }
        for c in comments
    ]

@app.delete("/api/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(
    comment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a comment (only author or seller can delete)"""
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    # Check if current user is the author or the product seller
    if comment.author_id != current_user.id and comment.product.seller_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only delete your own comments")
    
    db.delete(comment)
    db.commit()
    
    return None
# =============================================================================
# FRONTEND ROUTES (SERVE HTML)
# =============================================================================

@app.get("/")
async def read_root():
    """Serve the homepage"""
    return FileResponse("index.html")

@app.get("/{page_name}.html")
async def read_html(page_name: str):
    """Serve other HTML pages (e.g., login.html, products.html)"""
    # Security check: prevent directory traversal
    if ".." in page_name or "/" in page_name:
        raise HTTPException(status_code=404, detail="Page not found")
    
    file_path = f"{page_name}.html"
    if os.path.exists(file_path):
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="Page not found")
