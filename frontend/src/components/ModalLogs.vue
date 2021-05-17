<template>
  <div class="modal-backdrop">
    <div class="modal">
      <div class="header">
        <b class="displayName">{{ itemname }}</b>
        <button @click="close" title="Закрыть">X</button>
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
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { Options, Vue } from "vue-class-component";
import {
  RequestResponse,
  IInventoryItem,
  itemCategory,
  IFile,
  ILog,
} from "../typings/interfaces";

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

  logs: ILog[] = [];

  async mounted(): Promise<void> {
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
