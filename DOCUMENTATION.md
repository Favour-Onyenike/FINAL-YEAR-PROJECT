# UniMarket Full Documentation

## Overview
UniMarket is a full-stack peer-to-peer marketplace for university students. This document explains how every part of the code works, line by line.

---

## Project Structure

```
UniMarket/
├── backend/                    # FastAPI backend (Python)
│   ├── main.py                # Main API endpoints
│   ├── models.py              # Database table definitions
│   ├── database.py            # Database connection setup
│   ├── auth.py                # Authentication & security
│   ├── schemas.py             # Request/response validation
│   └── uploads/               # User uploaded images
│
├── js/                        # Frontend JavaScript
│   ├── app.js                 # General UI interactions
│   └── products.js            # Product filtering & sorting
│
├── css/                       # Stylesheets
│   ├── style.css              # Main styles
│   └── products.css           # Product page styles
│
├── HTML files                 # Frontend pages
│   ├── index.html             # Home page
│   ├── products.html          # Products listing
│   ├── login.html             # Login page
│   ├── signup.html            # Registration page
│   └── ...
│
├── server.py                  # Python HTTP server (frontend)
├── start.sh                   # Startup script
├── unimarket.db               # SQLite database (created automatically)
└── pyproject.toml             # Python dependencies
```

---

## Backend Overview

### How the Backend Works (High Level)

1. **User submits data** (login, create product, etc.)
2. **FastAPI receives the request** (main.py)
3. **Database is queried** (models.py with SQLAlchemy)
4. **Response is sent back** as JSON
5. **Frontend displays the result**

### Architecture

```
User Request
    ↓
FastAPI Routes (main.py)
    ↓
Validation (schemas.py)
    ↓
Authentication Check (auth.py)
    ↓
Database Query (models.py + database.py)
    ↓
Response
```

---

## File-by-File Breakdown

### 1. backend/database.py
**Purpose**: Database connection and initialization

**Key Concepts**:
- **Engine**: The connection to the database (SQLite or PostgreSQL)
- **Session**: A temporary connection used for one request
- **init_db()**: Creates tables and adds initial data on startup

**What happens on startup**:
1. Creates all database tables
2. Adds "Baze University" if not exists
3. Adds product categories if not exist

---

### 2. backend/models.py
**Purpose**: Define database table structure

**Tables Created**:
- `universities`: Stores university info
- `users`: Stores student/staff accounts
- `categories`: Product categories (Books, Electronics, etc.)
- `products`: Product listings
- `product_images`: Product photos
- `saved_items`: User bookmarks/wishlist

**Key Concept - Foreign Keys**:
A foreign key links one table to another:
```
User has university_id → Points to universities table
Product has seller_id → Points to users table
Product has category_id → Points to categories table
```

**Key Concept - Relationships**:
Make it easy to access related data:
```python
user = db.query(User).first()
user.products  # Get all products this user created (automatic!)
user.university  # Get the university they belong to (automatic!)
```

---

### 3. backend/auth.py
**Purpose**: Handle login, password security, and token verification

**Three Main Functions**:

1. **get_password_hash(password)**
   - Takes plain password
   - Hashes it using bcrypt (encryption)
   - Returns hash to store in database
   - Used during: REGISTRATION

2. **verify_password(plain_password, hash)**
   - Takes plain password from login form
   - Checks if it matches the stored hash
   - Returns True/False
   - Used during: LOGIN

3. **create_access_token(data)**
   - Creates a JWT token
   - Token contains user ID
   - Token expires in 7 days
   - Sent to frontend
   - Used during: LOGIN SUCCESS

4. **get_current_user(credentials, db)**
   - Reads token from Authorization header
   - Verifies token is valid and not expired
   - Finds user in database
   - Returns user object
   - Used during: EVERY PROTECTED ENDPOINT

**How Authentication Flow Works**:

```
REGISTRATION:
User enters password
  ↓
get_password_hash() → bcrypt hashes it
  ↓
Store hash in database (NOT plain password)

LOGIN:
User enters email and password
  ↓
Find user by email in database
  ↓
verify_password(password, stored_hash) → True/False
  ↓
If True: create_access_token() → Send token to frontend
  ↓
Frontend stores token in localStorage

MAKING API REQUESTS:
Frontend sends: Authorization: Bearer <token>
  ↓
get_current_user() reads the token
  ↓
Verifies signature using SECRET_KEY
  ↓
Checks if expired
  ↓
Finds user in database
  ↓
Returns user to endpoint (or raises 401 error)
```

---

### 4. backend/schemas.py
**Purpose**: Validate incoming data and format outgoing data

**What it does**:
- Checks that data matches expected format
- Example: Email must be valid, password must be 6+ chars
- Converts between Python objects and JSON

**Example**:
```python
class UserRegister(BaseModel):
    fullName: str = Field(..., min_length=2, max_length=255)
    # ↑ fullName must be string, 2-255 chars
    
    password: str = Field(..., min_length=6, max_length=72)
    # ↑ password must be 6-72 chars (bcrypt limit)
```

When frontend sends:
```json
{
    "fullName": "John Doe",
    "email": "john@bazeuniversity.edu.ng",
    "password": "password123",
    "universityId": 1
}
```

Pydantic automatically:
- Checks format is correct
- Validates email format
- Validates password length
- Returns error if anything is wrong

---

### 5. backend/main.py
**Purpose**: All API endpoints (routes)

**How endpoints work**:
```python
@app.post("/api/auth/login")
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    # endpoint code here
```

Breaking this down:
- `@app.post()`: HTTP POST request
- `"/api/auth/login"`: URL path
- `credentials: UserLogin`: Validate request with UserLogin schema
- `db: Session = Depends(get_db)`: Get database session automatically

**Main Endpoints**:

1. **POST /api/auth/register**
   - Validates email doesn't exist
   - Validates username doesn't exist
   - Validates university domain
   - Hashes password
   - Saves to database

2. **POST /api/auth/login**
   - Finds user by email
   - Verifies password
   - Creates JWT token
   - Returns token + user data

3. **GET /api/auth/me**
   - Requires valid JWT
   - Returns current user profile

4. **GET /api/products**
   - List all available products
   - Support filtering: category, price, condition
   - Support sorting: newest, price-asc, price-desc
   - Support pagination: page, limit

5. **GET /api/products/{id}**
   - Get details for one product

6. **POST /api/products**
   - Create new product (requires login)
   - Validate 1-5 images provided
   - Save to database with seller_id

7. **PUT /api/products/{id}**
   - Update product (requires login, must be owner)
   - Check user is the seller
   - Update fields

8. **DELETE /api/products/{id}**
   - Delete product (soft delete - mark as "deleted")
   - Requires login, must be owner

9. **POST /api/saved-items**
   - Toggle save/unsave product
   - Creates or deletes SavedItem record

10. **GET /api/saved-items**
    - Get user's saved products (requires login)

11. **POST /api/upload**
    - Handle image uploads
    - Save to backend/uploads/products/
    - Return URL

12. **GET /api/categories**
    - List all product categories

---

## Frontend Overview

### How Frontend Works

1. User opens website → server.py serves HTML
2. HTML loads CSS and JavaScript
3. JavaScript runs code to add interactivity
4. When user clicks buttons/submits forms → JavaScript makes API calls
5. API returns JSON data
6. JavaScript updates page with new data

### Key Frontend Concepts

**localStorage**: Browser storage that persists after page refresh
```javascript
localStorage.setItem('token', 'abc123')  // Save token
localStorage.getItem('token')            // Get token
localStorage.removeItem('token')         // Delete token
```

**API Calls from Frontend**:
```javascript
fetch('http://localhost:8000/api/products', {
    method: 'GET',  // or POST, PUT, DELETE
    headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token  // Include token for protected endpoints
    },
    body: JSON.stringify(data)  // Send data for POST/PUT
})
```

---

### 6. js/app.js
**Purpose**: General UI interactions

**What it does**:
- Mobile menu toggle
- Sticky header shadow
- Animated counters
- Save/bookmark buttons
- Dropdown menus
- Search functionality

---

### 7. js/products.js
**Purpose**: Product page filtering and sorting

**Key Functions**:

1. **fetchProducts()**
   - Makes API call with current filters
   - Builds query string: ?category=Electronics&sortBy=price-asc
   - Gets products from backend
   - Calls displayProducts() to show results

2. **displayProducts(products)**
   - Takes product array from API
   - Creates HTML for each product
   - Inserts into page
   - Updates Lucide icons

3. **Event Listeners**:
   - Category dropdown → calls fetchProducts()
   - Price slider → updates currentFilters, doesn't fetch yet
   - Apply Filter button → calls fetchProducts()
   - Sort dropdown → calls fetchProducts()
   - Clear All button → resets filters, calls fetchProducts()

---

## How Data Flows Through the App

### Registration Flow
```
1. User enters credentials on signup.html
2. JavaScript sends POST /api/auth/register
3. Backend validates email, username, university domain
4. Backend hashes password with bcrypt
5. Backend saves new User to database
6. Frontend receives success message
7. Frontend redirects to login.html
```

### Login Flow
```
1. User enters email and password on login.html
2. JavaScript sends POST /api/auth/login
3. Backend finds user by email
4. Backend verifies password with bcrypt
5. Backend creates JWT token
6. Backend returns token + user data
7. Frontend stores token in localStorage
8. Frontend redirects to products.html
9. Frontend makes API calls with token in header
```

### Create Product Flow
```
1. User fills form on sell.html
2. JavaScript uploads images → POST /api/upload
3. Backend saves images, returns URLs
4. JavaScript sends POST /api/products with image URLs
5. Backend validates images (1-5)
6. Backend saves Product to database with seller_id
7. Frontend shows success message
8. Product appears on products.html
```

### Browse Products Flow
```
1. User visits products.html
2. JavaScript calls fetchProducts()
3. fetchProducts() builds query string
4. Sends GET /api/products?category=Electronics&sortBy=price-asc
5. Backend queries database with filters
6. Backend returns matching products + images + seller info
7. JavaScript displays products in grid
```

---

## Security Features

### 1. Password Security
- Passwords hashed with bcrypt (one-way encryption)
- Password verification only compares hashes
- Plain passwords never stored in database

### 2. Authentication
- JWT tokens for stateless authentication
- Tokens expire in 7 days
- Tokens signed with SECRET_KEY (secret string)
- Only backend can create valid tokens

### 3. Email Validation
- University email required for registration
- @bazeuniversity.edu.ng enforced for Baze
- Prevents fake accounts

### 4. Authorization
- Protected endpoints check token validity
- Users can only edit/delete their own products
- Users can only view their own saved items

---

## Environment Variables

**LOCAL DEVELOPMENT**:
```bash
# Uses defaults (SQLite, localhost)
DATABASE_URL=sqlite:///./unimarket.db
JWT_SECRET_KEY=your-secret-key-here
```

**PRODUCTION**:
```bash
# Switch to PostgreSQL for scaling
DATABASE_URL=postgresql://user:pass@host/database

# Use strong secret key
JWT_SECRET_KEY=super-long-random-secret-string-with-upper-lower-numbers
```

---

## Running Locally

### Prerequisites
- Python 3.8+
- pip or uv package manager

### Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt
# or
uv sync

# 2. Run both servers
bash start.sh

# 3. Open browser
# Frontend: http://localhost:5000
# API Docs: http://localhost:8000/docs
```

### What happens on first run:
1. SQLite database created (unimarket.db)
2. All tables created automatically
3. Baze University added
4. Categories (Books, Electronics, etc.) added

---

## Switching to PostgreSQL

### Step 1: Create PostgreSQL Database
```bash
# Using pgAdmin or command line
createdb unimarket
```

### Step 2: Set Environment Variable
```bash
export DATABASE_URL="postgresql://user:password@localhost:5432/unimarket"
```

### Step 3: Run App
```bash
bash start.sh
```

### That's it!
- No code changes needed
- SQLAlchemy handles both SQLite and PostgreSQL
- Same app works with both!

---

## API Reference

### Authentication Endpoints

**Register**
```
POST /api/auth/register
{
    "fullName": "John Doe",
    "username": "johndoe",
    "email": "john@bazeuniversity.edu.ng",
    "password": "password123",
    "universityId": 1
}
→ 201 Created: {"message": "User registered successfully."}
```

**Login**
```
POST /api/auth/login
{
    "email": "john@bazeuniversity.edu.ng",
    "password": "password123"
}
→ 200 OK: {"token": "...", "user": {...}}
```

**Get Profile**
```
GET /api/auth/me
Headers: Authorization: Bearer <token>
→ 200 OK: {"id": 1, "fullName": "John Doe", ...}
```

### Product Endpoints

**List Products**
```
GET /api/products?category=Electronics&sortBy=price-asc&page=1&limit=20
→ 200 OK: {"page": 1, "products": [...], "totalResults": 42}
```

**Create Product**
```
POST /api/products
Headers: Authorization: Bearer <token>
{
    "name": "Textbook",
    "description": "...",
    "price": 50.00,
    "categoryId": 1,
    "images": ["url1", "url2"],
    "condition": "Like New"
}
→ 201 Created: {...product...}
```

**Save/Unsave Product**
```
POST /api/saved-items
Headers: Authorization: Bearer <token>
{"productId": 5}
→ 200 OK: {"isSaved": true}
```

---

## Troubleshooting

**API not responding**
- Check server is running: `http://localhost:8000/api/health`
- Check backend logs for errors

**Frontend can't connect to API**
- Frontend uses: `http://localhost:8000/api`
- Backend must be running on port 8000

**Database errors**
- First run: Delete unimarket.db, restart app
- Switches to PostgreSQL: Set DATABASE_URL env var

**Login issues**
- Check JWT_SECRET_KEY is set (or default is used)
- Token expires in 7 days - clear localStorage and re-login

---

## Next Steps

1. **Deploy to production**: Use Replit's publish button
2. **Switch to PostgreSQL**: Handles 50+ concurrent users
3. **Add more features**: Messaging, ratings, payments, etc.
4. **Scale the database**: Use PostgreSQL replication

---

## Summary

- **Backend** (Python/FastAPI): Handles logic, security, database
- **Frontend** (HTML/CSS/JS): User interface, API calls
- **Database**: Stores users, products, images, favorites
- **Security**: Password hashing, JWT tokens, email validation
- **Scalability**: Works with SQLite for small scale, PostgreSQL for large scale

Everything is built to be beginner-friendly while remaining production-ready!
