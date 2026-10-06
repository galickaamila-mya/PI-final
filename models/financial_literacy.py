from __future__ import annotations

from typing import Any


class FinancialLiteracyModel:

    # детерминированный анализ финансового профиля

    def __init__(self) -> None:
        self.weights = {
            "emergency_fund": 2.5,
            "savings_rate": 2.0,
            "debt_to_income": 2.0,
            "budgeting": 1.5,
            "investment_knowledge": 1.0,
            "insurance": 1.0,
        }

    def analyze_profile(
        self,
        user_profile: dict[str, Any],
        question: str | None = None,
    ) -> dict[str, Any]:
        income = max(float(user_profile.get("income", 0)), 0.0)
        expenses = max(float(user_profile.get("expenses", 0)), 0.0)
        savings = max(float(user_profile.get("savings", 0)), 0.0)
        debt = max(float(user_profile.get("debt", 0)), 0.0)

        monthly_income = income / 12 if income else 0.0
        monthly_expenses = expenses / 12 if expenses else 0.0
        disposable = monthly_income - monthly_expenses
        savings_rate = (disposable / monthly_income * 100) if monthly_income else 0.0
        debt_to_income = (debt / income * 100) if income else 0.0
        emergency_min = monthly_expenses * 3
        emergency_max = monthly_expenses * 6

        has_fund = bool(user_profile.get("has_emergency_fund", False))
        has_budget = bool(user_profile.get("has_budget", False))
        has_insurance = bool(user_profile.get("has_insurance", False))

        scores = {
            "emergency_fund": self._fund_score(has_fund, savings, emergency_min),
            "savings_rate": self._savings_score(savings_rate),
            "debt_to_income": self._debt_score(debt_to_income),
            "budgeting": self.weights["budgeting"] if has_budget else 0.0,
            "investment_knowledge": 0.5,
            "insurance": self.weights["insurance"] if has_insurance else 0.0,
        }
        literacy_score = round(sum(scores.values()), 1)

        risk_points = 0
        if literacy_score < 4:
            risk_points += 2
        elif literacy_score < 7:
            risk_points += 1
        if debt_to_income > 50:
            risk_points += 2
        elif debt_to_income > 43:
            risk_points += 1
        if not has_fund or savings < monthly_expenses:
            risk_points += 1

        risk_level = "high" if risk_points >= 3 else "medium" if risk_points >= 1 else "low"
        recommendations = self._recommendations(
            has_fund, savings, emergency_min, emergency_max, savings_rate,
            debt, debt_to_income, has_budget, has_insurance, monthly_income,
        )

        advice = self._advice(question, recommendations, literacy_score, risk_level)

        return {
            "literacy_score": literacy_score,
            "risk_level": risk_level,
            "recommendations": recommendations,
            "advice": advice,
            "metrics": {
                "savings_rate": round(savings_rate, 1),
                "debt_to_income_ratio": round(debt_to_income, 1),
                "monthly_disposable": round(disposable, 2),
                "recommended_emergency_fund": f"${emergency_min:,.0f}-${emergency_max:,.0f}",
            },
        }

    def _fund_score(self, has_fund: bool, savings: float, minimum: float) -> float:
        if has_fund and savings >= minimum:
            return self.weights["emergency_fund"]
        if savings >= minimum * 0.5:
            return self.weights["emergency_fund"] * 0.5
        return 0.0

    def _savings_score(self, rate: float) -> float:
        if rate >= 20:
            return 2.0
        if rate >= 10:
            return 1.4
        if rate >= 5:
            return 0.8
        return 0.0

    def _debt_score(self, ratio: float) -> float:
        if ratio < 36:
            return 2.0
        if ratio < 43:
            return 1.0
        return 0.0

    def _recommendations(self, has_fund, savings, minimum, maximum, savings_rate,
                         debt, debt_ratio, has_budget, has_insurance,
                         monthly_income) -> list[str]:
        result: list[str] = []
        if not has_fund or savings < minimum:
            result.append(f"Создайте резервный фонд: ${minimum:,.0f}-${maximum:,.0f}.")
        if debt > 0 and debt_ratio > 36:
            result.append(f"Составьте план погашения долга ${debt:,.0f}; отношение долг/доход составляет {debt_ratio:.1f}%.")
        if savings_rate < 20:
            result.append(f"Стремитесь откладывать до 20% дохода, ориентир — ${monthly_income * 0.2:,.0f} в месяц.")
        if not has_budget:
            result.append("Начните вести бюджет и ежемесячно сравнивайте доходы с расходами.")
        if not has_insurance:
            result.append("Проверьте необходимость медицинского страхования и страхования жизни.")
        if has_fund and savings >= minimum and debt_ratio < 36:
            result.append("После формирования резерва рассмотрите диверсифицированные долгосрочные инвестиции.")
        return result

    def _advice(self, question, recommendations, score, risk) -> str:
        topic = question or "общего финансового анализа"
        top = "\n".join(f"{i + 1}. {item}" for i, item in enumerate(recommendations[:4]))
        return (
            f"Ответ по теме: {topic}\n\n"
            f"Оценка финансовой грамотности: {score}/10. Уровень риска: {risk}.\n\n"
            f"Приоритетные действия:\n{top}\n\n"
            "Это образовательный расчёт по введённым данным; перед финансовыми решениями учитывайте свои условия и региональные правила."
        )
