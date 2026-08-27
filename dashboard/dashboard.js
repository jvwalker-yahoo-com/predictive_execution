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

let modeTimeline = [];
let bubblePoint = { x: 0, y: 0, r: 10 };
let heatmapMatrix = [[0,0,0,0],[0,0,0,0],[0,0,0,0]];
let safetyTriggered = false;

// -----------------------------
// CHART OBJECTS
// -----------------------------
let chartRisk, chartImpact, chartSlippage, chartLatency;
let chartBubble, chartHeatmap, chartTimeline, chartSafety;

// -----------------------------
// CREATE CHARTS
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

  chartBubble = new Chart(document.getElementById("chart_bubble"), {
    type: "bubble",
    data: { datasets: [{ label: "Bubble", data: [bubblePoint], backgroundColor: "#ff6666" }] },
    options: { animation: false }
  });

  chartHeatmap = new Chart(document.getElementById("chart_heatmap"), {
    type: "bar",
    data: {
      labels: ["R1","R2","R3","R4","R5","R6","R7","R8","R9","R10","R11","R12"],
      datasets: [{
        label: "Confidence",
        data: Array(12).fill(0),
        backgroundColor: Array(12).fill("#ffaa00")
      }]
    },
    options: { animation: false }
  });

  chartTimeline = new Chart(document.getElementById("chart_timeline"), {
    type: "line",
    data: { labels: [], datasets: [{ label: "Mode", data: [], borderColor: "#8888ff" }] },
    options: { animation: false }
  });

  chartSafety = new Chart(document.getElementById("chart_safety"), {
    type: "doughnut",
    data: {
      labels: ["Triggered", "Safe"],
      datasets: [{
        data: [0, 1],
        backgroundColor: ["#ff4444", "#44ff44"]
      }]
    },
    options: { animation: false }
  });
}

// -----------------------------
// UPDATE CHARTS
// -----------------------------
function updateCharts(state, bubbles, heatmap, timeline, safety) {

  // Trend charts
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

  // Bubble chart
  bubblePoint = {
    x: bubbles[0].risk,
    y: bubbles[0].impact,
    r: bubbles[0].size
  };
  chartBubble.data.datasets[0].data = [bubblePoint];
  chartBubble.update();

  // Heatmap (flatten matrix)
  const flat = heatmap.matrix.flat();
  chartHeatmap.data.datasets[0].data = flat;
  chartHeatmap.data.datasets[0].backgroundColor = flat.map(v =>
    `rgba(${Math.floor(v * 255)}, ${Math.floor(255 - v * 255)}, 0, 0.8)`
  );
  chartHeatmap.update();

  // Timeline
  const timelineValues = timeline.map(t => t.mode === "OK" ? 0 : 1);
  chartTimeline.data.labels = timelineValues.map((_, i) => i);
  chartTimeline.data.datasets[0].data = timelineValues;
  chartTimeline.update();

  // Safety gauge
  const triggered =
    safety.risk.triggered ||
    safety.impact.triggered ||
    safety.slippage.triggered ||
    safety.latency.triggered;

  chartSafety.data.datasets[0].data = triggered ? [1, 0] : [0, 1];
  chartSafety.update();
}

// -----------------------------
// LOAD PANELS + CHART DATA
// -----------------------------
async function load(endpoint, targetId) {
  try {
    const res = await fetch(`${BASE}/${endpoint}`);
    const data = await res.json();
    document.getElementById(targetId).innerText = JSON.stringify(data, null, 2);
    return data;
  } catch {
    document.getElementById(targetId).innerText = "ERROR";
    return null;
  }
}

// -----------------------------
// REFRESH ALL
// -----------------------------
async function refreshAll() {

  const state = await load("state", "panel_state");
  const bubbles = await load("bubble_chart", "panel_bubbles");
  const heatmap = await load("heatmap", "panel_heatmap");
  const timeline = await load("timeline", "panel_timeline");
  const safety = await load("safety_triggers", "panel_safety");

  updateCharts(state, bubbles, heatmap, timeline, safety);

  load("decision", "panel_decision");
  load("federation", "panel_federation");
  load("arbitration", "panel_arbitration");

  load("visualizer", "panel_visualizer");
  load("diagnostics", "panel_diagnostics");
  load("episodes", "panel_episodes");
  load("performance", "panel_performance");

  load("precedents", "panel_precedents");
  load("risk_matrix", "panel_risk_matrix");
  load("latency_spikes", "panel_latency_spikes");
  load("slippage_anomalies", "panel_slippage_anomalies");
}

// -----------------------------
// STARTUP
// -----------------------------
createCharts();
refreshAll();
setInterval(refreshAll, 2000);
