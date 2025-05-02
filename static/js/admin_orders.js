// Admin Orders JS

window.initiateMoneyTransfer = function(orderId, plateNumber) {
    // First confirmation
    if (confirm(`Are you sure you want to mark the money as transferred for plate ${plateNumber}?`)) {
        // Second confirmation
        if (confirm(`Please confirm again that you have transferred the money to the seller. This action cannot be undone.`)) {
            document.getElementById(`transferForm${orderId}`).submit();
        }
    }
} 