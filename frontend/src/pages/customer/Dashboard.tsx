import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { ordersApi, ticketsApi, refundsApi } from '../../services/endpoints'
import { useAuthStore } from '../../stores/authStore'
import Layout from '../../components/Layout'
import { Badge, statusColor, formatRupees, LoadingSpinner } from '../../components/ui'

export default function CustomerDashboard() {
  const { user } = useAuthStore()
  const { data: ordersData, isLoading: ordersLoading } = useQuery({
    queryKey: ['orders'],
    queryFn: () => ordersApi.list().then(r => r.data),
  })
  const { data: ticketsData, isLoading: ticketsLoading } = useQuery({
    queryKey: ['tickets'],
    queryFn: () => ticketsApi.list().then(r => r.data),
  })
  const { data: refunds } = useQuery({
    queryKey: ['refunds'],
    queryFn: () => refundsApi.list().then(r => r.data),
  })

  const recentOrders = ordersData?.items.slice(0, 3) ?? []
  const openTickets = ticketsData?.items.filter(t => !['resolved', 'closed'].includes(t.status)) ?? []
  const activeRefunds = refunds?.filter(r => r.status !== 'rejected' && r.status !== 'cancelled') ?? []

  return (
    <Layout title={`Welcome back, ${user?.name}! 👋`}>
      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="card text-center">
          <div className="text-3xl font-bold text-blue-600">{ordersData?.total ?? 0}</div>
          <div className="text-gray-600 mt-1">Total Orders</div>
          <Link to="/orders" className="text-sm text-blue-600 hover:underline mt-2 block">View all →</Link>
        </div>
        <div className="card text-center">
          <div className="text-3xl font-bold text-orange-500">{openTickets.length}</div>
          <div className="text-gray-600 mt-1">Open Tickets</div>
          <Link to="/tickets" className="text-sm text-blue-600 hover:underline mt-2 block">View all →</Link>
        </div>
        <div className="card text-center">
          <div className="text-3xl font-bold text-green-600">{activeRefunds.length}</div>
          <div className="text-gray-600 mt-1">Active Refunds</div>
          <Link to="/refunds" className="text-sm text-blue-600 hover:underline mt-2 block">View all →</Link>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="card mb-6">
        <h2 className="text-lg font-semibold mb-4">Quick Actions</h2>
        <div className="flex gap-3 flex-wrap">
          <Link to="/tickets/new" className="btn-primary">+ New Support Ticket</Link>
          <Link to="/orders" className="btn-secondary">View Orders</Link>
          <Link to="/refunds" className="btn-secondary">Track Refunds</Link>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Orders */}
        <div className="card">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-semibold">Recent Orders</h2>
            <Link to="/orders" className="text-sm text-blue-600 hover:underline">See all</Link>
          </div>
          {ordersLoading ? <LoadingSpinner /> : recentOrders.length === 0 ? (
            <p className="text-gray-500 text-sm">No orders yet.</p>
          ) : (
            <div className="space-y-3">
              {recentOrders.map(order => (
                <Link key={order.id} to={`/orders/${order.id}`}
                  className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition">
                  <div>
                    <p className="font-medium text-sm">{order.item_name}</p>
                    <p className="text-xs text-gray-500">{formatRupees(order.total_amount_paise)}</p>
                  </div>
                  <Badge color={statusColor(order.status)}>{order.status}</Badge>
                </Link>
              ))}
            </div>
          )}
        </div>

        {/* Open Tickets */}
        <div className="card">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-semibold">Open Tickets</h2>
            <Link to="/tickets" className="text-sm text-blue-600 hover:underline">See all</Link>
          </div>
          {ticketsLoading ? <LoadingSpinner /> : openTickets.length === 0 ? (
            <p className="text-gray-500 text-sm">No open tickets.</p>
          ) : (
            <div className="space-y-3">
              {openTickets.slice(0, 4).map(ticket => (
                <Link key={ticket.id} to={`/tickets/${ticket.id}`}
                  className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition">
                  <div>
                    <p className="font-medium text-sm truncate max-w-[200px]">{ticket.subject}</p>
                    <p className="text-xs text-gray-500 capitalize">{ticket.category}</p>
                  </div>
                  <Badge color={statusColor(ticket.status)}>{ticket.status.replace('_', ' ')}</Badge>
                </Link>
              ))}
            </div>
          )}
        </div>
      </div>
    </Layout>
  )
}
