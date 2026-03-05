import { AuthApi } from "../services/apiService.js";

export const LoginPage = {
  name: "LoginPage",
  data() {
    return {
      email: "",
      password: "",
      error: "",
      loading: false,
    };
  },
  methods: {
    async submitLogin() {
      this.loading = true;
      this.error = "";
      try {
        const { data } = await AuthApi.login({
          email: this.email,
          password: this.password,
        });
        localStorage.setItem("token", data.token);
        localStorage.setItem("role", data.role);
        this.$router.push({ name: `${data.role}Dashboard` });
      } catch (error) {
        this.error = error.response?.data?.message || "Login failed.";
      } finally {
        this.loading = false;
      }
    },
  },
  template: `
    <div class="row justify-content-center">
      <div class="col-lg-5">
        <div class="card shadow-sm">
          <div class="card-body p-4">
            <h2 class="h4 mb-3">Login</h2>
            <div v-if="error" class="alert alert-danger py-2">{{ error }}</div>
            <form @submit.prevent="submitLogin">
              <div class="mb-3">
                <label class="form-label">Email</label>
                <input v-model="email" type="email" class="form-control" required />
              </div>
              <div class="mb-3">
                <label class="form-label">Password</label>
                <input v-model="password" type="password" class="form-control" required />
              </div>
              <button class="btn btn-primary w-100" :disabled="loading">{{ loading ? 'Signing in...' : 'Login' }}</button>
            </form>
            <p class="mt-3 mb-0">Patient? <router-link to="/register">Create an account</router-link></p>
          </div>
        </div>
      </div>
    </div>
  `,
};

export const RegisterPage = {
  name: "RegisterPage",
  data() {
    return {
      form: {
        full_name: "",
        email: "",
        password: "",
        phone: "",
      },
      message: "",
      error: "",
      loading: false,
    };
  },
  methods: {
    async submitRegister() {
      this.loading = true;
      this.error = "";
      this.message = "";
      try {
        await AuthApi.register({ ...this.form, role: "patient" });
        this.message = "Registration complete. Please login.";
        this.form = { full_name: "", email: "", password: "", phone: "" };
      } catch (error) {
        this.error = error.response?.data?.message || "Registration failed.";
      } finally {
        this.loading = false;
      }
    },
  },
  template: `
    <div class="row justify-content-center">
      <div class="col-lg-6">
        <div class="card shadow-sm">
          <div class="card-body p-4">
            <h2 class="h4 mb-3">Patient Registration</h2>
            <div v-if="message" class="alert alert-success py-2">{{ message }}</div>
            <div v-if="error" class="alert alert-danger py-2">{{ error }}</div>
            <form @submit.prevent="submitRegister">
              <div class="mb-3"><label class="form-label">Full Name</label><input v-model="form.full_name" class="form-control" required /></div>
              <div class="mb-3"><label class="form-label">Email</label><input v-model="form.email" type="email" class="form-control" required /></div>
              <div class="mb-3"><label class="form-label">Phone</label><input v-model="form.phone" class="form-control" required /></div>
              <div class="mb-3"><label class="form-label">Password</label><input v-model="form.password" type="password" class="form-control" required /></div>
              <button class="btn btn-success w-100" :disabled="loading">{{ loading ? 'Creating...' : 'Register' }}</button>
            </form>
          </div>
        </div>
      </div>
    </div>
  `,
};
