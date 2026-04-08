import asyncio
import logging
from pathlib import Path

from app.config import settings
from app.services.config_service import load_config
from app.services.normalizer import Normalizer
from app.services.enricher import Enricher
from app.services.cognitive_agents import run_cognitive_analysis, log_to_ws
from app.services.synthesizer import run_cognitive_synthesis
from app.services.vector_store import run_vector_indexing

logger = logging.getLogger(__name__)


async def run_full_pipeline():
    """Roda todo o pipeline cognitivo de ponta a ponta:
    1. Normalização dos CSVs
    2. Enriquecimento e geração dos JSONs
    3. Análise Cognitiva com Agentes Especialistas (IA)
    4. Síntese e Consolidação do Relatório (IA)
    5. Indexação Vetorial no ChromaDB (IA)
    """
    cfg = load_config()
    data_dir = str(Path(cfg.get("diretorio_saida", str(settings.diretorio_saida))))

    await log_to_ws("Iniciando o Pipeline de Processamento Completo (Normalização até Indexação)...")

    try:
        # Etapa 1.1: Normalização
        await log_to_ws("Pipeline: Iniciando Normalização dos arquivos CSV...")
        normalizer = Normalizer(data_dir=data_dir)
        # Roda de forma não bloqueante para o loop de eventos
        await asyncio.to_thread(normalizer.process)
        await log_to_ws("Pipeline: Normalização concluída.")

        # Etapa 1.2: Enriquecimento
        await log_to_ws("Pipeline: Iniciando Enriquecimento e geração dos arquivos JSON...")
        enricher = Enricher(data_dir=data_dir)
        await asyncio.to_thread(enricher.process)
        await log_to_ws("Pipeline: Enriquecimento concluído. Dados estruturados com sucesso.")

        # Etapa 2: Análise dos Agentes Cognitivos
        await log_to_ws("Pipeline: Disparando Agentes Especialistas de Receitas e Despesas (IA)...")
        await run_cognitive_analysis()

        # Etapa 3: Consolidação e Síntese do Relatório
        await log_to_ws("Pipeline: Iniciando síntese e redação do Relatório Final Consolidado (IA)...")
        await run_cognitive_synthesis()

        # Etapa 4: Indexação Vetorial no ChromaDB
        await log_to_ws("Pipeline: Indexando o Relatório no Banco de Dados Vetorial local (ChromaDB)...")
        await run_vector_indexing()

        await log_to_ws("Pipeline Completo finalizado com 100% de sucesso!", is_success=True)

    except Exception as e:
        logger.error(f"Erro na execução do Pipeline Completo: {str(e)}")
        await log_to_ws(f"Erro crítico durante o processamento do Pipeline: {str(e)}", is_error=True)


def run_full_pipeline_background():
    """Wrapper síncrono para execução via BackgroundTasks do FastAPI."""
    import asyncio
    asyncio.run(run_full_pipeline())
