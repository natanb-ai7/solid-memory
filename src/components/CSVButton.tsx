import { Program } from '../api/types'

interface CSVButtonProps {
  data: Program[]
}

function CSVButton({ data }: CSVButtonProps) {
  const handleDownload = () => {
    const header = ['Program', 'Make', 'Region', 'Status', 'Start', 'Owner']
    const rows = data.map((item) => [
      item.name,
      item.make,
      item.region,
      item.status,
      new Date(item.startDate).toISOString(),
      item.owner,
    ])

    const csv = [header, ...rows]
      .map((row) => row.map((value) => `"${value}"`).join(','))
      .join('\n')

    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', 'programs.csv')
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
  }

  return (
    <button className="button-secondary" onClick={handleDownload} disabled={!data.length}>
      Export CSV
    </button>
  )
}

export default CSVButton
