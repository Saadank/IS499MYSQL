document.addEventListener('DOMContentLoaded', function() {
    const addButtons = document.querySelectorAll('.add-to-wishlist');
    
    addButtons.forEach(button => {
        button.addEventListener('click', async function() {
            const plateId = this.dataset.plateId;
            try {
                const response = await fetch(`/wishlist/add/${plateId}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });
                
                if (response.ok) {
                    alert('Added to wishlist successfully');
                } else {
                    alert('Failed to add to wishlist');
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Failed to add to wishlist');
            }
        });
    });
}); 