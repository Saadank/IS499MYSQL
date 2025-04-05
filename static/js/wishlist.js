document.addEventListener('DOMContentLoaded', function() {
    const removeButtons = document.querySelectorAll('.remove-from-wishlist');
    
    removeButtons.forEach(button => {
        button.addEventListener('click', async function() {
            const plateId = this.dataset.plateId;
            try {
                const response = await fetch(`/wishlist/remove/${plateId}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });
                
                if (response.ok) {
                    // Remove the plate card from the DOM
                    this.closest('.plate-card').remove();
                    
                    // If no plates left, show empty message
                    const platesGrid = document.querySelector('.plates-grid');
                    if (platesGrid && platesGrid.children.length === 0) {
                        platesGrid.innerHTML = '<p>Your wishlist is empty.</p>';
                    }
                } else {
                    alert('Failed to remove from wishlist');
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Failed to remove from wishlist');
            }
        });
    });
}); 