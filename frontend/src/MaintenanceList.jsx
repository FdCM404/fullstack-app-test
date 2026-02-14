import React from "react"

const MaintenanceList = ({ maintenances, updateMaintenance, deleteMaintenance, isAdmin }) => {
    return <div className="table-section">
        <h2>Maintenance Records</h2>
        <table>
            <thead>
                <tr>
                    <th>Equipment</th>
                    <th>Type</th>
                    <th>Date</th>
                    <th>Description</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                {maintenances.map((m) => (
                    <tr key={m.id}>
                        <td>{m.equipmentName || `Equipment #${m.equipmentId}`}</td>
                        <td>{m.maintenanceType}</td>
                        <td>{m.date}</td>
                        <td>{m.description}</td>
                        <td>
                            <button onClick={() => updateMaintenance(m)}>Update</button>
                            {isAdmin === 1 && (
                                <button onClick={() => deleteMaintenance(m.id)}>Delete</button>
                            )}
                        </td>
                    </tr>
                ))}
            </tbody>
        </table>
    </div>
}

export default MaintenanceList
