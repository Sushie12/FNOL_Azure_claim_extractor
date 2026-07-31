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
<> <Navbar />

  <div className="page">
    <button onClick={() => navigate(-1)} style={{ marginBottom: "1rem" }}>
      ← Back
    </button>

    <div className="card">
      <h2 style={{ marginBottom: "1.5rem" }}>Claim #{claim.id}</h2>

      <div style={{
        display: "grid",
        gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))",
        gap: "1rem"
      }}>
        <div><strong>Policy Number:</strong> {claim.policy_number}</div>
        <div><strong>Policyholder:</strong> {claim.policyholder_name}</div>
        <div><strong>Policyholder Email:</strong> {claim.policyholder_email}</div>
        <div><strong>Carrier:</strong> {claim.carrier}</div>
        <div><strong>Agency:</strong> {claim.agency_name}</div>
        <div><strong>Contact Person:</strong> {claim.contact_name}</div>
        <div><strong>Loss Date:</strong> {claim.date_of_loss}</div>
        <div><strong>Loss Time:</strong> {claim.loss_time}</div>
        <div><strong>Loss Location:</strong> {claim.loss_location}</div>
        <div><strong>Vehicle Make:</strong> {claim.vehicle_make}</div>
        <div><strong>Plate Number:</strong> {claim.plate_number}</div>
        <div><strong>Estimated Damage:</strong> ₹{claim.estimated_damage}</div>
        <div><strong>Recommended Route:</strong> {claim.recommended_route}</div>
        <div><strong>Reasoning:</strong> {claim.reasoning}</div>
      </div>

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
