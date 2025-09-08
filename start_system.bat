@echo off
echo 🚀 Starting Quantum-Enhanced AI Logistics Engine
echo ================================================

echo.
echo 🐍 Starting Python backend...
start "Python Backend" cmd /k "python solver_simple.py"

echo.
echo ⏳ Waiting for Python backend to start...
timeout /t 5 /nobreak > nul

echo.
echo 🌐 Starting Node.js frontend...
start "Node.js Frontend" cmd /k "node server.js"

echo.
echo ⏳ Waiting for frontend to start...
timeout /t 3 /nobreak > nul

echo.
echo ✅ System started!
echo 📱 Frontend: http://localhost:3000
echo 🔧 Backend: http://localhost:5000
echo.
echo Press any key to open the application...
pause > nul

start http://localhost:3000

