async function withdrawOffer(offerId) {
    if (!confirm('Are you sure you want to withdraw this offer?')) {
        return;
    }

    try {
        const response = await fetch(`/offers/${offerId}/withdraw`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (response.ok) {
            window.location.reload();
        } else {
            const data = await response.json();
            alert(data.detail || 'Failed to withdraw offer');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred while withdrawing the offer');
    }
}

async function acceptOffer(offerId) {
    if (!confirm('Are you sure you want to accept this offer?')) {
        return;
    }

    try {
        const response = await fetch(`/offers/${offerId}/accept`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (response.ok) {
            window.location.reload();
        } else {
            const data = await response.json();
            alert(data.detail || 'Failed to accept offer');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred while accepting the offer');
    }
}

async function rejectOffer(offerId) {
    if (!confirm('Are you sure you want to reject this offer?')) {
        return;
    }

    try {
        const response = await fetch(`/offers/${offerId}/reject`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (response.ok) {
            window.location.reload();
        } else {
            const data = await response.json();
            alert(data.detail || 'Failed to reject offer');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred while rejecting the offer');
    }
} 