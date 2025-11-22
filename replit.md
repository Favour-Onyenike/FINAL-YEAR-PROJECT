# UniMarket - Campus Marketplace

## Overview
UniMarket is a full-stack peer-to-peer marketplace designed for university students to buy, sell, and connect safely on campus. The project consists of a static frontend (HTML/CSS/JavaScript) and a FastAPI backend with RESTful API endpoints.

## Project Type
- **Type**: Full-stack web application
- **Frontend**: Static HTML/CSS/JavaScript
- **Backend**: FastAPI (Python)
- **Database**: SQLite (development)
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
- SQLite (database)
- JWT (authentication)
- bcrypt (password hashing)

## Project Structure
```
UniMarket/
├── backend/                # Backend API
│   ├── __init__.py        # Package initializer
│   ├── main.py            # FastAPI application and routes
│   ├── models.py          # SQLAlchemy database models
│   ├── database.py        # Database connection and initialization
│   ├── auth.py            # Authentication utilities (JWT, bcrypt)
│   ├── schemas.py         # Pydantic schemas for request/response
│   └── uploads/           # File upload directory
│       └── products/      # Product images
├── css/                    # Frontend stylesheets
│   ├── style.css          # Main global styles
│   └── products.css       # Product page styles
├── js/                     # Frontend JavaScript
│   └── app.js             # Main application logic
├── img/                    # Frontend image assets
├── index.html             # Landing page
├── login.html             # Login page
├── signup.html            # Registration page
├── products.html          # Product listing page
├── product-detail.html    # Product detail page
├── profile.html           # User profile page
├── server.py              # Frontend HTTP server
├── start.sh               # Startup script (runs both servers)
├── unimarket.db           # SQLite database
└── README.md              # Original documentation
```

## Key Features

### Frontend
- Responsive design for desktop, tablet, and mobile
- User authentication pages
- Product browsing by category
- Search functionality with suggestions
- Product detail views
- User profiles
- Newsletter subscription

### Backend API
- User authentication with JWT
- User registration with university email validation
- Product CRUD operations (Create, Read, Update, Delete)
- Product filtering and search
- Image upload functionality
- Saved items (wishlist) feature
- Automatic API documentation (Swagger UI at `/docs`)

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get JWT token
- `GET /api/auth/me` - Get current user profile (requires auth)

### Products
- `GET /api/products` - List products with filtering and pagination
- `GET /api/products/{id}` - Get single product details
- `POST /api/products` - Create new product (requires auth)
- `PUT /api/products/{id}` - Update product (requires auth, owner only)
- `DELETE /api/products/{id}` - Delete product (soft delete, requires auth, owner only)

### Saved Items
- `POST /api/saved-items` - Toggle save/unsave product (requires auth)
- `GET /api/saved-items` - Get user's saved products (requires auth)

### Other
- `POST /api/upload` - Upload product image
- `GET /api/categories` - Get all product categories
- `GET /api/health` - Health check endpoint

## Development Setup
The project runs both frontend and backend servers simultaneously:
- **Frontend**: Python HTTP server on port 5000 (0.0.0.0)
- **Backend**: FastAPI/Uvicorn on port 8000 (localhost)
- Both servers start automatically via `start.sh`

## Database Schema

### Tables
- **universities**: University information and email domains
- **users**: User accounts and profiles
- **categories**: Product categories
- **products**: Product listings
- **product_images**: Product images (1-5 per product)
- **saved_items**: User wishlists

## Recent Changes
- **2025-11-22**: Backend API Implementation
  - Created FastAPI backend with all required endpoints
  - Set up SQLite database with SQLAlchemy ORM
  - Implemented JWT authentication with bcrypt password hashing
  - Created database models for users, products, categories, images, saved items
  - Implemented CORS middleware for frontend integration
  - Added image upload functionality
  - Set up automatic database initialization with seed data
  - Configured dual-server workflow (frontend + backend)
  - Added comprehensive API documentation (Swagger UI)

- **2025-11-22**: Initial Replit setup
  - Added Python HTTP server (server.py) for serving static files
  - Configured to run on port 5000 with 0.0.0.0 host
  - Added cache control headers to prevent caching issues
  - Created .gitignore for Python files

## User Preferences
None specified yet.

## Notes
- Backend uses SQLite for development (can be swapped to PostgreSQL for production)
- JWT secret key should be set via environment variable `JWT_SECRET_KEY` in production
- File uploads are stored in `backend/uploads/products/`
- API documentation available at http://localhost:8000/docs
- Frontend uses localhost:8000 for API calls (update with REPLIT_DEV_DOMAIN for deployment)
