// API Configuration
// This file centralizes all API endpoint configuration

const isDevelopment = process.env.NODE_ENV === 'development';

// For Railway deployment, frontend and backend are on the same domain
// So we can use relative URLs in production
export const API_CONFIG = {
  // Backend API URL
  API_BASE_URL: process.env.REACT_APP_API_URL || 
                (isDevelopment ? 'http://localhost:8123' : ''),  // Empty string = same domain
  
  // WebSocket URL
  WS_URL: process.env.REACT_APP_WS_URL || 
          (isDevelopment 
            ? 'ws://localhost:8123/ws' 
            : `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/ws`),
};

// Export for easy access
export const { API_BASE_URL, WS_URL } = API_CONFIG;

