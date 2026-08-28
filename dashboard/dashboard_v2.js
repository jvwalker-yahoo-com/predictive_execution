// paste dashboard JS here
// Predictive Execution Dashboard — Updated Full File
// Works with Render backend and real-model API
// Predictive Execution Dashboard — Correct Version
// =========================================================
// Predictive Execution Dashboard – Full JS (Validated)
// =========================================================

const BASE_URL = "https://predictive-execution-1.onrender.com";

async function fetchJSON(path) {
  try {
    const res = await fetch(`${BASE_URL}${path}`);
    return await res.json();
  } catch (e) {
    return { error: e.message };
  }
}

async function update(id, path) {
  const el = document.getElementById(id);
  el.textContent = JSON.stringify(await fetchJSON(path), null, 2);
}

function tick() {
  update("state-json", "/state");
  update("decision-json", "/decision");
  update("federation-json", "/federation");
  update("arbitration-json", "/arbitration");
  update("anomaly-json", "/anomaly_detector");
  update("events-json", "/node_events");
  update("quadrant-json", "/quadrant");
  update("heartbeat-json", "/heartbeat");
  update("drift-json", "/sync_drift");
}

setInterval(tick, 1000);
tick();
