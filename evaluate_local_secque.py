from __future__ import annotations

import json
import string
from collections import Counter
from pathlib import Path
from models.financial_qa import FinancialQAModel

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"


def normalize(text: str) -> list[str]:
    text = text.lower().translate(str.maketrans("", "", string.punctuation))
    return text.split()


def exact_match(prediction: str, reference: str) -> float:
    return float(normalize(prediction) == normalize(reference))


def f1_score(prediction: str, reference: str) -> float:
    predicted, expected = normalize(prediction), normalize(reference)
    if not predicted or not expected:
        return 0.0
    common = Counter(predicted) & Counter(expected)
    count = sum(common.values())
    if not count:
        return 0.0
    precision = count / len(predicted)
    recall = count / len(expected)
    return 2 * precision * recall / (precision + recall)


def text_value(value) -> str:
    if isinstance(value, dict):
        value = value.get("text", "")
        if isinstance(value, list):
            return str(value[0]) if value else ""
    if isinstance(value, list):
        return str(value[0]) if value else ""
    return str(value)


def main() -> None:
    candidates = list(DATA_DIR.glob("secque_*.jsonl"))
    candidates = [path for path in candidates if "metadata" not in path.name]
    if not candidates:
        raise FileNotFoundError("Сначала запустите import_real_datasets.py")

    input_path = candidates[0]
    model = FinancialQAModel()
    em_values: list[float] = []
    f1_values: list[float] = []

    with input_path.open(encoding="utf-8") as file:
        for index, line in enumerate(file):
            row = json.loads(line)
            question = text_value(row.get("question", row.get("Question", "")))
            context = text_value(row.get("context", row.get("Context", "")))
            reference = text_value(row.get("answer", row.get("Answer", "")))
            if not question or not context or not reference:
                continue
            prediction = model.answer_question(question, context)["answer"]
            em_values.append(exact_match(prediction, reference))
            f1_values.append(f1_score(prediction, reference))
            print(f"{index + 1}. {question[:80]} -> {prediction}")

    print(f"Примеров: {len(em_values)}")
    print(f"Exact Match: {sum(em_values) / len(em_values) if em_values else 0:.4f}")
    print(f"F1-score: {sum(f1_values) / len(f1_values) if f1_values else 0:.4f}")


if __name__ == "__main__":
    main()
