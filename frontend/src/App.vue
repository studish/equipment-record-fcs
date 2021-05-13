<template>
  <TopBar></TopBar>
  <MainPage v-if="$store.state.user.authorized" />
  <LoginPage v-else />
</template>

<script lang="ts">
import { Options, Vue } from "vue-class-component";
import LoginPage from "./pages/LoginPage.vue";
import TopBar from "./components/TopBar.vue";
import MainPage from "./pages/MainPage.vue";

@Options({
  components: {
    LoginPage,
    MainPage,
    TopBar,
  },
})
export default class App extends Vue {
  mounted() {
    this.$store.dispatch("user/checkAuth");
  }
}
</script>

<style lang="scss">
html,
body {
  margin: 0;
  padding: 0;
  min-width: 100vw;
  min-height: 100vh;
}

#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  /* text-align: center; */
  color: #2c3e50;
  /* margin-top: 60px; */

  display: flex;
  flex-direction: column;
  align-items: stretch;
  justify-content: flex-start;

  min-width: 100vw;
  min-height: 100vh;
}

.page {
  flex-grow: 1;
}

input {
  border: 1px solid grey;

  &:focus {
    -webkit-box-shadow: 0px 0px 7px 0px rgba(50, 50, 255, 0.75);
    -moz-box-shadow: 0px 0px 7px 0px rgba(50, 50, 255, 0.75);
    box-shadow: 0px 0px 7px 0px rgba(50, 50, 255, 0.75);
  }
}
</style>
