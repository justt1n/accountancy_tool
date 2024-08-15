<template>
  <div id="app">
    <TitleComponent />
    <div class="flex">

      <div class="flex items-center space-x-4 p-2">
        <div class="flex">
          <LocalStoTextBox />
        </div>
        <ButtonComponent type="submit" variant="primary" @click="processData">
          Filter Data
        </ButtonComponent>
      </div>
    </div>
    <div class="bg-base-200 w-1/2"></div>
    <div class="flex">
      <div class="w-1/2 mockup-window bg-gray-100 border">
        <div class="w-full border">
          <label class="cursor-pointer label">
            <span class="label-text w-1/2">Number of product sheet</span>
            <input type="number" class="input w-1/2 border" v-model="srcSheetUrlNum"
              placeholder="Enter sheet URLs separated by ';'" />
          </label>
        </div>
        <div class="bg-gray-100 justify-center px-4 py-16">
          <div v-for="(url, i) in srcSheetUrlArray" :key="i">
            <SheetComponent :sheetId="'srcSheet' + i" :sheetLabel="'Product ' + i" :sheetData="srcSheetData[i]"
              :badgeText="'Source'" @update:sheet="updateSrcSheet(i)" @update:selectedData="updateSelectedSrcData(i)" />
          </div>
        </div>
      </div>
      <div class="w-1/2 mockup-window bg-gray-100 border">
        <div class="ml-3 mt-3">
          <ButtonComponent type="submit" variant="primary" @click="openTemplate">
            Open Template Payment
          </ButtonComponent>
        </div>
        <div class="bg-gray-100 justify-center px-4 py-16">
          <DesSheetComponent :sheetId="'destSheet'" :sheetLabel="'Payment'" :sheetData="destSheetData"
            @spreadsheet-selected="updateDestSheetId" @sheet-selected="updateSelectedSheet" />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import TitleComponent from "./components/TitleComponent.vue";
import SheetComponent from "./components/SheetComponent.vue";
import ButtonComponent from "./components/ButtonComponent.vue";
import DesSheetComponent from "./components/DesSheetComponent.vue";
import LocalStoTextBox from "./components/LocalStoTextBox.vue";
import axios from "axios";

export default {
  name: "App",
  components: {
    TitleComponent,
    SheetComponent,
    ButtonComponent,
    DesSheetComponent,
    LocalStoTextBox,
  },
  data() {
    return {
      srcSheetUrlNum: 1,
      srcSheet: "",
      srcSheetData: [],
      selectedSrcData: [],
      destSheet: "",
      destSheetData: [],
      selectedDestData: [],
      selectedSheet: [],
      destSheetId: "",
      selectedSheets: "",
    };
  },
  computed: {
    srcSheetUrlArray() {
      return this.srcSheetUrlNum;
    },
  },
  methods: {
    updateDestSheetId(spreadsheetId) {
      this.destSheetId = spreadsheetId;
      console.log("Destination Sheet ID:", this.destSheetId);
    },
    updateSelectedSheet(sheet) {
      this.selectedSheet = sheet;
      console.log("Selected Sheet:", this.selectedSheet);
    },
    updateSrcSheet(value) {
      this.srcSheet = value;
      console.log("Source Sheet:", this.srcSheet);
    },
    updateSelectedSrcData(value) {
      this.selectedSrcData = value;
    },
    updateDestSheet(value) {
      this.destSheet = value;
    },
    updateSelectedDestData(value) {
      this.selectedDestData = value;
    },
    async processData() {
      // Load data from localStorage
      const filterRequests =
        JSON.parse(localStorage.getItem("FilterRequests")) || [];

      // Build the request in the desired format
      const requestPayload = this.buildRequest(filterRequests);

      // Send post request
      try {
        console.log(JSON.stringify(requestPayload));
        const response = await axios.post(
          "http://localhost:8000/api/v2/filter",
          requestPayload,
          {
            headers: {
              "Content-Type": "application/json",
              Authorization: "Bearer your_token_here", // Replace with your actual token if needed
            },
          }
        );
        console.log("response:", response);
      } catch (error) {
        console.error("Error:", error);
      }
    },
    buildRequest(filterRequests) {
      const srcData = {};
      filterRequests.forEach((item, index) => {
        srcData[`${index}`] = {
          spreadsheet_id: item.spreadsheet_id,
          sheet_name: item.sheet_name,
          columns: item.columns,
        };
      });
      console.log("Selected Source Data:", srcData);
      const requestPayload = {
        src_spreadsheets: srcData,
        des_spreadsheet_id: this.destSheetId,
        des_sheet_name: this.selectedSheet,
      };
      return requestPayload;
    },
    openTemplate() {
      window.open("https://docs.google.com/spreadsheets/d/1jiV9BIOuOAlgQObuxRrxonvKThSFfttd77OWQyle3rE/edit?gid=0#gid=0");
    },
  },
};
</script>

<style scoped>
/* Add any specific styles for App.vue here */
</style>
