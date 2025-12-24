import { useMemo } from 'react'

interface StatusBadgeProps {
  lastUpdated: string
  make: string
  region: string
}

function StatusBadge({ lastUpdated, make, region }: StatusBadgeProps) {
  const { label, tone } = useMemo(() => {
    const updated = new Date(lastUpdated).getTime()
    const now = Date.now()
    const diffMinutes = (now - updated) / 1000 / 60

    if (diffMinutes < 60) {
      return { label: `Fresh • ${Math.round(diffMinutes)}m ago`, tone: 'fresh' }
    }
    if (diffMinutes < 360) {
      return { label: `Warming • ${Math.round(diffMinutes)}m ago`, tone: 'warming' }
    }
    return { label: `Stale • ${Math.round(diffMinutes / 60)}h ago`, tone: 'stale' }
  }, [lastUpdated])

  return (
    <span className={`badge ${tone}`}>
      <span>🔄</span>
      <span>
        {label} — {make} / {region}
      </span>
    </span>
  )
}

export default StatusBadge
