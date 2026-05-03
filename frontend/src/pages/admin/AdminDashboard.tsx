import React, { useState, useEffect } from 'react'
import { useAuth } from '@/lib/auth'
import { adminApi } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { formatDate, formatCurrency } from '@/lib/utils'

interface SystemStats {
  total_users: number
  total_farmers: number
  total_consumers: number
  total_admins: number
  total_products: number
  total_batches: number
  active_batches: number
  total_revenue: number
  blockchain_blocks: number
  ai_predictions_today: number
  fraud_alerts_today: number
}

interface User {
  id: number
  name: string
  email: string
  role: string
  location: string
  created_at: string
  last_login?: string
  status: string
}

interface Batch {
  id: number
  batch_code: string
  product_name: string
  farmer_name: string
  quantity_kg: number
  grade: string
  status: string
  quality_score: number
  created_at: string
  blockchain_verified: boolean
  fraud_alert: boolean
}

interface SystemHealth {
  status?: string
  database?: string
  database_status?: string
  blockchain?: {
    length: number
    valid: boolean
  }
  blockchain_status?: string
  ai_models_status?: string
  api_response_time?: number
  uptime_percentage?: number
  last_backup?: string
  users_count?: number
  batches_count?: number
  flagged_events?: number
  timestamp?: string
}

export default function AdminDashboard() {
  const { user } = useAuth()
  const [stats, setStats] = useState<SystemStats | null>(null)
  const [recentUsers, setRecentUsers] = useState<User[]>([])
  const [recentBatches, setRecentBatches] = useState<Batch[]>([])
  const [systemHealth, setSystemHealth] = useState<SystemHealth | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState<'overview' | 'users' | 'batches' | 'system'>('overview')

  useEffect(() => {
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    try {
      setLoading(true)
      setError(null)

      // Load system statistics
      const statsResponse = await adminApi.getSystemStats()
      setStats(statsResponse.data)

      // Load recent users
      const usersResponse = await adminApi.getRecentUsers(5)
      setRecentUsers(usersResponse.data)

      // Load recent batches
      const batchesResponse = await adminApi.getRecentBatches(10)
      setRecentBatches(batchesResponse.data)

      // Load system health
      const healthResponse = await adminApi.getSystemHealth()
      setSystemHealth(healthResponse.data)

    } catch (err: any) {
      console.error('Error loading dashboard data:', err)
      setError('Failed to load dashboard data')
    } finally {
      setLoading(false)
    }
  }

  const getRoleColor = (role: string) => {
    switch (role) {
      case 'admin':
        return 'bg-red-100 text-red-800'
      case 'farmer':
        return 'bg-green-100 text-green-800'
      case 'consumer':
        return 'bg-blue-100 text-blue-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800'
      case 'pending':
        return 'bg-yellow-100 text-yellow-800'
      case 'suspended':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getHealthStatusColor = (status: string) => {
    switch (status) {
      case 'healthy':
        return 'text-green-600'
      case 'warning':
        return 'text-yellow-600'
      case 'critical':
        return 'text-red-600'
      default:
        return 'text-gray-600'
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading dashboard...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <Card className="w-full max-w-md">
          <CardContent className="p-6 text-center">
            <p className="text-red-600 mb-4">{error}</p>
            <Button onClick={loadDashboardData}>Retry</Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Admin Dashboard</h1>
          <p className="text-muted-foreground">
            System overview and management controls
          </p>
        </div>
        <div className="flex space-x-2">
          <Button variant="outline">Export Reports</Button>
          <Button className="organic-gradient">System Settings</Button>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="border-b">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab('overview')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'overview'
                ? 'border-green-500 text-green-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Overview
          </button>
          <button
            onClick={() => setActiveTab('users')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'users'
                ? 'border-green-500 text-green-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Users
          </button>
          <button
            onClick={() => setActiveTab('batches')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'batches'
                ? 'border-green-500 text-green-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Batches
          </button>
          <button
            onClick={() => setActiveTab('system')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'system'
                ? 'border-green-500 text-green-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            System Health
          </button>
        </nav>
      </div>

      {activeTab === 'overview' && (
        <div className="space-y-6">
          {/* System Statistics */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Users</CardTitle>
                <div className="h-4 w-4 text-muted-foreground">👥</div>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats?.total_users || 0}</div>
                <p className="text-xs text-muted-foreground">
                  {stats?.total_farmers || 0} farmers, {stats?.total_consumers || 0} consumers
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Batches</CardTitle>
                <div className="h-4 w-4 text-muted-foreground">🌾</div>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats?.total_batches || 0}</div>
                <p className="text-xs text-muted-foreground">
                  {stats?.active_batches || 0} currently active
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Revenue</CardTitle>
                <div className="h-4 w-4 text-muted-foreground">💰</div>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {formatCurrency(stats?.total_revenue || 0)}
                </div>
                <p className="text-xs text-muted-foreground">Total platform revenue</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">AI Activity</CardTitle>
                <div className="h-4 w-4 text-muted-foreground">🤖</div>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats?.ai_predictions_today || 0}</div>
                <p className="text-xs text-muted-foreground">
                  {stats?.fraud_alerts_today || 0} fraud alerts today
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Recent Activity */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Recent Users</CardTitle>
                <CardDescription>
                  Latest user registrations
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {recentUsers.map((user) => (
                    <div key={user.id} className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2">
                          <span className="font-medium">{user.name}</span>
                          <Badge className={getRoleColor(user.role)}>
                            {user.role}
                          </Badge>
                          <Badge className={getStatusColor(user.status)}>
                            {user.status}
                          </Badge>
                        </div>
                        <div className="text-sm text-muted-foreground">
                          {user.email} • {user.location}
                        </div>
                        <div className="text-xs text-muted-foreground">
                          Joined: {formatDate(user.created_at)}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Recent Batches</CardTitle>
                <CardDescription>
                  Latest batch creations and updates
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {recentBatches.map((batch) => (
                    <div key={batch.id} className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2">
                          <span className="font-medium">{batch.batch_code}</span>
                          {batch.fraud_alert && (
                            <Badge className="bg-red-100 text-red-800">
                              ⚠️ Fraud Alert
                            </Badge>
                          )}
                          {batch.blockchain_verified && (
                            <Badge className="bg-green-100 text-green-800">
                              ⛓️ Verified
                            </Badge>
                          )}
                        </div>
                        <div className="text-sm text-muted-foreground">
                          {batch.product_name} • {batch.farmer_name}
                        </div>
                        <div className="text-xs text-muted-foreground">
                          Grade {batch.grade} • {Number(batch.quantity_kg).toFixed(2)} kg • {formatDate(batch.created_at)}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      )}

      {activeTab === 'users' && (
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>User Management</CardTitle>
              <CardDescription>
                All registered users in the system
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left py-2 px-2">Name</th>
                      <th className="text-left py-2 px-2">Email</th>
                      <th className="text-left py-2 px-2">Role</th>
                      <th className="text-left py-2 px-2">Location</th>
                      <th className="text-left py-2 px-2">Joined Date</th>
                    </tr>
                  </thead>
                  <tbody>
                    {recentUsers.map((user) => (
                      <tr key={user.id} className="border-b hover:bg-gray-50">
                        <td className="py-2 px-2 font-medium">{user.name}</td>
                        <td className="py-2 px-2 text-muted-foreground">{user.email}</td>
                        <td className="py-2 px-2">
                          <Badge className={getRoleColor(user.role)}>{user.role}</Badge>
                        </td>
                        <td className="py-2 px-2 text-muted-foreground">{user.location || '-'}</td>
                        <td className="py-2 px-2 text-muted-foreground">{formatDate(user.created_at)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {activeTab === 'batches' && (
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Batch Management</CardTitle>
              <CardDescription>
                All product batches in the system
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left py-2 px-2">Batch Code</th>
                      <th className="text-left py-2 px-2">Product</th>
                      <th className="text-left py-2 px-2">Grade</th>
                      <th className="text-left py-2 px-2">Quantity</th>
                      <th className="text-left py-2 px-2">Farmer</th>
                      <th className="text-left py-2 px-2">Date</th>
                    </tr>
                  </thead>
                  <tbody>
                    {recentBatches.map((batch) => (
                      <tr key={batch.id} className="border-b hover:bg-gray-50">
                        <td className="py-2 px-2 font-medium">{batch.batch_code}</td>
                        <td className="py-2 px-2 text-muted-foreground">{batch.product_name}</td>
                        <td className="py-2 px-2">
                          <Badge className={batch.grade === 'A' ? 'bg-green-100 text-green-800' : batch.grade === 'B' ? 'bg-yellow-100 text-yellow-800' : 'bg-red-100 text-red-800'}>
                            Grade {batch.grade}
                          </Badge>
                        </td>
                        <td className="py-2 px-2 text-muted-foreground">{Number(batch.quantity_kg).toFixed(2)} kg</td>
                        <td className="py-2 px-2 text-muted-foreground">{batch.farmer_name}</td>
                        <td className="py-2 px-2 text-muted-foreground">{formatDate(batch.created_at)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {activeTab === 'system' && systemHealth && (
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>System Health</CardTitle>
              <CardDescription>
                Monitor system performance and status
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-4 border rounded-lg">
                    <div>
                      <h3 className="font-medium">Database</h3>
                      <p className="text-sm text-muted-foreground">Primary data storage</p>
                    </div>
                    <div className={`text-lg font-bold ${getHealthStatusColor(systemHealth.database || systemHealth.database_status || 'unknown')}`}>
                      {(systemHealth.database || systemHealth.database_status || 'unknown').toUpperCase()}
                    </div>
                  </div>

                  <div className="flex items-center justify-between p-4 border rounded-lg">
                    <div>
                      <h3 className="font-medium">Blockchain</h3>
                      <p className="text-sm text-muted-foreground">Distributed ledger</p>
                    </div>
                    <div className={`text-lg font-bold ${getHealthStatusColor(systemHealth.blockchain?.valid ? 'operational' : systemHealth.blockchain_status || 'unknown')}`}>
                      {(systemHealth.blockchain?.valid ? 'operational' : systemHealth.blockchain_status || 'unknown').toUpperCase()}
                    </div>
                  </div>

                  <div className="flex items-center justify-between p-4 border rounded-lg">
                    <div>
                      <h3 className="font-medium">AI Models</h3>
                      <p className="text-sm text-muted-foreground">Machine learning services</p>
                    </div>
                    <div className={`text-lg font-bold ${getHealthStatusColor(systemHealth.ai_models_status || 'operational')}`}>
                      {(systemHealth.ai_models_status || 'operational').toUpperCase()}
                    </div>
                  </div>
                </div>

                <div className="space-y-4">
                  <div className="text-center p-4 border rounded-lg">
                    <div className="text-2xl font-bold text-blue-600 mb-2">
                      {systemHealth.api_response_time || 0}ms
                    </div>
                    <p className="text-sm font-medium">API Response Time</p>
                    <p className="text-xs text-muted-foreground">Average response time</p>
                  </div>

                  <div className="text-center p-4 border rounded-lg">
                    <div className="text-2xl font-bold text-green-600 mb-2">
                      {systemHealth.uptime_percentage}%
                    </div>
                    <p className="text-sm font-medium">System Uptime</p>
                    <p className="text-xs text-muted-foreground">Last 30 days</p>
                  </div>

                  <div className="text-center p-4 border rounded-lg">
                    <div className="text-lg font-bold text-purple-600 mb-2">
                      {systemHealth.last_backup ? formatDate(systemHealth.last_backup) : 'Never'}
                    </div>
                    <p className="text-sm font-medium">Last Backup</p>
                    <p className="text-xs text-muted-foreground">System data backup</p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}
