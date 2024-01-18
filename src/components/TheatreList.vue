<template>
  <div>
    <nav class="navbar">
      
      <div class="navbar-right">
      
        
        <button @click="goToDashboard" class="btn btn-primary dashboard-button">Dashboard</button>
      
        <button @click="logout" class="logout-button">Logout</button>
      </div>
    </nav>
    <div class="dashboard-table">
      <h1>Theatres</h1>
      <div v-if="message">{{ message }}</div>
      <table v-if="theatres.length > 0">
        <thead>
          <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Place</th>
            <th>Capacity</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="theatre in theatres" :key="theatre.id" v-if="theatre">
            <td>{{ theatre.id }}</td>
            <td>{{ theatre.name }}</td>
            <td>{{ theatre.place }}</td>
            <td>{{ theatre.capacity }}</td>
            <td>
              <button @click="editTheatre(theatre)">Edit</button>
              <button @click="deleteTheatre(theatre.id)">Delete</button>
              <button @click="exportTheatreCSV(theatre.id)">Export CSV</button>
            </td>
          </tr>
        </tbody>
      </table>
      <p v-else>No theatres found</p>
      <button @click="showForm = true">Create New Theatre</button>
    </div>

   
    <div v-if="showForm">
      <h2 v-if="editMode">Edit Theatre</h2>
      <h2 v-else>Create New Theatre</h2>
      <div>
      
        <input type="hidden" v-model="theatreData.id">
        <label>Name:</label>
        <input type="text" v-model="theatreData.name" required>

        <label>Place:</label>
        <input type="text" v-model="theatreData.place" required>

        <label>Capacity:</label>
        <input type="number" v-model="theatreData.capacity" required>

        <button @click="saveTheatre">{{ editMode ? 'Save' : 'Create' }}</button>
        <button @click="cancelForm">Cancel</button>
      </div>
    </div>
  </div>
</template>





<script>
import axios from 'axios';
import jwtDecode from 'jwt-decode';

export default {
  data() {
    return {
      theatres: [],
      showForm: false,
      editMode: false,
      theatreData: {
        id: null,
        name: '',
        place: '',
        capacity: null,
      },
      message: '',
    };
  },
  props: ['theatre'],
  
  created() {
  const token = localStorage.getItem("access_token");
  if (token) {
    const decodedToken = jwtDecode(token);
    const expirationTime = decodedToken.exp * 1000; 
    const currentTime = Date.now();

    const timeUntilExpiration = expirationTime - currentTime;
    setTimeout(() => {
      
      this.logout();
    }, timeUntilExpiration);
  }
},
  methods: {
    fetchTheatres() {

  const token = localStorage.getItem('access_token');


  if (!token) {
    console.error('Unauthorized: JWT token not found');
    return;
  }

  const headers = {  "Access-Control-Allow-Origin": "*",
    Authorization: `Bearer ${token}`,
  };

  axios.get('http://127.0.0.1:5000/theatres', { headers } ,console.log('request sent'))
    .then(response => {
      this.theatres = response.data;

     
      this.showForm = false;
    })
    .catch(error => {
      console.error('Error fetching theatres:', error);
    });
},



editTheatre(theatre) {
  if (theatre) {
    this.theatreData.id = theatre.id;
    this.theatreData.name = theatre.name;
    this.theatreData.place = theatre.place;
    this.theatreData.capacity = theatre.capacity;
    this.editMode = true;
    this.showForm = true;
  } 
},

    cancelForm() {
      this.showForm = false;
      this.editMode = false; 
    },

    saveTheatre() {
   
    const token = localStorage.getItem('access_token');

    if (!token) {
      console.error('Unauthorized: JWT token not found');
      return;
    }

    const headers = { "Access-Control-Allow-Origin": "*",
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
    };

    if (this.editMode) {
      const theatreId = this.theatreData.id;
      axios
        .put(`http://127.0.0.1:5000/theatres/${theatreId}`, this.theatreData, { headers })
        .then(response => {
          this.message = response.data.message;

         
          const index = this.theatres.findIndex(theatre => theatre.id === this.theatreData.id);
          if (index !== -1) {
            this.theatres[index] = { ...this.theatreData };
          }

        
          this.showForm = false;
          this.editMode = false;

          
          this.fetchTheatres();

          
        })
        .catch(error => {
          console.error('Error updating theatre:', error);
        });
    } else {
     
      axios
        .post('http://127.0.0.1:5000/theatres', this.theatreData, { headers })
        .then(response => {
          this.message = response.data.message;

          this.theatres.push(response.data.theatre);
          

          
          this.showForm = false;
          this.theatreData.name = '';
          this.theatreData.place = '';
          this.theatreData.capacity = null;
          this.editMode = false; 
        
          this.fetchTheatres();

          
        })
        .catch(error => {
          console.error('Error creating theatre:', error);
        });
    }
  },

  deleteTheatre(theatreId) {
  
  const token = localStorage.getItem('access_token');


  if (!token) {
    console.error('Unauthorized: JWT token not found');
    return;
  }


  const headers = {
    Authorization: `Bearer ${token}`,
  };

 
  axios
    .delete(`http://127.0.0.1:5000/theatres/${theatreId}`, { headers })
    .then(response => {
      this.message = response.data.message;

      this.theatres = this.theatres.filter(theatre => theatre.id !== theatreId);


    })
    .catch(error => {
      console.error('Error deleting theatre:', error);
    });
},
logout() {
      
      localStorage.removeItem('access_token');
      this.$router.push('/');
    },
    goToDashboard() {
   
      this.$router.push('/adminDashboard');
    },
    
    exportTheatreCSV(theatreId) {
  const token = localStorage.getItem('access_token');

  if (!token) {
    console.error('Unauthorized: JWT token not found');
    return;
  }

  
  const headers = {
    Authorization: `Bearer ${token}`,
  };

  
  console.log('Headers:', headers);
  console.log('Before axios.get');
  axios.get(`http://127.0.0.1:5000/export_theatre/${theatreId}`, { headers, responseType: 'blob' })
    .then(response => {
      console.log('Response status:', response.status);

     
      const blob = new Blob([response.data], { type: 'application/csv' });


      const url = window.URL.createObjectURL(blob);

   
      window.open(url);
    })
    .catch(error => {
      console.error('Error triggering export task:', error);
    });

  console.log('After axios.get');
}


  
}, 
  
mounted() {
    this.fetchTheatres();
  },

}

</script>
<style>
.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
 
}

.navbar-right {
  display: flex;
  align-items: center;
}


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
.dashboard-table { 
  padding: 20px;
  border-radius: 8px;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 20px;
  border: 2px solid #333;
}

th,
td {
  padding: 10px;
  text-align: left;
  border-bottom: 1px solid ; 
}

thead th {
  background-color: #555; 
  color: white; 
}

button {
  background-color: #4CAF50; 
  color: white;
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin-right: 5px;
}

button:hover {
  background-color: #45a049; 
.dashboard-link {
  margin-left: 200px; 
}}
</style>
