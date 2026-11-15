import { useState } from "react"

const EquipmentBulkImport = ({ onImported }) => {
    const [file, setFile] = useState(null)
    const [message, setMessage] = useState("")
    const [error, setError] = useState("")
    const [importing, setImporting] = useState(false)

    const importEquipment = async (event) => {
        event.preventDefault()
        if (!file) {
            setError("Select a CSV file first.")
            return
        }

        setImporting(true)
        setMessage("")
        setError("")
        const formData = new FormData()
        formData.append("file", file)

        try {
            const response = await fetch("/api/bulk_import_equipment", {
                method: "POST",
                body: formData,
            })
            const data = await response.json()
            if (!response.ok) {
                setError(data.message)
                return
            }
            setMessage(data.message)
            setFile(null)
            event.target.reset()
            onImported()
        } catch {
            setError("The import could not be completed.")
        } finally {
            setImporting(false)
        }
    }

    return (
        <section className="form-section bulk-import-section">
            <h3>Bulk Import Devices</h3>
            <p className="muted-copy">CSV columns: type, model, serialNumber, equipmentState, assignedTo, floor, roomNumber, locationDescription, ipAddress, macAddress, hostname, vlan</p>
            <form onSubmit={importEquipment}>
                <input
                    type="file"
                    accept=".csv,text/csv"
                    onChange={(event) => setFile(event.target.files[0] || null)}
                />
                <button type="submit" disabled={importing}>
                    {importing ? "Importing..." : "Import CSV"}
                </button>
            </form>
            {message && <p className="import-success">{message}</p>}
            {error && <p className="import-error">{error}</p>}
        </section>
    )
}

export default EquipmentBulkImport
