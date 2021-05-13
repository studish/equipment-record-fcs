<template>
  <div class="topBar">
    <h1>Заголовок</h1>
    <input
      type="search"
      v-if="$store.state.user.authorized"
      v-model="searchTerm"
      placeholder="Поиск..."
    />
    <button
      @click="$store.dispatch('user/logout')"
      v-if="$store.state.user.authorized"
    >
      Выход
    </button>
  </div>
</template>

<script lang="ts">
import store from "@/store";
import { Options, Vue } from "vue-class-component";

@Options({
  mounted() {
    console.log(store);
  },
})
export default class HelloWorld extends Vue {
  searchTerm = "";
}
</script>

<style scoped lang="scss">
.topBar {
  h1 {
    color: white;
    margin: 0;
    align-self: center;
  }

  height: 2.5rem;
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

    &:focus {
      background-color: white;
    }
  }
}
</style>
