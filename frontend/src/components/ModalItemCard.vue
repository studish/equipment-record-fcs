<template>
  <div class="modal-backdrop">
    <div class="modal-close-area" @click="$emit('close')"></div>
    <div class="modal">
      <div class="header">
        <ModalLogs
          v-if="showLogs"
          @close="showLogs = false"
          :itemid="item.id"
          :invid="item.invid"
          :itemname="item.displayName"
        ></ModalLogs>
        <ModalInquiry
          v-if="showInquiry"
          @close="showInquiry = false"
          :itemid="item.id"
          :invid="item.invid"
          :itemname="item.displayName"
        ></ModalInquiry>
        <button @click="showLogs = true" v-if="$store.state.user.authorized">
          Логи
        </button>
        <button @click="showInquiry = true">Подать заявку</button>
        <button @click="close" title="Закрыть">X</button>
      </div>
      <div class="body">
        <table>
          <tr>
            <td>Название:</td>
            <td>
              <b v-if="!editing" class="displayName">
                {{ editableItem.displayName }}
              </b>
              <input v-else type="text" v-model="editableItem.displayName" />
            </td>
          </tr>
          <tr>
            <td>Инв. номер:</td>
            <td>
              <input
                :disabled="!editing"
                type="text"
                v-model="editableItem.invid"
              />
            </td>
          </tr>
          <tr>
            <td>Категория:</td>
            <td>
              <select :disabled="!editing" v-model="editableItem.category">
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
            <td>Серийный номер:</td>
            <td>
              <input
                :disabled="!editing"
                type="text"
                v-model="editableItem.serial_num"
              />
            </td>
          </tr>
          <tr>
            <td>Цена (руб):</td>
            <td>
              <input
                type="text"
                :disabled="!editing"
                v-model="editableItem.price"
              />
            </td>
          </tr>
          <tr>
            <td>Доступно:</td>
            <td>
              <input
                type="checkbox"
                v-model="editableItem.available"
                :disabled="!editing"
              />
            </td>
          </tr>
          <tr>
            <td><b>Описание</b></td>
            <td>
              <textarea
                class="description"
                v-model="editableItem.description"
                :disabled="!editing"
              ></textarea>
            </td>
          </tr>
        </table>
        <div v-if="$store.state.user.adminRole">
          <button @click="toggleEdit()">
            {{ editing ? "Отмена" : "Редактировать" }}
          </button>
          <button v-if="editing" @click="save">Сохранить</button>
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
} from "../typings/interfaces";
import ModalLogs from "./ModalLogs.vue";
import ModalInquiry from "./ModalInquiry.vue";

@Options({
  name: "ModalItemCard",
  props: {
    item: {
      type: Object as () => IInventoryItem,
    },
  },
  components: {
    ModalLogs,
    ModalInquiry,
  },
  watch: {
    item() {
      this.editableItem = JSON.parse(JSON.stringify(this.item));
    },
  },
  emits: ["itemChanged", "close"],
})
export default class ModalItemCard extends Vue {
  categories = Object.keys(itemCategory).filter(
    (k) => typeof itemCategory[k as any] === "number"
  );

  category(cat: string): string {
    console.log(this);
    return cat[0] + cat.toLowerCase().slice(1, cat.length);
  }

  item!: IInventoryItem;
  editing = false;
  editableItem!: IInventoryItem;
  showLogs = false;
  showInquiry = false;

  beforeMount(): void {
    this.editableItem = JSON.parse(JSON.stringify(this.item));
  }

  close(): void {
    this.$emit("close");
  }

  toggleEdit(): void {
    if (!this.editing) {
      this.editing = true;
    } else {
      this.editableItem = JSON.parse(JSON.stringify(this.item));
      this.editing = false;
    }
  }

  async save(): Promise<void> {
    const response = await fetch("/api/item", {
      method: "PUT",
      body: JSON.stringify(this.editableItem),
      headers: {
        "Content-Type": "application/json",
      },
    });
    const json: RequestResponse<IInventoryItem> = await response.json();
    if (json.success) {
      this.$emit("itemChanged", json.data);
      this.toggleEdit();
    } else {
      alert(json.errorMessage);
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

  min-width: 40%;

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
