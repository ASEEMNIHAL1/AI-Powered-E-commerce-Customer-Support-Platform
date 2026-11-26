import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { ordersApi } from '../../services/endpoints'
import Layout from '../../components/Layout'
import { Badge, statusColor, formatRupees, LoadingSpinner, EmptyState } from '../../components/ui'
import { format } from 'date-fns'

export default function OrdersPage() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['orders'],
    queryFn: () => ordersApi.list().then(r => r.data),
  })

  return (
    <Layout title="My Orders">
      {isLoading ? <LoadingSpinner /> :
       error ? <div className="text-red-600">Failed to load orders</div> :
       (data?.items.length ?? 0) === 0 ? <EmptyState message="No orders yet." /> : (
        <div className="space-y-4">
          {data!.items.map(order => (
            <Link key={order.id} to={`/orders/${order.id}`}
              className="card block hover:shadow-md transition-shadow">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-semibold">{order.item_name}</h3>
                  <p className="text-sm text-gray-500 mt-1">Order #{order.id} · {order.category}</p>
                  <p className="text-sm text-gray-500">
                    {order.delivery_date
                      ? `Delivered: ${format(new Date(order.delivery_date), 'MMM d, yyyy')}`
                      : 'Not yet delivered'}
                  </p>
                </div>
                <div className="text-right">
                  <p className="font-semibold text-lg">{formatRupees(order.total_amount_paise)}</p>
                  <Badge color={statusColor(order.status)}>{order.status}</Badge>
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </Layout>
  )
}
