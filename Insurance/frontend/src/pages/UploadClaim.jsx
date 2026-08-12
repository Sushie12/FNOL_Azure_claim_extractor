import { useState } from "react";
import { useNavigate } from "react-router-dom";
import Navbar from "../components/Navbar";
import api from "../services/api";

export default function UploadClaim() {
const navigate = useNavigate();

const [file, setFile] = useState(null);
const [message, setMessage] = useState("");
const [loading, setLoading] = useState(false);

const handleUpload = async (e) => {
e.preventDefault();

if (!file) {
  setMessage("Please select a PDF file");
  return;
}

try {
  setLoading(true);
  setMessage("");

  const formData = new FormData();
  formData.append("file", file);

  await api.post("/upload", formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });

  setMessage("Claim uploaded successfully");

  // redirect back to home after 1 second
  setTimeout(() => {
    navigate("/");
  }, 1000);
} catch (error) {
  console.error(error);
  setMessage(
    error.deniedMessage ||
      error.response?.data?.detail ||
      "Upload failed"
  );
} finally {
  setLoading(false);
}

};

return (
<> <Navbar />
  <div style={{ padding: "2rem" }}>
    <div
      style={{
        maxWidth: "600px",
        margin: "0 auto",
        background: "white",
        padding: "2rem",
        borderRadius: "12px",
        boxShadow: "0 2px 10px rgba(0,0,0,0.08)",
      }}
    >
      <h2 style={{ marginBottom: "1.5rem" }}>Upload Insurance Claim</h2>

      <form onSubmit={handleUpload}>
        <div style={{ marginBottom: "1.5rem" }}>
          <label style={{ display: "block", marginBottom: "0.5rem" }}>
            Select Claim PDF
          </label>

          <input
            type="file"
            accept=".pdf"
            onChange={(e) => setFile(e.target.files[0])}
            style={{ width: "100%" }}
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          style={{
            background: "#2563eb",
            color: "white",
            border: "none",
            padding: "10px 18px",
            borderRadius: "8px",
            cursor: loading ? "not-allowed" : "pointer",
            fontWeight: 600,
          }}
        >
          {loading ? "Uploading..." : "Upload PDF"}
        </button>
      </form>

      {message && (
        <p
          style={{
            marginTop: "1rem",
            color: message.includes("successfully") ? "green" : "red",
            fontWeight: 500,
          }}
        >
          {message}
        </p>
      )}
    </div>
  </div>
</>


);
}
