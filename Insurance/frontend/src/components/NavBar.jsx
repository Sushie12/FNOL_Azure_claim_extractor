import { Link, useNavigate } from "react-router-dom";

export default function Navbar() {
const navigate = useNavigate();

const logout = () => {
localStorage.removeItem("token");
navigate("/login");
};

return (
    <nav
    style={{
    background: "#111827",
    color: "white",
    padding: "1rem 2rem",
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    boxShadow: "0 2px 6px rgba(0,0,0,0.15)"
    }}>

    <h2 style={{ margin: 0 }}>Insurance Claim Analyzer</h2>
    <div style={{ display: "flex", gap: "1rem", alignItems: "center" }}>
    <Link to="/" style={{ color: "white", textDecoration: "none" }}>
      Home
    </Link>

    <Link to="/upload" style={{ color: "white", textDecoration: "none" }}>
      Upload
    </Link>

    <Link to="/dashboard" style={{ color: "white", textDecoration: "none" }}>
      Dashboard
    </Link>

    <button
      onClick={logout}
      style={{
        background: "#ef4444",
        color: "white",
        border: "none",
        padding: "8px 14px",
        borderRadius: "8px",
        cursor: "pointer",
        fontWeight: 600
      }}
    >
      Logout
    </button>
  </div>
</nav>

);
}
