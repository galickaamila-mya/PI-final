from models.financial_literacy import FinancialLiteracyModel

profile = {
    "age": 28, "income": 60000, "savings": 10000,
    "expenses": 45000, "debt": 5000,
    "has_emergency_fund": False, "has_budget": True, "has_insurance": True,
}

result = FinancialLiteracyModel().analyze_profile(profile, "Как мне лучше распределить бюджет?")
print(result)
