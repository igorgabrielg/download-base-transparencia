import os
import json
import logging
from pathlib import Path
import chromadb
from chromadb.utils import embedding_functions

from app.config import settings
from app.services.config_service import load_config
from app.services.cognitive_agents import log_to_ws

logger = logging.getLogger(__name__)


def chunk_text(text: str, chunk_size: int = 700, overlap: int = 100) -> list[str]:
    """Fragmenta o texto em blocos respeitando o tamanho máximo e a sobreposição (overlap).
    Procura quebrar o texto em finais de frases ou parágrafos para não quebrar sentenças no meio.
    """
    if not text:
        return []
        
    chunks = []
    start = 0
    text_len = len(text)
    
    while start < text_len:
        # Se restam menos caracteres que o tamanho do chunk, pegamos o final
        if start + chunk_size >= text_len:
            chunks.append(text[start:])
            break
            
        end = start + chunk_size
        
        # Tenta achar um delimitador semântico (fim de parágrafo \n\n ou ponto final seguido de espaço/linha)
        # Procuramos no intervalo de [end - overlap, end]
        best_break = -1
        search_start = max(start, end - overlap)
        
        # Busca por quebras de parágrafo
        para_break = text.rfind("\n\n", search_start, end)
        if para_break != -1:
            best_break = para_break + 2
        else:
            # Busca por quebras de linha simples
            line_break = text.rfind("\n", search_start, end)
            if line_break != -1:
                best_break = line_break + 1
            else:
                # Busca por pontos finais ou pontos de interrogação/exclamação
                for char in [". ", "? ", "! "]:
                    break_point = text.rfind(char, search_start, end)
                    if break_point != -1:
                        best_break = break_point + len(char)
                        break
        
        # Se não encontrou nenhuma quebra ideal, quebra no tamanho rígido do chunk
        if best_break == -1:
            best_break = end
            
        chunks.append(text[start:best_break].strip())
        
        # O próximo início é recuado em relação ao overlap
        start = best_break - overlap
        if start < 0:
            start = best_break
            
    # Remove eventuais blocos vazios ou excessivamente curtos
    return [c for c in chunks if len(c) > 10]


async def run_vector_indexing():
    """Lê o relatório final consolidado, fragmenta e indexa no ChromaDB local."""
    cfg = load_config()
    data_dir = Path(cfg.get("diretorio_saida", str(settings.diretorio_saida)))
    
    report_file = data_dir / "reports" / "relatorio_final_consolidado.txt"
    if not report_file.exists():
        await log_to_ws("Relatório final consolidado não encontrado em reports. Execute a Etapa 3 primeiro.", is_error=True)
        return
        
    await log_to_ws("Iniciando a Etapa 4: Indexação Vetorial do Relatório Consolidado...")
    
    try:
        # 1. Lê o relatório principal
        texto_relatorio = ""
        if report_file.exists():
            with open(report_file, "r", encoding="utf-8") as f:
                texto_relatorio = f.read()
                
        # 2. Fragmenta o relatório principal (chunks de ~700 carac, overlap ~15%)
        chunks = []
        if texto_relatorio.strip():
            chunks = chunk_text(texto_relatorio, chunk_size=700, overlap=105)
            
        # 3. Adiciona fichas analíticas estruturadas por Órgão Superior (Ministério) a partir das bases enriquecidas
        despesas_enr_file = data_dir / "despesas_enriquecida.json"
        receitas_enr_file = data_dir / "receitas_enriquecida.json"
        
        orgaos_map = {}
        total_despesas_geral = 0.0
        total_receitas_geral = 0.0
        resumo_ugs_global = []
        
        # Coleta dados de despesas por órgão
        if despesas_enr_file.exists():
            try:
                with open(despesas_enr_file, "r", encoding="utf-8") as f:
                    desp_data = json.load(f)
                    total_despesas_geral = float(desp_data.get("total_geral", 0.0))
                    resumo_ugs_global = desp_data.get("resumo_ugs", [])
                    for org in desp_data.get("resumo_orgaos", []):
                        cod = str(org["codigo"])
                        orgaos_map[cod] = {
                            "nome": org["nome"],
                            "total_gasto": org.get("total_gasto", 0.0),
                            "descricao": org.get("descricao", "")
                        }
            except Exception as e:
                logger.error(f"Erro ao carregar despesas_enriquecida.json para indexação: {e}")
                
        # Coleta/mescla dados de receitas por órgão
        if receitas_enr_file.exists():
            try:
                with open(receitas_enr_file, "r", encoding="utf-8") as f:
                    rec_data = json.load(f)
                    total_receitas_geral = float(rec_data.get("total_realizado", 0.0))
                    for org in rec_data.get("resumo_orgaos", []):
                        cod = str(org["codigo"])
                        if cod in orgaos_map:
                            orgaos_map[cod].update({
                                "total_orcado": org.get("total_orcado", 0.0),
                                "total_realizado": org.get("total_realizado", 0.0),
                                "desvio_nominal": org.get("desvio_nominal", 0.0),
                                "percentual_realizado": org.get("percentual_realizado", 0.0)
                            })
                        else:
                            orgaos_map[cod] = {
                                "nome": org["nome"],
                                "total_orcado": org.get("total_orcado", 0.0),
                                "total_realizado": org.get("total_realizado", 0.0),
                                "desvio_nominal": org.get("desvio_nominal", 0.0),
                                "percentual_realizado": org.get("percentual_realizado", 0.0),
                                "descricao": org.get("descricao", "")
                            }
            except Exception as e:
                logger.error(f"Erro ao carregar receitas_enriquecida.json para indexação: {e}")
                
        # Converte as fichas dos órgãos para strings textuais estruturadas
        total_orgaos_adicionados = 0
        for cod, dados in orgaos_map.items():
            nome = dados["nome"]
            gasto = dados.get("total_gasto", 0.0)
            orcado = dados.get("total_orcado", 0.0)
            realizado = dados.get("total_realizado", 0.0)
            desvio = dados.get("desvio_nominal", 0.0)
            perc = dados.get("percentual_realizado", 0.0)
            desc = dados.get("descricao", "")
            
            part_despesa = (gasto / total_despesas_geral * 100) if total_despesas_geral > 0 else 0.0
            part_receita = (realizado / total_receitas_geral * 100) if total_receitas_geral > 0 else 0.0
            
            # Filtra e ordena as top 5 UGs vinculadas a este ministério por gasto
            ugs_vinculadas = [ug for ug in resumo_ugs_global if str(ug.get("codigo_ministerio")).strip() == str(cod).strip()]
            ugs_ordenadas = sorted(ugs_vinculadas, key=lambda x: x.get("total_gasto", 0.0), reverse=True)
            top_ugs = ugs_ordenadas[:5]
            
            top_ugs_str = ""
            if top_ugs:
                top_ugs_str = "Maiores Unidades Gestoras (UGs) em despesa executada vinculadas a este Ministério:\n"
                for i, ug in enumerate(top_ugs, 1):
                    gasto_ug = ug.get("total_gasto", 0.0)
                    part_ug = (gasto_ug / total_despesas_geral * 100) if total_despesas_geral > 0 else 0.0
                    top_ugs_str += f"- {i}. {ug['nome_ug']} (Código Siafi: {ug['codigo_ug']}): R$ {gasto_ug:,.2f} ({part_ug:.2f}% do gasto total governamental do período)\n"
            else:
                top_ugs_str = "Não há informações detalhadas de UGs executoras de despesa para este órgão."
            
            ficha = (
                f"Órgão Superior / Ministério: {nome} (Código Siafi: {cod})\n"
                f"Balanço Orçamentário e Financeiro Anual consolidado:\n"
                f"- Despesa Total Executada (Gastos efetuados): R$ {gasto:,.2f} ({part_despesa:.2f}% do gasto total governamental do período)\n"
                f"- Receita Prevista (Orçamento Planejado Atualizado): R$ {orcado:,.2f}\n"
                f"- Receita Realizada (Total Arrecadado): R$ {realizado:,.2f} ({part_receita:.2f}% da arrecadação total governamental do período)\n"
                f"- Desvio de Arrecadação Nominal: R$ {desvio:,.2f}\n"
                f"- Percentual de Execução/Realização da Receita: {perc:.2f}%\n"
                f"Relevância e Contexto Orçamentário: Este órgão superior tem uma participação de {part_despesa:.2f}% no total de despesas e responde por {part_receita:.2f}% do total de receitas realizadas/arrecadadas pelo governo. Ministérios com percentual elevado (como Educação, Saúde, Defesa ou Previdência) concentram grandes orçamentos devido à sua natureza de atuação de grande escala nacional e prestação de serviços públicos fundamentais de massa para a população. Órgãos ou entidades com participação muito baixa ou nula são geralmente unidades administrativas especializadas de suporte setorial ou atuação local/regional de baixa escala.\n"
                f"{top_ugs_str}\n"
                f"Escopo e Atuação: {desc}"
            )
            chunks.append(ficha)
            total_orgaos_adicionados += 1
            
        total_chunks = len(chunks)
        await log_to_ws(f"Indexação: {total_chunks} blocos semânticos gerados ({total_orgaos_adicionados} fichas de órgãos superiores).")
        
        # 3. Inicializa o ChromaDB local
        vector_store_dir = data_dir / "vector_store"
        vector_store_dir.mkdir(parents=True, exist_ok=True)
        
        await log_to_ws(f"Inicializando banco vetorial local (ChromaDB) em: {vector_store_dir}...")
        
        # Inicializa cliente persistente do ChromaDB
        client = chromadb.PersistentClient(path=str(vector_store_dir))
        
        # Define a função de embedding local padrão do ChromaDB
        embedding_fn = embedding_functions.DefaultEmbeddingFunction()
        
        # Cria ou obtém a coleção
        collection_name = "relatorios_consolidado"
        try:
            client.delete_collection(collection_name)
            await log_to_ws("Coleção anterior removida para garantir indexação limpa.")
        except Exception:
            pass
            
        collection = client.create_collection(
            name=collection_name,
            embedding_function=embedding_fn
        )
        
        # 4. Adiciona blocos de texto e gera embeddings localmente
        ids = [f"chunk_{i}" for i in range(total_chunks)]
        metadados = [{"index": i, "ano_fim": cfg.get("ano_fim", settings.ano_fim)} for i in range(total_chunks)]
        
        await log_to_ws("Vetorizando e inserindo blocos no banco de dados vetorial local...")
        
        # Inserção em lote no ChromaDB
        collection.add(
            documents=chunks,
            metadatas=metadados,
            ids=ids
        )
        
        await log_to_ws(f"Processamento concluído. {total_chunks} vetores de embeddings persistidos no ChromaDB local.")
        await log_to_ws("Indexação Vetorial finalizada com sucesso!", is_success=True)
        
    except Exception as e:
        await log_to_ws(f"Erro na indexação vetorial: {str(e)}", is_error=True)


def run_vector_indexing_background():
    """Wrapper síncrono para execução assíncrona em background pelo FastAPI."""
    import asyncio
    asyncio.run(run_vector_indexing())
