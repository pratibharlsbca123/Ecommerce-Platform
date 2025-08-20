let products = [
    { 
        id: 'prod-dress-001', 
        name: 'Summer Floral Dress', 
        categoryId: 'cat-dresses', 
        price: 3500.00,
        imageUrl: 'https://placehold.co/300x200/4CAF50/FFFFFF?text=Floral+Dress', // Image URL here
        attributes: { 'Style': 'A-Line', 'Material': 'Cotton', 'Length': 'Knee-length' } 
    },
    // ...other products
];

// Inside renderProducts function:
const imageUrl = product.imageUrl && isValidUrl(product.imageUrl) 
                ? product.imageUrl 
                : `https://placehold.co/100x100/CCCCCC/666666?text=No+Image`;

// ... then used in productCard.innerHTML:
`<img src="${imageUrl}" alt="${product.name || 'Product'}" class="product-image" onerror="this.onerror=null;this.src='https://placehold.co/150x100/CCCCCC/666666?text=Image+Error';">`
    if (e.target.classList.contains('edit-product-btn')) {
    const productId = e.target.dataset.id;
    const productToEdit = products.find(p => p.id === productId);
    // ... logic to populate form fields
    saveProductBtn.textContent = 'Update Product';
} else if (e.target.classList.contains('delete-product-btn')) {
    const productId = e.target.dataset.id;
    if (confirm('Are you sure you want to delete this product?')) { 
        products = products.filter(p => p.id !== productId);
        showNotification('Product deleted successfully!', 'success');
        renderProducts(filterCategorySelect.value);
    }
}