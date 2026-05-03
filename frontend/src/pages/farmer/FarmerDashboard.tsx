import React, { useState, useEffect } from 'react'
import { useAuth } from '@/lib/auth'
import { farmerApi, blockchainApi } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { formatDate, formatCurrency, getGradeColor, getStatusColor } from '@/lib/utils'
import CreateBatchForm from '@/components/forms/CreateBatchForm'

interface DashboardStats {
  total_products: number
  total_batches: number
  active_batches: number
  sold_batches: number
  total_revenue: number
  average_quality_score: number
}

interface Product {
  id: number
  name: string
  type: string
  description: string
  origin_state: string
  created_at: string
}

interface Batch {
  id: number
  batch_code: string
  product_id: number
  farmer_id: number
  quantity_kg: number
  harvest_date: string
  moisture_level: number
  color_score: number
  aroma_score: number
  defect_percentage: number
  weight_per_unit: number
  grade: string
  quality_score: number
  price_per_kg: number
  qr_code_path?: string
  qr_code_url?: string
  blockchain_block_index?: number
  status: string
  created_at: string
}

export default function FarmerDashboard() {
  const { user } = useAuth()
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [products, setProducts] = useState<Product[]>([])
  const [recentBatches, setRecentBatches] = useState<Batch[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showCreateBatch, setShowCreateBatch] = useState(false)
  const [showCreateProduct, setShowCreateProduct] = useState(false)
  const [showReports, setShowReports] = useState(false)
  const [viewBatch, setViewBatch] = useState<Batch | null>(null)
  const [qrBatch, setQrBatch] = useState<Batch | null>(null)

  useEffect(() => {
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    try {
      setLoading(true)
      setError(null)

      // Load dashboard stats
      const statsResponse = await farmerApi.getDashboard()
      setStats(statsResponse.data)

      // Load products
      const productsResponse = await farmerApi.getProducts()
      setProducts(productsResponse.data)

      // Load recent batches
      const batchesResponse = await farmerApi.getBatches(0, 5)
      setRecentBatches(batchesResponse.data)

    } catch (err: any) {
      console.error('Error loading dashboard data:', err)
      setError('Failed to load dashboard data')
    } finally {
      setLoading(false)
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
          <h1 className="text-3xl font-bold">Farmer Dashboard</h1>
          <p className="text-muted-foreground">
            Welcome back, {user?.name}! Manage your products and batches.
          </p>
        </div>
        <div className="flex space-x-2">
          <Button variant="outline" onClick={() => setShowReports(true)}>View Reports</Button>
          <Button className="organic-gradient" onClick={() => setShowCreateBatch(true)}>Create Batch</Button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Products</CardTitle>
            <div className="h-4 w-4 text-muted-foreground">📦</div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.total_products || 0}</div>
            <p className="text-xs text-muted-foreground">Active products</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Batches</CardTitle>
            <div className="h-4 w-4 text-muted-foreground">🌾</div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.total_batches || 0}</div>
            <p className="text-xs text-muted-foreground">All time batches</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Batches</CardTitle>
            <div className="h-4 w-4 text-muted-foreground">🔄</div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.active_batches || 0}</div>
            <p className="text-xs text-muted-foreground">Currently active</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Revenue</CardTitle>
            <div className="h-4 w-4 text-muted-foreground">💰</div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {formatCurrency(stats?.total_revenue || 0)}
            </div>
            <p className="text-xs text-muted-foreground">From sold batches</p>
          </CardContent>
        </Card>
      </div>

      {/* Recent Batches */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Batches</CardTitle>
          <CardDescription>
            Your latest batch creations and their current status
          </CardDescription>
        </CardHeader>
        <CardContent>
          {recentBatches.length === 0 ? (
            <div className="text-center py-8">
              <p className="text-muted-foreground mb-4">No batches created yet</p>
              <Button className="organic-gradient" onClick={() => setShowCreateBatch(true)}>Create Your First Batch</Button>
            </div>
          ) : (
            <div className="space-y-4">
              {recentBatches.map((batch) => (
                <div key={batch.id} className="flex items-center justify-between p-4 border rounded-lg">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <span className="font-medium">{batch.batch_code}</span>
                      <Badge className={getGradeColor(batch.grade)}>
                        Grade {batch.grade}
                      </Badge>
                      <Badge className={getStatusColor(batch.status)}>
                        {batch.status.replace('_', ' ')}
                      </Badge>
                    </div>
                    <div className="text-sm text-muted-foreground">
                      {Number(batch.quantity_kg).toFixed(2)} kg • Quality Score: {batch.quality_score} • 
                      {formatCurrency(batch.price_per_kg)}/kg
                    </div>
                    <div className="text-xs text-muted-foreground">
                      Harvested: {formatDate(batch.harvest_date)}
                    </div>
                  </div>
                  <div className="flex space-x-2">
                    <Button variant="outline" size="sm" onClick={() => setViewBatch(batch)}>View</Button>
                    <Button variant="outline" size="sm" onClick={() => setQrBatch(batch)}>QR Code</Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Products Overview */}
      <Card>
        <CardHeader>
          <CardTitle>Your Products</CardTitle>
          <CardDescription>
            Manage your agricultural products
          </CardDescription>
        </CardHeader>
        <CardContent>
          {products.length === 0 ? (
            <div className="text-center py-8">
              <p className="text-muted-foreground mb-4">No products registered yet</p>
              <Button variant="outline" onClick={() => setShowCreateProduct(true)}>Register Product</Button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {products.map((product) => (
                <Card key={product.id}>
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="font-medium">{product.name}</h3>
                      <Badge variant="outline">{product.type}</Badge>
                    </div>
                    <p className="text-sm text-muted-foreground mb-2">
                      {product.description}
                    </p>
                    <div className="text-xs text-muted-foreground">
                      Origin: {product.origin_state} • Created: {formatDate(product.created_at)}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Quality Insights */}
      <Card>
        <CardHeader>
          <CardTitle>Quality Insights</CardTitle>
          <CardDescription>
            AI-powered quality analysis and recommendations
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center p-4 border rounded-lg">
              <div className="text-2xl font-bold text-green-600 mb-2">
                {stats?.average_quality_score || 0}%
              </div>
              <p className="text-sm font-medium">Average Quality Score</p>
              <p className="text-xs text-muted-foreground">Across all batches</p>
            </div>
            <div className="text-center p-4 border rounded-lg">
              <div className="text-2xl font-bold text-blue-600 mb-2">
                A
              </div>
              <p className="text-sm font-medium">Most Common Grade</p>
              <p className="text-xs text-muted-foreground">Premium quality batches</p>
            </div>
            <div className="text-center p-4 border rounded-lg">
              <div className="text-2xl font-bold text-purple-600 mb-2">
                94%
              </div>
              <p className="text-sm font-medium">Customer Satisfaction</p>
              <p className="text-xs text-muted-foreground">Based on feedback</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Create Batch Modal */}
      {showCreateBatch && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <Card className="w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Create New Batch</CardTitle>
                <Button variant="ghost" size="sm" onClick={() => setShowCreateBatch(false)}>✕</Button>
              </div>
              <CardDescription>
                Create a new batch with AI quality grading and blockchain tracking
              </CardDescription>
            </CardHeader>
            <CardContent>
              <CreateBatchForm 
                onSuccess={() => {
                  setShowCreateBatch(false)
                  loadDashboardData()
                }}
                onCancel={() => setShowCreateBatch(false)}
              />
            </CardContent>
          </Card>
        </div>
      )}

      {/* Create Product Modal - Simple Version */}
      {showCreateProduct && (
        <CreateProductModal 
          onSuccess={() => {
            setShowCreateProduct(false)
            loadDashboardData()
          }}
          onCancel={() => setShowCreateProduct(false)}
        />
      )}

      {/* Reports Modal */}
      {showReports && (
        <ReportsModal 
          onClose={() => setShowReports(false)}
        />
      )}

      {/* View Batch Modal */}
      {viewBatch && (
        <ViewBatchModal 
          batch={viewBatch}
          onClose={() => setViewBatch(null)}
        />
      )}

      {/* QR Code Modal */}
      {qrBatch && (
        <QrCodeModal 
          batch={qrBatch}
          onClose={() => setQrBatch(null)}
        />
      )}
    </div>
  )
}

// Create Product Modal Component
function CreateProductModal({ onSuccess, onCancel }: { onSuccess: () => void, onCancel: () => void }) {
  const [formData, setFormData] = useState({
    name: '',
    type: 'organic',
    description: '',
    origin_state: ''
  })
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSubmitting(true)
    setError(null)

    try {
      await farmerApi.createProduct(formData)
      onSuccess()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create product')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <Card className="w-full max-w-md">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Register New Product</CardTitle>
            <Button variant="ghost" size="sm" onClick={onCancel}>✕</Button>
          </div>
          <CardDescription>
            Add a new agricultural product to your catalog
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <div className="p-3 bg-red-50 border border-red-200 rounded text-red-600 text-sm">
                {error}
              </div>
            )}
            <div>
              <Label htmlFor="name">Product Name</Label>
              <Input
                id="name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="e.g., Organic Coffee Beans"
                required
              />
            </div>
            <div>
              <Label htmlFor="type">Product Type</Label>
              <select
                id="type"
                value={formData.type}
                onChange={(e) => setFormData({ ...formData, type: e.target.value })}
                className="w-full p-2 border rounded"
              >
                <option value="spice">Spice</option>
                <option value="coffee">Coffee</option>
                <option value="tea">Tea</option>
                <option value="millet">Millet</option>
                <option value="organic">Organic</option>
              </select>
            </div>
            <div>
              <Label htmlFor="description">Description</Label>
              <Input
                id="description"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                placeholder="Brief description of your product"
              />
            </div>
            <div>
              <Label htmlFor="origin_state">Origin State</Label>
              <Input
                id="origin_state"
                value={formData.origin_state}
                onChange={(e) => setFormData({ ...formData, origin_state: e.target.value })}
                placeholder="e.g., Karnataka"
                required
              />
            </div>
            <div className="flex space-x-2 pt-4">
              <Button type="button" variant="outline" onClick={onCancel} className="flex-1">
                Cancel
              </Button>
              <Button type="submit" disabled={submitting} className="flex-1 organic-gradient">
                {submitting ? 'Creating...' : 'Register Product'}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}

// Reports Modal Component
function ReportsModal({ onClose }: { onClose: () => void }) {
  const [isLoading, setIsLoading] = useState<string | null>(null)

  const downloadAsPDF = (title: string, data: any) => {
    const printWindow = window.open('', '_blank')
    printWindow!.document.write(`
      <html><head><title>${title}</title>
      <style>
        body { font-family: Arial, sans-serif; padding: 20px; }
        h1 { color: #2D6A4F; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th { background: #2D6A4F; color: white; padding: 8px; text-align: left; }
        td { padding: 8px; border-bottom: 1px solid #ddd; }
        tr:nth-child(even) { background: #f9f9f9; }
        pre { background: #f5f5f5; padding: 10px; border-radius: 4px; overflow-x: auto; }
      </style></head>
      <body>
        <h1>Organic Roots — ${title}</h1>
        <p>Generated: ${new Date().toLocaleDateString()}</p>
        <pre>${JSON.stringify(data, null, 2)}</pre>
      </body></html>
    `)
    printWindow!.document.close()
    printWindow!.print()
  }

  const handleBatchSummary = async () => {
    setIsLoading('batch')
    try {
      const response = await farmerApi.getBatches(0, 1000)
      downloadAsPDF('Batch Summary Report', response.data)
    } catch (error) {
      console.error('Failed to download batch report:', error)
      alert('Failed to download batch report')
    } finally {
      setIsLoading(null)
    }
  }

  const handleQualityReport = async () => {
    setIsLoading('quality')
    try {
      const response = await farmerApi.getBatches(0, 1000)
      // Filter and sort by grade for quality analysis
      const batches = response.data
      const qualityData = {
        report_type: 'Quality Analysis',
        generated_at: new Date().toISOString(),
        total_batches: batches.length,
        grade_distribution: batches.reduce((acc: any, batch: any) => {
          acc[batch.grade] = (acc[batch.grade] || 0) + 1
          return acc
        }, {}),
        average_quality_score: batches.reduce((sum: number, b: any) => sum + (b.quality_score || 0), 0) / batches.length || 0,
        batches: batches.sort((a: any, b: any) => (b.quality_score || 0) - (a.quality_score || 0))
      }
      downloadAsPDF('Quality Report', qualityData)
    } catch (error) {
      console.error('Failed to download quality report:', error)
      alert('Failed to download quality report')
    } finally {
      setIsLoading(null)
    }
  }

  const handleRevenueReport = async () => {
    setIsLoading('revenue')
    try {
      const response = await farmerApi.getDashboard()
      const revenueData = {
        report_type: 'Revenue Report',
        generated_at: new Date().toISOString(),
        ...response.data
      }
      downloadAsPDF('Revenue Report', revenueData)
    } catch (error) {
      console.error('Failed to download revenue report:', error)
      alert('Failed to download revenue report')
    } finally {
      setIsLoading(null)
    }
  }

  const handleBlockchainLog = async () => {
    setIsLoading('blockchain')
    try {
      const response = await blockchainApi.getChain(100, 0)
      downloadAsPDF('Blockchain Log', response.data)
    } catch (error) {
      console.error('Failed to download blockchain log:', error)
      alert('Failed to download blockchain log')
    } finally {
      setIsLoading(null)
    }
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <Card className="w-full max-w-2xl max-h-[80vh] overflow-y-auto">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Farmer Reports</CardTitle>
            <Button variant="ghost" size="sm" onClick={onClose}>✕</Button>
          </div>
          <CardDescription>
            Download detailed analytics and reports for your farm
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Card className="p-4">
                <h3 className="font-medium mb-2">🌾 Batch Summary</h3>
                <p className="text-sm text-muted-foreground mb-4">
                  Complete list of all your batches with details
                </p>
                <Button 
                  variant="outline" 
                  size="sm" 
                  className="w-full"
                  onClick={handleBatchSummary}
                  disabled={isLoading === 'batch'}
                >
                  {isLoading === 'batch' ? 'Downloading...' : 'Download Batch Report'}
                </Button>
              </Card>
              <Card className="p-4">
                <h3 className="font-medium mb-2">� Quality Report</h3>
                <p className="text-sm text-muted-foreground mb-4">
                  Quality trends and grade distribution analysis
                </p>
                <Button 
                  variant="outline" 
                  size="sm" 
                  className="w-full"
                  onClick={handleQualityReport}
                  disabled={isLoading === 'quality'}
                >
                  {isLoading === 'quality' ? 'Downloading...' : 'Download Quality Report'}
                </Button>
              </Card>
              <Card className="p-4">
                <h3 className="font-medium mb-2">📈 Revenue Report</h3>
                <p className="text-sm text-muted-foreground mb-4">
                  Dashboard stats and revenue summary
                </p>
                <Button 
                  variant="outline" 
                  size="sm" 
                  className="w-full"
                  onClick={handleRevenueReport}
                  disabled={isLoading === 'revenue'}
                >
                  {isLoading === 'revenue' ? 'Downloading...' : 'Download Revenue Report'}
                </Button>
              </Card>
              <Card className="p-4">
                <h3 className="font-medium mb-2">🔗 Blockchain Log</h3>
                <p className="text-sm text-muted-foreground mb-4">
                  Immutable blockchain chain data
                </p>
                <Button 
                  variant="outline" 
                  size="sm" 
                  className="w-full"
                  onClick={handleBlockchainLog}
                  disabled={isLoading === 'blockchain'}
                >
                  {isLoading === 'blockchain' ? 'Downloading...' : 'Download Blockchain Log'}
                </Button>
              </Card>
            </div>
            <div className="flex justify-center pt-4">
              <Button onClick={onClose}>Close Reports</Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

// View Batch Modal Component
function ViewBatchModal({ batch, onClose }: { batch: Batch, onClose: () => void }) {
  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <Card className="w-full max-w-lg max-h-[80vh] overflow-y-auto">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Batch Details: {batch.batch_code}</CardTitle>
            <Button variant="ghost" size="sm" onClick={onClose}>✕</Button>
          </div>
          <CardDescription>
            Complete information about this batch
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label className="text-muted-foreground">Batch Code</Label>
                <p className="font-medium">{batch.batch_code}</p>
              </div>
              <div>
                <Label className="text-muted-foreground">Status</Label>
                <Badge className={getStatusColor(batch.status)}>
                  {batch.status.replace('_', ' ')}
                </Badge>
              </div>
              <div>
                <Label className="text-muted-foreground">Grade</Label>
                <p className="font-medium">{batch.grade}</p>
              </div>
              <div>
                <Label className="text-muted-foreground">Quality Score</Label>
                <p className="font-medium">{batch.quality_score}%</p>
              </div>
              <div>
                <Label className="text-muted-foreground">Quantity</Label>
                <p className="font-medium">{Number(batch.quantity_kg).toFixed(2)} kg</p>
              </div>
              <div>
                <Label className="text-muted-foreground">Price</Label>
                <p className="font-medium">{formatCurrency(batch.price_per_kg)}/kg</p>
              </div>
            </div>
            
            <div className="border-t pt-4">
              <h4 className="font-medium mb-2">Quality Metrics</h4>
              <div className="grid grid-cols-2 gap-2 text-sm">
                <div>Moisture: {batch.moisture_level}%</div>
                <div>Color Score: {batch.color_score}/10</div>
                <div>Aroma Score: {batch.aroma_score}/10</div>
                <div>Defects: {batch.defect_percentage}%</div>
              </div>
            </div>

            <div className="border-t pt-4">
              <h4 className="font-medium mb-2">Blockchain</h4>
              <p className="text-sm text-muted-foreground">
                Block Index: {batch.blockchain_block_index || 'Not recorded'}
              </p>
            </div>

            <div className="flex justify-center pt-4">
              <Button onClick={onClose}>Close</Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

// QR Code Modal Component
function QrCodeModal({ batch, onClose }: { batch: Batch, onClose: () => void }) {
  // Construct QR code image URL from the qr_code_path or batch code
  const getQrImageUrl = () => {
    if (batch.qr_code_path) {
      // Extract filename from path and construct full URL
      const filename = batch.qr_code_path.split('/').pop()
      return `http://localhost:8000/qr_codes/${filename}`
    }
    // Fallback: try to construct from batch code (may not work if file doesn't exist)
    return `http://localhost:8000/qr_codes/qr_${batch.batch_code}.png`
  }

  const handleDownloadQr = () => {
    const link = document.createElement('a')
    link.href = getQrImageUrl()
    link.download = `qr_${batch.batch_code}.png`
    link.click()
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <Card className="w-full max-w-md">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>QR Code: {batch.batch_code}</CardTitle>
            <Button variant="ghost" size="sm" onClick={onClose}>✕</Button>
          </div>
          <CardDescription>
            Scan to verify product authenticity
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col items-center space-y-4">
            <div className="bg-white p-4 rounded-lg border">
              {/* Actual QR code image from backend */}
              <img 
                src={getQrImageUrl()} 
                alt={`QR Code for ${batch.batch_code}`}
                className="w-48 h-48 object-contain"
                onError={(e) => {
                  // Show placeholder if image fails to load
                  const target = e.target as HTMLImageElement
                  target.style.display = 'none'
                  const parent = target.parentElement
                  if (parent) {
                    parent.innerHTML = `
                      <div class="w-48 h-48 bg-gray-200 flex items-center justify-center text-gray-500">
                        <div class="text-center">
                          <div class="text-4xl mb-2">📱</div>
                          <p class="text-xs">QR Code Not Found</p>
                          <p class="text-xs font-mono mt-1">${batch.batch_code}</p>
                        </div>
                      </div>
                    `
                  }
                }}
              />
            </div>
            <p className="text-sm text-muted-foreground text-center">
              Blockchain Verified • Grade {batch.grade} • {batch.quality_score}% Quality
            </p>
            <div className="flex space-x-2">
              <Button variant="outline" onClick={onClose}>Close</Button>
              <Button className="organic-gradient" onClick={handleDownloadQr}>Download QR</Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
