export interface Program {
  id: string
  name: string
  make: string
  region: string
  status: 'Active' | 'Planning' | 'Paused'
  startDate: string
  owner: string
  lastUpdated: string
}

export interface TimelineEvent {
  id: string
  programId: string
  programName: string
  action: string
  happenedAt: string
}

export interface SourceRecord {
  make: string
  region: string
  lastUpdated: string
  freshnessMinutes: number
}
