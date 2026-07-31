import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../services/api";

export default function Home() {
const navigate = useNavigate();

const [claims, setClaims] = useState([]);
const [page, setPage] = useState(1);
const [totalPages, setTotalPages] = useState(1);
const [loading, setLoading] = useState(true);

useEffect(() => {
loadClaims(page);
}, [page]);

const loadClaims = async (pageNumber) => {
try {
setLoading(true);


  const token = localStorage.getItem("token");

  const response = await api.get(
    `/claims?page=${pageNumber}&size=5`,
    {
      headers: {
        Authorization: `Bearer ${token}`
      }
    }
  );

  setClaims(response.data.claims || []);
  setTotalPages(response.data.totalPages || 1);
} catch (error) {
  console.error("Failed to load claims:", error);
} finally {
  setLoading(false);
}


};

const logout = () => {
localStorage.removeItem("token");
navigate("/login");
};

return (
<div style={{ minHeight: "100vh", background: "#f4f6f9" }}>
{/* Header */}
<header
style={{
background: "#0f172a",
color: "white",
padding: "1rem 2rem",
display: "flex",
justifyContent: "space-between",
alignItems: "center",
boxShadow: "0 2px 6px rgba(0,0,0,0.15)"
}}
> <div>
<h2 style={{ margin: 0 }}>Insurance Claim Analyzer</h2>
<p style={{ margin: "4px 0 0", fontSize: "0.9rem", color: "#cbd5e1" }}>
Claims management portal </p> </div>

```
    <div style={{ display: "flex", gap: "0.75rem" }}>
      <button
        onClick={() => navigate("/upload")}
        style={{
          background: "#2563eb",
          color: "white",
          border: "none",
          padding: "10px 16px",
          borderRadius: "8px",
          cursor: "pointer",
          fontWeight: 600
        }}
      >
        Upload a Claim
      </button>

      <button
        onClick={() => navigate("/dashboard")}
        style={{
          background: "#334155",
          color: "white",
          border: "none",
          padding: "10px 16px",
          borderRadius: "8px",
          cursor: "pointer",
          fontWeight: 600
        }}
      >
        Get Dashboard
      </button>

      <button
        onClick={logout}
        style={{
          background: "#ef4444",
          color: "white",
          border: "none",
          padding: "10px 16px",
          borderRadius: "8px",
          cursor: "pointer",
          fontWeight: 600
        }}
      >
        Logout
      </button>
    </div>
  </header>

  {/* Content */}
  <main style={{ padding: "2rem" }}>
    <div
      style={{
        background: "white",
        borderRadius: "14px",
        padding: "1.5rem",
        boxShadow: "0 2px 10px rgba(0,0,0,0.08)"
      }}
    >
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: "1rem"
        }}
      >
        <h2 style={{ margin: 0 }}>Claims Queue</h2>
        <span style={{ color: "#64748b" }}>
          Showing {claims.length} claims
        </span>
      </div>

      {loading ? (
        <p style={{ padding: "1rem", color: "#64748b" }}>
          Loading claims...
        </p>
      ) : claims.length === 0 ? (
        <div
          style={{
            textAlign: "center",
            padding: "3rem",
            color: "#64748b"
          }}
        >
          <p style={{ fontSize: "1.1rem", marginBottom: "0.5rem" }}>
            No claims found
          </p>
          <p>Upload a claim to get started.</p>
        </div>
      ) : (
        <>
          <div style={{ overflowX: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse" }}>
              <thead>
                <tr style={{ background: "#f8fafc" }}>
                  <th style={thStyle}>Claim ID</th>
                  <th style={thStyle}>Policyholder</th>
                  <th style={thStyle}>Agency</th>
                  <th style={thStyle}>Carrier</th>
                  <th style={thStyle}>Loss Date</th>
                  <th style={thStyle}>Est. Damage</th>
                  <th style={thStyle}>Route</th>
                </tr>
              </thead>

              <tbody>
                {claims.map((claim) => (
                  <tr
                    key={claim.id}
                    onClick={() => navigate(`/claims/${claim.id}`)}
                    style={{
                      cursor: "pointer",
                      borderBottom: "1px solid #e5e7eb"
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.background = "#f8fafc";
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.background = "transparent";
                    }}
                  >
                    <td style={tdStyle}>#{claim.id}</td>
                    <td style={tdStyle}>{claim.policyholder_name}</td>
                    <td style={tdStyle}>{claim.agency_name || "—"}</td>
                    <td style={tdStyle}>{claim.carrier}</td>
                    <td style={tdStyle}>{claim.date_of_loss || "—"}</td>
                    <td style={tdStyle}>
                      ₹{claim.estimated_damage || 0}
                    </td>
                    <td style={tdStyle}>
                      <span
                        style={{
                          padding: "4px 10px",
                          borderRadius: "999px",
                          background: "#dbeafe",
                          color: "#1d4ed8",
                          fontSize: "0.85rem",
                          fontWeight: 600
                        }}
                      >
                        {claim.recommended_route}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          <div
            style={{
              display: "flex",
              justifyContent: "center",
              alignItems: "center",
              gap: "1rem",
              marginTop: "1.5rem"
            }}
          >
            <button
              disabled={page === 1}
              onClick={() => setPage(page - 1)}
              style={pageButtonStyle(page === 1)}
            >
              Previous
            </button>

            <span style={{ fontWeight: 600, color: "#334155" }}>
              Page {page} of {totalPages}
            </span>

            <button
              disabled={page === totalPages}
              onClick={() => setPage(page + 1)}
              style={pageButtonStyle(page === totalPages)}
            >
              Next
            </button>
          </div>
        </>
      )}
    </div>
  </main>
</div>


);
}

const thStyle = {
textAlign: "left",
padding: "12px 14px",
fontWeight: 600,
color: "#374151",
borderBottom: "1px solid #e5e7eb"
};

const tdStyle = {
padding: "12px 14px",
color: "#111827"
};

const pageButtonStyle = (disabled) => ({
padding: "8px 14px",
borderRadius: "8px",
border: "none",
background: disabled ? "#cbd5e1" : "#2563eb",
color: "white",
cursor: disabled ? "not-allowed" : "pointer",
fontWeight: 600
});
