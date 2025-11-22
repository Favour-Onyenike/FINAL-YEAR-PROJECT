# UniMarket - Campus Marketplace

## Overview
UniMarket is a static website for a peer-to-peer marketplace designed for university students to buy, sell, and connect safely on campus. The project is a pure frontend application built with HTML, CSS, and vanilla JavaScript.

## Project Type
- **Type**: Static HTML/CSS/JavaScript website
- **Framework**: None (Vanilla JS)
- **Server**: Python HTTP server for development
- **Port**: 5000 (frontend)

## Technology Stack
- HTML5
- CSS3 (custom styling with CSS variables)
- JavaScript (ES6+, vanilla)
- Lucide Icons (via CDN)

## Project Structure
```
UniMarket/
├── css/                    # Stylesheets
│   ├── style.css          # Main global styles
│   └── products.css       # Product page styles
├── js/                     # JavaScript files
│   └── app.js             # Main application logic
├── img/                    # Image assets
├── index.html             # Landing page
├── login.html             # Login page
├── signup.html            # Registration page
├── products.html          # Product listing page
├── product-detail.html    # Product detail page
├── profile.html           # User profile page
├── server.py              # Python development server
└── README.md              # Original documentation
```

## Key Features
- Responsive design for desktop, tablet, and mobile
- User authentication pages (frontend only)
- Product browsing by category
- Search functionality with suggestions
- Product detail views
- User profiles
- Newsletter subscription

## Development Setup
The project uses a Python HTTP server to serve static files on port 5000 with cache control headers disabled to ensure changes are immediately visible during development.

## Recent Changes
- **2024-11-22**: Initial Replit setup
  - Added Python HTTP server (server.py) for serving static files
  - Configured to run on port 5000 with 0.0.0.0 host
  - Added cache control headers to prevent caching issues
  - Created .gitignore for Python files
  - Set up workflow for automatic server startup

## User Preferences
None specified yet.

## Notes
- This is a frontend-only application with no backend
- User data is stored in localStorage (client-side only)
- Product data is hardcoded in JavaScript
- Uses external CDN for Lucide icons
