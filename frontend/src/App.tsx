import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './stores/authStore'
import LoginPage from './pages/auth/LoginPage'
import RegisterPage from './pages/auth/RegisterPage'
import CustomerDashboard from './pages/customer/Dashboard'
import OrdersPage from './pages/customer/OrdersPage'
import OrderDetailPage from './pages/customer/OrderDetailPage'
import TicketsPage from './pages/customer/TicketsPage'
import TicketDetailPage from './pages/customer/TicketDetailPage'
import CreateTicketPage from './pages/customer/CreateTicketPage'
import RefundsPage from './pages/customer/RefundsPage'
import SupportDashboard from './pages/support/SupportDashboard'
import SupportTicketsPage from './pages/support/SupportTicketsPage'
import SupportTicketDetail from './pages/support/SupportTicketDetail'
import EscalationsPage from './pages/support/EscalationsPage'

function RequireAuth({ children }: { children: React.ReactNode }) {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated)
  if (!isAuthenticated()) return <Navigate to="/login" replace />
  return <>{children}</>
}

function RequireStaff({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isStaff } = useAuthStore()
  if (!isAuthenticated()) return <Navigate to="/login" replace />
  if (!isStaff()) return <Navigate to="/dashboard" replace />
  return <>{children}</>
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />

        {/* Customer routes */}
        <Route path="/dashboard" element={<RequireAuth><CustomerDashboard /></RequireAuth>} />
        <Route path="/orders" element={<RequireAuth><OrdersPage /></RequireAuth>} />
        <Route path="/orders/:id" element={<RequireAuth><OrderDetailPage /></RequireAuth>} />
        <Route path="/tickets" element={<RequireAuth><TicketsPage /></RequireAuth>} />
        <Route path="/tickets/new" element={<RequireAuth><CreateTicketPage /></RequireAuth>} />
        <Route path="/tickets/:id" element={<RequireAuth><TicketDetailPage /></RequireAuth>} />
        <Route path="/refunds" element={<RequireAuth><RefundsPage /></RequireAuth>} />

        {/* Support staff routes */}
        <Route path="/support" element={<RequireStaff><SupportDashboard /></RequireStaff>} />
        <Route path="/support/tickets" element={<RequireStaff><SupportTicketsPage /></RequireStaff>} />
        <Route path="/support/tickets/:id" element={<RequireStaff><SupportTicketDetail /></RequireStaff>} />
        <Route path="/support/escalations" element={<RequireStaff><EscalationsPage /></RequireStaff>} />

        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
