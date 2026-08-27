// paste dashboard JS here
// Predictive Execution Dashboard — Updated Full File
// Works with Render backend and real-model API
// Predictive Execution Dashboard — Correct Version
// =========================================================
// Predictive Execution Dashboard – Full JS (Validated)
// =========================================================
const BASE = "";

async function load(endpoint, targetId) {
  try {
    const res = await fetch(`${BASE}/${endpoint}`);
    const data = await res.json();
    document.getElementById(targetId).innerText = JSON.stringify(data, null, 2);
  } catch (e) {
    document.getElementById(targetId).innerText = "ERROR";
  }
}

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

refreshAll();
setInterval(refreshAll, 2000);
