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

  try {
    const token = localStorage.getItem("token");

    const response = await api.patch(
      `/claims/${claimId}/status`,
      {
        claim_status: newStatus
      },
      {
        headers: {
          Authorization: `Bearer ${token}`
        }
      }
    );

    // Update the claim in the frontend immediately
    setClaims((prevClaims) =>
      prevClaims.map((claim) =>
        claim.id === claimId
          ? {
              ...claim,
              claim_status: response.data.claim_status,
              reviewer_status_changed:
                response.data.reviewer_status_changed,
              status_updated_by_name:
                response.data.status_updated_by_name,
              status_updated_by_role:
                response.data.status_updated_by_role
            }
          : claim
      )
    );

    alert("Claim status updated successfully.");

  } catch (error) {
    console.error("Failed to update status:", error);

    alert(
      error.response?.data?.detail ||
      "Failed to update claim status."
    );
  }
};




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
> 
<div>
<h2 style={{ margin: 0 }}>Insurance Claim Analyzer</h2>
<p style={{ margin: "4px 0 0", fontSize: "0.9rem", color: "#cbd5e1" }}>
Claims management portal </p> </div>

    <div style={{ display: "flex", gap: "0.75rem" }}>
      {role==="Admin" && <button
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
      </button>}

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
      textAlign: "center",
      marginBottom: "2rem",
    }}
    >
    <h1 style={{marginBottom: "0.5rem",color: "#0f172a",fontSize: "2rem",}}>Welcome, {fullName}! ({role})</h1>
    </div>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: "1rem"
        }} >
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
                  <th style={thStyle}>Status</th>
                  {(role === "Admin" || role === "Reviewer") && (
                    <th style={thStyle}>Action</th>
                  )}
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
                    <td style={tdStyle}>{claim.agency==="null"?"---": claim.agency}</td>
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

                    <td style={tdStyle}>

                      {/* Auto Approved claims cannot be manually edited */}
                      {claim.claim_status === "Auto Approved" ? (

                        <span
                          style={{
                            padding: "4px 10px",
                            borderRadius: "999px",
                            background: "#f1f5f9",
                            color: "#334155",
                            fontSize: "0.85rem",
                            fontWeight: 600
                          }}
                        >
                          Auto Approved
                        </span>

                      ) : role === "Admin" ? (

                        /* ADMIN CAN ALWAYS EDIT */
                        <div>

                          <select
                            value={
                              selectedStatuses[claim.id] ||
                              claim.claim_status ||
                              ""
                            }
                            onChange={(e) =>
                              handleStatusChange(
                                claim.id,
                                e.target.value
                              )
                            }
                            onClick={(e) => e.stopPropagation()}
                            style={{
                              padding: "6px 10px",
                              borderRadius: "6px",
                              border: "1px solid #cbd5e1",
                              background: "white",
                              fontWeight: 600,
                              cursor: "pointer"
                            }}
                          >
                            <option value="Approved">Approved</option>
                            <option value="Rejected">Rejected</option>
                            <option value="Escalated">Escalated</option>
                          </select>

                          {/* {claim.status_updated_by_name && (
                            <div
                              style={{
                                marginTop: "5px",
                                fontSize: "0.75rem",
                                color: "#64748b"
                              }}
                            >
                              {claim.claim_status} by{" "}
                              {claim.status_updated_by_role},{" "}
                              {claim.status_updated_by_name}
                            </div>
                          )} */}

                        </div>

                      ) : role === "Reviewer" &&
                        !claim.reviewer_status_changed ? (

                        /* REVIEWER CAN EDIT ONLY ONCE */
                        <select
                          value={selectedStatuses[claim.id] || ""}
                          onChange={(e) =>
                            handleStatusChange(
                              claim.id,
                              e.target.value
                            )
                          }
                          onClick={(e) => e.stopPropagation()}
                          style={{
                            padding: "6px 10px",
                            borderRadius: "6px",
                            border: "1px solid #cbd5e1",
                            background: "white",
                            fontWeight: 600,
                            cursor: "pointer"
                          }}
                        >
                          <option value="" disabled>
                            Select status
                          </option>

                          <option value="Approved">Approved</option>
                          <option value="Rejected">Rejected</option>
                          <option value="Escalated">Escalated</option>
                        </select>

                      ) : (

                        /* REVIEWER ALREADY USED THEIR ONE CHANGE */
                        <div>

                          <span
                            style={{
                              padding: "4px 10px",
                              borderRadius: "999px",
                              background: "#f1f5f9",
                              color: "#334155",
                              fontSize: "0.85rem",
                              fontWeight: 600
                            }}
                          >
                            {claim.claim_status || "—"}
                          </span>

                          {/* {claim.status_updated_by_name && (
                            <div
                              style={{
                                marginTop: "5px",
                                fontSize: "0.75rem",
                                color: "#64748b"
                              }}
                            >
                              {claim.claim_status} by{" "}
                              {claim.status_updated_by_role?.toLowerCase()}{" "}
                              {claim.status_updated_by_name}
                            </div>
                          )} */}

                        </div>

                      )}

                    </td>

                    {(role === "Admin" || role === "Reviewer") && (
                    <td style={tdStyle}>

                      {/* ADMIN CAN ALWAYS SUBMIT */}
                      {role === "Admin" &&
                        claim.claim_status !== "Auto Approved" && (
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              handleStatusSubmit(claim.id);
                            }}
                            style={{
                              padding: "7px 14px",
                              border: "none",
                              borderRadius: "6px",
                              background: "#2563eb",
                              color: "white",
                              cursor: "pointer",
                              fontWeight: 600
                            }}
                          >
                            Submit
                          </button>
                        )}

                      {/* REVIEWER CAN SUBMIT ONLY ONCE */}
                      {role === "Reviewer" &&
                        !claim.reviewer_status_changed &&
                        claim.claim_status !== "Auto Approved" && (
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              handleStatusSubmit(claim.id);
                            }}
                            style={{
                              padding: "7px 14px",
                              border: "none",
                              borderRadius: "6px",
                              background: "#2563eb",
                              color: "white",
                              cursor: "pointer",
                              fontWeight: 600
                            }}
                          >
                            Submit
                          </button>
                        )}

                      {/* STATUS UPDATE MESSAGE */}
                      {claim.status_updated_by_name && (
                        <div
                          style={{
                            marginTop: "6px",
                            fontSize: "0.75rem",
                            color: "#64748b",
                            lineHeight: "1.3"
                          }}
                        >
                          {claim.claim_status} by{" "}
                          {claim.status_updated_by_role?.toLowerCase()}{" "}
                          {claim.status_updated_by_name}
                        </div>
                      )}

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

const pageButtonStyle = (disabled) => ({
padding: "8px 14px",
borderRadius: "8px",
border: "none",
background: disabled ? "#cbd5e1" : "#2563eb",
color: "white",
cursor: disabled ? "not-allowed" : "pointer",
fontWeight: 600
});
