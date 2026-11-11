import os
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CLOUDFLARED_EXE = ROOT / "cloudflared.exe"
DOWNLOAD_URL = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"

def ensure_cloudflared():
    if CLOUDFLARED_EXE.exists():
        return True

    print("========================================================")
    print(" TikTok LIVE Studio requires a public HTTPS link.")
    print(" Downloading Cloudflare Tunnel (one-time download ~35MB)...")
    print("========================================================")

    # Try curl first
    try:
        ret = subprocess.run(["curl.exe", "-L", "-o", str(CLOUDFLARED_EXE), DOWNLOAD_URL], check=True)
        if CLOUDFLARED_EXE.exists() and CLOUDFLARED_EXE.stat().st_size > 1000000:
            print("Download complete!\n")
            return True
    except Exception:
        pass

    # Fallback to urllib
    try:
        import urllib.request
        def progress(count, block_size, total_size):
            percent = int(count * block_size * 100 / total_size)
            sys.stdout.write(f"\rDownloading: {percent}%")
            sys.stdout.flush()
        urllib.request.urlretrieve(DOWNLOAD_URL, str(CLOUDFLARED_EXE), reporthook=progress)
        print("\nDownload complete!\n")
        return True
    except Exception as e:
        print(f"\nFailed to download cloudflared: {e}")
        return False

def main():
    if not ensure_cloudflared():
        print("\nCould not setup Cloudflare Tunnel.")
        print("Please check your internet connection or use Window Capture instead.")
        input("Press Enter to exit...")
        return

    print("\nStarting local Spotify Now Playing server...")
    app_proc = subprocess.Popen([sys.executable, str(ROOT / "app.py")])
    time.sleep(1.5)

    print("Starting secure tunnel for TikTok LIVE Studio...")
    tunnel_cmd = [str(CLOUDFLARED_EXE), "tunnel", "--url", "http://127.0.0.1:5055"]
    tunnel_proc = subprocess.Popen(
        tunnel_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace"
    )

    url_found = None
    url_pattern = re.compile(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com")

    start_time = time.time()
    try:
        for line in tunnel_proc.stdout:
            match = url_pattern.search(line)
            if match and not url_found:
                url_found = match.group(0)
                print("\n" + "=" * 62)
                print(" SUCCESS! HERE IS YOUR TIKTOK LIVE STUDIO LINK:")
                print(f" {url_found}")
                print("=" * 62)
                print("\nHOW TO USE IN TIKTOK LIVE STUDIO:")
                print("1. In TikTok LIVE Studio, click 'Add source'")
                print("2. Choose 'Link' (or 'Webpage' / 'Browser')")
                print(f"3. Paste this URL:  {url_found}")
                print("4. Set Width to 600, Height to 130")
                print("\nKeep this window OPEN while streaming.")
                print("Press Ctrl+C to stop.\n" + "-" * 62)
            elif not url_found and time.time() - start_time > 30:
                print("Still waiting for tunnel URL...")
                start_time = time.time()

        tunnel_proc.wait()
    except KeyboardInterrupt:
        print("\nStopping overlay and tunnel...")
    finally:
        tunnel_proc.terminate()
        app_proc.terminate()

if __name__ == "__main__":
    main()

