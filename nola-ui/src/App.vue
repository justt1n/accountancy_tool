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
    </div>
  </template>
  
  <script>
  import TitleComponent from "./components/TitleComponent.vue";
  import SheetComponent from "./components/SheetComponent.vue";
  
  export default {
    name: "App",
    components: {
      TitleComponent,
      SheetComponent,
    },
    data() {
      return {
        srcSheet: "",
        srcSheetData: [],
        selectedSrcData: [],
        destSheet: "",
        destSheetData: [],
        selectedDestData: []
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
      }
    }
  };
  </script>
  
  <style scoped>
  /* Add any specific styles for App.vue here */
  </style>