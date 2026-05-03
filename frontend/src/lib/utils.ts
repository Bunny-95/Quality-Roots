import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatCurrency(amount: number | null | undefined, currency: string = '₹'): string {
  if (amount === null || amount === undefined || isNaN(amount)) {
    return `${currency}0.00`
  }
  return `${currency}${amount.toLocaleString('en-IN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  })}`
}

export const formatDate = (date: string | Date | undefined | null): string => {
  if (!date) return 'N/A'
  try {
    return new Date(date).toLocaleDateString('en-IN', {
      day: '2-digit',
      month: 'short',
      year: 'numeric'
    })
  } catch {
    return 'N/A'
  }
}

export function formatDateTime(date: string | Date): string {
  const dateObj = typeof date === 'string' ? new Date(date) : date
  return dateObj.toLocaleString('en-IN', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

export function formatRelativeTime(date: string | Date): string {
  const dateObj = typeof date === 'string' ? new Date(date) : date
  const now = new Date()
  const diffInMs = now.getTime() - dateObj.getTime()
  const diffInDays = Math.floor(diffInMs / (1000 * 60 * 60 * 24))
  
  if (diffInDays === 0) return 'Today'
  if (diffInDays === 1) return 'Yesterday'
  if (diffInDays < 7) return `${diffInDays} days ago`
  if (diffInDays < 30) return `${Math.floor(diffInDays / 7)} weeks ago`
  if (diffInDays < 365) return `${Math.floor(diffInDays / 30)} months ago`
  return `${Math.floor(diffInDays / 365)} years ago`
}

export function getGradeColor(grade: string): string {
  switch (grade) {
    case 'A':
      return 'text-green-600 bg-green-50 border-green-200'
    case 'B':
      return 'text-yellow-600 bg-yellow-50 border-yellow-200'
    case 'C':
      return 'text-orange-600 bg-orange-50 border-orange-200'
    default:
      return 'text-gray-600 bg-gray-50 border-gray-200'
  }
}

export function getGradeLabel(grade: string): string {
  switch (grade) {
    case 'A':
      return 'Premium'
    case 'B':
      return 'Good'
    case 'C':
      return 'Standard'
    default:
      return 'Unknown'
  }
}

export function getStatusColor(status: string): string {
  switch (status) {
    case 'CREATED':
      return 'text-blue-600 bg-blue-50 border-blue-200'
    case 'QUALITY_CHECKED':
      return 'text-purple-600 bg-purple-50 border-purple-200'
    case 'DISPATCHED':
      return 'text-indigo-600 bg-indigo-50 border-indigo-200'
    case 'IN_TRANSIT':
      return 'text-yellow-600 bg-yellow-50 border-yellow-200'
    case 'RECEIVED':
      return 'text-green-600 bg-green-50 border-green-200'
    case 'SOLD':
      return 'text-emerald-600 bg-emerald-50 border-emerald-200'
    case 'FLAGGED':
      return 'text-red-600 bg-red-50 border-red-200'
    default:
      return 'text-gray-600 bg-gray-50 border-gray-200'
  }
}

export function getRoleColor(role: string): string {
  switch (role) {
    case 'farmer':
      return 'text-green-600 bg-green-50 border-green-200'
    case 'admin':
      return 'text-purple-600 bg-purple-50 border-purple-200'
    case 'consumer':
      return 'text-blue-600 bg-blue-50 border-blue-200'
    default:
      return 'text-gray-600 bg-gray-50 border-gray-200'
  }
}

export function getRiskColor(riskLevel: string): string {
  switch (riskLevel) {
    case 'LOW':
      return 'text-green-600 bg-green-50 border-green-200'
    case 'MEDIUM':
      return 'text-yellow-600 bg-yellow-50 border-yellow-200'
    case 'HIGH':
      return 'text-red-600 bg-red-50 border-red-200'
    default:
      return 'text-gray-600 bg-gray-50 border-gray-200'
  }
}

export function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
}

export function truncateHash(hash: string | null | undefined, startChars: number = 8, endChars: number = 8): string {
  if (!hash) return 'N/A'
  if (hash.length <= startChars + endChars + 3) return hash
  return hash.substring(0, startChars) + '...' + hash.substring(hash.length - endChars)
}

export function generateId(): string {
  return Math.random().toString(36).substring(2) + Date.now().toString(36)
}

export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: ReturnType<typeof setTimeout> | null = null
  return (...args: Parameters<T>) => {
    if (timeout) clearTimeout(timeout)
    timeout = setTimeout(() => func(...args), wait)
  }
}

export function capitalizeFirst(str: string): string {
  return str.charAt(0).toUpperCase() + str.slice(1)
}

export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes'
  
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

export function isValidEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

export function isValidPhone(phone: string): boolean {
  const phoneRegex = /^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}$/
  return phoneRegex.test(phone)
}

export function getProductTypeIcon(productType: string): string {
  switch (productType) {
    case 'coffee':
      return '☕'
    case 'tea':
      return '🍵'
    case 'spice':
      return '🌶️'
    case 'millet':
      return '🌾'
    case 'organic':
      return '🌿'
    default:
      return '📦'
  }
}

export function getProductTypeColor(productType: string): string {
  switch (productType) {
    case 'coffee':
      return 'text-amber-600 bg-amber-50 border-amber-200'
    case 'tea':
      return 'text-green-600 bg-green-50 border-green-200'
    case 'spice':
      return 'text-red-600 bg-red-50 border-red-200'
    case 'millet':
      return 'text-yellow-600 bg-yellow-50 border-yellow-200'
    case 'organic':
      return 'text-emerald-600 bg-emerald-50 border-emerald-200'
    default:
      return 'text-gray-600 bg-gray-50 border-gray-200'
  }
}
