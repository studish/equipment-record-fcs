<template>
  <div>
    <div class="itemCard">
      <div class="topRow">
        <span>#{{ inquiry.id }}</span>
        <button @click="description = !description">
          {{ description ? "Скрыть" : "Показать" }} комментарий
        </button>
      </div>
      <div class="midRow">
        <a :href="'mailto:' + inquiry.inquirerEmail">{{
          inquiry.inquirerName
        }}</a>
        <pre v-if="description" v-text="inquiry.comment"></pre>
      </div>
      <div class="bottomRow">
        <a :href="`/api/generateFiles?inqid=${inquiry.id}`" target="_blank"
          >Накладная</a
        >
        <div v-if="$store.state.user.adminRole">
          <button
            v-for="state in states"
            :key="'state' + state.status"
            @click="setState(state.status)"
          >
            {{ state.text }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { Options, Vue } from "vue-class-component";
import { IInquiry, inquiryStatus } from "../typings/interfaces";

@Options({
  name: "ItemCard",
  props: {
    inquiry: {
      type: Object as () => IInquiry,
    },
    states: {
      type: Array as () => Array<{ text: string; status: inquiryStatus }>,
    },
  },
  emits: ["update"],
})
export default class ItemCard extends Vue {
  inquiry!: IInquiry;
  description = false;

  async setState(status: inquiryStatus): Promise<void> {
    const response = await fetch("/api/inquiry", {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        status: inquiryStatus[status],
        itemId: this.inquiry.id,
      }),
    });
    const json = await response.json();
    if (!json.success) {
      alert("Ошибка: " + json.errorMessage);
    } else {
      this.$emit("update");
    }
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

  transition: all ease 0.2s;

  & > * {
    margin-bottom: 5px;

    &:last-child {
      margin-bottom: 0;
    }
  }

  .topRow,
  .bottomRow {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    align-items: flex-end;
  }
}
</style>
