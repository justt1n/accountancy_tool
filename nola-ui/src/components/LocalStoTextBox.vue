<template>
    <div class="w-full">
      <button @click="openModal" class="btn btn-primary">Show Stored Data</button>
  
      <div v-if="isModalOpen" class="modal modal-open">
        <div class="modal-box w-full max-w-full">
          <div class="modal-action">
            <button class="btn btn-sm btn-circle btn-ghost" @click="closeModal">&times;</button>
          </div>
          <label class="cursor-pointer label">
            <span class="label-text w-1/2">Stored Data</span>
          </label>
          <div v-if="storedData.length">
            <ul class="list-disc pl-5">
              <li v-for="(data, index) in storedData" :key="index">
                <div class="flex items-center"><h3 class="mr-2 bold-h3">Spreadsheet:</h3><span>{{ data.spreadsheet_id }}</span></div>
                <div class="flex items-center"><h3 class="mr-2 bold-h3">Sheet:</h3><span>{{ data.sheet_name }}</span></div>
                <div class="flex items-center"><h3 class="mr-2 bold-h3">Headers:</h3><span>{{ data.columns.join(', ') }}</span></div>
              </li>
            </ul>
          </div>
          <button @click="clearData" class="btn btn-danger mt-2">Clear Data</button>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    name: "LocalStoTextBox",
    data() {
      return {
        storedData: [],
        isModalOpen: false
      };
    },
    mounted() {
      this.loadData();
    },
    methods: {
      loadData() {
        const data = localStorage.getItem("FilterRequests");
        if (data) {
          this.storedData = JSON.parse(data).map(item => ({
            spreadsheet_id: item.spreadsheet_id,
            sheet_name: item.sheet_name,
            columns: item.columns
          }));
        }
      },
      clearData() {
        localStorage.removeItem("FilterRequests");
        this.storedData = [];
      },
      openModal() {
        this.isModalOpen = true;
        this.loadData();
      },
      closeModal() {
        this.isModalOpen = false;
      }
    },
    watch: {
      storedData(newValue) {
        localStorage.setItem("FilterRequests", JSON.stringify(newValue));
      }
    }
  };
  </script>
  
  <style scoped>
  .bold-h3 {
    font-weight: bold;
  }
  </style>