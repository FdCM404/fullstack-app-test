import React from "react"

const EquipmentList = ({ equipment, updateEquipment, deleteEquipment }) => {

    const getStateBadge = (state) => {
        const badgeMap = {
            OPERATIONAL: 'badge-operational',
            UNDER_MAINTENANCE: 'badge-maintenance',
            DAMAGED: 'badge-damaged',
            INACTIVE: 'badge-inactive',
            ARCHIVED: 'badge-archived'
        }
        return `badge ${badgeMap[state] || ''}`
    }

    return <div className="table-section">
        <h2>Equipment</h2>
        <table>
            <thead>
                <tr>
                    <th>Type</th>
                    <th>Model</th>
                    <th>Serial Number</th>
                    <th>Assigned To</th>
                    <th>State</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                {equipment.map((eq) => (
                    <tr key={eq.id}>
                        <td>{eq.type}</td>
                        <td>{eq.model}</td>
                        <td>{eq.serialNumber}</td>
                        <td>{eq.assignedTo ? `${eq.assignedTo.firstName} ${eq.assignedTo.lastName}` : "—"}</td>
                        <td><span className={getStateBadge(eq.equipmentState)}>{eq.equipmentState}</span></td>
                        <td>
                            <button onClick={() => updateEquipment(eq)}>Update</button>
                            <button onClick={() => deleteEquipment(eq.id)}>Delete</button>
                        </td>
                    </tr>
                ))}
            </tbody>
        </table>
    </div>
}

export default EquipmentList
