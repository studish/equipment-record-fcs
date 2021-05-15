import { createStore } from "vuex";
import { IUserState, RequestResponse } from "@/typings/interfaces";

type Page = "main" | "login";

export default createStore({
  state: {
    page: "main" as Page,
  },
  mutations: {
    SET_PAGE(state, page: Page) {
      state.page = page;
    },
  },
  actions: {
    switchToPage(store, payload: Page) {
      store.commit("SET_PAGE", payload);
    },
  },
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
          const jsonResponse: RequestResponse<IUserState> =
            await response.json();
          if (jsonResponse.success)
            store.commit("SET_USERSTATE", jsonResponse.data);
        },
        async authorize(
          store,
          payload: { username: string; password: string }
        ): Promise<RequestResponse<IUserState>> {
          const response = await fetch("/api/login", {
            method: "POST",
            credentials: "same-origin",
            body: JSON.stringify(payload),
            headers: {
              "Content-Type": "application/json",
            },
          });
          const jsonResponse: RequestResponse<IUserState> =
            await response.json();

          if (jsonResponse.success) {
            store.commit("SET_USERSTATE", jsonResponse.data);
          }

          return jsonResponse;
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
