#!/bin/bash
set -e

echo "==> Configurando backend..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd ..

echo "==> Configurando frontend..."
cd frontend
npm ci
cd ..

echo "==> Setup completo!"
