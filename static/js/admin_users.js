document.addEventListener('DOMContentLoaded', function() {
    // Ban/Unban functionality
    const toggleBanButtons = document.querySelectorAll('.toggle-ban-btn');
    toggleBanButtons.forEach(button => {
        button.addEventListener('click', async function() {
            const userId = this.dataset.userId;
            if (confirm('Are you sure you want to change this user\'s status?')) {
                try {
                    const response = await fetch(`/admin/users/${userId}/toggle-ban`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        }
                    });
                    
                    if (response.ok) {
                        window.location.reload();
                    } else {
                        alert('Failed to update user status');
                    }
                } catch (error) {
                    console.error('Error:', error);
                    alert('An error occurred while updating user status');
                }
            }
        });
    });

    // Delete functionality
    const deleteButtons = document.querySelectorAll('.delete-user-btn');
    deleteButtons.forEach(button => {
        button.addEventListener('click', async function() {
            const userId = this.dataset.userId;
            if (confirm('Are you sure you want to delete this user? This action cannot be undone.')) {
                try {
                    const response = await fetch(`/admin/users/${userId}/delete`, {
                        method: 'DELETE',
                        headers: {
                            'Content-Type': 'application/json'
                        }
                    });
                    
                    if (response.ok) {
                        window.location.reload();
                    } else {
                        alert('Failed to delete user');
                    }
                } catch (error) {
                    console.error('Error:', error);
                    alert('An error occurred while deleting the user');
                }
            }
        });
    });
});