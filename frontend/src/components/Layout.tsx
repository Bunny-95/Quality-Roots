import React from 'react'
import { Link, Outlet, useLocation } from 'react-router-dom'
import { useAuth } from '@/lib/auth'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { getRoleColor } from '@/lib/utils'

interface LayoutProps {
  children?: React.ReactNode
}

function Layout({ children }: LayoutProps) {
  const { user, logout } = useAuth()
  const location = useLocation()

  const handleLogout = () => {
    logout()
  }

  const navLinkClass = (path: string) => {
    const active =
      path === '/dashboard'
        ? location.pathname === '/dashboard'
        : location.pathname === path || location.pathname.startsWith(path + '/')
    return `text-sm font-medium transition-colors hover:text-primary ${
      active ? 'text-primary' : 'text-muted-foreground'
    }`
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b bg-white/95 backdrop-blur supports-[backdrop-filter]:bg-white/60">
        <div className="container mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center space-x-8">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 organic-gradient rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">OR</span>
              </div>
              <Link to="/dashboard" className="text-xl font-bold organic-text hover:opacity-90">
                Organic Roots
              </Link>
            </div>
            <nav className="hidden md:flex items-center gap-6">
              {(user?.role === 'farmer' || user?.role === 'admin') && (
                <>
                  <Link to="/dashboard" className={navLinkClass('/dashboard')}>
                    Dashboard
                  </Link>
                  <Link to="/dashboard/blockchain" className={navLinkClass('/dashboard/blockchain')}>
                    Blockchain
                  </Link>
                  <Link to="/dashboard/analytics" className={navLinkClass('/dashboard/analytics')}>
                    AI Analytics
                  </Link>
                </>
              )}
              {user?.role === 'admin' && (
                <Link to="/dashboard/admin" className={navLinkClass('/dashboard/admin')}>
                  Admin
                </Link>
              )}
            </nav>
          </div>

          <div className="flex items-center space-x-4">
            {user && (
              <>
                <div className="flex items-center space-x-2">
                  <Badge className={getRoleColor(user.role)}>
                    {user.role.charAt(0).toUpperCase() + user.role.slice(1)}
                  </Badge>
                  <span className="text-sm font-medium">{user.name}</span>
                </div>
                <Button variant="outline" size="sm" onClick={handleLogout}>
                  Logout
                </Button>
              </>
            )}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-6">
        {children || <Outlet />}
      </main>

      {/* Footer */}
      <footer className="border-t bg-white/95 backdrop-blur supports-[backdrop-filter]:bg-white/60 mt-auto">
        <div className="container mx-auto px-4 py-4">
          <div className="text-center text-sm text-muted-foreground">
            © 2026 Organic Roots. AI-enabled agricultural supply chain provenance.
          </div>
        </div>
      </footer>
    </div>
  )
}

export default Layout
