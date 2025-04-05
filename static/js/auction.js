function updateCountdown() {
    const countdownElement = document.getElementById("countdown");
    if (!countdownElement) return;

    const endTimeElement = countdownElement.getAttribute('data-end-time');
    if (!endTimeElement) return;

    const endTime = new Date(endTimeElement).getTime();
    const now = new Date().getTime();
    const distance = endTime - now;

    if (distance < 0) {
        countdownElement.innerHTML = "Auction Ended";
        // Reload page to update status
        setTimeout(() => window.location.reload(), 1000);
        return;
    }

    const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
    const seconds = Math.floor((distance % (1000 * 60)) / 1000);

    countdownElement.innerHTML = 
        minutes.toString().padStart(2, '0') + ":" + 
        seconds.toString().padStart(2, '0');
}

// Initialize countdown if there's an active auction
document.addEventListener('DOMContentLoaded', function() {
    const countdownElement = document.getElementById("countdown");
    if (countdownElement) {
        // Update countdown every second
        setInterval(updateCountdown, 1000);
        updateCountdown(); // Initial call
    }
}); 