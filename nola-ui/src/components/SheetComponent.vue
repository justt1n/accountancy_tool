<template>
  <div class="sheet">
    <div>
      <label
        :for="sheetId"
        class="input input-bordered flex items-center gap-2"
      >
        {{ sheetLabel }}:
        <input
          v-model="localSheet"
          :id="sheetId"
          type="text"
          @input="onSheetInput"
          class="grow"
        />
        <span class="badge badge-info">{{ badgeText }}</span>
      </label>
    </div>
    <div class="form-control">
      <h2 class="text-xl font-bold dark:text-white p-2">
      </h2>
      <label
        v-for="(item, index) in sheetData"
        :key="index"
        class="cursor-pointer label w-48"
      >
        <span class="label-text" :for="sheetId + index">{{ item }}</span>
        <input
          type="checkbox"
          :id="sheetId + index"
          v-model="localSelectedData"
          :value="item"
          class="checkbox checkbox-success"
        />
        <div v-if="selectedHeaders.length">
          <h3 class="text-lg font-bold">Selected Headers</h3>
          <ul>
            <li v-for="(header, index) in selectedHeaders" :key="index">
              {{ header }}
            </li>
          </ul>
        </div>
      </label>
    </div>
    <div v-if="sheetNames.length">
      <ul>
        <li v-for="(sheet, index) in sheetNames" :key="index">
          <DropdownComponent
            :sheetName="sheet"
            :spreadsheetId="srcSpreadsheetId"
            @update:selectedSheets="handleSelectedSheets"
          />
        </li>
      </ul>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import DropdownComponent from "./DropdownComponent.vue";

export default {
  name: "SheetComponent",
  components: {
    DropdownComponent,
  },
  props: {
    sheetId: String,
    sheetLabel: String,
    sheetData: Array,
    badgeText: String,
  },
  data() {
    return {
      localSheet: "",
      localSelectedData: [],
      sheetNames: [],
      srcSpreadsheetId: "",
      selectedSheet: [],
      selectedHeaders: [],
    };
  },
  watch: {
    localSheet(newValue) {
      this.$emit('update:sheet', newValue);
    },
    localSelectedData(newValue) {
      this.$emit('update:selectedData', newValue);
    }
  },
  methods: {
    async onSheetInput(event) {
      console.log("Source Sheet input:", event.target.value);
      this.srcSpreadsheetId = event.target.value.split("/")[5]; // Store the ID
      try {
        const response = await axios.post("http://127.0.0.1:8000/api/v2/test", {
          src_sheet_url: this.srcSpreadsheetId,
        });
        console.log("Response:", response.data);
        this.sheetNames = response.data.data;
        console.log("Sheet names:", this.sheetNames);
      } catch (error) {
        console.error("Error:", error);
      }
    },
  },
};
</script>

<style scoped>
/* Your styles here */
</style>