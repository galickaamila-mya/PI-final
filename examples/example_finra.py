from project_data.finra_nfcs_parser import FINRANFCSParser
from models.financial_literacy import FinancialLiteracyModel

responses = {
    "A3a": 35, "A8": 5, "J1": 2, "J2": 1, "J4": 1,
    "N1": 1, "N2": 1, "N9": 2, "O1": 1, "O2": 1,
    "M1": 1, "M2": 2, "M3": 1, "M4": 3, "M5": 2, "M6": 1,
}

parser = FINRANFCSParser()
profile = parser.responses_to_profile(responses)
knowledge_score = parser.calculate_financial_knowledge_score(responses)
result = FinancialLiteracyModel().analyze_profile(profile)

print("Profile:", profile)
print(f"FINRA knowledge score: {knowledge_score}/6")
print("Analysis:", result)
