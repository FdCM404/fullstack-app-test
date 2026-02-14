import { useNavigate } from "react-router-dom"

const Dashboard = () => {
    const navigate = useNavigate()
    const user = JSON.parse(localStorage.getItem("user"))

    const logout = () => {
        localStorage.removeItem("user")
        navigate("/")
    }

    if (!user) {
        navigate("/")
        return null
    }

    return (
        <div className="dashboard-container">
            <div className="dashboard-header">
                <h1>Dashboard</h1>
                <p>Welcome, {user.firstName} ({user.isAdmin ? "Admin" : "User"})</p>
                <button onClick={logout}>Logout</button>
            </div>
            <div className="dashboard-options">
                {user.isAdmin === 1 && (
                    <div className="dashboard-card" onClick={() => navigate("/contacts")}>
                        <h3>Contacts</h3>
                        <p>Manage users</p>
                    </div>
                )}
                <div className="dashboard-card" onClick={() => navigate("/maintenances")}>
                    <h3>Maintenances</h3>
                    <p>Manage maintenance records</p>
                </div>
                <div className="dashboard-card" onClick={() => navigate("/equipment")}>
                    <h3>Devices</h3>
                    <p>Manage equipment</p>
                </div>
                <div className="dashboard-card disabled">
                    <h3>Settings</h3>
                    <p>Coming soon</p>
                </div>
            </div>
        </div>
    )
}

export default Dashboard
