interface FilterProps {
  search: string
  onSearchChange: (value: string) => void
  make: string
  region: string
  makes: string[]
  regions: string[]
  onMakeChange: (value: string) => void
  onRegionChange: (value: string) => void
}

function FilterBar({
  search,
  onSearchChange,
  make,
  region,
  makes,
  regions,
  onMakeChange,
  onRegionChange,
}: FilterProps) {
  return (
    <div className="controls">
      <div>
        <label htmlFor="search">Search</label>
        <input
          id="search"
          type="text"
          placeholder="Name, owner or status"
          value={search}
          onChange={(e) => onSearchChange(e.target.value)}
        />
      </div>
      <div>
        <label htmlFor="make">Make</label>
        <select id="make" value={make} onChange={(e) => onMakeChange(e.target.value)}>
          <option value="">All makes</option>
          {makes.map((m) => (
            <option key={m} value={m}>
              {m}
            </option>
          ))}
        </select>
      </div>
      <div>
        <label htmlFor="region">Region</label>
        <select id="region" value={region} onChange={(e) => onRegionChange(e.target.value)}>
          <option value="">All regions</option>
          {regions.map((r) => (
            <option key={r} value={r}>
              {r}
            </option>
          ))}
        </select>
      </div>
    </div>
  )
}

export default FilterBar
