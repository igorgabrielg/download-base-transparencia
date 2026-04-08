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
        # 1. Lê o relatório
        with open(report_file, "r", encoding="utf-8") as f:
            texto_relatorio = f.read()
            
        if not texto_relatorio.strip():
            await log_to_ws("O arquivo de relatório consolidado está vazio.", is_error=True)
            return
            
        # 2. Fragmenta o texto (chunks de ~700 carac, overlap ~15%)
        chunks = chunk_text(texto_relatorio, chunk_size=700, overlap=105)
        total_chunks = len(chunks)
        await log_to_ws(f"Relatório consolidado fragmentado em {total_chunks} blocos semânticos.")
        
        # 3. Inicializa o ChromaDB local
        vector_store_dir = data_dir / "vector_store"
        vector_store_dir.mkdir(parents=True, exist_ok=True)
        
        await log_to_ws(f"Inicializando banco vetorial local (ChromaDB) em: {vector_store_dir}...")
        
        # Inicializa cliente persistente do ChromaDB
        client = chromadb.PersistentClient(path=str(vector_store_dir))
        
        # Define a função de embedding local padrão do ChromaDB
        # Usa o modelo offline default: all-MiniLM-L6-v2
        embedding_fn = embedding_functions.DefaultEmbeddingFunction()
        
        # Cria ou obtém a coleção
        # Para ser idempotente (limpar coleções anteriores), deletamos se já existir e criamos uma nova
        collection_name = "relatorios_consolidado"
        try:
            client.delete_collection(collection_name)
            await log_to_ws("Coleção anterior removida para garantir indexação limpa.")
        except Exception:
            # Coleção não existia, ignora erro
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
