import { Program, SourceRecord, TimelineEvent } from './types'

export const programs: Program[] = [
  {
    id: 'p-1',
    name: 'Fleet Renewal',
    make: 'Acme',
    region: 'North America',
    status: 'Active',
    startDate: '2024-01-05',
    owner: 'Ops',
    lastUpdated: '2024-06-12T10:30:00Z',
  },
  {
    id: 'p-2',
    name: 'Safety Revamp',
    make: 'Contoso',
    region: 'Europe',
    status: 'Planning',
    startDate: '2024-03-22',
    owner: 'Quality',
    lastUpdated: '2024-06-11T15:04:00Z',
  },
  {
    id: 'p-3',
    name: 'Factory Digitization',
    make: 'Acme',
    region: 'Asia Pacific',
    status: 'Active',
    startDate: '2023-11-15',
    owner: 'Engineering',
    lastUpdated: '2024-06-09T21:45:00Z',
  },
  {
    id: 'p-4',
    name: 'Logistics Backbone',
    make: 'Globex',
    region: 'Latin America',
    status: 'Paused',
    startDate: '2023-07-10',
    owner: 'Supply Chain',
    lastUpdated: '2024-06-06T12:12:00Z',
  },
  {
    id: 'p-5',
    name: 'AI Co-pilot',
    make: 'Contoso',
    region: 'North America',
    status: 'Active',
    startDate: '2024-04-01',
    owner: 'R&D',
    lastUpdated: '2024-06-12T09:12:00Z',
  },
]

export const timeline: TimelineEvent[] = [
  {
    id: 'h-1',
    programId: 'p-1',
    programName: 'Fleet Renewal',
    action: 'Milestone achieved: 25% rollout',
    happenedAt: '2024-05-28T14:45:00Z',
  },
  {
    id: 'h-2',
    programId: 'p-3',
    programName: 'Factory Digitization',
    action: 'Integration test signed off',
    happenedAt: '2024-05-14T09:02:00Z',
  },
  {
    id: 'h-3',
    programId: 'p-2',
    programName: 'Safety Revamp',
    action: 'Scope locked with steering committee',
    happenedAt: '2024-06-01T11:30:00Z',
  },
  {
    id: 'h-4',
    programId: 'p-5',
    programName: 'AI Co-pilot',
    action: 'Pilot cohort selected',
    happenedAt: '2024-06-08T17:20:00Z',
  },
]

export const sources: SourceRecord[] = [
  {
    make: 'Acme',
    region: 'North America',
    lastUpdated: '2024-06-12T10:30:00Z',
    freshnessMinutes: 25,
  },
  {
    make: 'Contoso',
    region: 'Europe',
    lastUpdated: '2024-06-11T15:04:00Z',
    freshnessMinutes: 150,
  },
  {
    make: 'Globex',
    region: 'Latin America',
    lastUpdated: '2024-06-06T12:12:00Z',
    freshnessMinutes: 720,
  },
  {
    make: 'Acme',
    region: 'Asia Pacific',
    lastUpdated: '2024-06-09T21:45:00Z',
    freshnessMinutes: 300,
  },
]
