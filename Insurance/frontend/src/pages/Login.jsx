// import { useState } from "react";
// import api from "../services/api";

// export default function Login() {
//   const [email, setEmail] = useState("");
//   const [password, setPassword] = useState("");
//   const [message, setMessage] = useState("");

//   const handleLogin = async (e) => {
//     e.preventDefault();

//     try {
//       const response = await api.post("/auth/login", {
//         email,
//         password,
//       });

//       localStorage.setItem("token", response.data.access_token);
//       setMessage("Login successful");
//     } catch (error) {
//       setMessage("Invalid credentials");
//     }
//   };

//   return (
//     <div style={{ padding: "2rem" }}>
//       <h2>Insurance Claim Analyzer</h2>

//       <form onSubmit={handleLogin}>
//         <div>
//           <input
//             type="email"
//             placeholder="Email"
//             value={email}
//             onChange={(e) => setEmail(e.target.value)}
//             required
//           />
//         </div>

//         <br />

//         <div>
//           <input
//             type="password"
//             placeholder="Password"
//             value={password}
//             onChange={(e) => setPassword(e.target.value)}
//             required
//           />
//         </div>

//         <br />

//         <button type="submit">Login</button>
//       </form>

//       <p>{message}</p>
//     </div>
//   );
// }


// import { useState } from "react";
// import api from "../services/api";

// export default function Login() {
//   const [email, setEmail] = useState("");
//   const [password, setPassword] = useState("");
//   const [message, setMessage] = useState("");

//   const handleLogin = async (e) => {
//     e.preventDefault();

//     try {
//       const response = await api.post("/auth/login", {
//         email: email.trim(),
//         password: password.trim(),
//       });

//        console.log("LOGIN RESPONSE:", response.data);

//        localStorage.setItem("token", response.data.access_token);
//        window.location.href = "/dashboard";
//     } catch (error) {
//       //console.error("LOGIN ERROR:", error.response?.data || error);

//       //setMessage(JSON.stringify(error.response?.data || "Login failed"));
//         console.log("FULL ERROR:", error);
//         console.log("RESPONSE:", error.response);
//         console.log("DATA:", error.response?.data);
//         setMessage(error.response?.data?.detail || error.message);
//     }
//   };

//   return (
//     <div style={{ padding: "2rem", fontFamily: "Arial" }}>
//       <h2>Insurance Claim Analyzer</h2>

//       <form onSubmit={handleLogin}>
//         <div>
//           <input
//             type="email"
//             placeholder="Email"
//             value={email}
//             onChange={(e) => setEmail(e.target.value)}
//             required
//           />
//         </div>

//         <br />

//         <div>
//           <input
//             type="password"
//             placeholder="Password"
//             value={password}
//             onChange={(e) => setPassword(e.target.value)}
//             required
//           />
//         </div>

//         <br />

//         <button type="submit">Login</button>
//       </form>

//       <p>
//         <strong>{message}</strong>
//       </p>
//     </div>
//   );
// }



import { useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../services/api";
import { useAuth } from "../context/AuthContext";

export default function Login() {
  const navigate = useNavigate();
  const { refreshUser } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleLogin = async (e) => {
    e.preventDefault();

    try {
      const response = await api.post("/auth/login", {
        email,
        password,
      });

      localStorage.setItem("token", response.data.access_token);
      await refreshUser();
      navigate("/");
    } catch (err) {
      setError("Invalid email or password");
    }
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        background: "#f3f4f6",
      }}
    >
      <form
        onSubmit={handleLogin}
        style={{
          background: "white",
          padding: "2rem",
          borderRadius: "12px",
          width: "360px",
          boxShadow: "0 4px 16px rgba(0,0,0,0.1)",
        }}
      >
        <h2 style={{ marginBottom: "1.5rem" }}>Sign In</h2>

        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          style={{ width: "100%", padding: "10px", marginBottom: "1rem" }}
          required
        />

        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          style={{ width: "100%", padding: "10px", marginBottom: "1rem" }}
          required
        />

        {error && (
          <p style={{ color: "red", marginBottom: "1rem" }}>{error}</p>
        )}

        <button type="submit" style={{ width: "100%" }}>
          Sign In
        </button>
      </form>
    </div>
  );
}