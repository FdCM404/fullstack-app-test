import { useState } from "react"
import { useNavigate, Link } from "react-router-dom"

const RegisterPage = () => {
    const [firstName, setFirstName] = useState("")
    const [lastName, setLastName] = useState("")
    const [email, setEmail] = useState("")
    const [password, setPassword] = useState("")
    const [role, setRole] = useState("")
    const navigate = useNavigate()

    const onSubmit = async (e) => {
        e.preventDefault()

        const response = await fetch("http://127.0.0.1:5000/register", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ firstName, lastName, email, password, role })
        })

        const data = await response.json()

        if (response.status === 201) {
            alert("Account created! Please login.")
            navigate("/")
        } else {
            alert(data.message)
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
                    <input
                        type="text"
                        id="role"
                        value={role}
                        placeholder="e.g. Network Engineer, IT Admin"
                        onChange={(e) => setRole(e.target.value)}
                    />
                </div>
                <button type="submit">Register</button>
            </form>
            <p>Already have an account? <Link to="/">Login</Link></p>
        </div>
    )
}

export default RegisterPage
