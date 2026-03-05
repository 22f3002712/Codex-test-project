import { AdminApi } from "../services/apiService.js";

const listTemplate = (title, description, itemsName) => `
  <div class="card shadow-sm">
    <div class="card-body">
      <h2 class="h4">${title}</h2>
      <p class="text-muted">${description}</p>
      <ul class="list-group">
        <li class="list-group-item" v-for="item in ${itemsName}" :key="item.id">{{ item.name || item.title || item.id }}</li>
        <li v-if="!${itemsName}.length" class="list-group-item text-muted">No records found.</li>
      </ul>
    </div>
  </div>
`;

export const AdminDashboard = {
  name: "AdminDashboard",
  data: () => ({ stats: {} }),
  async mounted() {
    const { data } = await AdminApi.getDashboard();
    this.stats = data;
  },
  template: `
    <div>
      <h1 class="h3 mb-3">Admin Dashboard</h1>
      <div class="row g-3">
        <div class="col-md-4" v-for="(value, key) in stats" :key="key">
          <div class="card border-primary"><div class="card-body"><h3 class="h6 text-uppercase">{{ key }}</h3><p class="display-6 mb-0">{{ value }}</p></div></div>
        </div>
      </div>
    </div>
  `,
};

export const DoctorManagement = {
  name: "DoctorManagement",
  data: () => ({ doctors: [] }),
  async mounted() {
    const { data } = await AdminApi.getDoctors();
    this.doctors = data;
  },
  template: listTemplate("Doctor Management", "Review and maintain doctor records.", "doctors"),
};

export const AppointmentManagement = {
  name: "AppointmentManagement",
  data: () => ({ appointments: [] }),
  async mounted() {
    const { data } = await AdminApi.getAppointments();
    this.appointments = data;
  },
  template: listTemplate("Appointment Management", "Monitor appointment status and volume.", "appointments"),
};

export const SearchPage = {
  name: "SearchPage",
  data: () => ({ query: "", results: [] }),
  methods: {
    async search() {
      const { data } = await AdminApi.searchPatients(this.query);
      this.results = data;
    },
  },
  template: `
    <div class="card shadow-sm">
      <div class="card-body">
        <h2 class="h4">Search</h2>
        <div class="input-group mb-3">
          <input v-model="query" class="form-control" placeholder="Find patient by name/email" />
          <button class="btn btn-outline-primary" @click="search">Search</button>
        </div>
        <ul class="list-group">
          <li class="list-group-item" v-for="item in results" :key="item.id">{{ item.name }} - {{ item.email }}</li>
          <li v-if="!results.length" class="list-group-item text-muted">No results.</li>
        </ul>
      </div>
    </div>
  `,
};
