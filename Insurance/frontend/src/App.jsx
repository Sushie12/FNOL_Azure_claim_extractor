import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

import Login from "./pages/Login";
import Home from "./pages/Home";
import Dashboard from "./pages/Dashboard";
import ClaimDetails from "./pages/ClaimDetails";
import UploadClaim from "./pages/UploadClaim";
import AccessDenied from "./pages/AccessDenied";
import { AuthProvider, useAuth } from "./context/AuthContext";

function ProtectedRoute({ children, allowedRoles }) {
  const { user, loading } = useAuth();
  const token = localStorage.getItem("token");

  if (!token) {
    return <Navigate to="/login" replace />;
  }

  if (loading) {
    return <p style={{ padding: "2rem" }}>Loading...</p>;
  }

  if (allowedRoles && !allowedRoles.includes(user?.role)) {
    return <AccessDenied />;
  }

  return children;
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />

          <Route
            path="/"
            element={
              <ProtectedRoute>
                <Home />
              </ProtectedRoute>
            }
          />

          <Route
            path="/claims/:id"
            element={
              <ProtectedRoute>
                <ClaimDetails />
              </ProtectedRoute>
            }
          />

          <Route
            path="/upload"
            element={
              <ProtectedRoute allowedRoles={["Admin", "Analyst"]}>
                <UploadClaim />
              </ProtectedRoute>
            }
          />

          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }
          />

          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
