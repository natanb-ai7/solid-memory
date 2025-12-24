import { ReactNode } from 'react'
import { NavLink } from 'react-router-dom'

interface Props {
  children: ReactNode
}

const linkClass = ({ isActive }: { isActive: boolean }) =>
  `px-4 py-2 rounded-md font-semibold transition-colors ${isActive ? 'bg-blue-600 text-white' : 'text-slate-700 hover:bg-slate-100'}`

function RootLayout({ children }: Props) {
  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <div className="text-lg font-bold text-blue-700">Program Monitor</div>
          <nav className="flex gap-2 text-sm">
            <NavLink className={linkClass} to="/programs">
              Current Programs
            </NavLink>
            <NavLink className={linkClass} to="/history">
              History
            </NavLink>
            <NavLink className={linkClass} to="/sources">
              Source status
            </NavLink>
          </nav>
        </div>
      </header>
      <main className="mx-auto max-w-6xl px-6 py-6">{children}</main>
    </div>
  )
}

export default RootLayout
