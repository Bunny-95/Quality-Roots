import React from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { useAuth, hasAnyRole } from '@/lib/auth'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'

interface ProtectedRouteProps {
  children: React.ReactNode
  allowedRoles?: string[]
}

function ProtectedRoute({ children, allowedRoles }: ProtectedRouteProps) {
  const { user, isLoading } = useAuth()
  const location = useLocation()

  // Show loading while checking auth
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading...</p>
        </div>
      </div>
    )
  }

  // Redirect to login if not authenticated
  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Card className="w-full max-w-md">
          <CardContent className="p-6">
            <div className="text-center">
              <h2 className="text-2xl font-bold mb-2">Authentication Required</h2>
              <p className="text-muted-foreground mb-6">
                Please log in to access this page.
              </p>
              <Button
                onClick={() => {
                  // Store the attempted location for redirect after login
                  localStorage.setItem('redirect_after_login', location.pathname)
                  window.location.replace('/login')

                }}
                className="w-full"
              >
                Go to Login
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  // Check role permissions
  if (allowedRoles && !hasAnyRole(user, allowedRoles)) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Card className="w-full max-w-md">
          <CardContent className="p-6">
            <div className="text-center">
              <h2 className="text-2xl font-bold mb-2">Access Denied</h2>
              <p className="text-muted-foreground mb-6">
                You don't have permission to access this page.
              </p>
              <Button
                onClick={() => window.history.back()}
                variant="outline"
                className="w-full"
              >
                Go Back
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  return <>{children}</>
}

export default ProtectedRoute
