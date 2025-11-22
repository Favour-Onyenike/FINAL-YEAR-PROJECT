const API_URL = window.location.hostname === 'localhost' 
    ? 'http://localhost:8000/api' 
    : `${window.location.protocol}//${window.location.hostname}:8000/api`;

let currentFilters = {
    category: '',
    minPrice: 0,
    maxPrice: 1000,
    condition: '',
    sortBy: 'newest',
    page: 1,
    limit: 20
};

async function fetchProducts() {
    try {
        const params = new URLSearchParams();
        
        if (currentFilters.category && currentFilters.category !== 'all') {
            params.append('category', currentFilters.category);
        }
        
        if (currentFilters.minPrice > 0) {
            params.append('minPrice', currentFilters.minPrice);
        }
        
        if (currentFilters.maxPrice < 1000) {
            params.append('maxPrice', currentFilters.maxPrice);
        }
        
        if (currentFilters.condition && currentFilters.condition !== 'all') {
            params.append('condition', currentFilters.condition);
        }
        
        params.append('sortBy', currentFilters.sortBy);
        params.append('page', currentFilters.page);
        params.append('limit', currentFilters.limit);
        
        const response = await fetch(`${API_URL}/products?${params.toString()}`);
        const data = await response.json();
        
        displayProducts(data.products);
        updateResultsCount(data.totalResults, data.page, data.limit);
        
    } catch (error) {
        console.error('Error fetching products:', error);
        displayError();
    }
}

function displayProducts(products) {
    const productGrid = document.querySelector('.product-grid');
    
    if (products.length === 0) {
        productGrid.innerHTML = `
            <div style="grid-column: 1 / -1; text-align: center; padding: 3rem;">
                <i data-lucide="package" style="width: 4rem; height: 4rem; margin: 0 auto 1rem; opacity: 0.5;"></i>
                <h3 style="font-size: 1.5rem; margin-bottom: 0.5rem;">No products found</h3>
                <p style="color: var(--muted);">Try adjusting your filters</p>
            </div>
        `;
        lucide.createIcons();
        return;
    }
    
    productGrid.innerHTML = products.map(product => `
        <a href="product-detail.html?id=${product.id}" class="product-card">
            <div class="product-image-container">
                <img src="${product.images[0]?.imageUrl || 'https://images.unsplash.com/photo-1544947950-fa07a98d237f?q=80&w=800'}" 
                     alt="${product.name}" 
                     class="product-image">
                <button class="product-save-btn" onclick="event.preventDefault(); toggleSave(${product.id})">
                    <i data-lucide="bookmark" style="width: 1.25rem;"></i>
                </button>
            </div>
            <div class="product-info">
                <h3 class="product-name">${product.name}</h3>
                <span class="product-price">$${product.price.toFixed(2)}</span>
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
    
    lucide.createIcons();
}

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

function updateResultsCount(total, page, limit) {
    const start = (page - 1) * limit + 1;
    const end = Math.min(page * limit, total);
    const countElement = document.querySelector('.products-header p');
    
    if (countElement) {
        countElement.textContent = `Showing ${start}-${end} of ${total} results`;
    }
}

function toggleSave(productId) {
    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = 'login.html';
        return;
    }
    
    fetch(`${API_URL}/saved-items`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ productId })
    })
    .then(response => response.json())
    .then(data => {
        console.log('Saved:', data.isSaved);
    })
    .catch(error => console.error('Error saving item:', error));
}

document.addEventListener('DOMContentLoaded', () => {
    const urlParams = new URLSearchParams(window.location.search);
    const categoryFromUrl = urlParams.get('category');
    
    const categorySelect = document.getElementById('category-select');
    if (categorySelect) {
        if (categoryFromUrl) {
            currentFilters.category = categoryFromUrl;
            const matchingOption = Array.from(categorySelect.options).find(
                opt => opt.value.toLowerCase() === categoryFromUrl.toLowerCase()
            );
            if (matchingOption) {
                categorySelect.value = matchingOption.value;
            }
        }
        
        categorySelect.addEventListener('change', (e) => {
            currentFilters.category = e.target.value === 'all' ? '' : e.target.value;
            currentFilters.page = 1;
            fetchProducts();
        });
    }
    
    const priceRange = document.getElementById('price-range');
    const priceValue = document.getElementById('price-value');
    if (priceRange && priceValue) {
        priceRange.addEventListener('input', (e) => {
            const value = parseInt(e.target.value);
            priceValue.textContent = value >= 1000 ? '$1000+' : `$${value}`;
            currentFilters.maxPrice = value;
        });
    }
    
    const conditionRadios = document.querySelectorAll('input[name="condition"]');
    conditionRadios.forEach(radio => {
        radio.addEventListener('change', (e) => {
            currentFilters.condition = e.target.value === 'all' ? '' : e.target.value;
        });
    });
    
    const sortSelect = document.querySelector('#sort-select');
    if (sortSelect) {
        sortSelect.addEventListener('change', (e) => {
            currentFilters.sortBy = e.target.value;
            currentFilters.page = 1;
            fetchProducts();
        });
    }
    
    const applyFilterBtn = document.querySelector('.filters-sidebar .btn-primary');
    if (applyFilterBtn) {
        applyFilterBtn.addEventListener('click', () => {
            currentFilters.page = 1;
            fetchProducts();
        });
    }
    
    const clearAllBtn = document.querySelector('.btn-ghost');
    if (clearAllBtn) {
        clearAllBtn.addEventListener('click', () => {
            currentFilters = {
                category: '',
                minPrice: 0,
                maxPrice: 1000,
                condition: '',
                sortBy: 'newest',
                page: 1,
                limit: 20
            };
            
            if (categorySelect) categorySelect.value = 'all';
            if (priceRange) {
                priceRange.value = 500;
                priceValue.textContent = '$500';
            }
            conditionRadios.forEach(radio => {
                radio.checked = radio.value === 'all';
            });
            if (sortSelect) sortSelect.selectedIndex = 0;
            
            fetchProducts();
        });
    }
    
    fetchProducts();
});
