@echo off
cd /d %~dp0
cmd /k "cd /d %~dp0\windows_env\Scripts & activate & cd /d %~dp0 & python app.py %*"
pause
