<template>
  <div class="modal-backdrop">
    <div class="modal-close-area" @click="$emit('close')"></div>
    <div class="modal">
      <div class="header"></div>
      <div class="body">
        <table>
          <tr>
            <td>
              <label for="name">Название:</label>
            </td>
            <td>
              <input type="text" id="name" v-model="item.displayName" />
            </td>
          </tr>
          <tr>
            <td>
              <label for="invnum">Инв. номер:</label>
            </td>
            <td>
              <input type="text" id="invnum" v-model="item.invid" />
            </td>
          </tr>
          <tr>
            <td>
              <label for="category">Категория:</label>
            </td>
            <td>
              <select v-model="item.category" id="category">
                <option
                  v-for="option in categories"
                  :value="option"
                  :key="option"
                >
                  {{ option }}
                </option>
              </select>
            </td>
          </tr>
          <tr>
            <td>
              <label for="serial">Серийный номер:</label>
            </td>
            <td>
              <input id="serial" type="text" v-model="item.serial_num" />
            </td>
          </tr>
          <tr>
            <td>
              <label for="price">Цена (руб):</label>
            </td>
            <td>
              <input id="price" type="text" v-model="item.price" />
            </td>
          </tr>
          <tr>
            <td>
              <label for="available">Доступно:</label>
            </td>
            <td>
              <input type="checkbox" id="available" v-model="item.available" />
            </td>
          </tr>
          <tr>
            <td>
              <label for="description">Описание</label>
            </td>
            <td>
              <textarea
                id="description"
                class="description"
                v-model="item.description"
                rows="10"
                cols="40"
              ></textarea>
            </td>
          </tr>
        </table>
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
  name: "NewItemModal",
  components: {
    ModalLogs,
    ModalInquiry,
  },
  emits: ["close", "success"],
})
export default class NewItemModal extends Vue {
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

  .modal-close-area {
    position: fixed;
    top: 0;
    bottom: 0;
    left: 0;
    right: 0;
  }
}

.modal {
  background: #ffffff;
  box-shadow: 2px 2px 20px 1px;
  overflow-x: auto;
  display: flex;
  flex-direction: column;
  align-items: stretch;

  min-width: 30%;

  .displayName {
    font-size: x-large;
  }

  table {
    width: 100%;
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
