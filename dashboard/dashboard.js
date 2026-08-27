// paste dashboard JS here
// Predictive Execution Dashboard — Updated Full File
// Works with Render backend and real-model API
// Predictive Execution Dashboard — Correct Version
// =========================================================
// Predictive Execution Dashboard – Full JS (Validated)
// =========================================================
const BASE = "";

// -----------------------------
// CHART BUFFERS
// -----------------------------
let riskData = [];
let impactData = [];
let slippageData = [];
let latencyData = [];

let chartRisk, chartImpact, chartSlippage, chartLatency;

// -----------------------------
// CHART INITIALIZATION
// -----------------------------
function createCharts() {
  chartRisk = new Chart(document.getElementById("chart_risk"), {
    type: "line",
    data: { labels: [], datasets: [{ label: "Risk", data: [], borderColor: "#ff4444" }] },
    options: { animation: false }
  });

  chartImpact = new Chart(document.getElementById("chart_impact"), {
    type: "line",
    data: { labels: [], datasets: [{ label: "Impact", data: [], borderColor: "#44aaff" }] },
    options: { animation: false }
  });

  chartSlippage = new Chart(document.getElementById("chart_slippage"), {
    type: "line",
    data: { labels: [], datasets: [{ label: "Slippage", data: [], borderColor: "#ffaa44" }] },
    options: { animation: false }
  });

  chartLatency = new Chart(document.getElementById("chart_latency"), {
    type: "line",
    data: { labels: [], datasets: [{ label: "Latency", data: [], borderColor: "#66ff66" }] },
    options: { animation: false }
  });
}

// -----------------------------
// UPDATE CHARTS
// -----------------------------
function updateCharts(state) {
  const timestamp = new Date().toLocaleTimeString();

  riskData.push(state.risk);
  impactData.push(state.impact);
  slippageData.push(state.slippage);
  latencyData.push(state.latency);

  if (riskData.length > 20) riskData.shift();
  if (impactData.length > 20) impactData.shift();
  if (slippageData.length > 20) slippageData.shift();
  if (latencyData.length > 20) latencyData.shift();

  chartRisk.data.labels = riskData.map((_, i) => i);
  chartRisk.data.datasets[0].data = riskData;
  chartRisk.update();

  chartImpact.data.labels = impactData.map((_, i) => i);
  chartImpact.data.datasets[0].data = impactData;
  chartImpact.update();

  chartSlippage.data.labels = slippageData.map((_, i) => i);
  chartSlippage.data.datasets[0].data = slippageData;
  chartSlippage.update();

  chartLatency.data.labels = latencyData.map((_, i) => i);
  chartLatency.data.datasets[0].data = latencyData;
  chartLatency.update();
}

// -----------------------------
// LOAD JSON PANELS
// -----------------------------
async function load(endpoint, targetId) {
  try {
    const res = await fetch(`${BASE}/${endpoint}`);
    const data = await res.json();
    document.getElementById(targetId).innerText = JSON.stringify(data, null, 2);

    if (endpoint === "state") updateCharts(data);

  } catch (e) {
    document.getElementById(targetId).innerText = "ERROR";
  }
}

// -----------------------------
// REFRESH ALL PANELS
// -----------------------------
function refreshAll() {
  load("state", "panel_state");
  load("decision", "panel_decision");
  load("federation", "panel_federation");
  load("arbitration", "panel_arbitration");

  load("visualizer", "panel_visualizer");
  load("diagnostics", "panel_diagnostics");
  load("episodes", "panel_episodes");
  load("performance", "panel_performance");

  load("precedents", "panel_precedents");
  load("timeline", "panel_timeline");
  load("safety_triggers", "panel_safety");
  load("risk_matrix", "panel_risk_matrix");

  load("bubble_chart", "panel_bubbles");
  load("heatmap", "panel_heatmap");
  load("latency_spikes", "panel_latency_spikes");
  load("slippage_anomalies", "panel_slippage_anomalies");
}

// -----------------------------
// STARTUP
// -----------------------------
createCharts();
refreshAll();
setInterval(refreshAll, 2000);
