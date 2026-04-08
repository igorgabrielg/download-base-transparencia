import os
import json
import asyncio
import logging
from pathlib import Path

from app.config import settings
from app.services.config_service import load_config
from app.core.websocket import manager as ws_manager

logger = logging.getLogger(__name__)

# Fallback robusto de chaves de API caso o config.json esteja vazio
def get_api_key(cfg: dict, provider: str) -> str:
    if provider == "gemini":
        # Para Gemini, usamos a CLI agy local, portanto não precisamos de API Key
        return ""
    elif provider == "claude":
        key = cfg.get("anthropic_api_key", "").strip()
        if not key:
            key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
            if not key:
                key = os.environ.get("CLAUDE_API_KEY", "").strip()
        return key
    return ""

async def log_to_ws(message: str, is_success=False, is_error=False):
    """Envia uma mensagem de log em tempo real para a interface via WebSocket."""
    logger.info(message)
    status = "concluido" if is_success else "erro" if is_error else "executando"
    
    # Geramos uma sequência randômica/incrementada para a mensagem ser computada no frontend
    import time
    msg_seq = int(time.time() * 1000)
    
    await ws_manager.broadcast({
        "status": status,
        "mensagem": f"IA: {message}",
        "msg_seq": msg_seq,
        "total_registros": 0,
        "pagina_atual": 0,
        "req_minuto": 0,
    })
    # Pequeno delay para garantir que o WebSocket envie ordenadamente
    await asyncio.sleep(0.1)

async def call_llm(provider: str, model_name: str, api_key: str, system_prompt: str, user_prompt: str) -> str:
    """Faz a chamada assíncrona ao LLM escolhido (CLI agy para Gemini ou API para Claude)."""
    if provider == "gemini":
        # Formata o prompt completo unindo system e user
        prompt_completo = f"System Instruction:\n{system_prompt}\n\nUser Query:\n{user_prompt}"
        
        # Executa o agy CLI via subprocesso assíncrono do Python
        # Usamos --dangerously-skip-permissions para evitar interatividade nas permissões
        cmd = ["agy", "--dangerously-skip-permissions", "-p", prompt_completo]
        
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                err_msg = stderr.decode(errors="replace").strip()
                raise RuntimeError(f"Erro na execução da CLI agy (código {process.returncode}): {err_msg}")
            
            resposta = stdout.decode(errors="replace").strip()
            if not resposta:
                raise RuntimeError("A CLI agy retornou uma resposta vazia.")
            return resposta
            
        except FileNotFoundError:
            raise RuntimeError("O executável 'agy' não foi encontrado no PATH do sistema. Certifique-se de que a CLI do Antigravity está instalada.")
        
    elif provider == "claude":
        from anthropic import AsyncAnthropic
        client = AsyncAnthropic(api_key=api_key)
        
        message = await client.messages.create(
            model=model_name,
            max_tokens=4000,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}]
        )
        return message.content[0].text
        
    else:
        raise ValueError(f"Provedor de IA desconhecido: {provider}")

async def run_receita_agent(provider: str, model_name: str, api_key: str, data_dir: Path):
    """Executa a análise do agente especialista em Receitas."""
    receita_file = data_dir / "receitas_enriquecida.json"
    if not receita_file.exists():
        await log_to_ws("Arquivo receitas_enriquecida.json não encontrado. Execute a Etapa 1 primeiro.", is_error=True)
        return

    await log_to_ws("Iniciando análise do Agente Especialista em Receitas...")
    
    with open(receita_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    system_prompt = (
        "Você é um Auditor de IA Especialista em Arrecadação Pública.\n"
        "Comporte-se de forma analítica, técnica e formal.\n"
        "Seu papel é avaliar os dados de Receitas Públicas anuais que serão fornecidos no formato JSON.\n"
        "Diretrizes obrigatórias:\n"
        "1. Avalie o Ano fechado específico fornecido nos dados.\n"
        "2. Calcule e descreva se a arrecadação geral atingiu a meta planejada, comparando o Orçamento Previsto Atualizado e a Receita Realizada através do percentual médio ponderado.\n"
        "3. Aponte o desvio orçamentário nominal e percentual.\n"
        "4. Destaque anomalias ou desvios significativos em Órgãos Superiores (Ministérios) específicos.\n"
        "5. Apresente um parecer conciso, estruturado em tópicos técnicos e focado unicamente no desempenho fiscal de receitas."
    )
    
    user_prompt = f"Dados de Receitas Enriquecidos para análise cognitiva:\n{json.dumps(data, indent=2, ensure_ascii=False)}"
    
    try:
        analise_texto = await call_llm(provider, model_name, api_key, system_prompt, user_prompt)
        
        # Persistência do Checkpoint 1
        out_file = data_dir / "receita_analise_cognitiva.json"
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump({"texto_analise_receita": analise_texto}, f, indent=2, ensure_ascii=False)
            
        await log_to_ws("Análise do Agente de Receita concluída e salva com sucesso.")
    except Exception as e:
        await log_to_ws(f"Erro na análise de Receitas: {str(e)}", is_error=True)

async def run_despesa_agent(provider: str, model_name: str, api_key: str, data_dir: Path):
    """Executa a análise do agente especialista em Despesas."""
    despesa_file = data_dir / "despesas_enriquecida.json"
    if not despesa_file.exists():
        await log_to_ws("Arquivo despesas_enriquecida.json não encontrado. Execute a Etapa 1 primeiro.", is_error=True)
        return

    await log_to_ws("Iniciando análise do Agente Especialista em Despesas...")
    
    with open(despesa_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    system_prompt = (
        "Você é um Auditor de IA Especialista em Execução Orçamentária e Despesa.\n"
        "Comporte-se de forma crítica, detalhada, técnica e formal.\n"
        "Seu papel é auditar a execução orçamentária e identificar gargalos nos dados de Despesas Públicas que serão fornecidos em JSON.\n"
        "Diretrizes obrigatórias:\n"
        "1. Avalie o acumulado de gastos totais do Ano fechado nos dados.\n"
        "2. Analise a distribuição de gastos entre os Órgãos Superiores (Ministérios).\n"
        "3. Faça uma análise crítica detalhada sobre as ações e gastos da Unidade Gestora (UG) líder de despesas no período, contextualizando sua atuação com base na descrição e metadados providos no dicionário correspondente no JSON.\n"
        "4. Foque estritamente em gargalos e comportamento de despesa anual.\n"
        "5. Estruture o resultado em formato de Parecer de Auditoria."
    )
    
    user_prompt = f"Dados de Despesas Enriquecidos para análise cognitiva:\n{json.dumps(data, indent=2, ensure_ascii=False)}"
    
    try:
        analise_texto = await call_llm(provider, model_name, api_key, system_prompt, user_prompt)
        
        # Persistência do Checkpoint 1
        out_file = data_dir / "despesa_analise_cognitiva.json"
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump({"texto_analise_despesa": analise_texto}, f, indent=2, ensure_ascii=False)
            
        await log_to_ws("Análise do Agente de Despesa concluída e salva com sucesso.")
    except Exception as e:
        await log_to_ws(f"Erro na análise de Despesas: {str(e)}", is_error=True)

async def run_cognitive_analysis():
    """Função orquestradora que executa os agentes de IA assincronamente."""
    cfg = load_config()
    data_dir = Path(cfg.get("diretorio_saida", str(settings.diretorio_saida)))
    
    provider = cfg.get("ia_provider", "gemini")
    model_name = cfg.get("ia_model", "gemini-3.5-flash")
    api_key = get_api_key(cfg, provider)
    
    if provider == "claude" and not api_key:
        await log_to_ws(f"Chave de API do provedor '{provider}' não foi configurada no .env ou no painel de configurações.", is_error=True)
        return
        
    await log_to_ws(f"Iniciando Processamento Cognitivo com o provedor '{provider}' e modelo '{model_name}'...")
    
    # Executa os dois agentes em paralelo de forma 100% assíncrona
    await asyncio.gather(
        run_receita_agent(provider, model_name, api_key, data_dir),
        run_despesa_agent(provider, model_name, api_key, data_dir)
    )
    
    await log_to_ws("Pipeline Cognitivo Distribuído finalizado com sucesso!", is_success=True)

def run_cognitive_analysis_background():
    """Wrapper síncrono para execução via BackgroundTasks do FastAPI."""
    asyncio.run(run_cognitive_analysis())
