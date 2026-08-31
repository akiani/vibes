import React from 'react'
import { createRoot } from 'react-dom/client'
import App from './App.jsx'

// Pico.css is a dependency rather than a CDN link, so the app works offline.
import '@picocss/pico/css/pico.min.css'
import './app.css'

createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
)
