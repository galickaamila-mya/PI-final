from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models.financial_qa import FinancialQAModel
from models.financial_literacy import FinancialLiteracyModel
from api.schemas import (
    FinancialQARequest, FinancialQAResponse, BatchQARequest,
    BatchQARequest, MetricsRequest,    UserProfile, FinancialLiteracyRequest, FinancialLiteracyResponse,
    HealthResponse,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
qa_model: FinancialQAModel | None = None
literacy_model: FinancialLiteracyModel | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global qa_model, literacy_model
    logger.info("Загрузка моделей...")
    qa_model = FinancialQAModel()
    literacy_model = FinancialLiteracyModel()
    logger.info("Модели загружены")
    yield
    qa_model = None
    literacy_model = None


app = FastAPI(
    title="Financial ML API",
    version="2.0.0",
    description="Две задачи: Financial QA и Financial Literacy.",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)


@app.get("/", tags=["Health"])
def root():
    return {"message": "Financial ML API", "docs": "/docs", "health": "/health"}


@app.get("/health", response_model=HealthResponse, tags=["Health"])
def health():
    loaded = qa_model is not None and literacy_model is not None
    return HealthResponse(status="ok" if loaded else "loading", models_loaded=loaded, message="API работает" if loaded else "Модели загружаются")


def get_qa() -> FinancialQAModel:
    if qa_model is None:
        raise HTTPException(503, "Модель Financial QA ещё не загружена")
    return qa_model


def get_literacy() -> FinancialLiteracyModel:
    if literacy_model is None:
        raise HTTPException(503, "Модель Financial Literacy ещё не загружена")
    return literacy_model


@app.post("/api/v1/financial-qa", response_model=FinancialQAResponse, tags=["Financial QA"])
def financial_qa(request: FinancialQARequest):
    try:
        return get_qa().answer_question(request.question, request.context, request.max_answer_length)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc


@app.post("/api/v1/financial-qa/batch", tags=["Financial QA"])
def financial_qa_batch(request: BatchQARequest):
    return {"results": get_qa().batch_answer(request.questions, request.context)}


@app.post("/api/v1/financial-qa/extract-metrics", tags=["Financial QA"])
def extract_metrics(context: str):
    return {"metrics": get_qa().extract_financial_metrics(context)}


@app.post("/api/v1/financial-literacy", response_model=FinancialLiteracyResponse, tags=["Financial Literacy"])
def financial_literacy(request: FinancialLiteracyRequest):
    return get_literacy().analyze_profile(request.user_profile.model_dump(), request.question)
