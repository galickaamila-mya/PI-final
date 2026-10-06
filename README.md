# Полная инструкция по запуску

## Установка

Проект рассчитан на Python 3.13 x64.

```bash
python -m venv venv
```

Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

Linux/macOS:

```bash
source venv/bin/activate
```

```bash
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

Если PyTorch не устанавливается, установите его отдельной командой для вашей ОС с официальной страницы PyTorch, затем повторите установку остальных пакетов.

## Запуск API

```bash
python run_api.py
```

Откройте Swagger:

```text
http://127.0.0.1:8000/docs
```

OpenAPI JSON:

```text
http://127.0.0.1:8000/openapi.json
```

Проверка:

```text
http://127.0.0.1:8000/health
```

При первом запуске модель QA скачивается из Hugging Face, поэтому требуется интернет.

## Запрос в Swagger: Financial QA

Откройте `POST /api/v1/financial-qa`, нажмите `Try it out`, вставьте:

```json
{
  "question": "What was the total revenue?",
  "context": "The company reported total revenue of $394.3 billion in 2024.",
  "max_answer_length": 100
}
```

Все три поля находятся внутри JSON-тела запроса.

## Запрос в Swagger: Financial Literacy

Откройте `POST /api/v1/financial-literacy`, нажмите `Try it out`, вставьте:

```json
{
  "user_profile": {
    "age": 28,
    "income": 60000,
    "savings": 10000,
    "expenses": 45000,
    "debt": 5000,
    "has_emergency_fund": false,
    "has_budget": true,
    "has_insurance": true
  },
  "question": "Как мне начать копить деньги?"
}
```


## Импорт реальных датасетов

В корне есть файл:

```text
import_real_datasets.py
```

Он загружает SECQUE и FinLit India из Hugging Face и сохраняет записи в папку `data/`.

```bash
python import_real_datasets.py
```

Для полной выгрузки в файле замените `max_rows=100` на `max_rows=None`.

После импорта для оценки SECQUE:

```bash
python evaluate_local_secque.py
```

## FINRA NFCS

PDF находится в:

```text
project_data/NFCS_2024_Questionnaire.pdf
```

Парсер находится в:

```text
project_data/finra_nfcs_parser.py
```

Пример:

```bash
python examples/example_finra.py
```

Приложенный PDF — опросник, а не таблица заполненных ответов. Для анализа реальных респондентов дополнительно нужны файл ответов и официальный codebook.

## Проверка проекта

Проверка синтаксиса:

```bash
python -m compileall -q .
```

Проверка API-схем без загрузки тяжёлой QA-модели:

```bash
pytest -q tests/test_api.py
```

Полная демонстрация:

```bash
python examples/example_literacy.py
python examples/example_finra.py
```
