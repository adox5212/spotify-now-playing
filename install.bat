@echo off
cd /d "%~dp0"
py -m pip install --upgrade pip
py -m pip install -r requirements.txt
echo.
echo Installation finished. If there were no errors, run start.bat
pause
