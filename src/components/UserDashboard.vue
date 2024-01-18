<template>
  <div>
    <button @click="Profile" class="btn btn-primary profile-button">Profile</button>
    <button @click="logout" class="btn btn-primary logout-button">Logout</button>
    <div v-if="message">{{ message }}</div>
    <input type="text" v-model="searchQuery" @input="performSearch" placeholder="Enter your search query">
    <label>Search by:</label>
    <select v-model="searchOption">
      <option value="theatreName">Theatre Name</option>
      <option value="theatrePlace">Theatre Place</option>
      <option value="showTags">Show Tags</option>
      <option value="showRating">Show Rating</option>
    </select>

    <div v-if="searchResults.length > 0">
      <h2>Search Results</h2>
      <ul v-if="searchOption === 'theatreName'">
        <li v-for="result in searchResults" :key="result.id">
          {{ result.name }} - {{ result.place }}
        </li>
      </ul>
      <ul v-else-if="searchOption === 'theatrePlace'">
        <li v-for="result in searchResults" :key="result.id">
          {{ result.name }} - {{ result.place }}
        </li>
      </ul>
      <ul v-else-if="searchOption === 'showTags'">
        <li v-for="result in searchResults" :key="result.id">
          {{ result.name }} - Tags: {{ result.tags }}
        </li>
      </ul>
      <ul v-else-if="searchOption === 'showRating'">
        <li v-for="result in searchResults" :key="result.id">
          {{ result.name }} - Rating: {{ result.rating }}
        </li>
      </ul>
    </div>

    <h1>Shows Available</h1>
    <div v-if="shows.length > 0" class="row">
  <div v-for="show in shows" :key="show.id" class="col-md-4">
    <div class="show-card-container">
      <div class="show-card" style="background-color: white; padding: 10px; margin: 10px;">
        <img :src="show.image" class="card-img-top" alt="Show Image" style="width: 100%; height: auto;">

        <h5>{{ show.name }}</h5>
        <p><strong>Theatre:</strong> {{ show.theatre_id }}</p>
        <p><strong>Start Time:</strong> {{ show.start_time }}</p>
        <p><strong>End Time:</strong> {{ show.end_time }}</p>
        <p><strong>Tags:</strong> {{ show.tags }}</p>
        <p><strong>Price:</strong> {{ show.ticket_price }}</p>
        

            <div v-if="show.id === selectedShowId && !bookingStatus">
              <label for="rating">Your Rating:</label>
              <input type="number" id="rating" v-model="rating" min="1" max="5" required>
            </div>
        <button
  v-if="!selectedShowId || selectedShowId !== show.id"
  :disabled="show.capacity === 0"
  @click="showBookingForm = true, selectedShowId = show.id"
  class="btn btn-primary"
>
  {{ show.capacity > 0 ? 'Book Tickets' : 'Houseful' }}
</button>

  <div v-if="selectedShowId === show.id && !bookingStatus">
  <form @submit.prevent="bookTickets(show.id)">
    <label for="numberOfTickets">Number of Tickets:</label>
    <input type="number" id="numberOfTickets" v-model="numberOfTickets" required>
    <button type="submit" class="btn btn-primary">Confirm Booking</button>
    <button @click="cancelBooking" class="btn btn-primary">Cancel</button>
  </form>
</div>
<div v-if="bookingStatus">
  <p>Tickets booked for {{ show.name }}. Thank you!</p>
</div>


      </div>
    </div>
  </div>
</div>

    </div>
</template>

<script>
import axios from 'axios';
import jwtDecode from "jwt-decode";


export default {
  data() {
    return {
      searchQuery: '',
      searchOption: 'theatreName', 
      searchResults: [],
      shows:[],
      message: '',
      showBookingForm: false,
      numberOfTickets: 0,
      selectedShowId: null,
      bookingStatus: false,
      bookedShowName:'',
      rating: 0,
    };
  },
  created() {
    this.fetchShows()
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
    performSearch() {
      const token = localStorage.getItem('access_token');
      console.log('Token:', token);

  if (!token) {
    console.error('Unauthorized: JWT token not found');
    return;
  }

  const headers = { 
    Authorization: `Bearer ${token}`,
  };
      if (this.searchOption === 'theatreName') {
        axios.get(`http://localhost:5000/search/theatres?name=${this.searchQuery}`,{ headers})
          .then((response) => {
            this.searchResults = response.data;

          })
          .catch((error) => {
            console.error('Error performing theatre name search:', error);
          });
      } else if (this.searchOption === 'theatrePlace') {
        axios.get(`http://localhost:5000/search/theatres?place=${this.searchQuery}`,{ headers })
          .then((response) => {
            this.searchResults = response.data;
          })
          .catch((error) => {
            console.error('Error performing theatre place search:', error);
          });
      } else if (this.searchOption === 'showTags') {
        axios.get(`http://localhost:5000/search/shows?tags=${this.searchQuery}`,{ headers })
          .then((response) => {
            this.searchResults = response.data;
          })
          .catch((error) => {
            console.error('Error performing show tags search:', error);
          });
      } else if (this.searchOption === 'showRating') {
        axios.get(`http://localhost:5000/search/shows?rating=${this.searchQuery}`,{ headers })
          .then((response) => {
            this.searchResults = response.data;
          })
          .catch((error) => {
            console.error('Error performing show rating search:', error);
          });
      }
    },
    logout() {
      localStorage.removeItem('access_token');
      this.$router.push('/');
    },
    Profile() {
      this.$router.push('/userprofile');
    },
    fetchShows() {
      
      const token = localStorage.getItem('access_token');
      console.log('Token:', token);

 
  if (!token) {
    console.error('Unauthorized: JWT token not found');
    return;
  }

 
  const headers = {
    Authorization: `Bearer ${token}`,
  };
     
      axios.get(`http://localhost:5000/shows`,{headers})
        .then((response) => { 
          console.log('Response:', response);
          this.shows = response.data;
        })
        .catch((error) => {
          console.error('Error fetching shows:', error);
          
        });
    },
    bookTickets(showId) {
  console.log('Book Tickets method called');

  const token = localStorage.getItem('access_token');
  console.log('Token:', token);

  if (!token) {
    console.error('Unauthorized: JWT token not found');
    return;
  }

  const headers = {
    "Access-Control-Allow-Origin": "*",
    Authorization: `Bearer ${token}`,
  };

  const show = this.shows.find((show) => show.id === showId);
  if (show && show.capacity > 0) {
    this.selectedShowId = showId;
    this.showBookingForm = true;

    console.log('Making API request to book tickets...');
    console.log('Number of Tickets:', this.numberOfTickets);

    axios
      .post(
        `http://localhost:5000/bookshows/${showId}/book`,
        { number_of_tickets: this.numberOfTickets, rating: this.rating },
        { headers }
      )
      .then((response) => {
        this.bookingStatus = true;
        this.bookedShowName = show.name;

        // After successfully booking tickets and submitting the rating,
        // fetch the updated show information, including the updated rating
        axios
          .get(`http://localhost:5000/shows`, { headers }) // Fetch all shows again
          .then((showsResponse) => {
            console.log('Response:', showsResponse);
            this.shows = showsResponse.data;
          })
          .catch((error) => {
            console.error('Error fetching updated show information:', error);
          });
      })
      .catch((error) => {
        console.error('Error booking tickets:', error);
      });
  } else {
    // Handle the case when show capacity is 0
  }
},

cancelBooking() {
    this.showBookingForm = false;
    this.bookingStatus = false; 
  },
  },
  
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
.profile-button {
  position: absolute;
  top: 10px;
  right: 80px;
  padding: 5px 10px;
  background-color: green ;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
.show-card-container {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: flex-start; 
}

.show-card {
  flex: 0 0 calc(33.33% - 20px); 
  border: 1px solid #ccc;
  border-radius: 5px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 10px; 
}


/* Add any other styles you need for your layout */
/* ... */
</style>





