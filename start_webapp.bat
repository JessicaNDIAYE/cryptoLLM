@echo off
cd /d "%~dp0webapp"
npm install
npm run dev
pause