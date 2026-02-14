import { useNavigate, useLocation, Outlet } from "react-router-dom"

const navItems = [
    { path: "/dashboard",              label: "Home",         icon: "⌂", adminOnly: false },
    { path: "/dashboard/contacts",     label: "Contacts",     icon: "⊕", adminOnly: true },
    { path: "/dashboard/maintenances", label: "Maintenances", icon: "⚙", adminOnly: false },
    { path: "/dashboard/equipment",    label: "Devices",      icon: "◈", adminOnly: false },
    { path: null,                      label: "Settings",     icon: "⊘", adminOnly: false, disabled: true },
]

const Dashboard = () => {
    const navigate = useNavigate()
    const location = useLocation()
    const user = JSON.parse(localStorage.getItem("user"))

    const logout = () => {
        localStorage.removeItem("user")
        navigate("/")
    }

    if (!user) {
        navigate("/")
        return null
    }

    const isHome = location.pathname === "/dashboard"

    return (
        <div className="dashboard-layout">
            {/* ── Sidebar ── */}
            <aside className="sidebar">
                <div className="sidebar-brand">
                    <span className="sidebar-logo">⬡</span>
                    <span className="sidebar-title">NetOps</span>
                </div>

                <nav className="sidebar-nav">
                    {navItems
                        .filter(item => !item.adminOnly || user.isAdmin === 1)
                        .map(item => (
                            <button
                                key={item.label}
                                className={
                                    "sidebar-link"
                                    + (item.disabled ? " disabled" : "")
                                    + (location.pathname === item.path ? " active" : "")
                                }
                                onClick={() => !item.disabled && navigate(item.path)}
                            >
                                <span className="sidebar-icon">{item.icon}</span>
                                <span>{item.label}</span>
                            </button>
                        ))
                    }
                </nav>

                <div className="sidebar-footer">
                    <p className="sidebar-user">{user.firstName} · {user.isAdmin ? "Admin" : "User"}</p>
                    <button className="sidebar-logout" onClick={logout}>Logout</button>
                </div>
            </aside>

            {/* ── Main content ── */}
            <main className="dashboard-main">
                {isHome ? (
                    <div className="dashboard-welcome">
                        <h1>Dashboard</h1>
                        <p>Select an option from the sidebar to get started.</p>
                    </div>
                ) : (
                    <Outlet />
                )}
            </main>
        </div>
    )
}

export default Dashboard
