// paste dashboard JS here
// Predictive Execution Dashboard — Updated Full File
// Works with Render backend and real-model API
// Predictive Execution Dashboard — Correct Version
// =========================================================
// Predictive Execution Dashboard – Full JS (Validated)
// =========================================================
const BASE = "https://predictive-execution-1.onrender.com";

async function load(endpoint, targetId) {
    try {
        const res = await fetch(`${BASE}/${endpoint}`);
        const data = await res.json();
        document.getElementById(targetId).innerText = JSON.stringify(data, null, 2);
    } catch {
        document.getElementById(targetId).innerText = "ERROR";
    }
}

function refreshAll() {
    load("state", "panel_state");
    load("decision", "panel_decision");
    load("federation", "panel_federation");
    load("arbitration", "panel_arbitration");

    load("federation_visualizer", "panel_federation_visualizer");
    load("brain_diagnostics", "panel_brain_diagnostics");
    load("episodes", "panel_episodes");
    load("performance", "panel_performance");

    load("precedents", "panel_precedents");
    load("mode_timeline", "panel_mode_timeline");
    load("mode_timeline", "panel_mode_analytics");
    load("safety", "panel_safety");

    load("confidence_heatmap", "panel_confidence_heatmap");
    load("bubble_chart", "panel_slippage_impact");
    load("visualizer", "panel_brain_performance");
    load("mode_timeline", "panel_mode_stability");

    load("risk_matrix", "panel_risk_matrix");
    load("risk_bubbles", "panel_risk_bubbles");
    load("latency", "panel_latency_spikes");
    load("slippage", "panel_slippage_anomalies");
}

// auto-refresh every 2 seconds
setInterval(refreshAll, 2000);

// initial load
refreshAll();
