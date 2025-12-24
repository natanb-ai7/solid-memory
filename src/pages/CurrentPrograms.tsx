import { useMemo, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { fetchPrograms } from '../api/client'
import { Program } from '../api/types'
import FilterBar from '../components/FilterBar'
import ProgramsTable from '../components/ProgramsTable'
import CSVButton from '../components/CSVButton'

function CurrentPrograms() {
  const { data, isLoading, isError, refetch, isFetching } = useQuery<Program[]>({
    queryKey: ['programs'],
    queryFn: fetchPrograms,
  })
  const [search, setSearch] = useState('')
  const [make, setMake] = useState('')
  const [region, setRegion] = useState('')

  const filtered = useMemo(() => {
    if (!data) return []
    return data.filter((program) => {
      const matchesSearch = `${program.name} ${program.owner} ${program.status}`
        .toLowerCase()
        .includes(search.toLowerCase())
      const matchesMake = make ? program.make === make : true
      const matchesRegion = region ? program.region === region : true
      return matchesSearch && matchesMake && matchesRegion
    })
  }, [data, search, make, region])

  const makes = useMemo(() => [...new Set((data ?? []).map((p) => p.make))], [data])
  const regions = useMemo(() => [...new Set((data ?? []).map((p) => p.region))], [data])

  return (
    <section className="space-y-4">
      <header className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="text-sm uppercase tracking-wide text-slate-500">Programs</p>
          <h1 className="text-2xl font-bold text-slate-900">Current Programs</h1>
          <p className="text-slate-600">Sorted, filtered, and exportable program data with cached API responses.</p>
        </div>
        <div className="flex items-center gap-2">
          <CSVButton data={filtered} />
          <button className="button-primary" onClick={() => refetch()} disabled={isFetching}>
            {isFetching ? 'Refreshing…' : 'Refresh'}
          </button>
        </div>
      </header>

      <FilterBar
        search={search}
        onSearchChange={setSearch}
        make={make}
        region={region}
        makes={makes}
        regions={regions}
        onMakeChange={setMake}
        onRegionChange={setRegion}
      />

      {isLoading && <p>Loading programs…</p>}
      {isError && <p className="text-red-600">Unable to load programs.</p>}
      {!isLoading && !isError && <ProgramsTable programs={filtered} />}
    </section>
  )
}

export default CurrentPrograms
