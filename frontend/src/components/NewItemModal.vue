<template>
  <div class="modal-backdrop">
    <div class="modal">
      <div class="header"></div>
      <div class="body">
        <p>Название: <input type="text" v-model="item.displayName" /></p>
        <p>
          Инв. номер:
          <input type="text" v-model="item.invid" />
        </p>
        <p>
          Категория:
          <select v-model="item.category">
            <option v-for="option in categories" :value="option" :key="option">
              {{ option }}
            </option>
          </select>
        </p>
        <p>
          Серийный номер:
          <input type="text" v-model="item.serial_num" />
        </p>
        <p>
          Цена (руб):
          <input type="text" v-model="item.price" />
        </p>
        <p>
          Доступно:
          <input type="checkbox" v-model="item.available" />
        </p>
        <b>Описание: </b>
        <textarea class="description" v-text="item.description"></textarea>
      </div>
      <div class="footer">
        <button @click="$emit('close')">Отмена</button>
        <button @click="save">Сохранить</button>
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
} from "../typings/interfaces";
import ModalLogs from "./ModalLogs.vue";
import ModalInquiry from "./ModalInquiry.vue";

@Options({
  name: "ModalItemCard",
  components: {
    ModalLogs,
    ModalInquiry,
  },
  emits: ["close", "success"],
})
export default class ModalItemCard extends Vue {
  categories = Object.keys(itemCategory).filter(
    (k) => typeof itemCategory[k as any] === "number"
  );

  item: IInventoryItem = {
    invid: "",
    category: itemCategory.НОУТБУК,
    displayName: "",
    description: "",
    serial_num: "",
    price: 0,
    available: true,
  };

  close(): void {
    this.$emit("close");
  }

  async save(): Promise<void> {
    const response = await fetch("/api/item", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(this.item),
    });
    const json: RequestResponse<IInventoryItem> = await response.json();
    if (json.success) {
      alert("Успешно добавлено!");
      this.$emit("success");
      this.$emit("close");
    } else {
      alert("Ошибка: " + json.errorMessage);
    }
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

  .displayName {
    font-size: x-large;
  }
}

.header {
  display: flex;
  flex-direction: row;
  justify-content: flex-end;
}

.body {
  padding: 10px;

  .description {
    white-space: pre-wrap;
  }
}
</style>
