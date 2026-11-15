import { useState } from "react"

const ContactForm = ({ existingContact = {}, updateCallback }) => {
    const ROLE_PERMISSIONS = {
        Administrator: ["VIEW_EQUIPMENT", "MANAGE_EQUIPMENT", "VIEW_MAINTENANCE", "MANAGE_MAINTENANCE", "VIEW_REPORTS", "MANAGE_USERS"],
        "Network Engineer": ["VIEW_EQUIPMENT", "MANAGE_EQUIPMENT", "VIEW_MAINTENANCE", "MANAGE_MAINTENANCE", "VIEW_REPORTS"],
        "IT Technician": ["VIEW_EQUIPMENT", "VIEW_REPORTS"],
    }
    const PERMISSIONS = [
        ["VIEW_EQUIPMENT", "View equipment"],
        ["MANAGE_EQUIPMENT", "Manage equipment"],
        ["VIEW_MAINTENANCE", "View maintenance"],
        ["MANAGE_MAINTENANCE", "Manage maintenance"],
        ["VIEW_REPORTS", "View reports"],
        ["MANAGE_USERS", "Manage users"],
    ]

    const [firstName, setFirstName] = useState(existingContact.firstName || "")
    const [lastName, setLastName] = useState(existingContact.lastName || "")
    const [email, setEmail] = useState(existingContact.email || "")
    const [role, setRole] = useState(existingContact.role || "IT Technician")
    const [password, setPassword] = useState("")
    const [permissions, setPermissions] = useState(existingContact.permissions || ROLE_PERMISSIONS[existingContact.role] || [])

    const updating = Object.entries(existingContact).length !== 0

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
            ? `/api/update_contact/${existingContact.id}`
            : "/api/create_contact"

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
                <select id="role" value={role} onChange={(e) => {
                    setRole(e.target.value)
                    setPermissions(ROLE_PERMISSIONS[e.target.value])
                }}>
                    {Object.keys(ROLE_PERMISSIONS).map((availableRole) => <option key={availableRole} value={availableRole}>{availableRole}</option>)}
                </select>
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
            {updating && (
                <div>
                    <label>Permissions:</label>
                    {PERMISSIONS.map(([value, label]) => (
                        <label key={value}>
                            <input
                                type="checkbox"
                                checked={permissions.includes(value)}
                                readOnly
                                disabled
                            />
                            {label}
                        </label>
                    ))}
                </div>
            )}

            <button type="submit">{updating ? "Update" : "Create"} Contact</button>
        </form>
    );
};

export default ContactForm