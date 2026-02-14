import { useState, useEffect } from "react"

const ContactForm = ({ existingContact = {}, updateCallback }) => {

    const [firstName, setFirstName] = useState(existingContact.firstName || "")
    const [lastName, setLastName] = useState(existingContact.lastName || "")
    const [email, setEmail] = useState(existingContact.email || "")
    const [role, setRole] = useState(existingContact.role || "")
    const [password, setPassword] = useState("")

    const updating = Object.entries(existingContact).length !== 0

    useEffect(() => {
        setFirstName(existingContact.firstName || "")
        setLastName(existingContact.lastName || "")
        setEmail(existingContact.email || "")
        setRole(existingContact.role || "")
        setPassword("")
    }, [existingContact])

    const onSubmit = async (e) => {
        e.preventDefault()

        const data = {
            firstName,
            lastName,
            email,
            role,
            password: password || undefined 
        }

        const url = updating
            ? `http://127.0.0.1:5000/update_contact/${existingContact.id}`
            : "http://127.0.0.1:5000/create_contact"

        const options = {
            method: updating ? "PATCH" : "POST",
            headers: {
                "Content-Type": "application/json"
            },
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
                <label htmlFor="firstName">First Name:</label>
                <input
                    type="text"
                    id="firstName"
                    value={firstName}
                    onChange={(e) => setFirstName(e.target.value)}
                />
            </div>

            <div>
                <label htmlFor="lastName">Last Name:</label>
                <input
                    type="text"
                    id="lastName"
                    value={lastName}
                    onChange={(e) => setLastName(e.target.value)}
                />
            </div>

            <div>
                <label htmlFor="Email">Email:</label>
                <input
                    type="text"
                    id="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                />
            </div>

            <div>
                <label htmlFor="Role">Role:</label>
                <input
                    type="text"
                    id="role"
                    value={role}
                    onChange={(e) => setRole(e.target.value)}
                />
            </div>

            <div>
                <label htmlFor="Password">Password:</label>
                <input
                    type="password"
                    id="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder={updating ? "Leave blank to keep current password" : ""}
                />
            </div>

            <button type="submit">{updating ? "Update" : "Create"} Contact</button>
        </form>
    );
};

export default ContactForm