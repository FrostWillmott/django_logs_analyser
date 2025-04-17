#!/usr/bin/env python3
import argparse
import os
import sys
from concurrent.futures import ProcessPoolExecutor
from typing import List

# Импортируем именно registry из пакета reports
from django_logs_analyser.reports import registry


def run(argv: List[str] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Analyze Django logs and generate reports"
    )
    parser.add_argument(
        "paths",
        nargs="+",
        help="Paths to Django log files",
    )
    parser.add_argument(
        "--report",
        required=True,
        choices=list(registry.keys()),
        help="Name of the report to generate",
    )
    args = parser.parse_args(argv)

    # Проверка существования файлов
    for path in args.paths:
        if not os.path.isfile(path):
            print(f"Error: File not found: {path}", file=sys.stderr)
            return 1

    # Достаем класс нужного отчёта из registry
    report_cls = registry[args.report]
    report = report_cls()

    # Обработка файлов параллельно
    results = []
    with ProcessPoolExecutor() as executor:
        futures = [executor.submit(report.process_file, path) for path in args.paths]
        for future in futures:
            try:
                results.append(future.result())
            except Exception as e:
                print(f"Error processing file: {e}", file=sys.stderr)
                return 1

    # Объединяем результаты и выводим
    combined = report.combine(results)
    output = report.render(combined)
    print(output)
    return 0


if __name__ == "__main__":
    sys.exit(run())
