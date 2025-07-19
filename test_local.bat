@echo off
echo 🧪 === TEST LOCAL AVANT PUSH ===
echo.

REM Test de validation
python test_streamlit_cloud.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ TESTS OK - Vous pouvez pusher !
    echo 🚀 git add . && git commit -m "update" && git push
) else (
    echo.
    echo ❌ TESTS ÉCHOUÉS - Corrigez avant de pusher
    exit /b 1
)

pause
