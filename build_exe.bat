@echo off
cd /d "%~dp0"
set PY=python
where py >nul 2>nul
if %errorlevel%==0 set PY=py -3
%PY% -m pip install -r requirements.txt pyinstaller
%PY% -m PyInstaller --onefile --noconsole --name KnightVsOgre --add-data "assets;assets" main.py
echo.
echo Pronto! O executavel esta em: dist\KnightVsOgre.exe
pause
