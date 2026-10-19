import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import api from "../services/api";

export default function Register() {
const navigate = useNavigate();

const [form, setForm] = useState({
full_name: "",
email: "",
password: "",
role: "Viewer",
});

const handleSubmit = async (e) => {
e.preventDefault();


try {
  await api.post("/auth/register", form);
  alert("Account created successfully");
  navigate("/login");
} catch (err) {
  alert(err.response?.data?.detail || "Registration failed");
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
      onSubmit={handleSubmit}
      style={{
        background: "white",
        padding: "2rem",
        borderRadius: "12px",
        width: "360px",
        boxShadow: "0 4px 16px rgba(0,0,0,0.1)",
      }}
    >
      <h2 style={{ marginBottom: "1.5rem" }}>Create Account</h2>


  <input
    placeholder="Full Name"
    value={form.full_name}
    onChange={(e) =>
      setForm({ ...form, full_name: e.target.value })
    }
    style={{ width: "100%", padding: "10px", marginBottom: "1rem" }}
  />

  <input
    type="email"
    placeholder="Email"
    value={form.email}
    onChange={(e) =>
      setForm({ ...form, email: e.target.value })
    }
    style={{ width: "100%", padding: "10px", marginBottom: "1rem" }}
  />

  <input
    type="password"
    placeholder="Password"
    value={form.password}
    onChange={(e) =>
      setForm({ ...form, password: e.target.value })
    }
    style={{ width: "100%", padding: "10px", marginBottom: "1rem" }}
  />

  <select
    value={form.role}
    onChange={(e) =>
      setForm({ ...form, role: e.target.value })
    }
    style={{ width: "100%", padding: "10px", marginBottom: "1rem" }}
  >
    <option value="Viewer">Viewer</option>
    <option value="Reviewer">Reviewer</option>
  </select>

  <button type="submit" style={{ width: "100%" }}>
    Create Account
  </button>

  <p style={{ marginTop: "1rem", textAlign: "center" }}>
    Already have an account? <Link to="/login">Log In</Link>
  </p>
</form>


  </div>
);
}

