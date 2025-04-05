function selectListingType(type) {
    console.log('Selected listing type:', type);
    
    // Update hidden input
    document.getElementById('listing_type').value = type;
    
    // Update button styles
    document.querySelectorAll('.listing-type-buttons button').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
    
    // Show/hide price sections and enable/disable inputs
    const buyNowSection = document.getElementById('buyNowSection');
    const auctionSection = document.getElementById('auctionSection');
    const offersSection = document.getElementById('offersSection');
    const buyNowInput = document.getElementById('buyNowPrice');
    const auctionInput = document.getElementById('auctionStartPrice');
    const offersInput = document.getElementById('minimumOfferPrice');
    
    // Disable and hide all sections first
    buyNowSection.style.display = 'none';
    auctionSection.style.display = 'none';
    offersSection.style.display = 'none';
    buyNowInput.disabled = true;
    auctionInput.disabled = true;
    offersInput.disabled = true;
    
    // Reset all price inputs
    buyNowInput.value = '0';
    auctionInput.value = '0';
    offersInput.value = '0';
    
    // Show and enable selected type
    switch(type) {
        case 'buy_now':
            buyNowSection.style.display = 'block';
            buyNowInput.disabled = false;
            buyNowInput.value = '';
            break;
        case 'auction':
            auctionSection.style.display = 'block';
            auctionInput.disabled = false;
            auctionInput.value = '';
            break;
        case 'offers':
            offersSection.style.display = 'block';
            offersInput.disabled = false;
            offersInput.value = '';
            break;
    }
} 