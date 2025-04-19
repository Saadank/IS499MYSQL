function selectListingType(type, event) {
    console.log('Selected listing type:', type);
    
    // Update hidden input
    document.getElementById('listing_type').value = type;
    
    // Update button styles
    document.querySelectorAll('.listing-type-buttons button').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
    
    // Show/hide price sections
    const buyNowSection = document.getElementById('buyNowSection');
    const auctionSection = document.getElementById('auctionSection');
    const offersSection = document.getElementById('offersSection');
    const buyNowInput = document.getElementById('buyNowPrice');
    const auctionInput = document.getElementById('auctionStartPrice');
    const offersInput = document.getElementById('minimumOfferPrice');
    
    // Hide all sections first
    buyNowSection.style.display = 'none';
    auctionSection.style.display = 'none';
    offersSection.style.display = 'none';
    
    // Reset all price inputs
    buyNowInput.value = '0';
    auctionInput.value = '0';
    offersInput.value = '0';
    
    // Show selected type and set focus
    switch(type) {
        case 'buy_now':
            buyNowSection.style.display = 'block';
            buyNowInput.value = '';
            buyNowInput.focus();
            break;
        case 'auction':
            auctionSection.style.display = 'block';
            auctionInput.value = '';
            auctionInput.focus();
            break;
        case 'offers':
            offersSection.style.display = 'block';
            offersInput.value = '';
            offersInput.focus();
            break;
    }
}

// Add form submission handler
document.getElementById('listingForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const listingType = document.getElementById('listing_type').value;
    if (!listingType) {
        alert('Please select a listing type');
        return;
    }

    // Get the appropriate price input based on listing type
    let priceInput;
    switch(listingType) {
        case 'buy_now':
            priceInput = document.getElementById('buyNowPrice');
            break;
        case 'auction':
            priceInput = document.getElementById('auctionStartPrice');
            break;
        case 'offers':
            priceInput = document.getElementById('minimumOfferPrice');
            break;
    }

    // Validate price
    if (!priceInput || !priceInput.value || priceInput.value <= 0) {
        alert('Please enter a valid price');
        return;
    }

    // If all validations pass, submit the form
    this.submit();
}); 