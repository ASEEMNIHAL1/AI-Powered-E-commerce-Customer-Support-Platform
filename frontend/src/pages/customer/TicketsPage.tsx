import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { ticketsApi } from '../../services/endpoints'
import Layout from '../../components/Layout'
import { Badge, statusColor, priorityColor, LoadingSpinner, EmptyState } from '../../components/ui'
import { format } from 'date-fns'

export default function TicketsPage() {
  const { data, isLoading } = useQuery({
    queryKey: ['tickets'],
    queryFn: () => ticketsApi.list().then(r => r.data),
  })

  return (
    <Layout title="Support Tickets">
      <div className="flex justify-between items-center mb-6">
        <div />
        <Link to="/tickets/new" className="btn-primary">+ New Ticket</Link>
      </div>
      {isLoading ? <LoadingSpinner /> :
       (data?.items.length ?? 0) === 0 ? <EmptyState message="No tickets yet. Create one to get support!" /> : (
        <div className="space-y-4">
          {data!.items.map(ticket => (
            <Link key={ticket.id} to={`/tickets/${ticket.id}`}
              className="card block hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <h3 className="font-semibold">{ticket.subject}</h3>
                    <Badge color={priorityColor(ticket.priority)}>{ticket.priority}</Badge>
                  </div>
                  <p className="text-sm text-gray-500 capitalize">{ticket.category} · #{ticket.id}</p>
                  <p className="text-xs text-gray-400 mt-1">{format(new Date(ticket.updated_at), 'MMM d, yyyy HH:mm')}</p>
                </div>
                <Badge color={statusColor(ticket.status)}>{ticket.status.replace('_', ' ')}</Badge>
              </div>
            </Link>
          ))}
        </div>
      )}
    </Layout>
  )
}
