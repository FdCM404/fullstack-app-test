import { useEffect, useState } from "react"
import { useNavigate } from "react-router-dom"
import EquipmentList from "../EquipmentList"
import EquipmentForm from "../EquipmentForm"

const EquipmentPage = () => {
    const [equipment, setEquipment] = useState([])
    const [contacts, setContacts] = useState([])
    const [currentEquipment, setCurrentEquipment] = useState({})
    const navigate = useNavigate()

    useEffect(() => {
        fetchEquipment()
        fetchContacts()
    }, [])

    const fetchEquipment = async () => {
        const response = await fetch("http://127.0.0.1:5000/equipment")
        const data = await response.json()
        setEquipment(data.equipment)
    }

    const fetchContacts = async () => {
        const response = await fetch("http://127.0.0.1:5000/contacts")
        const data = await response.json()
        setContacts(data.contacts)
    }

    const updateEquipment = (eq) => {
        setCurrentEquipment(eq)
    }

    const onUpdate = () => {
        setCurrentEquipment({})
        fetchEquipment()
    }

    const deleteEquipment = async (id) => {
        const response = await fetch(`http://127.0.0.1:5000/delete_equipment/${id}`, { method: "DELETE" })
        if (response.status === 200) {
            fetchEquipment()
        } else {
            const data = await response.json()
            alert(data.message)
        }
    }

    return (
        <div className="page-container">
            <button onClick={() => navigate("/dashboard")}>← Back to Dashboard</button>
            <EquipmentList equipment={equipment} updateEquipment={updateEquipment} deleteEquipment={deleteEquipment} />
            <div className="form-section">
                <h3>{Object.keys(currentEquipment).length ? 'Update Equipment' : 'Add Equipment'}</h3>
                <EquipmentForm existingEquipment={currentEquipment} updateCallback={onUpdate} contacts={contacts} />
            </div>
        </div>
    )
}

export default EquipmentPage
