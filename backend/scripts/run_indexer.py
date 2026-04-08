import os
import sys
import asyncio
import logging
from pathlib import Path

# Adiciona o diretório backend ao sys.path para permitir a importação do pacote app
backend_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(backend_dir))

from app.services.vector_store import run_vector_indexing

def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    print("==================================================")
    print("Iniciando Pipeline de Indexação Vetorial (ChromaDB)")
    print("==================================================")
    asyncio.run(run_vector_indexing())
    print("==================================================")

if __name__ == "__main__":
    main()
