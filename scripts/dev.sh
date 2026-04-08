#!/bin/bash
set -e

echo "==> Iniciando backend (uvicorn)..."
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

echo "==> Iniciando frontend (vite)..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null" EXIT

echo "==> Backend: http://localhost:8000 | Frontend: http://localhost:5173"
wait
