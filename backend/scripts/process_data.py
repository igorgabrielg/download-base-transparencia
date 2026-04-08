import os
import sys
from pathlib import Path

# Adiciona o diretório backend ao sys.path para permitir a importação do pacote app
backend_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(backend_dir))

from app.services.config_service import load_config
from app.services.normalizer import Normalizer
from app.services.enricher import Enricher

def main():
    print("==================================================")
    print("Iniciando Pipeline de Normalização e Enriquecimento")
    print("==================================================")
    
    cfg = load_config()
    data_dir = cfg.get("diretorio_saida", str(backend_dir / "data"))
    print(f"Diretório de dados ativo: {data_dir}")
    
    # 1. Normalização dos dados
    normalizer = Normalizer(data_dir=data_dir)
    normalizer.process()
    
    print("\n--------------------------------------------------")
    
    # 2. Enriquecimento dos dados
    enricher = Enricher(data_dir=data_dir)
    enricher.process()
    
    print("==================================================")
    print("Pipeline finalizado com sucesso!")
    print("==================================================")

if __name__ == "__main__":
    main()
