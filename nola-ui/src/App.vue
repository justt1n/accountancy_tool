<template>
  <div id="app">
    <div class="title">
      <h1 class="text-3xl font-bold tracking-tight text-gray-900 sm:text-4md md:text-4md p-6">
        <span class="block">
          <span class="text-transparent bg-clip-text bg-gradient-to-tr to-cyan-500 from-green-600">
            Product Payment
          </span>
          tool
        </span>
      </h1>
    </div>
    <div class="main">
      <form @submit.prevent="processData">
        <div class="flex">
          <!-- Src sheet -->
          <div class="src_scheet w-1/2">
            <div>
              <label for="srcSheet" class="input input-bordered flex items-center gap-2">Source Sheet:
                <input v-model="srcSheet" id="srcSheet" type="text" @input="onSrcSheetInput" class="grow" />
                <span class="badge badge-info">Product Url</span>
              </label>
            </div>
            <div class="form-control">
              <h2 class="text-xl font-bold dark:text-white p-2">Product Sheet Data</h2>
              <label v-for="(item, index) in srcSheetData" :key="index" class="cursor-pointer label w-48">
                <span class="label-text" :for="'src' + index">{{ item }}</span>
                <input type="checkbox" :id="'src' + index" v-model="selectedSrcData" :value="item"
                  class="checkbox checkbox-success" />
              </label>
            </div>
          </div>
          <!-- Des sheet -->
          <div class="des_sheet w-1/2">
            <div>
              <label for="srcSheet" class="input input-bordered flex items-center gap-2">Payment Sheet:
                <input v-model="desSheet" id="desSheet" type="text" @input="onDesSheetInput" class="grow" />
                <span class="badge badge-info">Payment Url</span>
              </label>
            </div>
            <div class="form-control">
              <h2 class="text-xl font-bold dark:text-white p-2">Payment Sheet Data</h2>
              <label v-for="(item, index) in desSheetData" :key="index" class="cursor-pointer label w-48">
                <span class="label-text" :for="'src' + index">{{ item }}</span>
                <input type="checkbox" :id="'src' + index" v-model="selectedDesData" :value="item"
                  class="checkbox checkbox-success" />
              </label>
            </div>
          </div>
        </div>
        <!-- Button -->
        <div class="button">
          <table>
            <tr>
              <th>
                <button class="btn btn-success" type="button" @click="loadData">
                  Load Data
                </button>
              </th>
              <th></th>
              <th>
                <button class="btn btn-success" type="submit">Process</button>
              </th>
            </tr>
          </table>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  data() {
    return {
      srcSheet: null,
      desSheet: null,
      srcSheetData: [],
      desSheetData: [],
      selectedSrcData: [],
      selectedDesData: [],
      allRangesData: [],
      selectedRanges: [],
      // other data properties
    };
  },
  methods: {
    async onSrcSheetInput(event) {
      console.log("Source Sheet input:", event.target.value);
      var src_spreadsheet_id = event.target.value.split("/")[5];
      try {
        const response = await axios.post(
          "http://127.0.0.1:8000/api/core/getAllSheetFromSpreadsheet",
          {
            src_sheet_url: src_spreadsheet_id,
          }
        );
        console.log("Response:", response.data);
        this.srcSheetData = response.data.sheets;
      } catch (error) {
        console.error("Error:", error);
      }
    },
    async onDesSheetInput(event) {
      console.log("Des Sheet input:", event.target.value);
      var des_spreadsheet_id = event.target.value.split("/")[5];
      try {
        const response = await axios.post(
          "http://127.0.0.1:8000/api/core/getAllSheetFromSpreadsheet",
          {
            src_sheet_url: des_spreadsheet_id,
          }
        );
        console.log("Response:", response.data);
        this.desSheetData = response.data.sheets;
      } catch (error) {
        console.error("Error:", error);
      }
    },
    buildDataToFilter() {
      console.log("Building data to filter");
      //get spreadsheet_id from srcSheet and desSheet
      var src_spreadsheet_id = this.srcSheet.split("/")[5];
      var des_spreadsheet_id = this.desSheet.split("/")[5];
      //check if srcSheet and desSheet are not empty
      if (src_spreadsheet_id == "" || des_spreadsheet_id == "") {
        alert("Please enter the source and destination spreadsheet");
        return;
      }
      //check if data not empty
      if (this.selectedSrcData.length == 0 || this.selectedDesData.length == 0) {
        alert("Please select the data to filter");
        return;
      }
      //check if len of desSheetData == 1
      if (this.selectedDesData.length != 1) {
        alert("Please select only one destination sheet, found: " + this.selectedDesData.length);
        return;
      }
      //build data to filter
      var data = {
        src_sheet_url: src_spreadsheet_id,
        des_sheet_url: des_spreadsheet_id,
        src_sheet_names: this.selectedSrcData,
        des_sheet_name: this.selectedDesData[0],
      };
      console.log("Data to filter:", JSON.stringify(data));
      return JSON.stringify(data);
    },
    buildDataToProcess() {
      console.log("Building data to process");
      var src_spreadsheet_id = this.srcSheet.split("/")[5];
      var des_spreadsheet_id = this.desSheet.split("/")[5];
      if (src_spreadsheet_id == "" || des_spreadsheet_id == "") {
        alert("Please enter the source and destination spreadsheet");
        return;
      }
      //check selectedRanges not empty
      if (this.selectedDesData.length == 0) {
        alert("Please select only one destination sheet, found: " + this.selectedDesData.length);
        return;
      }

      //build data to process
      var data = {
        src_sheet_url: src_spreadsheet_id,
        des_sheet_url: des_spreadsheet_id,
        des_sheet_names: this.selectedDesData
      };
      console.log("Build data to process. Data: ", JSON.stringify(data));
      return JSON.stringify(data);
    },
    async showInfo() {
      console.log("Show modal");
    },
    async loadData() {
      var data = this.buildDataToFilter();
      try {
        const response = await axios.post(
          "http://127.0.0.1:8000/api/core/testMultiSheet",
          data, {
          headers: {
            'Content-Type': 'application/json'
          }
        });
        console.log("Response:", response);
      } catch (error) {
        console.error("Error:", error);
      }
      console.log("Load data clicked");
    },
    async processData() {
      var data = this.buildDataToProcess();
      try {
        const response = await axios.post(
          "http://127.0.0.1:8000/api/core/testMultiSheet2",
          data, {
          headers: {
            'Content-Type': 'application/json'
          }
        });
        console.log("Response:", response);
      } catch (error) {
        console.error("Error:", error);
      }
      console.log("Process data clicked");
    },
  },
};
</script>
