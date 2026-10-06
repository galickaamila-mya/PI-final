from pydantic import BaseModel, Field
from typing import Optional


class FinancialQARequest(BaseModel):
    question: str = Field(..., min_length=1, examples=["What was the total revenue?"])
    context: str = Field(..., min_length=1, examples=["The company reported revenue of $100 million."])
    max_answer_length: int = Field(default=100, ge=1, le=500)


class MetricsRequest(BaseModel):
    context: str = Field(..., min_length=1)


class FinancialQAResponse(BaseModel):
    answer: str
    confidence: float
    start_position: int
    end_position: int


class BatchQARequest(BaseModel):
    questions: list[str] = Field(..., min_length=1, max_length=50)
    context: str = Field(..., min_length=1)


class UserProfile(BaseModel):
    age: int = Field(..., ge=13, le=120)
    income: float = Field(..., ge=0)
    savings: float = Field(default=0, ge=0)
    expenses: float = Field(default=0, ge=0)
    debt: float = Field(default=0, ge=0)
    has_emergency_fund: bool = False
    has_budget: bool = False
    has_insurance: bool = False


class FinancialLiteracyRequest(BaseModel):
    user_profile: UserProfile
    question: Optional[str] = None


class Metrics(BaseModel):
    savings_rate: float
    debt_to_income_ratio: float
    monthly_disposable: float
    recommended_emergency_fund: str


class FinancialLiteracyResponse(BaseModel):
    literacy_score: float
    risk_level: str
    recommendations: list[str]
    advice: str
    metrics: Metrics


class HealthResponse(BaseModel):
    status: str
    models_loaded: bool
    message: str
