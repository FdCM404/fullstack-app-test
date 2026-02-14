import { useEffect, useState } from "react"
import MaintenanceList from "../MaintenanceList"
import MaintenanceForm from "../MaintenanceForm"

const MaintenancePage = () => {
    const [maintenances, setMaintenances] = useState([])
    const [equipment, setEquipment] = useState([])
    const [currentMaintenance, setCurrentMaintenance] = useState({})
    const user = JSON.parse(localStorage.getItem("user"))

    useEffect(() => {
        fetchMaintenances()
        fetchEquipment()
    }, [])

    const fetchMaintenances = async () => {
        const response = await fetch("http://127.0.0.1:5000/maintenances")
        const data = await response.json()
        setMaintenances(data.maintenances)
    }

    const fetchEquipment = async () => {
        const response = await fetch("http://127.0.0.1:5000/equipment")
        const data = await response.json()
        setEquipment(data.equipment)
    }

    const updateMaintenance = (m) => {
        setCurrentMaintenance(m)
    }

    const onUpdate = () => {
        setCurrentMaintenance({})
        fetchMaintenances()
    }

    const deleteMaintenance = async (id) => {
        const response = await fetch(`http://127.0.0.1:5000/delete_maintenance/${id}`, { method: "DELETE" })
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
            />
            <div className="form-section">
                <h3>{Object.keys(currentMaintenance).length ? 'Update Maintenance' : 'Add Maintenance'}</h3>
                <MaintenanceForm
                    existingMaintenance={currentMaintenance}
                    updateCallback={onUpdate}
                    equipment={equipment}
                />
            </div>
        </div>
    )
}

export default MaintenancePage
