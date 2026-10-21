# eToro ReAuth Mobile Companion (Standalone APK)

A lightweight, standalone Android mobile application (`com.cockpit.etoroauth`) designed to reauthorize, configure, and monitor your eToro API keys and execution status directly from your phone.

---

## 📱 Features

1. **Backend Server Integration**:
   - Easily connect to your Cockpit server (Render cloud URL or local Wi-Fi IP).
   - Real-time latency and connection heartbeat indicator.
   - Presets for local emulator (`http://10.0.2.2:8000`) and quick URL pasting.

2. **Server Auth & Cooldown Diagnostics**:
   - Displays real-time eToro lockout status and cooldown countdown timer.
   - Displays masked key fingerprints stored on the server.
   - Highlights any upstream auth error messages directly on your mobile screen.

3. **1-Tap Key Reauthorization & Sanitization**:
   - **`x-user-key` (Personal Secret Token)**:
     - 1-Tap **"📋 PASTE FROM CLIPBOARD"** button.
     - Automatically strips surrounding quotation marks (`"` / `'`) and extraneous whitespace.
     - Live token inspection: character counter and JWT verification (`ey...`).
     - Password visibility toggle (SHOW / HIDE).
   - **`x-api-key` (Application Key)**:
     - Pre-filled with the official eToro public application key (`sdgdskldFPLGfjHn1421dgnlxdGTbngdflg6290bRjslfihsjhSDsdgGHH25hjf`).
     - "Reset to Default" button.
   - **Mode Selection**: Switch between **LIVE** (real execution) and **DEMO** (virtual simulation) with 1 tap.

4. **Multi-Level Verification & Execution**:
   - **⚡ PUSH & REAUTHORIZE ON SERVER**: Sends new keys to `/api/config` and updates your running backend without restarting.
   - **🧪 TEST LIVE AUTH VIA SERVER**: Invokes `/api/etoro/test_connection` to confirm the backend handshake is 100% authenticated.
   - **🌐 DIRECT PHONE-TO-ETORO PING**: Directly queries eToro's Public API (`/api/v1/me`) from your phone to verify reachability.
   - **💼 PORTFOLIO SNAPSHOT**: Audits live account equity, available cash, and active open positions.

5. **Offline & Battery Efficient**:
   - Total APK size is under **30 KB**!
   - Hardware-accelerated UI rendered from offline local assets.
   - Native Android bridge for device vibration, toast notifications, and persistent configuration storage.

---

## 🚀 How to Install on Your Phone

### Option A: Via Local Wi-Fi (Fastest)
1. Run the local delivery server from your PC:
   ```bash
   python serve_apk.py
   ```
2. Your terminal will display a Wi-Fi link (e.g. `http://192.168.1.xxx:8080`).
3. Open this link in your phone's browser (Chrome, Samsung Internet, etc.).
4. Tap **Download APK**.
5. When prompted by Android, allow "Install unknown apps" for your browser and tap **Install**.

### Option B: Via USB Cable / ADB
If your phone is plugged in with USB debugging enabled:
```bash
adb install -r f:\Antigravity\sotck_predict\etoro-authorizer.apk
```

### Option C: Cloud Drive / Messaging
Transfer `f:\Antigravity\sotck_predict\etoro-authorizer.apk` to your phone via Google Drive, WhatsApp, Telegram, or email, and tap to install.

---

## 🛠 Rebuilding the APK

If you make modifications to the HTML, CSS, JavaScript, or Java bridge:
```powershell
# In PowerShell:
cd f:\Antigravity\sotck_predict\etoro_auth_app
.\build_apk.ps1

# Or with Python:
python build_apk.py
```
The script will compile resources, generate DEX, align, sign with the debug keystore, and output the refreshed `etoro-authorizer.apk` in the project root.
