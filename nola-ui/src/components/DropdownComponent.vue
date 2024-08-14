<template>
  <div class="relative">
    <button class="btn m-1" @click="toggleModal">
      {{ sheetName }}
    </button>
    <div v-if="showModal" class="fixed z-10 inset-0 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
      <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" aria-hidden="true"></div>
        <span class="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>
        <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
          <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
            <div class="sm:flex sm:items-start">
              <div class="mt-3 text-center sm:mt-0 sm:ml-4 sm:text-left">
                <h3 class="text-lg leading-6 font-medium text-gray-900" id="modal-title">
                  Select Headers
                </h3>
                <div class="mt-2">
                  <ul>
                    <li v-if="loading">Loading...</li>
                    <li v-else v-for="(header, index) in headers" :key="index">
                      <label class="cursor-pointer label flex items-center">
                        <span class="label-text">{{ header }}</span>
                        <input
                          class="checkbox checkbox-success mr-2"
                          type="checkbox"
                          :id="`header-${index}`"
                          :value="header"
                          v-model="selectedHeaders"
                          @change="onCheckboxChange"
                        />
                      </label>
                    </li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
          <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
            <button type="button" class="btn m-1" @click="submitModal">
              Submit
            </button>
            <button type="button" class="btn m-1" @click="resetModal">
              Reset
            </button>
            <button type="button" class="btn m-1" @click="showModal = false">
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: "DropdownComponent",
  props: {
    sheetName: String,
    spreadsheetId: String,
  },
  data() {
    return {
      showModal: false,
      headers: [],
      selectedHeaders: [],
      loading: false,
      loaded: false,
    };
  },
  methods: {
    toggleModal() {
      this.showModal = !this.showModal;
      console.log("showModal:", this.showModal);

      if (this.showModal && !this.loaded) {
        const items = JSON.parse(localStorage.getItem('items')) || [];
        const existingItem = items.find(item => 
          item.spreadsheet_id === this.spreadsheetId && 
          item.sheet_name === this.sheetName
        );

        if (existingItem) {
          this.headers = existingItem.columns;
          this.selectedHeaders = existingItem.columns;
          this.loaded = true;
          console.log("Loaded headers from localStorage:", this.headers);
        } else {
          console.log("Fetching headers...");
          this.fetchHeaders();
        }
      }
    },
    async fetchHeaders() {
      this.loading = true;
      try {
        const response = await axios.post(
          "http://127.0.0.1:8000/api/v2/headers",
          {
            src_sheet_url: this.spreadsheetId,
            src_sheet_name: this.sheetName,
          }
        );
        this.headers = response.data.data;
        this.loaded = true;
        console.log("Fetched headers:", this.headers);
      } catch (error) {
        console.error("Error fetching headers:", error);
      } finally {
        this.loading = false;
      }
    },
    onCheckboxChange() {
      this.$emit("update:selectedHeaders", this.selectedHeaders);
    },
    submitModal() {
      const newItem = {
        spreadsheet_id: this.spreadsheetId,
        sheet_name: this.sheetName,
        columns: this.selectedHeaders,
      };
      console.log("Saving item:", newItem);
      let items = JSON.parse(localStorage.getItem("FilterRequests")) || [];

      const isDuplicate = items.some(
        (item) =>
          item.spreadsheet_id === newItem.spreadsheet_id &&
          item.sheet_name === newItem.sheet_name
      );

      if (!isDuplicate) {
        items.push(newItem);
        localStorage.setItem("FilterRequests", JSON.stringify(items));
        console.log("Item saved to localStorage:", newItem);
      } else {
        console.log("Duplicate item found, not saving:", newItem);
      }

      this.showModal = false;
    },
    resetModal() {
      //remove that item from localStorage with that spreadsheet_id and sheet_name
      let items = JSON.parse(localStorage.getItem("FilterRequests")) || [];
      items = items.filter(
        (item) =>
          item.spreadsheet_id !== this.spreadsheetId ||
          item.sheet_name !== this.sheetName
      );
      localStorage.setItem("FilterRequests", JSON.stringify(items));
      this.fetchHeaders();
    },
  }
};
</script>