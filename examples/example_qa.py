from pathlib import Path
from models.financial_qa import FinancialQAModel

root = Path(__file__).resolve().parents[1]
context = (root / "project_data" / "sample_sec_filing.txt").read_text(encoding="utf-8")
model = FinancialQAModel()

questions = [
    "What was the total revenue?",
    "What was the net income?",
    "What was the EBITDA?",
    "What were the main risks?",
]

for question in questions:
    result = model.answer_question(question, context)
    print(f"Q: {question}\nA: {result['answer']}\nConfidence: {result['confidence']:.3f}\n")
