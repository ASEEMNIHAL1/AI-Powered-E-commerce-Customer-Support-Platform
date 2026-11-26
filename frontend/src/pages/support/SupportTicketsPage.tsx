import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { supportApi } from '../../services/endpoints'
import Layout from '../../components/Layout'
import { Badge, statusColor, priorityColor, LoadingSpinner, EmptyState } from '../../components/ui'
import { format } from 'date-fns'

export default function SupportTicketsPage() {
  const [statusFilter, setStatusFilter] = useState('')
  const [priorityFilter, setPriorityFilter] = useState('')

  const { data, isLoading } = useQuery({
    queryKey: ['support-tickets', statusFilter, priorityFilter],
    queryFn: () => supportApi.listTickets({
      status: statusFilter || undefined,
      priority: priorityFilter || undefined,
    }).then(r => r.data),
  })

  return (
    <Layout title="All Tickets">
      <div className="flex gap-4 mb-6">
        <select className="input w-40" value={statusFilter} onChange={e => setStatusFilter(e.target.value)}>
          <option value="">All Statuses</option>
          {['open', 'in_progress', 'awaiting_customer', 'escalated', 'resolved', 'closed'].map(s => (
            <option key={s} value={s}>{s.replace('_', ' ')}</option>
          ))}
        </select>
        <select className="input w-40" value={priorityFilter} onChange={e => setPriorityFilter(e.target.value)}>
          <option value="">All Priorities</option>
          {['low', 'medium', 'high', 'urgent'].map(p => <option key={p} value={p}>{p}</option>)}
        </select>
      </div>

      {isLoading ? <LoadingSpinner /> :
       (data?.items.length ?? 0) === 0 ? <EmptyState message="No tickets found." /> : (
        <div className="space-y-3">
          {data!.items.map(ticket => (
            <Link key={ticket.id} to={`/support/tickets/${ticket.id}`}
              className="card block hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-gray-400 text-sm">#{ticket.id}</span>
                    <h3 className="font-semibold">{ticket.subject}</h3>
                    <Badge color={priorityColor(ticket.priority)}>{ticket.priority}</Badge>
                  </div>
                  <p className="text-sm text-gray-500 mt-1 capitalize">{ticket.category}</p>
                  <p className="text-xs text-gray-400">{format(new Date(ticket.updated_at), 'MMM d, yyyy HH:mm')}</p>
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
