import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { supportApi } from '../../services/endpoints'
import Layout from '../../components/Layout'
import { Badge, statusColor, priorityColor, LoadingSpinner, EmptyState, formatRupees } from '../../components/ui'
import { format } from 'date-fns'
import toast from 'react-hot-toast'

export default function EscalationsPage() {
  const qc = useQueryClient()
  const [decisions, setDecisions] = useState<Record<number, { decision: string; note: string; refund: string }>>({})

  const { data: escalations, isLoading } = useQuery({
    queryKey: ['escalations'],
    queryFn: () => supportApi.listEscalations().then(r => r.data),
  })

  const decideMutation = useMutation({
    mutationFn: ({ id, ...data }: any) => supportApi.decideEscalation(id, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['escalations'] })
      toast.success('Decision recorded')
    },
    onError: (err: any) => toast.error(err.response?.data?.detail || 'Decision failed'),
  })

  const getDecision = (id: number) => decisions[id] || { decision: '', note: '', refund: '' }
  const setDecision = (id: number, field: string, value: string) =>
    setDecisions(d => ({ ...d, [id]: { ...getDecision(id), [field]: value } }))

  return (
    <Layout title="Escalation Review Queue">
      {isLoading ? <LoadingSpinner /> :
       (escalations?.length ?? 0) === 0 ? <EmptyState message="No escalations pending." /> : (
        <div className="space-y-6">
          {escalations!.map(esc => {
            const d = getDecision(esc.id)
            return (
              <div key={esc.id} className="card">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <div className="flex items-center gap-2">
                      <h3 className="font-semibold">Escalation #{esc.id}</h3>
                      <Badge color={priorityColor(esc.priority)}>{esc.priority}</Badge>
                      <Badge color={statusColor(esc.status)}>{esc.status.replace('_', ' ')}</Badge>
                    </div>
                    <p className="text-sm text-gray-500 mt-1">
                      Ticket #{esc.ticket_id}
                      {esc.refund_id && ` · Refund #${esc.refund_id}`}
                    </p>
                    <p className="text-xs text-gray-400">{format(new Date(esc.created_at), 'MMM d, yyyy HH:mm')}</p>
                  </div>
                  <Link to={`/support/tickets/${esc.ticket_id}`} className="text-sm text-blue-600 hover:underline">
                    View Ticket →
                  </Link>
                </div>

                <div className="bg-orange-50 border border-orange-200 rounded-lg p-4 mb-4">
                  <p className="text-sm font-medium text-orange-800">Summary</p>
                  <p className="text-sm text-orange-700 mt-1">{esc.summary}</p>
                </div>

                {esc.decision_note && (
                  <div className="bg-gray-50 rounded p-3 text-sm mb-4">
                    <span className="font-medium">Previous decision:</span> {esc.decision_note}
                  </div>
                )}

                {esc.status === 'open' && (
                  <div className="border-t pt-4 space-y-3">
                    <div className="grid grid-cols-2 gap-3">
                      <div>
                        <label className="text-sm font-medium text-gray-700 mb-1 block">Decision</label>
                        <select className="input" value={d.decision} onChange={e => setDecision(esc.id, 'decision', e.target.value)}>
                          <option value="">Select...</option>
                          <option value="approved">Approve</option>
                          <option value="rejected">Reject</option>
                          <option value="more_info_requested">Request More Info</option>
                          <option value="resolved">Mark Resolved</option>
                        </select>
                      </div>
                      {esc.refund_id && (
                        <div>
                          <label className="text-sm font-medium text-gray-700 mb-1 block">Refund Decision</label>
                          <select className="input" value={d.refund} onChange={e => setDecision(esc.id, 'refund', e.target.value)}>
                            <option value="">No refund action</option>
                            <option value="approve">Approve Refund</option>
                            <option value="reject">Reject Refund</option>
                          </select>
                        </div>
                      )}
                    </div>
                    <textarea className="input resize-none" rows={2} placeholder="Decision note (optional)"
                      value={d.note} onChange={e => setDecision(esc.id, 'note', e.target.value)} />
                    <button className="btn-primary" disabled={!d.decision || decideMutation.isPending}
                      onClick={() => decideMutation.mutate({
                        id: esc.id,
                        decision: d.decision,
                        note: d.note || undefined,
                        refund_decision: d.refund || undefined,
                      })}>
                      Submit Decision
                    </button>
                  </div>
                )}
              </div>
            )
          })}
        </div>
      )}
    </Layout>
  )
}
