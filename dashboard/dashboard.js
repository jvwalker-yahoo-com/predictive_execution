// paste dashboard JS here
// Predictive Execution Dashboard — Updated Full File
// Works with Render backend and real-model API
// Predictive Execution Dashboard — Correct Version

const BASE = "https://predictive-execution.onrender.com";

async function fetchJSON(path) {
  try {
    const res = await fetch(BASE + path);
    return await res.json();
  } catch (err) {
    return { error: "Connection failed" };
  }
}

async function refresh() {
  document.getElementById("state").innerText =
    JSON.stringify(await fetchJSON("/state"), null, 2);

  document.getElementById("decision").innerText =
    JSON.stringify(await fetchJSON("/decision"), null, 2);

  document.getElementById("federation").innerText =
    JSON.stringify(await fetchJSON("/federation"), null, 2);

  document.getElementById("arbitration").innerText =
    JSON.stringify(await fetchJSON("/arbitration"), null, 2);

  document.getElementById("episodes").innerText =
    JSON.stringify(await fetchJSON("/episodes"), null, 2);

  document.getElementById("performance").innerText =
    JSON.stringify(await fetchJSON("/performance"), null, 2);

  document.getElementById("precedents").innerText =
    JSON.stringify(await fetchJSON("/precedents"), null, 2);
}

setInterval(refresh, 3000);
refresh();
