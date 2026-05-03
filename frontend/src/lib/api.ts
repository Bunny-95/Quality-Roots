import axios, { AxiosResponse } from 'axios'

// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('organic_roots_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor to handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('organic_roots_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// API Response type
export interface ApiResponse<T = any> {
  data: T
  message?: string
  status: number
}

// Auth API
export const authApi = {
  register: (userData: {
    name: string
    email: string
    password: string
    role: string
    phone?: string
    location?: string
  }) => api.post('/auth/register', userData),

  login: (credentials: {
    email: string
    password: string
  }) => api.post('/auth/login', credentials),

  getMe: () => api.get('/auth/me'),

  logout: () => api.post('/auth/logout'),

  changePassword: (data: {
    current_password: string
    new_password: string
  }) => api.put('/auth/change-password', data),

  updateProfile: (data: {
    name?: string
    phone?: string
    location?: string
  }) => api.put('/auth/profile', data),
}

// Farmer API
export const farmerApi = {
  getDashboard: () => api.get('/farmer/dashboard'),

  createProduct: (productData: {
    name: string
    type: string
    description?: string
    origin_state: string
  }) => api.post('/farmer/products', productData),

  getProducts: () => api.get('/farmer/products'),

  createBatch: (batchData: {
    product_id: number
    quantity_kg: number
    harvest_date: string
    moisture_level: number
    color_score: number
    aroma_score: number
    defect_percentage: number
    weight_per_unit: number
  }) => api.post('/farmer/batches', batchData),

  getBatches: (skip = 0, limit = 100) => 
    api.get(`/farmer/batches?skip=${skip}&limit=${limit}`),

  getBatch: (batchId: number) => api.get(`/farmer/batches/${batchId}`),

  getDemandForecast: (productType: string) => 
    api.get(`/farmer/demand-forecast?product_type=${productType}`),

  getQualityInsights: () => api.get('/farmer/quality-insights'),

  updateBatchStatus: (batchId: number, status: string) => 
    api.put(`/farmer/batches/${batchId}/status`, { new_status: status }),
}

// Admin API
export const adminApi = {
  getDashboard: () => api.get('/admin/dashboard'),

  getSystemStats: () => api.get('/admin/stats'),

  getRecentUsers: (limit = 5) => api.get(`/admin/users/recent?limit=${limit}`),

  getRecentBatches: (limit = 10) => api.get(`/admin/batches/recent?limit=${limit}`),

  getSystemHealth: () => api.get('/admin/health'),

  getUsers: (skip = 0, limit = 100) => 
    api.get(`/admin/users?skip=${skip}&limit=${limit}`),

  getUser: (userId: number) => api.get(`/admin/users/${userId}`),

  getAllBatches: (skip = 0, limit = 100) => 
    api.get(`/admin/batches?skip=${skip}&limit=${limit}`),

  getBatch: (batchId: number) => api.get(`/admin/batches/${batchId}`),

  getFlaggedEvents: (skip = 0, limit = 50) => 
    api.get(`/admin/flagged?skip=${skip}&limit=${limit}`),

  analyzeFraud: (batchId: number) => api.post(`/admin/analyze-fraud/${batchId}`),

  getProducts: (skip = 0, limit = 100) => 
    api.get(`/admin/products?skip=${skip}&limit=${limit}`),

  getQualityAnalytics: () => api.get('/admin/quality-analytics'),

  getBlockchainStatus: () => api.get('/admin/blockchain-status'),

  getSummaryReport: () => api.get('/admin/reports/summary'),

  toggleUserStatus: (userId: number) => api.post(`/admin/users/${userId}/toggle-status`),

  getAuditLog: (skip = 0, limit = 100) => 
    api.get(`/admin/audit-log?skip=${skip}&limit=${limit}`),
}

// Consumer API
export const consumerApi = {
  verifyBatch: (batchCode: string) => api.get(`/consumer/verify/${batchCode}`),

  getBatchJourney: (batchCode: string) => api.get(`/consumer/journey/${batchCode}`),

  verifyProduct: (batchCode: string) => api.get(`/consumer/verify/${batchCode}`),

  getProductInfo: (batchCode: string) => api.get(`/consumer/product-info/${batchCode}`),

  getBatchEvents: (batchCode: string) => api.get(`/consumer/batch-events/${batchCode}`),

  verifyBlockchain: (batchCode: string) => api.get(`/consumer/blockchain-verify/${batchCode}`),

  getQualityDetails: (batchCode: string) => api.get(`/consumer/quality-details/${batchCode}`),

  searchProducts: (params: {
    query?: string
    product_type?: string
    grade?: string
    limit?: number
  }) => {
    const searchParams = new URLSearchParams()
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined) searchParams.append(key, value.toString())
    })
    return api.get(`/consumer/search?${searchParams}`)
  },

  getProductTypes: () => api.get('/consumer/product-types'),

  getGrades: () => api.get('/consumer/grades'),

  getStats: () => api.get('/consumer/stats'),
}

// Blockchain API
export const blockchainApi = {
  getChain: (limit = 50, offset = 0) => 
    api.get(`/blockchain/chain?limit=${limit}&offset=${offset}`),

  getBlock: (index: number) => api.get(`/blockchain/block/${index}`),

  searchBlock: (hash: string) => api.get(`/blockchain/search/block/${hash}`),

  searchTransaction: (hash: string) => api.get(`/blockchain/search/transaction/${hash}`),

  getBlocks: (offset = 0, limit = 20) => api.get(`/blockchain/blocks?offset=${offset}&limit=${limit}`),

  getTransactions: (offset = 0, limit = 20) => api.get(`/blockchain/transactions?offset=${offset}&limit=${limit}`),

  getTransaction: (hash: string) => api.get(`/blockchain/transaction/${hash}`),

  verifyChain: () => api.get('/blockchain/verify'),

  getStats: () => api.get('/blockchain/stats'),

  getBatchBlockchain: (batchCode: string) => api.get(`/blockchain/batch/${batchCode}`),

  searchBlockchain: (params: {
    query?: string
    event_type?: string
    limit?: number
  }) => {
    const searchParams = new URLSearchParams()
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined) searchParams.append(key, value.toString())
    })
    return api.get(`/blockchain/search?${searchParams}`)
  },

  getEvents: (params: {
    event_type?: string
    limit?: number
    offset?: number
  }) => {
    const searchParams = new URLSearchParams()
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined) searchParams.append(key, value.toString())
    })
    return api.get(`/blockchain/events?${searchParams}`)
  },

  getRecentBlocks: (limit = 10) => api.get(`/blockchain/recent?limit=${limit}`),

  getHealth: () => api.get('/blockchain/health'),
}

// AI API
export const aiApi = {
  getModelStats: () => api.get('/ai/models/stats'),

  getQualityAnalytics: () => api.get('/ai/analytics/quality'),

  getFraudAnalytics: () => api.get('/ai/analytics/fraud'),

  getDemandForecasts: () => api.get('/ai/forecasts/demand'),

  gradeQuality: (data: {
    batch_code: string
    product_type: string
    moisture_level: number
    color_score: number
    aroma_score: number
    defect_percentage: number
    weight_per_unit: number
  }) => api.post('/ai/grade-quality', data),

  detectFraud: (data: {
    transaction_id?: string
    price_per_kg: number
    quantity_kg: number
    transit_days: number
    temperature_reported: number
    location_jump_km: number
    time_since_last_event_hours: number
  }) => api.post('/ai/detect-fraud', data),

  forecastDemand: (data: {
    product_type: string
    historical_prices: number[]
    historical_demand: number[]
    season: string
  }) => api.post('/ai/forecast', data),

  getProductInsights: (productType: string) => 
    api.get(`/ai/insights/${productType}`),

  getModelsStatus: () => api.get('/ai/models/status'),

  gradeMultipleBatches: (batches: any[]) => api.post('/ai/batch-grade-multiple', { batch_requests: batches }),

  detectMultipleFraud: (transactions: any[]) => api.post('/ai/batch-detect-fraud-multiple', { transaction_requests: transactions }),

  getFeatureImportance: () => api.get('/ai/quality/feature-importance'),
}

// Supply Chain API
export const supplyApi = {
  addEvent: (data: {
    batch_id: number
    event_type: string
    actor_name: string
    actor_role: string
    location: string
    notes?: string
  }) => api.post('/supply/event', data),

  getBatchTimeline: (batchCode: string) => api.get(`/supply/batch/${batchCode}`),

  getEvents: (params: {
    batch_id?: number
    event_type?: string
    actor_role?: string
    is_flagged?: boolean
    skip?: number
    limit?: number
  }) => {
    const searchParams = new URLSearchParams()
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined) searchParams.append(key, value.toString())
    })
    return api.get(`/supply/events?${searchParams}`)
  },

  getEvent: (eventId: number) => api.get(`/supply/event/${eventId}`),

  updateEvent: (eventId: number, data: {
    notes?: string
    location?: string
  }) => api.put(`/supply/event/${eventId}`, data),

  getStats: () => api.get('/supply/stats'),

  getFlaggedEvents: (skip = 0, limit = 50) => 
    api.get(`/supply/flagged-events?skip=${skip}&limit=${limit}`),

  addBatchEvent: (batchId: number, data: {
    event_type: string
    actor_name: string
    actor_role: string
    location: string
    notes?: string
  }) => api.post(`/supply/batch/${batchId}/event`, data),

  getEventTypes: () => api.get('/supply/event-types'),

  getActorRoles: () => api.get('/supply/actor-roles'),
}

export default api
