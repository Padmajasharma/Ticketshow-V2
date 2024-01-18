<template>
  <div>
    <button @click="logout" class="btn btn-primary logout-button">Logout</button>
    <h2>Admin Dashboard</h2>
    <div v-if="message">{{ message }}</div>
    <router-link to="/theatres">Manage Theatres</router-link>
    <router-link to="/shows">Manage Shows</router-link>

    <!-- Display the popularity graph here -->
    <div v-if="imgUrl">
      <img :src="imgUrl" alt="Popularity Graph" />
    </div>
  </div>
</template>

<script>
import jwtDecode from "jwt-decode";
import axios from "axios";

export default {
  data() {
    return {
      message: "",
      imgUrl: "", // Store the URL of the popularity graph image
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
    this.fetchImage();

    // Fetch the popularity graph image from your Flask route
  },
  methods: {
    logout() {
      localStorage.removeItem("access_token");
      this.$router.push("/");
    },
    fetchImage() {
      // Axios GET request to fetch the image
      axios.get("http://127.0.0.1:5000/popularity_graph_image")
        .then((response) => {
          console.log(response.data);
          this.imgUrl = response.data;
        })
        .catch((error) => {
          console.error("Error fetching image:", error);
        });
    }
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
body {
  background-image: url("/src/assets/background.jpg");
  background-size: cover;
  background-position: center;
}

</style>
