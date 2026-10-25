import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../services/api";

export default function Home() {
  const navigate = useNavigate();
  const fullName = localStorage.getItem("full_name");
  const role = localStorage.getItem("role");

  const [claims, setClaims] = useState([]);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(true);
  const [selectedStatuses, setSelectedStatuses] = useState({});

  const canAct = role === "Admin" || role === "Reviewer";

  // Auto Approved: always locked. Admin: never locked. Reviewer: locked after one change.
  const isLocked = (claim) => {
    if (claim.claim_status === "Auto Approved") return true;
    if (role === "Admin") return false;
    return Boolean(claim.reviewer_status_changed);
  };

  const handleStatusChange = (claimId, newStatus) => {
    setSelectedStatuses((prev) => ({
      ...prev,
      [claimId]: newStatus
    }));
  };

  const handleStatusSubmit = async (claimId) => {
    const newStatus = selectedStatuses[claimId];

    if (!newStatus) {
      alert("Please select a status.");
      return;
    }

    if (
      role === "Reviewer" &&
      !window.confirm(`Set status to "${newStatus}"? You can't change this again.`)
    ) {
      return;
    }

    try {
      const token = localStorage.getItem("token");

      const response = await api.patch(
        `/claims/${claimId}/status`,
        { claim_status: newStatus },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      // Update the claim immediately. If the backend response doesn't include
      // the name/role, fall back to the logged-in user's own details.
      setClaims((prevClaims) =>
        prevClaims.map((claim) =>
          claim.id === claimId
            ? {
                ...claim,
                claim_status: response.data.claim_status || newStatus,
                reviewer_status_changed:
                  response.data.reviewer_status_changed ??
                  (role === "Reviewer" ? true : claim.reviewer_status_changed),
                status_updated_by_name:
                  response.data.status_updated_by_name || fullName,
                status_updated_by_role:
                  response.data.status_updated_by_role || role
              }
            : claim
        )
      );

      // clear the temporary dropdown selection
      setSelectedStatuses((prev) => {
        const copy = { ...prev };
        delete copy[claimId];
        return copy;
      });

      alert("Claim status updated successfully.");
    } catch (error) {
      console.error("Failed to update status:", error);
      alert(error.response?.data?.detail || "Failed to update claim status.");
    }
  };

  useEffect(() => {
    loadClaims(page);
  }, [page]);

  const loadClaims = async (pageNumber) => {
    try {
      setLoading(true);

      const token = localStorage.getItem("token");

      const response = await api.get(`/claims?page=${pageNumber}&size=5`, {
        headers: { Authorization: `Bearer ${token}` }
      });

      setClaims(response.data.claims || []);
      setTotalPages(response.data.totalPages || 1);
    } catch (error) {
      console.error("Failed to load claims:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteClaim = async (claimId) => {
    if (
      !window.confirm(
        "Are you sure you want to delete this claim? This action cannot be undone."
      )
    ) {
      return;
    }

    try {
      const token = localStorage.getItem("token");

      await api.delete(`/claims/${claimId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });

      setClaims((prevClaims) => prevClaims.filter((claim) => claim.id !== claimId));
      alert("Claim deleted successfully.");
    } catch (error) {
      console.error("Failed to delete claim:", error);
      alert(error.response?.data?.detail || "Failed to delete claim.");
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
      >
        <div>
          <h2 style={{ margin: 0 }}>Insurance Claim Analyzer</h2>
          <p style={{ margin: "4px 0 0", fontSize: "0.9rem", color: "#cbd5e1" }}>
            Claims management portal
          </p>
        </div>

        <div style={{ display: "flex", gap: "0.75rem" }}>
          {role === "Admin" && (
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
          )}

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
          <div style={{ textAlign: "center", marginBottom: "2rem" }}>
            <h1 style={{ marginBottom: "0.5rem", color: "#0f172a", fontSize: "2rem" }}>
              Welcome, {fullName}! ({role})
            </h1>
          </div>

          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              marginBottom: "1rem"
            }}
          >
            <h2 style={{ margin: 0 }}>Claims Queue</h2>
            <span style={{ color: "#64748b" }}>Showing {claims.length} claims</span>
          </div>

          {loading ? (
            <p style={{ padding: "1rem", color: "#64748b" }}>Loading claims...</p>
          ) : claims.length === 0 ? (
            <div style={{ textAlign: "center", padding: "3rem", color: "#64748b" }}>
              <p style={{ fontSize: "1.1rem", marginBottom: "0.5rem" }}>No claims found</p>
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
                      <th style={thStyle}>Status</th>
                      {canAct && <th style={thStyle}>Action</th>}
                      {role === "Admin" && <th style={thStyle}></th>}
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
                        <td style={tdStyle}>
                          {claim.agency === "null" ? "---" : claim.agency}
                        </td>
                        <td style={tdStyle}>{claim.carrier}</td>
                        <td style={tdStyle}>{claim.date_of_loss || "—"}</td>
                        <td style={tdStyle}>₹{claim.estimated_damage || 0}</td>
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

                        {/* STATUS: final status, read-only, visible to everyone */}
                        <td style={tdStyle}>
                          <span style={statusBadgeStyle}>
                            {claim.claim_status || "—"}
                          </span>
                        </td>

                        {/* ACTION: Admin + Reviewer only */}
                        {canAct && (
                          <td style={tdStyle}>
                            {claim.claim_status === "Auto Approved" ? (
                              <span style={{ fontSize: "0.8rem", color: "#64748b" }}>
                                Auto approved by system
                              </span>
                            ) : (
                              <>
                                <div
                                  style={{
                                    display: "flex",
                                    alignItems: "center",
                                    gap: "8px"
                                  }}
                                >
                                  <select
                                    disabled={isLocked(claim)}
                                    value={
                                      selectedStatuses[claim.id] ||
                                      (role === "Admin" || isLocked(claim)
                                        ? claim.claim_status || ""
                                        : "")
                                    }
                                    onChange={(e) =>
                                      handleStatusChange(claim.id, e.target.value)
                                    }
                                    onClick={(e) => e.stopPropagation()}
                                    style={selectStyle(isLocked(claim))}
                                  >
                                    <option value="" disabled>
                                      Select status
                                    </option>
                                    <option value="Approved">Approved</option>
                                    <option value="Rejected">Rejected</option>
                                    <option value="Escalated">Escalated</option>
                                  </select>

                                  {!isLocked(claim) && (
                                    <button
                                      onClick={(e) => {
                                        e.stopPropagation();
                                        handleStatusSubmit(claim.id);
                                      }}
                                      style={submitButtonStyle}
                                    >
                                      Submit
                                    </button>
                                  )}
                                </div>

                                {/* "Approved by admin, System Administrator" */}
                                {claim.status_updated_by_name && (
                                  <div
                                    style={{
                                      marginTop: "4px",
                                      fontSize: "0.75rem",
                                      color: "#64748b"
                                    }}
                                  >
                                    {claim.claim_status} by{" "}
                                    {claim.status_updated_by_role?.toLowerCase()},{" "}
                                    {claim.status_updated_by_name}
                                  </div>
                                )}
                              </>
                            )}
                          </td>
                        )}

                        {/* DELETE: Admin only */}
                        {role === "Admin" && (
                          <td style={{ ...tdStyle, textAlign: "center" }}>
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                handleDeleteClaim(claim.id);
                              }}
                              title="Delete Claim"
                              style={{
                                background: "#fee2e2",
                                border: "none",
                                borderRadius: "6px",
                                padding: "6px 10px",
                                cursor: "pointer",
                                display: "inline-flex",
                                alignItems: "center",
                                justifyContent: "center",
                                color: "#ef4444"
                              }}
                              onMouseEnter={(e) =>
                                (e.currentTarget.style.background = "#fca5a5")
                              }
                              onMouseLeave={(e) =>
                                (e.currentTarget.style.background = "#fee2e2")
                              }
                            >
                              <svg
                                width="18"
                                height="18"
                                viewBox="0 0 24 24"
                                fill="none"
                                stroke="currentColor"
                                strokeWidth="2"
                                strokeLinecap="round"
                                strokeLinejoin="round"
                              >
                                <polyline points="3 6 5 6 21 6"></polyline>
                                <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                                <line x1="10" y1="11" x2="10" y2="17"></line>
                                <line x1="14" y1="11" x2="14" y2="17"></line>
                              </svg>
                            </button>
                          </td>
                        )}
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

const statusBadgeStyle = {
  padding: "4px 10px",
  borderRadius: "999px",
  background: "#f1f5f9",
  color: "#334155",
  fontSize: "0.85rem",
  fontWeight: 600
};

const selectStyle = (locked) => ({
  padding: "6px 10px",
  borderRadius: "6px",
  border: "1px solid #cbd5e1",
  background: locked ? "#f1f5f9" : "white",
  color: locked ? "#64748b" : "#111827",
  fontWeight: 600,
  cursor: locked ? "not-allowed" : "pointer",
  opacity: locked ? 0.8 : 1
});

const submitButtonStyle = {
  padding: "6px 12px",
  border: "none",
  borderRadius: "6px",
  background: "#2563eb",
  color: "white",
  cursor: "pointer",
  fontWeight: 600
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
