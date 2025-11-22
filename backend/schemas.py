from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List
from datetime import datetime

class UserRegister(BaseModel):
    fullName: str = Field(..., min_length=2, max_length=255)
    username: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=72, description="Password must be between 6 and 72 characters (bcrypt limit)")
    universityId: int

class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., max_length=72)

class UserResponse(BaseModel):
    id: int
    fullName: str
    email: str
    username: str
    bio: Optional[str] = None
    profileImage: Optional[str] = None
    phone: Optional[str] = None
    
    class Config:
        from_attributes = True

class LoginResponse(BaseModel):
    token: str
    user: UserResponse

class ProductImageResponse(BaseModel):
    id: int
    imageUrl: str
    isPrimary: int
    
    class Config:
        from_attributes = True

class SellerInfo(BaseModel):
    id: int
    fullName: str
    username: str
    profileImage: Optional[str] = None
    
    class Config:
        from_attributes = True

class CategoryResponse(BaseModel):
    id: int
    name: str
    
    class Config:
        from_attributes = True

class ProductResponse(BaseModel):
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
    name: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    price: float = Field(..., gt=0)
    categoryId: int
    location: Optional[str] = None
    images: List[str] = Field(..., min_items=1, max_items=5)
    condition: Optional[str] = None
    size: Optional[str] = None
    color: Optional[str] = None

class ProductUpdate(BaseModel):
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
    page: int
    limit: int
    totalPages: int
    totalResults: int
    products: List[ProductResponse]

class SavedItemToggle(BaseModel):
    productId: int

class SavedItemResponse(BaseModel):
    isSaved: bool

class UploadResponse(BaseModel):
    imageUrl: str
