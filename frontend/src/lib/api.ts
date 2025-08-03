/**
 * API configuration and utilities
 */

// Get API base URL from environment variable or use default
const getApiBaseUrl = (): string => {
  
  // In production or dev, use the environment variable or default
  const apiUrl = import.meta.env?.VITE_API_URL as string
  console.log(`apiUrl: ${apiUrl}`)
  if (apiUrl) {
    // If we have a full URL, use it directly
    return apiUrl
  }
  // Fallback to default
  return 'http://api.trading-system.madoka/api'
}

// Create full API URL
export const createApiUrl = (endpoint: string): string => {
  const baseUrl = getApiBaseUrl()
  const cleanEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`
  
  // If baseUrl is a full URL, append the endpoint
  if (baseUrl.startsWith('http')) {
    return `${baseUrl}${cleanEndpoint}`
  }
  
  // Otherwise, treat it as a relative path
  return `${baseUrl}${cleanEndpoint}`
}

// API client with environment-aware URL handling
export const apiClient = {
  get: async (endpoint: string) => {
    const url = createApiUrl(endpoint)
    console.log('API GET request to:', url) // Debug log
    const response = await fetch(url)
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    return response.json()
  },
  
  post: async (endpoint: string, data: any) => {
    const url = createApiUrl(endpoint)
    console.log('API POST request to:', url) // Debug log
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    })
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    return response.json()
  },
} 