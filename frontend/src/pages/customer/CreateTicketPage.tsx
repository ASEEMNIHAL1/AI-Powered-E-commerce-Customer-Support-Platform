import { useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { ticketsApi, ordersApi } from '../../services/endpoints'
import Layout from '../../components/Layout'
import toast from 'react-hot-toast'

const CATEGORIES = ['refund', 'shipping', 'product', 'payment', 'account', 'other']
const PRIORITIES = ['low', 'medium', 'high', 'urgent']

export default function CreateTicketPage() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const qc = useQueryClient()

  const [subject, setSubject] = useState('')
  const [description, setDescription] = useState('')
  const [category, setCategory] = useState('other')
  const [priority, setPriority] = useState('medium')
  const [orderId, setOrderId] = useState(searchParams.get('order') || '')

  const { data: ordersData } = useQuery({
    queryKey: ['orders'],
    queryFn: () => ordersApi.list().then(r => r.data),
  })

  const mutation = useMutation({
    mutationFn: () => ticketsApi.create({
      subject, description, category, priority,
      order_id: orderId ? Number(orderId) : undefined,
    }),
    onSuccess: (resp) => {
      qc.invalidateQueries({ queryKey: ['tickets'] })
      toast.success('Ticket created!')
      navigate(`/tickets/${resp.data.id}`)
    },
    onError: (err: any) => toast.error(err.response?.data?.detail || 'Failed to create ticket'),
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!subject.trim()) { toast.error('Subject is required'); return }
    mutation.mutate()
  }

  return (
    <Layout title="Create Support Ticket">
      <div className="max-w-2xl">
        <div className="card">
          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Subject *</label>
              <input type="text" className="input" value={subject} onChange={e => setSubject(e.target.value)} required placeholder="Briefly describe your issue" />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Category</label>
                <select className="input" value={category} onChange={e => setCategory(e.target.value)}>
                  {CATEGORIES.map(c => <option key={c} value={c} className="capitalize">{c}</option>)}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Priority</label>
                <select className="input" value={priority} onChange={e => setPriority(e.target.value)}>
                  {PRIORITIES.map(p => <option key={p} value={p} className="capitalize">{p}</option>)}
                </select>
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Related Order (optional)</label>
              <select className="input" value={orderId} onChange={e => setOrderId(e.target.value)}>
                <option value="">No specific order</option>
                {ordersData?.items.map(o => (
                  <option key={o.id} value={o.id}>#{o.id} – {o.item_name}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Description *</label>
              <textarea className="input min-h-[120px] resize-y" value={description} onChange={e => setDescription(e.target.value)} required placeholder="Please provide details about your issue..." />
            </div>
            <div className="flex gap-3">
              <button type="submit" className="btn-primary" disabled={mutation.isPending}>
                {mutation.isPending ? 'Creating...' : 'Create Ticket'}
              </button>
              <button type="button" className="btn-secondary" onClick={() => navigate('/tickets')}>Cancel</button>
            </div>
          </form>
        </div>
      </div>
    </Layout>
  )
}
