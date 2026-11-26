import { useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { supportApi, messagesApi } from '../../services/endpoints'
import Layout from '../../components/Layout'
import { Badge, statusColor, priorityColor, LoadingSpinner, formatRupees } from '../../components/ui'
import { format } from 'date-fns'
import toast from 'react-hot-toast'

export default function SupportTicketDetail() {
  const { id } = useParams<{ id: string }>()
  const qc = useQueryClient()
  const [note, setNote] = useState('')
  const [status, setStatus] = useState('')

  const { data: ticket } = useQuery({
    queryKey: ['support-ticket', id],
    queryFn: () => supportApi.getTicket(Number(id)).then(r => r.data),
  })
  const { data: messages = [], isLoading } = useQuery({
    queryKey: ['messages-support', id],
    queryFn: () => messagesApi.list(Number(id)).then(r => r.data),
  })
  const { data: notes = [] } = useQuery({
    queryKey: ['notes', id],
    queryFn: () => supportApi.getNotes(Number(id)).then(r => r.data),
  })

  const updateMutation = useMutation({
    mutationFn: () => supportApi.updateTicket(Number(id), { status }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['support-ticket', id] }); toast.success('Status updated') },
    onError: () => toast.error('Update failed'),
  })

  const noteMutation = useMutation({
    mutationFn: () => supportApi.addNote(Number(id), note),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['notes', id] }); setNote(''); toast.success('Note added') },
    onError: () => toast.error('Failed to add note'),
  })

  return (
    <Layout>
      <Link to="/support/tickets" className="text-blue-600 hover:underline text-sm mb-4 block">← Back to Tickets</Link>

      {ticket && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-4">
            {/* Ticket header */}
            <div className="card">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h2 className="text-xl font-semibold">{ticket.subject}</h2>
                  <p className="text-gray-500 text-sm">#{ticket.id} · {ticket.category} · Customer #{ticket.customer_id}</p>
                </div>
                <div className="flex gap-2">
                  <Badge color={priorityColor(ticket.priority)}>{ticket.priority}</Badge>
                  <Badge color={statusColor(ticket.status)}>{ticket.status.replace('_', ' ')}</Badge>
                </div>
              </div>
              <p className="text-gray-700">{ticket.description}</p>
            </div>

            {/* Conversation */}
            <div className="card">
              <h3 className="font-semibold mb-4">Conversation</h3>
              {isLoading ? <LoadingSpinner /> :
               messages.length === 0 ? <p className="text-gray-400 text-sm">No messages yet.</p> : (
                <div className="space-y-3 max-h-80 overflow-y-auto">
                  {messages.map((msg: any) => (
                    <div key={msg.id} className={`p-3 rounded-lg text-sm ${
                      msg.sender_type === 'customer' ? 'bg-blue-50 border-l-2 border-blue-400' :
                      'bg-gray-50 border-l-2 border-gray-300'
                    }`}>
                      <div className="flex justify-between items-center mb-1">
                        <span className="font-medium capitalize text-xs">{msg.sender_type}</span>
                        <span className="text-gray-400 text-xs">{format(new Date(msg.created_at), 'MMM d HH:mm')}</span>
                      </div>
                      <p className="whitespace-pre-wrap">{msg.content}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-4">
            {/* Status update */}
            <div className="card">
              <h3 className="font-semibold mb-3">Update Status</h3>
              <select className="input mb-3" value={status} onChange={e => setStatus(e.target.value)}>
                <option value="">Select status...</option>
                {['open', 'in_progress', 'awaiting_customer', 'escalated', 'resolved', 'closed'].map(s => (
                  <option key={s} value={s}>{s.replace('_', ' ')}</option>
                ))}
              </select>
              <button className="btn-primary w-full" disabled={!status || updateMutation.isPending}
                onClick={() => updateMutation.mutate()}>
                Update
              </button>
            </div>

            {/* Internal Notes */}
            <div className="card">
              <h3 className="font-semibold mb-3">Internal Notes</h3>
              <div className="space-y-2 mb-3 max-h-40 overflow-y-auto">
                {notes.map((n: any) => (
                  <div key={n.id} className="p-2 bg-yellow-50 border border-yellow-200 rounded text-sm">
                    <p>{n.content}</p>
                    <p className="text-xs text-gray-400 mt-1">{format(new Date(n.created_at), 'MMM d HH:mm')}</p>
                  </div>
                ))}
              </div>
              <textarea className="input resize-none mb-2" rows={3} placeholder="Add an internal note..." value={note} onChange={e => setNote(e.target.value)} />
              <button className="btn-secondary w-full" disabled={!note.trim() || noteMutation.isPending}
                onClick={() => noteMutation.mutate()}>
                Add Note
              </button>
            </div>
          </div>
        </div>
      )}
    </Layout>
  )
}
