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
          {{ sheetLabel }} Data
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
        </label>
      </div>
      <div v-if="sheetNames.length">
      <h3 class="text-lg font-bold">Sheet Names</h3>
      <ul>
        <li v-for="(sheet, index) in sheetNames" :key="index">
          <div class="form-control">
            <label class="cursor-pointer label">
              <span class="label-text">{{ sheet }}</span>
              <input
                type="radio"
                v-model="selectedSheet"
                :value="sheet"
                class="radio radio-primary"
              />
            </label>
          </div>
        </li>
      </ul>
    </div>
  </div>
</template>
  
  <script>
  import axios from "axios";
  
  export default {
    name: "SheetComponent",
    components: {
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
    handleSelectedSheets(sheet) {
      this.selectedSheet = sheet;
      this.$emit("update:selectedSheets", this.selectedSheet);
    },
  };
  </script>
  
  <style scoped>
  /* Your styles here */
  </style>