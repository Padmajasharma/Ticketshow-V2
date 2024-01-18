import Vue from 'vue';
import App from './App.vue';
import VueRouter from 'vue-router';
import Home from './components/Home.vue';
import SignupForm from './components/SignupForm.vue';
import LoginForm from './components/LoginForm.vue';
import UserDashboard from './components/UserDashboard.vue';
import AdminDashboard from './components/AdminDashboard.vue';
import TheatreList from './components/TheatreList.vue';
import ShowList from './components/ShowList.vue';
import UserProfile from './components/UserProfile.vue';


Vue.use(VueRouter);

const routes = [
  { path: '/', component: Home },
  { path: '/signup', component: SignupForm },
  { path: '/login', component: LoginForm },
  { path: '/Userdashboard', component: UserDashboard },
  { path: '/Admindashboard', component: AdminDashboard },
  { path: '/theatres', component: TheatreList },
  { path: '/shows', component: ShowList },
  { path: '/userprofile',component: UserProfile}
];

const router = new VueRouter({
  routes
});

new Vue({
  router,
  render: h => h(App)
}).$mount('#app');
