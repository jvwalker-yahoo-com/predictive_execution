/**
 * eToro ReAuth Mobile Application Logic
 */

const DEFAULT_API_KEY = "sdgdskldFPLGfjHn1421dgnlxdGTbngdflg6290bRjslfihsjhSDsdgGHH25hjf";
const DEFAULT_BASE_URL = "https://public-api.etoro.com";
const DEFAULT_RENDER_URL = "https://autonomous-trading-cockpit.onrender.com";
const DEFAULT_LAN_URL = "http://192.168.8.105:8000";

function generateUUID() {
  if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
    return crypto.randomUUID();
  }
  return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, function(c) {
    const r = Math.random() * 16 | 0;
    const v = c === "x" ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}

// DOM Elements Cache
const el = {
  serverPulse: document.getElementById("serverPulse"),
  headerModeBadge: document.getElementById("headerModeBadge"),
  headerPingBadge: document.getElementById("headerPingBadge"),
  backendStatusTag: document.getElementById("backendStatusTag"),
  backendUrlInput: document.getElementById("backendUrlInput"),
  btnTestBackend: document.getElementById("btnTestBackend"),
  presetLocalHost: document.getElementById("presetLocalHost"),
  presetRender: document.getElementById("presetRender"),
  
  btnRefreshStatus: document.getElementById("btnRefreshStatus"),
  statusCooldown: document.getElementById("statusCooldown"),
  statusConfigured: document.getElementById("statusConfigured"),
  statusMaskedUserKey: document.getElementById("statusMaskedUserKey"),
  statusMaskedApiKey: document.getElementById("statusMaskedApiKey"),
  authErrorAlert: document.getElementById("authErrorAlert"),
  authErrorMessage: document.getElementById("authErrorMessage"),

  inputUserKey: document.getElementById("inputUserKey"),
  flagKeyLen: document.getElementById("flagKeyLen"),
  flagKeyEy: document.getElementById("flagKeyEy"),
  btnPasteUserKey: document.getElementById("btnPasteUserKey"),
  btnClearUserKey: document.getElementById("btnClearUserKey"),
  btnToggleUserKeyVisibility: document.getElementById("btnToggleUserKeyVisibility"),
  inputApiKey: document.getElementById("inputApiKey"),
  btnResetDefaultApiKey: document.getElementById("btnResetDefaultApiKey"),
  inputBaseUrl: document.getElementById("inputBaseUrl"),
  modeRadioLive: document.getElementById("modeRadioLive"),
  modeRadioDemo: document.getElementById("modeRadioDemo"),

  btnPushConfig: document.getElementById("btnPushConfig"),
  btnTestServerConn: document.getElementById("btnTestServerConn"),
  btnDirectPhoneTest: document.getElementById("btnDirectPhoneTest"),
  btnCheckPortfolio: document.getElementById("btnCheckPortfolio"),
  statEquity: document.getElementById("statEquity"),
  statCash: document.getElementById("statCash"),
  statPositions: document.getElementById("statPositions"),
  statRealizedPnl: document.getElementById("statRealizedPnl"),

  logConsole: document.getElementById("logConsole"),
  btnClearLog: document.getElementById("btnClearLog"),
  btnCopyLog: document.getElementById("btnCopyLog")
};

// Android Native Bridge Wrapper
const Bridge = {
  hasBridge: typeof window.AndroidBridge !== "undefined",

  getPreference(key, defaultVal) {
    if (this.hasBridge) {
      try { return window.AndroidBridge.getPreference(key, defaultVal); } catch(e){}
    }
    return localStorage.getItem(key) || defaultVal;
  },

  savePreference(key, val) {
    if (this.hasBridge) {
      try { window.AndroidBridge.savePreference(key, val); } catch(e){}
    }
    try { localStorage.setItem(key, val); } catch(e){}
  },

  async getClipboard() {
    if (this.hasBridge) {
      try {
        const text = window.AndroidBridge.getClipboardText();
        if (text) return text;
      } catch(e){}
    }
    if (navigator.clipboard && navigator.clipboard.readText) {
      try { return await navigator.clipboard.readText(); } catch(e){}
    }
    return "";
  },

  setClipboard(text) {
    if (this.hasBridge) {
      try { window.AndroidBridge.setClipboardText(text); return; } catch(e){}
    }
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text);
    }
  },

  vibrate(ms = 40) {
    if (this.hasBridge) {
      try { window.AndroidBridge.vibrate(ms); } catch(e){}
    } else if (navigator.vibrate) {
      navigator.vibrate(ms);
    }
  },

  toast(msg) {
    if (this.hasBridge) {
      try { window.AndroidBridge.showToast(msg); return; } catch(e){}
    }
    console.log("[Toast]", msg);
  },

  async request(method, url, headers = {}, body = null) {
    // If native bridge is available, use it to bypass mobile browser CORS entirely
    if (this.hasBridge) {
      try {
        const headersStr = JSON.stringify(headers);
        const bodyStr = body ? (typeof body === "string" ? body : JSON.stringify(body)) : "";
        const rawRes = window.AndroidBridge.nativeHttpRequest(method, url, headersStr, bodyStr);
        return JSON.parse(rawRes);
      } catch(e) {
        console.warn("Native HTTP failed, falling back to fetch:", e);
      }
    }

    // Standard fetch fallback
    try {
      const opts = {
        method,
        headers: { ...headers }
      };
      if (body) {
        opts.body = typeof body === "string" ? body : JSON.stringify(body);
        if (!opts.headers["Content-Type"]) opts.headers["Content-Type"] = "application/json";
      }
      const resp = await fetch(url, opts);
      const text = await resp.text();
      return {
        statusCode: resp.status,
        isSuccess: resp.ok,
        body: text
      };
    } catch(err) {
      return {
        statusCode: 0,
        isSuccess: false,
        error: err.message,
        body: JSON.stringify({ error: err.message })
      };
    }
  }
};

// Logging Utility
function log(msg, type = "info") {
  const ts = new Date().toTimeString().split(" ")[0];
  const prefix = type === "error" ? "❌ " : (type === "success" ? "✅ " : "ℹ️ ");
  const line = `[${ts}] ${prefix}${msg}\n`;
  el.logConsole.textContent = line + el.logConsole.textContent;
}

// Key Sanitizer
function sanitizeKey(raw) {
  if (!raw) return "";
  let clean = raw.trim();
  // Strip surrounding quotes
  if ((clean.startsWith('"') && clean.endsWith('"')) || (clean.startsWith("'") && clean.endsWith("'"))) {
    clean = clean.substring(1, clean.length - 1).trim();
  }
  return clean;
}

// Update Token Diagnostic Flags
function updateKeyFlags() {
  const key = sanitizeKey(el.inputUserKey.value);
  const len = key.length;
  el.flagKeyLen.textContent = `${len} chars`;
  
  if (len > 200) {
    el.flagKeyLen.className = "flag-pill active";
  } else if (len > 0) {
    el.flagKeyLen.className = "flag-pill";
  } else {
    el.flagKeyLen.className = "flag-pill";
  }

  const isEy = key.startsWith("ey");
  el.flagKeyEy.textContent = isEy ? "JWT: Yes (ey...)" : (len > 0 ? "JWT: No" : "JWT? No");
  el.flagKeyEy.className = isEy ? "flag-pill active" : "flag-pill";
}

// Load Preferences on Boot
function loadSettings() {
  let savedUrl = Bridge.getPreference("backend_url", "");
  if (!savedUrl || savedUrl.includes("10.0.2.2")) {
    savedUrl = DEFAULT_RENDER_URL;
    Bridge.savePreference("backend_url", DEFAULT_RENDER_URL);
  }
  el.backendUrlInput.value = savedUrl;

  const savedApiKey = Bridge.getPreference("etoro_api_key", DEFAULT_API_KEY);
  el.inputApiKey.value = savedApiKey || DEFAULT_API_KEY;

  const savedUserKey = Bridge.getPreference("etoro_user_key", "");
  el.inputUserKey.value = savedUserKey;

  const savedBaseUrl = Bridge.getPreference("etoro_base_url", DEFAULT_BASE_URL);
  el.inputBaseUrl.value = savedBaseUrl || DEFAULT_BASE_URL;

  const savedMode = Bridge.getPreference("execution_mode", "live");
  if (savedMode === "demo") {
    el.modeRadioDemo.checked = true;
    updateModeBadge("demo");
  } else {
    el.modeRadioLive.checked = true;
    updateModeBadge("live");
  }

  updateKeyFlags();
  if (savedUrl) {
    testBackendConnection(true);
  }
}

function updateModeBadge(mode) {
  if (mode === "demo") {
    el.headerModeBadge.textContent = "DEMO";
    el.headerModeBadge.className = "badge badge-mode demo";
  } else {
    el.headerModeBadge.textContent = "LIVE";
    el.headerModeBadge.className = "badge badge-mode";
  }
}

// Backend Server Ping & Sync
async function testBackendConnection(silent = false) {
  let url = el.backendUrlInput.value.trim().replace(/\/+$/, "");
  if (!url) {
    if (!silent) log("Please enter a backend server URL.", "error");
    return;
  }
  Bridge.savePreference("backend_url", url);

  if (!silent) log(`Testing backend ping: ${url}/api/config`);
  const t0 = performance.now();
  
  const res = await Bridge.request("GET", `${url}/api/config`);
  const elapsed = Math.round(performance.now() - t0);

  if (res.isSuccess) {
    el.serverPulse.className = "pulse-dot online";
    el.backendStatusTag.textContent = "ONLINE";
    el.backendStatusTag.className = "status-indicator online";
    el.headerPingBadge.textContent = `${elapsed} ms`;
    Bridge.vibrate(20);

    try {
      const cfg = JSON.parse(res.body);
      if (cfg.execution_mode) {
        updateModeBadge(cfg.execution_mode);
        if (cfg.execution_mode === "demo") el.modeRadioDemo.checked = true;
        else el.modeRadioLive.checked = true;
      }
      if (!silent) log(`Connected! Latency: ${elapsed}ms. Mode: ${cfg.execution_mode?.toUpperCase()}`, "success");
    } catch(e) {
      if (!silent) log(`Connected! Latency: ${elapsed}ms`, "success");
    }

    // Automatically refresh eToro status
    await refreshServerEtoroStatus();
  } else {
    el.serverPulse.className = "pulse-dot";
    el.backendStatusTag.textContent = "OFFLINE";
    el.backendStatusTag.className = "status-indicator";
    el.headerPingBadge.textContent = "ERR";
    Bridge.vibrate(80);
    if (!silent) log(`Failed to reach backend (${res.statusCode}): ${res.error || res.body}`, "error");
  }
}

// Refresh Server eToro Status
async function refreshServerEtoroStatus() {
  const url = el.backendUrlInput.value.trim().replace(/\/+$/, "");
  if (!url) return;

  const res = await Bridge.request("GET", `${url}/api/etoro/status`);
  if (res.isSuccess) {
    try {
      const data = JSON.parse(res.body);
      
      // Cooldown
      if (data.auth_cooldown) {
        el.statusCooldown.textContent = `⚠️ LOCKED (${data.auth_cooldown_remaining_sec}s)`;
        el.statusCooldown.style.color = "var(--color-danger)";
      } else {
        el.statusCooldown.textContent = "CLEAR";
        el.statusCooldown.style.color = "var(--color-emerald)";
      }

      // Configured
      el.statusConfigured.textContent = data.is_configured ? "YES" : "NO";
      el.statusConfigured.style.color = data.is_configured ? "var(--color-emerald)" : "var(--color-danger)";

      // Masked keys
      el.statusMaskedUserKey.textContent = data.user_key_masked || "none";
      el.statusMaskedApiKey.textContent = data.api_key_masked || "none";

      // Last auth error
      if (data.last_auth_error) {
        el.authErrorAlert.classList.remove("hidden");
        el.authErrorMessage.textContent = data.last_auth_error;
      } else {
        el.authErrorAlert.classList.add("hidden");
      }

      if (data.execution_mode) {
        updateModeBadge(data.execution_mode);
      }
    } catch(e) {
      console.warn("Failed to parse status:", e);
    }
  }
}

// Push Keys & Reauthorize on Server
async function pushConfigToServer() {
  const url = el.backendUrlInput.value.trim().replace(/\/+$/, "");
  if (!url) {
    log("Backend URL missing.", "error");
    Bridge.toast("Please enter Server Base URL first");
    return;
  }

  const rawUserKey = el.inputUserKey.value;
  const userKey = sanitizeKey(rawUserKey);
  const apiKey = el.inputApiKey.value.trim() || DEFAULT_API_KEY;
  const baseUrl = el.inputBaseUrl.value.trim() || DEFAULT_BASE_URL;
  const mode = el.modeRadioLive.checked ? "live" : "demo";

  if (!userKey) {
    log("Please paste your eToro x-user-key first.", "error");
    Bridge.toast("x-user-key is required!");
    Bridge.vibrate(100);
    return;
  }

  // Auto-clean input value
  el.inputUserKey.value = userKey;
  updateKeyFlags();

  // Save to local preferences
  Bridge.savePreference("etoro_user_key", userKey);
  Bridge.savePreference("etoro_api_key", apiKey);
  Bridge.savePreference("etoro_base_url", baseUrl);
  Bridge.savePreference("execution_mode", mode);

  log(`Pushing new credentials to ${url}/api/config (Mode: ${mode.toUpperCase()})...`);
  el.btnPushConfig.textContent = "⏳ PUSHING KEYS...";

  const payload = {
    etoro_api_key: apiKey,
    etoro_user_key: userKey,
    etoro_base_url: baseUrl,
    execution_mode: mode,
    simulation_mode: (mode !== "live")
  };

  const res = await Bridge.request("POST", `${url}/api/config`, { "Content-Type": "application/json" }, payload);
  el.btnPushConfig.textContent = "⚡ PUSH & REAUTHORIZE ON SERVER";

  if (res.isSuccess) {
    Bridge.vibrate(50);
    Bridge.toast("Credentials successfully updated on server!");
    log("Server configuration updated and persisted to disk!", "success");
    await refreshServerEtoroStatus();
    
    // Automatically trigger test connection
    log("Automatically initiating live auth test...");
    await testEtoroServerConnection();
  } else {
    Bridge.vibrate(120);
    log(`Failed to update config (${res.statusCode}): ${res.error || res.body}`, "error");
    Bridge.toast("Server update failed!");
  }
}

// Test eToro Connection via Backend Server
async function testEtoroServerConnection() {
  const url = el.backendUrlInput.value.trim().replace(/\/+$/, "");
  if (!url) {
    log("Backend URL missing.", "error");
    return;
  }

  log(`Invoking ${url}/api/etoro/test_connection...`);
  el.btnTestServerConn.textContent = "🧪 TESTING...";

  const res = await Bridge.request("POST", `${url}/api/etoro/test_connection`);
  el.btnTestServerConn.textContent = "🧪 TEST LIVE AUTH VIA SERVER";

  if (res.isSuccess) {
    try {
      const data = JSON.parse(res.body);
      if (data.connected) {
        Bridge.vibrate([30, 50, 30]);
        Bridge.toast("eToro Handshake Verified (HTTP 200)!");
        log("🎉 SUCCESS: eToro Live API Connected & Authenticated (HTTP 200)!", "success");
      } else {
        Bridge.vibrate(100);
        log(`Auth Test Result (${data.status_code || 'ERR'}): ${data.message || 'Authentication rejected'}`, "error");
        if (data.detail) log(`Detail: ${data.detail}`, "error");
      }
    } catch(e) {
      log(`Raw Response: ${res.body}`, "info");
    }
    await refreshServerEtoroStatus();
  } else {
    Bridge.vibrate(100);
    log(`Endpoint failed (${res.statusCode}): ${res.error || res.body}`, "error");
  }
}

// Direct Mobile-to-eToro Ping
async function testDirectEtoroPing() {
  const baseUrl = el.inputBaseUrl.value.trim() || DEFAULT_BASE_URL;
  const userKey = sanitizeKey(el.inputUserKey.value);
  const apiKey = el.inputApiKey.value.trim() || DEFAULT_API_KEY;

  if (!userKey) {
    log("Direct ping requires x-user-key.", "error");
    Bridge.toast("Please paste x-user-key first");
    return;
  }

  log(`[Direct Phone Ping] Querying ${baseUrl}/api/v1/me...`);
  el.btnDirectPhoneTest.textContent = "🌐 TESTING DIRECT...";

  const headers = {
    "x-api-key": apiKey,
    "x-user-key": userKey,
    "x-request-id": generateUUID(),
    "Accept": "application/json"
  };

  const res = await Bridge.request("GET", `${baseUrl}/api/v1/me`, headers);
  el.btnDirectPhoneTest.textContent = "🌐 DIRECT PHONE-TO-ETORO PING";

  if (res.isSuccess) {
    Bridge.vibrate(40);
    Bridge.toast("Direct eToro connection succeeded!");
    log(`✅ Direct eToro Phone Auth SUCCESS (HTTP ${res.statusCode})!`, "success");
    try {
      const data = JSON.parse(res.body);
      log(`Account CID: ${data.cid || data.gcid || 'Verified'}. Username: ${data.username || data.name || 'Verified'}`);
    } catch(e){}
  } else {
    Bridge.vibrate(100);
    log(`❌ Direct Ping Failed (HTTP ${res.statusCode}): ${res.body || res.error}`, "error");
  }
}

// Check Portfolio Snapshot
async function checkPortfolioSnapshot() {
  const url = el.backendUrlInput.value.trim().replace(/\/+$/, "");
  if (!url) return;

  log(`Fetching portfolio snapshot from ${url}/api/portfolio...`);
  const res = await Bridge.request("GET", `${url}/api/portfolio`);
  if (res.isSuccess) {
    try {
      const data = JSON.parse(res.body);
      el.statEquity.textContent = `$${(data.equity || 0).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
      el.statCash.textContent = `$${(data.cash || 0).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
      const openPos = data.open_positions || data.positions || [];
      const posCount = Array.isArray(openPos) ? openPos.length : Object.keys(openPos).length;
      el.statPositions.textContent = posCount;
      const pnl = data.total_realized_pnl_usd || 0;
      el.statRealizedPnl.textContent = `${pnl >= 0 ? '+' : ''}$${pnl.toFixed(2)}`;
      el.statRealizedPnl.style.color = pnl >= 0 ? "var(--color-emerald)" : "var(--color-danger)";

      const posList = Array.isArray(openPos) ? openPos : Object.values(openPos);
      const listContainer = document.getElementById("positionsListContainer");
      if (listContainer && posList.length > 0) {
        listContainer.innerHTML = posList.map(p => {
          const upnl = p.unrealized_pnl_usd || 0;
          const upnlColor = upnl >= 0 ? "var(--color-emerald)" : "var(--color-danger)";
          return `
            <div style="display:flex; justify-content:space-between; align-items:center; background:rgba(255,255,255,0.05); padding:6px 10px; border-radius:6px; margin-bottom:5px; font-size:12px; border-left:3px solid var(--color-cyan);">
              <span style="font-weight:bold; color:var(--color-cyan);">${p.symbol} <span style="font-size:10px; opacity:0.8;">(${p.direction})</span></span>
              <span>$${(p.market_value_usd || 0).toFixed(2)}</span>
              <span style="color:${upnlColor}; font-weight:600;">${upnl >= 0 ? '+' : ''}$${upnl.toFixed(2)}</span>
            </div>
          `;
        }).join("");
      } else if (listContainer) {
        listContainer.innerHTML = "";
      }

      const symSummary = posList.map(p => p.symbol).join(", ");
      log(`Portfolio synced: Equity $${(data.equity||0).toFixed(2)}, Cash $${(data.cash||0).toFixed(2)}, Positions (${posCount}): ${symSummary || 'None'}`, "success");
    } catch(e) {
      log("Error parsing portfolio data", "error");
    }
  } else {
    log(`Failed to fetch portfolio (${res.statusCode})`, "error");
  }
}

// Event Listeners Setup
function initEventListeners() {
  // Test Backend Button
  el.btnTestBackend.addEventListener("click", () => testBackendConnection(false));

  // Preset Buttons
  el.presetLocalHost.addEventListener("click", () => {
    el.backendUrlInput.value = DEFAULT_LAN_URL;
    Bridge.toast("Set to Local PC LAN: " + DEFAULT_LAN_URL);
    testBackendConnection(false);
  });
  el.presetRender.addEventListener("click", () => {
    el.backendUrlInput.value = DEFAULT_RENDER_URL;
    Bridge.toast("Set to Render Cloud: " + DEFAULT_RENDER_URL);
    testBackendConnection(false);
  });

  // Refresh Status
  el.btnRefreshStatus.addEventListener("click", () => {
    refreshServerEtoroStatus();
    Bridge.vibrate(20);
  });

  // User Key Input Change & Sanitization
  el.inputUserKey.addEventListener("input", updateKeyFlags);

  // Paste User Key
  el.btnPasteUserKey.addEventListener("click", async () => {
    Bridge.vibrate(25);
    const clip = await Bridge.getClipboard();
    if (clip) {
      const clean = sanitizeKey(clip);
      el.inputUserKey.value = clean;
      updateKeyFlags();
      Bridge.toast(`Pasted ${clean.length} characters`);
      log(`Pasted user key (${clean.length} chars, JWT: ${clean.startsWith("ey") ? "YES" : "NO"})`);
    } else {
      Bridge.toast("Clipboard is empty");
    }
  });

  // Clear User Key
  el.btnClearUserKey.addEventListener("click", () => {
    el.inputUserKey.value = "";
    updateKeyFlags();
    Bridge.vibrate(15);
  });

  // Toggle Visibility
  el.btnToggleUserKeyVisibility.addEventListener("click", () => {
    if (el.inputUserKey.style.webkitTextSecurity === "disc") {
      el.inputUserKey.style.webkitTextSecurity = "none";
      el.btnToggleUserKeyVisibility.textContent = "HIDE";
    } else {
      el.inputUserKey.style.webkitTextSecurity = "disc";
      el.btnToggleUserKeyVisibility.textContent = "SHOW";
    }
  });

  // Reset Default App API Key
  el.btnResetDefaultApiKey.addEventListener("click", () => {
    el.inputApiKey.value = DEFAULT_API_KEY;
    Bridge.toast("Reset to default eToro public key");
  });

  // Mode Selection
  el.modeRadioLive.addEventListener("change", () => updateModeBadge("live"));
  el.modeRadioDemo.addEventListener("change", () => updateModeBadge("demo"));

  // Main Actions
  el.btnPushConfig.addEventListener("click", pushConfigToServer);
  el.btnTestServerConn.addEventListener("click", testEtoroServerConnection);
  el.btnDirectPhoneTest.addEventListener("click", testDirectEtoroPing);
  el.btnCheckPortfolio.addEventListener("click", checkPortfolioSnapshot);

  // Console Controls
  el.btnClearLog.addEventListener("click", () => {
    el.logConsole.textContent = "";
  });
  el.btnCopyLog.addEventListener("click", () => {
    Bridge.setClipboard(el.logConsole.textContent);
  });
}

// Initialize on DOM Ready
document.addEventListener("DOMContentLoaded", () => {
  loadSettings();
  initEventListeners();
  log("Companion controller active. Native Bridge: " + (Bridge.hasBridge ? "CONNECTED" : "WEB-FALLBACK"));
});
