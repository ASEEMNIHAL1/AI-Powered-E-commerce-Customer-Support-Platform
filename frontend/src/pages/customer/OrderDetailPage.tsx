import { useQuery } from '@tanstack/react-query'
import { useParams, Link } from 'react-router-dom'
import { ordersApi } from '../../services/endpoints'
import Layout from '../../components/Layout'
import { Badge, statusColor, formatRupees, LoadingSpinner } from '../../components/ui'
import { format } from 'date-fns'

export default function OrderDetailPage() {
  const { id } = useParams<{ id: string }>()
  const { data: order, isLoading } = useQuery({
    queryKey: ['order', id],
    queryFn: () => ordersApi.get(Number(id)).then(r => r.data),
  })

  return (
    <Layout title="Order Details">
      {isLoading ? <LoadingSpinner /> : !order ? <div>Order not found</div> : (
        <div className="max-w-2xl">
          <Link to="/orders" className="text-blue-600 hover:underline text-sm mb-4 block">← Back to Orders</Link>
          <div className="card">
            <div className="flex justify-between items-start mb-6">
              <div>
                <h2 className="text-xl font-semibold">{order.item_name}</h2>
                <p className="text-gray-500">Order #{order.id}</p>
              </div>
              <Badge color={statusColor(order.status)}>{order.status}</Badge>
            </div>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <p className="text-gray-500">Category</p>
                <p className="font-medium capitalize">{order.category}</p>
              </div>
              <div>
                <p className="text-gray-500">Amount</p>
                <p className="font-medium">{formatRupees(order.total_amount_paise)}</p>
              </div>
              <div>
                <p className="text-gray-500">Order Date</p>
                <p className="font-medium">{format(new Date(order.created_at), 'MMM d, yyyy')}</p>
              </div>
              <div>
                <p className="text-gray-500">Delivery Date</p>
                <p className="font-medium">
                  {order.delivery_date ? format(new Date(order.delivery_date), 'MMM d, yyyy') : 'Pending'}
                </p>
              </div>
            </div>
            <div className="mt-6 flex gap-3">
              <Link to={`/tickets/new?order=${order.id}`} className="btn-primary">
                Get Support for this Order
              </Link>
            </div>
          </div>
        </div>
      )}
    </Layout>
  )
}
