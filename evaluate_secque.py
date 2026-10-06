"""Загрузка SECQUE и пример расчёта EM/F1."""
from collections import Counter
import re
import string
from datasets import load_dataset
from models.financial_qa import FinancialQAModel


def normalize(text: str) -> list[str]:
    text = text.lower().translate(str.maketrans("", "", string.punctuation))
    return text.split()


def exact_match(prediction: str, reference: str) -> float:
    return float(" ".join(normalize(prediction)) == " ".join(normalize(reference)))


def f1(prediction: str, reference: str) -> float:
    pred, ref = normalize(prediction), normalize(reference)
    common = Counter(pred) & Counter(ref)
    same = sum(common.values())
    if not same:
        return 0.0
    precision = same / len(pred)
    recall = same / len(ref)
    return 2 * precision * recall / (precision + recall)


if __name__ == "__main__":
    dataset = load_dataset("nogabenyoash/SecQue")
    split = "test" if "test" in dataset else next(iter(dataset))
    rows = dataset[split]
    print("Split:", split, "Rows:", len(rows))
    print("Columns:", rows.column_names)
    model = FinancialQAModel()
    em_values, f1_values = [], []
    for row in rows.select(range(min(20, len(rows)))):
        question = row.get("question", row.get("Question", ""))
        context = row.get("context", row.get("Context", ""))
        reference = row.get("answer", row.get("Answer", ""))
        if isinstance(reference, dict):
            reference = reference.get("text", [""])[0]
        if not question or not context or not reference:
            continue
        prediction = model.answer_question(question, context)["answer"]
        em_values.append(exact_match(prediction, str(reference)))
        f1_values.append(f1(prediction, str(reference)))
    print("Exact Match:", sum(em_values) / len(em_values) if em_values else 0)
    print("F1:", sum(f1_values) / len(f1_values) if f1_values else 0)
