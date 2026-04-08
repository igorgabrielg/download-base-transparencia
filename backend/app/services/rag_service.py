import logging
from pathlib import Path
import chromadb
from chromadb.utils import embedding_functions

from app.config import settings
from app.services.config_service import load_config
from app.services.cognitive_agents import call_llm, get_api_key

logger = logging.getLogger(__name__)


async def run_rag_query(pergunta: str) -> dict:
    """Consulta o ChromaDB local, recupera os trechos mais relevantes do relatório

    consolidado e gera a resposta via LLM com prompt blindado.
    """
    cfg = load_config()
    data_dir = Path(cfg.get("diretorio_saida", str(settings.diretorio_saida)))
    vector_store_dir = data_dir / "vector_store"

    # 1. Verifica se a pasta do banco vetorial existe
    if not vector_store_dir.exists():
        logger.warning(f"Diretório vector_store não encontrado em: {vector_store_dir}")
        return {
            "resposta": (
                "O banco de dados vetorial local não foi encontrado. "
                "Por favor, certifique-se de que a indexação da Etapa 4 foi executada com sucesso "
                "a partir do Relatório Consolidado."
            ),
            "contexto": [],
        }

    # 2. Conecta ao cliente persistente do ChromaDB
    try:
        client = chromadb.PersistentClient(path=str(vector_store_dir))
        embedding_fn = embedding_functions.DefaultEmbeddingFunction()
        
        # Obtém a coleção correspondente
        collection = client.get_collection(
            name="relatorios_consolidado",
            embedding_function=embedding_fn
        )
    except Exception as e:
        logger.error(f"Erro ao obter coleção relatorios_consolidado do ChromaDB: {str(e)}")
        return {
            "resposta": (
                "A coleção de dados indexados não foi encontrada no banco vetorial. "
                "Por favor, execute a etapa de Indexação Vetorial (Etapa 4) antes de realizar o chat."
            ),
            "contexto": [],
        }

    # 3. Realiza a query vetorial
    try:
        # Recupera os top 4 trechos mais próximos
        results = collection.query(
            query_texts=[pergunta],
            n_results=4
        )
        
        documents = results.get("documents", [[]])[0]
        if not documents:
            return {
                "resposta": (
                    "Não encontrei informações relevantes nas análises consolidadas "
                    "que pudessem responder a essa pergunta."
                ),
                "contexto": [],
            }
            
    except Exception as e:
        logger.error(f"Erro na query do ChromaDB: {str(e)}")
        return {
            "resposta": f"Erro de busca no banco vetorial: {str(e)}",
            "contexto": [],
        }

    # 4. Constrói o Prompt RAG blindado
    context_text = "\n\n---\n\n".join(documents)
    
    system_prompt = (
        "Você é um Assistente Virtual Especialista em Auditoria Orçamentária.\n"
        "Você deve responder à pergunta do usuário baseando-se exclusivamente no contexto técnico fornecido abaixo.\n"
        "Se a resposta não estiver no texto, diga educadamente que não possui essa informação nas análises anuais.\n"
        "Nunca alucine ou invente dados."
    )
    
    user_prompt = (
        f"Contexto técnico extraído do Relatório Consolidado de Auditoria:\n\n"
        f"{context_text}\n\n"
        f"Pergunta do usuário: {pergunta}"
    )

    # 5. Obtém provedor, modelo e credenciais de IA configurados
    provider = cfg.get("ia_provider", "gemini")
    model_name = cfg.get("ia_model", "gemini-3.5-flash")
    api_key = get_api_key(cfg, provider)

    if provider == "claude" and not api_key:
        return {
            "resposta": "Erro: A chave de API do Claude não está configurada nas configurações de IA.",
            "contexto": documents,
        }

    # 6. Executa a chamada à LLM
    try:
        resposta = await call_llm(provider, model_name, api_key, system_prompt, user_prompt)
        return {
            "resposta": resposta,
            "contexto": documents,
        }
    except Exception as e:
        logger.error(f"Erro ao chamar LLM no RAG: {str(e)}")
        return {
            "resposta": f"Erro de processamento da IA ({provider}): {str(e)}",
            "contexto": documents,
        }
