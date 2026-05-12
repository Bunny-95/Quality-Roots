import { Routes, Route } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'

// Auth Provider
import { AuthProvider } from '@/lib/auth'

// Layout Components
import Layout from '@/components/Layout'

// Page Components
import LandingPage from '@/pages/LandingPage'
import LoginPage from '@/pages/auth/LoginPage'
import RegisterPage from '@/pages/auth/RegisterPage'
import FarmerDashboard from '@/pages/farmer/FarmerDashboard'
import AdminDashboard from '@/pages/admin/AdminDashboard'
import VerifyPage from '@/pages/consumer/VerifyPage'
import ExplorerPage from '@/pages/blockchain/ExplorerPage'
import AIAnalyticsPage from '@/pages/analytics/AIAnalyticsPage'

// Protected Route Component
import ProtectedRoute from '@/components/ProtectedRoute'
import DashboardRedirect from '@/components/DashboardRedirect'

function App() {
  return (
    <AuthProvider>
      <div className="min-h-screen bg-background">
        <Routes>
          {/* Public Routes */}
          <Route path="/" element={<LandingPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/dashboard/consumer" element={
            <ProtectedRoute allowedRoles={['consumer']}>
              <Layout>
                <VerifyPage />
              </Layout>
            </ProtectedRoute>
          } />
          {/* Consumer Routes (Public) */}
          <Route path="/verify" element={<VerifyPage />} />

          {/* Protected Routes */}
          <Route path="/dashboard" element={
            <ProtectedRoute allowedRoles={['farmer', 'admin']}>
              <Layout>
                <FarmerDashboard />
              </Layout>
            </ProtectedRoute>
          } />
          <Route path="/dashboard/admin" element={
            <ProtectedRoute allowedRoles={['admin']}>
              <Layout>
                <AdminDashboard />
              </Layout>
            </ProtectedRoute>
          } />
          <Route path="/dashboard/blockchain" element={
            <ProtectedRoute allowedRoles={['farmer', 'admin']}>
              <Layout>
                <ExplorerPage />
              </Layout>
            </ProtectedRoute>
          } />
          <Route path="/dashboard/analytics" element={
            <ProtectedRoute allowedRoles={['farmer', 'admin']}>
              <Layout>
                <AIAnalyticsPage />
              </Layout>
            </ProtectedRoute>
          } />
          <Route path="/select-dashboard" element={<DashboardRedirect />} />

          {/* Fallback */}
          <Route path="*" element={<LandingPage />} />
        </Routes>

        {/* Global Toast Notifications */}
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: 'hsl(var(--background))',
              color: 'hsl(var(--foreground))',
              border: '1px solid hsl(var(--border))',
            },
            success: {
              iconTheme: {
                primary: 'hsl(var(--primary))',
                secondary: 'hsl(var(--primary-foreground))',
              },
            },
            error: {
              iconTheme: {
                primary: 'hsl(var(--destructive))',
                secondary: 'hsl(var(--destructive-foreground))',
              },
            },
          }}
        />
      </div>
    </AuthProvider>
  )
}

export default App
