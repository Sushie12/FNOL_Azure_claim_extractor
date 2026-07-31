


// import { useEffect, useState } from "react";
// import api from "../services/api";

// export default function Dashboard() {
//   const [claims, setClaims] = useState([]);
//   const [loading, setLoading] = useState(true);

//   async function fetchClaims() {
//     try {
//       const token = localStorage.getItem("token");
//       const response = await api.get("/claims", {
//         headers: {
//           Authorization: `Bearer ${token}`
//         }
//       });
//       console.log(response.data);

//       setClaims(response.data.claims || []);
//     } catch (error) {
//       console.error("Failed to fetch claims:", error);
//     } finally {
//       setLoading(false);
//     }
//   }

//   useEffect(() => {
//     fetchClaims();
//   }, []);

//   if (loading) {
//     return <p>Loading claims...</p>;
//   }

//   return (
//     <div style={{ padding: "2rem" }}>
//       <h2>Claims Dashboard</h2>

//       <div style={{ marginBottom: "1rem" }}>
//         <a href="/upload">
//             <button>Upload New Claim</button>
//         </a>
//       </div>

//       {claims.length === 0 ? (
//         <p>No claims found.</p>
//       ) : (
//         <table border="1" cellPadding="10" style={{ borderCollapse: "collapse" }}>
//           <thead>
//             <tr>
//               <th>ID</th>
//               <th>Policyholder</th>
//               <th>Carrier</th>
//               <th>Route</th>
//             </tr>
//           </thead>

//           <tbody>
//             {claims.map((claim) => (
//               <tr key={claim.id}>
//                 <td>{claim.id}</td>
//                 <td>{claim.policyholder_name}</td>
//                 <td>{claim.carrier}</td>
//                 <td>{claim.recommended_route}</td>
//               </tr>
//             ))}
//           </tbody>
//         </table>
//       )}
//     </div>
//   );
// }


import Navbar from "../components/Navbar";

export default function Dashboard() {
return (
<> <Navbar />
  <div className="page">
    <h1 style={{ marginBottom: "1.5rem" }}>Dashboard</h1>

    <div style={{
      display: "grid",
      gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
      gap: "1rem"
    }}>
      <div className="card">
        <h3>Total Claims</h3>
        <p style={{ fontSize: "2rem", marginTop: "0.5rem" }}>12</p>
      </div>

      <div className="card">
        <h3>Pending Review</h3>
        <p style={{ fontSize: "2rem", marginTop: "0.5rem" }}>5</p>
      </div>

      <div className="card">
        <h3>Approved</h3>
        <p style={{ fontSize: "2rem", marginTop: "0.5rem" }}>4</p>
      </div>

      <div className="card">
        <h3>Rejected</h3>
        <p style={{ fontSize: "2rem", marginTop: "0.5rem" }}>3</p>
      </div>
    </div>

    <div className="card" style={{ marginTop: "2rem" }}>
      <h3>Recent Activity</h3>
      <p style={{ marginTop: "1rem", color: "#6b7280" }}>
        Claims uploaded through the React portal will appear here.
      </p>
    </div>
  </div>
</>


);
}
