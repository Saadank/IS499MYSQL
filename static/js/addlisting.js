function selectListingType(type, event) {
    console.log('Selected listing type:', type);
    
    // Update hidden input
    document.getElementById('listing_type').value = type;
    
    // Update button styles
    document.querySelectorAll('.listing-type-buttons button').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
    
    // Show/hide price section
    const buyNowSection = document.getElementById('buyNowSection');
    const buyNowInput = document.getElementById('buyNowPrice');
    
    // Show Buy Now section and set focus
    buyNowSection.style.display = 'block';
    buyNowInput.value = '';
    buyNowInput.focus();
}

// Add form submission handler
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('listingForm');
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const listingType = document.getElementById('listing_type').value;
            if (!listingType) {
                alert('Please select a listing type');
                return;
            }

            const priceInput = document.getElementById('buyNowPrice');

            // Validate price
            if (!priceInput || !priceInput.value || priceInput.value <= 0) {
                alert('Please enter a valid price');
                return;
            }

            // If all validations pass, submit the form
            this.submit();
        });
    }
}); 