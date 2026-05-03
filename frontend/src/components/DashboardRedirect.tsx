import { Navigate } from 'react-router-dom'
import { useAuth } from '@/lib/auth'

export default function DashboardRedirect() {
  const { user, isLoading } = useAuth()

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

  if (!user) {
    return <Navigate to="/login" replace />
  }

  // Redirect based on role
  switch (user.role) {
    case 'admin':
      return <Navigate to="/dashboard/admin" replace />
    case 'farmer':
      return <Navigate to="/dashboard" replace />
    case 'consumer':
      return <Navigate to="/verify" replace />
    default:
      return <Navigate to="/" replace />
  }
}
