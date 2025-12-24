import { useMemo, useState } from 'react'
import { Program } from '../api/types'
import StatusBadge from './StatusBadge'

interface TableProps {
  programs: Program[]
}

type SortKey = keyof Pick<Program, 'name' | 'make' | 'region' | 'status' | 'startDate'>

function ProgramsTable({ programs }: TableProps) {
  const [sortKey, setSortKey] = useState<SortKey>('name')
  const [direction, setDirection] = useState<'asc' | 'desc'>('asc')

  const sorted = useMemo(() => {
    const copy = [...programs]
    copy.sort((a, b) => {
      const first = a[sortKey]
      const second = b[sortKey]
      if (first < second) return direction === 'asc' ? -1 : 1
      if (first > second) return direction === 'asc' ? 1 : -1
      return 0
    })
    return copy
  }, [programs, sortKey, direction])

  const handleSort = (key: SortKey) => {
    if (sortKey === key) {
      setDirection((prev) => (prev === 'asc' ? 'desc' : 'asc'))
    } else {
      setSortKey(key)
      setDirection('asc')
    }
  }

  return (
    <table className="table">
      <thead>
        <tr>
          <th onClick={() => handleSort('name')}>Program</th>
          <th onClick={() => handleSort('make')}>Make</th>
          <th onClick={() => handleSort('region')}>Region</th>
          <th onClick={() => handleSort('status')}>Status</th>
          <th onClick={() => handleSort('startDate')}>Start</th>
          <th>Owner</th>
          <th>Data freshness</th>
        </tr>
      </thead>
      <tbody>
        {sorted.map((program) => (
          <tr key={program.id}>
            <td>
              <div className="font-semibold">{program.name}</div>
              <div className="text-sm text-slate-500">{program.id}</div>
            </td>
            <td>{program.make}</td>
            <td>{program.region}</td>
            <td>{program.status}</td>
            <td>{new Date(program.startDate).toLocaleDateString()}</td>
            <td>{program.owner}</td>
            <td>
              <StatusBadge lastUpdated={program.lastUpdated} make={program.make} region={program.region} />
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}

export default ProgramsTable
