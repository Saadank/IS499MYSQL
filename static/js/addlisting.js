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
            // Get all digit inputs
            const digit1 = form.querySelector('select[name="digit1"]').value;
            const digit2 = form.querySelector('select[name="digit2"]').value;
            const digit3 = form.querySelector('select[name="digit3"]').value;
            const digit4 = form.querySelector('select[name="digit4"]').value;
            
            // Validate first digit (must be 1-9, not 0)
            if (digit1 === '0') {
                e.preventDefault();
                alert('First digit cannot be 0');
                return;
            }
            
            // Get all non-empty digits
            const digits = [digit1, digit2, digit3, digit4].filter(d => d !== 'x' && d !== '');
            
            // Validate zeros have adjacent non-zero digits
            for (let i = 0; i < digits.length; i++) {
                if (digits[i] === '0') {
                    // Check if there's a non-zero digit before or after
                    const hasAdjacentNonZero = 
                        (i > 0 && digits[i-1] !== '0') ||  // Check digit before
                        (i < digits.length-1 && digits[i+1] !== '0');  // Check digit after
                    
                    if (!hasAdjacentNonZero) {
                        e.preventDefault();
                        alert('Each zero must have an adjacent non-zero digit');
                        return;
                    }
                }
            }
            
            // Basic validation
            const priceInput = form.querySelector('input[name="buy_now_price"]');
            if (!priceInput || !priceInput.value || priceInput.value <= 0) {
                e.preventDefault();
                alert('Please enter a valid price');
                return;
            }
        });
    }
}); 