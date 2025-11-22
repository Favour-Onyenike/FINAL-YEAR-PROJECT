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
 * - Helper function to convert relative image paths to backend URLs
 * 
 * HOW IT WORKS:
 * 1. Wait for page to load (DOMContentLoaded)
 * 2. Run initialization code
 * 3. Attach event listeners to interactive elements
 * 4. Handle user interactions (clicks, scrolls, etc.)
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

/**
 * Fetch unread message count and update the notification badge
 * Called on page load and when new messages arrive
 */
async function updateMessageBadge() {
    try {
        const token = getToken();
        const userStr = localStorage.getItem('user');
        
        if (!token || !userStr) {
            // Hide badge if not logged in
            const badge = document.getElementById('message-badge');
            if (badge) badge.classList.add('hidden');
            console.debug('Badge update skipped: user not logged in');
            return;
        }
        
        // Parse user object to get ID
        const user = JSON.parse(userStr);
        const userId = user.id;
        
        if (!userId) {
            console.debug('No userId found in user object');
            return;
        }
        
        console.debug('Updating message badge for user:', userId);
        
        // Get all users to check for messages
        const response = await fetch('/api/users', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        
        if (!response.ok) {
            console.warn('Failed to fetch users for message badge. Status:', response.status);
            // Don't clear token - just skip badge update
            return;
        }
        
        const users = await response.json();
        let unreadCount = 0;
        
        // Check messages with each user for unread count
        for (let user of users) {
            if (user.id === parseInt(userId)) continue; // Skip current user
            
            try {
                const msgResponse = await fetch(`/api/messages/${user.id}`, {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                
                if (msgResponse.ok) {
                    const messages = await msgResponse.json();
                    // Count unread messages (is_read = 0 and we are receiver)
                    for (let msg of messages) {
                        if (msg.isRead === 0 && msg.receiverId === parseInt(userId)) {
                            unreadCount++;
                        }
                    }
                }
            } catch (error) {
                // Continue checking other users even if one fails
                console.debug('Error checking messages with user', user.id);
            }
        }
        
        // Update badge
        const badge = document.getElementById('message-badge');
        if (badge) {
            if (unreadCount > 0) {
                badge.textContent = unreadCount > 99 ? '99+' : unreadCount;
                badge.classList.remove('hidden');
            } else {
                badge.classList.add('hidden');
            }
        }
    } catch (error) {
        console.error('Error updating message badge:', error);
        // Don't block the rest of the app if badge update fails
    }
}

/**
 * Update message badge when page loads (if user is logged in)
 */
document.addEventListener('DOMContentLoaded', () => {
    if (isLoggedIn()) {
        updateMessageBadge();
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
    const searchBars = document.querySelectorAll('.search-bar input');
    
    searchBars.forEach(searchInput => {
        // Handle Enter key in search input
        searchInput.addEventListener('keypress', (event) => {
            if (event.key === 'Enter') {
                event.preventDefault();
                performSearch(searchInput.value);
            }
        });
        
        // Handle search icon click (look for parent search bar)
        const searchBar = searchInput.closest('.search-bar');
        if (searchBar) {
            const searchIcon = searchBar.querySelector('.search-icon');
            if (searchIcon) {
                searchIcon.addEventListener('click', () => {
                    performSearch(searchInput.value);
                });
            }
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
