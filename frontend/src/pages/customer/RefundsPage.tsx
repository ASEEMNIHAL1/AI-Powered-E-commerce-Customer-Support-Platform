import { useQuery } from '@tanstack/react-query'
import Layout from '../../components/Layout'
import { Badge, statusColor, formatRupees, LoadingSpinner, EmptyState } from '../../components/ui'
import { refundsApi } from '../../services/endpoints'
import { format } from 'date-fns'

export default function RefundsPage() {
  const { data: refunds, isLoading } = useQuery({
    queryKey: ['refunds'],
    queryFn: () => refundsApi.list().then(r => r.data),
  })

  return (
    <Layout title="My Refunds">
      {isLoading ? <LoadingSpinner /> :
       (refunds?.length ?? 0) === 0 ? <EmptyState message="No refund requests found." /> : (
        <div className="space-y-4">
          {refunds!.map(refund => (
            <div key={refund.id} className="card">
              <div className="flex items-start justify-between">
                <div>
                  <p className="font-semibold">Refund #{refund.id} · Order #{refund.order_id}</p>
                  <p className="text-sm text-gray-600 mt-1">{refund.reason}</p>
                  <p className="text-xs text-gray-400 mt-1">{format(new Date(refund.created_at), 'MMM d, yyyy')}</p>
                  {refund.review_note && (
                    <div className="mt-2 p-2 bg-gray-50 rounded text-sm text-gray-700">
                      <span className="font-medium">Review Note:</span> {refund.review_note}
                    </div>
                  )}
                </div>
                <div className="text-right">
                  <p className="font-bold text-lg">{formatRupees(refund.amount_paise)}</p>
                  <Badge color={statusColor(refund.status)}>{refund.status}</Badge>
                  {refund.status === 'escalated' && (
                    <p className="text-xs text-orange-600 mt-1">Under human review</p>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </Layout>
  )
}
