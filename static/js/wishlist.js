document.addEventListener('DOMContentLoaded', function() {
    const wishlistButtons = document.querySelectorAll('.btn-wishlist');
    
    wishlistButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const productId = this.dataset.productId;
            
            fetch(`/add_to_wishlist/${productId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                },
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    this.classList.toggle('in-wishlist');
                    updateWishlistCount(data.wishlist_count);
                }
            });
        });
    });
}); 