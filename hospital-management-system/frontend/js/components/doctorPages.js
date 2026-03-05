import { DoctorApi } from "../services/apiService.js";

export const DoctorDashboard = {
  name: "DoctorDashboard",
  data: () => ({ summary: {} }),
  async mounted() {
    const { data } = await DoctorApi.getDashboard();
    this.summary = data;
  },
  template: `
    <div>
      <h1 class="h3 mb-3">Doctor Dashboard</h1>
      <div class="alert alert-info">Welcome back. Today's overview is below.</div>
      <div class="row g-3">
        <div class="col-md-4" v-for="(value, key) in summary" :key="key"><div class="card"><div class="card-body"><h3 class="h6">{{ key }}</h3><p class="display-6 mb-0">{{ value }}</p></div></div></div>
      </div>
    </div>
  `,
};

export const PatientList = {
  name: "PatientList",
  data: () => ({ patients: [] }),
  async mounted() {
    const { data } = await DoctorApi.getPatients();
    this.patients = data;
  },
  template: `
    <div class="card"><div class="card-body"><h2 class="h4">Patient List</h2><ul class="list-group"><li class="list-group-item" v-for="p in patients" :key="p.id">{{ p.name }} - {{ p.condition || 'N/A' }}</li></ul></div></div>
  `,
};

export const AppointmentManager = {
  name: "AppointmentManager",
  data: () => ({ appointments: [] }),
  async mounted() {
    const { data } = await DoctorApi.getAppointments();
    this.appointments = data;
  },
  template: `
    <div class="card"><div class="card-body"><h2 class="h4">Appointment Manager</h2><table class="table"><thead><tr><th>Patient</th><th>Date</th><th>Status</th></tr></thead><tbody><tr v-for="a in appointments" :key="a.id"><td>{{ a.patient_name }}</td><td>{{ a.date }}</td><td><span class="badge text-bg-secondary">{{ a.status }}</span></td></tr></tbody></table></div></div>
  `,
};

export const TreatmentForm = {
  name: "TreatmentForm",
  data: () => ({ payload: { patient_id: "", diagnosis: "", prescription: "" }, submitted: false }),
  methods: {
    async saveTreatment() {
      await DoctorApi.submitTreatment(this.payload);
      this.submitted = true;
      this.payload = { patient_id: "", diagnosis: "", prescription: "" };
    },
  },
  template: `
    <div class="card"><div class="card-body"><h2 class="h4">Treatment Form</h2><div v-if="submitted" class="alert alert-success py-2">Treatment submitted.</div><form @submit.prevent="saveTreatment"><div class="mb-3"><label class="form-label">Patient ID</label><input class="form-control" v-model="payload.patient_id" required></div><div class="mb-3"><label class="form-label">Diagnosis</label><textarea class="form-control" v-model="payload.diagnosis" required></textarea></div><div class="mb-3"><label class="form-label">Prescription</label><textarea class="form-control" v-model="payload.prescription" required></textarea></div><button class="btn btn-primary">Submit</button></form></div></div>
  `,
};
