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

    // Edit Profile Modal logic
    const editBtn = document.getElementById('edit-profile-btn');
    const modal = document.getElementById('edit-profile-modal');
    const cancelBtn = document.getElementById('cancel-edit-profile');
    const form = document.getElementById('edit-profile-form');

    // Toggle password fields in Edit Profile modal
    const togglePasswordFields = document.getElementById('toggle-password-fields');
    const passwordFields = document.getElementById('edit-password-fields');
    if (togglePasswordFields && passwordFields) {
        togglePasswordFields.onclick = function(e) {
            e.preventDefault();
            passwordFields.style.display = passwordFields.style.display === 'block' ? 'none' : 'block';
        };
    }

    if (editBtn && modal && cancelBtn && form) {
        editBtn.onclick = function() {
            document.getElementById('edit-profile-password-section').style.display = 'block';
            document.getElementById('edit-profile-fields-section').style.display = 'none';
            document.getElementById('edit-profile-password').value = '';
            if (passwordFields) passwordFields.style.display = 'none';
            modal.classList.add('show');
        };
        cancelBtn.onclick = function() {
            modal.classList.remove('show');
        };
        // Password verification logic
        const verifyBtn = document.getElementById('verify-profile-password');
        verifyBtn.onclick = async function(e) {
            e.preventDefault();
            const password = document.getElementById('edit-profile-password').value;
            if (!password) {
                alert('Please enter your password.');
                return;
            }
            // Verify password via AJAX
            const formData = new FormData();
            formData.append('current_password', password);
            const response = await fetch('/users/verify-password', {
                method: 'POST',
                body: formData
            });
            const data = await response.json();
            if (response.ok && data.verified) {
                document.getElementById('edit-profile-password-section').style.display = 'none';
                document.getElementById('edit-profile-fields-section').style.display = 'block';
            } else {
                alert(data.detail || 'Incorrect password.');
            }
        };
        form.onsubmit = async function(e) {
            e.preventDefault();
            if (document.getElementById('edit-profile-fields-section').style.display !== 'block') return;
            const username = document.getElementById('edit-username').value;
            const email = document.getElementById('edit-email').value;
            const phone = document.getElementById('edit-phone').value;
            if (!username || !email || !phone) {
                alert('All fields are required.');
                return;
            }
            if (!/^\d{10}$/.test(phone)) {
                alert('Phone number must be exactly 10 digits');
                return;
            }
            // If password fields are visible, validate and submit password change
            if (passwordFields && passwordFields.style.display === 'block') {
                const currentPassword = document.getElementById('edit-current-password').value;
                const newPassword = document.getElementById('edit-new-password').value;
                const confirmPassword = document.getElementById('edit-confirm-password').value;
                if (!currentPassword || !newPassword || !confirmPassword) {
                    alert('Please fill in all password fields.');
                    return;
                }
                if (newPassword !== confirmPassword) {
                    alert('New passwords do not match.');
                    return;
                }
                // Submit password change
                const pwdFormData = new FormData();
                pwdFormData.append('current_password', currentPassword);
                pwdFormData.append('new_password', newPassword);
                const pwdResponse = await fetch('/users/update-password', {
                    method: 'POST',
                    body: pwdFormData
                });
                const pwdData = await pwdResponse.json();
                if (!pwdResponse.ok) {
                    alert(pwdData.detail || 'Failed to update password');
                    return;
                }
            }
            // Submit profile update
            const formData = new FormData();
            formData.append('username', username);
            formData.append('email', email);
            formData.append('phone_number', phone);
            const response = await fetch('/users/update-profile', {
                method: 'POST',
                body: formData
            });
            const data = await response.json();
            if (response.ok) {
                alert('Profile updated successfully');
                location.reload();
            } else {
                alert(data.detail || 'Failed to update profile');
            }
        };
    }

    const closeBtn = document.getElementById('close-edit-profile-modal');
    if (closeBtn) {
        closeBtn.onclick = function() {
            modal.classList.remove('show');
        };
    }

    // Change Password Modal logic
    const changePasswordBtn = document.getElementById('change-password-btn');
    const changePasswordModal = document.getElementById('change-password-modal');
    const closeChangePasswordBtn = document.getElementById('close-change-password-modal');
    const cancelChangePasswordBtn = document.getElementById('cancel-change-password');
    const changePasswordForm = document.getElementById('change-password-form');

    if (changePasswordBtn && changePasswordModal && closeChangePasswordBtn && cancelChangePasswordBtn && changePasswordForm) {
        changePasswordBtn.onclick = function() {
            changePasswordModal.classList.add('show');
        };
        closeChangePasswordBtn.onclick = function() {
            changePasswordModal.classList.remove('show');
        };
        cancelChangePasswordBtn.onclick = function() {
            changePasswordModal.classList.remove('show');
        };
        changePasswordForm.onsubmit = async function(e) {
            e.preventDefault();
            const currentPassword = document.getElementById('current-password').value;
            const newPassword = document.getElementById('new-password').value;
            const confirmPassword = document.getElementById('confirm-password').value;
            if (!currentPassword || !newPassword || !confirmPassword) {
                alert('Please fill in all fields.');
                return;
            }
            if (newPassword !== confirmPassword) {
                alert('New passwords do not match.');
                return;
            }
            const formData = new FormData();
            formData.append('current_password', currentPassword);
            formData.append('new_password', newPassword);
            const response = await fetch('/users/update-password', {
                method: 'POST',
                body: formData
            });
            const data = await response.json();
            if (response.ok) {
                alert('Password updated successfully');
                changePasswordModal.classList.remove('show');
                changePasswordForm.reset();
            } else {
                alert(data.detail || 'Failed to update password');
            }
        };
    }
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