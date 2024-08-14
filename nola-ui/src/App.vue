<template>
  <div id="app">
    <TitleComponent />
          <div class="flex">
            <div class="w-1/2 border">
              <label class="cursor-pointer label">
              <span class="label-text w-1/2">Number of product sheet</span>
              <input type="number" class="input w-1/2 border" v-model="srcSheetUrlNum" placeholder="Enter sheet URLs separated by ';'" />
            </label>
            </div>  
          </div>
          <div class="bg-base-200 w-1/2">
              <ButtonComponent type="submit" variant="primary" @click="processData">
                Filter Data
              </ButtonComponent>
          </div>
    <div class="flex">
      <div class="w-1/2 mockup-window bg-gray-300 border">
        <div class="bg-gray-100 justify-center px-4 py-16">
          <div v-for="(url, i) in srcSheetUrlArray" :key="i">
            <SheetComponent
              :sheetId="'srcSheet' + i"
              :sheetLabel="'Product ' + i"
              :sheetData="srcSheetData[i]"
              :badgeText="'Source'"
              @update:sheet="updateSrcSheet(i)"
              @update:selectedData="updateSelectedSrcData(i)"
            />
        </div>
      </div>
        
      </div>
        <div class="w-1/2 mockup-window bg-gray-100 border">
          <div class="bg-gray-100 justify-center px-4 py-16">
            <DesSheetComponent
              :sheetId="'destSheet'"
              :sheetLabel="'Destination Sheet'"
              :sheetData="destSheetData"
              :badgeText="'Destination'"
              @update:sheet="updateDestSheet"
              @update:selectedData="updateSelectedDestData"
            />
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

  export default {
    name: "App",
    components: {
      TitleComponent,
      SheetComponent,
      ButtonComponent,
      DesSheetComponent
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
      };
    },
    computed: {
      srcSheetUrlArray() {
        return this.srcSheetUrlNum;
      }
    },
    methods: {
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