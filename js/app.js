/**
 * UNIMARKET GLOBAL SCRIPTS
 * ========================
 * This file contains global JavaScript functions used across all pages.
 * 
 * WHAT IT DOES:
 * - Initialize Lucide Icons (SVG icons library)
 * - Mobile menu toggle (hamburger menu)
 * - Sticky header shadow on scroll
 * - Animated counter for hero statistics
 * - Navigation bar state management
 * - Logout functionality
 * 
 * HOW IT WORKS:
 * 1. Wait for page to load (DOMContentLoaded)
 * 2. Run initialization code
 * 3. Attach event listeners to interactive elements
 * 4. Handle user interactions (clicks, scrolls, etc.)
 */

// =============================================================================
// LUCIDE ICONS INITIALIZATION
// =============================================================================
// Lucide is an SVG icon library that renders icons dynamically
// We need to initialize it to convert <i data-lucide="icon-name"></i> to actual icons
lucide.createIcons();

// =============================================================================
// WAIT FOR PAGE TO LOAD
// =============================================================================
// DOMContentLoaded = All HTML is loaded (but images might still be loading)
// Good time to attach event listeners and initialize UI
document.addEventListener('DOMContentLoaded', () => {
    // Re-initialize icons after DOM is ready
    lucide.createIcons();

    /* =========================================
       MOBILE MENU TOGGLE
       ========================================= */
    /**
     * Mobile hamburger menu that shows/hides navigation
     * Only visible on small screens (see CSS media queries)
     */
    const menuBtn = document.querySelector('.mobile-menu-btn');
    const mobileMenu = document.querySelector('.mobile-menu');

    if (menuBtn && mobileMenu) {
        menuBtn.addEventListener('click', () => {
            // Toggle 'open' class to show/hide menu
            mobileMenu.classList.toggle('open');
        });
    }

    /* =========================================
       STICKY HEADER SHADOW ON SCROLL
       ========================================= */
    /**
     * When user scrolls down, add a shadow to header
     * Makes it look like header is floating above content
     * Better visual hierarchy and UX
     */
    const header = document.querySelector('.site-header');
    if (header) {
        window.addEventListener('scroll', () => {
            if (window.scrollY > 10) {
                // User scrolled down more than 10px
                header.style.boxShadow = '0 4px 6px -1px rgba(0, 0, 0, 0.1)';
            } else {
                // User at top of page
                header.style.boxShadow = 'none';
            }
        });
    }

    /* =========================================
       ANIMATED COUNTER FOR HERO STATS
       ========================================= */
    /**
     * Animate numbers counting up (e.g., 0 to 5000)
     * Used for stats like "5k+ Active Users"
     * Makes page feel more dynamic and polished
     */
    const animateCounter = (element, target, duration = 2000) => {
        /**
         * Animate a number from 0 to target over duration milliseconds
         * 
         * PARAMETERS:
         * - element: DOM element containing the number
         * - target: Number to count up to
         * - duration: How many milliseconds the animation takes
         * 
         * HOW IT WORKS:
         * 1. Calculate how much to increase each frame: target / (duration / 16ms)
         * 2. setInterval runs 16ms apart (roughly 60fps)
         * 3. Each interval, increase current by increment
         * 4. Update element text
         * 5. When current >= target, stop
         */
        const increment = target / (duration / 16);
        let current = 0;

        const timer = setInterval(() => {
            current += increment;
            if (current >= target) {
                // Animation complete
                element.textContent = target.toLocaleString();
                clearInterval(timer);
            } else {
                // Still animating
                element.textContent = Math.floor(current).toLocaleString();
            }
        }, 16);
    };

    // Find all stat numbers and animate them when visible
    const heroStats = document.querySelectorAll('.stat-number');
    if (heroStats.length > 0) {
        const heroStatsContainer = document.querySelector('.hero-stats');
        if (heroStatsContainer) {
            // IntersectionObserver triggers callback when element becomes visible
            // This prevents animating stats that user might never see
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        // Stats are now visible on screen
                        heroStats.forEach(stat => {
                            // Get target number from data attribute
                            // Example: <span class="stat-number" data-target="5000">0</span>
                            const target = parseInt(stat.getAttribute('data-target'));
                            if (target) animateCounter(stat, target);
                        });
                        // Stop observing after animation starts
                        observer.disconnect();
                    }
                });
            }, { threshold: 0.5 });  // Trigger when 50% visible
            observer.observe(heroStatsContainer);
        }
    }

    /* =========================================
       DROPDOWN MENUS
       ========================================= */
    /**
     * Handle dropdown menus in navigation
     * Click to show/hide, close when clicking outside
     */
    const dropdownToggles = document.querySelectorAll('[data-dropdown-toggle]');
    dropdownToggles.forEach(toggle => {
        toggle.addEventListener('click', (e) => {
            e.preventDefault();
            // Find the dropdown menu this toggle controls
            const dropdownId = toggle.getAttribute('data-dropdown-toggle');
            const dropdown = document.getElementById(dropdownId);
            if (dropdown) {
                dropdown.classList.toggle('show');
            }
        });
    });

    // Close dropdowns when clicking outside
    document.addEventListener('click', (e) => {
        if (!e.target.closest('[data-dropdown-toggle]') && !e.target.closest('.dropdown-menu')) {
            document.querySelectorAll('.dropdown-menu.show').forEach(menu => {
                menu.classList.remove('show');
            });
        }
    });

    /* =========================================
       AUTHENTICATION STATE CHECK
       ========================================= */
    /**
     * Check if user is logged in and update navigation
     * Show different links for logged in vs logged out users
     */
    const token = localStorage.getItem('token');
    const authLinks = document.querySelector('.auth-links');
    
    if (authLinks) {
        if (token) {
            // User is logged in
            // Show: Profile, My Products, Logout buttons
            // Hide: Login, Sign Up buttons
            authLinks.innerHTML = `
                <a href="profile.html" class="nav-link">Profile</a>
                <a href="#" class="nav-link" onclick="logout(); return false;">Logout</a>
            `;
        } else {
            // User is not logged in
            // Show: Login, Sign Up buttons
            // Hide: Profile, My Products, Logout buttons
            authLinks.innerHTML = `
                <a href="login.html" class="nav-link">Log In</a>
                <a href="signup.html" class="nav-link-primary">Sign Up</a>
            `;
        }
    }
});

/* =============================================================================
   LOGOUT FUNCTION
   ============================================================================= */
/**
 * Log out the current user and redirect to home page
 * 
 * WHAT IT DOES:
 * 1. Remove JWT token from localStorage
 * 2. Redirect to home page
 * 3. Navigation bar automatically updates because token is gone
 */
function logout() {
    // Remove token from browser storage
    localStorage.removeItem('token');
    
    // Redirect to home page
    window.location.href = '/';
}

/* =============================================================================
   UTILITY FUNCTIONS
   ============================================================================= */

/**
 * Get the JWT token from localStorage
 * Used before making authenticated API requests
 */
function getToken() {
    return localStorage.getItem('token');
}

/**
 * Check if user is logged in
 * Returns true if token exists, false otherwise
 */
function isLoggedIn() {
    return !!getToken();
}

/**
 * Check if user is logged in, redirect to login if not
 * Use at top of pages that require authentication
 */
function requireLogin() {
    if (!isLoggedIn()) {
        // User not logged in, redirect to login page
        window.location.href = '/login.html';
    }
}
