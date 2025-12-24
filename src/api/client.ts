import { programs, sources, timeline } from './mockData'
import { Program, SourceRecord, TimelineEvent } from './types'

const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms))

export async function fetchPrograms(): Promise<Program[]> {
  await delay(200)
  return programs
}

export async function fetchTimeline(): Promise<TimelineEvent[]> {
  await delay(180)
  return timeline
}

export async function fetchSourceStatus(): Promise<SourceRecord[]> {
  await delay(120)
  return sources
}
