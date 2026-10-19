import { useEffect, useState } from "react";
import Navbar from "../components/Navbar";
import api from "../services/api";

export default function Dashboard() {
  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      const token = localStorage.getItem("token");

      const response = await api.get("/dashboard", {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });

      setDashboard(response.data);

    } catch (error) {
      console.error("Failed to load dashboard:", error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <>
        <Navbar />

        <div className="page">
          <h1>Dashboard</h1>
          <p>Loading dashboard...</p>
        </div>
      </>
    );
  }

  if (!dashboard) {
    return (
      <>
        <Navbar />

        <div className="page">
          <h1>Dashboard</h1>
          <p>Failed to load dashboard.</p>
        </div>
      </>
    );
  }

  return (
    <>
      <Navbar />

      <div className="page">
        <h1 style={{ marginBottom: "1.5rem" }}>
          Dashboard
        </h1>

        <div
          style={{
            display: "grid",
            gridTemplateColumns:
              "repeat(auto-fit, minmax(220px, 1fr))",
            gap: "1rem"
          }}
        >

          {/* Total Claims */}
          <div className="card">
            <h3>Total Claims</h3>

            <p
              style={{
                fontSize: "2rem",
                marginTop: "0.5rem"
              }}
            >
              {dashboard.totalClaims}
            </p>
          </div>


          {/* Pending Review */}
          <div className="card">
            <h3>Pending Review</h3>

            <p
              style={{
                fontSize: "2rem",
                marginTop: "0.5rem"
              }}
            >
              {dashboard.pendingReview}
            </p>
          </div>


          {/* Approved */}
          <div className="card">
            <h3>Approved</h3>

            <p
              style={{
                fontSize: "2rem",
                marginTop: "0.5rem"
              }}
            >
              {dashboard.approved}
            </p>
          </div>


          {/* Rejected */}
          <div className="card">
            <h3>Rejected</h3>

            <p
              style={{
                fontSize: "2rem",
                marginTop: "0.5rem"
              }}
            >
              {dashboard.rejected}
            </p>
          </div>

        </div>

        {/* Claim Statistics */}
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
            gap: "1rem",
            marginTop: "1rem"
          }}>

          <div className="card">
            <h3>Average Claim Amount</h3>
            <p style={{ fontSize: "2rem", marginTop: "0.5rem" }}>
              ₹{dashboard.averageClaimAmount}
            </p>
          </div>

          <div className="card">
            <h3>Highest Claim Amount</h3>
            <p style={{ fontSize: "2rem", marginTop: "0.5rem" }}>
              ₹{dashboard.highestClaimAmount}
            </p>
          </div>

          <div className="card">
            <h3>Average Risk Score</h3>
            <p style={{ fontSize: "2rem", marginTop: "0.5rem" }}>
              {dashboard.averageRiskScore}
            </p>
          </div>

          <div className="card">
            <h3>Highest Risk Score</h3>
            <p style={{ fontSize: "2rem", marginTop: "0.5rem" }}>
              {dashboard.highestRiskScore}
            </p>
          </div>
        </div>


        {/* Risk Distribution */}
        <div
          className="card"
          style={{ marginTop: "2rem" }}
        >
          <h3>Claims by Risk Level</h3>

          <div
            style={{
              display: "flex",
              gap: "1rem",
              marginTop: "1rem",
              flexWrap: "wrap"
            }}
          >
            <div>
              <strong>Low</strong>
              <p>{dashboard.claimsByRiskLevel.low}</p>
            </div>

            <div>
              <strong>Medium</strong>
              <p>{dashboard.claimsByRiskLevel.medium}</p>
            </div>

            <div>
              <strong>High</strong>
              <p>{dashboard.claimsByRiskLevel.high}</p>
            </div>
          </div>
        </div>

        {/* Route Distribution */}
        <div
          className="card"
          style={{ marginTop: "2rem" }}
        >
          <h3>Claims by Route</h3>

          <div style={{ marginTop: "1rem" }}>
            {dashboard.routeDistribution.map((item) => (
              <div
                key={item.route}
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  padding: "0.75rem 0",
                  borderBottom: "1px solid #e5e7eb"
                }}
              >
                <span>{item.route}</span>
                <strong>{item.count}</strong>
              </div>
            ))}
          </div>
        </div>


        {/* Carrier Distribution */}
        <div
          className="card"
          style={{ marginTop: "2rem" }}
        >
          <h3>Claims by Carrier</h3>

          <div style={{ marginTop: "1rem" }}>
            {dashboard.carrierDistribution.map((item) => (
              <div
                key={item.carrier}
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  padding: "0.75rem 0",
                  borderBottom: "1px solid #e5e7eb"
                }}
              >
                <span>{item.carrier || "Unknown"}</span>
                <strong>{item.count}</strong>
              </div>
            ))}
          </div>
        </div>


        {/* Recent Activity */}
        <div
          className="card"
          style={{ marginTop: "2rem" }}
        >
          <h3>Recent Activity</h3>

          {dashboard.recentClaims &&
          dashboard.recentClaims.length > 0 ? (

            <div style={{ marginTop: "1rem" }}>

              {dashboard.recentClaims.map((claim) => (
                <div
                  key={claim.id}
                  style={{
                    padding: "0.75rem 0",
                    borderBottom:
                      "1px solid #e5e7eb"
                  }}
                >
                  <strong>
                    Claim #{claim.id}
                  </strong>

                  {" — "}

                  {claim.policyholder_name}

                  {" — "}

                  {claim.claim_status || "No status"}
                </div>
              ))}

            </div>

          ) : (

            <p
              style={{
                marginTop: "1rem",
                color: "#6b7280"
              }}
            >
              No recent claims.
            </p>

          )}
        </div>

      </div>
    </>
  );
}