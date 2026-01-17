@echo off
cd /d %~dp0

echo ==========================================
echo  検索順位チェックツール（自動更新機能付き）
echo ==========================================
echo.

:: 1. まずアップデートを実行
.\python_env\Scripts\python.exe update.py

:: 2. ツール本体を起動
.\python_env\Scripts\python.exe -m streamlit run app.py --global.developmentMode=false

pause