@echo off
cd /d %~dp0

:: --- 1. 自動アップデート機能 ---
echo ---------------------------------------
echo  最新のコードを取得しています...
echo ---------------------------------------
git pull origin main
:: ※ Gitを入れていない場合はエラーになりますが、無視して起動します

:: --- 2. 仮想環境の有効化 ---
call venv\Scripts\activate

:: --- 3. APIサーバーを別画面で起動 ---
echo ---------------------------------------
echo  司令塔サーバー(API)を起動します...
echo ---------------------------------------
:: "start" を使うと、新しい黒い画面を開いて並列で動かせます
start "GRC_API_SERVER" uvicorn manager.server:app --host 0.0.0.0 --port 8000

:: サーバーが立ち上がるまで5秒待つ
timeout /t 5 /nobreak >nul

:: --- 4. 入力画面(Streamlit)を起動 ---
echo ---------------------------------------
echo  入力画面(Streamlit)を起動します...
echo ---------------------------------------
streamlit run manager/app.py

pause