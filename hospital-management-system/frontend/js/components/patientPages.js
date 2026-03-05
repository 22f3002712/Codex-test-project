import { PatientApi } from "../services/apiService.js";

export const PatientDashboard = {
  name: "PatientDashboard",
  data: () => ({ profile: {} }),
  async mounted() {
    const { data } = await PatientApi.getDashboard();
    this.profile = data;
  },
  template: `<div class="card"><div class="card-body"><h1 class="h3">Patient Dashboard</h1><p class="mb-1"><strong>Name:</strong> {{ profile.name }}</p><p class="mb-0"><strong>Upcoming Appointments:</strong> {{ profile.upcoming_appointments || 0 }}</p></div></div>`,
};

export const DoctorSearch = {
  name: "DoctorSearch",
  data: () => ({ doctors: [] }),
  async mounted() {
    const { data } = await PatientApi.getDoctors();
    this.doctors = data;
  },
  template: `<div class="card"><div class="card-body"><h2 class="h4">Doctor Search</h2><div class="list-group"><div class="list-group-item" v-for="doc in doctors" :key="doc.id"><div class="fw-semibold">{{ doc.name }}</div><small>{{ doc.specialization }}</small></div></div></div></div>`,
};

export const AppointmentBooking = {
  name: "AppointmentBooking",
  data: () => ({ form: { doctor_id: "", date: "", reason: "" }, done: false }),
  methods: {
    async book() {
      await PatientApi.bookAppointment(this.form);
      this.done = true;
      this.form = { doctor_id: "", date: "", reason: "" };
    },
  },
  template: `<div class="card"><div class="card-body"><h2 class="h4">Appointment Booking</h2><div v-if="done" class="alert alert-success py-2">Appointment request submitted.</div><form @submit.prevent="book"><div class="mb-3"><label class="form-label">Doctor ID</label><input class="form-control" v-model="form.doctor_id" required/></div><div class="mb-3"><label class="form-label">Date</label><input type="datetime-local" class="form-control" v-model="form.date" required/></div><div class="mb-3"><label class="form-label">Reason</label><textarea class="form-control" v-model="form.reason" required></textarea></div><button class="btn btn-primary">Book</button></form></div></div>`,
};

export const TreatmentHistory = {
  name: "TreatmentHistory",
  data: () => ({ records: [] }),
  async mounted() {
    const { data } = await PatientApi.getTreatments();
    this.records = data;
  },
  template: `<div class="card"><div class="card-body"><h2 class="h4">Treatment History</h2><table class="table table-striped"><thead><tr><th>Date</th><th>Diagnosis</th><th>Prescription</th></tr></thead><tbody><tr v-for="item in records" :key="item.id"><td>{{ item.date }}</td><td>{{ item.diagnosis }}</td><td>{{ item.prescription }}</td></tr></tbody></table></div></div>`,
};
