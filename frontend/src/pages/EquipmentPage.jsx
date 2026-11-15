import { useEffect, useState } from "react"
import EquipmentList from "../EquipmentList"
import EquipmentForm from "../EquipmentForm"
import EquipmentBulkImport from "../EquipmentBulkImport"

const EquipmentPage = () => {
    const [equipment, setEquipment] = useState([])
    const [contacts, setContacts] = useState([])
    const [currentEquipment, setCurrentEquipment] = useState({})
    const [selectedEquipment, setSelectedEquipment] = useState(null)
    const [filters, setFilters] = useState({ search: "", type: "", state: "", location: "", responsible: "" })
    const [deleteMessage, setDeleteMessage] = useState("")
    const user = JSON.parse(localStorage.getItem("user"))
    const canManage = user?.permissions?.includes("MANAGE_EQUIPMENT")

    useEffect(() => {
        fetch("/api/equipment")
            .then((response) => response.json())
            .then((data) => setEquipment(data.equipment))
        fetch("/api/contacts")
            .then((response) => response.json())
            .then((data) => setContacts(data.contacts))
    }, [])

    const fetchEquipment = async () => {
        const params = new URLSearchParams(
            Object.entries(filters).filter(([, value]) => value)
        )
        const response = await fetch(`/api/equipment?${params}`)
        const data = await response.json()
        setEquipment(data.equipment)
    }

    const updateEquipment = (eq) => {
        setCurrentEquipment(eq)
    }

    const editSelectedEquipment = () => {
        setCurrentEquipment(selectedEquipment)
    }

    const onUpdate = () => {
        setCurrentEquipment({})
        fetchEquipment()
    }

    const deleteEquipment = async (id) => {
        const response = await fetch(`/api/delete_equipment/${id}`, { method: "DELETE" })
        if (response.status === 200) {
            setDeleteMessage("Equipment deleted successfully.")
            fetchEquipment()
        } else if (response.status === 409) {
            const data = await response.json()
            if (data.requiresArchive) {
                const confirmed = window.confirm(`${data.message}\n\nConfirm logical archiving?`)
                if (!confirmed) return

                const archiveResponse = await fetch(`/api/update_equipment/${id}`, {
                    method: "PATCH",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        equipmentState: "ARCHIVED",
                        changedBy: JSON.parse(localStorage.getItem("user"))?.id || null,
                    }),
                })
                if (archiveResponse.ok) {
                    setDeleteMessage("Equipment archived successfully.")
                    fetchEquipment()
                } else {
                    const archiveData = await archiveResponse.json()
                    alert(archiveData.message)
                }
                return
            }

            if (data.requiresConfirmation) {
                const confirmed = window.confirm("Are you sure you want to permanently delete this equipment?")
                if (!confirmed) return

                const deleteResponse = await fetch(`/api/delete_equipment/${id}?confirmed=true`, { method: "DELETE" })
                if (deleteResponse.ok) {
                    setDeleteMessage("Equipment deleted successfully.")
                    fetchEquipment()
                } else {
                    const deleteData = await deleteResponse.json()
                    alert(deleteData.message)
                }
            }
        } else {
            const data = await response.json()
            alert(data.message)
        }
    }

    const updateFilter = (event) => {
        const { name, value } = event.target
        setFilters((current) => ({ ...current, [name]: value }))
    }

    const searchEquipment = (event) => {
        event.preventDefault()
        fetchEquipment()
    }

    const clearFilters = () => {
        const emptyFilters = { search: "", type: "", state: "", location: "", responsible: "" }
        setFilters(emptyFilters)
        fetch("/api/equipment").then((response) => response.json()).then((data) => setEquipment(data.equipment))
    }

    const showDetails = async (equipmentId) => {
        const response = await fetch(`/api/equipment/${equipmentId}`)
        const data = await response.json()
        if (response.ok) {
            setSelectedEquipment(data.equipment)
        } else {
            alert(data.message)
        }
    }

    const getLocationLabel = (location) => {
        if (!location) return "—"
        return `Floor ${location.floor}, Room ${location.roomNumber}${location.description ? ` · ${location.description}` : ""}`
    }

    return (
        <div className="page-container">
            <section className="equipment-search">
                <div className="equipment-heading">
                    <div>
                        <p className="eyebrow">Inventory / query</p>
                        <h1>Devices</h1>
                    </div>
                    <span className="result-count">{equipment.length} result{equipment.length === 1 ? "" : "s"}</span>
                </div>
                <form className="search-form" onSubmit={searchEquipment}>
                    <div className="search-wide">
                        <label htmlFor="search">Search</label>
                        <input id="search" name="search" value={filters.search} onChange={updateFilter} placeholder="Model, serial number or type" />
                    </div>
                    <div>
                        <label htmlFor="type">Type</label>
                        <select id="type" name="type" value={filters.type} onChange={updateFilter}>
                            <option value="">All</option>
                            {["FIREWALL", "ROUTER", "SWITCH", "SERVER", "OTHER"].map((type) => <option key={type} value={type}>{type}</option>)}
                        </select>
                    </div>
                    <div>
                        <label htmlFor="state">State</label>
                        <select id="state" name="state" value={filters.state} onChange={updateFilter}>
                            <option value="">All</option>
                            {["OPERATIONAL", "UNDER_MAINTENANCE", "DAMAGED", "INACTIVE", "ARCHIVED"].map((state) => <option key={state} value={state}>{state}</option>)}
                        </select>
                    </div>
                    <div>
                        <label htmlFor="location">Location</label>
                        <input id="location" name="location" value={filters.location} onChange={updateFilter} placeholder="Floor, room or description" />
                    </div>
                    <div>
                        <label htmlFor="responsible">Responsible</label>
                        <select id="responsible" name="responsible" value={filters.responsible} onChange={updateFilter}>
                            <option value="">All</option>
                            {contacts.map((contact) => <option key={contact.id} value={contact.id}>{contact.firstName} {contact.lastName}</option>)}
                        </select>
                    </div>
                    <div className="search-actions">
                        <button type="submit">Search</button>
                        <button type="button" onClick={clearFilters}>Clear</button>
                    </div>
                </form>
            </section>
            <EquipmentList equipment={equipment} updateEquipment={updateEquipment} deleteEquipment={deleteEquipment} showDetails={showDetails} getLocationLabel={getLocationLabel} canManage={canManage} />
            {deleteMessage && <p className="import-success">{deleteMessage}</p>}
            {selectedEquipment && (
                <section className="equipment-details">
                    <div className="details-header">
                        <div>
                            <p className="eyebrow">Technical sheet</p>
                            <h2>{selectedEquipment.type} · {selectedEquipment.model}</h2>
                        </div>
                        <div>
                            <button type="button" onClick={editSelectedEquipment}>Edit</button>
                            <button type="button" onClick={() => setSelectedEquipment(null)}>Close</button>
                        </div>
                    </div>
                    <div className="details-grid">
                        <div><span>Serial Number</span><strong>{selectedEquipment.serialNumber}</strong></div>
                        <div><span>State</span><strong>{selectedEquipment.equipmentState}</strong></div>
                        <div><span>Responsible</span><strong>{selectedEquipment.assignedTo ? `${selectedEquipment.assignedTo.firstName} ${selectedEquipment.assignedTo.lastName}` : "Unassigned"}</strong></div>
                        <div><span>Location</span><strong>{getLocationLabel(selectedEquipment.locationDetails)}</strong></div>
                    </div>
                    <h3>Network Parameters</h3>
                    <div className="details-grid network-grid">
                        {Object.entries({ "IP address": "ipAddress", "MAC address": "macAddress", Hostname: "hostname", VLAN: "vlan" }).map(([label, key]) => (
                            <div key={key}><span>{label}</span><strong>{selectedEquipment.networkParameters?.[key] || "Not registered"}</strong></div>
                        ))}
                    </div>
                    <h3>Maintenance History</h3>
                    {selectedEquipment.maintenanceHistory?.length ? (
                        <ul className="maintenance-history">
                            {selectedEquipment.maintenanceHistory.map((record) => <li key={record.id}><strong>{record.date}</strong><span>{record.maintenanceType} · {record.description}</span></li>)}
                        </ul>
                    ) : <p className="muted-copy">No maintenance records found.</p>}
                    <h3>Change History</h3>
                    {selectedEquipment.changeHistory?.length ? (
                        <ul className="maintenance-history">
                            {selectedEquipment.changeHistory.map((change) => (
                                <li key={change.id}>
                                    <strong>{new Date(change.changedAt).toLocaleString()}</strong>
                                    <span>
                                        <b>{change.field}</b>: {change.previousValue || "Empty"} → {change.newValue || "Empty"}
                                        {" · "}{change.changedBy ? `${change.changedBy.firstName} ${change.changedBy.lastName}` : "Unknown user"}
                                    </span>
                                </li>
                            ))}
                        </ul>
                    ) : <p className="muted-copy">No changes recorded.</p>}
                </section>
            )}
            {canManage && <div className="form-section">
                <h3>{Object.keys(currentEquipment).length ? 'Update Equipment' : 'Add Equipment'}</h3>
                <EquipmentForm key={currentEquipment.id || "new"} existingEquipment={currentEquipment} updateCallback={onUpdate} contacts={contacts} />
            </div>}
            {canManage && <EquipmentBulkImport onImported={fetchEquipment} />}
        </div>
    )
}

export default EquipmentPage
