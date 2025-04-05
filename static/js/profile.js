document.addEventListener('DOMContentLoaded', function() {
    const removeButtons = document.querySelectorAll('.remove-plate');
    
    removeButtons.forEach(button => {
        button.addEventListener('click', async function() {
            const plateId = this.dataset.plateId;
            
            if (confirm('Are you sure you want to remove this plate? This action cannot be undone.')) {
                try {
                    const response = await fetch(`/plates/${plateId}`, {
                        method: 'DELETE',
                        headers: {
                            'Content-Type': 'application/json'
                        }
                    });
                    
                    if (response.ok) {
                        // Remove the plate card from the DOM
                        const plateCard = this.closest('.plate-card');
                        plateCard.remove();
                        
                        // If no plates left, show empty message
                        const platesGrid = document.querySelector('.plates-grid');
                        if (platesGrid && platesGrid.children.length === 0) {
                            platesGrid.innerHTML = `
                                <p>You haven't listed any plates yet.</p>
                                <a href="/addlisting" class="button">Add New Plate</a>
                            `;
                        }
                    } else {
                        alert('Failed to remove plate');
                    }
                } catch (error) {
                    console.error('Error:', error);
                    alert('Failed to remove plate');
                }
            }
        });
    });
}); 