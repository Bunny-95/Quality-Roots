import React, { useState, useEffect } from 'react'
import { aiApi } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { formatDate, formatCurrency } from '@/lib/utils'

interface AIModelStats {
  model_name: string
  total_predictions: number
  accuracy_percentage: number
  avg_confidence: number
  last_trained: string
  model_version: string
  status: string
}

interface QualityAnalytics {
  total_graded: number
  grade_distribution: {
    grade: string
    count: number
    percentage: number
  }[]
  avg_quality_score: number
  quality_trend: {
    date: string
    score: number
  }[]
  top_factors: {
    factor: string
    impact: number
  }[]
}

interface FraudAnalytics {
  total_alerts: number
  confirmed_fraud: number
  false_positives: number
  detection_rate: number
  fraud_types: {
    type: string
    count: number
  }[]
  recent_alerts: {
    id: number
    batch_code: string
    confidence: number
    timestamp: string
    status: string
  }[]
}

interface DemandForecast {
  product_name: string
  current_demand: number
  predicted_demand: number
  confidence: number
  trend: string
  seasonality: string
  factors: {
    factor: string
    weight: number
  }[]
}

export default function AIAnalyticsPage() {
  const [modelStats, setModelStats] = useState<AIModelStats[]>([])
  const [qualityAnalytics, setQualityAnalytics] = useState<QualityAnalytics | null>(null)
  const [fraudAnalytics, setFraudAnalytics] = useState<FraudAnalytics | null>(null)
  const [demandForecasts, setDemandForecasts] = useState<DemandForecast[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState<'models' | 'quality' | 'fraud' | 'forecast'>('models')

  useEffect(() => {
    loadAnalyticsData()
  }, [])

  const loadAnalyticsData = async () => {
    try {
      setLoading(true)
      setError(null)

      // Load AI model statistics
      const modelsResponse = await aiApi.getModelStats()
      setModelStats(modelsResponse.data)

      // Load quality analytics
      const qualityResponse = await aiApi.getQualityAnalytics()
      setQualityAnalytics(qualityResponse.data)

      // Load fraud analytics
      const fraudResponse = await aiApi.getFraudAnalytics()
      setFraudAnalytics(fraudResponse.data)

      // Load demand forecasts
      const forecastResponse = await aiApi.getDemandForecasts()
      setDemandForecasts(forecastResponse.data)

    } catch (err: any) {
      console.error('Error loading analytics data:', err)
      setError('Failed to load analytics data')
    } finally {
      setLoading(false)
    }
  }

  const getModelStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800'
      case 'training':
        return 'bg-yellow-100 text-yellow-800'
      case 'maintenance':
        return 'bg-orange-100 text-orange-800'
      case 'offline':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getGradeColor = (grade: string) => {
    switch (grade) {
      case 'A':
        return 'bg-green-100 text-green-800'
      case 'B':
        return 'bg-blue-100 text-blue-800'
      case 'C':
        return 'bg-yellow-100 text-yellow-800'
      case 'D':
        return 'bg-orange-100 text-orange-800'
      case 'F':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getFraudStatusColor = (status: string) => {
    switch (status) {
      case 'confirmed':
        return 'bg-red-100 text-red-800'
      case 'investigating':
        return 'bg-yellow-100 text-yellow-800'
      case 'false_positive':
        return 'bg-gray-100 text-gray-800'
      default:
        return 'bg-blue-100 text-blue-800'
    }
  }

  const getTrendColor = (trend: string) => {
    switch (trend) {
      case 'increasing':
        return 'text-green-600'
      case 'decreasing':
        return 'text-red-600'
      case 'stable':
        return 'text-blue-600'
      default:
        return 'text-gray-600'
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading AI analytics...</p>
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
            <Button onClick={loadAnalyticsData}>Retry</Button>
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
          <h1 className="text-3xl font-bold">AI Analytics</h1>
          <p className="text-muted-foreground">
            Monitor AI model performance and insights
          </p>
        </div>
        <div className="flex space-x-2">
          <Button variant="outline">Export Data</Button>
          <Button className="organic-gradient">Retrain Models</Button>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="border-b">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab('models')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'models'
                ? 'border-purple-500 text-purple-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Model Performance
          </button>
          <button
            onClick={() => setActiveTab('quality')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'quality'
                ? 'border-purple-500 text-purple-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Quality Analytics
          </button>
          <button
            onClick={() => setActiveTab('fraud')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'fraud'
                ? 'border-purple-500 text-purple-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Fraud Detection
          </button>
          <button
            onClick={() => setActiveTab('forecast')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'forecast'
                ? 'border-purple-500 text-purple-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Demand Forecast
          </button>
        </nav>
      </div>

      {/* Models Tab */}
      {activeTab === 'models' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {modelStats.map((model) => (
              <Card key={model.model_name}>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg">{model.model_name}</CardTitle>
                    <Badge className={getModelStatusColor(model.status)}>
                      {model.status}
                    </Badge>
                  </div>
                  <CardDescription>
                    Version {model.model_version}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex justify-between">
                      <span className="text-sm text-muted-foreground">Total Predictions</span>
                      <span className="font-medium">{model.total_predictions.toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-muted-foreground">Accuracy</span>
                      <span className="font-medium text-green-600">{model.accuracy_percentage}%</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-muted-foreground">Avg Confidence</span>
                      <span className="font-medium text-blue-600">{model.avg_confidence}%</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-muted-foreground">Last Trained</span>
                      <span className="font-medium text-xs">{formatDate(model.last_trained)}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}

      {/* Quality Analytics Tab */}
      {activeTab === 'quality' && qualityAnalytics && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Total Batches Graded</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-green-600">
                  {qualityAnalytics.total_graded.toLocaleString()}
                </div>
                <p className="text-sm text-muted-foreground">Since inception</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Average Quality Score</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-blue-600">
                  {qualityAnalytics.avg_quality_score.toFixed(1)}%
                </div>
                <p className="text-sm text-muted-foreground">Across all batches</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Top Quality Factors</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {qualityAnalytics.top_factors.slice(0, 3).map((factor, index) => (
                    <div key={index} className="flex justify-between">
                      <span className="text-sm">{factor.factor}</span>
                      <span className="text-sm font-medium">{factor.impact}%</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Grade Distribution</CardTitle>
              <CardDescription>
                Breakdown of quality grades assigned
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {qualityAnalytics.grade_distribution.map((grade) => (
                  <div key={grade.grade} className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <Badge className={getGradeColor(grade.grade)}>
                        Grade {grade.grade}
                      </Badge>
                      <span className="text-sm text-muted-foreground">
                        {grade.count.toLocaleString()} batches
                      </span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <div className="w-32 bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-gradient-to-r from-green-400 to-green-600 h-2 rounded-full"
                          style={{ width: `${grade.percentage}%` }}
                        ></div>
                      </div>
                      <span className="text-sm font-medium">{grade.percentage}%</span>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Fraud Detection Tab */}
      {activeTab === 'fraud' && fraudAnalytics && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Total Alerts</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-orange-600">
                  {fraudAnalytics.total_alerts}
                </div>
                <p className="text-sm text-muted-foreground">Fraud alerts generated</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Confirmed Fraud</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-red-600">
                  {fraudAnalytics.confirmed_fraud}
                </div>
                <p className="text-sm text-muted-foreground">Verified cases</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Detection Rate</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-green-600">
                  {fraudAnalytics.detection_rate.toFixed(1)}%
                </div>
                <p className="text-sm text-muted-foreground">Accuracy rate</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-lg">False Positives</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-yellow-600">
                  {fraudAnalytics.false_positives}
                </div>
                <p className="text-sm text-muted-foreground">Incorrect alerts</p>
              </CardContent>
            </Card>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Fraud Types</CardTitle>
                <CardDescription>
                  Common fraud patterns detected
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {fraudAnalytics.fraud_types.map((type, index) => (
                    <div key={index} className="flex justify-between items-center">
                      <span className="text-sm">{type.type.replace('_', ' ')}</span>
                      <Badge variant="outline">{type.count}</Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Recent Alerts</CardTitle>
                <CardDescription>
                  Latest fraud detection alerts
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {fraudAnalytics.recent_alerts.slice(0, 5).map((alert) => (
                    <div key={alert.id} className="flex justify-between items-center">
                      <div>
                        <div className="font-medium">{alert.batch_code}</div>
                        <div className="text-sm text-muted-foreground">
                          {formatDate(alert.timestamp)}
                        </div>
                      </div>
                      <div className="text-right">
                        <Badge className={getFraudStatusColor(alert.status)}>
                          {alert.status.replace('_', ' ')}
                        </Badge>
                        <div className="text-sm text-muted-foreground">
                          {alert.confidence}% confidence
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

      {/* Demand Forecast Tab */}
      {activeTab === 'forecast' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {demandForecasts.map((forecast) => (
              <Card key={forecast.product_name}>
                <CardHeader>
                  <CardTitle className="text-lg">{forecast.product_name}</CardTitle>
                  <CardDescription>
                    Demand forecast analysis
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex justify-between">
                      <span className="text-sm text-muted-foreground">Current Demand</span>
                      <span className="font-medium">{forecast.current_demand.toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-muted-foreground">Predicted Demand</span>
                      <span className={`font-medium ${getTrendColor(forecast.trend)}`}>
                        {forecast.predicted_demand.toLocaleString()}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-muted-foreground">Confidence</span>
                      <span className="font-medium text-blue-600">{forecast.confidence}%</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-muted-foreground">Trend</span>
                      <span className={`font-medium ${getTrendColor(forecast.trend)}`}>
                        {forecast.trend}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-muted-foreground">Seasonality</span>
                      <span className="font-medium">{forecast.seasonality}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
