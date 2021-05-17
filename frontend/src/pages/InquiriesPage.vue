<template>
  <div class="page">
    <h1>Заявки</h1>

    <div class="statusFilter">
      <span
        v-for="state in states"
        :key="state.status"
        v-text="state.text"
        :class="status === state.status ? ['active'] : []"
        @click="status = state.status"
      ></span>
    </div>

    <div class="cards">
      <!-- <Pagination
         :count="itemsCount"
         @offset="(x) => (offset = x)"
         :pagesize="20"
         :offset="offset"
         /> -->

      <InquiryCard
        v-for="inquiry in inquiries"
        :key="'inquiry' + inquiry.id"
        :inquiry="inquiry"
        :states="states"
        @update="loadInquiries"
      />

      <!-- <Pagination
         :count="itemsCount"
         @offset="(x) => (offset = x)"
         :pagesize="20"
         :offset="offset"
         /> -->
    </div>
  </div>
</template>

<script lang="ts">
import { Options, Vue } from "vue-class-component";
import {
  IInquiry,
  RequestResponse,
  inquiryStatus,
} from "../typings/interfaces";
import Pagination from "../components/Pagination.vue";
import InquiryCard from "../components/InquiryCard.vue";

@Options({
  name: "InquiriesPage",
  components: {
    Pagination,
    InquiryCard,
  },
  watch: {
    status() {
      this.loadInquiries();
    },
  },
})
export default class InquiriesPage extends Vue {
  states = [
    { status: inquiryStatus.new, text: "Новые" },
    { status: inquiryStatus.queued, text: "В обработке" },
    { status: inquiryStatus.finished, text: "Архив" },
  ];

  inquiries: IInquiry[] = [];
  status = inquiryStatus.new;
  offset = 0;
  itemsCount = 0;

  async loadInquiries(): Promise<void> {
    const response = await fetch(
      "/api/inquiries?" +
        new URLSearchParams({
          status: inquiryStatus[this.status],
          offset: this.offset.toString(),
        })
    );
    const json: RequestResponse<IInquiry[]> = await response.json();
    if (json.success) {
      this.inquiries = json.data;
    } else {
      alert("Ошибка: " + json.errorMessage);
    }
  }

  async mounted(): Promise<void> {
    await this.loadInquiries();
  }
}
</script>

<style scoped lang="scss">
.cards {
  padding: 2em;
}

.statusFilter {
  display: flex;
  flex-direction: row;
  justify-content: center;
  span {
    margin-right: 1em;
    color: blue;
    text-decoration: underline;
    cursor: pointer;

    &.active {
      font-weight: bold;
      color: black;
      text-decoration: inherit;
      cursor: inherit;
    }
  }
}
</style>
