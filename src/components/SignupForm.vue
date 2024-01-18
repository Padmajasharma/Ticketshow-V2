<template>
  <div>
    <h2>Signup</h2>
    <div v-if="message">{{ message }}</div>
    <form @submit="signup">
      <label>ID</label>
      <input type="integer" v-model="id" required />
      <label>Email</label>
      <input type="text" v-model="email" required />
      <label>Username</label>
      <input type="text" v-model="username" required />
      <label>Password</label>
      <input type="password" v-model="password" required />
      <button type="submit">Signup</button>
    </form>
    <router-link to="/login">Already have an account? Login here</router-link>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      id: null,
      email:'',
      username: '',
      password: '',
      message: '',
    };
  },
  methods: {
    signup() {
      
      const headers = { "Access-Control-Allow-Origin": "*",'Content-Type': 'application/json'};

      axios.post('http://127.0.0.1:5000/signup', {id: this.id, email: this.email,
        username: this.username,
        password: this.password
       })
        .then(response => {
         
          this.message = response.data.message; 
          this.$router.push('/login'); 
        })
        .catch(error => {
         
          if (error.response && error.response.data && error.response.data.error) {
            this.message = error.response.data.error;
          } else {
            this.message = 'An error occurred during signup';
          }
        });
    }
  }
};
</script>
<style>
body {
  background-image: url("/src/assets/background.jpg");
  background-size: cover;
  background-position: center;
}
</style>
