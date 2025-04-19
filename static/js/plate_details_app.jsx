import React, { useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';
import PlateDetails from './components/PlateDetails';

const App = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Get plate ID from URL
        const plateId = window.location.pathname.split('/').pop();
        console.log('Fetching plate details for ID:', plateId);

        // Fetch data
        const response = await fetch(`/api/plates/${plateId}`);
        console.log('Response status:', response.status);

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.detail || 'Failed to fetch plate details');
        }

        const jsonData = await response.json();
        console.log('Received data:', jsonData);

        setData(jsonData);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching plate details:', error);
        setError(error.message);
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '20px' }}>
        Loading plate details...
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ color: 'red', textAlign: 'center', padding: '20px' }}>
        Error: {error}
        <br />
        <button onClick={() => window.location.reload()}>
          Try Again
        </button>
      </div>
    );
  }

  if (!data || !data.plate) {
    return (
      <div style={{ textAlign: 'center', padding: '20px' }}>
        No plate details found.
        <br />
        <a href="/forsale" style={{ color: 'blue', textDecoration: 'underline' }}>
          Back to For Sale
        </a>
      </div>
    );
  }

  return (
    <PlateDetails 
      plate={data.plate}
      username={data.username}
    />
  );
};

// Wait for DOM to be ready
document.addEventListener('DOMContentLoaded', () => {
  console.log('DOM loaded, initializing React app');
  const container = document.getElementById('react-app');
  if (container) {
    console.log('Found react-app container, rendering app');
    const root = createRoot(container);
    root.render(<App />);
  } else {
    console.error('Could not find react-app container');
  }
}); 