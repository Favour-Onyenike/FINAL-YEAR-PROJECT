/**
 * ================================================================================
 * UNIMARKET - GLOBAL JAVASCRIPT LIBRARY (app.js)
 * ================================================================================
 *
 * PURPOSE:
 * This file contains reusable JavaScript functions and utilities used across
 * ALL pages of UniMarket. Think of it as a "global library" that every page
 * loads and uses.
 *
 * WHAT THIS FILE DOES:
 * 1. Authentication Management - Token handling, login/logout
 * 2. Icon Library - Initialize Lucide SVG icons on every page
 * 3. Notification System - Real-time message badge updates
 * 4. UI Interactions - Mobile menu, header scroll effects, search
 * 5. Image Handling - Convert relative paths to backend URLs
 * 6. Helper Functions - Shared functions used across pages
 * 7. Global State - Token, user data in localStorage
 *
 * KEY FEATURES:
 * ✓ Authentication: JWT tokens, login/logout, "Remember Me"
 * ✓ Message Badges: Shows red dot (●) when you have unread messages
 * ✓ Badge Updates: Every 5 seconds + real-time via Socket.IO
 * ✓ Mobile Responsive: Touch-friendly hamburger menu
 * ✓ Image URLs: Converts /uploads/ paths to backend URLs
 * ✓ Global Search: Search from any page
 * ✓ Error Handling: Graceful error messages for API failures
 *
 * FILE STRUCTURE:
 * 1. Helper Functions (top):
 *    - getToken() - Get JWT from localStorage
 *    - getImageUrl() - Convert relative paths to backend URLs
 *    - isLoggedIn() - Check if user has valid token
 *    - requireLogin() - Redirect to login if not authenticated
 *
 * 2. Authentication Functions:
 *    - Login/Register/Logout - Handle auth state
 *    - Token storage - Save/retrieve JWT
 *    - User data - Store user profile locally
 *
 * 3. Notification System (THE MESSAGE BADGE SYSTEM):
 *    - updateMessageBadge() - Main function that:
 *      * Gets all users from backend
 *      * Checks messages with each user
 *      * Counts unread messages
 *      * Updates red dot badge on message icon
 *    - Periodic updates - Called every 5 seconds
 *    - Real-time updates - Called when Socket.IO receives message
 *    - Badge display - Shows ● (red dot) when unread > 0
 *
 * 4. UI Initialization:
 *    - Icon initialization - Convert <i data-lucide="icon"></i> to SVG icons
 *    - Event listeners - Attach click handlers to buttons
 *    - Mobile menu - Toggle hamburger menu on click
 *    - Header effects - Add shadow on scroll
 *
 * 5. Global Search:
 *    - Search bar on all pages
 *    - Type and press Enter -> Goes to products.html?search=query
 *
 * HOW IT WORKS:
 * 1. Page loads -> Loads app.js
 * 2. DOMContentLoaded event fires
 * 3. Initialize icons, menus, event listeners
 * 4. If user logged in:
 *    - Load user data from localStorage
 *    - Display user profile in navbar
 *    - Update message badge
 *    - Set 5-second timer to check for new messages
 * 5. User opens messages page:
 *    - Socket.IO connects (in messages.html)
 *    - Listens for receive_message events
 *    - Calls updateMessageBadge() when message arrives
 *
 * NOTIFICATION BADGE FLOW:
 * +------ REAL-TIME (Socket.IO) ------+
 * |                                   |
 * | Message arrives -> receive_message event -> updateMessageBadge()
 * |                                   |
 * |---- PERIODIC (5-second interval) -+
 * |                                   |
 * | Timer fires -> updateMessageBadge() -> Count unread messages
 * |                                   |
 * +--- Result: Red dot appears (●) ---+
 *
 * GLOBAL STATE (localStorage):
 * - token: JWT authentication token (expires in 7 days)
 * - userId: Your numeric user ID
 * - user: Full user object (JSON string)
 * - rememberMe: Boolean flag for "Remember Me" functionality
 *
 * SECURITY NOTES:
 * - All API calls include Authorization header with JWT
 * - Tokens expire in 7 days
 * - Never send token in URL (only in headers)
 * - Clear token on logout
 * - Check token before accessing protected pages
 *
 * COMMON FUNCTIONS:
 * - getToken() - Returns JWT or null
 * - isLoggedIn() - Boolean check
 * - updateMessageBadge() - Update notification badge
 * - getImageUrl(path) - Convert path to backend URL
 * - logout() - Clear token and redirect to home
 *
 * DEPENDENCIES:
 * - Lucide Icons (CDN) - Icon rendering
 * - Socket.IO Client (in messages.html) - Real-time messaging
 * - REST API (backend) - Data persistence
 *
 * ================================================================================
 */

// =============================================================================
// IMAGE URL HELPER - CONVERT RELATIVE PATHS TO BACKEND URLs
// =============================================================================
// In Replit, frontend is on port 5000, backend is on port 8000
// Product images and user avatars are stored on backend, so relative paths need to be converted
function getImageUrl(imagePath) {
    // If already a full URL or empty, return as-is
    if (!imagePath || imagePath.startsWith('http://') || imagePath.startsWith('https://')) {
        return imagePath;
    }
    
    // Convert relative path to backend URL
    const currentUrl = new URL(window.location.href);
    const backendUrl = new URL(currentUrl);
    backendUrl.port = '8000';
    backendUrl.pathname = imagePath;
    return backendUrl.toString();
}

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
        
        // Close mobile menu when any link is clicked
        mobileMenu.querySelectorAll('a, button').forEach(link => {
            link.addEventListener('click', () => {
                mobileMenu.classList.remove('open');
            });
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
       SHOP DROPDOWN MENU (Navigation)
       ========================================= */
    /**
     * Handle Shop dropdown that shows categories
     * Click Shop button to toggle, close when clicking outside
     */
    const navDropdownTriggers = document.querySelectorAll('.nav-dropdown-trigger');
    navDropdownTriggers.forEach(trigger => {
        trigger.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            // Find parent nav-dropdown and toggle open class
            const dropdown = trigger.closest('.nav-dropdown');
            if (dropdown) {
                dropdown.classList.toggle('open');
                // Close other nav dropdowns
                document.querySelectorAll('.nav-dropdown.open').forEach(other => {
                    if (other !== dropdown) {
                        other.classList.remove('open');
                    }
                });
            }
        });
    });

    // Close nav dropdown when clicking outside
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.nav-dropdown')) {
            document.querySelectorAll('.nav-dropdown.open').forEach(dropdown => {
                dropdown.classList.remove('open');
            });
        }
    });

    /* =========================================
       PROFILE DROPDOWN MENU
       ========================================= */
    /**
     * Handle profile dropdown that shows View Profile and Logout options
     * Click profile icon to toggle, close when clicking outside
     */
    const profileDropdownTriggers = document.querySelectorAll('.profile-dropdown-trigger');
    profileDropdownTriggers.forEach(trigger => {
        trigger.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            // Find parent dropdown and toggle open class
            const dropdown = trigger.closest('.profile-dropdown');
            if (dropdown) {
                dropdown.classList.toggle('open');
                // Close other dropdowns
                document.querySelectorAll('.profile-dropdown.open').forEach(other => {
                    if (other !== dropdown) {
                        other.classList.remove('open');
                    }
                });
            }
        });
    });

    // Close profile dropdown when clicking outside
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.profile-dropdown')) {
            document.querySelectorAll('.profile-dropdown.open').forEach(dropdown => {
                dropdown.classList.remove('open');
            });
        }
    });

    /* =========================================
       NAVBAR AUTH STATE - ICONS VS BUTTONS
       ========================================= */
    /**
     * Toggle between Login/SignUp buttons and Icons (Bell, Message, Saved, Profile)
     * When logged in: Show icon buttons, hide login/signup
     * When logged out: Show login/signup buttons, hide icons
     */
    function updateNavbarAuthState() {
        const token = localStorage.getItem('token');
        const loggedOutActions = document.getElementById('logged-out-actions');
        const loggedInActions = document.getElementById('logged-in-actions');
        const mobileLoggedOutActions = document.getElementById('mobile-logged-out-actions');
        const mobileLoggedInActions = document.getElementById('mobile-logged-in-actions');
        
        if (loggedOutActions && loggedInActions) {
            if (token) {
                // User is logged in - Show icons, hide login/signup buttons
                loggedOutActions.classList.add('hidden');
                loggedInActions.classList.remove('hidden');
            } else {
                // User is not logged in - Show login/signup buttons, hide icons
                loggedOutActions.classList.remove('hidden');
                loggedInActions.classList.add('hidden');
            }
        }
        
        // Update mobile menu auth state
        if (mobileLoggedOutActions && mobileLoggedInActions) {
            if (token) {
                // User is logged in - Show authenticated links, hide login/signup
                mobileLoggedOutActions.classList.add('hidden');
                mobileLoggedInActions.classList.remove('hidden');
            } else {
                // User is not logged in - Show login/signup buttons, hide authenticated links
                mobileLoggedOutActions.classList.remove('hidden');
                mobileLoggedInActions.classList.add('hidden');
            }
        }
    }
    
    // Update navbar auth state on page load
    updateNavbarAuthState();
    
    /* =========================================
       AUTHENTICATION STATE CHECK (Legacy)
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
    // Remove token and user data from browser storage
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    
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
 * Clear broken tokens on page load
 * If token is literally "undefined", clear it
 */
function clearBrokenToken() {
    const token = localStorage.getItem('token');
    
    // If token is literally "undefined" or "null" (broken from old code), clear it
    if (token === 'undefined' || token === 'null') {
        console.log('❌ BROKEN TOKEN DETECTED! Clearing localStorage...');
        localStorage.clear();
        
        // Only redirect if not already on login/signup
        const currentPage = window.location.pathname;
        if (!currentPage.includes('login') && !currentPage.includes('signup')) {
            window.location.href = '/login.html';
        }
    }
}

// Clear broken token when page loads
window.addEventListener('load', clearBrokenToken);

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

/* =============================================================================
   UNREAD MESSAGE BADGE - Shows notification for new messages
   ============================================================================= */
// This system displays a red dot (●) on the message icon when you have unread messages
// It works by:
// 1. Fetching all messages between you and each user
// 2. Counting how many are unread (is_read = 0)
// 3. Updating the navbar badge if count > 0
// 4. Checking every 5 seconds + when new messages arrive (Socket.IO)

/**
 * Fetch unread message count from backend and update the notification badge
 * 
 * WHAT IT DOES:
 * 1. Gets current user ID from localStorage
 * 2. Fetches all users from backend
 * 3. For each user: Gets messages and counts unread ones
 * 4. Updates the red dot (●) on message icon if count > 0
 * 
 * WHEN IT'S CALLED:
 * - On page load (DOMContentLoaded event)
 * - Every 5 seconds (periodic check)
 * - When new message arrives (Socket.IO receive_message event)
 * 
 * RETURNS: Nothing (updates DOM directly)
 * 
 * LOGIC FLOW:
 * GET /api/users -> For each user:
 *   GET /api/messages/{user_id} -> Count messages where:
 *     - is_read = 0 (unread)
 *     - receiverId = my_id (I'm the receiver)
 * Total count > 0 -> Show red dot
 * Total count = 0 -> Hide badge
 * 
 * PERFORMANCE NOTE:
 * This fetches messages for ALL users, which can be slow with many users.
 * Acceptable because:
 * - Called only every 5 seconds
 * - Users typically have < 20 conversations
 * - Backend efficiently queries database
 * 
 * ERROR HANDLING:
 * - If /api/users fails: Skip badge update (don't crash)
 * - If /api/messages/{id} fails: Continue checking other users
 * - If badge element not found: Log warning but continue
 */
async function updateMessageBadge() {
    try {
        const token = getToken();
        if (!token) {
            const badge = document.getElementById('message-badge');
            if (badge) badge.classList.add('hidden');
            return;
        }
        
        // Use the optimized endpoint to get all conversations with unread counts
        const response = await fetch('/api/conversations', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        
        if (!response.ok) return;
        
        const conversations = await response.json();
        let unreadCount = 0;
        
        // Sum up unread counts from all conversations
        for (let convo of conversations) {
            if (convo.unreadCount) {
                unreadCount += convo.unreadCount;
            }
        }
        
        // Update the badge
        const badge = document.getElementById('message-badge');
        if (badge) {
            if (unreadCount > 0) {
                badge.textContent = '●';
                badge.classList.remove('hidden');
                badge.style.fontSize = '0.5rem';
                badge.style.color = '#ef4444';
            } else {
                badge.classList.add('hidden');
                badge.style.display = 'none';
            }
        }
    } catch (error) {
        console.error('Error updating message badge:', error);
    }
}

/**
 * Initialize badge updates on page load and set periodic refresh
 * 
 * WHAT HAPPENS:
 * 1. When page loads (DOMContentLoaded)
 * 2. If user is logged in:
 *    - Call updateMessageBadge() immediately
 *    - Set interval to call it every 5 seconds
 * 
 * WHY EVERY 5 SECONDS?
 * - Balances responsiveness with server load
 * - Fast enough to feel real-time
 * - Slow enough to not overload backend
 * - Gets combined with Socket.IO for instant updates
 * 
 * COMBINED WITH SOCKET.IO:
 * - Socket.IO: Instant update when message arrives (real-time)
 * - 5-second interval: Backup in case Socket.IO is slow
 * - Both together = highly responsive notification system
 */
document.addEventListener('DOMContentLoaded', () => {
    if (isLoggedIn()) {
        // User is logged in - update badge immediately
        updateMessageBadge();
        
        // Then check for new messages every 5 seconds
        // This is a fallback to make sure we don't miss any messages
        // Even if Socket.IO is temporarily slow
        setInterval(() => {
            if (isLoggedIn()) {
                updateMessageBadge();
            }
        }, 5000);  // 5000 milliseconds = 5 seconds
    }
    
    // Global search functionality
    initializeGlobalSearch();
});

// =============================================================================
// GLOBAL SEARCH - Works from any page
// =============================================================================
/**
 * Initialize search bars on all pages
 * When user types in search bar and presses Enter or clicks search,
 * redirect to products.html with search query parameter
 */
function initializeGlobalSearch() {
    const searchBars = document.querySelectorAll('.search-bar');
    
    searchBars.forEach(searchBar => {
        const searchInput = searchBar.querySelector('input');
        const searchIcon = searchBar.querySelector('.search-icon');
        
        if (!searchInput) return;
        
        // Handle Enter key in search input
        searchInput.addEventListener('keypress', (event) => {
            if (event.key === 'Enter') {
                event.preventDefault();
                performSearch(searchInput.value);
            }
        });
        
        // Handle search icon click - toggle expand on mobile, search on desktop
        if (searchIcon) {
            searchIcon.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                
                // Check if we're on mobile
                const isMobile = window.innerWidth < 768;
                
                if (isMobile) {
                    // Toggle expand on mobile
                    if (!searchBar.classList.contains('expanded')) {
                        // Expand
                        searchBar.classList.add('expanded');
                        searchInput.focus();
                    } else {
                        // Collapse and search if there's text
                        if (searchInput.value.trim()) {
                            performSearch(searchInput.value);
                        } else {
                            searchBar.classList.remove('expanded');
                        }
                    }
                } else {
                    // On desktop, perform search immediately
                    performSearch(searchInput.value);
                }
            });
        }
        
        // Close search bar when clicking outside (mobile only)
        if (window.innerWidth < 768) {
            document.addEventListener('click', (e) => {
                if (!searchBar.contains(e.target)) {
                    searchBar.classList.remove('expanded');
                }
            });
        }
    });
}

/**
 * Check authentication and navigate to a page
 * If user is not logged in, redirect to login page
 * If logged in, navigate to the target page
 * @param {string} targetPage - The page to navigate to (e.g., 'sell.html')
 */
function checkAuthAndNavigate(targetPage) {
    const token = localStorage.getItem('token');
    const user = localStorage.getItem('user');
    
    // Check if user is authenticated
    if (!token || !user) {
        // Not logged in - redirect to login page
        window.location.href = 'login.html';
    } else {
        // Logged in - navigate to target page
        window.location.href = targetPage;
    }
}

/**
 * Perform search and redirect to products page
 * @param {string} query - Search query from user
 */
function performSearch(query) {
    // Trim whitespace
    query = query.trim();
    
    // Don't search if empty
    if (!query) return;
    
    // Redirect to products page with search parameter
    // If already on products page, just update the filter
    if (window.location.pathname.includes('products.html')) {
        // Already on products page - update search filter
        if (window.products && window.products.updateSearch) {
            window.products.updateSearch(query);
        }
    } else {
        // Navigate to products page with search query
        window.location.href = `products.html?search=${encodeURIComponent(query)}`;
    }
}
