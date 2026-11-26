import api from './api'
import type { User, TokenResponse, Order, Ticket, Message, Refund, Escalation, Note } from '../types'

// Auth
export const authApi = {
  register: (name: string, email: string, password: string) =>
    api.post<User>('/auth/register', { name, email, password }),
  login: (email: string, password: string) =>
    api.post<TokenResponse>('/auth/login', { email, password }),
  me: () => api.get<User>('/auth/me'),
}

// Orders
export const ordersApi = {
  list: () => api.get<{ items: Order[]; total: number }>('/orders'),
  get: (id: number) => api.get<Order>(`/orders/${id}`),
}

// Tickets
export const ticketsApi = {
  create: (data: { subject: string; description: string; category: string; order_id?: number; priority?: string }) =>
    api.post<Ticket>('/tickets', data),
  list: () => api.get<{ items: Ticket[]; total: number }>('/tickets'),
  get: (id: number) => api.get<Ticket>(`/tickets/${id}`),
  update: (id: number, data: { status?: string; priority?: string }) =>
    api.patch<Ticket>(`/tickets/${id}`, data),
}

// Messages & Chat
export const messagesApi = {
  list: (ticketId: number) => api.get<Message[]>(`/tickets/${ticketId}/messages`),
  chat: (ticketId: number, content: string) =>
    api.post<Message>(`/tickets/${ticketId}/chat`, { content }),
}

// Refunds
export const refundsApi = {
  create: (data: { order_id: number; ticket_id: number; amount_paise: number; reason: string }) =>
    api.post<Refund>('/refunds', data),
  list: () => api.get<Refund[]>('/refunds'),
  get: (id: number) => api.get<Refund>(`/refunds/${id}`),
}

// Support (staff only)
export const supportApi = {
  listTickets: (params?: { status?: string; priority?: string }) =>
    api.get<{ items: Ticket[]; total: number }>('/support/tickets', { params }),
  getTicket: (id: number) => api.get<Ticket>(`/support/tickets/${id}`),
  updateTicket: (id: number, data: { status?: string; priority?: string }) =>
    api.patch<Ticket>(`/support/tickets/${id}`, data),
  listEscalations: () => api.get<Escalation[]>('/support/escalations'),
  decideEscalation: (id: number, data: { decision: string; note?: string; refund_decision?: string }) =>
    api.post<Escalation>(`/support/escalations/${id}/decision`, data),
  addNote: (ticketId: number, content: string) =>
    api.post<Note>(`/support/tickets/${ticketId}/notes`, { content }),
  getNotes: (ticketId: number) => api.get<Note[]>(`/support/tickets/${ticketId}/notes`),
}
