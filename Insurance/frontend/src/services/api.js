
import axios from "axios";

const api = axios.create({
baseURL: "http://localhost:8000",
});

// api.interceptors.response.use(
//   (response) => response,

//   (error) => {
//     if (error.response?.status === 401) {

//       localStorage.removeItem("token");
//       localStorage.removeItem("name");
//       localStorage.removeItem("role");

//       window.location.href = "/login";
//     }

//     return Promise.reject(error);
//   }
// );



// ---------------- INACTIVITY LOGOUT ----------------

const INACTIVITY_LIMIT = 60 * 60 * 1000; // 60 minutes

let inactivityTimer;

const logoutUser = () => {
  localStorage.removeItem("token");
  localStorage.removeItem("name");
  localStorage.removeItem("role");

  window.location.href = "/login";
};

const resetInactivityTimer = () => {
  clearTimeout(inactivityTimer);

  // Only start timer if user is logged in
  if (localStorage.getItem("token")) {
    inactivityTimer = setTimeout(() => {
      logoutUser();
    }, INACTIVITY_LIMIT);
  }
};

const activityEvents = [
  "mousemove",
  "mousedown",
  "keydown",
  "scroll",
  "touchstart"
];

activityEvents.forEach((event) => {
  window.addEventListener(event, resetInactivityTimer);
});

// Start timer when the application loads
resetInactivityTimer();


// ---------------- JWT 401 HANDLER ----------------

api.interceptors.response.use(
  (response) => response,

  (error) => {
    if (error.response?.status === 401) {

      localStorage.removeItem("token");
      localStorage.removeItem("name");
      localStorage.removeItem("role");

      window.location.href = "/login";
    }

    return Promise.reject(error);
  }
);

export default api;



