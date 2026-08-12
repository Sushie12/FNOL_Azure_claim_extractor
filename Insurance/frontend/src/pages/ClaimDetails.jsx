import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import Navbar from "../components/Navbar";
import api from "../services/api";
import { useAuth } from "../context/AuthContext";

// Mirrors ALLOWED_TRANSITIONS in backend/app/utils/permissions.py.
// The server is the real gate; this only shapes the UI.
const STATUS_OPTIONS_BY_ROLE = {
  Admin: [
    "Pending Review",
    "Investigation In Progress",
    "Specialist Assigned",
    "Approved",
    "Rejected",
  ],
  Analyst: [
    "Pending Review",
    "Investigation In Progress",
    "Specialist Assigned",
  ],
  Reviewer: ["Approved", "Rejected"],
};

export default function ClaimDetails() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();

  const [claim, setClaim] = useState(null);
  const [status, setStatus] = useState("");
  const [message, setMessage] = useState("");

  const options = STATUS_OPTIONS_BY_ROLE[user?.role] || [];

  useEffect(() => {
    const loadClaim = async () => {
      try {
        const response = await api.get(`/claims/${id}`);
        setClaim(response.data);
        setStatus(response.data.claim_status || "");
      } catch (error) {
        console.error(error);
      }
    };

    loadClaim();
  }, [id]);

  const saveStatus = async () => {
    setMessage("");

    try {
      const response = await api.patch(`/claims/${id}/status`, {
        claim_status: status,
      });

      setClaim(response.data);
      setMessage(`Status updated to ${response.data.claim_status}`);
    } catch (error) {
      setMessage(
        error.deniedMessage ||
          error.response?.data?.detail ||
          "Could not update status"
      );
    }
  };

  if (!claim) return <p style={{ padding: "2rem" }}>Loading claim...</p>;

  return (
    <>
      <Navbar />

      <div className="page">
        <button onClick={() => navigate(-1)} style={{ marginBottom: "1rem" }}>
          ← Back
        </button>

        <div className="card">
          <h2 style={{ marginBottom: "1.5rem" }}>Claim #{claim.id}</h2>

          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))",
              gap: "1rem",
            }}
          >
            <div><strong>Policy Number:</strong> {claim.policy_number}</div>
            <div><strong>Policyholder:</strong> {claim.policyholder_name}</div>
            <div><strong>Policyholder Email:</strong> {claim.policyholder_email}</div>
            <div><strong>Carrier:</strong> {claim.carrier}</div>
            <div><strong>Agency:</strong> {claim.agency}</div>
            <div><strong>Contact Person:</strong> {claim.contact_name}</div>
            <div><strong>Loss Date:</strong> {claim.date_of_loss}</div>
            <div><strong>Loss Time:</strong> {claim.loss_time}</div>
            <div><strong>Loss Location:</strong> {claim.loss_location}</div>
            <div><strong>Vehicle Make:</strong> {claim.vehicle_make}</div>
            <div><strong>Plate Number:</strong> {claim.vehicle_plate_number}</div>
            <div><strong>Estimated Damage:</strong> ₹{claim.estimated_damage}</div>
            <div><strong>Recommended Route:</strong> {claim.recommended_route}</div>
            <div><strong>Risk Level:</strong> {claim.risk_level}</div>
            <div><strong>Current Status:</strong> {claim.claim_status}</div>
            <div><strong>Reasoning:</strong> {claim.reasoning}</div>
          </div>

          <div style={{ marginTop: "2rem" }}>
            <h3>Update Claim Status</h3>

            {options.length === 0 ? (
              <p style={{ color: "#64748b" }}>
                Your role ({user?.role}) cannot change claim status.
              </p>
            ) : (
              <div style={{ display: "flex", gap: "0.75rem", alignItems: "center" }}>
                <select
                  value={status}
                  onChange={(e) => setStatus(e.target.value)}
                  style={{ padding: "8px 10px", borderRadius: "8px" }}
                >
                  {!options.includes(status) && (
                    <option value={status}>{status}</option>
                  )}

                  {options.map((option) => (
                    <option key={option} value={option}>
                      {option}
                    </option>
                  ))}
                </select>

                <button
                  onClick={saveStatus}
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
                  Save
                </button>
              </div>
            )}

            {message && (
              <p style={{ marginTop: "1rem", fontWeight: 500 }}>{message}</p>
            )}
          </div>
        </div>
      </div>
    </>
  );
}
