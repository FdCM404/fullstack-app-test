import { useState, useEffect } from "react"

const EQUIPMENT_TYPES = ["FIREWALL", "ROUTER", "SWITCH", "SERVER", "OTHER"]
const EQUIPMENT_STATES = ["OPERATIONAL", "UNDER_MAINTENANCE", "DAMAGED", "INACTIVE", "ARCHIVED"]

const EquipmentForm = ({ existingEquipment = {}, updateCallback, contacts = [] }) => {

    const [type, setType] = useState(existingEquipment.type || "")
    const [model, setModel] = useState(existingEquipment.model || "")
    const [serialNumber, setSerialNumber] = useState(existingEquipment.serialNumber || "")
    const [equipmentState, setEquipmentState] = useState(existingEquipment.equipmentState || "OPERATIONAL")
    const [assignedTo, setAssignedTo] = useState(existingEquipment.assignedTo?.id || "")

    const updating = Object.entries(existingEquipment).length !== 0

    useEffect(() => {
        setType(existingEquipment.type || "")
        setModel(existingEquipment.model || "")
        setSerialNumber(existingEquipment.serialNumber || "")
        setEquipmentState(existingEquipment.equipmentState || "OPERATIONAL")
        setAssignedTo(existingEquipment.assignedTo?.id || "")
    }, [existingEquipment])

    const onSubmit = async (e) => {
        e.preventDefault()

        if (!updating && serialNumber.length < 10) {
            alert("Serial Number must be at least 10 characters long.")
            return
        }

        const data = {
            type,
            model,
            serialNumber,
            equipmentState,
            assignedTo: assignedTo || null
        }

        const url = updating
            ? `http://127.0.0.1:5000/update_equipment/${existingEquipment.id}`
            : "http://127.0.0.1:5000/create_equipment"

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
                <label htmlFor="type">Type:</label>
                <select id="type" value={type} onChange={(e) => setType(e.target.value)}>
                    <option value="">-- Select --</option>
                    {EQUIPMENT_TYPES.map((t) => (
                        <option key={t} value={t}>{t}</option>
                    ))}
                </select>
            </div>

            <div>
                <label htmlFor="model">Model:</label>
                <input
                    type="text"
                    id="model"
                    value={model}
                    onChange={(e) => setModel(e.target.value)}
                />
            </div>

            <div>
                <label htmlFor="serialNumber">Serial Number:</label>
                <input
                    type="text"
                    id="serialNumber"
                    value={serialNumber}
                    onChange={(e) => setSerialNumber(e.target.value)}
                />
            </div>

            <div>
                <label htmlFor="assignedTo">Assigned To:</label>
                <select id="assignedTo" value={assignedTo} onChange={(e) => setAssignedTo(e.target.value)}>
                    <option value="">-- None --</option>
                    {contacts.map((c) => (
                        <option key={c.id} value={c.id}>{c.firstName} {c.lastName}</option>
                    ))}
                </select>
            </div>

            <div>
                <label htmlFor="equipmentState">State:</label>
                <select id="equipmentState" value={equipmentState} onChange={(e) => setEquipmentState(e.target.value)}>
                    {EQUIPMENT_STATES.map((s) => (
                        <option key={s} value={s}>{s}</option>
                    ))}
                </select>
            </div>

            <button type="submit">{updating ? "Update" : "Add"} Equipment</button>
        </form>
    )
}

export default EquipmentForm
