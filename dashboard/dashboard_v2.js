// =========================================================
// Predictive Execution Dashboard – Full JS (Validated)
// =========================================================

const BASE_URL = window.location.origin.includes("localhost") || window.location.origin.includes("127.0.0.1")
  ? window.location.origin
  : "https://predictive-execution-1.onrender.com";

async function fetchJSON(path) {
  try {
    const res = await fetch(`${BASE_URL}${path}`);
    return await res.json();
  } catch (e) {
    return { error: e.message };
  }
}

async function update(ids, path) {
  const data = await fetchJSON(path);
  const text = JSON.stringify(data, null, 2);
  const idList = Array.isArray(ids) ? ids : [ids];
  for (const id of idList) {
    const el = document.getElementById(id);
    if (el) {
      el.textContent = text;
    }
  }
  return data;
}

function tick() {
  update(["panel_state", "state-json"], "/state");
  update(["panel_decision", "decision-json"], "/decision");
  update(["panel_federation", "federation-json"], "/federation");
  update(["panel_arbitration", "arbitration-json"], "/arbitration");
  update(["panel_anomaly", "anomaly-json"], "/anomaly_detector");
  update(["panel_events", "events-json"], "/node_events");
  update(["panel_quadrant", "quadrant-json"], "/quadrant");
  update(["panel_heartbeat", "heartbeat-json"], "/heartbeat");
  update(["panel_drift", "drift-json"], "/sync_drift");
}

setInterval(tick, 2000);
tick();
