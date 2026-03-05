const { createApp } = Vue;

createApp({
  data() {
    return {
      role: "admin",
      roles: ["admin", "doctor", "patient"],
    };
  },
  computed: {
    heading() {
      return `${this.role.charAt(0).toUpperCase()}${this.role.slice(1)} Dashboard`;
    },
  },
  template: `
    <div>
      <h1 class="mb-4">Hospital Management System</h1>
      <div class="card mb-4">
        <div class="card-body">
          <label for="role" class="form-label">View Dashboard</label>
          <select id="role" class="form-select" v-model="role">
            <option v-for="item in roles" :key="item" :value="item">{{ item }}</option>
          </select>
        </div>
      </div>
      <div class="alert alert-primary">
        <strong>{{ heading }}</strong>
        <p class="mb-0">Bootstrap-styled Vue SPA shell is ready for Admin, Doctor, and Patient workflows.</p>
      </div>
    </div>
  `,
}).mount("#app");
