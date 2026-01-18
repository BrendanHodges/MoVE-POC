// --------------------
// 0) MAP SETUP
// --------------------
const map = L.map("map", { doubleClickZoom: false }).setView([39.8, -98.6], 4);

L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  attribution: "© OpenStreetMap contributors",
}).addTo(map);

// --------------------
// 1) SHARED APP STATE
// --------------------
window.App = {
  map,
  legendControl: null,

  // layers
  usStatesLayer: null,
  activeCountyLayer: null,

  // geo
  usStatesData: null,
  usCountiesData: null,
  selectedCountiesData: null, 

  // selection
  selectedStateFP: null,
  selectedStateName: null,

  // scores
  stateScores: {},   
  countyScores: {},
  allCountyScores: {},  

  // populations
  countyPopulation: {},

  // helpers
  getStateScore(stateFP) {
    return window.App.stateScores[stateFP]?.score ?? null;
  },

  getCountyScore(geoid) {
    return window.App.countyScores[geoid]?.score ?? null;
  },

  getColor(score) {
    return score > 80 ? "#003049" :
           score > 60 ? "#669BBC" :
           score > 40 ? "#FDF0D5" :
           score > 20 ? "#C1121F" : "#780000";
  }
};

// --------------------
// 2) INITIAL LOADERS (STATE-ONLY)
// --------------------
async function loadStateScores() {
  const res = await fetch("/api/state-scores");
  if (!res.ok) throw new Error(`state-scores failed: ${res.status}`);
  return res.json();
}

async function loadStatesGeo() {
  const res = await fetch("/static/data/us_states.json");
  if (!res.ok) throw new Error(`us_states.json failed: ${res.status}`);
  return res.json();
}

// --------------------
// 3) BOOTSTRAP
// --------------------
async function init() {
  try {
    const [stateScores, statesGeo] = await Promise.all([
      loadStateScores(),
      loadStatesGeo(),
    ]);
  
    window.App.stateScores = stateScores;
    window.App.usStatesData = statesGeo;

    // hand off to US view
    if (typeof window.initUSView !== "function") {
      throw new Error("initUSView() not found (us.js not loaded?)");
    }

    window.initUSView();
  } catch (err) {
    console.error("Init error:", err);
    document.getElementById("sidebar").innerHTML = `
      <h2>Error</h2>
      <p>Failed to load state data.</p>
    `;
  }
}

init();
