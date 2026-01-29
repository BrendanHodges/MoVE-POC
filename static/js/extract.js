//Geography
const geoRadios = document.querySelectorAll('input[name="geo_level"]');
const stateInput = document.getElementById("stateInput");
const countyInput = document.getElementById("countyInput");

//MoVE toggle
const includeMoveCheckbox = document.getElementById("includeMoveScore");

//Variable selectors
const varType1Select = document.getElementById("varType1");
const varType2Select = document.getElementById("varType2");
const varType3Select = document.getElementById("varType3");

//Action buttons
const previewButton = document.getElementById("previewBtn");
const clearButton = document.getElementById("clearBtn");
const exportCsvButton = document.getElementById("exportCsvBtn");
const exportJsonButton = document.getElementById("exportJsonBtn");

//Selected variables display
const selectedVariablesContainer = document.getElementById("selected-variables");
const selectedCountSpan = document.getElementById("selected-count");

//Preview table
const previewTable = document.getElementById("preview-table");
const previewTableHead = previewTable.querySelector("thead");
const previewTableBody = previewTable.querySelector("tbody");

//Messages
const extractorMessages = document.getElementById("extractor-messages");


function handleGeoLevelChange() {
  geoRadios.forEach(radio => {
    if (radio.checked && radio.value === "county") {
      countyInput.disabled = false;
      countyInput.focus();
    }

    if (radio.checked && radio.value === "state") {
      countyInput.disabled = true;
      countyInput.value = ""; // clear county if switching back to state
    }
  });
}



geoRadios.forEach(radio => {
  radio.addEventListener("change", handleGeoLevelChange);
});


handleGeoLevelChange(); 