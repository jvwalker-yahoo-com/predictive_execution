// paste dashboard JS here
// Predictive Execution Dashboard — Updated Full File
// Works with Render backend and real-model API
// Predictive Execution Dashboard — Correct Version
// =========================================================
// Predictive Execution Dashboard – Full JS (Validated)
// =========================================================
const BASE = "";

// chart buffers
let riskData = [];
let impactData = [];
let slippageData = [];
let latencyData = [];

let chartRisk, chartImpact, chartSlippage, chartLatency;
let chartBubble, chartHeatmap, chartTimeline, chartSafety;

// neon helper
function neon(color) {
  return {
    borderColor: color,
    backgroundColor: color + "33",
    pointBackgroundColor: color,
    pointBorderColor: color
  };
}

function createCharts() {

  chartRisk = new Chart(document.getElementById("chart_risk"), {
    type: "line",
    data: { labels: [], datasets: [{ label: "Risk", data: [], ...neon("#ff0044") }] },
    options: { animation: false }
  });

  chartImpact = new Chart(document.getElementById("chart_impact"), {
    type: "line",
    data: { labels: [], datasets: [{ label: "Impact", data: [], ...neon("#00aaff") }] },
    options: { animation: false }
  });

  chartSlippage = new Chart(document.getElementById("chart_slippage"), {
    type: "line",
    data: { labels: [], datasets: [{ label: "Slippage", data: [], ...neon("#ffaa00") }] },
    options: { animation: false }
  });

  chartLatency = new Chart(document.getElementById("chart_latency"), {
    type: "line",
    data: { labels: [], datasets: [{ label: "Latency", data: [], ...neon("#00ff66") }] },
    options: { animation: false }
  });

  chartBubble = new Chart(document.getElementById("chart_bubble"), {
    type: "bubble",
    data: { datasets: [{ label: "Bubble", data: [], backgroundColor: "#ff0044aa" }] },
    options: { animation: false }
  });

  chartHeatmap = new Chart(document.getElementById("chart_heatmap"), {
    type: "bar",
    data: {
      labels: Array.from({ length: 12 }, (_, i) => `C${i + 1}`),
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
    data: { labels: [], datasets: [{ label: "Mode", data: [], ...neon("#bb88ff") }] },
    options: { animation: false }
  });

  chartSafety = new Chart(document.getElementById("chart_safety"), {
    type: "doughnut",
    data: {
      labels: ["Triggered", "Safe"],
      datasets: [{
        data: [0, 1],
        backgroundColor: ["#ff0044", "#00ff66"]
      }]
    },
    options: { animation: false }
  });
}

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

async function refreshAll() {

  const state = await load("state", "panel_state");
  await load("decision", "panel_decision");
  await load("federation", "panel_federation");
  await load("arbitration", "panel_arbitration");

  const bubbles = await fetch(`${BASE}/bubble_chart`).then(r => r.json()).catch(() => null);
  const heatmap = await fetch(`${BASE}/heatmap`).then(r => r.json()).catch(() => null);
  const timeline = await fetch(`${BASE}/timeline`).then(r => r.json()).catch(() => null);
  const safety = await fetch(`${BASE}/safety_triggers`).then(r => r.json()).catch(() => null);

  if (state) {
    riskData.push(state.risk);
    impactData.push(state.impact);
    slippageData.push(state.slippage);
    latencyData.push(state.latency);

    if (riskData.length > 50) riskData.shift();
    if (impactData.length > 50) impactData.shift();
    if (slippageData.length > 50) slippageData.shift();
    if (latencyData.length > 50) latencyData.shift();

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

  if (bubbles && bubbles.length > 0) {
    const b = bubbles[0];
    chartBubble.data.datasets[0].data = [{
      x: b.risk,
      y: b.impact,
      r: b.size
    }];
    chartBubble.update();
  }

  if (heatmap && heatmap.matrix) {
    const flat = heatmap.matrix.flat();
    chartHeatmap.data.datasets[0].data = flat;
    chartHeatmap.data.datasets[0].backgroundColor = flat.map(v =>
      `rgba(${Math.floor(v * 255)}, ${Math.floor(255 - v * 255)}, 0, 0.8)`
    );
    chartHeatmap.update();
  }

  if (timeline && Array.isArray(timeline)) {
    const vals = timeline.map(t => t.mode === "OK" ? 0 : t.mode === "WARN" ? 1 : 2);
    chartTimeline.data.labels = vals.map((_, i) => i);
    chartTimeline.data.datasets[0].data = vals;
    chartTimeline.update();
  }

  if (safety) {
    const triggered =
      safety.risk?.triggered ||
      safety.impact?.triggered ||
      safety.slippage?.triggered ||
      safety.latency?.triggered;

    chartSafety.data.datasets[0].data = triggered ? [1, 0] : [0, 1];
    chartSafety.update();
  }

  // SAFE NEW FUNCTIONALITY
  load("anomaly_detector", "panel_anomaly");
  load("mode_events", "panel_events");
  load("quadrant", "panel_quadrant");
  load("heartbeat", "panel_heartbeat");
  load("sync_drift", "panel_drift");
}

createCharts();
refreshAll();
setInterval(refreshAll, 2000);
