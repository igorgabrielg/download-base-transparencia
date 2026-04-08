import os
import sys
import pandas as pd
from pathlib import Path

# Adiciona o diretório backend ao sys.path para permitir a importação do pacote app
backend_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(backend_dir))

from app.config import settings
from app.services.config_service import load_config

def generate_mock_receitas():
    # Estrutura de dados mockados realistas, simulando strings e formatos inconsistentes da API
    data = [
        {
            "anoMes": "202401",
            "codigoOrgaoSuperior": "30000",
            "nomeOrgaoSuperior": "Ministério da Justiça e Segurança Pública",
            "codigoOrgao": "30101",
            "nomeOrgao": "Departamento de Polícia Federal",
            "codigoUG": "200331",
            "nomeUG": "SUPERINTENDENCIA REGIONAL DA PF NO PARA",
            "orcamentoAtualizado": "R$ 1.500.000,00",
            "receitaRealizada": "1250000.50"
        },
        {
            "anoMes": 202402,
            "codigoOrgaoSuperior": "26000",
            "nomeOrgaoSuperior": "Ministério da Educação",
            "codigoOrgao": "26237",
            "nomeOrgao": "Universidade Federal de Juiz de Fora",
            "codigoUG": "153061",
            "nomeUG": "UNIVERSIDADE FEDERAL DE JUIZ DE FORA",
            "orcamentoAtualizado": "500000,00",
            "receitaRealizada": "R$ 480.000,75"
        },
        {
            "anoMes": "202403",
            "codigoOrgaoSuperior": "52000",
            "nomeOrgaoSuperior": "Ministério da Defesa",
            "codigoOrgao": "52111",
            "nomeOrgao": "Comando da Aeronáutica",
            "codigoUG": "120195",
            "nomeUG": "CENTRO DE AQUISICOES ESPECIFICAS",
            "orcamentoAtualizado": "2000000.00",
            "receitaRealizada": "2100000,00"
        },
        {
            "anoMes": "202501",
            "codigoOrgaoSuperior": "26000",
            "nomeOrgaoSuperior": "Ministério da Educação",
            "codigoOrgao": "26443",
            "nomeOrgao": "Empresa Brasileira de Serviços Hospitalares",
            "codigoUG": "155013",
            "nomeUG": "HOSPITAL UNIVERSITARIO ONOFRE LOPES",
            "orcamentoAtualizado": "R$ 750.000,00",
            "receitaRealizada": "700000"
        }
    ]

    cfg = load_config()
    data_dir = Path(cfg.get("diretorio_saida", str(backend_dir / "data")))
    data_dir.mkdir(parents=True, exist_ok=True)
    
    df = pd.DataFrame(data)
    
    # Gerar arquivos separados para cada anoMes para simular o download do Portal
    for period in df["anoMes"].unique():
        period_str = str(period)
        ano = period_str[:4]
        mes = period_str[4:]
        
        # Filtra os dados daquele periodo
        df_period = df[df["anoMes"] == period]
        
        filename = data_dir / f"receitas_{ano}_{mes}.csv"
        df_period.to_csv(filename, index=False)
        print(f"Gerado arquivo mock: {filename}")

if __name__ == "__main__":
    generate_mock_receitas()

if __name__ == "__main__":
    generate_mock_receitas()
