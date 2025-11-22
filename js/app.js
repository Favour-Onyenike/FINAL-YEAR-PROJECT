/**
 * UniMarket Global Scripts
 * Handles UI interactions, animations, and global functionality.
 */

// Initialize Lucide Icons
lucide.createIcons();

document.addEventListener('DOMContentLoaded', () => {
    /**
     * Re-initialize icons after DOM is ready
     * Ensures icons are rendered for any dynamically added elements.
     */
    lucide.createIcons();

    /* =========================================
       Mobile Menu Toggle
       ========================================= */
    // Mobile Menu Toggle
    const menuBtn = document.querySelector('.hamburger-menu');
    const mobileMenu = document.querySelector('.mobile-menu');

    if (menuBtn && mobileMenu) {
        menuBtn.addEventListener('click', () => {
            mobileMenu.classList.toggle('open');
        });
    }

    /* =========================================
       Sticky Header Shadow on Scroll
       ========================================= */
    // Sticky Header Shadow on Scroll
    const header = document.querySelector('.header');
    if (header) {
        window.addEventListener('scroll', () => {
            if (window.scrollY > 10) {
                header.style.boxShadow = '0 4px 6px -1px rgba(0, 0, 0, 0.1)';
            } else {
                header.style.boxShadow = 'none';
            }
        });
    }

    /* =========================================
       Animated Counter for Hero Stats
       ========================================= */
    /**
     * Animates a counter from 0 to a target number.
     * @param {HTMLElement} element - The element to update.
     * @param {number} target - The target number to reach.
     * @param {number} duration - The duration of the animation in milliseconds.
     */
    const animateCounter = (element, target, duration = 2000) => {
        const start = 0;
        const increment = target / (duration / 16);
        let current = start;

        const timer = setInterval(() => {
            current += increment;
            if (current >= target) {
                element.textContent = target.toLocaleString();
                clearInterval(timer);
            } else {
                element.textContent = Math.floor(current).toLocaleString();
            }
        }, 16);
    };

    // Initialize counters when hero section is visible
    const heroStats = document.querySelectorAll('.stat-number');
    if (heroStats.length > 0) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    heroStats.forEach(stat => {
                        const target = parseInt(stat.getAttribute('data-target'));
                        animateCounter(stat, target);
                    });
                    observer.disconnect();
                }
            });
        }, { threshold: 0.5 });

        const heroStatsContainer = document.querySelector('.hero-stats');
        if (heroStatsContainer) {
            observer.observe(heroStatsContainer);
        }
    }

    /* =========================================
       Save Button Toggle
       ========================================= */
    // Save Button Toggle
    document.querySelectorAll('.save-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            btn.classList.toggle('saved');

            const svg = btn.querySelector('svg');
            if (btn.classList.contains('saved')) {
                svg.setAttribute('fill', 'currentColor');
            } else {
                svg.setAttribute('fill', 'none');
            }
        });
    });

    /* =========================================
       Newsletter Form Submission
       ========================================= */
    // Newsletter Form Submission
    const newsletterForm = document.querySelector('.newsletter-form');
    if (newsletterForm) {
        const submitBtn = newsletterForm.querySelector('.btn-subscribe');
        const emailInput = newsletterForm.querySelector('.newsletter-input');

        submitBtn?.addEventListener('click', (e) => {
            e.preventDefault();
            const email = emailInput?.value;

            if (email && email.includes('@')) {
                alert('Thank you for subscribing!');
                emailInput.value = '';
            } else {
                alert('Please enter a valid email address');
            }
        });
    }

    /* =========================================
       User Authentication Check
       ========================================= */
    // Check if user is logged in (from localStorage)
    const user = localStorage.getItem('user');
    const authButtons = document.getElementById('auth-buttons');
    const userMenu = document.getElementById('user-menu');

    if (user && authButtons && userMenu) {
        authButtons.style.display = 'none';
        userMenu.style.display = 'flex';
    }

    /* =========================================
       Shop Dropdown Functionality
       ========================================= */
    // Shop Dropdown Functionality
    const dropdown = document.querySelector('.nav-dropdown');
    const trigger = document.querySelector('.nav-dropdown-trigger');
    const menu = document.querySelector('.dropdown-menu');

    if (dropdown && trigger && menu) {
        // Toggle dropdown on click
        trigger.addEventListener('click', function (e) {
            e.preventDefault();
            e.stopPropagation();
            dropdown.classList.toggle('open');
        });

        // Close dropdown when clicking an item
        menu.querySelectorAll('.dropdown-item').forEach(function (item) {
            item.addEventListener('click', function () {
                dropdown.classList.remove('open');
            });
        });

        // Close dropdown when clicking outside
        document.addEventListener('click', function (e) {
            if (!dropdown.contains(e.target)) {
                dropdown.classList.remove('open');
            }
        });

        // Close dropdown on Escape key
        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape') {
                dropdown.classList.remove('open');
            }
        });
    }
});