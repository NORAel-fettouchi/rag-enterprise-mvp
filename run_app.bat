@echo off
REM Script de lancement RAG-Enterprise MVP
REM Lancer l'application Streamlit

echo.
echo ============================================================
echo          RAG-ENTERPRISE MVP - STREAMLIT LAUNCHER
echo ============================================================
echo.

REM Définir le répertoire du script comme répertoire courant
cd /d "%~dp0"

REM Lancer Streamlit
echo Lancement de l'application RAG...
echo.

C:\Users\pc\AppData\Local\Programs\Python\Python312\python.exe -m streamlit run streamlit_app.py

REM Si Streamlit s'arrête, afficher un message
echo.
echo L'application s'est arrêtée.
pause
