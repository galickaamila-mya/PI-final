from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import requests
from datasets import load_dataset


ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"

HEADERS = {
    "User-Agent": "financial-ml-project/1.0"
}


def save_jsonl(
    rows: list[dict[str, Any]],
    output_path: Path,
) -> None:
    """
    Сохранить список записей в JSONL.
    """
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with output_path.open(
        "w",
        encoding="utf-8",
    ) as file:
        for row in rows:
            file.write(
                json.dumps(
                    row,
                    ensure_ascii=False,
                    default=str,
                )
                + "\n"
            )


def request_json(url: str) -> Any:
    """
    Выполнить GET-запрос и вернуть JSON.
    """
    response = requests.get(
        url,
        headers=HEADERS,
        timeout=120,
    )

    response.raise_for_status()
    return response.json()


def get_repository_files(
    owner: str,
    repository: str,
) -> list[str]:
    """
    Получить список файлов репозитория Hugging Face.
    """
    api_url = (
        f"https://huggingface.co/api/datasets/"
        f"{owner}/{repository}/tree/main"
        "?recursive=true"
    )

    data = request_json(api_url)

    paths: list[str] = []

    for item in data:
        if item.get("type") == "file":
            path = item.get("path")

            if path:
                paths.append(path)

    return paths


def is_data_file(path: str) -> bool:
    """
    Проверить, является ли файл поддерживаемым файлом данных.
    """
    lower_path = path.lower()

    supported_extensions = (
        ".json",
        ".jsonl",
        ".csv",
        ".tsv",
        ".parquet",
        ".json.gz",
        ".csv.gz",
        ".jsonl.gz",
    )

    return lower_path.endswith(supported_extensions)


def download_file(
    owner: str,
    repository: str,
    file_path: str,
    output_path: Path,
) -> None:
    """
    Скачать файл из репозитория Hugging Face.
    """
    url = (
        f"https://huggingface.co/datasets/"
        f"{owner}/{repository}/resolve/main/"
        f"{file_path}?download=true"
    )

    print(f"Скачивание:\n{url}")

    response = requests.get(
        url,
        headers=HEADERS,
        timeout=300,
    )

    response.raise_for_status()

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path.write_bytes(response.content)

    print(
        f"Сохранено: {output_path} "
        f"({len(response.content):,} bytes)"
    )


def flatten_json_data(data: Any) -> list[dict[str, Any]]:
    """
    Привести разные структуры JSON к списку объектов.
    """
    if isinstance(data, list):
        return [
            item if isinstance(item, dict) else {"value": item}
            for item in data
        ]

    if isinstance(data, dict):
        # Частые варианты структуры:
        # {"data": [...]}
        # {"train": [...]}
        # {"questions": [...]}
        for key in (
            "data",
            "train",
            "test",
            "validation",
            "questions",
            "records",
            "items",
        ):
            value = data.get(key)

            if isinstance(value, list):
                return [
                    item if isinstance(item, dict) else {"value": item}
                    for item in value
                ]

        return [data]

    return [{"value": data}]


def inspect_json_file(
    path: Path,
    max_rows: int = 100,
) -> None:
    """
    Прочитать JSON-файл и сохранить нормализованную JSONL-копию.
    """
    print(f"Обработка JSON: {path}")

    try:
        with path.open(
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)

        rows = flatten_json_data(data)

        output_path = DATA_DIR / f"{path.stem}.jsonl"
        save_jsonl(rows[:max_rows], output_path)

        print(
            f"Нормализовано строк: {min(len(rows), max_rows)}"
        )

    except Exception as error:
        print(f"Не удалось прочитать JSON {path}: {error}")


def download_repository_data(
    owner: str,
    repository: str,
    prefix: str,
    max_rows: int = 100,
) -> None:
    """
    Скачать файлы данных из репозитория напрямую.
    """
    print(
        f"\nПоиск файлов в "
        f"{owner}/{repository}"
    )

    try:
        paths = get_repository_files(
            owner,
            repository,
        )
    except Exception as error:
        print(f"Не удалось получить список файлов: {error}")
        return

    data_files = [
        path
        for path in paths
        if is_data_file(path)
    ]

    if not data_files:
        print(
            "Поддерживаемые файлы не найдены.\n"
            "Найденные файлы репозитория:"
        )

        for path in paths[:100]:
            print(f"  {path}")

        return

    print("Найдены файлы данных:")

    for path in data_files:
        print(f"  {path}")

    for file_path in data_files:
        filename = Path(file_path).name
        output_path = DATA_DIR / f"{prefix}_{filename}"

        try:
            download_file(
                owner=owner,
                repository=repository,
                file_path=file_path,
                output_path=output_path,
            )

            if output_path.suffix.lower() == ".json":
                inspect_json_file(
                    output_path,
                    max_rows=max_rows,
                )

        except Exception as error:
            print(
                f"Не удалось скачать "
                f"{file_path}: {error}"
            )


def import_secque_with_datasets() -> bool:
    """
    Попробовать загрузить SECQUE стандартным способом.
    """
    print("\nЗагрузка SECQUE через datasets...")

    try:
        dataset = load_dataset(
            "nogabenyoash/SecQue",
        )

        for split_name, split_data in dataset.items():
            limit = min(100, len(split_data))

            rows = [
                dict(split_data[index])
                for index in range(limit)
            ]

            output_path = (
                DATA_DIR
                / f"secque_{split_name}.jsonl"
            )

            save_jsonl(rows, output_path)

            print(
                f"SECQUE {split_name}: "
                f"{len(rows)} строк"
            )

        return True

    except Exception as error:
        print(
            "Стандартная загрузка SECQUE завершилась "
            f"ошибкой: {error}"
        )
        return False


def main() -> None:
    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    secque_ok = import_secque_with_datasets()

    if not secque_ok:
        download_repository_data(
            owner="nogabenyoash",
            repository="SecQue",
            prefix="secque",
        )

    # FinLit India загружаем напрямую.
    # Это обход ошибки DataFilesNotFoundError.
    download_repository_data(
        owner="rohith2006345",
        repository="finlit-india-complete-dataset",
        prefix="finlit_india",
    )

    print("\nИмпорт завершён.")
    print(f"Файлы находятся в: {DATA_DIR}")


if __name__ == "__main__":
    main()