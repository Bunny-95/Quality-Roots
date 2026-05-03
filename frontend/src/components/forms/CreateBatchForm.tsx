import React, { useState, useEffect } from 'react'
import { farmerApi } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'

interface Product {
  id: number
  name: string
  type: string
  description: string
  origin_state: string
}

interface BatchFormData {
  product_id: number
  quantity_kg: number
  harvest_date: string
  moisture_level: number
  color_score: number
  aroma_score: number
  defect_percentage: number
  weight_per_unit: number
}

interface FormErrors {
  product_id?: string
  quantity_kg?: string
  harvest_date?: string
  moisture_level?: string
  color_score?: string
  aroma_score?: string
  defect_percentage?: string
  weight_per_unit?: string
  general?: string
}

interface CreateBatchFormProps {
  onSuccess?: () => void
  onCancel?: () => void
}

export default function CreateBatchForm({ onSuccess, onCancel }: CreateBatchFormProps) {
  const [products, setProducts] = useState<Product[]>([])
  const [loading, setLoading] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [aiResult, setAiResult] = useState<any>(null)
  const [errors, setErrors] = useState<FormErrors>({})

  const [formData, setFormData] = useState<BatchFormData>({
    product_id: 0,
    quantity_kg: 0,
    harvest_date: new Date().toISOString().split('T')[0],
    moisture_level: 0,
    color_score: 0,
    aroma_score: 0,
    defect_percentage: 0,
    weight_per_unit: 0,
  })

  useEffect(() => {
    loadProducts()
  }, [])

  const loadProducts = async () => {
    try {
      setLoading(true)
      const response = await farmerApi.getProducts()
      setProducts(response.data)
    } catch (error) {
      console.error('Error loading products:', error)
      setErrors({ general: 'Failed to load products' })
    } finally {
      setLoading(false)
    }
  }

  const validateForm = (): boolean => {
    const newErrors: FormErrors = {}

    if (!formData.product_id) {
      newErrors.product_id = 'Please select a product'
    }

    if (!formData.quantity_kg || formData.quantity_kg <= 0) {
      newErrors.quantity_kg = 'Quantity must be greater than 0'
    }

    if (!formData.harvest_date) {
      newErrors.harvest_date = 'Harvest date is required'
    }

    if (formData.moisture_level < 0 || formData.moisture_level > 100) {
      newErrors.moisture_level = 'Moisture level must be between 0 and 100'
    }

    if (formData.color_score < 0 || formData.color_score > 10) {
      newErrors.color_score = 'Color score must be between 0 and 10'
    }

    if (formData.aroma_score < 0 || formData.aroma_score > 10) {
      newErrors.aroma_score = 'Aroma score must be between 0 and 10'
    }

    if (formData.defect_percentage < 0 || formData.defect_percentage > 100) {
      newErrors.defect_percentage = 'Defect percentage must be between 0 and 100'
    }

    if (formData.weight_per_unit <= 0) {
      newErrors.weight_per_unit = 'Weight per unit must be greater than 0'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({ 
      ...prev, 
      [name]: name.includes('quantity_kg') || name.includes('moisture_level') || 
                name.includes('color_score') || name.includes('aroma_score') || 
                name.includes('defect_percentage') || name.includes('weight_per_unit') ||
                name === 'product_id' 
                ? parseFloat(value) || 0 
                : value 
    }))
    
    // Clear error for this field when user starts typing
    if (errors[name as keyof FormErrors]) {
      setErrors(prev => ({ ...prev, [name]: undefined }))
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!validateForm()) {
      return
    }

    setSubmitting(true)
    setErrors({})

    try {
      // Create batch with AI grading
      const response = await farmerApi.createBatch(formData)
      setAiResult(response.data)
      
      if (onSuccess) {
        onSuccess()
      }
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Failed to create batch'
      setErrors({ general: message })
    } finally {
      setSubmitting(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading products...</p>
        </div>
      </div>
    )
  }

  if (aiResult) {
    return (
      <Card>
        <CardHeader className="text-center">
          <CardTitle className="text-green-600">Batch Created Successfully!</CardTitle>
          <CardDescription>
            Your batch has been created with AI quality grading
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="text-center p-4 border rounded-lg">
              <div className="text-2xl font-bold text-green-600 mb-2">
                {aiResult.batch_code}
              </div>
              <p className="text-sm font-medium">Batch Code</p>
            </div>
            <div className="text-center p-4 border rounded-lg">
              <div className="text-2xl font-bold text-blue-600 mb-2">
                Grade {aiResult.grade}
              </div>
              <p className="text-sm font-medium">Quality Grade</p>
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center p-3 border rounded">
              <div className="text-lg font-bold">{aiResult.quality_score}%</div>
              <p className="text-xs text-muted-foreground">Quality Score</p>
            </div>
            <div className="text-center p-3 border rounded">
              <div className="text-lg font-bold">{aiResult.price_per_kg}</div>
              <p className="text-xs text-muted-foreground">Price per kg</p>
            </div>
            <div className="text-center p-3 border rounded">
              <div className="text-lg font-bold">{aiResult.confidence}%</div>
              <p className="text-xs text-muted-foreground">AI Confidence</p>
            </div>
          </div>

          <div className="flex space-x-2">
            <Button onClick={() => window.print()} variant="outline">
              Print QR Code
            </Button>
            <Button onClick={onSuccess} className="organic-gradient">
              Create Another Batch
            </Button>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Create New Batch</CardTitle>
        <CardDescription>
          Add a new batch with AI-powered quality grading
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Product Selection */}
          <div className="space-y-2">
            <Label htmlFor="product_id">Select Product *</Label>
            <select
              id="product_id"
              name="product_id"
              value={formData.product_id}
              onChange={handleInputChange}
              className="w-full p-2 border rounded-md"
              disabled={submitting}
            >
              <option value="">Choose a product...</option>
              {products.map((product) => (
                <option key={product.id} value={product.id}>
                  {product.name} - {product.type}
                </option>
              ))}
            </select>
            {errors.product_id && (
              <p className="text-sm text-red-500">{errors.product_id}</p>
            )}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Quantity */}
            <div className="space-y-2">
              <Label htmlFor="quantity_kg">Quantity (kg) *</Label>
              <Input
                id="quantity_kg"
                name="quantity_kg"
                type="number"
                step="0.1"
                min="0.1"
                placeholder="100.0"
                value={formData.quantity_kg || ''}
                onChange={handleInputChange}
                disabled={submitting}
                className={errors.quantity_kg ? 'border-red-500' : ''}
              />
              {errors.quantity_kg && (
                <p className="text-sm text-red-500">{errors.quantity_kg}</p>
              )}
            </div>

            {/* Harvest Date */}
            <div className="space-y-2">
              <Label htmlFor="harvest_date">Harvest Date *</Label>
              <Input
                id="harvest_date"
                name="harvest_date"
                type="date"
                value={formData.harvest_date}
                onChange={handleInputChange}
                disabled={submitting}
                className={errors.harvest_date ? 'border-red-500' : ''}
              />
              {errors.harvest_date && (
                <p className="text-sm text-red-500">{errors.harvest_date}</p>
              )}
            </div>
          </div>

          {/* Quality Parameters */}
          <div className="space-y-4">
            <h3 className="text-lg font-medium">Quality Parameters</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="moisture_level">Moisture Level (%)</Label>
                <Input
                  id="moisture_level"
                  name="moisture_level"
                  type="number"
                  step="0.1"
                  min="0"
                  max="100"
                  placeholder="12.5"
                  value={formData.moisture_level || ''}
                  onChange={handleInputChange}
                  disabled={submitting}
                  className={errors.moisture_level ? 'border-red-500' : ''}
                />
                {errors.moisture_level && (
                  <p className="text-sm text-red-500">{errors.moisture_level}</p>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="color_score">Color Score (0-10)</Label>
                <Input
                  id="color_score"
                  name="color_score"
                  type="number"
                  step="0.1"
                  min="0"
                  max="10"
                  placeholder="8.5"
                  value={formData.color_score || ''}
                  onChange={handleInputChange}
                  disabled={submitting}
                  className={errors.color_score ? 'border-red-500' : ''}
                />
                {errors.color_score && (
                  <p className="text-sm text-red-500">{errors.color_score}</p>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="aroma_score">Aroma Score (0-10)</Label>
                <Input
                  id="aroma_score"
                  name="aroma_score"
                  type="number"
                  step="0.1"
                  min="0"
                  max="10"
                  placeholder="7.8"
                  value={formData.aroma_score || ''}
                  onChange={handleInputChange}
                  disabled={submitting}
                  className={errors.aroma_score ? 'border-red-500' : ''}
                />
                {errors.aroma_score && (
                  <p className="text-sm text-red-500">{errors.aroma_score}</p>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="defect_percentage">Defect Percentage (%)</Label>
                <Input
                  id="defect_percentage"
                  name="defect_percentage"
                  type="number"
                  step="0.1"
                  min="0"
                  max="100"
                  placeholder="2.5"
                  value={formData.defect_percentage || ''}
                  onChange={handleInputChange}
                  disabled={submitting}
                  className={errors.defect_percentage ? 'border-red-500' : ''}
                />
                {errors.defect_percentage && (
                  <p className="text-sm text-red-500">{errors.defect_percentage}</p>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="weight_per_unit">Weight per Unit (g)</Label>
                <Input
                  id="weight_per_unit"
                  name="weight_per_unit"
                  type="number"
                  step="0.1"
                  min="0.1"
                  placeholder="250.0"
                  value={formData.weight_per_unit || ''}
                  onChange={handleInputChange}
                  disabled={submitting}
                  className={errors.weight_per_unit ? 'border-red-500' : ''}
                />
                {errors.weight_per_unit && (
                  <p className="text-sm text-red-500">{errors.weight_per_unit}</p>
                )}
              </div>
            </div>
          </div>

          {/* General Error */}
          {errors.general && (
            <div className="bg-red-50 border border-red-200 rounded-md p-3">
              <p className="text-sm text-red-600">{errors.general}</p>
            </div>
          )}

          {/* Submit Buttons */}
          <div className="flex space-x-2">
            <Button
              type="submit"
              className="organic-gradient"
              disabled={submitting}
            >
              {submitting ? 'Creating Batch...' : 'Create Batch with AI Grading'}
            </Button>
            {onCancel && (
              <Button type="button" variant="outline" onClick={onCancel}>
                Cancel
              </Button>
            )}
          </div>
        </form>
      </CardContent>
    </Card>
  )
}
