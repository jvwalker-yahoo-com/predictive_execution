package com.cockpit.etoroauth;

import android.content.ClipData;
import android.content.ClipboardManager;
import android.content.Context;
import android.content.SharedPreferences;
import android.os.Build;
import android.os.VibrationEffect;
import android.os.Vibrator;
import android.webkit.JavascriptInterface;
import android.widget.Toast;

import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.util.Iterator;

public class WebAppInterface {
    private final Context mContext;
    private final SharedPreferences mPrefs;
    private static final String PREFS_NAME = "eToroAuthPrefs";

    public WebAppInterface(Context context) {
        this.mContext = context;
        this.mPrefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE);
    }

    @JavascriptInterface
    public String getClipboardText() {
        try {
            ClipboardManager clipboard = (ClipboardManager) mContext.getSystemService(Context.CLIPBOARD_SERVICE);
            if (clipboard != null && clipboard.hasPrimaryClip()) {
                ClipData clip = clipboard.getPrimaryClip();
                if (clip != null && clip.getItemCount() > 0) {
                    CharSequence text = clip.getItemAt(0).getText();
                    if (text != null) {
                        return text.toString().trim();
                    }
                }
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
        return "";
    }

    @JavascriptInterface
    public void setClipboardText(String text) {
        try {
            ClipboardManager clipboard = (ClipboardManager) mContext.getSystemService(Context.CLIPBOARD_SERVICE);
            if (clipboard != null) {
                ClipData clip = ClipData.newPlainText("eToro Auth", text);
                clipboard.setPrimaryClip(clip);
                showToast("Copied to clipboard");
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @JavascriptInterface
    public void savePreference(String key, String value) {
        try {
            mPrefs.edit().putString(key, value).apply();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @JavascriptInterface
    public String getPreference(String key, String defaultValue) {
        try {
            return mPrefs.getString(key, defaultValue);
        } catch (Exception e) {
            return defaultValue;
        }
    }

    @JavascriptInterface
    public void vibrate(long milliseconds) {
        try {
            Vibrator v = (Vibrator) mContext.getSystemService(Context.VIBRATOR_SERVICE);
            if (v != null) {
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                    v.vibrate(VibrationEffect.createOneShot(milliseconds, VibrationEffect.DEFAULT_AMPLITUDE));
                } else {
                    v.vibrate(milliseconds);
                }
            }
        } catch (Exception ignored) {}
    }

    @JavascriptInterface
    public void showToast(final String message) {
        try {
            if (mContext instanceof MainActivity) {
                ((MainActivity) mContext).runOnUiThread(new Runnable() {
                    @Override
                    public void run() {
                        Toast.makeText(mContext, message, Toast.LENGTH_SHORT).show();
                    }
                });
            }
        } catch (Exception ignored) {}
    }

    @JavascriptInterface
    public String nativeHttpRequest(String method, String urlStr, String headersJson, String bodyStr) {
        JSONObject result = new JSONObject();
        HttpURLConnection conn = null;
        try {
            URL url = new URL(urlStr);
            conn = (HttpURLConnection) url.openConnection();
            conn.setRequestMethod(method.toUpperCase());
            conn.setConnectTimeout(12000);
            conn.setReadTimeout(15000);
            conn.setDoInput(true);

            if (headersJson != null && !headersJson.isEmpty()) {
                JSONObject headers = new JSONObject(headersJson);
                Iterator<String> keys = headers.keys();
                while (keys.hasNext()) {
                    String k = keys.next();
                    conn.setRequestProperty(k, headers.getString(k));
                }
            }

            if (bodyStr != null && !bodyStr.isEmpty() && ("POST".equalsIgnoreCase(method) || "PUT".equalsIgnoreCase(method))) {
                conn.setDoOutput(true);
                try (OutputStream os = conn.getOutputStream()) {
                    byte[] input = bodyStr.getBytes(StandardCharsets.UTF_8);
                    os.write(input, 0, input.length);
                }
            }

            int statusCode = conn.getResponseCode();
            result.put("statusCode", statusCode);
            result.put("isSuccess", statusCode >= 200 && statusCode < 300);

            InputStream is = (statusCode >= 200 && statusCode < 400) ? conn.getInputStream() : conn.getErrorStream();
            if (is != null) {
                BufferedReader reader = new BufferedReader(new InputStreamReader(is, StandardCharsets.UTF_8));
                StringBuilder response = new StringBuilder();
                String line;
                while ((line = reader.readLine()) != null) {
                    response.append(line).append("\n");
                }
                reader.close();
                result.put("body", response.toString().trim());
            } else {
                result.put("body", "");
            }
        } catch (Exception e) {
            try {
                result.put("statusCode", 0);
                result.put("isSuccess", false);
                result.put("error", e.getMessage());
                result.put("body", "{\"error\": \"" + e.toString().replace("\"", "\\\"") + "\"}");
            } catch (Exception ignored) {}
        } finally {
            if (conn != null) {
                conn.disconnect();
            }
        }
        return result.toString();
    }
}
