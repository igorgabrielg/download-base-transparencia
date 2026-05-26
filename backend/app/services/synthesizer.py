import os
import re
import json
import asyncio
import logging
from pathlib import Path

from app.config import settings
from app.services.config_service import load_config
from app.core.websocket import manager as ws_manager
from app.services.cognitive_agents import get_api_key, call_llm, log_to_ws

logger = logging.getLogger(__name__)

async def run_cognitive_synthesis():
    """Lê os pareceres cognitivos individuais, aciona o Agente Redator e gera o relatório consolidado."""
    cfg = load_config()
    data_dir = Path(cfg.get("diretorio_saida", str(settings.diretorio_saida)))
    reports_dir = data_dir / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    receita_file = data_dir / "receita_analise_cognitiva.json"
    despesa_file = data_dir / "despesa_analise_cognitiva.json"
    
    if not receita_file.exists() or not despesa_file.exists():
        await log_to_ws("Pareceres de Receita e/ou Despesa não encontrados. Execute a Etapa 2 primeiro.", is_error=True)
        return

    await log_to_ws("Lendo pareceres especialistas das etapas anteriores...")
    
    # 1. Carrega as análises cognitivas textuais
    with open(receita_file, "r", encoding="utf-8") as f:
        receita_data = json.load(f)
    with open(despesa_file, "r", encoding="utf-8") as f:
        despesa_data = json.load(f)
        
    texto_receita = receita_data.get("texto_analise_receita", "")
    texto_despesa = despesa_data.get("texto_analise_despesa", "")
    
    if not texto_receita or not texto_despesa:
        await log_to_ws("Os pareceres especialistas de Receita ou Despesa estão vazios.", is_error=True)
        return

    provider = cfg.get("ia_provider", "gemini")
    model_name = cfg.get("ia_model", "gemini-3.5-flash")
    api_key = get_api_key(cfg, provider)
    
    if provider == "claude" and not api_key:
        await log_to_ws(f"Chave de API do provedor '{provider}' não foi configurada.", is_error=True)
        return
        
    await log_to_ws("Iniciando a Consolidação do Relatório Final via Auditor-Chefe...")

    # 2. Configura Prompts
    system_prompt = (
        "Você é o Auditor-Chefe de Estado e Redator Técnico Especialista.\n"
        "Comporte-se de forma analítica, crítica, técnica e extremamente formal (linguagem jurídica/técnica de auditoria).\n"
        "Sua tarefa é ler dois pareceres parciais (um focado em Receitas/Arrecadação e outro em Despesas/Execução) e consolidá-los em um Relatório Final único.\n"
        "Diretrizes obrigatórias:\n"
        "1. Correlacione e cruze os dados: avalie se o volume de despesas e os gargalos identificados no parecer de despesa estão compatíveis e sustentáveis frente à eficiência ou frustração de arrecadação descrita no parecer de receita.\n"
        "2. Identifique gargalos macroeconômicos (ex: se houve frustração de receita em algum ministério/órgão que manteve gastos ou despesas altas).\n"
        "3. Faça uma análise crítica detalhada sobre as assimetrias orçamentárias do período: explique os motivos estruturais ou constitucionais pelos quais determinados ministérios e órgãos superiores chaves (como Educação, Saúde, Defesa ou outros líderes de gastos nos dados) concentram grandes volumes de recursos, e contextualize o motivo pelo qual certos órgãos/UGs menores operam com orçamento muito baixo ou nulo (ex: natureza regional, atuação descentralizada ou escopo reduzido).\n"
        "4. Determine e classifique explicitamente a situação fiscal geral do período analisado em uma das três categorias: 'Positiva', 'Neutra' ou 'Negativa'.\n"
        "5. Você DEVE incluir na última linha do seu relatório a tag exata: 'Classificacao Fiscal: [Positiva/Neutra/Negativa]'.\n"
        "6. O relatório deve ser formal, coerente e sem contradições lógicas, formatado em Markdown para fácil leitura."
    )
    
    user_prompt = (
        "Consolide os pareceres técnicos abaixo em um parecer final de auditoria:\n\n"
        "--- INÍCIO DO BLOCO DE RECEITAS ---\n"
        f"{texto_receita}\n"
        "--- FIM DO BLOCO DE RECEITAS ---\n\n"
        "--- INÍCIO DO BLOCO DE DESPESAS ---\n"
        f"{texto_despesa}\n"
        "--- FIM DO BLOCO DE DESPESAS ---\n"
    )

    try:
        # 3. Invoca o LLM
        relatorio_texto = await call_llm(provider, model_name, api_key, system_prompt, user_prompt)
        
        # 4. Extrai a classificação fiscal via Regex
        classificacao = "Neutra"  # Default fallback
        match = re.search(r"Classificacao Fiscal:\s*(Positiva|Neutra|Negativa)", relatorio_texto, re.IGNORECASE)
        if match:
            classificacao = match.group(1).strip().capitalize()
            
        # 5. Persistência física do Checkpoint 2
        # Arquivo de texto puro (.txt)
        txt_path = reports_dir / "relatorio_final_consolidado.txt"
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(relatorio_texto)
            
        # Arquivo estruturado (.json)
        json_path = reports_dir / "relatorio_final_consolidado.json"
        report_data = {
            "classificacao_fiscal": classificacao,
            "provedor_ia": provider,
            "modelo_ia": model_name,
            "texto_relatorio": relatorio_texto
        }
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
            
        await log_to_ws(f"Relatório Final Consolidado gravado na pasta reports. Classificação Fiscal: {classificacao}.")
        await log_to_ws("Síntese e Consolidação finalizadas com sucesso!", is_success=True)
        
    except Exception as e:
        await log_to_ws(f"Erro na síntese do Relatório: {str(e)}", is_error=True)

def run_cognitive_synthesis_background():
    """Wrapper síncrono para execução em background pelo FastAPI."""
    asyncio.run(run_cognitive_synthesis())
