import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function AccessDenied() {
  const navigate = useNavigate();
  const { user } = useAuth();

  return (
    <div
      style={{
        minHeight: "100vh",
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        alignItems: "center",
        background: "#f3f4f6",
        gap: "0.75rem",
      }}
    >
      <h1 style={{ margin: 0, fontSize: "3rem", color: "#ef4444" }}>403</h1>

      <h2 style={{ margin: 0 }}>Access Denied</h2>

      <p style={{ color: "#475569" }}>
        Your role <strong>{user?.role || "unknown"}</strong> is not allowed to
        open this page.
      </p>

      <button
        onClick={() => navigate("/")}
        style={{
          background: "#2563eb",
          color: "white",
          border: "none",
          padding: "10px 18px",
          borderRadius: "8px",
          cursor: "pointer",
          fontWeight: 600,
        }}
      >
        Back to Claims Queue
      </button>
    </div>
  );
}
