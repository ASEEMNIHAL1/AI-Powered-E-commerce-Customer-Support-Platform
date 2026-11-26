// Shared UI components
import clsx from 'clsx'
import type { ReactNode } from 'react'

export function Badge({ children, color = 'gray' }: { children: ReactNode; color?: string }) {
  const colors: Record<string, string> = {
    gray: 'bg-gray-100 text-gray-700',
    blue: 'bg-blue-100 text-blue-700',
    green: 'bg-green-100 text-green-700',
    red: 'bg-red-100 text-red-700',
    yellow: 'bg-yellow-100 text-yellow-700',
    orange: 'bg-orange-100 text-orange-700',
    purple: 'bg-purple-100 text-purple-700',
  }
  return (
    <span className={clsx('badge', colors[color] || colors.gray)}>
      {children}
    </span>
  )
}

export function statusColor(status: string): string {
  const map: Record<string, string> = {
    open: 'blue', in_progress: 'yellow', escalated: 'orange',
    resolved: 'green', closed: 'gray', awaiting_customer: 'purple',
    pending: 'yellow', approved: 'green', rejected: 'red',
    delivered: 'green', shipped: 'blue', confirmed: 'blue',
    pending_order: 'yellow', cancelled: 'red', returned: 'gray',
  }
  return map[status] || 'gray'
}

export function priorityColor(priority: string): string {
  const map: Record<string, string> = {
    low: 'gray', medium: 'blue', high: 'orange', urgent: 'red',
  }
  return map[priority] || 'gray'
}

export function LoadingSpinner() {
  return (
    <div className="flex items-center justify-center p-8">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
    </div>
  )
}

export function ErrorMessage({ message }: { message: string }) {
  return (
    <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
      {message}
    </div>
  )
}

export function EmptyState({ message }: { message: string }) {
  return (
    <div className="text-center text-gray-500 py-12">
      <p className="text-lg">{message}</p>
    </div>
  )
}

export function formatRupees(paise: number): string {
  return `₹${(paise / 100).toLocaleString('en-IN', { minimumFractionDigits: 2 })}`
}
