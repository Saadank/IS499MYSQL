document.addEventListener('DOMContentLoaded', function() {
    // Wishlist button functionality
    const wishlistButton = document.querySelector('.wishlist-button button');
    if (wishlistButton) {
        wishlistButton.addEventListener('click', async function() {
            const plateId = this.dataset.plateId;
            const isInWishlist = this.textContent === '♥';
            
            try {
                const endpoint = isInWishlist ? `/wishlist/remove/${plateId}` : `/wishlist/add/${plateId}`;
                const response = await fetch(endpoint, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });
                
                if (response.ok) {
                    // Toggle heart icon
                    this.textContent = isInWishlist ? '♡' : '♥';
                    this.style.color = isInWishlist ? 'black' : 'red';
                } else {
                    const data = await response.json();
                    if (response.status === 401) {
                        // User is not logged in
                        window.location.href = '/login';
                    } else {
                        alert(data.detail || 'Failed to update wishlist');
                    }
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Failed to update wishlist');
            }
        });
    }

    // Add hover effects for grid items
    const gridItems = document.querySelectorAll('.grid-item');
    gridItems.forEach(item => {
        item.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px)';
        });
        
        item.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
}); 