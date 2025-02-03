import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App'; // Import your App component
import './index.css'; // If you have a css file

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App /> {/* Render the App component */}
  </React.StrictMode>
);

// If you removed reportWebVitals, comment this line:
// reportWebVitals();