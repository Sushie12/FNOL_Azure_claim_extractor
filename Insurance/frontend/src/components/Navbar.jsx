import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Navbar() {
  const navigate = useNavigate();
  const { user, hasRole, logout } = useAuth();

  const handleLogout = () => {
    logout();
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
        boxShadow: "0 2px 6px rgba(0,0,0,0.15)",
      }}
    >
      <h2 style={{ margin: 0 }}>Insurance Claim Analyzer</h2>

      <div style={{ display: "flex", gap: "1rem", alignItems: "center" }}>
        <Link to="/" style={{ color: "white", textDecoration: "none" }}>
          Home
        </Link>

        {hasRole("Admin", "Analyst") && (
          <Link to="/upload" style={{ color: "white", textDecoration: "none" }}>
            Upload
          </Link>
        )}

        <Link to="/dashboard" style={{ color: "white", textDecoration: "none" }}>
          Dashboard
        </Link>

        {user && (
          <span
            style={{
              background: "#1f2937",
              border: "1px solid #374151",
              padding: "6px 12px",
              borderRadius: "999px",
              fontSize: "0.85rem",
            }}
          >
            {user.email} · <strong>{user.role}</strong>
          </span>
        )}

        <button
          onClick={handleLogout}
          style={{
            background: "#ef4444",
            color: "white",
            border: "none",
            padding: "8px 14px",
            borderRadius: "8px",
            cursor: "pointer",
            fontWeight: 600,
          }}
        >
          Logout
        </button>
      </div>
    </nav>
  );
}
