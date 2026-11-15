import { useState } from "react"
import { useNavigate, Link } from "react-router-dom"

const RegisterPage = () => {
    const [firstName, setFirstName] = useState("")
    const [lastName, setLastName] = useState("")
    const [email, setEmail] = useState("")
    const [password, setPassword] = useState("")
    const [role, setRole] = useState("IT Technician")
    const navigate = useNavigate()

    const onSubmit = async (e) => {
        e.preventDefault()

        try {
            const response = await fetch("/api/register", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ firstName, lastName, email, password, role })
            })
            const data = await response.json()

            if (!response.ok) {
                alert(data.message || "Registration failed.")
                return
            }

            alert("Account created! Please login.")
            navigate("/")
        } catch {
            alert("Could not connect to the backend. Make sure Flask is running on port 5000.")
        }
    }

    return (
        <div className="login-container">
            <h2>Register</h2>
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
                    <label htmlFor="email">Email:</label>
                    <input
                        type="text"
                        id="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                    />
                </div>
                <div>
                    <label htmlFor="password">Password:</label>
                    <input
                        type="password"
                        id="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                    />
                </div>
                <div>
                    <label htmlFor="role">Role:</label>
                    <select id="role" value={role} onChange={(e) => setRole(e.target.value)}>
                        <option value="Administrator">Administrator</option>
                        <option value="Network Engineer">Network Engineer</option>
                        <option value="IT Technician">IT Technician</option>
                    </select>
                </div>
                <button type="submit">Register</button>
            </form>
            <p>Already have an account? <Link to="/">Login</Link></p>
        </div>
    )
}

export default RegisterPage
