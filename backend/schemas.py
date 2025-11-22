"""
REQUEST/RESPONSE SCHEMAS
========================
This module defines all data validation schemas using Pydantic.

WHAT PYDANTIC DOES:
1. Validates that incoming request data matches expected format
2. Converts request data to Python objects
3. Converts Python objects back to JSON for responses
4. Provides automatic error messages if data is invalid

WHY WE NEED THIS:
- Type safety: Ensures API gets correct data types
- Automatic validation: Checks constraints (min length, max length, etc.)
- Documentation: Auto-generates API docs showing expected request formats
- Conversion: Handles JSON ↔ Python object conversion automatically

HOW IT WORKS:
1. User sends JSON request: {"email": "john@example.com", "password": "password123"}
2. FastAPI validates against schema (e.g., UserLogin)
3. If valid: Create Python object and pass to endpoint
4. If invalid: Return 422 error with details on what's wrong
5. Endpoint returns Python object
6. FastAPI converts back to JSON and sends to client
"""

from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List
from datetime import datetime

# =============================================================================
# AUTHENTICATION SCHEMAS
# =============================================================================

class UserRegister(BaseModel):
    """
    Schema for user registration request.
    
    USED BY: POST /api/auth/register
    
    FIELDS:
    - fullName: User's full name (2-255 chars)
    - username: Unique username (3-100 chars)
    - email: Valid email address (must use university domain)
    - password: Password (6-72 chars - bcrypt limit)
    - universityId: Which university they belong to
    
    VALIDATION:
    - fullName: At least 2 characters, max 255
    - username: At least 3 characters, max 100
    - email: Must be valid email format
    - password: Between 6-72 characters (bcrypt limitation)
    - universityId: Must be integer
    
    EXAMPLE REQUEST:
    {
        "fullName": "John Doe",
        "username": "johndoe",
        "email": "john@bazeuniversity.edu.ng",
        "password": "password123",
        "universityId": 1
    }
    """
    fullName: str = Field(..., min_length=2, max_length=255)  # ... = required
    username: str = Field(..., min_length=3, max_length=100)
    email: EmailStr  # EmailStr automatically validates email format
    password: str = Field(..., min_length=6, max_length=72, description="Password must be between 6 and 72 characters (bcrypt limit)")
    universityId: int

class UserLogin(BaseModel):
    """
    Schema for login request.
    
    USED BY: POST /api/auth/login
    
    FIELDS:
    - email: User's email address
    - password: User's password
    
    EXAMPLE REQUEST:
    {
        "email": "john@bazeuniversity.edu.ng",
        "password": "password123"
    }
    """
    email: EmailStr
    password: str = Field(..., max_length=72)

class UserResponse(BaseModel):
    """
    Schema for user profile response.
    
    USED BY: GET /api/auth/me response
    
    FIELDS:
    - id: User's ID
    - fullName: User's full name
    - email: User's email
    - username: User's username
    - bio: Optional biography
    - profileImage: Optional profile picture URL
    - phone: Optional phone number
    
    from_attributes = True:
    Converts database model to Pydantic model automatically
    Without this, would need to manually create dict from User object
    """
    id: int
    fullName: str
    email: str
    username: str
    bio: Optional[str] = None
    profileImage: Optional[str] = None
    phone: Optional[str] = None
    
    class Config:
        from_attributes = True  # Convert database models to this schema

class UserUpdate(BaseModel):
    """
    Schema for updating user profile.
    
    USED BY: PUT /api/users/{user_id} request
    
    FIELDS:
    - fullName: User's full name (optional, 2-255 chars)
    - bio: User's biography (optional, max 5000 chars)
    - avatarUrl: URL to profile picture (optional)
    
    All fields are optional - only update fields that are provided.
    
    EXAMPLE REQUEST:
    {
        "fullName": "John Doe",
        "bio": "I'm a student at Baze University",
        "avatarUrl": "/uploads/products/abc123.jpg"
    }
    """
    fullName: Optional[str] = Field(None, min_length=2, max_length=255)
    bio: Optional[str] = Field(None, max_length=5000)
    avatarUrl: Optional[str] = None

class LoginResponse(BaseModel):
    """
    Schema for login response.
    
    USED BY: POST /api/auth/login response
    
    FIELDS:
    - token: JWT token for authentication (send in Authorization header)
    - user: Current user's profile information
    
    EXAMPLE RESPONSE:
    {
        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "user": {
            "id": 1,
            "fullName": "John Doe",
            "email": "john@bazeuniversity.edu.ng",
            "username": "johndoe",
            "bio": null,
            "profileImage": null,
            "phone": null
        }
    }
    """
    token: str
    user: UserResponse

# =============================================================================
# PRODUCT SCHEMAS
# =============================================================================

class ProductImageResponse(BaseModel):
    """
    Schema for product image in responses.
    
    FIELDS:
    - id: Image ID
    - imageUrl: URL to access the image
    - isPrimary: Is this the main/cover image? (1=yes, 0=no)
    """
    id: int
    imageUrl: str
    isPrimary: int
    
    class Config:
        from_attributes = True

class SellerInfo(BaseModel):
    """
    Schema for seller information in product responses.
    
    Shows basic seller info without sensitive data.
    
    FIELDS:
    - id: Seller's user ID
    - fullName: Seller's name
    - username: Seller's username
    - profileImage: Optional seller's profile picture
    """
    id: int
    fullName: str
    username: str
    profileImage: Optional[str] = None
    
    class Config:
        from_attributes = True

class CategoryResponse(BaseModel):
    """
    Schema for product category in responses.
    
    FIELDS:
    - id: Category ID
    - name: Category name (e.g., "Electronics", "Textbooks")
    """
    id: int
    name: str
    
    class Config:
        from_attributes = True

class ProductResponse(BaseModel):
    """
    Schema for complete product in responses.
    
    USED BY:
    - GET /api/products/{id}
    - GET /api/products (in the products array)
    - GET /api/saved-items
    
    FIELDS:
    - id: Product ID
    - name: Product name/title
    - description: Full product description
    - price: Product price
    - location: Where product is located (optional)
    - condition: Product condition (New, Like New, Good, Fair)
    - size: Product size (optional, for clothing)
    - color: Product color (optional)
    - status: available/sold/deleted
    - createdAt: When product was listed
    - updatedAt: When product was last updated
    - images: Array of product images
    - seller: Seller information
    - category: Product category
    
    EXAMPLE:
    {
        "id": 5,
        "name": "Calculus Textbook",
        "description": "Used calculus textbook...",
        "price": 45.99,
        "location": "Library Building",
        "condition": "Like New",
        "size": null,
        "color": null,
        "status": "available",
        "createdAt": "2025-11-22T10:30:00",
        "updatedAt": "2025-11-22T10:30:00",
        "images": [
            {"id": 1, "imageUrl": "/uploads/products/uuid.jpg", "isPrimary": 1}
        ],
        "seller": {...},
        "category": {...}
    }
    """
    id: int
    name: str
    description: str
    price: float
    location: Optional[str] = None
    condition: Optional[str] = None
    size: Optional[str] = None
    color: Optional[str] = None
    status: str
    createdAt: datetime
    updatedAt: datetime
    images: List[ProductImageResponse]
    seller: SellerInfo
    category: CategoryResponse
    
    class Config:
        from_attributes = True

class ProductCreate(BaseModel):
    """
    Schema for creating a new product.
    
    USED BY: POST /api/products
    
    FIELDS:
    - name: Product name (1-255 chars, required)
    - description: Full description (required)
    - price: Product price (must be > 0, required)
    - categoryId: Category ID (required)
    - location: Where product is located (optional)
    - images: Array of image URLs (1-5 images required)
    - condition: Product condition (optional)
    - size: Product size like "M", "Large" (optional)
    - color: Product color (optional)
    
    VALIDATION:
    - price > 0: Can't have free or negative price
    - 1-5 images: Must provide at least 1, max 5
    - name min length 1: Can't be empty
    - description min length 1: Can't be empty
    
    EXAMPLE REQUEST:
    {
        "name": "Calculus Textbook",
        "description": "Used calculus textbook, excellent condition...",
        "price": 45.99,
        "categoryId": 1,
        "location": "Library Building",
        "images": ["/uploads/products/uuid1.jpg", "/uploads/products/uuid2.jpg"],
        "condition": "Like New",
        "size": null,
        "color": null
    }
    
    NOTE: Images must be uploaded via /api/upload endpoint first
    """
    name: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    price: float = Field(..., gt=0)  # gt=0 means "greater than 0"
    categoryId: int
    location: Optional[str] = None
    images: List[str] = Field(..., min_items=1, max_items=5)  # 1-5 images required
    condition: Optional[str] = None
    size: Optional[str] = None
    color: Optional[str] = None

class ProductUpdate(BaseModel):
    """
    Schema for updating an existing product.
    
    USED BY: PUT /api/products/{id}
    
    DIFFERENCES FROM ProductCreate:
    - All fields are OPTIONAL (use None if not updating that field)
    - Same validation rules, just all optional
    
    EXAMPLE REQUEST (only updating price and name):
    {
        "name": "New Price on Calculus Textbook",
        "price": 35.99,
        "description": null,
        "categoryId": null,
        ...other fields null...
    }
    
    Only non-null fields will be updated in database
    """
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, min_length=1)
    price: Optional[float] = Field(None, gt=0)
    categoryId: Optional[int] = None
    location: Optional[str] = None
    images: Optional[List[str]] = Field(None, min_items=1, max_items=5)
    condition: Optional[str] = None
    size: Optional[str] = None
    color: Optional[str] = None

class ProductListResponse(BaseModel):
    """
    Schema for list of products response (paginated).
    
    USED BY: GET /api/products
    
    FIELDS:
    - page: Current page number
    - limit: Number of results per page
    - totalPages: Total number of pages
    - totalResults: Total number of products matching filters
    - products: Array of ProductResponse objects
    
    PAGINATION EXAMPLE:
    If totalResults=100 and limit=20:
    - Page 1: results 1-20
    - Page 2: results 21-40
    - Page 3: results 41-60
    - Page 4: results 61-80
    - Page 5: results 81-100
    - totalPages=5
    
    EXAMPLE RESPONSE:
    {
        "page": 1,
        "limit": 20,
        "totalPages": 5,
        "totalResults": 100,
        "products": [...]  // Array of 20 ProductResponse objects
    }
    """
    page: int
    limit: int
    totalPages: int
    totalResults: int
    products: List[ProductResponse]

# =============================================================================
# SAVED ITEMS (BOOKMARKS) SCHEMAS
# =============================================================================

class SavedItemToggle(BaseModel):
    """
    Schema for saving/unsaving a product.
    
    USED BY: POST /api/saved-items
    
    FIELDS:
    - productId: Which product to save/unsave
    
    BEHAVIOR:
    - If product is already saved: Unsave it (delete SavedItem record)
    - If product is not saved: Save it (create SavedItem record)
    - Response shows current state after toggle
    
    EXAMPLE REQUEST:
    {"productId": 5}
    """
    productId: int

class SavedItemResponse(BaseModel):
    """
    Schema for saved item toggle response.
    
    RETURNED BY: POST /api/saved-items
    
    FIELDS:
    - isSaved: Current save state after toggle
    
    EXAMPLE RESPONSE:
    {"isSaved": true}  // Now saved
    {"isSaved": false}  // Now unsaved
    """
    isSaved: bool

# =============================================================================
# FILE UPLOAD SCHEMA
# =============================================================================

class UploadResponse(BaseModel):
    """
    Schema for file upload response.
    
    USED BY: POST /api/upload
    
    FIELDS:
    - imageUrl: URL where uploaded image is accessible
    
    USAGE FLOW:
    1. Frontend sends image file to POST /api/upload
    2. Backend saves file and returns this response
    3. Frontend gets back the imageUrl
    4. Frontend includes imageUrl in images array when creating product
    5. Backend stores the URL in product_images table
    
    EXAMPLE RESPONSE:
    {"imageUrl": "/uploads/products/3fa85f64-5717-4562-b3fc-2c963f66afa6.jpg"}
    
    This URL can be used in:
    <img src="/uploads/products/3fa85f64-5717-4562-b3fc-2c963f66afa6.jpg" />
    """
    imageUrl: str
