<template>
  <div class="dropdown">
    <div tabindex="0" role="button" class="btn m-1" @click="toggleDropdown">
      {{ sheetName }}
    </div>
    <ul
      v-if="showDropdown"
      tabindex="0"
      class="dropdown-content menu bg-base-100 rounded-box z-[1] w-52 p-2 shadow"
    >
      <li v-if="loading">Loading...</li>
      <li v-else v-for="(header, index) in headers" :key="index">
        <label class="checkbox-container">
          <input
            type="checkbox"
            :id="`header-${index}`"
            :value="header"
            v-model="selectedHeaders"
            @change="onCheckboxChange"
          />
          {{ header }}
        </label>
      </li>
    </ul>
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "DropdownComponent",
  props: {
    sheetName: String,
    spreadsheetId: String, // Add this line
  },
  data() {
    return {
      showDropdown: false,
      headers: [],
      selectedHeaders: [],
      loading: false,
      loaded: false,
    };
  },
  methods: {
    toggleDropdown() {
      // Toggle the dropdown visibility
      this.showDropdown = !this.showDropdown;

      // Fetch headers if the dropdown is shown and headers are not yet loaded
      if (this.showDropdown && this.headers.length === 0) {
        this.fetchHeaders();
      }
    },
    async fetchHeaders() {
      this.loading = true;
      try {
        const response = await axios.post(
          "http://127.0.0.1:8000/api/v2/headers",
          {
            src_sheet_url: this.spreadsheetId,
            src_sheet_name: this.sheetName, // Use the prop here
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
      this.$emit("update:selectedSheets", this.sheetName, this.selectedHeaders);
    },
  },
};
</script>

<style scoped>
.checkbox-container {
  display: flex;
  align-items: center;
}
</style>
