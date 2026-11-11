@echo off
setlocal
echo ========================================================
echo  Opening Spotify Overlay in Standalone Window
echo  (Ideal for TikTok LIVE Studio "Window Capture")
echo ========================================================

rem Look for Chrome
if exist "C:\Program Files\Google\Chrome\Application\chrome.exe" (
    start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" --app=http://127.0.0.1:5055/ --window-size=620,165
    goto :done
)

rem Look for Edge (x86 or standard)
if exist "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" (
    start "" "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --app=http://127.0.0.1:5055/ --window-size=620,165
    goto :done
)
if exist "C:\Program Files\Microsoft\Edge\Application\msedge.exe" (
    start "" "C:\Program Files\Microsoft\Edge\Application\msedge.exe" --app=http://127.0.0.1:5055/ --window-size=620,165
    goto :done
)

rem Fallback to default browser
start http://127.0.0.1:5055/

:done
echo Overlay window launched!
echo In TikTok LIVE Studio: Add Source -^> Window Capture -^> Select this window.

