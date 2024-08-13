<template>
    <div id="app">
      <TitleComponent />
      <div class="flex">
        <SheetComponent
          :sheetId="'srcSheet'"
          :sheetLabel="'Source Sheet'"
          :sheetData="srcSheetData"
          :badgeText="'Source'"
          @update:sheet="updateSrcSheet"
          @update:selectedData="updateSelectedSrcData"
        />
        <SheetComponent
          :sheetId="'destSheet'"
          :sheetLabel="'Destination Sheet'"
          :sheetData="destSheetData"
          :badgeText="'Destination'"
          @update:sheet="updateDestSheet"
          @update:selectedData="updateSelectedDestData"
        />
      </div>
      <ButtonComponent type="submit" variant="primary" @click="processData">
        Submit
      </ButtonComponent>
    </div>
  </template>
  
  <script>
  import TitleComponent from "./components/TitleComponent.vue";
  import SheetComponent from "./components/SheetComponent.vue";
  import ButtonComponent from "./components/ButtonComponent.vue";
  
  export default {
    name: "App",
    components: {
      TitleComponent,
      SheetComponent,
      ButtonComponent,
    },
    data() {
      return {
        srcSheet: "",
        srcSheetData: [],
        selectedSrcData: [],
        destSheet: "",
        destSheetData: [],
        selectedDestData: [],
        selectedSheet: [],
      };
    },
    methods: {
      updateSrcSheet(value) {
        this.srcSheet = value;
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
        console.log("Processing data...");
        console.log("Source Sheet:", this.srcSheet);
        console.log("Selected Source Data:", this.selectedSrcData);
        console.log("Destination Sheet:", this.destSheet);
        console.log("Selected Destination Data:", this.selectedDestData);
      },
    },
  };
  </script>
  
  <style scoped>
  /* Add any specific styles for App.vue here */
  </style>