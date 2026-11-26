import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import Layout from '../../components/Layout'
import { supportApi } from '../../services/endpoints'
import { LoadingSpinner } from '../../components/ui'

export default function SupportDashboard() {
  const { data: ticketsData } = useQuery({
    queryKey: ['support-tickets'],
    queryFn: () => supportApi.listTickets().then(r => r.data),
  })
  const { data: escalations } = useQuery({
    queryKey: ['escalations'],
    queryFn: () => supportApi.listEscalations().then(r => r.data),
  })

  const openTickets = ticketsData?.items.filter(t => t.status === 'open').length ?? 0
  const escalatedCount = ticketsData?.items.filter(t => t.status === 'escalated').length ?? 0
  const pendingEsc = escalations?.filter(e => e.status === 'open').length ?? 0

  return (
    <Layout title="Support Dashboard">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="card text-center">
          <div className="text-3xl font-bold text-blue-600">{ticketsData?.total ?? 0}</div>
          <div className="text-gray-600 mt-1">Total Tickets</div>
        </div>
        <div className="card text-center">
          <div className="text-3xl font-bold text-orange-500">{escalatedCount}</div>
          <div className="text-gray-600 mt-1">Escalated Tickets</div>
        </div>
        <div className="card text-center">
          <div className="text-3xl font-bold text-red-500">{pendingEsc}</div>
          <div className="text-gray-600 mt-1">Pending Escalation Reviews</div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="card">
          <h2 className="text-lg font-semibold mb-4">Quick Links</h2>
          <div className="space-y-3">
            <Link to="/support/tickets" className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100">
              <span>All Tickets</span>
              <span className="text-blue-600 font-semibold">{ticketsData?.total ?? 0}</span>
            </Link>
            <Link to="/support/escalations" className="flex items-center justify-between p-3 bg-orange-50 rounded-lg hover:bg-orange-100">
              <span>Escalation Review Queue</span>
              <span className="text-orange-600 font-semibold">{pendingEsc} pending</span>
            </Link>
          </div>
        </div>
        <div className="card">
          <h2 className="text-lg font-semibold mb-4">Recent Open Tickets</h2>
          {ticketsData?.items.filter(t => t.status === 'open').slice(0, 5).map(t => (
            <Link key={t.id} to={`/support/tickets/${t.id}`}
              className="block p-2 hover:bg-gray-50 rounded text-sm mb-2">
              <span className="font-medium">#{t.id}</span> – {t.subject}
            </Link>
          ))}
        </div>
      </div>
    </Layout>
  )
}
