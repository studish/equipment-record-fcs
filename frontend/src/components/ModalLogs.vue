<template>
  <div class="modal-backdrop">
    <div class="modal">
      <div class="header">
        <b class="displayName">{{ itemname }}</b>
        <div>
          <button @click="setShowCreateLog(true)">Добавить лог</button>
          <button @click="close" title="Закрыть">X</button>
        </div>
      </div>
      <div class="body">
        <div v-for="log in logs" :key="'log' + log.id">
          <span class="timestamp" v-text="log.timestamp"></span>
          {{ log.description }}
          <div v-if="log.files" class="files">
            <a
              v-for="file in log.files"
              :key="'file' + file.id"
              :href="`/api/download?id=${file.id}`"
              target="_blank"
              >{{ file.fileName }}</a
            >
          </div>
        </div>
        <div v-show="showCreateLog" class="createLog">
          <label for="newLogText">
            <b>Новый лог:</b>
          </label>
          <form
            ref="newLogForm"
            id="newLogForm"
            method="post"
            enctype="multipart/form-data"
          >
            <input type="text" name="description" v-model="newLogText" />
            <input type="file" name="files" multiple />
          </form>
          <button @click="createLog">Создать</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { Options, Vue } from "vue-class-component";
import { RequestResponse, ILog } from "../typings/interfaces";

@Options({
  name: "ModalLogs",
  props: {
    itemid: Number,
    itemname: String,
    invid: String,
  },
  emits: ["close"],
})
export default class ModalLogs extends Vue {
  itemid!: number;
  invid!: string;
  itemname!: string;

  showCreateLog = false;
  newLogText = "";

  logs: ILog[] = [];

  async loadData(): Promise<void> {
    const response = await fetch(
      "/api/logs?" +
        new URLSearchParams({
          itemid: this.itemid.toString(),
        }).toString()
    );
    const json: RequestResponse<ILog[]> = await response.json();
    if (json.success) {
      this.logs = json.data;
    } else {
      alert(json.errorMessage);
    }
  }

  async mounted(): Promise<void> {
    await this.loadData();
  }

  setShowCreateLog(value: boolean): void {
    this.showCreateLog = value;
  }

  just(str: { toString: () => string }, length: number, char: string): string {
    let result = str.toString();
    return char.repeat(length - result.length) + result;
  }

  async createLog(): Promise<void> {
    console.log(this.$refs);
    const data = new FormData(this.$refs.newLogForm as HTMLFormElement);
    data.append("itemId", this.itemid.toString());
    const date = new Date();
    const j = (x: { toString: () => string }) => this.just(x, 2, "0");
    let timestamp =
      `${date.getFullYear()}-${j(date.getMonth())}-${j(date.getDay())}` +
      ` ${j(date.getHours())}-${j(date.getMinutes())}-${j(date.getSeconds())}`;
    data.append("timestamp", timestamp);

    const response = await fetch("/api/log", {
      method: "POST",
      headers: {
        // "Content-Type": undefined,
      },
      body: data,
    });
    const json: RequestResponse<ILog> = await response.json();
    if (json.success) {
      this.loadData();
    }
  }

  close(): void {
    this.$emit("close");
  }
}
</script>

<style scoped lang="scss">
input {
  padding: 5px;
  cursor: text;
}

.modal-backdrop {
  position: fixed;
  top: 0;
  bottom: 0;
  left: 0;
  right: 0;
  background-color: rgba(0, 0, 0, 0.3);
  display: flex;
  justify-content: center;
  align-items: center;

  padding: 10px;
}

.modal {
  background: #ffffff;
  box-shadow: 2px 2px 20px 1px;
  overflow-x: auto;
  display: flex;
  flex-direction: column;
  align-items: stretch;

  min-width: 60%;
}

.header {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  padding-left: 1em;

  .displayName {
    align-self: flex-end;
    font-size: x-large;
  }
}

.body {
  padding: 10px;

  .timestamp {
    color: grey;
    font-style: italic;

    &::before {
      content: "[";
    }

    &::after {
      content: "] --- ";
    }
  }
}

.files {
  a {
    margin-right: 0.5em;
  }
}
</style>
