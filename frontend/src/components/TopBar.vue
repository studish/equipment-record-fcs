<template>
  <div class="topBar">
    <a href="#" @click="$store.dispatch('switchToPage', 'main')">
      <h1>Учёт техники ФКН</h1>
    </a>
    <input
      type="search"
      v-model="searchTerm"
      v-if="$store.state.page === 'main'"
      placeholder="Поиск..."
    />
    <div class="buttonsContainer">
      <span v-if="$store.state.user.authorized" class="username">{{
        $store.state.user.username
      }}</span>
      <button
        v-if="$store.state.user.adminRole && $store.state.page !== 'inquiries'"
        @click="$store.dispatch('switchToPage', 'inquiries')"
      >
        Заявки
      </button>
      <button
        v-if="$store.state.page !== 'main'"
        @click="$store.dispatch('switchToPage', 'main')"
      >
        Инвентарь
      </button>
      <button
        @click="$store.dispatch('user/logout')"
        v-if="$store.state.user.authorized"
      >
        Выход
      </button>
      <button
        v-else-if="$store.state.page !== 'login'"
        @click="$store.dispatch('switchToPage', 'login')"
      >
        Вход
      </button>
    </div>
  </div>
</template>

<script lang="ts">
import { Options, Vue } from "vue-class-component";

@Options({
  name: "TopBar",
  emits: ["searchTermChanged"],
  watch: {
    searchTerm() {
      this.$emit("searchTermChanged", this.searchTerm);
    },
  },
})
export default class HelloWorld extends Vue {
  searchTerm = "";
}
</script>

<style scoped lang="scss">
.buttonsContainer {
  display: flex;
  flex-direction: row;
  justify-items: flex-end;
  align-items: stretch;
}

.username {
  align-self: center;
  color: white;
  margin-right: 2em;
}

.topBar {
  position: fixed;
  width: 100vw;
  box-sizing: border-box;

  a {
    h1 {
      color: white;
      margin: 0;
      align-self: center;
    }
    text-decoration: none;
  }

  height: 3rem;
  background-color: #0b2b68;
  padding: 5px 10px;

  display: flex;
  flex-direction: row;
  align-items: stretch;
  justify-content: space-between;

  -webkit-box-shadow: 0px 0px 5px 0px rgba(50, 50, 50, 0.75);
  -moz-box-shadow: 0px 0px 5px 0px rgba(50, 50, 50, 0.75);
  box-shadow: 0px 0px 5px 0px rgba(50, 50, 50, 0.75);

  input {
    padding: 1em 1em;
    background-color: lightgrey;
    transition: all 0.3s ease;
    border-radius: 100px;

    &:focus {
      background-color: white;
    }
  }
}
</style>
