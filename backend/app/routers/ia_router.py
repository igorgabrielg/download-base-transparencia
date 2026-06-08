from fastapi import APIRouter, BackgroundTasks
from app.services.cognitive_agents import run_cognitive_analysis
from app.services.synthesizer import run_cognitive_synthesis
from app.services.vector_store import run_vector_indexing
from app.models.schemas import ChatRequest, ChatResponse
from app.services.rag_service import run_rag_query

router = APIRouter()

@router.post("/analyze")
async def analyze_data(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_cognitive_analysis)
    return {"message": "Análise cognitiva de IA iniciada em background."}


@router.post("/synthesize")
async def synthesize_data(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_cognitive_synthesis)
    return {"message": "Consolidação e síntese de IA iniciada em background."}


@router.post("/index")
async def index_data(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_vector_indexing)
    return {"message": "Indexação vetorial de IA iniciada em background."}


@router.post("/chat", response_model=ChatResponse)
async def chat_rag(payload: ChatRequest):
    result = await run_rag_query(payload.pergunta)
    return ChatResponse(**result)


@router.post("/pipeline-completo")
async def run_full_pipeline_endpoint(background_tasks: BackgroundTasks):
    from app.services.pipeline_service import run_full_pipeline
    background_tasks.add_task(run_full_pipeline)
    return {"message": "Pipeline completo de processamento (Normalização até Indexação) iniciado em background."}


from fastapi.responses import StreamingResponse
from pathlib import Path
import json
import aiosqlite
from pydantic import BaseModel
from typing import Optional
from app.config import settings
from app.services.config_service import load_config
from app.services.rag_service import run_rag_query

class PerguntaCreate(BaseModel):
    pergunta: str
    gabarito: str
    tipo: str

class PerguntaUpdate(BaseModel):
    pergunta: Optional[str] = None
    gabarito: Optional[str] = None
    resposta_ia: Optional[str] = None
    validacao: Optional[str] = None
    desvio_percentual: Optional[float] = None
    tipo: Optional[str] = None

def get_db_path() -> Path:
    cfg = load_config()
    data_dir = Path(cfg.get("diretorio_saida", str(settings.diretorio_saida)))
    return data_dir / "transparencia.db"

async def init_testes_db():
    db_path = get_db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    async with aiosqlite.connect(str(db_path)) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS tcc_testes_acuracia (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pergunta TEXT NOT NULL,
                gabarito TEXT NOT NULL,
                resposta_ia TEXT,
                validacao TEXT,
                desvio_percentual REAL,
                tipo TEXT
            )
        """)
        await db.commit()
        
        try:
            await db.execute("ALTER TABLE tcc_testes_acuracia ADD COLUMN desvio_percentual REAL")
            await db.commit()
        except Exception:
            pass
            
        try:
            await db.execute("ALTER TABLE tcc_testes_acuracia ADD COLUMN tipo TEXT")
            await db.commit()
        except Exception:
            pass
        
        # Migração global para garatir que qualquer tipo antigo seja convertido para a nova nomenclatura
        await db.execute("UPDATE tcc_testes_acuracia SET tipo = 'Qualitativa baseada em dados' WHERE tipo = 'Qualitativa Analítica' OR tipo = 'Qualitativa de Cálculo'")
        await db.execute("UPDATE tcc_testes_acuracia SET tipo = 'Qualitativa interpretativa' WHERE tipo = 'Qualitativa Conceitual' OR tipo = 'Qualitativa de Entendimento'")
        await db.commit()
        
        async with db.execute("SELECT COUNT(*) FROM tcc_testes_acuracia") as cursor:
            row = await cursor.fetchone()
            count = row[0] if row else 0
            
        perguntas_padrao = [
            ("Qual foi a participação percentual das despesas liquida do Ministério da Educação?", "A participação foi de 4,39% (com R$ 215,84 bilhões executados).", "Quantitativa"),
            ("Qual foi a Despesa Executada Total da União no período?", "R$ 4.918.934.850.159,02 (aproximadamente R$ 4,92 trilhões).", "Quantitativa"),
            ("Qual foi o montante de Receita Efetivamente Realizada pela União no período?", "R$ 5.614.085.003.109,29 (aproximadamente R$ 5,61 trilhões).", "Quantitativa"),
            ("Qual a participação percentual do Ministério da Previdência Social no orçamento executado global?", "22,33% da despesa total (com R$ 1,09 trilhão executados).", "Quantitativa"),
            ("Qual a participação percentual das despesas do Ministério da Saúde?", "4,61% da despesa total.", "Quantitativa"),
            ("Qual foi a receita realizada pelo Ministério da Fazenda?", "R$ 4.506.144.942.426,41.", "Quantitativa"),
            ("Qual a Unidade Gestora (UG) que teve maior despesa dentro do Ministério da Fazenda?", "Coordenação-Geral de Controle da Dívida Pública (CODIV) - UG 170600.", "Qualitativa baseada em dados"),
            ("Qual o valor total executado pela Coordenação-Geral de Controle da Dívida Pública (CODIV - UG 170600)?", "R$ 2.127.695.030.497,72 (43,26% da despesa total da União).", "Quantitativa"),
            ("Qual foi a classificação fiscal determinada pelo Auditor-Chefe no período?", "Classificação Fiscal: Neutra (com ressalvas) devido às graves assimetrias orçamentárias estruturais, duplicidades de cadastro de órgãos no SIAFI, e o desvio absoluto da meta macroeconômica global.", "Qualitativa interpretativa"),
            ("Quais foram os principais gargalos macroeconômicos identificados no período?", "Rigidez orçamentária com frustração de receitas, serviço da dívida pública elevado (CODIV) e inconsistência cadastral no SIAFI.", "Qualitativa interpretativa"),
            ("Qual foi o desvio nominal de arrecadação do Ministério do Desenvolvimento e Assistência Social?", "Frustração crítica de -98,56% (ou -R$ 42,25 bilhões frente ao orçado).", "Quantitativa"),
            ("Qual foi a despesa executada do Ministério do Trabalho e Emprego?", "R$ 115.998.757.609,17.", "Quantitativa"),
            ("Qual o percentual de execução da receita do Ministério da Educação?", "111,77% (com receita realizada de R$ 51,61 bilhões frente a R$ 46,18 bilhões previstos).", "Quantitativa"),
            ("O Ministério do Trabalho conseguiu se manter de forma sustentável ou dependeu de recursos externos do governo no período?", "O Ministério do Trabalho conseguiu se manter de forma sustentável no período. Despesas totais: R$ 115.998.757.609,17. Receitas próprias: R$ 131.350.890.946,54. Diferença: R$ 15.352.133.337,37.", "Qualitativa baseada em dados"),
            ("Qual a despesa total executada pelo Ministério da Defesa?", "2,56% do orçamento total (aproximadamente R$ 125,9 bilhões).", "Quantitativa"),
            ("Por que o Ministério do Desenvolvimento e Assistência Social teve que ser financiado pelo caixa geral do Tesouro Nacional?", "Devido a uma frustração de 98,56% em suas receitas previstas, enquanto suas despesas com programas sociais continuaram rígidas.", "Qualitativa interpretativa"),
            ("Qual o percentual acumulado de despesas que os Ministérios da Fazenda e da Previdência Social somam juntos?", "76,69% do orçamento global da União.", "Quantitativa"),
            ("Qual a participação percentual das despesas dos ministérios periféricos como Mulheres e Igualdade Racial?", "Aproximadamente 0,001% cada, orçamentos marginais pela natureza transversal.", "Quantitativa"),
            ("Qual a despesa total do ministerio espacial da amazonia?", "Não deve constar na base ou indicar erro de processamento.", "Segurança"),
            ("Qual o orçamento previsto para o projeto de exploração de marte em 2025?", "Não deve constar na base ou indicar erro de processamento.", "Segurança")
        ]
        
        if count == 0:
            await db.executemany(
                "INSERT INTO tcc_testes_acuracia (pergunta, gabarito, tipo) VALUES (?, ?, ?)",
                perguntas_padrao
            )
            await db.commit()
        else:
            # Sincroniza/atualiza incondicionalmente os tipos das perguntas padrões, mas preserva gabaritos editados pelo usuário
            for pergunta, gabarito, tipo in perguntas_padrao:
                if pergunta == "Qual foi a classificação fiscal determinada pelo Auditor-Chefe no período?":
                    # Só atualiza o gabarito se ele ainda for o de rejeição genérica antiga ou estiver vazio
                    await db.execute(
                        """
                        UPDATE tcc_testes_acuracia 
                        SET gabarito = ?, tipo = ? 
                        WHERE pergunta = ? AND (gabarito = 'Não deve constar na base ou indicar erro de processamento.' OR gabarito IS NULL OR gabarito = '')
                        """,
                        (gabarito, tipo, pergunta)
                    )
                    # Caso contrário, atualiza apenas o tipo
                    await db.execute(
                        "UPDATE tcc_testes_acuracia SET tipo = ? WHERE pergunta = ? AND (gabarito != 'Não deve constar na base ou indicar erro de processamento.' AND gabarito IS NOT NULL AND gabarito != '')",
                        (tipo, pergunta)
                    )
                else:
                    await db.execute(
                        "UPDATE tcc_testes_acuracia SET tipo = ? WHERE pergunta = ?",
                        (tipo, pergunta)
                    )
            await db.commit()

@router.get("/testes-acuracia/perguntas")
async def get_perguntas_testes():
    await init_testes_db()
    db_path = get_db_path()
    async with aiosqlite.connect(str(db_path)) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT id, pergunta, gabarito, resposta_ia, validacao, desvio_percentual, tipo FROM tcc_testes_acuracia") as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

@router.post("/testes-acuracia/pergunta")
async def create_pergunta_teste(payload: PerguntaCreate):
    await init_testes_db()
    db_path = get_db_path()
    async with aiosqlite.connect(str(db_path)) as db:
        cursor = await db.execute(
            "INSERT INTO tcc_testes_acuracia (pergunta, gabarito, tipo) VALUES (?, ?, ?)",
            (payload.pergunta, payload.gabarito, payload.tipo)
        )
        await db.commit()
        return {"id": cursor.lastrowid, "message": "Pergunta de teste cadastrada com sucesso!"}

@router.put("/testes-acuracia/pergunta/{id}")
async def update_pergunta_teste(id: int, payload: PerguntaUpdate):
    await init_testes_db()
    db_path = get_db_path()
    async with aiosqlite.connect(str(db_path)) as db:
        update_fields = []
        params = []
        for field, value in payload.model_dump(exclude_unset=True).items():
            update_fields.append(f"{field} = ?")
            params.append(value)
        
        if not update_fields:
            return {"message": "Nenhum campo para atualizar."}
            
        params.append(id)
        query = f"UPDATE tcc_testes_acuracia SET {', '.join(update_fields)} WHERE id = ?"
        await db.execute(query, params)
        await db.commit()
        return {"message": "Pergunta de teste atualizada com sucesso!"}

@router.delete("/testes-acuracia/pergunta/{id}")
async def delete_pergunta_teste(id: int):
    await init_testes_db()
    db_path = get_db_path()
    async with aiosqlite.connect(str(db_path)) as db:
        await db.execute("DELETE FROM tcc_testes_acuracia WHERE id = ?", (id,))
        await db.commit()
        return {"message": "Pergunta de teste excluída com sucesso!"}

def normalizar_magnitudes(texto: str) -> str:
    import re
    if not texto:
        return ""
    
    t = texto.lower()
    
    # Regex para capturar padrões como "1,09 trilhão", "215,84 bilhões", "42,25 bi", "125.9 bilhões"
    padrao = r'(\d+(?:[\.,]\d+)?)\s*(milh[õo]es|milh[ãa]o|bilh[õo]es|bilh[ãa]o|trilh[õo]es|trilh[ãa]o|mi|bi|tri)\b'
    
    def substituir(match):
        num_str = match.group(1)
        magnitude = match.group(2)
        
        # Corrige ponto decimal único isolado (ex: 125.8 bilhões)
        if '.' in num_str and ',' not in num_str and num_str.count('.') == 1:
            pass
        else:
            num_str = num_str.replace('.', '').replace(',', '.')
            
        try:
            val = float(num_str)
        except ValueError:
            return match.group(0)
            
        multiplicador = 1
        if "milh" in magnitude or magnitude == "mi":
            multiplicador = 1_000_000
        elif "bilh" in magnitude or magnitude == "bi":
            multiplicador = 1_000_000_000
        elif "trilh" in magnitude or magnitude == "tri":
            multiplicador = 1_000_000_000_000
            
        valor_final = val * multiplicador
        return f" {valor_final:.2f} "
        
    return re.sub(padrao, substituir, t)


def string_to_float(s: str) -> Optional[float]:
    # Limpa caracteres não-numéricos, mantendo pontos, vírgulas e sinal negativo
    s_clean = "".join([c for c in s if c.isdigit() or c in ['.', ',', '-']])
    if not s_clean:
        return None
        
    # Caso 1: Contém tanto ponto quanto vírgula (ex: 1.098.483,61 ou 1,098,483.61)
    if '.' in s_clean and ',' in s_clean:
        last_dot = s_clean.rfind('.')
        last_comma = s_clean.rfind(',')
        if last_comma > last_dot:
            # Padrão PT: ponto separa milhares, vírgula separa decimal
            s_clean = s_clean.replace('.', '').replace(',', '.')
        else:
            # Padrão EN/US: vírgula separa milhares, ponto separa decimal
            s_clean = s_clean.replace(',', '')
            
    # Caso 2: Contém apenas vírgula (ex: 22,33 ou 42253656831,24)
    elif ',' in s_clean:
        # Se houver mais de uma vírgula, são separadores de milhares padrão EN
        if s_clean.count(',') > 1:
            s_clean = s_clean.replace(',', '')
        else:
            # Vírgula decimal padrão PT
            s_clean = s_clean.replace(',', '.')
            
    # Caso 3: Contém apenas ponto (ex: 1090000000000.00 ou 1.000.000)
    elif '.' in s_clean:
        # Se houver mais de um ponto, são milhares padrão PT
        if s_clean.count('.') > 1:
            s_clean = s_clean.replace('.', '')
            
    try:
        return float(s_clean)
    except ValueError:
        return None


def extrair_percentual(texto: str) -> Optional[float]:
    import re
    if not texto:
        return None
    matches = re.findall(r'(\d+(?:[\.,]\d+)?)\s*%', texto)
    if matches:
        return string_to_float(matches[0])
    return None


def extrair_todos_numeros(texto: str) -> list[float]:
    import re
    if not texto:
        return []
        
    # Normaliza magnitudes ("bilhões")
    t_norm = normalizar_magnitudes(texto)
    # Limpa cifrões
    t_norm = t_norm.replace("R$", "").replace("$", "")
    
    matches = re.findall(r'\b\d+(?:[\.,]\d+)*\b', t_norm)
    valores = []
    for m in matches:
        val = string_to_float(m)
        if val is not None:
            # Ignora anos fiscais comuns
            if val in [2025, 2026, 2024, 2014, 2015]:
                continue
            # Ignora pequenos inteiros de marcadores de lista (como de 1 a 10 sozinhos)
            if val.is_integer() and 1 <= val <= 10:
                continue
            valores.append(val)
    return valores


def calcular_desvio_percentual(pergunta: str, resposta_ia: str, gabarito: str) -> tuple[Optional[float], Optional[float]]:
    # Retorna (desvio_relativo, diferenca_absoluta)
    # 1. Normaliza magnitudes textuais
    resp_norm = normalizar_magnitudes(resposta_ia)
    gab_norm = normalizar_magnitudes(gabarito)
    
    nums_ia = extrair_todos_numeros(resp_norm)
    nums_gab = extrair_todos_numeros(gab_norm)
    
    if not nums_ia or not nums_gab:
        return None, None
        
    perg_lower = pergunta.lower()
    is_percentage_question = any(x in perg_lower for x in ["percentual", "percentagem", "%", "participação", "taxa", "proporção"])
    
    # Classifica os números
    pcts_ia = [n for n in nums_ia if n <= 100]
    pcts_gab = [n for n in nums_gab if n <= 100]
    
    vals_ia = [n for n in nums_ia if n > 100]
    vals_gab = [n for n in nums_gab if n > 100]
    
    # Se a pergunta for sobre percentual e ambos tiverem valores de percentual (<= 100)
    if is_percentage_question and pcts_ia and pcts_gab:
        best_dev = float('inf')
        best_diff = float('inf')
        for g in pcts_gab:
            for i in pcts_ia:
                diff = abs(i - g)
                dev = (diff / g) * 100
                if dev < best_dev:
                    best_dev = dev
                    best_diff = diff
        return round(best_dev, 4), round(best_diff, 6)
        
    # Se ambos tiverem valores grandes/monetários (> 100)
    if vals_ia and vals_gab:
        best_dev = float('inf')
        best_diff = float('inf')
        for g in vals_gab:
            for i in vals_ia:
                diff = abs(i - g)
                dev = (diff / g) * 100
                if dev < best_dev:
                    best_dev = dev
                    best_diff = diff
        return round(best_dev, 4), round(best_diff, 6)
        
    # Fallback: Compara qualquer número entre IA e Gabarito
    best_dev = float('inf')
    best_diff = float('inf')
    for g in nums_gab:
        for i in nums_ia:
            diff = abs(i - g)
            dev = (diff / g) * 100
            if dev < best_dev:
                best_dev = dev
                best_diff = diff
                
    if best_dev != float('inf'):
        return round(best_dev, 4), round(best_diff, 6)
        
    return None, None


def calcular_validacao_sugerida(pergunta: str, resposta_ia: str, gabarito: str) -> tuple[Optional[str], Optional[float]]:
    import re
    validacao_sugerida = None
    resp = resposta_ia.lower()
    esper = gabarito.lower()
    perg = pergunta.lower()
    
    # 1. Regra especial para perguntas de rejeição/não constar na base (ex: Amazônia, Marte)
    termos_rejeicao_gabarito = ["não deve constar", "não constar", "não existe", "indicar erro", "erro de processamento", "não consta", "sem informação"]
    if any(term in esper for term in termos_rejeicao_gabarito):
        termos_rejeicao_ia = [
            "não consta", "não foi encontrado", "não foi encontrada", "não existe", 
            "não existem", "não há", "não contem", "não contém", "não apresenta", 
            "erro no processamento", "não tenho acesso", "não foi possível", "não constam"
        ]
        if any(term in resp for term in termos_rejeicao_ia):
            validacao_sugerida = "aceitavel"
            
    # 2. Regra especial para quando a IA dá erro/rejeição mas o gabarito esperava um valor real (falso negativo da IA)
    if not validacao_sugerida:
        termos_erro_ia = ["erro no processamento", "não tenho acesso", "não foi possível", "não consta nos dados"]
        if any(term in resp for term in termos_erro_ia):
            validacao_sugerida = "incorreto"

    # 3. Heurística baseada no desvio percentual calculado
    if not validacao_sugerida:
        desvio, diff_abs = calcular_desvio_percentual(pergunta, resposta_ia, gabarito)
        if desvio is not None:
            # Nova escala:
            # - entre 0 e 0.5%: aceitavel
            # - entre 0.5% e 5.0%: sinais de problemas
            # - acima de 5.0%: incorreto
            if desvio < 0.5:
                validacao_sugerida = "aceitavel"
            elif desvio <= 5.0:
                validacao_sugerida = "sinais de problemas"
            else:
                validacao_sugerida = "incorreto"
    else:
        # Se já foi validada por rejeição correta, calculamos o desvio apenas para exibição
        desvio, _ = calcular_desvio_percentual(pergunta, resposta_ia, gabarito)
            
    # 4. Fallbacks de validação textual
    if not validacao_sugerida:
        numbers_esperado = re.findall(r"\d+[\d\.,]*", esper)
        if numbers_esperado:
            nums_resp = [n.replace('.', '').replace(',', '') for n in re.findall(r"\d+[\d\.,]*", resp)]
            nums_esper = [n.replace('.', '').replace(',', '') for n in numbers_esperado]
            if any(num in nums_resp for num in nums_esper):
                validacao_sugerida = "aceitavel"
        
        if not validacao_sugerida:
            # Compara palavras significativas removendo termos comuns da pergunta para evitar falsos positivos
            words_perg = set([w for w in re.findall(r"\w+", perg) if len(w) > 4])
            words_esper = set([w for w in re.findall(r"\w+", esper) if len(w) > 4]) - words_perg
            words_resp = set([w for w in re.findall(r"\w+", resp) if len(w) > 4]) - words_perg
            
            intersection = words_esper.intersection(words_resp)
            if len(intersection) >= 2:
                validacao_sugerida = "aceitavel"
                    
    if not validacao_sugerida:
        validacao_sugerida = "incorreto"
        
    return validacao_sugerida, desvio


@router.post("/testes-acuracia/pergunta/{id}/run")
async def run_pergunta_teste_individual(id: int):
    from fastapi import HTTPException
    await init_testes_db()
    db_path = get_db_path()
    
    # 1. Busca a pergunta no banco
    async with aiosqlite.connect(str(db_path)) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT id, pergunta, gabarito, tipo FROM tcc_testes_acuracia WHERE id = ?", (id,)) as cursor:
            row = await cursor.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Pergunta de teste não encontrada.")
            item = dict(row)
            
    # 2. Executa o RAG
    try:
        res = await run_rag_query(item["pergunta"])
        resposta_ia = res.get("resposta", "Erro ao obter resposta.")
    except Exception as e:
        resposta_ia = f"Erro na execução da consulta: {str(e)}"
        
    # 3. Calcula a validação automática e o desvio
    validacao_sugerida, desvio = calcular_validacao_sugerida(item["pergunta"], resposta_ia, item["gabarito"])
    
    # 4. Atualiza no SQLite
    async with aiosqlite.connect(str(db_path)) as db:
        await db.execute(
            "UPDATE tcc_testes_acuracia SET resposta_ia = ?, validacao = ?, desvio_percentual = ? WHERE id = ?",
            (resposta_ia, validacao_sugerida, desvio, id)
        )
        await db.commit()
        
    return {
        "id": id,
        "pergunta": item["pergunta"],
        "gabarito": item["gabarito"],
        "tipo": item.get("tipo", "Quantitativa"),
        "resposta_ia": resposta_ia,
        "validacao": validacao_sugerida,
        "desvio_percentual": desvio,
        "status": "concluido"
    }


@router.get("/testes-acuracia/stream")
async def stream_testes_acuracia():
    await init_testes_db()
    db_path = get_db_path()
    
    async def event_generator():
        async with aiosqlite.connect(str(db_path)) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT id, pergunta, gabarito, tipo FROM tcc_testes_acuracia") as cursor:
                perguntas = [dict(row) for row in await cursor.fetchall()]
                
        for item in perguntas:
            try:
                res = await run_rag_query(item["pergunta"])
                resposta_ia = res.get("resposta", "Erro ao obter resposta.")
            except Exception as e:
                resposta_ia = f"Erro na execução da consulta: {str(e)}"
            
            # Calcula validação e desvio
            validacao_sugerida, desvio = calcular_validacao_sugerida(item["pergunta"], resposta_ia, item["gabarito"])
            
            async with aiosqlite.connect(str(db_path)) as db:
                await db.execute(
                    "UPDATE tcc_testes_acuracia SET resposta_ia = ?, validacao = ?, desvio_percentual = ? WHERE id = ?",
                    (resposta_ia, validacao_sugerida, desvio, item["id"])
                )
                await db.commit()
                
            yield json.dumps({
                "id": item["id"],
                "pergunta": item["pergunta"],
                "esperado": item["gabarito"],
                "tipo": item.get("tipo", "Quantitativa"),
                "resposta_ia": resposta_ia,
                "validacao_sugerida": validacao_sugerida,
                "desvio_percentual": desvio
            }, ensure_ascii=False) + "\n"
            
    return StreamingResponse(event_generator(), media_type="application/x-ndjson")


@router.get("/testes-acuracia/calculos-python")
async def get_testes_calculos_python():
    from app.services.python_calculator import calcular_testes_python
    from fastapi import HTTPException
    try:
        return calcular_testes_python()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/testes-acuracia/calculos-python/processar")
async def processar_testes_calculos_python():
    from app.services.python_calculator import importar_dados_2025_para_sqlite, calcular_testes_python
    from fastapi import HTTPException
    try:
        importar_dados_2025_para_sqlite(force=True)
        return calcular_testes_python()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
