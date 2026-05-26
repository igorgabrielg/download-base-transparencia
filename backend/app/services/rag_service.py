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
    documents = []
    try:
        # Recupera os top 8 trechos mais próximos (com o Relatório Consolidado já fixo no prompt, 8 é ideal para focar em detalhes ministeriais)
        results = collection.query(
            query_texts=[pergunta],
            n_results=8
        )
        documents = results.get("documents", [[]])[0]
    except Exception as e:
        logger.error(f"Erro na query do ChromaDB: {str(e)}")
        # Não falhamos imediatamente caso o relatório geral consolidado físico exista
        pass

    # 4. Lê o Relatório Consolidado Geral Físico (se existir) para injetá-lo fixo no contexto
    report_file = data_dir / "reports" / "relatorio_final_consolidado.txt"
    texto_relatorio_geral = ""
    if report_file.exists():
        try:
            with open(report_file, "r", encoding="utf-8") as f:
                texto_relatorio_geral = f.read().strip()
        except Exception as e:
            logger.error(f"Erro ao ler relatorio_final_consolidado.txt: {e}")

    # Se não temos nem documentos do banco nem o relatório geral físico, indicamos erro
    if not documents and not texto_relatorio_geral:
        return {
            "resposta": "Teve um erro no processamento e não tenho acesso a essa informação, solicitando um novo processamento.",
            "contexto": [],
        }

    # 5. Constrói o Prompt RAG blindado
    context_text = "\n\n---\n\n".join(documents)
    
    system_prompt = (
        "Você é um Assistente Virtual Especialista em Auditoria Orçamentária.\n"
        "Você deve responder à pergunta do usuário baseando-se no contexto técnico fornecido abaixo, que representa os dados extraídos das análises anuais consolidadas e fichas dos ministérios.\n\n"
        "Instruções cruciais de resposta:\n"
        "1. Se as informações necessárias para responder à pergunta NÃO constam de forma alguma nos dados e fichas extraídos dos arquivos CSV (por exemplo, se a pergunta se refere a um ano fiscal não processado, ou a um ministério que comprovadamente não existe nas bases orçamentárias), informe de forma clara e objetiva que a informação não consta no CSV.\n"
        "2. Se você identificar que a pergunta se refere a dados que deveriam ser calculáveis ou existentes, mas o contexto fornecido abaixo é incompleto, insuficiente ou se por qualquer outro motivo você não conseguir calcular ou responder com precisão técnica com base exclusiva nos dados abaixo, responda EXATAMENTE: 'Teve um erro no processamento e não tenho acesso a essa informação, solicitando um novo processamento.'\n"
        "3. Nunca invente dados ou alucine informações fora do contexto técnico fornecido. Se houver contradição ou falta de dados para cálculo preciso, aplique a instrução da regra 2."
    )
    
    user_prompt = (
        f"=== RELATÓRIO CONSOLIDADO GERAL DA UNIÃO ===\n"
        f"{texto_relatorio_geral}\n\n"
        f"=== DETALHES DE MINISTÉRIOS E UGS (VETORIAL) ===\n"
        f"{context_text}\n\n"
        f"Pergunta do usuário: {pergunta}"
    )

    # 6. Obtém provedor, modelo e credenciais de IA configurados
    provider = cfg.get("ia_provider", "gemini")
    model_name = cfg.get("ia_model", "gemini-3.5-flash")
    api_key = get_api_key(cfg, provider)

    if provider == "claude" and not api_key:
        return {
            "resposta": "Erro: A chave de API do Claude não está configurada nas configurações de IA.",
            "contexto": documents,
        }

    # 7. Executa a chamada à LLM
    try:
        resposta = await call_llm(provider, model_name, api_key, system_prompt, user_prompt)
        return {
            "resposta": resposta,
            "contexto": documents,
        }
    except Exception as e:
        logger.error(f"Erro ao chamar LLM no RAG: {str(e)}")
        return {
            "resposta": "Teve um erro no processamento e não tenho acesso a essa informação, solicitando um novo processamento.",
            "contexto": documents,
        }
