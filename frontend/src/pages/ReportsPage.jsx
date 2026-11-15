import { useEffect, useState } from "react"

const ReportsPage = () => {
    const [equipment, setEquipment] = useState([])
    const [filters, setFilters] = useState({
        reportType: "maintenance",
        format: "csv",
        equipmentId: "",
        equipmentType: "",
        state: "",
        maintenanceType: "",
        startDate: "",
        endDate: "",
    })
    const [message, setMessage] = useState("")
    const [error, setError] = useState("")

    useEffect(() => {
        fetch("/api/equipment?includeArchived=true")
            .then((response) => response.json())
            .then((data) => setEquipment(data.equipment))
    }, [])

    const updateFilter = (event) => {
        const { name, value } = event.target
        setFilters((current) => ({ ...current, [name]: value }))
    }

    const generateReport = async (event) => {
        event.preventDefault()
        setMessage("")
        setError("")
        const params = new URLSearchParams(Object.entries(filters).filter(([, value]) => value))
        try {
            const response = await fetch(`/api/reports?${params}`)
            if (!response.ok) {
                const data = await response.json()
                setError(data.message || "The report could not be generated. Please try again.")
                return
            }
            const blob = await response.blob()
            const url = URL.createObjectURL(blob)
            const link = document.createElement("a")
            link.href = url
            link.download = `${filters.reportType}-report.${filters.format}`
            link.click()
            URL.revokeObjectURL(url)
            setMessage("Report generated successfully.")
        } catch {
            setError("The report could not be generated. Please try again.")
        }
    }

    return (
        <div className="page-container">
            <section className="equipment-search">
                <p className="eyebrow">Reporting / export</p>
                <h1>Reports</h1>
                <form className="search-form" onSubmit={generateReport}>
                    <div>
                        <label htmlFor="reportType">Report Type</label>
                        <select id="reportType" name="reportType" value={filters.reportType} onChange={updateFilter}>
                            <option value="maintenance">Maintenance</option>
                            <option value="equipment">Equipment</option>
                        </select>
                    </div>
                    <div>
                        <label htmlFor="format">Export Format</label>
                        <select id="format" name="format" value={filters.format} onChange={updateFilter}>
                            <option value="csv">CSV</option>
                            <option value="pdf">PDF</option>
                        </select>
                    </div>
                    <div>
                        <label htmlFor="equipmentId">Equipment</label>
                        <select id="equipmentId" name="equipmentId" value={filters.equipmentId} onChange={updateFilter}>
                            <option value="">All</option>
                            {equipment.map((item) => <option key={item.id} value={item.id}>{item.type} - {item.model}</option>)}
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
                        <label htmlFor="equipmentType">Equipment Type</label>
                        <select id="equipmentType" name="equipmentType" value={filters.equipmentType} onChange={updateFilter}>
                            <option value="">All</option>
                            {["FIREWALL", "ROUTER", "SWITCH", "SERVER", "OTHER"].map((type) => <option key={type} value={type}>{type}</option>)}
                        </select>
                    </div>
                    <div>
                        <label htmlFor="maintenanceType">Intervention Type</label>
                        <select id="maintenanceType" name="maintenanceType" value={filters.maintenanceType} onChange={updateFilter}>
                            <option value="">All</option>
                            {["PREVENTIVE", "CORRECTIVE", "SOFTWARE_UPDATE", "REPLACEMENT", "INSPECTION"].map((type) => <option key={type} value={type}>{type}</option>)}
                        </select>
                    </div>
                    <div>
                        <label htmlFor="startDate">From</label>
                        <input id="startDate" name="startDate" type="date" value={filters.startDate} onChange={updateFilter} />
                    </div>
                    <div>
                        <label htmlFor="endDate">To</label>
                        <input id="endDate" name="endDate" type="date" value={filters.endDate} onChange={updateFilter} />
                    </div>
                    <button type="submit">Generate Report</button>
                </form>
                {message && <p className="import-success">{message}</p>}
                {error && <p className="import-error">{error}</p>}
            </section>
        </div>
    )
}

export default ReportsPage
