import os
import sys
import asyncio
from pathlib import Path

# Adiciona o diretório backend ao sys.path para permitir a importação do pacote app
backend_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(backend_dir))

from app.services.synthesizer import run_cognitive_synthesis

def main():
    print("==================================================")
    print("Iniciando Agente Redator (Síntese e Consolidação)")
    print("==================================================")
    asyncio.run(run_cognitive_synthesis())
    print("==================================================")

if __name__ == "__main__":
    main()
