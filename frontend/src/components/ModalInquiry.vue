<template>
  <div class="modal-backdrop">
    <div class="modal">
      <div class="header">
        <b class="displayName">{{ itemname }}</b>
        <button @click="close" title="Закрыть">X</button>
      </div>
      <div class="body">
        <table>
          <tr>
            <td><label for="name">ФИО: </label></td>
            <td>
              <input type="text" name="name" v-model="inquiry.inquirerName" />
            </td>
          </tr>
          <tr>
            <td><label for="email">E-mail: </label></td>
            <td>
              <input
                type="email"
                name="email"
                v-model="inquiry.inquirerEmail"
              />
            </td>
          </tr>
          <tr>
            <td><label for="comment">Комментарий: </label></td>
            <td><textarea name="comment" v-model="inquiry.comment" /></td>
          </tr>
        </table>
        <button @click="send">Отправить</button>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { Options, Vue } from "vue-class-component";
import {
  inquiryStatus,
  IInquiry,
  RequestResponse,
} from "../typings/interfaces";

@Options({
  name: "ModalInquiry",
  props: {
    itemid: Number,
    itemname: String,
    invid: String,
  },
  emits: ["close"],
})
export default class ModalInquiry extends Vue {
  itemid!: number;
  invid!: string;
  itemname!: string;

  inquiry: IInquiry = {
    inquirerName: "",
    inquirerEmail: "",
    comment: "",
    status: inquiryStatus.new,
    itemId: this.itemid,
  };

  close(): void {
    this.$emit("close");
  }

  async send(): Promise<void> {
    const data = JSON.parse(JSON.stringify(this.inquiry));
    data.status = inquiryStatus[data.status];
    const response = await fetch("/api/inquiry", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    });
    const json: RequestResponse<IInquiry> = await response.json();
    if (json.success) {
      alert("Заявка успешно подана, ожидайте письма на указанный адрес");
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
