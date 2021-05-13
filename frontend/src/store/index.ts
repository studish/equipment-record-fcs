import { createStore } from "vuex";
import { IUserState } from "../typings/interfaces";

export default createStore({
  state: {},
  mutations: {},
  actions: {},
  modules: {
    user: {
      namespaced: true,
      state: {
        authorized: false,
        username: null as string | null,
        adminRole: false,
      },
      mutations: {
        SET_USERSTATE(state, { authorized, username, adminRole }: IUserState) {
          console.log(
            "Setting userstate: " +
              JSON.stringify({ authorized, username, adminRole })
          );
          state.authorized = authorized;
          state.username = username;
          state.adminRole = adminRole;
        },
      },
      actions: {
        async checkAuth(store) {
          const response = await fetch("/api/checkAuth", {
            credentials: "same-origin",
          });
          const jsonResponse: IUserState = await response.json();
          store.commit("SET_USERSTATE", jsonResponse);
        },
        async authorize(
          store,
          payload: { username: string; password: string }
        ) {
          const response = await fetch("/api/login", {
            method: "POST",
            credentials: "same-origin",
            body: JSON.stringify(payload),
            headers: {
              "Content-Type": "application/json",
            },
          });
          const jsonResponse: IUserState = await response.json();
          store.commit("SET_USERSTATE", jsonResponse);
        },
        async logout(store) {
          await fetch("/api/logout", {
            method: "POST",
            credentials: "same-origin",
          });
          await store.dispatch("checkAuth");
        },
      },
    },
  },
});
