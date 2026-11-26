// Shared Layout component with nav
import { Link, useNavigate } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'
import type { ReactNode } from 'react'

export default function Layout({ children, title }: { children: ReactNode; title?: string }) {
  const { user, logout, isStaff } = useAuthStore()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
            <div className="flex items-center gap-6">
              <Link to="/dashboard" className="text-xl font-bold text-blue-600">🛍 ShopEasy</Link>
              {isStaff() ? (
                <>
                  <Link to="/support" className="text-sm text-gray-600 hover:text-blue-600">Dashboard</Link>
                  <Link to="/support/tickets" className="text-sm text-gray-600 hover:text-blue-600">Tickets</Link>
                  <Link to="/support/escalations" className="text-sm text-gray-600 hover:text-blue-600">Escalations</Link>
                </>
              ) : (
                <>
                  <Link to="/dashboard" className="text-sm text-gray-600 hover:text-blue-600">Dashboard</Link>
                  <Link to="/orders" className="text-sm text-gray-600 hover:text-blue-600">Orders</Link>
                  <Link to="/tickets" className="text-sm text-gray-600 hover:text-blue-600">Support</Link>
                  <Link to="/refunds" className="text-sm text-gray-600 hover:text-blue-600">Refunds</Link>
                </>
              )}
            </div>
            <div className="flex items-center gap-4">
              <span className="text-sm text-gray-600">{user?.name}</span>
              <span className="badge bg-blue-100 text-blue-700 capitalize">{user?.role}</span>
              <button onClick={handleLogout} className="text-sm text-red-600 hover:underline">Logout</button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {title && <h1 className="text-2xl font-bold text-gray-900 mb-6">{title}</h1>}
        {children}
      </main>
    </div>
  )
}
