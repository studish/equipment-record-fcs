import { createApp } from "vue";
import App from "./App.vue";
import store from "./store";

const app = createApp(App);
app.use(store).mount("#app");
// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
app.config.devtools = true;
