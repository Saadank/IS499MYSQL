// Seller Control Panel JS

window.deletePlate = async function(plateId) {
    if (confirm('Are you sure you want to delete this listing?')) {
        try {
            const response = await fetch(`/plates/${plateId}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            if (response.ok) {
                // Reload the page to show updated list
                window.location.reload();
            } else {
                const error = await response.json();
                alert(error.detail || 'Failed to delete plate');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Failed to delete plate');
        }
    }
}

window.initiateOrderCompletion = function(orderId, plateNumber) {
    if (confirm(`Are you sure you want to complete the order for license plate ${plateNumber}?`)) {
        if (confirm(`Please confirm again that you have transferred the license plate ${plateNumber} to the buyer. This action cannot be undone.`)) {
            document.getElementById(`completeForm${orderId}`).submit();
        }
    }
} 