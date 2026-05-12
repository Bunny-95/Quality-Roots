import React, { useState } from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '@/lib/auth'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { isValidEmail } from '@/lib/utils'

interface LoginFormData {
  email: string
  password: string
}

interface FormErrors {
  email?: string
  password?: string
  general?: string
}

export default function LoginPage() {
  const { login, isLoading } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()

  const [formData, setFormData] = useState<LoginFormData>({
    email: '',
    password: ''
  })
  
  const [errors, setErrors] = useState<FormErrors>({})
  const [isSubmitting, setIsSubmitting] = useState(false)

  // Get redirect path from location state or localStorage
  const getRedirectPath = (userRole: string) => {
    const savedPath = (location.state as any)?.from?.pathname || 
                     localStorage.getItem('redirect_after_login')
    
    // If there's a saved path, use it
    if (savedPath) return savedPath
    
    // Otherwise, redirect based on role
    switch (userRole) {
      case 'admin':
        return '/dashboard/admin'
      case 'farmer':
        return '/dashboard'
      case 'consumer':
        return '/verify'
      default:
        return '/'
    }
  }

  const validateForm = (): boolean => {
    const newErrors: FormErrors = {}

    if (!formData.email) {
      newErrors.email = 'Email is required'
    } else if (!isValidEmail(formData.email)) {
      newErrors.email = 'Please enter a valid email address'
    }

    if (!formData.password) {
      newErrors.password = 'Password is required'
    } else if (formData.password.length < 6) {
      newErrors.password = 'Password must be at least 6 characters'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
    
    // Clear error for this field when user starts typing
    if (errors[name as keyof FormErrors]) {
      setErrors(prev => ({ ...prev, [name]: undefined }))
    }
  }

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    e.stopPropagation()
    
    if (!validateForm()) {
      return
    }

    setIsSubmitting(true)
    setErrors({})

    try {
      const user = await login(formData.email, formData.password)
      
      // Get user role from returned user
      const userRole = user?.role || 'consumer'
      
      // Clear redirect path from localStorage
      localStorage.removeItem('redirect_after_login')
      
      // Navigate based on role
      const redirectPath = getRedirectPath(userRole)
      navigate(redirectPath, { replace: true })
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Login failed. Please try again.'
      setErrors({ general: message })
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-green-50 to-emerald-100 p-4">
      <div className="w-full max-w-md">
        {/* Logo and Title */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 organic-gradient rounded-full mb-4">
            <span className="text-white font-bold text-2xl">OR</span>
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Organic Roots</h1>
          <p className="text-gray-600">AI-enabled agricultural supply chain</p>
        </div>

        {/* Login Form */}
        <Card>
          <CardHeader className="text-center">
            <CardTitle className="text-2xl">Welcome Back</CardTitle>
            <CardDescription>
              Sign in to your account to continue
            </CardDescription>
          </CardHeader>
          <CardContent>
          <form 
  onSubmit={(e) => { e.preventDefault(); handleSubmit(e); }} 
  className="space-y-4"
>
              {/* Email Field */}
              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  name="email"
                  type="email"
                  placeholder="Enter your email"
                  value={formData.email}
                  onChange={handleInputChange}
                  disabled={isSubmitting}
                  className={errors.email ? 'border-red-500' : ''}
                />
                {errors.email && (
                  <p className="text-sm text-red-500">{errors.email}</p>
                )}
              </div>

              {/* Password Field */}
              <div className="space-y-2">
                <Label htmlFor="password">Password</Label>
                <Input
                  id="password"
                  name="password"
                  type="password"
                  placeholder="Enter your password"
                  value={formData.password}
                  onChange={handleInputChange}
                  disabled={isSubmitting}
                  className={errors.password ? 'border-red-500' : ''}
                />
                {errors.password && (
                  <p className="text-sm text-red-500">{errors.password}</p>
                )}
              </div>

              {/* General Error */}
              {errors.general && (
                <div className="bg-red-50 border border-red-200 rounded-md p-3">
                  <p className="text-sm text-red-600">{errors.general}</p>
                </div>
              )}

              {/* Submit Button */}
              <Button
                type="submit"
                className="w-full organic-gradient"
                disabled={isSubmitting || isLoading}
                
              >
                {isSubmitting || isLoading ? 'Signing in...' : 'Sign In'}
              </Button>
            </form>

            {/* Demo Accounts */}
            <div className="mt-6 p-4 bg-gray-50 rounded-md">
              <p className="text-sm font-medium text-gray-700 mb-2">Demo Accounts:</p>
              <div className="space-y-1 text-xs text-gray-600">
                <p><strong>Farmer:</strong> ravi.kumar@organicroots.com / farmer123</p>
                <p><strong>Admin:</strong> admin@organicroots.com / admin123</p>
                <p><strong>Consumer:</strong> Register as consumer</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Register Link */}
        <div className="text-center mt-6">
          <p className="text-gray-600">
            Don't have an account?{' '}
            <Link 
              to="/register" 
              className="font-medium text-green-600 hover:text-green-700"
            >
              Sign up
            </Link>
          </p>
        </div>

        {/* Back to Home */}
        <div className="text-center mt-4">
          <Link 
            to="/" 
            className="text-sm text-gray-500 hover:text-gray-700"
          >
            ← Back to Home
          </Link>
        </div>
      </div>
    </div>
  )
}
