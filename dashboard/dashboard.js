// paste dashboard JS here
// Predictive Execution Dashboard — Updated Full File
// Works with Render backend and real-model API
// Predictive Execution Dashboard — Correct Version
const API_BASE = "https://predictive-execution.onrender.com";

let slippageTrend = [];
let impactTrend = [];
const TREND_LIMIT = 50;

// Generic fetch
async function safeFetch(endpoint, target) {
    try {
        const res = await fetch(`${API_BASE}/${endpoint}`);
        const data = await res.json();
        document.getElementById(target).textContent = JSON.stringify(data, null, 2);
    } catch (err) {
        document.getElementById(target).textContent = JSON.stringify({ error: "Connection failed" }, null, 2);
    }
}

// Brain diagnostics
async function fetchDiagnostics() {
    try {
        const res = await fetch(`${API_BASE}/federation`);
        const data = await res.json();

        const outputs = data.federation.outputs || [];
        const formatted = outputs.map(o => {
            return `${o.name}
  Mode: ${o.mode}
  Confidence: ${o.confidence}
  Risk: ${o.riskScore}
  Impact: ${o.impactBps}
  Slippage: ${o.slippageBps}
  Diagnostics: ${o.diagnostics.join(", ")}
`;
        }).join("\n");

        document.getElementById("diagnostics").textContent = formatted;

    } catch (err) {
        document.getElementById("diagnostics").textContent =
            JSON.stringify({ error: "Connection failed" }, null, 2);
    }
}

// Federation visualizer
async function fetchFederationVisualizer() {
    try {
        const res = await fetch(`${API_BASE}/federation`);
        const data = await res.json();

        const outputs = data.federation.outputs || [];
        const mode = data.federation.federation.mode;
        const confidence = data.federation.federation.confidence;

        const lines = [];
        lines.push(`Final Mode: ${mode}`);
        lines.push(`Final Confidence: ${confidence}`);
        lines.push("");
        lines.push("Brain Votes:");

        outputs.forEach(o => {
            const bar = "█".repeat(Math.floor(o.confidence / 5));
            lines.push(
                `${o.name.padEnd(12)} | Mode: ${o.mode.padEnd(6)} | Conf: ${String(
                    o.confidence
                ).padEnd(3)} | ${bar}`
            );
        });

        document.getElementById("federationVisualizer").textContent = lines.join("\n");

    } catch (err) {
        document.getElementById("federationVisualizer").textContent =
            JSON.stringify({ error: "Connection failed" }, null, 2);
    }
}

// Mode timeline
async function fetchModeTimeline() {
    try {
        const res = await fetch(`${API_BASE}/mode_history`);
        const data = await res.json();

        const formatted = data.map(entry => {
            const ts = new Date(entry.timestamp * 1000).toLocaleTimeString();
            return `${ts} — ${entry.mode}
  Reasons: ${entry.reasons.join("; ")}
  Confidence: ${entry.confidence}
  Risk: ${entry.risk.toFixed(3)}  Impact: ${entry.impact.toFixed(3)}
  Latency: ${entry.latency}  Slippage: ${entry.slippage.toFixed(3)}
`;
        }).join("\n");

        document.getElementById("modeTimeline").textContent = formatted;

    } catch (err) {
        document.getElementById("modeTimeline").textContent =
            JSON.stringify({ error: "Connection failed" }, null, 2);
    }
}

// Mode analytics
async function fetchModeAnalytics() {
    try {
        const res = await fetch(`${API_BASE}/mode_history`);
        const data = await res.json();

        if (!Array.isArray(data) || data.length === 0) {
            document.getElementById("modeAnalytics").textContent = "No mode history yet.";
            return;
        }

        const counts = { LIVE: 0, SHADOW: 0, HALT: 0 };
        let totalConfidence = 0;
        let riskSum = { LIVE: 0, SHADOW: 0, HALT: 0 };
        let riskCount = { LIVE: 0, SHADOW: 0, HALT: 0 };

        data.forEach(entry => {
            const mode = entry.mode;
            counts[mode] = (counts[mode] || 0) + 1;

            totalConfidence += entry.confidence;

            riskSum[mode] += entry.risk;
            riskCount[mode] += 1;
        });

        const avgConfidence = totalConfidence / data.length;

        const avgRisk = {
            LIVE: riskCount.LIVE ? (riskSum.LIVE / riskCount.LIVE).toFixed(3) : "N/A",
            SHADOW: riskCount.SHADOW ? (riskSum.SHADOW / riskCount.SHADOW).toFixed(3) : "N/A",
            HALT: riskCount.HALT ? (riskSum.HALT / riskCount.HALT).toFixed(3) : "N/A",
        };

        const lastMode = data[data.length - 1].mode;

        const formatted = `
Mode Counts:
  LIVE:   ${counts.LIVE}
  SHADOW: ${counts.SHADOW}
  HALT:   ${counts.HALT}

Last Mode: ${lastMode}

Average Confidence: ${avgConfidence.toFixed(3)}

Average Risk by Mode:
  LIVE:   ${avgRisk.LIVE}
  SHADOW: ${avgRisk.SHADOW}
  HALT:   ${avgRisk.HALT}
`;

        document.getElementById("modeAnalytics").textContent = formatted;

    } catch (err) {
        document.getElementById("modeAnalytics").textContent =
            JSON.stringify({ error: "Connection failed" }, null, 2);
    }
}

// Safety triggers
async function fetchSafetyTriggers() {
    try {
        const res = await fetch(`${API_BASE}/mode_history`);
        const data = await res.json();

        const triggers = data
            .filter(e => e.mode === "HALT" || e.mode === "SHADOW")
            .map(e => {
                const ts = new Date(e.timestamp * 1000).toLocaleTimeString();
                return `${ts} — ${e.mode}
  Trigger: ${e.reasons.join("; ")}
  Risk: ${e.risk.toFixed(3)}  Impact: ${e.impact.toFixed(3)}
`;
            }).join("\n");

        document.getElementById("safetyTriggers").textContent =
            triggers || "No safety triggers yet.";

    } catch (err) {
        document.getElementById("safetyTriggers").textContent =
            JSON.stringify({ error: "Connection failed" }, null, 2);
    }
}

// Confidence heatmap
async function fetchConfidenceHeatmap() {
    try {
        const res = await fetch(`${API_BASE}/federation`);
        const data = await res.json();

        const outputs = data.federation.outputs || [];

        const formatted = outputs.map(o => {
            const bar = "█".repeat(Math.floor(o.confidence / 5));
            return `${o.name}: ${o.confidence}  ${bar}`;
        }).join("\n");

        document.getElementById("confidenceHeatmap").textContent = formatted;

    } catch (err) {
        document.getElementById("confidenceHeatmap").textContent =
            JSON.stringify({ error: "Connection failed" }, null, 2);
    }
}

// Slippage & impact trends
async function fetchTrendCharts() {
    try {
        const res = await fetch(`${API_BASE}/predict`);
        const data = await res.json();

        slippageTrend.push(data.slippage);
        impactTrend.push(data.impact);

        if (slippageTrend.length > TREND_LIMIT) slippageTrend.shift();
        if (impactTrend.length > TREND_LIMIT) impactTrend.shift();

        const formatted = `
Slippage Trend:
${slippageTrend.map(v => v.toFixed(2)).join("  ")}

Impact Trend:
${impactTrend.map(v => v.toFixed(2)).join("  ")}
`;

        document.getElementById("trendCharts").textContent = formatted;

    } catch (err) {
        document.getElementById("trendCharts").textContent =
            JSON.stringify({ error: "Connection failed" }, null, 2);
    }
}

// Main loop
function updateDashboard() {
    safeFetch("state", "state");
    safeFetch("decision", "decision");
    safeFetch("federation", "federation");
    safeFetch("arbitration", "arbitration");
    safeFetch("episodes", "episodes");
    safeFetch("performance", "performance");
    safeFetch("precedents", "precedents");

    fetchDiagnostics();
    fetchFederationVisualizer();
    fetchModeTimeline();
    fetchModeAnalytics();
    fetchSafetyTriggers();
    fetchConfidenceHeatmap();
    fetchTrendCharts();
}

setInterval(updateDashboard, 1000);
updateDashboard();
