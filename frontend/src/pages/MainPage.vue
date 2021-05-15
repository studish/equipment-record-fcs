<template>
  <div class="page">
    <div class="sideBar">
      <!-- <h3>Фильтры</h3> -->

      <h4>Категория</h4>
      <div v-for="category in categories" :key="category">
        <input
          type="checkbox"
          :id="'chk' + category"
          v-model="filter.category[category]"
        />
        <label :for="'chk' + category">
          {{ capitalize(category.toLowerCase()) }}
        </label>
      </div>

      <button class="loadResultsButton" @click="loadResults">
        Показать результаты
      </button>
    </div>
    <div class="content">
      <Pagination
        :count="itemsCount"
        @offset="(x) => (offset = x)"
        :pagesize="20"
        :offset="offset"
      />

      <ItemCard v-for="item in items" :key="item.id" :item="item"></ItemCard>

      <Pagination
        :count="itemsCount"
        @offset="(x) => (offset = x)"
        :pagesize="20"
        :offset="offset"
      />
    </div>
  </div>
</template>

<script lang="ts">
import { Options, Vue } from "vue-class-component";
import ItemCard from "../components/ItemCard.vue";
import Pagination from "../components/Pagination.vue";
import { itemCategory, IInventoryItem } from "../typings/interfaces";

@Options({
  name: "MainPage",
  watch: {
    filter() {
      return;
    },
    offset() {
      console.log("Loading");
      this.loadResults();
    },
    searchTerm() {
      if (this.timer !== -1) {
        clearTimeout(this.timer);
      }
      this.timer = setTimeout(this.loadResults, 1000);
    },
  },
  components: { ItemCard, Pagination },
  props: {
    searchTerm: String,
  },
})
export default class MainPage extends Vue {
  categories = Object.keys(itemCategory).filter(
    (k) => typeof itemCategory[k as any] === "number"
  );

  timer = -1;
  items: IInventoryItem[] = [];
  itemsCount = 0;
  offset = 0;

  filter = {
    category: {} as Record<string, boolean>,
  };

  capitalize(str: string): string {
    return str[0].toUpperCase() + str.slice(1, str.length);
  }

  searchTerm!: string;

  async loadResults(): Promise<void> {
    try {
      const categories = Object.keys(this.filter.category).filter(
        (k) => this.filter.category[k]
      );
      const response = await fetch(
        "/api/items?" +
          new URLSearchParams({
            search: this.searchTerm as string,
            offset: this.offset.toString(),
            categories: categories.join(","),
          })
      );
      const json = await response.json();
      if (json.success) {
        this.items = json.data.items;
        this.itemsCount = json.data.count;
      }
    } catch (e) {
      console.log(e);
    }
  }

  async mounted(): Promise<void> {
    await this.loadResults();
  }
}
</script>

<style scoped lang="scss">
.page {
  display: flex;
  flex-direction: row;
  align-items: stretch;
  justify-content: flex-start;

  .sideBar {
    min-width: 10em;
    border-right: 1px solid grey;
    padding: 1em;

    h3 {
      margin: 0;
    }

    .loadResultsButton {
      margin-top: 2em;
    }
  }

  .content {
    flex-grow: 1;

    display: flex;
    flex-direction: column;
    justify-content: flex-start;
    align-items: stretch;

    padding: 2em;
  }
}
</style>
