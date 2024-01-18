<template>
    <div>
      <button @click="goToDashboard" class="btn btn-primary dashboard-button">Dashboard</button>
      <button @click="logout" class="logout-button">Logout</button>
    
      <div>
        <h2>User Details</h2>
        <p>UserName: {{ user.username }}</p>
        <p>Email: {{ user.email }}</p>
        <!-- Other user details here -->
      </div>
  
      <div>
        <h2>Booked Tickets</h2>
        <ul>
        <li v-for="ticket in bookedTickets" :key="ticket.show_name">
          <h3>{{ ticket.show_name }}</h3>
          <p>Show Start: {{ ticket.show_start_time }}</p>
          <p>Show End: {{ ticket.show_end_time }}</p>
          <p>Number of Tickets: {{ ticket.ticket_count }}</p>
          <!-- Other ticket and show details here -->
        </li>
      </ul>
      </div>
    </div>
  </template>
  
  <script>
  import axios from 'axios';

  export default {
    data() {
      return {
        user: {}, // User details
        bookedTickets: [] // Array of booked tickets
      };
    },
    mounted() {
      // Fetch user data and booked tickets here
      // You can use axios or another HTTP library to make API requests
      this.fetchUserData();
    },
    methods: {
      logout() {
      localStorage.removeItem('access_token');
      this.$router.push('/');
    },
      goToDashboard() {
   
   this.$router.push('/userdashboard');
 },
 async fetchUserData() {
      const token = localStorage.getItem('access_token');
      console.log('Token:', token);

      if (!token) {
        console.error('Unauthorized: JWT token not found');
        return;
      }

      const headers = {
        Authorization: `Bearer ${token}`,
      };

      try {
        const response = await axios.get('http://localhost:5000/userprofile', { headers });
        this.user = response.data.user;
        this.bookedTickets = response.data.booked_shows;
        console.log(this.bookedTickets) // Set bookedTickets
      } catch (error) {
        console.error('Error fetching user data:', error);
      }
    }
}

};
</script>
<style>
.logout-button {
  position: absolute;
  top: 10px;
  right: 10px;
  padding: 5px 10px;
  background-color: #f44336;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
.dashboard-button {
  position: absolute;
  top: 10px;
  right: 80px; 
  background-color: #007bff; 
  color: #fff; 
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
</style>