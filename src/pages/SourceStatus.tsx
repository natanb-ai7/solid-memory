import { useMemo, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { fetchSourceStatus } from '../api/client'
import { SourceRecord } from '../api/types'
import StatusBadge from '../components/StatusBadge'

function SourceStatus() {
  const { data, isLoading, isError } = useQuery<SourceRecord[]>({
    queryKey: ['sources'],
    queryFn: fetchSourceStatus,
  })
  const [sortKey, setSortKey] = useState<'make' | 'region' | 'freshnessMinutes'>('freshnessMinutes')

  const sorted = useMemo(() => {
    if (!data) return []
    return [...data].sort((a, b) => {
      const first = a[sortKey]
      const second = b[sortKey]
      if (first < second) return -1
      if (first > second) return 1
      return 0
    })
  }, [data, sortKey])

  return (
    <section className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm uppercase tracking-wide text-slate-500">Source reliability</p>
          <h1 className="text-2xl font-bold text-slate-900">Source status</h1>
          <p className="text-slate-600">Data freshness badges per make/region with client-side caching.</p>
        </div>
        <div className="controls">
          <div>
            <label htmlFor="sort">Sort by</label>
            <select id="sort" value={sortKey} onChange={(e) => setSortKey(e.target.value as typeof sortKey)}>
              <option value="freshnessMinutes">Freshness (minutes)</option>
              <option value="make">Make</option>
              <option value="region">Region</option>
            </select>
          </div>
        </div>
      </div>

      {isLoading && <p>Loading source status…</p>}
      {isError && <p className="text-red-600">Unable to load source status.</p>}

      <div className="grid">
        {sorted.map((source) => (
          <div key={`${source.make}-${source.region}`} className="card">
            <div className="text-sm uppercase tracking-wide text-slate-500">{source.make}</div>
            <div className="text-lg font-semibold text-slate-900">{source.region}</div>
            <div className="text-sm text-slate-500">Updated {new Date(source.lastUpdated).toLocaleString()}</div>
            <div className="mt-2">
              <StatusBadge lastUpdated={source.lastUpdated} make={source.make} region={source.region} />
            </div>
          </div>
        ))}
      </div>
    </section>
  )
}

export default SourceStatus
