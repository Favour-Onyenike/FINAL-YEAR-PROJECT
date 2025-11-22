/**
 * PRODUCTS PAGE SCRIPT
 * ====================
 * This script handles product listing, filtering, sorting, and pagination.
 * 
 * WHAT IT DOES:
 * - Load products from API
 * - Filter by category, price, condition
 * - Sort by newest, price (asc/desc)
 * - Display products in grid
 * - Handle pagination (page numbers)
 * - Save/bookmark products
 * 
 * HOW IT WORKS:
 * 1. Page loads → fetchProducts() to get initial products
 * 2. User changes filter → fetchProducts() called again
 * 3. Backend returns filtered products
 * 4. displayProducts() renders them to page
 */

// =============================================================================
// API CONFIGURATION
// =============================================================================
/**
 * API_URL determines where to send requests
 * 
 * Works in both development (localhost) and production (Replit/custom domain):
 * - Uses the same hostname as the current page
 * - Always connects to port 8000
 * - Works with: localhost, Replit domains, custom domains
 * 
 * WHY THIS APPROACH:
 * - No hardcoded hostnames
 * - Works everywhere without configuration
 * - Frontend and backend use same domain, different ports
 */
const API_URL = `${window.location.protocol}//${window.location.hostname}:8000/api`;

// =============================================================================
// CURRENT FILTER STATE
// =============================================================================
/**
 * Stores the current filter and sort values
 * Updated when user changes filters
 * Sent to API to fetch matching products
 */
let currentFilters = {
    category: '',          // Selected category name (empty = all)
    minPrice: 0,          // Minimum price filter
    maxPrice: 1000,       // Maximum price filter
    condition: '',        // Selected condition (empty = all)
    sortBy: 'newest',     // Sort: newest, price-asc, price-desc
    page: 1,              // Current page number
    limit: 20,            // Results per page
    // Clothing-specific filters (for category = "Clothing")
    sizes: [],            // Array of selected sizes (XS, S, M, L, XL)
    colors: [],           // Array of selected colors (Red, Blue, Black, White)
    subCategories: []     // Array of selected clothing types (Shirts, Trousers, Dresses, Skirts)
};

// =============================================================================
// FETCH PRODUCTS FROM API
// =============================================================================
/**
 * Fetch products from backend API with current filters
 * 
 * FLOW:
 * 1. Build query string from currentFilters
 * 2. Skip filters that are "default" (empty, 0, etc.)
 * 3. Send GET request to API
 * 4. Get response with products and total count
 * 5. Call displayProducts() to render them
 * 6. Call updateResultsCount() to show "X of Y results"
 */
async function fetchProducts() {
    try {
        // Build query parameters
        const params = new URLSearchParams();
        
        // Add category filter if selected
        // Skip if 'all' or empty (no filter)
        if (currentFilters.category && currentFilters.category !== 'all') {
            params.append('category', currentFilters.category);
        }
        
        // Add minimum price filter if greater than 0
        if (currentFilters.minPrice > 0) {
            params.append('minPrice', currentFilters.minPrice);
        }
        
        // Add maximum price filter if less than max
        if (currentFilters.maxPrice < 1000) {
            params.append('maxPrice', currentFilters.maxPrice);
        }
        
        // Add condition filter if selected
        // Skip if 'all' or empty (no filter)
        if (currentFilters.condition && currentFilters.condition !== 'all') {
            params.append('condition', currentFilters.condition);
        }
        
        // Add clothing-specific filters if Clothing is selected
        if (currentFilters.category === 'Clothing') {
            // Add sizes if any selected (comma-separated)
            if (currentFilters.sizes.length > 0) {
                params.append('sizes', currentFilters.sizes.join(','));
            }
            
            // Add colors if any selected (comma-separated)
            if (currentFilters.colors.length > 0) {
                params.append('colors', currentFilters.colors.join(','));
            }
            
            // Add sub-categories if any selected (comma-separated)
            if (currentFilters.subCategories.length > 0) {
                params.append('subCategories', currentFilters.subCategories.join(','));
            }
        }
        
        // Add sorting method
        params.append('sortBy', currentFilters.sortBy);
        
        // Add pagination
        params.append('page', currentFilters.page);
        params.append('limit', currentFilters.limit);
        
        // Make API request with all filters
        const response = await fetch(`${API_URL}/products?${params.toString()}`);
        const data = await response.json();
        
        // Display the products on the page
        displayProducts(data.products);
        
        // Update the "Showing X-Y of Z results" text
        updateResultsCount(data.totalResults, data.page, data.limit);
        
    } catch (error) {
        console.error('Error fetching products:', error);
        displayError();
    }
}

// =============================================================================
// DISPLAY PRODUCTS
// =============================================================================
/**
 * Render products to the page
 * 
 * WHAT IT DOES:
 * 1. Get the product grid container
 * 2. For each product: Create HTML card
 * 3. Include image, name, price, category, location, condition
 * 4. Add save button to each product
 * 5. Insert all HTML into the page
 * 6. Re-initialize Lucide icons (they need to be created after HTML changes)
 */
function displayProducts(products) {
    const productGrid = document.querySelector('.product-grid');
    
    // Handle empty results
    if (products.length === 0) {
        productGrid.innerHTML = `
            <div style="grid-column: 1 / -1; text-align: center; padding: 3rem;">
                <i data-lucide="package" style="width: 4rem; height: 4rem; margin: 0 auto 1rem; opacity: 0.5;"></i>
                <h3 style="font-size: 1.5rem; margin-bottom: 0.5rem;">No products found</h3>
                <p style="color: var(--muted); margin-bottom: 1.5rem;">Try adjusting your filters</p>
                <a href="products.html" class="btn btn-primary">View All Products</a>
            </div>
        `;
        lucide.createIcons();
        return;
    }
    
    // Create HTML for each product
    productGrid.innerHTML = products.map(product => `
        <a href="product-detail.html?id=${product.id}" class="product-card">
            <!-- Product Image -->
            <div class="product-image-container">
                <img src="${product.images[0]?.imageUrl || 'https://images.unsplash.com/photo-1544947950-fa07a98d237f?q=80&w=800'}" 
                     alt="${product.name}" 
                     class="product-image">
                
                <!-- Save Button -->
                <!-- onclick="event.preventDefault()" prevents following the link when clicking button -->
                <button class="product-save-btn" onclick="event.preventDefault(); toggleSave(${product.id})">
                    <i data-lucide="bookmark" style="width: 1.25rem;"></i>
                </button>
            </div>
            
            <!-- Product Info -->
            <div class="product-info">
                <h3 class="product-name">${product.name}</h3>
                <span class="product-price">₦${product.price.toFixed(2)}</span>
                
                <!-- Category & Location -->
                <div class="product-meta">
                    <span class="meta-item">
                        <i data-lucide="tag" style="width: 1rem;"></i> 
                        ${product.category.name}
                    </span>
                    ${product.location ? `
                        <span class="meta-item">
                            <i data-lucide="map-pin" style="width: 1rem;"></i> 
                            ${product.location}
                        </span>
                    ` : ''}
                </div>
                
                <!-- Condition Badge -->
                ${product.condition ? `
                    <div style="margin-top: 0.5rem;">
                        <span style="font-size: 0.75rem; padding: 0.25rem 0.5rem; background: var(--secondary); border-radius: 0.25rem;">
                            ${product.condition}
                        </span>
                    </div>
                ` : ''}
            </div>
        </a>
    `).join('');
    
    // Re-initialize Lucide icons
    // They need to be created after we insert new HTML
    lucide.createIcons();
}

// =============================================================================
// ERROR DISPLAY
// =============================================================================
/**
 * Display error message when products fail to load
 */
function displayError() {
    const productGrid = document.querySelector('.product-grid');
    productGrid.innerHTML = `
        <div style="grid-column: 1 / -1; text-align: center; padding: 3rem;">
            <i data-lucide="alert-circle" style="width: 4rem; height: 4rem; margin: 0 auto 1rem; color: red; opacity: 0.5;"></i>
            <h3 style="font-size: 1.5rem; margin-bottom: 0.5rem;">Error loading products</h3>
            <p style="color: var(--muted);">Please try again later</p>
        </div>
    `;
    lucide.createIcons();
}

// =============================================================================
// UPDATE RESULTS COUNT
// =============================================================================
/**
 * Update the "Showing X-Y of Z results" text
 * Helps user understand pagination
 * 
 * CALCULATION:
 * - start = (page - 1) * limit + 1
 *   (Page 1, limit 20: start = 1)
 *   (Page 2, limit 20: start = 21)
 *   (Page 3, limit 20: start = 41)
 * 
 * - end = min(page * limit, total)
 *   (Page 1, limit 20, total 100: end = 20)
 *   (Page 2, limit 20, total 100: end = 40)
 *   (Page 3, limit 20, total 50: end = 50) // Last page might have fewer
 */
function updateResultsCount(total, page, limit) {
    const start = (page - 1) * limit + 1;
    const end = Math.min(page * limit, total);
    const countElement = document.querySelector('.products-header p');
    
    if (countElement) {
        countElement.textContent = `Showing ${start}-${end} of ${total} results`;
    }
}

// =============================================================================
// TOGGLE SAVE/BOOKMARK
// =============================================================================
/**
 * Save or unsave a product (bookmark/wishlist)
 * 
 * REQUIRES: User must be logged in (has JWT token)
 * 
 * FLOW:
 * 1. Check if user is logged in
 * 2. Send POST to /api/saved-items with productId
 * 3. Backend toggles: if saved → unsave, if not saved → save
 * 4. Update button visual state
 */
async function toggleSave(productId) {
    // Check if user is logged in
    const token = localStorage.getItem('token');
    if (!token) {
        // Not logged in, redirect to login
        alert('Please log in to save products');
        window.location.href = '/login.html';
        return;
    }
    
    try {
        // Send request to toggle save
        const response = await fetch(`${API_URL}/saved-items`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`  // Include JWT token
            },
            body: JSON.stringify({ productId })
        });
        
        const data = await response.json();
        
        // Optionally update button to show save state
        // For now, just log the result
        console.log(data.isSaved ? 'Product saved' : 'Product unsaved');
        
    } catch (error) {
        console.error('Error toggling save:', error);
    }
}

// =============================================================================
// FILTER EVENT HANDLERS
// =============================================================================
/**
 * These functions are called when user changes filters
 * They update currentFilters and call fetchProducts()
 */

function updateCategory(category) {
    currentFilters.category = category;
    currentFilters.page = 1;  // Reset to page 1
    fetchProducts();
}

function updateCondition(condition) {
    currentFilters.condition = condition;
    currentFilters.page = 1;  // Reset to page 1
    fetchProducts();
}

function updateSort(sortBy) {
    currentFilters.sortBy = sortBy;
    currentFilters.page = 1;  // Reset to page 1
    fetchProducts();
}

function updatePriceRange(min, max) {
    currentFilters.minPrice = min;
    currentFilters.maxPrice = max;
    currentFilters.page = 1;  // Reset to page 1
    fetchProducts();
}

function updateClothingFilters() {
    // Get all selected sizes
    const sizeCheckboxes = document.querySelectorAll('input[name="size"]:checked');
    currentFilters.sizes = Array.from(sizeCheckboxes).map(cb => cb.value);
    
    // Get all selected colors
    const colorCheckboxes = document.querySelectorAll('input[name="color"]:checked');
    currentFilters.colors = Array.from(colorCheckboxes).map(cb => cb.value);
    
    // Get all selected sub-categories
    const subCategoryCheckboxes = document.querySelectorAll('input[name="sub-category"]:checked');
    currentFilters.subCategories = Array.from(subCategoryCheckboxes).map(cb => cb.value);
    
    currentFilters.page = 1;  // Reset to page 1
    fetchProducts();
}

function clearAllFilters() {
    currentFilters = {
        category: '',
        minPrice: 0,
        maxPrice: 1000,
        condition: '',
        sortBy: 'newest',
        page: 1,
        limit: 20,
        sizes: [],
        colors: [],
        subCategories: []
    };
    
    // Reset UI elements
    const categorySelect = document.querySelector('#category-select');
    const conditionRadios = document.querySelectorAll('input[name="condition"]');
    const priceRange = document.querySelector('#price-range');
    const priceValue = document.querySelector('#price-value');
    
    if (categorySelect) categorySelect.value = 'all';
    if (conditionRadios) conditionRadios[0].checked = true;  // Check "Any"
    if (priceRange) priceRange.value = 500;
    if (priceValue) priceValue.textContent = '₦500';
    
    // Clear all clothing-specific checkboxes
    document.querySelectorAll('input[name="size"]').forEach(cb => cb.checked = false);
    document.querySelectorAll('input[name="color"]').forEach(cb => cb.checked = false);
    document.querySelectorAll('input[name="sub-category"]').forEach(cb => cb.checked = false);
    
    fetchProducts();
}

// =============================================================================
// INITIALIZE ON PAGE LOAD
// =============================================================================
/**
 * When products.html loads, fetch and display initial products
 */
document.addEventListener('DOMContentLoaded', () => {
    // Hide loader when products page loads
    window.addEventListener('load', () => {
        const loader = document.getElementById('loader');
        if (loader) {
            loader.classList.add('hidden');
        }
    });
    
    // Fetch products
    fetchProducts();
});
