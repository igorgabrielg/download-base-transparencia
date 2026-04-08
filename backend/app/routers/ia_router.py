from fastapi import APIRouter, BackgroundTasks
from app.services.cognitive_agents import run_cognitive_analysis_background
from app.services.synthesizer import run_cognitive_synthesis_background
from app.services.vector_store import run_vector_indexing_background
from app.models.schemas import ChatRequest, ChatResponse
from app.services.rag_service import run_rag_query

router = APIRouter()

@router.post("/analyze")
async def analyze_data(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_cognitive_analysis_background)
    return {"message": "Análise cognitiva de IA iniciada em background."}


@router.post("/synthesize")
async def synthesize_data(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_cognitive_synthesis_background)
    return {"message": "Consolidação e síntese de IA iniciada em background."}


@router.post("/index")
async def index_data(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_vector_indexing_background)
    return {"message": "Indexação vetorial de IA iniciada em background."}


@router.post("/chat", response_model=ChatResponse)
async def chat_rag(payload: ChatRequest):
    result = await run_rag_query(payload.pergunta)
    return ChatResponse(**result)


@router.post("/pipeline-completo")
async def run_full_pipeline_endpoint(background_tasks: BackgroundTasks):
    from app.services.pipeline_service import run_full_pipeline_background
    background_tasks.add_task(run_full_pipeline_background)
    return {"message": "Pipeline completo de processamento (Normalização até Indexação) iniciado em background."}



