import { createApp } from "https://cdn.jsdelivr.net/npm/vue@3.5.12/+esm";
import router from "./router/index.js";

const linksByRole = {
  admin: [
    { name: "adminDashboard", label: "AdminDashboard" },
    { name: "doctorManagement", label: "DoctorManagement" },
    { name: "appointmentManagement", label: "AppointmentManagement" },
    { name: "searchPage", label: "SearchPage" },
  ],
  doctor: [
    { name: "doctorDashboard", label: "DoctorDashboard" },
    { name: "patientList", label: "PatientList" },
    { name: "appointmentManager", label: "AppointmentManager" },
    { name: "treatmentForm", label: "TreatmentForm" },
  ],
  patient: [
    { name: "patientDashboard", label: "PatientDashboard" },
    { name: "doctorSearch", label: "DoctorSearch" },
    { name: "appointmentBooking", label: "AppointmentBooking" },
    { name: "treatmentHistory", label: "TreatmentHistory" },
  ],
};

const App = {
  computed: {
    isLoggedIn() {
      return Boolean(localStorage.getItem("token"));
    },
    role() {
      return localStorage.getItem("role");
    },
    navLinks() {
      return linksByRole[this.role] || [];
    },
  },
  methods: {
    logout() {
      localStorage.removeItem("token");
      localStorage.removeItem("role");
      this.$router.push({ name: "login" });
    },
  },
  template: `
    <div>
      <nav class="navbar navbar-expand-lg navbar-dark bg-primary rounded mb-4 px-3">
        <a class="navbar-brand" href="#">Hospital System</a>
        <div class="collapse navbar-collapse d-flex justify-content-between">
          <ul class="navbar-nav me-auto" v-if="isLoggedIn">
            <li class="nav-item" v-for="link in navLinks" :key="link.name">
              <router-link class="nav-link" :to="{ name: link.name }">{{ link.label }}</router-link>
            </li>
          </ul>
          <div class="d-flex gap-2">
            <router-link v-if="!isLoggedIn" class="btn btn-light btn-sm" to="/login">Login</router-link>
            <router-link v-if="!isLoggedIn" class="btn btn-outline-light btn-sm" to="/register">Register</router-link>
            <button v-if="isLoggedIn" class="btn btn-light btn-sm" @click="logout">Logout</button>
          </div>
        </div>
      </nav>
      <router-view />
    </div>
  `,
};

createApp(App).use(router).mount("#app");
