from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import List, Optional
import os
import shutil
import uuid
from datetime import datetime

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

app = FastAPI(title="UniMarket API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("backend/uploads/products", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="backend/uploads"), name="uploads")

@app.on_event("startup")
def startup_event():
    init_db()

@app.get("/api/health")
def health_check():
    return {"status": "healthy"}

@app.post("/api/auth/register", status_code=status.HTTP_201_CREATED)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(
        or_(User.username == user_data.username, User.email == user_data.email)
    ).first()
    
    if existing_user:
        if existing_user.username == user_data.username:
            raise HTTPException(status_code=409, detail="Username already exists")
        if existing_user.email == user_data.email:
            raise HTTPException(status_code=409, detail="Email already exists")
    
    university = db.query(University).filter(University.id == user_data.universityId).first()
    if not university:
        raise HTTPException(status_code=400, detail="Invalid university")
    
    if university.id == 1:
        if not user_data.email.endswith(f"@{university.domain}"):
            raise HTTPException(
                status_code=400,
                detail=f"Email must end with @{university.domain} for {university.name}"
            )
    
    hashed_password = get_password_hash(user_data.password)
    
    new_user = User(
        full_name=user_data.fullName,
        username=user_data.username,
        email=user_data.email,
        password_hash=hashed_password,
        university_id=user_data.universityId
    )
    
    db.add(new_user)
    db.commit()
    
    return {"message": "User registered successfully."}

@app.post("/api/auth/login", response_model=LoginResponse)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == credentials.email).first()
    
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )
    
    access_token = create_access_token(data={"userId": user.id})
    
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
    return {
        "id": current_user.id,
        "fullName": current_user.full_name,
        "email": current_user.email,
        "username": current_user.username,
        "bio": current_user.bio,
        "profileImage": current_user.profile_image,
        "phone": current_user.phone
    }

def serialize_product(product: Product) -> dict:
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
        "images": [
            {
                "id": img.id,
                "imageUrl": img.image_url,
                "isPrimary": img.is_primary
            } for img in product.images
        ],
        "seller": {
            "id": product.seller.id,
            "fullName": product.seller.full_name,
            "username": product.seller.username,
            "profileImage": product.seller.profile_image
        },
        "category": {
            "id": product.category.id,
            "name": product.category.name
        }
    }

@app.get("/api/products", response_model=ProductListResponse)
def get_products(
    q: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    minPrice: Optional[float] = Query(None),
    maxPrice: Optional[float] = Query(None),
    condition: Optional[str] = Query(None),
    sortBy: Optional[str] = Query("newest"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(Product).filter(Product.status == "available")
    
    if q:
        search_term = f"%{q}%"
        query = query.filter(
            or_(
                Product.name.like(search_term),
                Product.description.like(search_term)
            )
        )
    
    if category:
        cat = db.query(Category).filter(Category.name == category).first()
        if cat:
            query = query.filter(Product.category_id == cat.id)
    
    if minPrice is not None:
        query = query.filter(Product.price >= minPrice)
    
    if maxPrice is not None:
        query = query.filter(Product.price <= maxPrice)
    
    if condition:
        query = query.filter(Product.condition == condition)
    
    if sortBy == "price-asc":
        query = query.order_by(Product.price.asc())
    elif sortBy == "price-desc":
        query = query.order_by(Product.price.desc())
    else:
        query = query.order_by(Product.created_at.desc())
    
    total = query.count()
    total_pages = (total + limit - 1) // limit
    
    products = query.offset((page - 1) * limit).limit(limit).all()
    
    return {
        "page": page,
        "limit": limit,
        "totalPages": total_pages,
        "totalResults": total,
        "products": [serialize_product(p) for p in products]
    }

@app.get("/api/products/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return serialize_product(product)

@app.post("/api/products", status_code=status.HTTP_201_CREATED, response_model=ProductResponse)
def create_product(
    product_data: ProductCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    category = db.query(Category).filter(Category.id == product_data.categoryId).first()
    if not category:
        raise HTTPException(status_code=400, detail="Invalid category")
    
    if len(product_data.images) < 1 or len(product_data.images) > 5:
        raise HTTPException(status_code=400, detail="Product must have between 1 and 5 images")
    
    new_product = Product(
        name=product_data.name,
        description=product_data.description,
        price=product_data.price,
        category_id=product_data.categoryId,
        seller_id=current_user.id,
        location=product_data.location,
        condition=product_data.condition,
        size=product_data.size,
        color=product_data.color,
        status="available"
    )
    
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    
    for idx, image_url in enumerate(product_data.images):
        product_image = ProductImage(
            product_id=new_product.id,
            image_url=image_url,
            is_primary=1 if idx == 0 else 0
        )
        db.add(product_image)
    
    db.commit()
    db.refresh(new_product)
    
    return serialize_product(new_product)

@app.put("/api/products/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product_data: ProductUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if product.seller_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only edit your own products")
    
    update_data = product_data.model_dump(exclude_unset=True)
    
    if "images" in update_data:
        images = update_data.pop("images")
        if len(images) < 1 or len(images) > 5:
            raise HTTPException(status_code=400, detail="Product must have between 1 and 5 images")
        
        db.query(ProductImage).filter(ProductImage.product_id == product_id).delete()
        
        for idx, image_url in enumerate(images):
            product_image = ProductImage(
                product_id=product_id,
                image_url=image_url,
                is_primary=1 if idx == 0 else 0
            )
            db.add(product_image)
    
    if "categoryId" in update_data:
        category = db.query(Category).filter(Category.id == update_data["categoryId"]).first()
        if not category:
            raise HTTPException(status_code=400, detail="Invalid category")
        product.category_id = update_data.pop("categoryId")
    
    for key, value in update_data.items():
        setattr(product, key, value)
    
    product.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(product)
    
    return serialize_product(product)

@app.delete("/api/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if product.seller_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only delete your own products")
    
    product.status = "deleted"
    db.commit()
    
    return None

@app.post("/api/saved-items", response_model=SavedItemResponse)
def toggle_saved_item(
    data: SavedItemToggle,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(Product.id == data.productId).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    saved_item = db.query(SavedItem).filter(
        and_(SavedItem.user_id == current_user.id, SavedItem.product_id == data.productId)
    ).first()
    
    if saved_item:
        db.delete(saved_item)
        db.commit()
        return {"isSaved": False}
    else:
        new_saved_item = SavedItem(
            user_id=current_user.id,
            product_id=data.productId
        )
        db.add(new_saved_item)
        db.commit()
        return {"isSaved": True}

@app.get("/api/saved-items", response_model=List[ProductResponse])
def get_saved_items(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    saved_items = db.query(SavedItem).filter(SavedItem.user_id == current_user.id).all()
    product_ids = [item.product_id for item in saved_items]
    
    products = db.query(Product).filter(Product.id.in_(product_ids)).all()
    
    return [serialize_product(p) for p in products]

@app.post("/api/upload", response_model=UploadResponse)
async def upload_image(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    file_extension = file.filename.split(".")[-1]
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = f"backend/uploads/products/{unique_filename}"
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return {"imageUrl": f"/uploads/products/{unique_filename}"}

@app.get("/api/categories")
def get_categories(db: Session = Depends(get_db)):
    categories = db.query(Category).all()
    return [{"id": c.id, "name": c.name} for c in categories]
