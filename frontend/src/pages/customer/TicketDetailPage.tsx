import { useState, useRef, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { ticketsApi, messagesApi } from '../../services/endpoints'
import Layout from '../../components/Layout'
import { Badge, statusColor, LoadingSpinner } from '../../components/ui'
import { useAuthStore } from '../../stores/authStore'
import { format } from 'date-fns'
import toast from 'react-hot-toast'
import type { Message } from '../../types'

export default function TicketDetailPage() {
  const { id } = useParams<{ id: string }>()
  const { user } = useAuthStore()
  const qc = useQueryClient()
  const [input, setInput] = useState('')
  const bottomRef = useRef<HTMLDivElement>(null)

  const { data: ticket } = useQuery({
    queryKey: ['ticket', id],
    queryFn: () => ticketsApi.get(Number(id)).then(r => r.data),
  })

  const { data: messages = [], isLoading } = useQuery({
    queryKey: ['messages', id],
    queryFn: () => messagesApi.list(Number(id)).then(r => r.data),
    refetchInterval: 5000,
  })

  const chatMutation = useMutation({
    mutationFn: (content: string) => messagesApi.chat(Number(id), content),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['messages', id] }),
    onError: (err: any) => toast.error(err.response?.data?.detail || 'Failed to send message'),
  })

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSend = () => {
    if (!input.trim()) return
    chatMutation.mutate(input.trim())
    setInput('')
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend() }
  }

  return (
    <Layout>
      <div className="max-w-4xl">
        <Link to="/tickets" className="text-blue-600 hover:underline text-sm mb-4 block">← Back to Tickets</Link>

        {ticket && (
          <div className="card mb-4">
            <div className="flex items-start justify-between">
              <div>
                <h2 className="text-xl font-semibold">{ticket.subject}</h2>
                <p className="text-gray-500 text-sm mt-1 capitalize">
                  {ticket.category} · Ticket #{ticket.id}
                  {ticket.order_id && ` · Order #${ticket.order_id}`}
                </p>
                <p className="text-sm text-gray-600 mt-2">{ticket.description}</p>
              </div>
              <Badge color={statusColor(ticket.status)}>{ticket.status.replace('_', ' ')}</Badge>
            </div>
          </div>
        )}

        {/* Chat */}
        <div className="card flex flex-col" style={{ height: '500px' }}>
          <div className="flex-1 overflow-y-auto space-y-3 pb-4">
            {isLoading ? <LoadingSpinner /> :
             messages.length === 0 ? (
              <div className="text-center text-gray-400 py-8">
                <p>Start a conversation with our AI support agent.</p>
                <p className="text-sm mt-1">Type your question below.</p>
              </div>
            ) : messages.map((msg: Message) => (
              <div key={msg.id} className={`flex ${msg.sender_type === 'customer' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[70%] rounded-2xl px-4 py-2 ${
                  msg.sender_type === 'customer'
                    ? 'bg-blue-600 text-white rounded-br-sm'
                    : msg.sender_type === 'agent'
                    ? 'bg-gray-100 text-gray-900 rounded-bl-sm'
                    : 'bg-yellow-50 text-yellow-800 text-xs rounded-lg border border-yellow-200'
                }`}>
                  <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                  <p className={`text-xs mt-1 ${msg.sender_type === 'customer' ? 'text-blue-200' : 'text-gray-400'}`}>
                    {msg.sender_type === 'agent' ? '🤖 AI Agent · ' : ''}
                    {format(new Date(msg.created_at), 'HH:mm')}
                  </p>
                </div>
              </div>
            ))}
            {chatMutation.isPending && (
              <div className="flex justify-start">
                <div className="bg-gray-100 rounded-2xl px-4 py-2">
                  <div className="flex gap-1 items-center">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                  </div>
                </div>
              </div>
            )}
            <div ref={bottomRef} />
          </div>
          <div className="border-t pt-3 flex gap-2">
            <textarea
              className="input resize-none flex-1"
              rows={2}
              placeholder="Type your message... (Enter to send)"
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={chatMutation.isPending}
            />
            <button className="btn-primary self-end" onClick={handleSend} disabled={chatMutation.isPending || !input.trim()}>
              Send
            </button>
          </div>
        </div>
      </div>
    </Layout>
  )
}
