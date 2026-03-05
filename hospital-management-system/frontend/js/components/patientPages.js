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
  data: () => ({
    form: { doctor_id: "", date: "", reason: "" },
    done: false,
    error: "",
    validationErrors: [],
  }),
  methods: {
    validateForm() {
      const errors = [];
      const doctorId = Number(this.form.doctor_id);

      if (!Number.isInteger(doctorId) || doctorId <= 0) {
        errors.push("Doctor ID must be a positive number.");
      }

      if (!this.form.date) {
        errors.push("Appointment date and time are required.");
      } else {
        const selectedDate = new Date(this.form.date);
        if (Number.isNaN(selectedDate.getTime()) || selectedDate < new Date()) {
          errors.push("Appointment date and time must be in the future.");
        }
      }

      if (!this.form.reason || this.form.reason.trim().length < 3) {
        errors.push("Reason must contain at least 3 characters.");
      }

      this.validationErrors = errors;
      return errors.length === 0;
    },
    async book() {
      this.done = false;
      this.error = "";

      if (!this.validateForm()) {
        return;
      }

      const [appointment_date, timeWithSeconds] = this.form.date.split("T");
      const appointment_time = timeWithSeconds.slice(0, 5);

      try {
        await PatientApi.bookAppointment({
          doctor_id: Number(this.form.doctor_id),
          appointment_date,
          appointment_time,
          reason: this.form.reason.trim(),
        });
        this.done = true;
        this.form = { doctor_id: "", date: "", reason: "" };
      } catch (error) {
        this.error = error.message || "Failed to book appointment.";
      }
    },
  },
  template: `<div class="card"><div class="card-body"><h2 class="h4">Appointment Booking</h2><div v-if="done" class="alert alert-success py-2">Appointment request submitted.</div><div v-if="error" class="alert alert-danger py-2">{{ error }}</div><ul v-if="validationErrors.length" class="alert alert-warning py-2 mb-3"><li v-for="(item, idx) in validationErrors" :key="idx">{{ item }}</li></ul><form @submit.prevent="book"><div class="mb-3"><label class="form-label">Doctor ID</label><input class="form-control" v-model="form.doctor_id" required/></div><div class="mb-3"><label class="form-label">Date</label><input type="datetime-local" class="form-control" v-model="form.date" required/></div><div class="mb-3"><label class="form-label">Reason</label><textarea class="form-control" v-model="form.reason" required></textarea></div><button class="btn btn-primary">Book</button></form></div></div>`,
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
