function toggleProfileMenu() {
    const dropdown = document.getElementById('profileDropdown');
    dropdown.classList.toggle('show');
}

// Close dropdown when clicking outside
document.addEventListener('click', function(event) {
    const dropdown = document.getElementById('profileDropdown');
    const button = event.target.closest('.profile-button');
    
    if (!button && dropdown.classList.contains('show')) {
        dropdown.classList.remove('show');
    }
}); 