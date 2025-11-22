# UniMarket - Campus Marketplace

## Overview
UniMarket is a full-stack peer-to-peer marketplace designed for university students to buy, sell, and connect safely on campus. It features a static frontend (HTML/CSS/JavaScript) and a FastAPI backend with RESTful API endpoints. The project aims to provide a secure and efficient platform for campus commerce, with robust user authentication, product management, and an intuitive user experience.

## User Preferences
None specified yet.

## System Architecture
UniMarket employs a client-server architecture with a clear separation between the static frontend and the FastAPI backend.

### UI/UX Decisions
- **Responsive Design**: The frontend is designed to be responsive across desktop, tablet, and mobile devices.
- **Styling**: Custom CSS with CSS variables is used for a consistent look and feel.
- **Icons**: Lucide Icons are utilized via CDN for a modern iconography set.
- **User Flow**: Dedicated pages for login, signup, product browsing, detail views, and user profiles ensure a guided user experience.
- **Dynamic Filtering**: Advanced, category-specific filters (e.g., clothing type, size, color) provide a refined search experience.
- **Empty States**: Clear "View All Products" links are provided when no products match filters/search.
- **Loading Indicators**: Loading spinners with custom messages are implemented on key pages to improve perceived performance.

### Technical Implementations
- **Frontend**: Built with vanilla HTML5, CSS3, and JavaScript (ES6+), ensuring high performance and maintainability.
- **Backend**: Developed using Python 3.11 and FastAPI, leveraging its speed and automatic documentation features.
- **Database**: SQLAlchemy serves as the ORM, abstracting database interactions. SQLite is used for development, with readiness for PostgreSQL in production.
- **Authentication**: JWT tokens are used for stateless authentication with a 7-day expiry. Passwords are secured using bcrypt hashing. University email validation is required for registration.
- **Product Management**: Comprehensive CRUD operations are supported, including image uploads (3-5 images required per product) with UUID naming for uniqueness. Soft deletes are implemented for products.
- **Search & Filtering**: Products can be filtered by category, price range, condition, and sorted by various criteria, with pagination support.
- **Image Optimization**: Images are compressed, and lazy loading is implemented on product images for performance.
- **Currency**: All prices are displayed in Nigerian Naira (₦).
- **Dual Server Setup**: The application runs both frontend (Python HTTP server on port 5000) and backend (FastAPI/Uvicorn on port 8000) simultaneously, managed by a `start.sh` script.

### Feature Specifications
- **User Accounts**: Registration, login, profile management, and JWT-based authentication.
- **Product Listings**: Create, view, update, and delete products; support for multiple images per product.
- **Browsing & Search**: Category-based browsing, full-text search, advanced filtering, and sorting options.
- **Saved Items**: Users can save products to a wishlist.
- **API Documentation**: Automatic Swagger UI documentation is available at `/docs` for all API endpoints.

### System Design Choices
- **Modular Structure**: The project is organized into distinct `backend/`, `css/`, `js/`, and HTML page directories for clarity.
- **Environment Agnostic Database**: SQLAlchemy allows seamless switching between SQLite (development) and PostgreSQL (production) with an environment variable.
- **Security Focus**: Emphasis on password hashing, JWT token security, email validation, and authorization checks (users can only modify their own products).
- **CORS**: Fully enabled for development to facilitate frontend-backend interaction.

## Feature Status: All Working ✅

### Profile & User Features (All Verified)
- ✅ **Profile Page**: Avatar, username, stats (Listings & Sales), bio display
- ✅ **Edit Profile**: Full name, username, bio editing, profile picture upload
- ✅ **My Listings Tab**: View user listings with bookmark/save buttons, "New Listing" button
- ✅ **Saved Items**: View bookmarked products on profile or saved-items.html page
- ✅ **Messages**: Buyer-seller chat interface with conversation list
- ✅ **Product Detail**: Full gallery with thumbnails, seller info, ratings, contact button
- ✅ **New Listing Form**: 3-5 image requirement with real-time validation feedback
- ✅ **Like Feature**: Completely removed - clean UI with save & comment only

### Recent Changes (2025-11-22)
1. **Socket.IO Real-time Chat Integration**: Implemented WebSocket support for real-time messaging
   - Installed `python-socketio` and `python-engineio` packages
   - Created `Message` database model for persistent message storage
   - Added Socket.IO event handlers: `connect`, `disconnect`, `authenticate`, `send_message`
   - Created REST API endpoints for messages: `POST /api/messages` and `GET /api/messages/{user_id}`
   - Socket.IO client library added to all 14 HTML pages via CDN
   - Backend now runs `app_with_sio` (ASGI app combining FastAPI + Socket.IO)
   - Real-time message delivery when users are online; fallback to REST API
   - Messages persist to SQLite database
   - User presence tracking via `connected_users` dictionary
   - **UI/Functionality unchanged** - All existing features remain fully functional

2. **Unread Message Badge Feature**: Added notification badge to message icon
   - Red circular badge with count display on navbar message icon
   - Pulsing animation to catch user attention
   - Shows count of unread messages (99+ if more than 99)
   - Auto-hides when all messages read
   - Works on all pages (index, products, messages, profile, etc.)
   - JavaScript function `updateMessageBadge()` refreshes on page load
   - Improved error handling - won't block app if badge update fails

3. **Messages Page Fixes & Improvements**:
   - **Added missing `/api/users` endpoint**: Allows frontend to fetch all users for conversation list
   - **Infinite loading fix**: Added 10-second timeout to prevent hang
   - **Better error handling**: Shows error message instead of "Loading..." if request fails
   - **Improved conversation loading**: Gracefully handles individual message fetch failures
   - **Fixed updateMessageBadge()**: Better error handling and logging

2. **Profile Update Functionality**: Added backend PUT endpoint (PUT /api/users/{user_id}) and GET endpoint (GET /api/users/{user_id}) for profile management
   - Full Name, Bio, and Avatar URL can now be updated
   - Changes persist to database and are immediately visible
3. **Profile Dropdown Menu**: Replaced separate logout button with a profile dropdown
   - Click profile icon to reveal dropdown menu
   - Dropdown options: "View Profile" and "Log Out"
   - Cleaner navbar with consolidated profile actions
   - Works across all pages (index, products, messages, profile, saved-items, edit-profile, sell)
4. **Removed Notification Icon**: Cleaned up desktop navbar by removing notification bell icon
   - Messages section already handles all communication needs
   - Navbar now shows: Messages, Saved Items, Profile (with dropdown)
5. **Like Feature Removal**: All heart icons removed from homepage, products, profile, and saved-items pages
6. **Image Validation**: Enforced 3-5 image minimum/maximum per product listing with live feedback
7. **UI Cleanup**: All references to likes removed for a simpler, focused interface
8. **Working Account Creation**: 
   - Signup and login forms now connected to real backend API
   - Users can create accounts with full name, email (@bazeuniversity.edu.ng), and password
   - **Password Requirements**: Minimum 6 characters, 1 uppercase letter, 1 number
   - Confirm password field with validation
   - Eye icon toggle to show/hide passwords on both forms
   - **Green loading icon** → Success checkmark or error X for visual feedback
   - Accounts are saved to SQLite database
   - JWT tokens issued and stored for authenticated sessions
   - Users can log in and access profile page
   - Auto-login after signup for seamless experience
9. **Dynamic User Profiles**:
   - Each new signup creates their own profile page with their name/username
   - Profile page loads user data from localStorage on signup
   - Users can edit their profile (name, bio) from "Edit Profile" button
   - New users start with blank bio saying "No bio yet"
   - Each user's profile is independent and shows only their data
   - Only account owners can edit their profile and view saved items
   - Other users can view profiles but see limited read-only information
10. **Profile Picture Upload**:
    - No default profile image - users must upload their own
    - Click camera icon on Edit Profile page to upload a picture
    - Instant preview of selected image before saving
    - Image automatically uploaded to backend when file selected
    - Avatar URL saved with profile changes
    - Supports all standard image formats (JPG, PNG, GIF, WebP, etc.)
    - Placeholder icons show until user uploads an image
11. **Navbar Authentication State**:
    - When logged out: Shows "Log In" and "Sign Up" buttons
    - When logged in: Shows icon buttons (Notification bell, Message, Saved bookmark, Profile)
    - Automatically updates based on JWT token presence in localStorage
    - Logout removes token and user data
12. **API Proxy**:
    - Frontend server (port 5000) now proxies /api/* requests to backend (port 8000)
    - Enables API calls from embedded Replit domain without "connection error"
    - Seamless authentication flow for signup and login

## External Dependencies
- **FastAPI**: Python web framework for building the backend API.
- **SQLAlchemy**: Python SQL toolkit and Object-Relational Mapper.
- **SQLite**: Default database for development.
- **psycopg2-binary**: PostgreSQL adapter for Python (for production database).
- **python-jose[cryptography]**: For JWT (JSON Web Token) authentication.
- **bcrypt**: For secure password hashing.
- **uvicorn**: ASGI server to run FastAPI applications.
- **python-socketio**: WebSocket support for real-time messaging via Socket.IO.
- **python-engineio**: Engine for Socket.IO communication protocol.
- **Lucide Icons**: Icon library used via CDN for frontend iconography.
- **Socket.IO Client**: JavaScript library (via CDN) for real-time client-side communication.