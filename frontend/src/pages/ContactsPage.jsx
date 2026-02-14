import { useEffect, useState } from "react"
import ContactList from "../ContactList"
import ContactForm from "../ContactForm"

const ContactsPage = () => {
    const [contacts, setContacts] = useState([])
    const [currentContact, setCurrentContact] = useState({})

    useEffect(() => {
        fetchContacts()
    }, [])

    const fetchContacts = async () => {
        const response = await fetch("http://127.0.0.1:5000/contacts")
        const data = await response.json()
        setContacts(data.contacts)
    }

    const updateContact = (contact) => {
        setCurrentContact(contact)
    }

    const onUpdate = () => {
        setCurrentContact({})
        fetchContacts()
    }

    const deleteContact = async (id) => {
        const response = await fetch(`http://127.0.0.1:5000/delete_contact/${id}`, { method: "DELETE" })
        if (response.status === 200) {
            fetchContacts()
        } else {
            const data = await response.json()
            alert(data.message)
        }
    }

    return (
        <div className="page-container">
            <ContactList contacts={contacts} updateContact={updateContact} deleteContact={deleteContact} />
            <div className="form-section">
                <h3>{Object.keys(currentContact).length ? 'Update Contact' : 'Add Contact'}</h3>
                <ContactForm existingContact={currentContact} updateCallback={onUpdate} />
            </div>
        </div>
    )
}

export default ContactsPage
