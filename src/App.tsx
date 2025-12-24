import { Navigate, Route, Routes } from 'react-router-dom'
import RootLayout from './layout/RootLayout'
import CurrentPrograms from './pages/CurrentPrograms'
import History from './pages/History'
import SourceStatus from './pages/SourceStatus'

function App() {
  return (
    <RootLayout>
      <Routes>
        <Route path="/" element={<Navigate to="/programs" replace />} />
        <Route path="/programs" element={<CurrentPrograms />} />
        <Route path="/history" element={<History />} />
        <Route path="/sources" element={<SourceStatus />} />
      </Routes>
    </RootLayout>
  )
}

export default App
