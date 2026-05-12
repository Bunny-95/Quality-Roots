import React, { useState, useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import { consumerApi } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { formatDate, formatCurrency, getGradeColor, getStatusColor } from '@/lib/utils'

interface BatchDetails {
  id?: number
  batch_code: string
  product_id?: number
  product_name: string
  product_type: string
  quantity_kg: number
  harvest_date: string
  grade: string
  status?: string
  quality_score: number
  price_per_kg?: number
  qr_code_url?: string
  farmer_name: string
  farmer_location: string
  /** Model confidence 0–1 from API; also accept legacy field names */
  ai_confidence?: number
  confidence?: number
  confidence_score?: number
  blockchain_verified: boolean
  fraud_free?: boolean
  origin_state?: string
}

function formatAiConfidencePercent(batch: BatchDetails): string {
  const raw =
    batch.ai_confidence ?? batch.confidence ?? batch.confidence_score
  if (raw === undefined || raw === null) return 'N/A'
  const n = Number(raw)
  if (Number.isNaN(n)) return 'N/A'
  const pct = n <= 1 ? n * 100 : n
  return `${pct.toFixed(1)}%`
}

interface SupplyChainEvent {
  id: number
  event_type: string
  description: string
  location: string
  timestamp: string
  actor: string
}

export default function VerifyPage() {
  const [searchParams] = useSearchParams()
  const [batchCode, setBatchCode] = useState(searchParams.get('batch') || '')
  const [batchDetails, setBatchDetails] = useState<BatchDetails | null>(null)
  const [supplyChainEvents, setSupplyChainEvents] = useState<SupplyChainEvent[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [verifying, setVerifying] = useState(false)

  useEffect(() => {
    if (batchCode) {
      verifyBatch(batchCode)
    }
  }, [batchCode])

  const verifyBatch = async (code: string) => {
    try {
      setLoading(true)
      setError(null)
      setVerifying(true)

      // Get batch details - API returns {success, message, product_journey}
      const batchResponse = await consumerApi.verifyBatch(code)
      const journeyData = batchResponse.data?.product_journey || batchResponse.data
      setBatchDetails(journeyData)

      // Get supply chain events
      const eventsResponse = await consumerApi.getBatchJourney(code)
      const eventsData = eventsResponse.data
      
      // Extract journey events from response (API returns object with journey_events array)
      const events = eventsData?.journey_events 
        ?? eventsData?.events 
        ?? (Array.isArray(eventsData) ? eventsData : [])
      setSupplyChainEvents(Array.isArray(events) ? events : [])

    } catch (error: any) {
      console.error('Error verifying batch:', error)
      const message = error.response?.data?.detail || 'Failed to verify batch. Please check the batch code.'
      setError(message)
      setBatchDetails(null)
      setSupplyChainEvents([])
    } finally {
      setLoading(false)
      setVerifying(false)
    }
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setBatchCode(e.target.value)
    if (error) {
      setError(null)
    }
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (batchCode.trim()) {
      verifyBatch(batchCode.trim())
    }
  }

  const getEventTypeColor = (eventType: string) => {
    switch (eventType) {
      case 'harvested':
        return 'bg-green-100 text-green-800'
      case 'processed':
        return 'bg-blue-100 text-blue-800'
      case 'packaged':
        return 'bg-purple-100 text-purple-800'
      case 'shipped':
        return 'bg-orange-100 text-orange-800'
      case 'delivered':
        return 'bg-emerald-100 text-emerald-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getEventTypeIcon = (eventType: string) => {
    switch (eventType) {
      case 'harvested':
        return '🌾'
      case 'processed':
        return '⚙️'
      case 'packaged':
        return '📦'
      case 'shipped':
        return '🚚'
      case 'delivered':
        return '✅'
      default:
        return '📍'
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-emerald-100 p-4">
      <div className="container mx-auto max-w-6xl">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 organic-gradient rounded-full mb-4">
            <span className="text-white font-bold text-2xl">OR</span>
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Product Verification</h1>
          <p className="text-gray-600">
            Scan QR code or enter batch code to verify product authenticity
          </p>
        </div>

        {/* Verification Form */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>Verify Product</CardTitle>
            <CardDescription>
              Enter the batch code from the product label or QR code
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="flex space-x-2">
                <div className="flex-1">
                  <Label htmlFor="batchCode">Batch Code</Label>
                  <Input
                    id="batchCode"
                    type="text"
                    placeholder="e.g., BATCH-2024-001"
                    value={batchCode}
                    onChange={handleInputChange}
                    disabled={verifying}
                    className={error ? 'border-red-500' : ''}
                  />
                  {error && (
                    <p className="text-sm text-red-500 mt-1">{error}</p>
                  )}
                </div>
                <div className="flex items-end">
                  <Button
                    type="submit"
                    className="organic-gradient"
                    disabled={verifying || !batchCode.trim()}
                  >
                    {verifying ? 'Verifying...' : 'Verify'}
                  </Button>
                </div>
              </div>
            </form>
          </CardContent>
        </Card>

        {/* Loading State */}
        {loading && (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
            <p className="text-muted-foreground">Verifying product...</p>
          </div>
        )}

        {/* Batch Details */}
        {batchDetails && !loading && (
          <div className="space-y-6">
            {/* Product Overview */}
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="flex items-center space-x-2">
                    <span>{batchDetails.product_name}</span>
                    <Badge className={getGradeColor(batchDetails.grade)}>
                      Grade {batchDetails.grade}
                    </Badge>
                    {batchDetails.blockchain_verified && (
                      <Badge className="bg-green-100 text-green-800">
                        ⛓️ Blockchain Verified
                      </Badge>
                    )}
                  </CardTitle>
                  <Badge className={getStatusColor(batchDetails.status || 'Active')}>
                    {(batchDetails.status || 'Active').replace(/_/g, ' ')}
                  </Badge>
                </div>
                <CardDescription>
                  Batch Code: {batchDetails.batch_code}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                  <div className="text-center p-4 border rounded-lg">
                    <div className="text-2xl font-bold text-green-600 mb-2">
                      {batchDetails.quality_score}%
                    </div>
                    <p className="text-sm font-medium">Quality Score</p>
                    <p className="text-xs text-muted-foreground">AI Verified</p>
                  </div>
                  <div className="text-center p-4 border rounded-lg">
                    <div className="text-2xl font-bold text-blue-600 mb-2">
                      {formatAiConfidencePercent(batchDetails)}
                    </div>
                    <p className="text-sm font-medium">AI Confidence</p>
                    <p className="text-xs text-muted-foreground">Grading Accuracy</p>
                  </div>
                  <div className="text-center p-4 border rounded-lg">
                    <div className="text-2xl font-bold text-purple-600 mb-2">
                      {Number(batchDetails.quantity_kg).toFixed(2)} kg
                    </div>
                    <p className="text-sm font-medium">Batch Size</p>
                    <p className="text-xs text-muted-foreground">Total Quantity</p>
                  </div>
                  <div className="text-center p-4 border rounded-lg">
                    <div className="text-2xl font-bold text-orange-600 mb-2">
                      {formatCurrency(batchDetails.price_per_kg)}
                    </div>
                    <p className="text-sm font-medium">Price per kg</p>
                    <p className="text-xs text-muted-foreground">Market Price</p>
                  </div>
                </div>

                <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="p-4 bg-gray-50 rounded-lg">
                    <h3 className="font-medium mb-2">👨‍🌾 Farmer Information</h3>
                    <p className="text-sm text-gray-600">{batchDetails.farmer_name}</p>
                    <p className="text-sm text-gray-600">{batchDetails.farmer_location}</p>
                  </div>
                  <div className="p-4 bg-gray-50 rounded-lg">
                    <h3 className="font-medium mb-2">📅 Harvest Information</h3>
                    <p className="text-sm text-gray-600">Harvested: {formatDate(batchDetails.harvest_date ?? undefined)}</p>
                    <p className="text-sm text-gray-600">Product Type: {batchDetails.product_type}</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Supply Chain Journey */}
            <Card>
              <CardHeader>
                <CardTitle>Supply Chain Journey</CardTitle>
                <CardDescription>
                  Track the product's journey from farm to table
                </CardDescription>
              </CardHeader>
              <CardContent>
                {!Array.isArray(supplyChainEvents) || supplyChainEvents.length === 0 ? (
                  <div className="text-center py-8">
                    <p className="text-muted-foreground">No supply chain events recorded</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {supplyChainEvents.map((event, index) => (
                      <div key={event.id} className="flex items-start space-x-4">
                        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary text-white flex items-center justify-center text-sm font-medium">
                          {getEventTypeIcon(event.event_type)}
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center space-x-2 mb-1">
                            <Badge className={getEventTypeColor(event.event_type || 'unknown')}>
                              {(event.event_type || 'unknown').replace('_', ' ').toUpperCase()}
                            </Badge>
                            <span className="text-sm text-gray-500">
                              {formatDate(event.timestamp ?? undefined)}
                            </span>
                          </div>
                          <h3 className="font-medium text-gray-900">{event.description}</h3>
                          <p className="text-sm text-gray-600">
                            📍 {event.location} • 👤 {event.actor}
                          </p>
                        </div>
                        {index < supplyChainEvents.length - 1 && (
                          <div className="flex-shrink-0 w-8 h-8 flex items-center justify-center">
                            <div className="w-0.5 h-8 bg-gray-300"></div>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Trust Indicators */}
            <Card>
              <CardHeader>
                <CardTitle>Trust & Authenticity</CardTitle>
                <CardDescription>
                  Multiple verification layers ensure product authenticity
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="text-center p-4 border rounded-lg">
                    <div className="text-2xl mb-2">⛓️</div>
                    <h3 className="font-medium mb-1">Blockchain Verified</h3>
                    <p className="text-sm text-gray-600">
                      All transactions recorded on immutable blockchain
                    </p>
                  </div>
                  <div className="text-center p-4 border rounded-lg">
                    <div className="text-2xl mb-2">🤖</div>
                    <h3 className="font-medium mb-1">AI Quality Graded</h3>
                    <p className="text-sm text-gray-600">
                      Advanced AI algorithms ensure quality standards
                    </p>
                  </div>
                  <div className="text-center p-4 border rounded-lg">
                    <div className="text-2xl mb-2">🔒</div>
                    <h3 className="font-medium mb-1">Fraud Protected</h3>
                    <p className="text-sm text-gray-600">
                      AI-powered fraud detection ensures authenticity
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Back to Home */}
        <div className="text-center mt-8">
          <Button variant="outline" onClick={() => window.location.href = '/'}>
            ← Back to Home
          </Button>
        </div>
      </div>
    </div>
  )
}
