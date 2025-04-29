document.addEventListener('DOMContentLoaded', function() {
    const removeButtons = document.querySelectorAll('.remove-plate');
    
    removeButtons.forEach(button => {
        button.addEventListener('click', async function() {
            const plateId = this.dataset.plateId;
            
            if (confirm('Are you sure you want to remove this plate? This action cannot be undone.')) {
                try {
                    const response = await fetch(`/plates/${plateId}`, {
                        method: 'DELETE',
                        headers: {
                            'Content-Type': 'application/json'
                        }
                    });
                    
                    if (response.ok) {
                        // Remove the plate card from the DOM
                        const plateCard = this.closest('.plate-card');
                        plateCard.remove();
                        
                        // If no plates left, show empty message
                        const platesGrid = document.querySelector('.plates-grid');
                        if (platesGrid && platesGrid.children.length === 0) {
                            platesGrid.innerHTML = `
                                <p>You haven't listed any plates yet.</p>
                                <a href="/addlisting" class="button">Add New Plate</a>
                            `;
                        }
                    } else {
                        alert('Failed to remove plate');
                    }
                } catch (error) {
                    console.error('Error:', error);
                    alert('Failed to remove plate');
                }
            }
        });
    });

    // Set up event listeners for edit buttons
    const editButtons = document.querySelectorAll('.edit-button');
    editButtons.forEach(button => {
        button.addEventListener('click', function() {
            const field = this.dataset.field;
            toggleEditForm(field);
        });
    });

    // Set up event listeners for update buttons
    const updateButtons = document.querySelectorAll('.update-button');
    updateButtons.forEach(button => {
        button.addEventListener('click', function() {
            const field = this.dataset.field;
            updateProfile(field);
        });
    });

    // Set up event listeners for cancel buttons
    const cancelButtons = document.querySelectorAll('.cancel-button');
    cancelButtons.forEach(button => {
        button.addEventListener('click', function() {
            const field = this.dataset.field;
            toggleEditForm(field);
        });
    });
});

function toggleEditForm(field) {
    const form = document.getElementById(`${field}-edit-form`);
    if (form) {
        form.style.display = form.style.display === 'none' || form.style.display === '' ? 'block' : 'none';
    }
}

async function updateProfile(field) {
    const formData = new FormData();
    let endpoint = '';
    
    switch(field) {
        case 'phone':
            const newPhone = document.getElementById('new-phone').value;
            if (!newPhone) {
                alert('Please enter a phone number');
                return;
            }
            // Validate phone number format
            if (!/^\d{10}$/.test(newPhone)) {
                alert('Phone number must be exactly 10 digits');
                return;
            }
            formData.append('phone_number', newPhone);
            endpoint = '/users/update-phone';
            break;
            
        case 'iban':
            const newIban = document.getElementById('new-iban').value;
            if (!newIban) {
                alert('Please enter an IBAN');
                return;
            }
            formData.append('iban', newIban);
            endpoint = '/users/update-iban';
            break;
            
        case 'password':
            const currentPassword = document.getElementById('current-password').value;
            const newPassword = document.getElementById('new-password').value;
            const confirmPassword = document.getElementById('confirm-password').value;
            
            if (!currentPassword || !newPassword || !confirmPassword) {
                alert('Please fill in all password fields');
                return;
            }
            
            if (newPassword !== confirmPassword) {
                alert('New passwords do not match');
                return;
            }
            
            formData.append('current_password', currentPassword);
            formData.append('new_password', newPassword);
            endpoint = '/users/update-password';
            break;
    }
    
    try {
        const response = await fetch(endpoint, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok) {
            alert('Profile updated successfully');
            location.reload();
        } else {
            // Show more specific error messages
            if (data.detail === "Phone number already registered") {
                alert('This phone number is already registered by another user. Please use a different phone number.');
            } else if (data.detail === "Phone number must be exactly 10 digits") {
                alert('Phone number must be exactly 10 digits');
            } else {
                alert(data.detail || 'Failed to update profile');
            }
        }
    } catch (error) {
        alert('An error occurred while updating your profile');
        console.error(error);
    }
} 