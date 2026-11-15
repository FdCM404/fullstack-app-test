import { useState } from "react"
import { useNavigate, Link } from "react-router-dom"

const LoginPage = () => {
    const [email, setEmail] = useState("")
    const [password, setPassword] = useState("")
    const navigate = useNavigate()

    const onSubmit = async (e) => {
        e.preventDefault()

        try {
            const response = await fetch("/api/login", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email, password })
            })
            const data = await response.json()

            if (!response.ok) {
                alert(data.message || "Login failed.")
                return
            }

            localStorage.setItem("user", JSON.stringify(data.user))
            navigate("/dashboard")
        } catch {
            alert("Could not connect to the backend. Make sure Flask is running on port 5000.")
        }
    }

    return (
        <div className="login-container">
            <h2>Login</h2>
            <form onSubmit={onSubmit}>
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
                <button type="submit">Login</button>
            </form>
            <p>Don't have an account? <Link to="/register">Register</Link></p>
        </div>
    )
}

export default LoginPage
