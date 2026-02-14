import { Routes, Route, Navigate } from 'react-router-dom'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import Dashboard from './pages/Dashboard'
import ContactsPage from './pages/ContactsPage'
import EquipmentPage from './pages/EquipmentPage'
import MaintenancePage from './pages/MaintenancePage'
import './App.css'

function App() {
  return (
    <Routes>
      <Route path="/" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />

      {/* Dashboard layout with sidebar — child routes render in <Outlet /> */}
      <Route path="/dashboard" element={<Dashboard />}>
        <Route path="contacts" element={<ContactsPage />} />
        <Route path="equipment" element={<EquipmentPage />} />
        <Route path="maintenances" element={<MaintenancePage />} />
      </Route>

      <Route path="*" element={<Navigate to="/" />} />
    </Routes>
  );
}

export default App
