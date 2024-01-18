<template>
  <div>
    <h1>TicketShow</h1>
    <router-view></router-view>
  </div>
</template>

<script>
import TheatreList from './components/TheatreList.vue';
import ShowList from './components/ShowList.vue';

export default {
  // Add any necessary component logic here
  components: {
    TheatreList,
    ShowList,
  },
};
</script>
