import {
  createRouter,
  createWebHashHistory,
} from "https://cdn.jsdelivr.net/npm/vue-router@4.4.5/+esm";
import { LoginPage, RegisterPage } from "../components/authPages.js";
import {
  AdminDashboard,
  DoctorManagement,
  AppointmentManagement,
  SearchPage,
} from "../components/adminPages.js";
import {
  DoctorDashboard,
  PatientList,
  AppointmentManager,
  TreatmentForm,
} from "../components/doctorPages.js";
import {
  PatientDashboard,
  DoctorSearch,
  AppointmentBooking,
  TreatmentHistory,
} from "../components/patientPages.js";

const routes = [
  { path: "/", redirect: "/login" },
  { path: "/login", name: "login", component: LoginPage },
  { path: "/register", name: "register", component: RegisterPage },

  { path: "/admin/dashboard", name: "adminDashboard", component: AdminDashboard, meta: { role: "admin", requiresAuth: true } },
  { path: "/admin/doctors", name: "doctorManagement", component: DoctorManagement, meta: { role: "admin", requiresAuth: true } },
  { path: "/admin/appointments", name: "appointmentManagement", component: AppointmentManagement, meta: { role: "admin", requiresAuth: true } },
  { path: "/admin/search", name: "searchPage", component: SearchPage, meta: { role: "admin", requiresAuth: true } },

  { path: "/doctor/dashboard", name: "doctorDashboard", component: DoctorDashboard, meta: { role: "doctor", requiresAuth: true } },
  { path: "/doctor/patients", name: "patientList", component: PatientList, meta: { role: "doctor", requiresAuth: true } },
  { path: "/doctor/appointments", name: "appointmentManager", component: AppointmentManager, meta: { role: "doctor", requiresAuth: true } },
  { path: "/doctor/treatment", name: "treatmentForm", component: TreatmentForm, meta: { role: "doctor", requiresAuth: true } },

  { path: "/patient/dashboard", name: "patientDashboard", component: PatientDashboard, meta: { role: "patient", requiresAuth: true } },
  { path: "/patient/doctors", name: "doctorSearch", component: DoctorSearch, meta: { role: "patient", requiresAuth: true } },
  { path: "/patient/booking", name: "appointmentBooking", component: AppointmentBooking, meta: { role: "patient", requiresAuth: true } },
  { path: "/patient/treatments", name: "treatmentHistory", component: TreatmentHistory, meta: { role: "patient", requiresAuth: true } },
];

const router = createRouter({
  history: createWebHashHistory(),
  routes,
});

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem("token");
  const role = localStorage.getItem("role");

  if (to.meta.requiresAuth && !token) {
    return next({ name: "login" });
  }

  if (to.meta.role && to.meta.role !== role) {
    const dashboardByRole = {
      admin: "adminDashboard",
      doctor: "doctorDashboard",
      patient: "patientDashboard",
    };
    return next({ name: dashboardByRole[role] || "login" });
  }

  if ((to.name === "login" || to.name === "register") && token && role) {
    const defaultRoute = {
      admin: "adminDashboard",
      doctor: "doctorDashboard",
      patient: "patientDashboard",
    };
    return next({ name: defaultRoute[role] || "login" });
  }

  return next();
});

export default router;
