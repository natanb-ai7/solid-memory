import { useQuery } from '@tanstack/react-query'
import { fetchTimeline } from '../api/client'
import { TimelineEvent } from '../api/types'
import StatusBadge from '../components/StatusBadge'

function History() {
  const { data, isLoading, isError } = useQuery<TimelineEvent[]>({
    queryKey: ['timeline'],
    queryFn: fetchTimeline,
  })

  return (
    <section className="space-y-4">
      <div>
        <p className="text-sm uppercase tracking-wide text-slate-500">Events</p>
        <h1 className="text-2xl font-bold text-slate-900">History</h1>
        <p className="text-slate-600">Recent actions across programs with cached API reads.</p>
      </div>

      {isLoading && <p>Loading history…</p>}
      {isError && <p className="text-red-600">Unable to load history.</p>}

      <div className="space-y-3">
        {data?.map((event) => (
          <div key={event.id} className="card flex items-center justify-between">
            <div>
              <div className="text-sm uppercase tracking-wide text-slate-500">{event.programName}</div>
              <div className="font-semibold text-slate-900">{event.action}</div>
              <div className="text-sm text-slate-500">{new Date(event.happenedAt).toLocaleString()}</div>
            </div>
            <StatusBadge lastUpdated={event.happenedAt} make={event.programName} region={event.programId} />
          </div>
        ))}
      </div>
    </section>
  )
}

export default History
