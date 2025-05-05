@echo off
echo QuickSnap を起動します...
python main.py
if %ERRORLEVEL% neq 0 (
    echo エラーが発生しました。
    echo Python がインストールされていることを確認してください。
    echo 必要なパッケージをインストールするには:
    echo   pip install -r requirements.txt
    pause
)