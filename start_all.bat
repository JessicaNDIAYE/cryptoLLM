@echo off
echo ========================================
echo   InvestBuddy - Demarrage des services
echo ========================================
echo.

echo [1/4] Demarrage de l'API Prediction (port 8080)...
start "InvestBuddy - API Prediction" cmd /k "cd /d %~dp0serving && python api.py"
timeout /t 3 /nobreak > nul

echo [2/4] Demarrage de l'API Agent RAG (port 4000)...
start "InvestBuddy - API Agent" cmd /k "cd /d %~dp0agent && python main.py"
timeout /t 3 /nobreak > nul

echo [3/4] Demarrage du Frontend React (port 5173)...
start "InvestBuddy - Webapp" cmd /k "cd /d %~dp0webapp && npm run dev"
timeout /t 5 /nobreak > nul

echo [4/4] Demarrage d'Evidently Monitoring (port 8082)...
start "InvestBuddy - Evidently" cmd /k "cd /d %~dp0reporting && python project.py"

echo.
echo ========================================
echo   Tous les services sont demarres !
echo ========================================
echo.
echo   - API Prediction : http://localhost:8080/docs
echo   - API Agent      : http://localhost:4000/docs
echo   - Webapp         : http://localhost:5173
echo   - Evidently      : http://localhost:8082
echo.
echo   Appuyez sur une touche pour ouvrir le navigateur...
pause > nul

start http://localhost:5173