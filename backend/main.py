"""
UNIMARKET API - MAIN ENDPOINTS
==============================
This is the main backend API file that handles all HTTP requests.
It contains all the routes (endpoints) that the frontend calls.

STRUCTURE:
1. Import statements (required libraries)
2. FastAPI app initialization
3. CORS middleware setup (allows frontend to call API)
4. Startup event (runs when server starts)
5. API endpoints organized by feature:
   - Health check
   - Authentication (register, login, get profile)
   - Products (list, get, create, update, delete)
   - Saved items (bookmark products)
   - Image uploads
   - Categories

WHAT HAPPENS WHEN A REQUEST COMES IN:
1. FastAPI receives HTTP request (POST, GET, etc.)
2. Matches URL to @app.post/@app.get decorator
3. Validates request data with Pydantic schema
4. Gets database session
5. Executes endpoint function
6. Returns response as JSON
"""

from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware  # Allow cross-origin requests
from fastapi.staticfiles import StaticFiles  # Serve static files (images)
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_  # SQL query helpers
from typing import List, Optional
import os
import shutil
import uuid  # Generate unique filenames
from datetime import datetime

# Import database and authentication functions
from backend.database import get_db, init_db
from backend.models import User, University, Product, ProductImage, SavedItem, Category
from backend.schemas import (
    UserRegister, UserLogin, UserResponse, LoginResponse,
    ProductCreate, ProductUpdate, ProductResponse, ProductListResponse,
    SavedItemToggle, SavedItemResponse, UploadResponse,
    SellerInfo, CategoryResponse, ProductImageResponse
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
    user = db.query(User).filter(User.email == credentials.email).first()
    
    # Verify password
    # verify_password does bcrypt comparison (doesn't expose the hash)
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
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
    page: int = Query(1, ge=1),  # Page number (starts at 1)
    limit: int = Query(20, ge=1, le=100),  # Results per page
    db: Session = Depends(get_db)
):
    """
    List all available products with filtering, sorting, and pagination.
    
    QUERY PARAMETERS (all optional):
    ?q=textbook&category=Textbooks&minPrice=10&maxPrice=100&condition=Like New&sortBy=price-asc&page=1&limit=20
    
    RETURNS:
    {
        "page": 1,
        "limit": 20,
        "totalPages": 5,
        "totalResults": 100,
        "products": [...]  // Array of product objects
    }
    
    HOW IT WORKS:
    1. Start with query: Get all products where status="available"
    2. Apply filters: Search text, category, price range, condition
    3. Apply sorting: newest, price ascending, or price descending
    4. Apply pagination: Skip to correct page, limit results
    5. Count total results and calculate total pages
    6. Return paginated results
    """
    # Start with all available products (not deleted/sold)
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
