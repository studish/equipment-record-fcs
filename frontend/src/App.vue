<template>
  <TopBar @search-term-changed="updateSearchTerm"></TopBar>
  <MainPage v-if="$store.state.page === 'main'" :searchTerm="searchTerm" />
  <LoginPage v-else-if="$store.state.page === 'login'" />
  <InquiriesPage
    v-else-if="
      $store.state.page === 'inquiries' && $store.state.user.authorized
    "
  />
  <NotFoundPage v-else />
</template>

<script lang="ts">
import { Options, Vue } from "vue-class-component";
import LoginPage from "./pages/LoginPage.vue";
import TopBar from "./components/TopBar.vue";
import MainPage from "./pages/MainPage.vue";
import InquiriesPage from "./pages/InquiriesPage.vue";
import NotFoundPage from "./pages/NotFoundPage.vue";

@Options({
  name: "App",
  components: {
    LoginPage,
    MainPage,
    TopBar,
    InquiriesPage,
    NotFoundPage,
  },
})
export default class App extends Vue {
  mounted(): void {
    this.$store.dispatch("user/checkAuth");
  }

  searchTerm = "";

  updateSearchTerm(term: string): void {
    this.searchTerm = term;
  }
}
</script>

<style lang="scss">
* {
  box-sizing: border-box;
}

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

  padding: 2em;

  max-height: calc(100vh - 3rem);
  overflow-y: auto;
  margin-top: 3rem;
}

input {
  border: 1px solid grey;

  &:focus {
    -webkit-box-shadow: 0px 0px 7px 0px rgba(50, 50, 255, 0.75);
    -moz-box-shadow: 0px 0px 7px 0px rgba(50, 50, 255, 0.75);
    box-shadow: 0px 0px 7px 0px rgba(50, 50, 255, 0.75);
  }
}

button {
  border: 0px;
  margin: 3px;
  padding: 0.5em 1em;
  -webkit-box-shadow: 0px 0px 2px 0px rgba(50, 50, 50, 0.75);
  -moz-box-shadow: 0px 0px 2px 0px rgba(50, 50, 50, 0.75);
  box-shadow: 0px 0px 2px 0px rgba(50, 50, 50, 0.75);

  transition: all 0.1s ease;
  cursor: pointer;

  &:hover {
    background: white;

    -webkit-box-shadow: 0px 0px 7px 0px rgba(50, 50, 50, 0.75);
    -moz-box-shadow: 0px 0px 7px 0px rgba(50, 50, 50, 0.75);
    box-shadow: 0px 0px 7px 0px rgba(50, 50, 50, 0.75);
  }
}

.modal {
  z-index: 10;
}
</style>
