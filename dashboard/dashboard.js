// paste dashboard JS here
// Predictive Execution Dashboard — Updated Full File
// Works with Render backend and real-model API
// Predictive Execution Dashboard — Correct Version
const API_BASE = "https://predictive-execution.onrender.com";

let slippageTrend = [];
let impactTrend = [];
const TREND_LIMIT = 50;

// ---------- generic fetch ----------
async function safeFetch(endpoint, target) {
    try {
        const res = await fetch(`${API_BASE}/${endpoint}`);
        const data = await res.json();
        document.getElementById(target).textContent = JSON.stringify(data, null, 2);
    } catch (err) {
        document.getElementById(target).textContent = JSON.stringify({ error: "Connection failed" }, null, 2);
    }
}

// ---------- brain diagnostics ----------
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

// ---------- federation visualizer ----------
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

// ---------- mode timeline ----------
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

// ---------- mode analytics ----------
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

// ---------- safety triggers ----------
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

// ---------- confidence heatmap ----------
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

// ---------- slippage & impact trends ----------
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

// ---------- brain performance ----------
async function fetchBrainPerformance() {
    try {
        const resFed = await fetch(`${API_BASE}/federation`);
        const resPerf = await fetch(`${API_BASE}/performance`);
        const fed = await resFed.json();
        const perf = await resPerf.json();

        const outputs = fed.federation.outputs || [];
        const scores = {};

        outputs.forEach(o => {
            scores[o.name] = {
                confidence: o.confidence,
                risk: o.riskScore,
                impact: o.impactBps,
                slippage: o.slippageBps,
                episodes: 0,
            };
        });

        (perf.samples || []).forEach(s => {
            const name = s.brain;
            if (!scores[name]) return;
            scores[name].episodes += 1;
        });

        const formatted = Object.entries(scores).map(([name, s]) => {
            return `${name}
  Episodes:   ${s.episodes}
  Conf:       ${s.confidence}
  Risk:       ${s.risk}
  Impact:     ${s.impact}
  Slippage:   ${s.slippage}
`;
        }).join("\n");

        document.getElementById("brainPerformance").textContent =
            formatted || "No performance data yet.";

    } catch (err) {
        document.getElementById("brainPerformance").textContent =
            JSON.stringify({ error: "Connection failed" }, null, 2);
    }
}

// ---------- mode stability ----------
async function fetchModeStability() {
    try {
        const res = await fetch(`${API_BASE}/mode_history`);
        const data = await res.json();

        if (!Array.isArray(data) || data.length < 2) {
            document.getElementById("modeStability").textContent = "Not enough history.";
            return;
        }

        let switches = 0;
        let lastMode = data[0].mode;
        let haltCount = 0;
        let totalDuration = 0;

        for (let i = 1; i < data.length; i++) {
            const e = data[i];
            if (e.mode !== lastMode) switches++;
            if (e.mode === "HALT") haltCount++;
            totalDuration += (data[i].timestamp - data[i - 1].timestamp);
            lastMode = e.mode;
        }

        const avgInterval = totalDuration / (data.length - 1);
        const volatility = (switches / data.length).toFixed(3);

        const formatted = `
Mode Stability:
  Switches:          ${switches}
  HALT events:       ${haltCount}
  Avg interval (s):  ${avgInterval.toFixed(1)}
  Volatility score:  ${volatility}
`;

        document.getElementById("modeStability").textContent = formatted;

    } catch (err) {
        document.getElementById("modeStability").textContent =
            JSON.stringify({ error: "Connection failed" }, null, 2);
    }
}

// ---------- live risk matrix ----------
async function fetchRiskMatrix() {
    try {
        const res = await fetch(`${API_BASE}/predict`);
        const data = await res.json();

        const risk = data.risk;
        const impact = data.impact;
        const slippage = data.slippage;
        const latency = data.latency;

        function quadrant(r, i) {
            if (r < 0.3 && i < 0.3) return "SAFE";
            if (r < 0.6 && i < 0.6) return "WATCH";
            if (r < 0.8 && i < 0.8) return "DANGER";
            return "CRITICAL";
        }

        const qRI = quadrant(risk, impact);
        const qRS = quadrant(risk, slippage);
        const qRL = quadrant(risk, latency);

        const formatted = `
Risk Matrix:
  Risk:     ${risk.toFixed(3)}
  Impact:   ${impact.toFixed(3)}
  Slippage: ${slippage.toFixed(3)}
  Latency:  ${latency.toFixed(3)}

Quadrants:
  Risk × Impact:   ${qRI}
  Risk × Slippage: ${qRS}
  Risk × Latency:  ${qRL}
`;

        document.getElementById("riskMatrix").textContent = formatted;

    } catch (err) {
        document.getElementById("riskMatrix").textContent =
            JSON.stringify({ error: "Connection failed" }, null, 2);
    }
}

// ---------- risk bubble chart ----------
async function fetchRiskBubble() {
    try {
        const res = await fetch(`${API_BASE}/mode_history`);
        const data = await res.json();

        const bubbles = data.slice(-20).map(e => {
            const size = Math.max(1, Math.round(e.risk * 10));
            const bubble = "●".repeat(size);
            const ts = new Date(e.timestamp * 1000).toLocaleTimeString();
            return `${ts} ${bubble} (${e.mode} r=${e.risk.toFixed(2)} i=${e.impact.toFixed(2)})`;
        }).join("\n");

        document.getElementById("riskBubble").textContent =
            bubbles || "No recent risk samples.";

    } catch (err) {
        document.getElementById("riskBubble").textContent =
            JSON.stringify({ error: "Connection failed" }, null, 2);
    }
}

// ---------- latency spikes ----------
async function fetchLatencySpikes() {
    try {
        const res = await fetch(`${API_BASE}/mode_history`);
        const data = await res.json();

        const spikes = data
            .filter(e => e.latency > 200)
            .map(e => {
                const ts = new Date(e.timestamp * 1000).toLocaleTimeString();
                return `${ts} latency=${e.latency}ms mode=${e.mode}`;
            }).join("\n");

        document.getElementById("latencySpikes").textContent =
            spikes || "No latency spikes detected.";

    } catch (err) {
        document.getElementById("latencySpikes").textContent =
            JSON.stringify({ error: "Connection failed" }, null, 2);
    }
}

// ---------- slippage anomalies ----------
async function fetchSlippageAnomalies() {
    try {
        const res = await fetch(`${API_BASE}/mode_history`);
        const data = await res.json();

        const anomalies = data
            .filter(e => Math.abs(e.slippage) > 5)
            .map(e => {
                const ts = new Date(e.timestamp * 1000).toLocaleTimeString();
                return `${ts} slippage=${e.slippage.toFixed(2)}bps mode=${e.mode}`;
            }).join("\n");

        document.getElementById("slippageAnomalies").textContent =
            anomalies || "No slippage anomalies detected.";

    } catch (err) {
        document.getElementById("slippageAnomalies").textContent =
            JSON.stringify({ error: "Connection failed" }, null, 2);
    }
}

// ---------- auto-collapse panels ----------
function initPanelCollapsing() {
    const panels = document.querySelectorAll(".panel");
    panels.forEach(panel => {
        const header = panel.querySelector("h2");
        if (!header) return;
        header.addEventListener("click", () => {
            panel.classList.toggle("collapsed");
        });
    });
}

// ---------- main loop ----------
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
    fetchBrainPerformance();
    fetchModeStability();
    fetchRiskMatrix();
    fetchRiskBubble();
    fetchLatencySpikes();
    fetchSlippageAnomalies();
}

document.addEventListener("DOMContentLoaded", () => {
    initPanelCollapsing();
    updateDashboard();
    setInterval(updateDashboard, 1000);
});
