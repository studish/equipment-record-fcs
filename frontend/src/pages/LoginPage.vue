<template>
  <div class="loginPage page">
    <div class="loginForm">
      <h1>Вход</h1>
      <input
        type="text"
        v-model="login"
        name="login"
        placeholder="Логин"
        @keyup.enter="sendLogin"
      />
      <input
        type="password"
        v-model="password"
        name="password"
        placeholder="Пароль"
        @keyup.enter="sendLogin"
      />
      <button @click="sendLogin">Войти</button>
      <transition name="slide">
        <span class="error" v-if="error">{{ errorMessage }}</span>
      </transition>
    </div>
  </div>
</template>

<script lang="ts">
import { Options, Vue } from "vue-class-component";
import { RequestResponse } from "@/typings/interfaces";

@Options({
  name: "LoginPage",
})
export default class LoginPage extends Vue {
  login = "";
  password = "";
  error = false;
  errorMessage = ""; // TODO

  async sendLogin(): Promise<void> {
    if (this.login.trim().length === 0 || this.password.trim().length === 0) {
      this.error = true;
      this.errorMessage = "Введите логин и пароль";
      return;
    }

    const result: RequestResponse<any> = await this.$store.dispatch(
      "user/authorize",
      {
        username: this.login,
        password: this.password,
      }
    );
    if (!result.success) {
      this.error = true;
      this.errorMessage = result.errorMessage;
    }

    await this.$store.dispatch("switchToPage", "main");
  }
}
</script>

<style scoped lang="scss">
h1 {
  padding-top: 0;
  padding-bottom: 0;
  margin: 0;
}

.loginPage {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;

  .loginForm {
    text-align: center;
    border: 1px lightgrey solid;
    border-radius: 5px;
    padding: 2em 3em;
    display: flex;
    flex-direction: column;
    align-items: stretch;
    justify-items: flex-start;
    transition: all 0.5s ease;

    & > * {
      margin-top: 1rem;
      padding: 0.5rem 1rem;
      border-radius: 5px;
    }

    .error {
      color: darkred;
    }
  }
}

.slide-enter-active {
  animation: slide-in 0.5s;
}
.slide-leave-active {
  animation: slide-in 0.5s reverse;
}

@keyframes slide-in {
  0% {
    transform: translateX(10px);
    opacity: 0;
  }

  100% {
    transform: translateX(0);
    opacity: 1;
  }
}
</style>
