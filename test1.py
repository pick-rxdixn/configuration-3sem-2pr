import subprocess
import sys


def run_demo():

    examples = [
        [
            "Правильный пример с репозиторием:",
            ["py", "KONF2_1.py", "--package", "numpy", "--repository", "https://pypi.org"]
        ],
        [
            "Правильный пример с файлом репозитория:",
            ["py", "KONF2_1.py", "--package", "requests", "--file-repo", "./test_repo", "--test-mode"]
        ],
        [
            "Правильный пример с версией и фильтром:",
            ["py", "KONF2_1.py", "--package", "django", "--repository", "https://pypi.org", "--version",
             "3.2", "--filter", "security"]
        ],
        [
            "Ошибка: отсутствует обязательный параметр --package:",
            ["py", "KONF2_1.py", "--repository", "https://pypi.org"]
        ],
        [
            "Ошибка: отсутствует источник данных:",
            ["py", "KONF2_1.py", "--package", "numpy"]
        ],
        [
            "Ошибка: неверный URL:",
            ["py", "KONF2_1.py", "--package", "numpy", "--repository", "invalid_url"]
        ]
    ]

    for description, command in examples:
        print(f"\n{description}")
        print(">" * 50)
        try:
            result = subprocess.run(command, capture_output=True, text=True)
            print(result.stdout)
            if result.stderr:
                print("STDERR:", result.stderr)
        except Exception as e:
            print(f"Ошибка выполнения: {e}")


if __name__ == "__main__":
    print("Демонстрация работы инструмента визуализации графа зависимостей")
    print("=" * 60)
    run_demo()