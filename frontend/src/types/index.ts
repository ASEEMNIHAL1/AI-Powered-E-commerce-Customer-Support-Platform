// Shared TypeScript types

export interface User {
  id: number
  name: string
  email: string
  role: 'customer' | 'staff' | 'admin'
  created_at: string
}

export interface Order {
  id: number
  customer_id: number
  status: 'pending' | 'confirmed' | 'shipped' | 'delivered' | 'cancelled' | 'returned'
  item_name: string
  category: 'electronics' | 'clothing' | 'food' | 'books' | 'home' | 'other'
  total_amount_paise: number
  delivery_date: string | null
  created_at: string
}

export interface Ticket {
  id: number
  customer_id: number
  order_id: number | null
  subject: string
  description: string
  category: 'refund' | 'shipping' | 'product' | 'payment' | 'account' | 'other'
  status: 'open' | 'in_progress' | 'awaiting_customer' | 'escalated' | 'resolved' | 'closed'
  priority: 'low' | 'medium' | 'high' | 'urgent'
  created_at: string
  updated_at: string
}

export interface Message {
  id: number
  ticket_id: number
  sender_type: 'customer' | 'agent' | 'system'
  sender_id: number | null
  content: string
  created_at: string
}

export interface Refund {
  id: number
  order_id: number
  ticket_id: number
  amount_paise: number
  reason: string
  status: 'pending' | 'approved' | 'rejected' | 'escalated' | 'cancelled'
  idempotency_key: string
  requested_by: number
  reviewed_by: number | null
  review_note: string | null
  created_at: string
  updated_at: string
}

export interface Escalation {
  id: number
  ticket_id: number
  refund_id: number | null
  summary: string
  priority: 'low' | 'medium' | 'high' | 'urgent'
  status: 'open' | 'under_review' | 'approved' | 'rejected' | 'more_info_requested' | 'resolved'
  assigned_to: number | null
  decision_note: string | null
  created_at: string
  updated_at: string
}

export interface Note {
  id: number
  ticket_id: number
  author_id: number
  content: string
  created_at: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
}
