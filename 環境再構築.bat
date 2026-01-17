@echo off
cd /d %~dp0

echo ==========================================
echo  環境の完全修復を開始します...
echo ==========================================
echo.

:: 1. 壊れたフォルダがあれば削除
if exist "python_env" (
    echo 古い python_env を削除しています...
    rmdir /s /q "python_env"
)

:: 2. 新しい仮想環境を作成（標準的な構成で作ります）
echo.
echo 新しい python_env を作成中...
python -m venv python_env

:: 3. 必要な部品（ライブラリ）をインストール
echo.
echo 必要な部品をインストールしています...
if exist "python_env\Scripts\pip.exe" (
    .\python_env\Scripts\pip.exe install -r requirements.txt
    echo.
    echo ✅ 修復が完了しました！
) else (
    echo.
    echo ❌ エラー：Pythonがインストールされていないか、作成に失敗しました。
)

pause