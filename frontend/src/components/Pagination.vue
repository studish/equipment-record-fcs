<template>
  <div class="pagination">
    <span v-if="offset" @click="emit(Math.max(offset - pagesize, 0))"
      >Назад</span
    >
    <span
      class="item"
      :class="offset / pagesize + 1 === page ? ['current'] : []"
      v-for="page in pages"
      :key="page"
      @click="emit((page - 1) * pagesize)"
      v-text="page"
    ></span>
    <span
      v-if="offset < count - pagesize"
      @click="
        emit(
          Math.min(
            offset + pagesize,
            Math.max(0, Math.floor(count / pagesize - 1) * pagesize)
          )
        )
      "
      v-text="'Вперёд'"
    ></span>
  </div>
</template>

<script lang="ts">
import { Options, Vue } from "vue-class-component";

@Options({
  name: "Pagination",
  props: {
    count: Number,
    pagesize: Number,
    offset: Number,
  },
})
export default class Pagination extends Vue {
  count!: number;
  pagesize!: number;

  get pages(): number[] {
    let cnt = 1;
    let pages = [] as number[];
    for (let i = 0; i < this.count; i += this.pagesize) {
      pages.push(cnt++);
    }
    return pages;
  }

  emit(offset: number): void {
    this.$emit("offset", offset);
    window.scrollTo(0, 0);
  }
}
</script>

<style scoped lang="scss">
.pagination {
  display: flex;
  flex-direction: row;
  justify-content: center;

  margin-top: 0;
  margin-bottom: 1em;

  span {
    margin-left: 0.2em;
    margin-right: 0.2em;

    color: darkblue;
    text-decoration: underline;
    cursor: pointer;

    &.current {
      color: black;
      font-weight: bold;
      text-decoration: inherit;
      cursor: unset;
    }
  }
}
</style>
