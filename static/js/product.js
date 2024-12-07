document.addEventListener('DOMContentLoaded', function() {
    // Search functionality
    document.getElementById('searchInput').addEventListener('input', function(e) {
        const searchTerm = e.target.value.toLowerCase();
        const products = document.querySelectorAll('.product-card');

        products.forEach(product => {
            const title = product.querySelector('.product-title').textContent.toLowerCase();
            const description = product.querySelector('.product-description').textContent.toLowerCase();

            if (title.includes(searchTerm) || description.includes(searchTerm)) {
                product.style.display = 'block';
            } else {
                product.style.display = 'none';
            }
        });
    });

    // Category filter
    document.getElementById('categoryFilter').addEventListener('change', function(e) {
        const category = e.target.value.toLowerCase();
        const products = document.querySelectorAll('.product-card');

        products.forEach(product => {
            if (!category || product.dataset.category.toLowerCase() === category) {
                product.style.display = 'block';
            } else {
                product.style.display = 'none';
            }
        });
    });
});
