from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any
from pypdf import PdfReader


class FINRANFCSParser:

    def __init__(self, pdf_path: str | Path | None = None) -> None:
        base = Path(__file__).resolve().parent
        self.pdf_path = Path(pdf_path) if pdf_path else base / "NFCS_2024_Questionnaire.pdf"
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF FINRA не найден: {self.pdf_path}")
        self.questions: dict[str, str] = {}
        self._parse()

    @staticmethod
    def _clean(value: str) -> str:
        return " ".join(value.split())

    def _parse(self) -> None:
        reader = PdfReader(str(self.pdf_path))
        text = "\n".join((page.extract_text() or "") for page in reader.pages)
        pattern = re.compile(r"#\s*([A-Za-z0-9]+)\)\s*(.*?)(?=\n#\s*[A-Za-z0-9]+\)|\Z)", re.S)
        for qid, body in pattern.findall(text):
            body = self._clean(body)
            if body:
                self.questions[qid] = body

    def get_all_questions(self) -> dict[str, str]:
        return self.questions.copy()

    def get_key_questions(self) -> dict[str, dict[str, str]]:
        descriptions = {
            "A3a": "Возраст", "A8": "Годовой доход", "A11": "Финансово зависимые дети",
            "J1": "Траты больше дохода", "J2": "Резервный фонд", "J3": "Финансовые цели",
            "J4": "Ведение бюджета", "N1": "Кредитная карта", "N2": "Полное погашение кредитки",
            "N9": "Студенческий кредит", "L1": "Пенсионный счёт", "L3": "Инвестиции",
            "O1": "Медицинская страховка", "O2": "Страхование жизни",
            "M1": "Сложный процент", "M2": "Инфляция", "M3": "Стоимость денег во времени",
            "M4": "Диверсификация", "M5": "Облигации", "M6": "Ипотека",
        }
        return {
            qid: {"description": description, "text": self.questions.get(qid, "Формулировка не найдена")}
            for qid, description in descriptions.items()
        }

    @staticmethod
    def _yes(value: Any) -> bool:
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.strip().lower() in {"1", "yes", "да", "true"}
        return value == 1

    @staticmethod
    def _income(value: Any) -> float:
        ranges = {1: 15_000, 2: 20_000, 3: 35_000, 4: 50_000, 5: 75_000, 6: 100_000, 7: 150_000, 8: 200_000}
        try:
            number = float(value)
            if int(number) in ranges:
                return float(ranges[int(number)])
            if number > 10:
                return number
        except (TypeError, ValueError):
            pass
        return 50_000.0

    def responses_to_profile(self, responses: dict[str, Any]) -> dict[str, Any]:
        income = self._income(responses.get("A8"))
        expenses = income * (1.1 if self._yes(responses.get("J1")) else 0.75)
        emergency = self._yes(responses.get("J2"))
        savings = expenses / 12 * 4 if emergency else 0.0
        debt = 0.0
        if self._yes(responses.get("N1")) and not self._yes(responses.get("N2")):
            debt += income * 0.1
        if self._yes(responses.get("N9")):
            debt += income * 0.2
        return {
            "age": int(float(responses.get("A3a", 30))), "income": income,
            "savings": savings, "expenses": expenses, "debt": debt,
            "has_emergency_fund": emergency,
            "has_budget": self._yes(responses.get("J4")),
            "has_insurance": self._yes(responses.get("O1")) or self._yes(responses.get("O2")),
        }

    def calculate_financial_knowledge_score(self, responses: dict[str, Any]) -> int:
        correct = {"M1": 1, "M2": 2, "M3": 1, "M4": 3, "M5": 2, "M6": 1}
        return sum(responses.get(qid) == answer for qid, answer in correct.items())

    def calculate_financial_literacy_score(self, responses: dict[str, Any]) -> int:
        return self.calculate_financial_knowledge_score(responses)

    def export_questions(self, output_path: str | Path = "finra_questions.json") -> None:
        with Path(output_path).open("w", encoding="utf-8") as file:
            json.dump(self.questions, file, ensure_ascii=False, indent=2)
