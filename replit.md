# UniMarket - Campus Marketplace

## Overview
UniMarket is a full-stack, peer-to-peer campus marketplace designed exclusively for Baze University students. It facilitates secure buying, selling, and communication using Nigerian Naira (₦). The platform offers comprehensive product management, real-time messaging, user authentication, and profile management, aiming to create a vibrant internal economy within the university.

## User Preferences
I prefer detailed explanations and clear, concise language. Please ensure all code changes are well-documented. I favor iterative development and prefer to be asked before major changes are implemented. Do not make changes to the `replit.md` file itself. Do not make changes to files in the `backend/uploads/products/` directory.

## System Architecture
UniMarket employs a client-server architecture. The frontend, built with vanilla HTML, CSS, and JavaScript, communicates with a FastAPI backend. Real-time features are handled via Socket.IO.

### UI/UX Decisions
- **Responsive Design**: Mobile-first approach using CSS media queries.
- **Styling**: Modern CSS3 with CSS variables for theming.
- **Iconography**: Lucide Icons via CDN for a lightweight solution.

### Technical Implementations
- **Frontend**: Vanilla HTML5, CSS3, JavaScript (ES6+), Socket.IO Client.
- **Backend**: Python 3.11 with FastAPI, SQLAlchemy ORM, JWT for authentication, bcrypt for password hashing, and Uvicorn as the ASGI server.
- **Real-time Messaging**: Socket.IO for instant message delivery with a REST API fallback for persistence.
- **Authentication**: Stateless JWT tokens with a 7-day expiry and university email domain validation (`@bazeuniversity.edu.ng`).
- **Image Handling**: Product and profile image uploads with compression and lazy loading.
- **Database**: SQLite for development, PostgreSQL-ready for production, managed with SQLAlchemy.

### Feature Specifications
- **User Authentication**: University-gated registration, secure password hashing, JWT-based authentication, "Remember Me" functionality.
- **User Profiles**: Avatar upload, customizable bio, username/full name management, viewable stats (listings/sales), edit-only by owner.
- **Product Management**: Create, view, edit, and delete listings with multiple images, category filtering, price/condition sorting, and soft deletes.
- **Messaging System**: Real-time Socket.IO chat, conversation list, message persistence, read status, unread notifications, and message history.
- **Saved Items (Wishlist)**: Bookmark products for later viewing, with persistence and removal options.

### System Design Choices
- **Dual Server Setup**: Frontend (static files) and Backend (FastAPI) run concurrently, orchestrated by a `start.sh` script.
- **Database Agnostic**: Designed for easy transition between SQLite (development) and PostgreSQL (production).
- **CORS Enabled**: Configured for cross-origin requests between frontend and backend.
- **Performance**: Async/await for concurrency, database indexing, connection pooling, and client-side optimizations like lazy loading.
- **Security**: JWT tokens, bcrypt hashing, SQL injection prevention via ORM, user authorization checks, and environment variable usage for secrets.

## External Dependencies
- **Database**: SQLite (development), PostgreSQL (production)
- **Real-time Communication**: Socket.IO
- **Icons**: Lucide Icons (via CDN)
- **Password Hashing**: bcrypt
- **Web Server**: Uvicorn (development), Gunicorn (production)
- **Static File Server**: Nginx (production)
- **SSL Certificates**: Let's Encrypt (production)