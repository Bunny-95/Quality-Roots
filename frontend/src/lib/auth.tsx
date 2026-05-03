import React, { createContext, useContext, useEffect, useState } from 'react'
import { authApi } from './api'
import toast from 'react-hot-toast'

// User type
export interface User {
  id: number
  name: string
  email: string
  role: 'farmer' | 'admin' | 'consumer'
  phone?: string
  location?: string
  created_at: string
  is_active: boolean
}

// Auth context type
interface AuthContextType {
  user: User | null
  token: string | null
  isLoading: boolean
  login: (email: string, password: string) => Promise<User>
  register: (userData: {
    name: string
    email: string
    password: string
    role: string
    phone?: string
    location?: string
  }) => Promise<void>
  logout: () => void
  refreshUser: () => Promise<void>
}

// Create context
const AuthContext = createContext<AuthContextType | undefined>(undefined)

// Auth provider component
export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  // Initialize auth state
  useEffect(() => {
    const initializeAuth = async () => {
      const storedToken = localStorage.getItem('organic_roots_token')
      
      if (storedToken) {
        try {
          setToken(storedToken)
          // Verify token and get user data
          const response = await authApi.getMe()
          setUser(response.data)
        } catch (error) {
          // Token is invalid, remove it
          localStorage.removeItem('organic_roots_token')
          setToken(null)
          setUser(null)
        }
      }
      
      setIsLoading(false)
    }

    initializeAuth()
  }, [])

  // Login function
  const login = async (email: string, password: string): Promise<User> => {
    try {
      setIsLoading(true)
      const response = await authApi.login({ email, password })
      
      const { access_token, user: userData } = response.data
      
      // Store token
      localStorage.setItem('organic_roots_token', access_token)
      setToken(access_token)
      setUser(userData)
      
      toast.success(`Welcome back, ${userData.name}!`)
      return userData
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Login failed'
      toast.error(message)
      throw error
    } finally {
      setIsLoading(false)
    }
  }

  // Register function
  const register = async (userData: {
    name: string
    email: string
    password: string
    role: string
    phone?: string
    location?: string
  }) => {
    try {
      setIsLoading(true)
      const response = await authApi.register(userData)
      
      const { access_token, user: newUser } = response.data
      
      // Store token
      localStorage.setItem('organic_roots_token', access_token)
      setToken(access_token)
      setUser(newUser)
      
      toast.success(`Welcome to Organic Roots, ${newUser.name}!`)
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Registration failed'
      toast.error(message)
      throw error
    } finally {
      setIsLoading(false)
    }
  }

  // Logout function
  const logout = async () => {
    try {
      if (token) {
        await authApi.logout()
      }
    } catch (error) {
      // Even if logout fails on server, clear local state
      console.error('Logout error:', error)
    } finally {
      // Clear local state
      localStorage.removeItem('organic_roots_token')
      setToken(null)
      setUser(null)
      toast.success('Logged out successfully')
    }
  }

  // Refresh user data
  const refreshUser = async () => {
    if (!token) return
    
    try {
      const response = await authApi.getMe()
      setUser(response.data)
    } catch (error) {
      // Token might be expired
      logout()
    }
  }

  const value: AuthContextType = {
    user,
    token,
    isLoading,
    login,
    register,
    logout,
    refreshUser,
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

// Hook to use auth context
export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

// Check if user has specific role
export function hasRole(user: User | null, role: string): boolean {
  return user?.role === role
}

// Check if user has any of the specified roles
export function hasAnyRole(user: User | null, roles: string[]): boolean {
  return user ? roles.includes(user.role) : false
}
