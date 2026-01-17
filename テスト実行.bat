@echo off
cd /d %~dp0

echo ==========================================
echo  社内LAN偽装テストを実行します
echo ==========================================
echo.

:: 新しい環境を使って実行
.\python_env\Scripts\python.exe simulation_test.py

pause