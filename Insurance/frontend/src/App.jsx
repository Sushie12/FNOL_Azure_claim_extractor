// import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

// import Login from "./pages/Login";
// import Home from "./pages/Home";
// import ClaimDetails from "./pages/ClaimDetails";
// import UploadClaim from "./pages/UploadClaim";
// import Dashboard from "./pages/Dashboard";

// function ProtectedRoute({ children }) {
// const token = localStorage.getItem("token");

// return token ? children : <Navigate to="/login" replace />;
// }

// export default function App() {
// return ( <BrowserRouter> <Routes>
// {/* Login page */}
// <Route path="/login" element={<Login />} />

//     {/* Home page = Claims Queue */}
//     <Route
//       path="/"
//       element={
//         <ProtectedRoute>
//           <Home />
//         </ProtectedRoute>
//       }
//     />

//     {/* Full claim details */}
//     <Route
//       path="/claims/:id"
//       element={
//         <ProtectedRoute>
//           <ClaimDetails />
//         </ProtectedRoute>
//       }
//     />

//     {/* Upload claim */}
//     <Route
//       path="/upload"
//       element={
//         <ProtectedRoute>
//           <UploadClaim />
//         </ProtectedRoute>
//       }
//     />

//     {/* Analytics dashboard */}
//     <Route
//       path="/dashboard"
//       element={
//         <ProtectedRoute>
//           <Dashboard />
//         </ProtectedRoute>
//       }
//     />

//     {/* Redirect any unknown route to home */}
//     <Route path="*" element={<Navigate to="/" replace />} />
//   </Routes>
// </BrowserRouter>

// );
// }


import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

import Login from "./pages/Login";
import Home from "./pages/Home";
import Dashboard from "./pages/Dashboard";
import ClaimDetails from "./pages/ClaimDetails";
import UploadClaim from "./pages/UploadClaim";

function ProtectedRoute({ children }) {
const token = localStorage.getItem("token");
return token ? children : <Navigate to="/login" />;
}

export default function App() {
return ( <BrowserRouter> <Routes>
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
        <ProtectedRoute>
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
  </Routes>
</BrowserRouter>

);
}

