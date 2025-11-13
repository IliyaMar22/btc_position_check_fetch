// API Configuration
// This file centralizes all API endpoint configuration

const isDevelopment = process.env.NODE_ENV === 'development';

// Use environment variables if available, otherwise use defaults
export const API_CONFIG = {
  // Backend API URL
  API_BASE_URL: process.env.REACT_APP_API_URL || 
                (isDevelopment ? 'http://localhost:8123' : 'https://your-backend-url.railway.app'),
  
  // WebSocket URL
  WS_URL: process.env.REACT_APP_WS_URL || 
          (isDevelopment ? 'ws://localhost:8123/ws' : 'wss://your-backend-url.railway.app/ws'),
};

// Export for easy access
export const { API_BASE_URL, WS_URL } = API_CONFIG;

