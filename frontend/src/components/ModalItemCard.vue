<template>
  <div class="modal-backdrop">
    <div class="modal">
      <div class="header">
        <button @click="close" title="Закрыть">X</button>
      </div>
      <div class="body">
        <b class="displayName">{{ item.displayName }}</b>
        <p>
          Инв. номер:
          <input disabled type="text" v-model="item.invid" />
        </p>
        <p>
          Категория: <i>{{ category(item.category) }}</i>
        </p>
        <p>
          Серийный номер:
          <input disabled type="text" v-model="item.serial_num" />
        </p>
        <p>Цена (руб): <input type="text" disabled v-model="item.price" /></p>
        <b>Описание</b>
        <div class="description" v-text="item.description"></div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { Options, Vue } from "vue-class-component";
import { IInventoryItem } from "../typings/interfaces";

@Options({
  name: "ModalItemCard",
  props: {
    item: {
      type: Object as () => IInventoryItem,
    },
  },
})
export default class ModalItemCard extends Vue {
  category(cat: string): string {
    return cat[0] + cat.toLowerCase().slice(1, cat.length);
  }

  item!: IInventoryItem;

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
