<template>
  <div>
    <h2>Login</h2>

    <div v-if="message">{{ message }}</div>
    <form @submit.prevent="login">
      <label>Id</label>
      <input type="integer" v-model="id"/>
      <label>Username</label>
      <input type="text" v-model="username" required />
      <label>Password</label>
      <input type="password" v-model="password" required />
      <button type="submit">Login</button>
    </form>
    <router-link to="/signup">Don't have an account? Signup here</router-link>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      id: null,
      username: '',
      password: '',
      message: '', 
    };
  },
  methods: {
    login() {
      const headers = { 'Content-Type': 'application/json'};
    
      axios.post('http://127.0.0.1:5000/login', {
        username: this.username,
        password: this.password,
      },{headers})
      .then(response => {
        
        const token = response.data.token;
        const is_admin = response.data.is_admin;
       
        localStorage.setItem('access_token', token);
        
        localStorage.setItem('is_admin', is_admin);
        if (is_admin) {
          this.$router.push('/admindashboard');
        } else {
          this.$router.push('/userdashboard');
        }
      })
      .catch(error => {
        if (error.response && error.response.data && error.response.data.message) {
          this.message = error.response.data.message;
        } else {
          this.message = 'An error occurred during login';
        }
      });
    },
  },
};
</script>
<style>
body {
  background-image: url("/src/assets/background.jpg");
  background-size: cover;
  background-position: center;
}
</style>

