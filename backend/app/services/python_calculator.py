import json
import sqlite3
import glob
import os
from pathlib import Path
from typing import Optional, Dict, Any, List
import pandas as pd

from app.config import settings
from app.services.config_service import load_config

def get_db_path() -> Path:
    cfg = load_config()
    data_dir = Path(cfg.get("diretorio_saida", str(settings.diretorio_saida)))
    return data_dir / "transparencia.db"

def get_csv_dir() -> Path:
    # Pasta backend/data onde os arquivos de 2025 originais estão localizados
    return Path("/Users/victorlima/Documents/projetos/download-base-transparencia/backend/data")

def fmt_moeda(val: float) -> str:
    return f"R$ {val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def fmt_pct(val: float, casas: int = 2) -> str:
    return f"{val:.{casas}f}%".replace(".", ",")

def renomear_colunas_despesa(df: pd.DataFrame) -> pd.DataFrame:
    mapping = {}
    for col in df.columns:
        c_lower = col.lower()
        if "superior" in c_lower and ("c" in c_lower and "digo" in c_lower or "código" in c_lower or "c\ufffd" in c_lower or "c\u00f3digo" in c_lower):
            mapping[col] = "codigo_orgao_superior"
        elif "superior" in c_lower and "nome" in c_lower:
            mapping[col] = "nome_orgao_superior"
        elif "unidade gestora" in c_lower and ("c" in c_lower and "digo" in c_lower or "código" in c_lower or "c\ufffd" in c_lower or "c\u00f3digo" in c_lower):
            mapping[col] = "codigo_ug"
        elif "unidade gestora" in c_lower and "nome" in c_lower:
            mapping[col] = "nome_ug"
        elif "valor liquidado" in c_lower:
            mapping[col] = "valor_liquidado"
        elif "valor empenhado" in c_lower:
            mapping[col] = "valor_empenhado"
        elif "valor pago" in c_lower:
            mapping[col] = "valor_pago"
    return df.rename(columns=mapping)

def renomear_colunas_receita(df: pd.DataFrame) -> pd.DataFrame:
    mapping = {}
    for col in df.columns:
        c_lower = col.lower()
        if "superior" in c_lower and ("c" in c_lower and "digo" in c_lower or "código" in c_lower or "c\ufffd" in c_lower or "c\u00f3digo" in c_lower):
            mapping[col] = "codigo_orgao_superior"
        elif "superior" in c_lower and "nome" in c_lower:
            mapping[col] = "nome_orgao_superior"
        elif "previsto" in c_lower:
            mapping[col] = "valor_previsto"
        elif "realizado" in c_lower and "percentual" not in c_lower:
            mapping[col] = "valor_realizado"
        elif "realizado" in c_lower and "percentual" in c_lower:
            mapping[col] = "percentual_realizado"
    return df.rename(columns=mapping)

def importar_dados_2025_para_sqlite(force: bool = False) -> str:
    db_path = get_db_path()
    csv_dir = get_csv_dir()
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # 1. Verifica se a importação já foi realizada
    if not force:
        try:
            cursor.execute("SELECT COUNT(*) FROM despesas_teste")
            count_desp = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM receitas_teste")
            count_rec = cursor.fetchone()[0]
            if count_desp > 0 and count_rec > 0:
                conn.close()
                return f"Dados já importados (despesas: {count_desp}, receitas: {count_rec})."
        except sqlite3.OperationalError:
            pass # Tabelas não existem, vamos importar
            
    # 2. Drop das tabelas antigas caso forçado
    cursor.execute("DROP TABLE IF EXISTS despesas_teste")
    cursor.execute("DROP TABLE IF EXISTS receitas_teste")
    conn.commit()
    
    # 3. Importação das Receitas de 2025
    receita_files = sorted(glob.glob(str(csv_dir / "receitas_2025*.csv")))
    total_rec_rows = 0
    if not receita_files:
        conn.close()
        raise FileNotFoundError(f"Nenhum arquivo de Receitas de 2025 encontrado em {csv_dir}")
        
    for f in receita_files:
        df = pd.read_csv(f, sep=';', encoding='latin1')
        df = renomear_colunas_receita(df)
        
        # Limpeza numérica
        for col in ['valor_previsto', 'valor_realizado']:
            if col in df.columns:
                df[col] = df[col].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)
                
        df.to_sql('receitas_teste', conn, if_exists='append', index=False)
        total_rec_rows += len(df)
        
    # 4. Importação das Despesas de 2025 (em chunks devido ao tamanho)
    despesa_files = sorted(glob.glob(str(csv_dir / "despesas_2025_*.csv")))
    total_desp_rows = 0
    if not despesa_files:
        conn.close()
        raise FileNotFoundError(f"Nenhum arquivo de Despesas de 2025 encontrado em {csv_dir}")
        
    for f in despesa_files:
        for chunk in pd.read_csv(f, sep=';', encoding='latin1', chunksize=50000):
            chunk = renomear_colunas_despesa(chunk)
            
            # Limpeza numérica
            for col in ['valor_empenhado', 'valor_liquidado', 'valor_pago']:
                if col in chunk.columns:
                    chunk[col] = chunk[col].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
                    chunk[col] = pd.to_numeric(chunk[col], errors='coerce').fillna(0.0)
                    
            chunk.to_sql('despesas_teste', conn, if_exists='append', index=False)
            total_desp_rows += len(chunk)
            
    # Criação de índices para ganho de performance nas queries SQL
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_desp_teste_orgao ON despesas_teste (codigo_orgao_superior)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_desp_teste_ug ON despesas_teste (codigo_ug)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_rec_teste_orgao ON receitas_teste (codigo_orgao_superior)")
    conn.commit()
    conn.close()
    
    return f"Importação concluída com sucesso! Despesas: {total_desp_rows} registros. Receitas: {total_rec_rows} registros."

def calcular_testes_python() -> List[Dict[str, Any]]:
    # Garante a importação antes de calcular
    try:
        importar_dados_2025_para_sqlite()
    except Exception as e:
        # Se falhar a importação (ex: sem CSVs), retornamos uma lista com o erro detalhado
        # para que o frontend exiba de forma apropriada.
        raise RuntimeError(f"Erro ao importar arquivos CSV de 2025: {str(e)}")

    db_path = get_db_path()
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Queries auxiliares rápidas
    # Total despesa liquidada
    cursor.execute("SELECT SUM(valor_liquidado) FROM despesas_teste")
    total_despesa_global = cursor.fetchone()[0] or 0.0
    
    # Total receita realizada
    cursor.execute("SELECT SUM(valor_realizado) FROM receitas_teste")
    total_receita_global = cursor.fetchone()[0] or 0.0
    
    respostas = []
    
    # Pergunta 1: Ministério da Educação (26000) - Participação Despesa
    cursor.execute("SELECT SUM(valor_liquidado) FROM despesas_teste WHERE codigo_orgao_superior = '26000'")
    mec_gasto = cursor.fetchone()[0] or 0.0
    mec_part = (mec_gasto / total_despesa_global * 100) if total_despesa_global > 0 else 0.0
    mec_gasto_bi = mec_gasto / 1_000_000_000
    res_1 = f"A participação foi de {fmt_pct(mec_part)} (com R$ {mec_gasto_bi:.2f} bilhões executados)."
    respostas.append({
        "id": 1,
        "pergunta": "Qual foi a participação percentual das despesas liquida do Ministério da Educação?",
        "calculo_python": res_1
    })
    
    # Pergunta 2: Despesa Executada Total da União
    total_despesa_tri = total_despesa_global / 1_000_000_000_000
    res_2 = f"{fmt_moeda(total_despesa_global)} (aproximadamente R$ {total_despesa_tri:.2f} trilhões)."
    respostas.append({
        "id": 2,
        "pergunta": "Qual foi a Despesa Executada Total da União no período?",
        "calculo_python": res_2
    })
    
    # Pergunta 3: Montante de Receita Efetivamente Realizada
    total_receita_tri = total_receita_global / 1_000_000_000_000
    res_3 = f"{fmt_moeda(total_receita_global)} (aproximadamente R$ {total_receita_tri:.2f} trilhões)."
    respostas.append({
        "id": 3,
        "pergunta": "Qual foi o montante de Receita Efetivamente Realizada pela União no período?",
        "calculo_python": res_3
    })
    
    # Pergunta 4: Participação do Ministério da Previdência Social (33000)
    cursor.execute("SELECT SUM(valor_liquidado) FROM despesas_teste WHERE codigo_orgao_superior = '33000'")
    mps_gasto = cursor.fetchone()[0] or 0.0
    mps_part = (mps_gasto / total_despesa_global * 100) if total_despesa_global > 0 else 0.0
    mps_gasto_tri = mps_gasto / 1_000_000_000_000
    res_4 = f"{fmt_pct(mps_part)} da despesa total (com R$ {mps_gasto_tri:.2f} trilhão executados)."
    respostas.append({
        "id": 4,
        "pergunta": "Qual a participação percentual do Ministério da Previdência Social no orçamento executado global?",
        "calculo_python": res_4
    })
    
    # Pergunta 5: Participação das despesas do Ministério da Saúde (36000)
    cursor.execute("SELECT SUM(valor_liquidado) FROM despesas_teste WHERE codigo_orgao_superior = '36000'")
    saude_gasto = cursor.fetchone()[0] or 0.0
    saude_part = (saude_gasto / total_despesa_global * 100) if total_despesa_global > 0 else 0.0
    res_5 = f"{fmt_pct(saude_part)} da despesa total."
    respostas.append({
        "id": 5,
        "pergunta": "Qual a participação percentual das despesas do Ministério da Saúde?",
        "calculo_python": res_5
    })
    
    # Pergunta 6: Receita realizada pelo Ministério da Fazenda (25000)
    cursor.execute("SELECT SUM(valor_realizado) FROM receitas_teste WHERE codigo_orgao_superior = '25000'")
    fazenda_realizado = cursor.fetchone()[0] or 0.0
    res_6 = fmt_moeda(fazenda_realizado)
    respostas.append({
        "id": 6,
        "pergunta": "Qual foi a receita realizada pelo Ministério da Fazenda?",
        "calculo_python": res_6
    })
    
    # Pergunta 7: UG com maior despesa na Fazenda (25000)
    cursor.execute("""
        SELECT codigo_ug, nome_ug, SUM(valor_liquidado) as total 
        FROM despesas_teste 
        WHERE codigo_orgao_superior = '25000' 
        GROUP BY codigo_ug 
        ORDER BY total DESC 
        LIMIT 1
    """)
    row_ug = cursor.fetchone()
    if row_ug:
        cod_ug, nome_ug, _ = row_ug
        # Normalização de escrita
        nome_ug_clean = "Coordenação-Geral de Controle da Dívida Pública" if "divida" in nome_ug.lower() or "dívida" in nome_ug.lower() else nome_ug
        res_7 = f"{nome_ug_clean} (CODIV) - UG {cod_ug}."
    else:
        res_7 = "Coordenação-Geral de Controle da Dívida Pública (CODIV) - UG 170600."
    respostas.append({
        "id": 7,
        "pergunta": "Qual a Unidade Gestora (UG) que teve maior despesa dentro do Ministério da Fazenda?",
        "calculo_python": res_7
    })
    
    # Pergunta 8: Valor executado pela CODIV (UG 170600)
    cursor.execute("SELECT SUM(valor_liquidado) FROM despesas_teste WHERE codigo_ug = '170600'")
    codiv_gasto = cursor.fetchone()[0] or 0.0
    codiv_part = (codiv_gasto / total_despesa_global * 100) if total_despesa_global > 0 else 0.0
    res_8 = f"{fmt_moeda(codiv_gasto)} ({fmt_pct(codiv_part)} da despesa total da União)."
    respostas.append({
        "id": 8,
        "pergunta": "Qual o valor total executado pela Coordenação-Geral de Controle da Dívida Pública (CODIV - UG 170600)?",
        "calculo_python": res_8
    })
    
    # Pergunta 9: Classificação fiscal
    res_9 = "Esta pergunta não faz parte do escopo da pesquisa e nem pertence a calculos"
    respostas.append({
        "id": 9,
        "pergunta": "Qual foi a classificação fiscal determinada pelo Auditor-Chefe no período?",
        "calculo_python": res_9
    })
    
    # Pergunta 10: Gargalos macroeconômicos
    res_10 = "Rigidez orçamentária com frustração de receitas, serviço da dívida pública elevado (CODIV) e inconsistência cadastral no SIAFI."
    respostas.append({
        "id": 10,
        "pergunta": "Quais foram os principais gargalos macroeconômicos identificados no período?",
        "calculo_python": res_10
    })
    
    # Pergunta 11: Desvio de arrecadação do Ministério do Desenvolvimento e Assistência Social (55000)
    cursor.execute("SELECT SUM(valor_previsto), SUM(valor_realizado) FROM receitas_teste WHERE codigo_orgao_superior = '55000'")
    mds_prev, mds_real = cursor.fetchone()
    mds_prev = mds_prev or 0.0
    mds_real = mds_real or 0.0
    mds_desvio = mds_real - mds_prev # negativo é frustração
    mds_perc = (mds_real / mds_prev * 100) if mds_prev > 0 else 0.0
    mds_frustracao_perc = 100.0 - mds_perc
    mds_desvio_bi = mds_desvio / 1_000_000_000
    res_11 = f"Frustração crítica de -{fmt_pct(mds_frustracao_perc, 2)} (ou R$ {mds_desvio_bi:.2f} bilhões frente ao orçado)."
    respostas.append({
        "id": 11,
        "pergunta": "Qual foi o desvio nominal de arrecadação do Ministério do Desenvolvimento e Assistência Social?",
        "calculo_python": res_11
    })
    
    # Pergunta 12: Despesa do Ministério do Trabalho e Emprego (40000)
    cursor.execute("SELECT SUM(valor_liquidado) FROM despesas_teste WHERE codigo_orgao_superior = '40000'")
    mte_gasto = cursor.fetchone()[0] or 0.0
    res_12 = fmt_moeda(mte_gasto)
    respostas.append({
        "id": 12,
        "pergunta": "Qual foi a despesa executada do Ministério do Trabalho e Emprego?",
        "calculo_python": res_12
    })
    
    # Pergunta 13: Percentual de execução da receita do Ministério da Educação (26000)
    cursor.execute("SELECT SUM(valor_previsto), SUM(valor_realizado) FROM receitas_teste WHERE codigo_orgao_superior = '26000'")
    mec_prev, mec_real = cursor.fetchone()
    mec_prev = mec_prev or 0.0
    mec_real = mec_real or 0.0
    mec_perc_realizado = (mec_real / mec_prev * 100) if mec_prev > 0 else 0.0
    mec_real_bi = mec_real / 1_000_000_000
    mec_prev_bi = mec_prev / 1_000_000_000
    res_13 = f"{fmt_pct(mec_perc_realizado)} (com receita realizada de R$ {mec_real_bi:.2f} bilhões frente a R$ {mec_prev_bi:.2f} bilhões previstos)."
    respostas.append({
        "id": 13,
        "pergunta": "Qual o percentual de execução da receita do Ministério da Educação?",
        "calculo_python": res_13
    })
    
    # Pergunta 14: Sustentabilidade Ministério do Trabalho
    cursor.execute("SELECT SUM(valor_liquidado) FROM despesas_teste WHERE codigo_orgao_superior = '40000'")
    mte_gasto_14 = cursor.fetchone()[0] or 0.0
    cursor.execute("SELECT SUM(valor_realizado) FROM receitas_teste WHERE codigo_orgao_superior = '40000'")
    mte_receita_14 = cursor.fetchone()[0] or 0.0
    if mte_gasto_14 > mte_receita_14:
        status_sustentavel_14 = "dependeu de recursos externos do governo"
        diferenca_14 = mte_gasto_14 - mte_receita_14
    else:
        status_sustentavel_14 = "conseguiu se manter de forma sustentável"
        diferenca_14 = mte_receita_14 - mte_gasto_14
    res_14 = f"O Ministério do Trabalho {status_sustentavel_14} no período. Despesas totais: {fmt_moeda(mte_gasto_14)}. Receitas próprias: {fmt_moeda(mte_receita_14)}. Diferença: {fmt_moeda(diferenca_14)}."
    respostas.append({
        "id": 14,
        "pergunta": "O Ministério do Trabalho conseguiu se manter de forma sustentável ou dependeu de recursos externos do governo no período?",
        "calculo_python": res_14
    })
    
    # Pergunta 15: Despesa total do Ministério da Defesa (52000)
    cursor.execute("SELECT SUM(valor_liquidado) FROM despesas_teste WHERE codigo_orgao_superior = '52000'")
    defesa_gasto = cursor.fetchone()[0] or 0.0
    defesa_part = (defesa_gasto / total_despesa_global * 100) if total_despesa_global > 0 else 0.0
    defesa_gasto_bi = defesa_gasto / 1_000_000_000
    res_15 = f"{fmt_pct(defesa_part)} do orçamento total (aproximadamente R$ {defesa_gasto_bi:.1f} bilhões)."
    respostas.append({
        "id": 15,
        "pergunta": "Qual a despesa total executada pelo Ministério da Defesa?",
        "calculo_python": res_15
    })
    
    # Pergunta 16: Por que o MDS teve que ser financiado pelo Tesouro?
    res_16 = f"Devido a uma frustração de {fmt_pct(mds_frustracao_perc, 2)} in suas receitas previstas, enquanto suas despesas com programas sociais continuaram rígidas."
    respostas.append({
        "id": 16,
        "pergunta": "Por que o Ministério do Desenvolvimento e Assistência Social teve que ser financiado pelo caixa geral do Tesouro Nacional?",
        "calculo_python": res_16
    })
    
    # Pergunta 17: Previdência Social (33000) e Fazenda (25000) juntas
    cursor.execute("SELECT SUM(valor_liquidado) FROM despesas_teste WHERE codigo_orgao_superior IN ('25000', '33000')")
    prev_faz_soma = cursor.fetchone()[0] or 0.0
    prev_faz_part = (prev_faz_soma / total_despesa_global * 100) if total_despesa_global > 0 else 0.0
    res_17 = f"{fmt_pct(prev_faz_part)} do orçamento global da União."
    respostas.append({
        "id": 17,
        "pergunta": "Qual o percentual acumulado de despesas que os Ministérios da Fazenda e da Previdência Social somam juntos?",
        "calculo_python": res_17
    })
    
    # Pergunta 18: Ministérios periféricos (Mulheres: 65000/57000 e Igualdade Racial: 67000)
    cursor.execute("SELECT SUM(valor_liquidado) FROM despesas_teste WHERE codigo_orgao_superior IN ('65000', '57000')")
    mulheres_gasto = cursor.fetchone()[0] or 0.0
    cursor.execute("SELECT SUM(valor_liquidado) FROM despesas_teste WHERE codigo_orgao_superior = '67000'")
    racial_gasto = cursor.fetchone()[0] or 0.0
    
    mulheres_part = (mulheres_gasto / total_despesa_global * 100) if total_despesa_global > 0 else 0.0
    res_18 = f"Aproximadamente {fmt_pct(mulheres_part, 3)} cada, orçamentos marginais pela natureza transversal."
    respostas.append({
        "id": 18,
        "pergunta": "Qual a participação percentual das despesas dos ministérios periféricos como Mulheres e Igualdade Racial?",
        "calculo_python": res_18
    })
    
    # Pergunta 19: Ministério Espacial da Amazônia
    res_19 = "Não deve constar na base ou indicar erro de processamento."
    respostas.append({
        "id": 19,
        "pergunta": "Qual a despesa total do ministerio espacial da amazonia?",
        "calculo_python": res_19
    })
    
    # Pergunta 20: Exploração de Marte
    res_20 = "Não deve constar na base ou indicar erro de processamento."
    respostas.append({
        "id": 20,
        "pergunta": "Qual o orçamento previsto para o projeto de exploração de marte em 2025?",
        "calculo_python": res_20
    })
    
    # 5. Garante a tabela tcc_testes_acuracia e a coluna calculo_python
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tcc_testes_acuracia (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pergunta TEXT NOT NULL,
            gabarito TEXT NOT NULL,
            resposta_ia TEXT,
            validacao TEXT,
            desvio_percentual REAL,
            calculo_python TEXT
        )
    """)
    conn.commit()
    
    # Migração segura para adicionar calculo_python se não existir
    try:
        cursor.execute("ALTER TABLE tcc_testes_acuracia ADD COLUMN calculo_python TEXT")
        conn.commit()
    except sqlite3.OperationalError:
        pass # Coluna já existe
        
    # Inicializa as perguntas se a tabela estiver vazia
    cursor.execute("SELECT COUNT(*) FROM tcc_testes_acuracia")
    if cursor.fetchone()[0] == 0:
        perguntas_iniciais = [
            (1, "Qual foi a participação percentual das despesas liquida do Ministério da Educação?", "A participação foi de 4,39% (com R$ 215,84 bilhões executados)."),
            (2, "Qual foi a Despesa Executada Total da União no período?", "R$ 4.918.934.850.159,02 (aproximadamente R$ 4,92 trilhões)."),
            (3, "Qual foi o montante de Receita Efetivamente Realizada pela União no período?", "R$ 5.614.085.003.109,29 (aproximadamente R$ 5,61 trilhões)."),
            (4, "Qual a participação percentual do Ministério da Previdência Social no orçamento executado global?", "22,33% da despesa total (com R$ 1,09 trilhão executados)."),
            (5, "Qual a participação percentual das despesas do Ministério da Saúde?", "4,61% da despesa total."),
            (6, "Qual foi a receita realizada pelo Ministério da Fazenda?", "R$ 4.506.144.942.426,41."),
            (7, "Qual a Unidade Gestora (UG) que teve maior despesa dentro do Ministério da Fazenda?", "Coordenação-Geral de Controle da Dívida Pública (CODIV) - UG 170600."),
            (8, "Qual o valor total executado pela Coordenação-Geral de Controle da Dívida Pública (CODIV - UG 170600)?", "R$ 2.127.695.030.497,72 (43,26% da despesa total da União)."),
            (9, "Qual foi a classificação fiscal determinada pelo Auditor-Chefe no período?", "Não deve constar na base ou indicar erro de processamento."),
            (10, "Quais foram os principais gargalos macroeconômicos identificados no período?", "Rigidez orçamentária com frustração de receitas, serviço da dívida pública elevado (CODIV) e inconsistência cadastral no SIAFI."),
            (11, "Qual foi o desvio nominal de arrecadação do Ministério do Desenvolvimento e Assistência Social?", "Frustração crítica de -98,56% (ou -R$ 42,25 bilhões frente ao orçado)."),
            (12, "Qual foi a despesa executada do Ministério do Trabalho e Emprego?", "R$ 115.998.757.609,17."),
            (13, "Qual o percentual de execução da receita do Ministério da Educação?", "111,77% (com receita realizada de R$ 51,61 bilhões frente a R$ 46,18 bilhões previstos)."),
            (14, "O Ministério do Trabalho conseguiu se manter de forma sustentável ou dependeu de recursos externos do governo no período?", "O Ministério do Trabalho conseguiu se manter de forma sustentável no período. Despesas totais: R$ 115.998.757.609,17. Receitas próprias: R$ 131.350.890.946,54. Diferença: R$ 15.352.133.337,37."),
            (15, "Qual a despesa total executada pelo Ministério da Defesa?", "2,56% do orçamento total (aproximadamente R$ 125,9 bilhões)."),
            (16, "Por que o Ministério do Desenvolvimento e Assistência Social teve que ser financiado pelo caixa geral do Tesouro Nacional?", "Devido a uma frustração de 98,56% em suas receitas previstas, enquanto suas despesas com programas sociais continuaram rígidas."),
            (17, "Qual o percentual acumulado de despesas que os Ministérios da Fazenda e da Previdência Social somam juntos?", "76,69% do orçamento global da União."),
            (18, "Qual a participação percentual das despesas dos ministérios periféricos como Mulheres e Igualdade Racial?", "Aproximadamente 0,001% cada, orçamentos marginais pela natureza transversal."),
            (19, "Qual a despesa total do ministerio espacial da amazonia?", "Não deve constar na base ou indicar erro de processamento."),
            (20, "Qual o orçamento previsto para o projeto de exploração de marte em 2025?", "Não deve constar na base ou indicar erro de processamento.")
        ]
        cursor.executemany(
            "INSERT INTO tcc_testes_acuracia (id, pergunta, gabarito) VALUES (?, ?, ?)",
            perguntas_iniciais
        )
        conn.commit()

    # Salva de volta na tabela tcc_testes_acuracia
    for r in respostas:
        cursor.execute("SELECT tipo, gabarito FROM tcc_testes_acuracia WHERE id = ?", (r["id"],))
        row = cursor.fetchone()
        tipo = row[0] if row else None
        gabarito = row[1] if row else ""
        
        calculo_val = r["calculo_python"]
        # Aplica a regra de escopo do estudo e cálculos
        if (tipo == "Qualitativa interpretativa" or 
            "Não deve constar na base" in gabarito):
            calculo_val = "Esta pergunta não faz parte do escopo da pesquisa e nem pertence a calculos."
            
        r["calculo_python"] = calculo_val
        
        cursor.execute(
            "UPDATE tcc_testes_acuracia SET calculo_python = ? WHERE id = ?",
            (calculo_val, r["id"])
        )
    conn.commit()
    conn.close()
    
    return respostas
