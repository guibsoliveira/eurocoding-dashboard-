@echo off
title Eurocoding Dashboard
cd /d %~dp0
echo.
echo  ============================================
echo    EUROCODING - Iniciando Interface...
echo  ============================================
echo.
echo  Acesse no navegador: http://localhost:8501
echo  Para fechar: pressione Ctrl+C nesta janela
echo.
py -m streamlit run app.py --server.port 8501
pause
