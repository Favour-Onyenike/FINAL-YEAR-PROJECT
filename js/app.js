/**
 * UniMarket Global Scripts
 * Clean version - replace your entire app.js with this
 */

// Initialize Lucide Icons
lucide.createIcons();

document.addEventListener('DOMContentLoaded', () => {
    // Re-initialize icons after DOM is ready
    lucide.createIcons();

    /* =========================================
       Mobile Menu Toggle
       ========================================= */
    const menuBtn = document.querySelector('.mobile-menu-btn');
    const mobileMenu = document.querySelector('.mobile-menu');

    if (menuBtn && mobileMenu) {
        menuBtn.addEventListener('click', () => {
            mobileMenu.classList.toggle('open');
        });
    }

    /* =========================================
       Sticky Header Shadow on Scroll
       ========================================= */
    const header = document.querySelector('.site-header');
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
    const animateCounter = (element, target, duration = 2000) => {
        const increment = target / (duration / 16);
        let current = 0;

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

    const heroStats = document.querySelectorAll('.stat-number');
    if (heroStats.length > 0) {
        const heroStatsContainer = document.querySelector('.hero-stats');
        if (heroStatsContainer) {
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        heroStats.forEach(stat => {
                            const target = parseInt(stat.getAttribute('data-target'));
                            if (target) animateCounter(stat, target);
                        });
                        observer.disconnect();
                    }
                });
            }, { threshold: 0.5 });
            observer.observe(heroStatsContainer);
        }
    }

    /* =========================================
       Save Button Toggle
       ========================================= */
    document.querySelectorAll('.save-btn, .product-save-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            btn.classList.toggle('saved');

            const svg = btn.querySelector('svg');
            if (svg) {
                if (btn.classList.contains('saved')) {
                    svg.setAttribute('fill', 'currentColor');
                } else {
                    svg.setAttribute('fill', 'none');
                }
            }
        });
    });

    /* =========================================
       Newsletter Form Submission
       ========================================= */
    const newsletterForm = document.querySelector('.newsletter-form');
    if (newsletterForm) {
        const submitBtn = newsletterForm.querySelector('.btn-subscribe');
        const emailInput = newsletterForm.querySelector('.newsletter-input');

        if (submitBtn && emailInput) {
            submitBtn.addEventListener('click', (e) => {
                e.preventDefault();
                const email = emailInput.value;

                if (email && email.includes('@')) {
                    alert('Thank you for subscribing!');
                    emailInput.value = '';
                } else {
                    alert('Please enter a valid email address');
                }
            });
        }
    }

    /* =========================================
       User Authentication Check
       ========================================= */
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
    const dropdown = document.querySelector('.nav-dropdown');
    const trigger = document.querySelector('.nav-dropdown-trigger');
    const menu = document.querySelector('.dropdown-menu');

    if (dropdown && trigger && menu) {
        trigger.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropdown.classList.toggle('open');
        });

        menu.querySelectorAll('.dropdown-item').forEach(item => {
            item.addEventListener('click', () => {
                dropdown.classList.remove('open');
            });
        });

        document.addEventListener('click', (e) => {
            if (!dropdown.contains(e.target)) {
                dropdown.classList.remove('open');
            }
        });

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                dropdown.classList.remove('open');
            }
        });
    }

    /* =========================================
       Search Bar with Suggestions
       ========================================= */
    const products = [
        { id: 1, name: "Calculus: Early Transcendentals", price: 45.00, category: "Textbooks", image: "https://images.unsplash.com/photo-1544947950-fa07a98d237f?q=80&w=200" },
        { id: 2, name: "Sony WH-1000XM4", price: 180.00, category: "Electronics", image: "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?q=80&w=200" },
        { id: 3, name: "TI-84 Plus CE", price: 85.00, category: "Electronics", image: "https://images.unsplash.com/photo-1585336261022-680e295ce3fe?q=80&w=200" },
        { id: 4, name: "LED Desk Lamp", price: 20.00, category: "Furniture", image: "https://images.unsplash.com/photo-1555685812-4b943f3e99a6?q=80&w=200" },
        { id: 5, name: "Introduction to Algorithms", price: 55.00, category: "Textbooks", image: "https://images.unsplash.com/photo-1532012197267-da84d127e765?q=80&w=200" },
        { id: 6, name: "MacBook Air M1", price: 650.00, category: "Electronics", image: "https://images.unsplash.com/photo-1517336714731-489689fd1ca4?q=80&w=200" },
        { id: 7, name: "Ergonomic Office Chair", price: 120.00, category: "Furniture", image: "https://images.unsplash.com/photo-1505843490538-5133c6c7d0e1?q=80&w=200" },
        { id: 8, name: "Psychology 101", price: 30.00, category: "Textbooks", image: "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?q=80&w=200" }
    ];

    const searchBar = document.querySelector('.search-bar');
    const searchInput = searchBar?.querySelector('input');

    if (searchBar && searchInput) {
        const suggestionsContainer = document.createElement('div');
        suggestionsContainer.className = 'search-suggestions';
        searchBar.appendChild(suggestionsContainer);

        searchInput.addEventListener('input', (e) => {
            const query = e.target.value.toLowerCase();
            suggestionsContainer.innerHTML = '';

            if (query.length < 2) {
                suggestionsContainer.classList.remove('show');
                return;
            }

            const matches = products.filter(p =>
                p.name.toLowerCase().includes(query) ||
                p.category.toLowerCase().includes(query)
            );

            if (matches.length > 0) {
                matches.forEach(product => {
                    const item = document.createElement('a');
                    item.href = `product-detail.html?id=${product.id}`;
                    item.className = 'suggestion-item';
                    item.innerHTML = `
                        <img src="${product.image}" alt="${product.name}" class="suggestion-image">
                        <div class="suggestion-info">
                            <span class="suggestion-name">${product.name}</span>
                            <span class="suggestion-price">$${product.price.toFixed(2)}</span>
                        </div>
                    `;
                    suggestionsContainer.appendChild(item);
                });
                suggestionsContainer.classList.add('show');
            } else {
                suggestionsContainer.classList.remove('show');
            }
        });

        searchInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && searchInput.value.trim() !== '') {
                e.preventDefault();
                window.location.href = `products.html?q=${encodeURIComponent(searchInput.value)}`;
                suggestionsContainer.classList.remove('show');
            }
        });

        document.addEventListener('click', (e) => {
            if (!searchBar.contains(e.target)) {
                suggestionsContainer.classList.remove('show');
            }
        });
    }
});