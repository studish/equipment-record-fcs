<template>
  <div>
    <div class="itemCard" @click="showModal = true">
      <div class="topRow">
        <span>#{{ item.invid }}</span>
        <span>кат.: {{ category(item.category) }}</span>
      </div>
      <div class="midRow">
        <b>{{ item.displayName }}</b>
      </div>
      <div class="bottomRow">
        <span v-if="item.available">В наличии</span>
        <span v-else>Недоступен</span>
      </div>
    </div>
    <ModalItemCard
      v-if="showModal"
      :item="item"
      @close="showModal = false"
      @itemChanged="handleItemChanged"
    ></ModalItemCard>
  </div>
</template>

<script lang="ts">
import { Options, Vue } from "vue-class-component";
import { IInventoryItem } from "../typings/interfaces";
import ModalItemCard from "./ModalItemCard.vue";

@Options({
  name: "ItemCard",
  props: {
    item: {
      type: Object as () => IInventoryItem,
    },
  },
  components: {
    ModalItemCard,
  },
  emits: ["update:item"],
})
export default class ItemCard extends Vue {
  showModal = false;

  category(cat: string): string {
    return cat[0] + cat.toLowerCase().slice(1, cat.length);
  }

  handleItemChanged(event: IInventoryItem): void {
    this.$emit("update:item", event);
  }
}
</script>

<style scoped lang="scss">
.itemCard {
  display: flex;
  flex-direction: column;
  align-items: stretch;
  justify-content: flex-start;

  margin-bottom: 1em;
  border: 1px solid lightgrey;
  padding: 7px 5px;

  background-color: white;
  -webkit-box-shadow: 0px 0px 5px 0px rgba(50, 50, 50, 0.75);
  -moz-box-shadow: 0px 0px 5px 0px rgba(50, 50, 50, 0.75);
  box-shadow: 0px 0px 5px 0px rgba(50, 50, 50, 0.75);

  cursor: pointer;

  transition: all ease 0.2s;
  &:hover {
    transform: translateX(5px);
    -webkit-box-shadow: -5px 0px 8px 0px rgba(50, 50, 50, 0.75);
    -moz-box-shadow: -5px 0px 8px 0px rgba(50, 50, 50, 0.75);
    box-shadow: -5px 0px 8px 0px rgba(50, 50, 50, 0.75);
  }

  & > * {
    margin-bottom: 5px;

    &:last-child {
      margin-bottom: 0;
    }
  }

  .topRow {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
  }
}
</style>
