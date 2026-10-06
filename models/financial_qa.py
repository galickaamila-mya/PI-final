from __future__ import annotations

from typing import Any
import logging
import torch
from transformers import pipeline

logger = logging.getLogger(__name__)


class FinancialQAModel:

    # функция извлекает ответы из финансового контекста

    def __init__(self, model_name: str = "deepset/roberta-base-squad2") -> None:
        self.model_name = model_name
        self.device = 0 if torch.cuda.is_available() else -1
        self.pipeline = pipeline(
            "question-answering",
            model=model_name,
            device=self.device,
        )

    def answer_question(
        self,
        question: str,
        context: str,
        max_answer_length: int = 100,
        min_score: float = 0.01,
    ) -> dict[str, Any]:
        if not question.strip():
            raise ValueError("Вопрос не должен быть пустым")
        if not context.strip():
            raise ValueError("Контекст не должен быть пустым")

        result = self.pipeline(
            question=question,
            context=context,
            handle_impossible_answer=True,
        )

        answer = str(result.get("answer", "")).strip()
        score = float(result.get("score", 0.0))

        if score < min_score or not answer:
            answer = "Ответ не найден с достаточной уверенностью"

        return {
            "answer": answer,
            "confidence": score,
            "start_position": int(result.get("start", 0)),
            "end_position": int(result.get("end", 0)),
        }

    def batch_answer(self, questions: list[str], context: str) -> list[dict[str, Any]]:
        return [
            {"question": question, **self.answer_question(question, context)}
            for question in questions
        ]

    def extract_financial_metrics(self, context: str) -> dict[str, str]:
        questions = {
            "revenue": "What was the total revenue?",
            "net_income": "What was the net income?",
            "ebitda": "What was the EBITDA?",
            "total_assets": "What were the total assets?",
            "total_liabilities": "What were the total liabilities?",
            "eps": "What was the earnings per share?",
        }
        output: dict[str, str] = {}
        for key, question in questions.items():
            result = self.answer_question(question, context, min_score=0.05)
            output[key] = result["answer"]
        return output
