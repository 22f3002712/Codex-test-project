import axios from "https://cdn.jsdelivr.net/npm/axios@1.7.7/+esm";

const API_BASE_URL = "http://localhost:5000/api";

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("token");
      localStorage.removeItem("role");
    }
    return Promise.reject(error);
  },
);

export const AuthApi = {
  login(payload) {
    return apiClient.post("/auth/login", payload);
  },
  register(payload) {
    return apiClient.post("/auth/register", payload);
  },
};

export const AdminApi = {
  getDashboard() {
    return apiClient.get("/admin/dashboard");
  },
  getDoctors() {
    return apiClient.get("/admin/doctors");
  },
  getAppointments() {
    return apiClient.get("/admin/appointments");
  },
  searchPatients(query) {
    return apiClient.get(`/admin/search?query=${encodeURIComponent(query)}`);
  },
};

export const DoctorApi = {
  getDashboard() {
    return apiClient.get("/doctor/dashboard");
  },
  getPatients() {
    return apiClient.get("/doctor/patients");
  },
  getAppointments() {
    return apiClient.get("/doctor/appointments");
  },
  submitTreatment(payload) {
    return apiClient.post("/doctor/treatments", payload);
  },
};

export const PatientApi = {
  getDashboard() {
    return apiClient.get("/patient/dashboard");
  },
  getDoctors() {
    return apiClient.get("/patient/doctors");
  },
  bookAppointment(payload) {
    return apiClient.post("/patient/appointments", payload);
  },
  getTreatments() {
    return apiClient.get("/patient/treatments");
  },
};

export default apiClient;
