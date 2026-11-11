# Spotify Now Playing — Minimal Windows Overlay

A free local overlay for Windows Spotify Desktop. It reads the active Windows media session (SMTC), not the Spotify Web API. It does not require Spotify Premium, a Spotify Developer app, Client ID, or Client Secret.

## Requirements
- Windows 10 or Windows 11
- Spotify Windows desktop app
- Python 3.10–3.12 recommended (64-bit)
- Internet connection for the first-time Python package installation only

## Install
1. Install Python from https://www.python.org/downloads/windows/
2. During setup, enable **Add Python to PATH**.
3. Extract this ZIP to a normal folder (not inside the ZIP preview).
4. Double-click `install.bat`.
5. When installation finishes, double-click `start.bat`.
6. Keep the black terminal window open while streaming.
7. Open `http://127.0.0.1:5055/` in your browser to preview the overlay.

## TikTok LIVE Studio Setup

TikTok LIVE Studio blocks `127.0.0.1` and `localhost` in its "Link" source for security reasons, and only accepts public `https://` URLs. 

You have **two easy ways** to use this overlay in TikTok LIVE Studio:

---

### Option 1: Use TikTok "Link" Source with Free Cloudflare Tunnel (Recommended)
This gives you a real `https://` URL that TikTok LIVE Studio accepts directly into its Link source.
1. Make sure you ran `install.bat` once.
2. Double-click **`start_tiktok_link.bat`**.
3. It will generate a secure public link like:
   `https://random-words.trycloudflare.com`
4. In TikTok LIVE Studio:
   - Click **Add source** -> **Link** (or **Webpage / Browser**).
   - Paste the `https://...` link shown in the terminal.
   - Set width to **600** and height to **130**.
5. Keep the terminal window open while streaming.

---

### Option 2: Use "Window Capture" (No Internet/Tunnel Required)
If you prefer not to use an external link:
1. Double-click `start.bat`.
2. Double-click **`open_overlay_window.bat`** (opens a clean, borderless widget window).
3. In TikTok LIVE Studio:
   - Click **Add source** -> **Window Capture**.
   - Select the **Spotify Now Playing** window.
   - Position and resize it wherever you want on the stream.

---

### Option 3: Via OBS Virtual Camera (Optional)
If you already use OBS Studio:
1. In OBS, add a **Browser Source** pointing to `http://127.0.0.1:5055/` (OBS supports local URLs natively).
2. Click **Start Virtual Camera** in OBS.
3. In TikTok LIVE Studio, add a **Camera** source and pick **OBS Virtual Camera**.

## How it works
Windows exposes metadata from supported media apps through Global System Media Transport Controls. This app polls the current Windows media session and serves a local HTML overlay. The active Windows media session may belong to another app if it was used more recently; close/pause other media apps while testing.

## Troubleshooting
- **"Nothing playing"**: Open Spotify Desktop, play a song for 10 seconds, and make sure it is not paused. Close other media players and restart `start.bat`.
- **No album art**: Some tracks or Windows sessions do not expose a thumbnail. The song title and artist can still work.
- **Python command not found**: Reinstall Python and tick "Add Python to PATH", then reopen CMD.
- **Package install error**: Use 64-bit Python 3.10–3.12 and run `install.bat` again.
- **Blank Browser source**: First check `http://127.0.0.1:5055/` in Chrome/Edge. If it works there, refresh the LIVE Studio source.
- **No session detected**: The app relies on Windows media-session metadata. It cannot guarantee Spotify will expose it on every Windows/device configuration.

## Privacy
The server binds only to `127.0.0.1` (your own PC). It does not upload song metadata or album art to a remote server. Do not change the host to `0.0.0.0` unless you understand the security implications.
