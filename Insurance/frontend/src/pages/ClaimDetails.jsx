import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import Navbar from "../components/Navbar";
import api from "../services/api";

export default function ClaimDetails() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [claim, setClaim] = useState(null);

  useEffect(() => {
    const loadClaim = async () => {
      try {
        const token = localStorage.getItem("token");

        const response = await api.get(`/claims/${id}`, {
          headers: {
            Authorization: `Bearer ${token}`
          }
        });

        setClaim(response.data);
      } catch (error) {
        console.error(error);
      }
    };

    loadClaim();
  }, [id]);

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

          <Section title="Policy Information">
            <Field label="Policy Number" value={claim.policy_number} />
            <Field label="Policyholder" value={claim.policyholder_name} />
            <Field label="Policyholder Email" value={claim.policyholder_email} />
            <Field label="Carrier" value={claim.carrier} />
          </Section>

          <Section title="Incident Information">
            <Field label="Loss Date" value={claim.date_of_loss} />
            <Field label="Loss Time" value={claim.loss_time} />
            <Field label="Loss Location" value={claim.loss_location} />
            <Field label="Estimated Damage" value={`₹${claim.estimated_damage || 0}`} />
            <Field label="Injured" value={claim.injured} />
          </Section>

          <Section title="Involved Parties">
            <Field label="Agency" value={claim.agency} />
            <Field label="Contact Person" value={claim.contact_name} />
            <Field label="Contact Email" value={claim.contact_email} />
          </Section>

          <Section title="Asset Details">
            <Field label="Vehicle Make" value={claim.vehicle_make} />
            <Field label="Plate Number" value={claim.vehicle_plate_number} />
          </Section>

          <Section title="Result">
            <Field label="Recommended Route" value={claim.recommended_route} />
            <Field label="Reasoning" value={claim.reasoning} />
          </Section>

          <div style={{ marginTop: "2rem" }}>
            <h3>Accident Description</h3>
            <p>{claim.accident_description}</p>
          </div>

          <div style={{ marginTop: "1.5rem" }}>
            <h3>Damage Description</h3>
            <p>{claim.damage_description}</p>
          </div>
        </div>
      </div>
    </>
  );
}

function Section({ title, children }) {
  return (
    <div
      style={{
        border: "1px solid #b6bac1",
        borderRadius: "10px",
        padding: "1.25rem 1.5rem",
        marginBottom: "1.25rem"
      }}
    >
      <h3
        style={{
          margin: "0 0 1rem 0",
          fontSize: "0.95rem",
          fontWeight: 700,
          color: "#334155",
          textTransform: "uppercase",
          letterSpacing: "0.03em"
        }}
      >
        {title}
      </h3>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))",
          gap: "0.9rem"
        }}
      >
        {children}
      </div>
    </div>
  );
}

function Field({ label, value }) {
  return (
    <div>
      <strong>{label}:</strong> {value || "--"}
    </div>
  );
}