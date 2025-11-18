@echo off
setlocal

set "config=%~1"
if not defined config set "config=main.toml"

for %%I in ("%config%") do set "config_name=%%~nI"
if not defined config_name set "config_name=main"

if not exist "logs" mkdir "logs"
set "logPath=logs\%config_name%.log"

:home
"%~dp0frps.exe" -c "%config%" >> "%logPath%" 2>&1
goto home
