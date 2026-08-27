// paste dashboard JS here
// Predictive Execution Dashboard — Updated Full File
// Works with Render backend and real-model API
// Predictive Execution Dashboard — Correct Version
// =========================================================
// Predictive Execution Dashboard – Full JS (Validated)
// =========================================================

const BASE = "https://predictive-execution-1.onrender.com";

// -----------------------------
// Helper
// -----------------------------
async function load(endpoint, targetId) {
    try {
        const res = await fetch(`${BASE}/${endpoint}`);
        const data = await res.json();
        document.getElementById(targetId).innerText = JSON.stringify(data, null, 2);
    } catch (e) {
        document.getElementById(targetId).innerText = "ERROR";
    }
}

// -----------------------------
// STATE
// -----------------------------
document.getElementById("btn_state").onclick = () => {
    load("state", "panel_state");
};

// -----------------------------
// DECISION
// -----------------------------
document.getElementById("btn_decision").onclick = () => {
    load("decision", "panel_decision");
};

// -----------------------------
// FEDERATION SUMMARY
// -----------------------------
document.getElementById("btn_federation").onclick = () => {
    load("federation", "panel_federation");
};

// -----------------------------
// ARBITRATION
// -----------------------------
document.getElementById("btn_arbitration").onclick = () => {
    load("arbitration", "panel_arbitration");
};

// -----------------------------
// FEDERATION VISUALIZER
// -----------------------------
document.getElementById("btn_federation_visualizer").onclick = () => {
    load("federation_visualizer", "panel_federation_visualizer");
};

// -----------------------------
// BRAIN DIAGNOSTICS
// -----------------------------
document.getElementById("btn_brain_diagnostics").onclick = () => {
    load("brain_diagnostics", "panel_brain_diagnostics");
};

// -----------------------------
// RECENT EPISODES
// -----------------------------
document.getElementById("btn_episodes").onclick = () => {
    load("episodes", "panel_episodes");
};

// -----------------------------
// PERFORMANCE SAMPLES
// -----------------------------
document.getElementById("btn_performance").onclick = () => {
    load("performance", "panel_performance");
};

// -----------------------------
// ARBITRATION PRECEDENTS
// -----------------------------
document.getElementById("btn_precedents").onclick = () => {
    load("precedents", "panel_precedents");
};

// -----------------------------
// MODE SWITCH TIMELINE
// -----------------------------
document.getElementById("btn_mode_timeline").onclick = () => {
    load("mode_timeline", "panel_mode_timeline");
};

// -----------------------------
// MODE SWITCH ANALYTICS
// -----------------------------
document.getElementById("btn_mode_analytics").onclick = () => {
    load("mode_timeline", "panel_mode_analytics");
};

// -----------------------------
// SAFETY TRIGGERS
// -----------------------------
document.getElementById("btn_safety").onclick = () => {
    load("safety", "panel_safety");
};

// -----------------------------
// BRAIN CONFIDENCE HEATMAP
// -----------------------------
document.getElementById("btn_confidence_heatmap").onclick = () => {
    load("confidence_heatmap", "panel_confidence_heatmap");
};

// -----------------------------
// SLIPPAGE & IMPACT TRENDS
// -----------------------------
document.getElementById("btn_slippage_impact").onclick = () => {
    load("bubble_chart", "panel_slippage_impact");
};

// -----------------------------
// BRAIN PERFORMANCE
// -----------------------------
document.getElementById("btn_brain_performance").onclick = () => {
    load("visualizer", "panel_brain_performance");
};

// -----------------------------
// MODE STABILITY
// -----------------------------
document.getElementById("btn_mode_stability").onclick = () => {
    load("mode_timeline", "panel_mode_stability");
};

// -----------------------------
// LIVE RISK MATRIX
// -----------------------------
document.getElementById("btn_risk_matrix").onclick = () => {
    load("risk_matrix", "panel_risk_matrix");
};

// -----------------------------
// RISK BUBBLE CHART
// -----------------------------
document.getElementById("btn_risk_bubbles").onclick = () => {
    load("risk_bubbles", "panel_risk_bubbles");
};

// -----------------------------
// LATENCY SPIKES
// -----------------------------
document.getElementById("btn_latency_spikes").onclick = () => {
    load("latency", "panel_latency_spikes");
};

// -----------------------------
// SLIPPAGE ANOMALIES
// -----------------------------
document.getElementById("btn_slippage_anomalies").onclick = () => {
    load("slippage", "panel_slippage_anomalies");
};
