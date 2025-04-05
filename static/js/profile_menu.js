function toggleProfileMenu() {
    const dropdown = document.getElementById('profileDropdown');
    dropdown.classList.toggle('show');
    
    // Close dropdown when clicking outside
    document.addEventListener('click', function(event) {
        const isClickInside = document.querySelector('.profile-menu-container').contains(event.target);
        if (!isClickInside && dropdown.classList.contains('show')) {
            dropdown.classList.remove('show');
        }
    });
} 