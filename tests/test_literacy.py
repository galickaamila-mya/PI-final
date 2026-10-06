import pytest
from models.financial_literacy import FinancialLiteracyModel


@pytest.fixture
def base_profile():
    return {
        "age": 34,
        "income": 120000,
        "savings": 45000,
        "expenses": 65300,
        "debt": 0,
        "has_emergency_fund": True,
        "has_budget": True,
        "has_insurance": False
    }


def test_literacy_is_deterministic(base_profile):
    model = FinancialLiteracyModel()

    res1 = model.analyze_profile(base_profile)
    res2 = model.analyze_profile(base_profile)

    assert res1 == res2
