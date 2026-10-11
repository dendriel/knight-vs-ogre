@echo off
cd /d "%~dp0"
set PY=python
where py >nul 2>nul
if %errorlevel%==0 set PY=py -3
echo Instalando dependencias (so na primeira vez)...
%PY% -m pip install -r requirements.txt
echo Iniciando o jogo...
%PY% main.py
pause
