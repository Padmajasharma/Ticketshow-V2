<template>
  <div>
    
    <nav class="navbar">
      

      <div class="navbar-right">
      
        <button @click="goToDashboard" class="btn btn-primary dashboard-button">Dashboard</button>

        <button @click="logout" class="logout-button">Logout</button>
      </div>
    </nav>

    <div class="dashboard-table">
      <h1>Shows</h1>
      <div v-if="message">{{ message }}</div>

      <table v-if="shows.length > 0">
        <thead>
          <tr>
            <th>Name</th>
            <th>Rating</th>
            <th>Tags</th>
            <th>Ticket Price</th>
            <th>Start Time</th>
            <th>End Time</th>
            <th>Theatre</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="show in shows" :key="show.id">
            <td>{{ show.name }}</td>
            <td>{{ show.rating }}</td>
            <td>{{ show.tags }}</td>
            <td>{{ show.ticket_price }}</td>
            <td>{{ show.start_time }}</td>
            <td>{{ show.end_time }}</td>
            <td>{{ show.theatre_id }}</td>
            
            <td>
              <button @click="editShow(show)">Edit</button>
              <button @click="confirmDelete(show)">Delete</button>
            </td>
          </tr>
        </tbody>
      </table>

      <p v-else>No shows found</p>
      <button @click="showForm=true">Create New Show</button>
    </div>


    <div v-if="showForm">
      <h2 v-if="editMode">Edit Show</h2>
      <h2 v-else>Create New Show</h2>
        <label>Name:</label>
        <input type="text" v-model="showData.name" required>

        <label>Tags:</label>
        <input type="text" v-model="showData.tags" required>

        <label>Ticket Price:</label>
        <input type="number" v-model="showData.ticket_price" required>
        <label>Start Time:</label>
        <input type="datetime-local" v-model="showData.start_time" required>

        <label>End Time:</label>
        <input type="datetime-local" v-model="showData.end_time" required>

        <label>Image:</label>
        <input type="file" ref="imageInput" name="image" accept="image/*" @change="onFileChange">

<label>Theatre:</label>
<select v-model="showData.theatre_id" required>
  <option v-for="theatre in theatres" :key="theatre.id" :value="theatre.id">{{ theatre.name }}</option>
</select>


       


        <button type="button" @click="saveShow">{{ editMode ? 'Save' : 'Create' }}</button>
        <button type="button" @click="cancelForm">Cancel</button>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import jwtDecode from "jwt-decode";

export default {
  data() {
    return {
      shows: [],
      theatres: [], 
      showForm: false,
      editMode: false,
      showData: {
        id: null,
        name: '',
        start_time: null,
        end_time: null,
        tags: '',
        ticket_price: null,
        theatre_id: null,
        image: null, 
      },
      message: '',

    };
  },
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
   
    fetchShows() {
      const token = localStorage.getItem('access_token');
  if (!token) {
    console.error('Unauthorized: JWT token not found');
    return;
  }

  const headers = {"Access-Control-Allow-Origin": "*",
    Authorization: `Bearer ${token}`,
  };
      axios.get('http://127.0.0.1:5000/shows',{headers})
        .then(response => {
          this.shows = response.data;
          this.showForm = false;
        })
        .catch(error => {
          console.error('Error fetching shows:', error);
        });
    },

    fetchTheatres() {
 
  const token = localStorage.getItem('access_token');


  if (!token) {
    console.error('Unauthorized: JWT token not found');
    return;
  }

 
  const headers = { "Access-Control-Allow-Origin": "*",
    Authorization: `Bearer ${token}`,
  };

  axios.get('http://127.0.0.1:5000/theatres', { headers })
    .then(response => {
      this.theatres = response.data;

      
      this.showForm = false;
    })
    .catch(error => {
      console.error('Error fetching theatres:', error);
    });
},


    createShow() {
      
      this.showData.id = null;
      this.showData.name = '';
      this.showData.image = null;
      this.showData.start_time = null;
      this.showData.end_time = null;
      this.showData.tags = '';
      this.showData.ticket_price = null;
      this.showData.theatre_id = null;

      this.editMode = false;
      this.showForm = true;
    },

    editShow(show) {
      
      this.showData.id = show.id;
      this.showData.name = show.name;
      this.showData.start_time = show.start_time;
      this.showData.end_time = show.end_time; 
      this.showData.rating = show.rating;
      this.showData.tags = show.tags;
      this.showData.ticket_price = show.ticket_price;
      this.showData.theatre_id = show.theatre_id;

      this.editMode = true;
      this.showForm = true;
    },
    async saveShow() {
  const token = localStorage.getItem('access_token');

 
  if (!token) {
    console.error('Unauthorized: JWT token not found');
    return;
  }


  const headers = {"Access-Control-Allow-Origin": "*", 
    Authorization: `Bearer ${token}`,
  };

  if (this.editMode) {
  
    this.showData.start_time = this.formatDate(this.showData.start_time);
    this.showData.end_time = this.formatDate(this.showData.end_time);

    console.log('Formatted Start Time2:', this.showData.start_time);
console.log('Formatted End Time2:', this.showData.end_time);
    console.log(this.showData);
    axios.put(`http://127.0.0.1:5000/shows/${this.showData.id}`, this.showData, { headers })
      .then(response => {
        this.message = response.data.message;

   
        this.showForm = false;
        this.editMode = false;

      
        this.fetchShows();

   
      })
      .catch(error => {
        console.error('Error updating show:', error);
      });
  } 
  
  else {
    try {
  const formData = new FormData();
  formData.append('name', this.showData.name);
  formData.append('start_time', this.showData.start_time);
  formData.append('end_time', this.showData.end_time);
  formData.append('tags', this.showData.tags);
  formData.append('ticket_price', this.showData.ticket_price);
  formData.append('theatre_id', this.showData.theatre_id);

  const imageInput = this.$refs.imageInput;
  const imageFile = imageInput.files[0];
  formData.append('image', imageFile);

  const headers = {
    Authorization: `Bearer ${token}`,
    // 'Content-Type': 'multipart/form-data', // Remove this line
  };

  const response = await axios.post('http://127.0.0.1:5000/shows', formData, { headers });
  console.log(response.data);

  this.message = response.data.message;
  this.showForm = false;
  this.showData.name = '';
  this.showData.start_time = null;
  this.showData.end_time = null;
  this.showData.tags = '';
  this.showData.ticket_price = null;
  this.showData.theatre_id = null;
  this.showData.image = null;
  this.editMode = false;

  this.fetchShows();
} catch (error) {
  // Handle the error here, you can log it or show an error message to the user
  console.error('An error occurred:', error);
  // Optionally, show an error message to the user
  this.message = 'An error occurred while saving the data.';
}
  }
},
    // New code for creating a show with image as JSON

    /* const imageFile = this.showData.image; // Access the image data from showData

    if (!imageFile) {
      console.error('Image file is required');
      return;
    }

    const base64ImageData = await this.readFileAsBase64(imageFile);

    const jsonData = {
      name: this.showData.name,
      start_time: this.formatDate(this.showData.start_time),
      end_time: this.formatDate(this.showData.end_time),
      tags: this.showData.tags,
      ticket_price: this.showData.ticket_price,
      theatre_id: this.showData.theatre_id,
      image: base64ImageData, // Include the base64-encoded image data
    };

    try {
      const response = await axios.post('http://127.0.0.1:5000/shows', jsonData, { headers });

      console.log(response.data);
      this.message = response.data.message;
      this.showForm = false;

      this.fetchShows();
      // Reset your form data and other fields
    } catch (error) {
      console.error('An error occurred:', error);
      // Handle the error appropriately
      // Optionally, show an error message to the user
      this.message = 'An error occurred while saving the data.';
    }
  }
},

async readFileAsBase64(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result.split(',')[1]); // Extract the base64 part
    reader.onerror = reject;
    reader.readAsDataURL(file); // Convert the image to base64
  });
},

  */


formatDate(dateString) {
    const date = new Date(dateString);
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    
    const formattedDate = `${year}-${month}-${day}T${hours}:${minutes}`;
    return formattedDate;
},


    deleteShow(showId) {
      // Get the JWT token from localStorage
      const token = localStorage.getItem('access_token');

    
      if (!token) {
        console.error('Unauthorized: JWT token not found');
        return;
      }


      const headers = { "Access-Control-Allow-Origin": "*",
        Authorization: `Bearer ${token}`,
      };

     
      axios
        .delete(`http://127.0.0.1:5000/shows/${showId}`, { headers })
        .then(response => {
          this.message = response.data.message;

        
          this.shows = this.shows.filter(show => show.id !== showId);

        })
        .catch(error => {
          console.error('Error deleting show:', error);
        });
    },

    confirmDelete(show) {
      if (confirm('Are you sure you want to delete this show?')) {
        this.deleteShow(show.id);
      }
    },
    cancelForm() {
      this.showForm = false;
      this.editMode = false; 
    },
    logout() {
      localStorage.removeItem('access_token');
      this.$router.push('/');
    },
    onFileChange(event) {
  const file = event.target.files[0];
  console.log('Selected file:', file);
  this.showData.image = file;
},

goToDashboard() {
   
   this.$router.push('/adminDashboard');
 },

    
  },

  

  mounted() {
    this.fetchShows();
    this.fetchTheatres();
  },
};
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
</style>