# UniMarket

UniMarket is a peer-to-peer marketplace application designed specifically for university students to buy, sell, and connect safely on campus.

## Table of Contents
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Setup Instructions](#setup-instructions)
- [Usage](#usage)

## Features
- **User Authentication**: Sign up and log in pages with university selection.
- **Product Listings**: Browse products by category, price, and condition.
- **Product Details**: View detailed information about items, including images and seller location.
- **Responsive Design**: Fully responsive layout that works on desktop, tablet, and mobile devices.
- **Interactive UI**: 
  - Sticky header with shadow on scroll.
  - Mobile navigation menu.
  - Animated counters for hero statistics.
  - Image sliders and galleries.

## Technology Stack
- **HTML5**: Semantic markup for structure.
- **CSS3**: Custom styling with CSS variables for theming and responsive Flexbox/Grid layouts.
- **JavaScript (ES6+)**: Vanilla JavaScript for DOM manipulation and interactivity.
- **Lucide Icons**: Lightweight and consistent icon set.

## Project Structure
```
UniMarket/
├── css/
│   └── style.css       # Main stylesheet containing all global and component styles
├── js/
│   └── app.js          # Core JavaScript logic for UI interactions
├── img/                # Image assets (logos, placeholders, etc.)
├── index.html          # Landing page
├── login.html          # User login page
├── signup.html         # User registration page
├── products.html       # Product listing/catalog page
├── product-detail.html # Individual product view
├── profile.html        # User profile page
└── README.md           # Project documentation
```

## Setup Instructions
1. **Clone the repository** (or download the source code).
2. **Open the project**: Navigate to the project folder.
3. **Launch**: Open `index.html` in your preferred web browser (Chrome, Firefox, Edge, etc.).
   - No build step or server is required for the static version.
   - For development, using a local server (like Live Server in VS Code) is recommended to ensure all assets load correctly.

## Usage
- **Navigation**: Use the top navigation bar to switch between Home, Shop, and About pages.
- **Search**: Use the search bar in the header to find specific items.
- **Filtering**: On the Shop page, use the sidebar filters to narrow down products by category, price, or condition.
- **Authentication**: Click "Sign Up" to create an account or "Log In" to access existing accounts.

## Contributing
1. Fork the repository.
2. Create a new feature branch (`git checkout -b feature/AmazingFeature`).
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4. Push to the branch (`git push origin feature/AmazingFeature`).
5. Open a Pull Request.

## License
Distributed under the MIT License. See `LICENSE` for more information.
