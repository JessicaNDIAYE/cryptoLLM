@echo off
chcp 65001 > nul
echo   InvestBuddy n8n - Demarrage Automatique


:: Demarrer n8n
echo [1/4] Demarrage de n8n...
docker-compose up -d n8n

:: Attendre que n8n soit ready (healthcheck)
echo [2/4] Attente du demarrage (30s)...
:wait_loop
timeout /t 5 /nobreak > nul
curl -s http://localhost:5678/healthz > nul 2>&1
if %errorlevel% neq 0 (
    echo     En attente...
    goto wait_loop
)
echo     n8n est pret!

:: Creer l'owner si pas encore fait
echo [3/4] Configuration du compte...
curl -s -X POST http://localhost:5678/rest/owner/setup ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"crypto.agentbuddy@gmail.com\",\"firstName\":\"InvestBuddy\",\"lastName\":\"Admin\",\"password\":\"InvestBuddy2024!\"}" > nul 2>&1

:: Importer le workflow via CLI
echo [4/4] Import du workflow...
docker exec investbuddy-n8n n8n import:workflow --input=/home/node/.n8n/workflows/working_workflow.json > nul 2>&1


echo   n8n est pret sur http://localhost:5678
echo.
echo   Email    : crypto.agentbuddy@gmail.com
echo   Password : InvestBuddy2024!
echo.
echo   Ouverture du navigateur...
start http://localhost:5678
