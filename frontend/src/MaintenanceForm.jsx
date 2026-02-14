import { useState, useEffect } from "react"

const MAINTENANCE_TYPES = ["PREVENTIVE", "CORRECTIVE", "SOFTWARE_UPDATE", "REPLACEMENT", "INSPECTION"]

const MaintenanceForm = ({ existingMaintenance = {}, updateCallback, equipment = [] }) => {

    const [equipmentId, setEquipmentId] = useState(existingMaintenance.equipmentId || "")
    const [maintenanceType, setMaintenanceType] = useState(existingMaintenance.maintenanceType || "")
    const [date, setDate] = useState(existingMaintenance.date || "")
    const [description, setDescription] = useState(existingMaintenance.description || "")

    const updating = Object.entries(existingMaintenance).length !== 0

    useEffect(() => {
        setEquipmentId(existingMaintenance.equipmentId || "")
        setMaintenanceType(existingMaintenance.maintenanceType || "")
        setDate(existingMaintenance.date || "")
        setDescription(existingMaintenance.description || "")
    }, [existingMaintenance])

    const onSubmit = async (e) => {
        e.preventDefault()

        const data = {
            equipmentId: parseInt(equipmentId),
            maintenanceType,
            date,
            description
        }

        const url = updating
            ? `http://127.0.0.1:5000/update_maintenance/${existingMaintenance.id}`
            : "http://127.0.0.1:5000/create_maintenance"

        const options = {
            method: updating ? "PATCH" : "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data)
        }

        const response = await fetch(url, options)
        if (response.status !== 201 && response.status !== 200) {
            const data = await response.json()
            alert(data.message)
        } else {
            if (updateCallback) updateCallback()
        }
    }

    return (
        <form onSubmit={onSubmit}>
            <div>
                <label htmlFor="equipmentId">Equipment:</label>
                <select id="equipmentId" value={equipmentId} onChange={(e) => setEquipmentId(e.target.value)}>
                    <option value="">-- Select --</option>
                    {equipment.map((eq) => (
                        <option key={eq.id} value={eq.id}>{eq.type} - {eq.model} ({eq.serialNumber})</option>
                    ))}
                </select>
            </div>

            <div>
                <label htmlFor="maintenanceType">Type:</label>
                <select id="maintenanceType" value={maintenanceType} onChange={(e) => setMaintenanceType(e.target.value)}>
                    <option value="">-- Select --</option>
                    {MAINTENANCE_TYPES.map((t) => (
                        <option key={t} value={t}>{t}</option>
                    ))}
                </select>
            </div>

            <div>
                <label htmlFor="date">Date:</label>
                <input
                    type="date"
                    id="date"
                    value={date}
                    onChange={(e) => setDate(e.target.value)}
                />
            </div>

            <div>
                <label htmlFor="description">Description:</label>
                <input
                    type="text"
                    id="description"
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                />
            </div>

            <button type="submit">{updating ? "Update" : "Add"} Maintenance</button>
        </form>
    )
}

export default MaintenanceForm
