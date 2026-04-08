import os
import sys
import asyncio
from pathlib import Path

# Adiciona o diretório backend ao sys.path para permitir a importação do pacote app
backend_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(backend_dir))

from app.services.cognitive_agents import run_cognitive_analysis

def main():
    print("==================================================")
    print("Iniciando Agentes de IA Cognitivos Distribuídos")
    print("==================================================")
    asyncio.run(run_cognitive_analysis())
    print("==================================================")

if __name__ == "__main__":
    main()
