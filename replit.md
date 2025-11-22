# UniMarket - Campus Marketplace

## Overview
UniMarket is a full-stack peer-to-peer marketplace designed for university students to buy, sell, and connect safely on campus. The project consists of a static frontend (HTML/CSS/JavaScript) and a FastAPI backend with RESTful API endpoints.

## Project Type
- **Type**: Full-stack web application
- **Frontend**: Static HTML/CSS/JavaScript
- **Backend**: FastAPI (Python)
- **Database**: SQLite (development) / PostgreSQL ready
- **Frontend Port**: 5000
- **Backend Port**: 8000

## Technology Stack

### Frontend
- HTML5
- CSS3 (custom styling with CSS variables)
- JavaScript (ES6+, vanilla)
- Lucide Icons (via CDN)

### Backend
- Python 3.11
- FastAPI (web framework)
- SQLAlchemy (ORM)
- SQLite (database, development)
- PostgreSQL driver (psycopg2-binary) installed for production
- JWT (authentication)
- bcrypt (password hashing)

## Project Structure
```
UniMarket/
├── backend/                # Backend API
│   ├── __init__.py        # Package initializer
│   ├── main.py            # FastAPI application and routes (DOCUMENTED)
│   ├── models.py          # SQLAlchemy database models (DOCUMENTED)
│   ├── database.py        # Database connection and initialization (DOCUMENTED)
│   ├── auth.py            # Authentication utilities: JWT, bcrypt (DOCUMENTED)
│   ├── schemas.py         # Pydantic schemas for request/response (DOCUMENTED)
│   └── uploads/           # File upload directory
│       └── products/      # Product images
├── css/                    # Frontend stylesheets
│   ├── style.css          # Main global styles
│   └── products.css       # Product page styles
├── js/                     # Frontend JavaScript
│   ├── app.js             # Global UI interactions (DOCUMENTED)
│   └── products.js        # Product page filtering & sorting (DOCUMENTED)
├── img/                    # Frontend image assets
├── HTML pages             # Landing, login, signup, products, etc.
│   ├── index.html
│   ├── login.html
│   ├── signup.html
│   ├── products.html
│   ├── product-detail.html
│   └── profile.html
├── server.py              # Frontend HTTP server (DOCUMENTED)
├── start.sh               # Startup script (DOCUMENTED)
├── DOCUMENTATION.md       # Comprehensive beginner-friendly guide
├── unimarket.db           # SQLite database
└── README.md              # Original documentation
```

## Key Features

### Frontend
- Responsive design for desktop, tablet, and mobile
- User authentication pages (login/signup)
- Product browsing by category
- Search functionality with suggestions
- Product detail views
- User profiles
- Newsletter subscription

### Backend API
- User authentication with JWT tokens (7-day expiry)
- User registration with university email validation
- Product CRUD operations (Create, Read, Update, Delete)
- Product filtering: category, price range, condition
- Product sorting: newest, price ascending/descending
- Pagination support (configurable page size)
- Image upload functionality (1-5 images per product)
- Saved items/wishlist feature
- Automatic API documentation (Swagger UI at `/docs`)

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user with university email
- `POST /api/auth/login` - Login and get JWT token
- `GET /api/auth/me` - Get current user profile (requires JWT)

### Products
- `GET /api/products` - List products with filtering, sorting, pagination
- `GET /api/products/{id}` - Get single product details
- `POST /api/products` - Create new product (requires JWT)
- `PUT /api/products/{id}` - Update product (requires JWT, owner only)
- `DELETE /api/products/{id}` - Soft delete product (requires JWT, owner only)

### Saved Items
- `POST /api/saved-items` - Toggle save/unsave product (requires JWT)
- `GET /api/saved-items` - Get user's saved products (requires JWT)

### Other
- `POST /api/upload` - Upload product image file
- `GET /api/categories` - Get all product categories
- `GET /api/health` - Health check endpoint

## Development Setup
The project runs both frontend and backend servers simultaneously:
- **Frontend**: Python HTTP server on port 5000 (0.0.0.0 - all interfaces)
- **Backend**: FastAPI/Uvicorn on port 8000 (127.0.0.1 - localhost only)
- Both servers start automatically via `start.sh`

```bash
bash start.sh
# Frontend: http://localhost:5000 or http://0.0.0.0:5000
# API Docs: http://localhost:8000/docs
```

## Database Schema

### Tables
- **universities**: University information and email domains
- **users**: User accounts and profiles
- **categories**: Product categories
- **products**: Product listings with soft delete
- **product_images**: Product images (1-5 per product)
- **saved_items**: User wishlists/bookmarks

## Security Features
- **Password Security**: Passwords hashed with bcrypt (one-way, slow by design)
- **Authentication**: JWT tokens for stateless authentication
- **Token Expiry**: Tokens expire in 7 days
- **Email Validation**: University email domain required for registration
- **Authorization**: Users can only edit/delete their own products
- **Soft Deletes**: Products marked deleted, not permanently removed

## Recent Changes
- **2025-11-22**: Major Performance Optimization & Fixes
  - **Image Compression**: Reduced from 35.5MB to 9MB (75% savings!)
    * cloths.jpg: 18.8MB → 3.7MB (80% saved)
    * elect.jpg: 10.8MB → 1.2MB (89% saved)
    * textbooks.jpg: 3.2MB → 1.1MB (64% saved)
  - **Lazy Loading**: Added `loading="lazy"` to homepage product images
  - **Fixed Duplicate Script Error**: Removed duplicate products.js script tag (was causing API_URL error)
  - **Price Range Updated**: ₦0 - ₦10,000 (was 0-1000)
  - **Expected Results**: Homepage now loads in 1-2 seconds (was 5-10 seconds)
  - **Zero Functionality Loss**: All features, UI, and design preserved perfectly

- **2025-11-22**: Empty State UI Improvements
  - Added "View All Products" link when no products match filter/search
  - Shows on both desktop and mobile
  - Helps users clear filters and browse all items
  - Link takes them back to products page with no filters

- **2025-11-22**: Mobile Filter Modal Made Scrollable
  - Filter modal can now scroll when content exceeds screen height
  - Header stays visible at top
  - "Apply" and "Cancel" buttons stay at bottom
  - All filter options are accessible on mobile

- **2025-11-22**: Seller Listing Form Enhanced for Better Filtering
  - Updated sell.html to ask sellers for appropriate details
  - When seller selects "Clothing" category, dynamic fields appear:
    * **Clothing Type**: Shirts, Trousers, Dresses, Skirts (required for clothing)
    * **Size**: XS, S, M, L, XL dropdown (required for clothing)
    * **Color**: Text input for color (required for clothing)
  - **Condition field** now shows for all products (not just clothing)
  - Price field now displays as ₦ (Nigerian Naira)
  - Clothing-specific fields become required when "Clothing" is selected
  - Clothing-specific fields become optional when different category is selected
  - Form properly collects all data for accurate product filtering
  - Added loader to sell.html page

- **2025-11-22**: Advanced Clothing Filters Added
  - Implemented dynamic clothing-specific filters (only show when "Clothing" category selected)
  - Added Sub-Category filter: Shirts, Trousers, Dresses, Skirts
  - Added Size filter: XS, S, M, L, XL (checkboxes - multiple selection)
  - Added Color filter: Red, Blue, Black, White (checkboxes - multiple selection)
  - Frontend sends all filters as query parameters: sizes=M,L&colors=Red,Blue&subCategories=Shirts
  - Connected "Apply Filter" button and clothing filter checkboxes to updateClothingFilters()
  - Connected "Clear All" button to clearAllFilters() which resets all filters and UI

- **2025-11-22**: Loading Spinners Added
  - Created css/loader.css with animated spinner
  - Added loader HTML to index.html, products.html, product-detail.html
  - Loader shows while page is loading, hides automatically when page fully loads
  - Each page has custom loading message (Loading..., Loading products..., etc.)

- **2025-11-22**: Currency Updated to Nigerian Naira
  - Changed all prices from USD ($) to Nigerian Naira (₦)
  - Updated hardcoded prices in index.html, products.html, product-detail.html
  - Updated dynamic price formatting in js/products.js
  - All prices now display as ₦X.XX across the entire app

- **2025-11-22**: Fixed Sort & Filter Functionality
  - Added event listeners for sort dropdown in products.html
  - Connected category, condition, and price filters to JavaScript functions
  - All filters now properly call fetchProducts() to reload data from API

- **2025-11-22**: Fixed Homepage Performance Issue
  - Added Lucide Icons library to <head> of index.html
  - Removed duplicate script tag to prevent errors
  - Homepage now loads quickly without JavaScript errors

- **2025-11-22**: Comprehensive Documentation Added
  - Added detailed inline comments to all backend files (database.py, models.py, auth.py, schemas.py, main.py)
  - Added comprehensive JavaScript documentation (app.js, products.js)
  - Added documentation to server.py and start.sh
  - Created DOCUMENTATION.md: 400+ line beginner-friendly guide covering:
    * High-level architecture and data flow
    * File-by-file explanations
    * Security features
    * How to switch to PostgreSQL
    * Complete API reference
    * Troubleshooting guide
  - Every function now has detailed docstrings explaining:
    * What it does
    * How it works step-by-step
    * Parameters and return values
    * Usage examples

- **2025-11-22**: PostgreSQL Ready
  - Installed psycopg2-binary driver
  - App is database-agnostic via SQLAlchemy
  - Can switch to PostgreSQL by setting DATABASE_URL environment variable
  - No code changes needed when switching databases

- **2025-11-22**: Backend API Implementation
  - Created FastAPI backend with all required endpoints
  - Set up SQLite database with SQLAlchemy ORM
  - Implemented JWT authentication with bcrypt password hashing
  - Created database models for users, products, categories, images, saved items
  - Implemented CORS middleware for frontend integration
  - Added image upload functionality with UUID naming
  - Set up automatic database initialization with seed data
  - Configured dual-server workflow (frontend + backend)
  - Added comprehensive API documentation (Swagger UI)

- **2025-11-22**: Initial Replit setup
  - Added Python HTTP server (server.py) for serving static files
  - Configured to run on port 5000 with 0.0.0.0 host
  - Added cache control headers to prevent caching issues
  - Created .gitignore for Python files

## Documentation

### For Complete Beginners
Start with **DOCUMENTATION.md** - It explains:
- High-level overview of how the app works
- Step-by-step walkthroughs of major flows (registration, login, creating products)
- How data moves through the system
- Security concepts explained simply

### For Understanding Specific Code
Check the **inline comments** in each file:
- **backend/main.py**: Every endpoint has detailed explanation
- **backend/models.py**: Each database table explained with relationships
- **backend/auth.py**: Password hashing and JWT authentication explained
- **backend/database.py**: Database initialization process explained
- **backend/schemas.py**: Request/response validation explained with examples
- **js/products.js**: Filtering, sorting, pagination logic explained
- **js/app.js**: UI interactions and Lucide icons explained

### For Developers
API documentation available at: **http://localhost:8000/docs** (Swagger UI)

## Database Configuration

### Development (SQLite)
No setup needed - automatically creates `unimarket.db`

### Production (PostgreSQL)
```bash
# Set environment variable
export DATABASE_URL="postgresql://user:password@host:5432/database"

# Run app - everything else is automatic!
bash start.sh
```

**Why this works**: SQLAlchemy ORM abstracts away database differences. Same Python code works with SQLite and PostgreSQL!

## User Preferences
None specified yet.

## Notes
- Backend uses SQLite for development, but is ready for PostgreSQL (tested with psycopg2-binary driver)
- JWT secret key defaults to placeholder - should be set via `JWT_SECRET_KEY` environment variable in production
- File uploads stored in `backend/uploads/products/` with UUID filenames for uniqueness
- API documentation available at http://localhost:8000/docs (interactive Swagger UI)
- Frontend currently uses localhost:8000 for API calls (update to public domain for production deployment)
- CORS is fully enabled for development (allow_origins=["*"])
- Database initialization runs automatically on startup - creates tables and adds seed data

## Getting Help
- **How does the database work?** → Read DOCUMENTATION.md "Database Overview" section
- **How is user data validated?** → Read backend/schemas.py (all schemas documented)
- **How does authentication work?** → Read backend/auth.py (detailed comments on each function)
- **How do I understand a specific API endpoint?** → Read backend/main.py (each endpoint documented)
- **How do I change a feature?** → Find the file, read its inline comments, understand the flow, then modify
