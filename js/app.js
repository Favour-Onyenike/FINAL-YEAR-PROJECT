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
        // Get authentication token
        const token = getToken();
        // Get user object from localStorage (set during login)
        const userStr = localStorage.getItem('user');
        
        // If not logged in, hide badge and exit
        if (!token || !userStr) {
            const badge = document.getElementById('message-badge');
            if (badge) badge.classList.add('hidden');
            console.debug('Badge update skipped: user not logged in');
            return;
        }
        
        // Parse user object to extract our user ID
        const user = JSON.parse(userStr);
        const userId = user.id;
        
        // Verify we have a user ID
        if (!userId) {
            console.debug('No userId found in user object');
            return;
        }
        
        console.debug('Updating message badge for user:', userId);
        
        // STEP 1: Get list of all users on the platform
        const response = await fetch('/api/users', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        
        // Error handling: If we can't get users, skip badge update
        if (!response.ok) {
            console.warn('Failed to fetch users for message badge. Status:', response.status);
            return;
        }
        
        // Parse response
        const users = await response.json();
        let unreadCount = 0;  // Total count of unread messages
        
        // STEP 2: For EACH user, check messages and count unread ones
        for (let user of users) {
            // Skip checking messages with ourselves
            if (user.id === parseInt(userId)) continue;
            
            try {
                // Get all messages between me and this user
                const msgResponse = await fetch(`/api/messages/${user.id}`, {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                
                // If fetch succeeds, process messages
                if (msgResponse.ok) {
                    const messages = await msgResponse.json();
                    
                    // STEP 3: Count unread messages
                    // An unread message is:
                    // - is_read = 0 (hasn't been read yet)
                    // - receiverId = my_id (I'm the one receiving it)
                    for (let msg of messages) {
                        if (msg.isRead === 0 && msg.receiverId === parseInt(userId)) {
                            // This is an unread message addressed to me!
                            unreadCount++;
                        }
                    }
                }
            } catch (error) {
                // If this one user fails, continue checking others
                // Don't let one failure break the whole notification system
                console.debug('Error checking messages with user', user.id);
            }
        }
        
        // STEP 4: Update the notification badge on the DOM
        // The badge is a small red dot (●) on the message icon in the navbar
        const badge = document.getElementById('message-badge');
        console.log('Badge element:', badge, 'Unread count:', unreadCount);
        
        if (badge) {
            // If we have unread messages, show the red dot
            if (unreadCount > 0) {
                // Set content to red dot
                badge.textContent = '●';
                // Make it visible (remove hidden class)
                badge.classList.remove('hidden');
                // Style it to be small and red
                badge.style.fontSize = '0.5rem';
                badge.style.color = '#ef4444';  // Red color
                console.log('✅ Badge updated with unread count:', unreadCount);
            } else {
                // No unread messages - hide the badge
                badge.classList.add('hidden');
                console.log('No unread messages');
            }
        } else {
            // Badge element doesn't exist on this page
            // (OK for pages that don't have the badge, like profile page)
            console.warn('Message badge element not found on this page');
        }
    } catch (error) {
        // Catch any unexpected errors
        console.error('Error updating message badge:', error);
        // Don't crash the app if badge update fails
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
