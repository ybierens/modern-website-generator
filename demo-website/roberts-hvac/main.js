console.log('🚀 Starting application...');

import React from 'https://esm.sh/react@18.2.0';
console.log('✅ React loaded');

import ReactDOM from 'https://esm.sh/react-dom@18.2.0/client';
console.log('✅ ReactDOM loaded');

import { App } from './app.js';
console.log('✅ App component loaded');

// Fetch data.json and render the app
async function init() {
  try {
    console.log('📡 Fetching data.json...');
    const response = await fetch('./data.json');
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    console.log('✅ Data loaded:', data);
    
    console.log('🎨 Creating React root...');
    const root = ReactDOM.createRoot(document.getElementById('root'));
    
    console.log('🎨 Rendering app...');
    root.render(React.createElement(App, { data }));
    
    console.log('✅ App rendered successfully!');
  } catch (error) {
    console.error('❌ Error loading application:', error);
    document.getElementById('root').innerHTML = `
      <div style="padding: 40px; text-align: center; font-family: sans-serif;">
        <h1 style="color: #ef4444;">Error Loading Application</h1>
        <p style="color: #64748b; margin: 20px 0;">Something went wrong while loading the website.</p>
        <pre style="background: #f1f5f9; padding: 20px; border-radius: 8px; text-align: left; overflow: auto;">
${error.message}

${error.stack || ''}
        </pre>
        <p style="color: #64748b; margin-top: 20px;">Please check the browser console (F12) for more details.</p>
      </div>
    `;
  }
}

console.log('🎬 Initializing app...');
init();

