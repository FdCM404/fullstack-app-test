import { useEffect, useState } from "react"
import MaintenanceList from "../MaintenanceList"
import MaintenanceForm from "../MaintenanceForm"

const MaintenancePage = () => {
    const [maintenances, setMaintenances] = useState([])
    const [equipment, setEquipment] = useState([])
    const [currentMaintenance, setCurrentMaintenance] = useState({})
    const user = JSON.parse(localStorage.getItem("user"))
    const canManage = user?.permissions?.includes("MANAGE_MAINTENANCE")

    useEffect(() => {
        fetch("/api/maintenances")
            .then((response) => response.json())
            .then((data) => setMaintenances(data.maintenances))
        fetch("/api/equipment")
            .then((response) => response.json())
            .then((data) => setEquipment(data.equipment))
    }, [])

    const fetchMaintenances = async () => {
        const response = await fetch("/api/maintenances")
        const data = await response.json()
        setMaintenances(data.maintenances)
    }

    const updateMaintenance = (m) => {
        setCurrentMaintenance(m)
    }

    const onUpdate = () => {
        setCurrentMaintenance({})
        fetchMaintenances()
    }

    const deleteMaintenance = async (id) => {
        const response = await fetch(`/api/delete_maintenance/${id}`, { method: "DELETE" })
        if (response.status === 200) {
            fetchMaintenances()
        } else {
            const data = await response.json()
            alert(data.message)
        }
    }

    return (
        <div className="page-container">
            <MaintenanceList
                maintenances={maintenances}
                updateMaintenance={updateMaintenance}
                deleteMaintenance={deleteMaintenance}
                isAdmin={user?.isAdmin}
                canManage={canManage}
            />
            {canManage && <div className="form-section">
                <h3>{Object.keys(currentMaintenance).length ? 'Update Maintenance' : 'Add Maintenance'}</h3>
                <MaintenanceForm
                    existingMaintenance={currentMaintenance}
                    updateCallback={onUpdate}
                    equipment={equipment}
                />
            </div>}
        </div>
    )
}

export default MaintenancePage
