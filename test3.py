import subprocess
import sys


def run_demo():

    examples = [
        [
            "Демонстрация 1: Простой граф без циклов",
            ["py", "KONF2_3.py", "--package", "A", "--file-repo", "test_repo.json", "--test-mode",
             "--max-depth", "3"]
        ],
        [
            "Демонстрация 2: Обнаружение циклов",
            ["py", "KONF2_3.py", "--package", "A", "--file-repo", "test_repo.json", "--test-mode"]
        ],
        [
            "Демонстрация 3: С исключением пакетов",
            ["py", "KONF2_3.py", "--package", "A", "--file-repo", "test_repo.json", "--test-mode",
             "--exclude", "G"]
        ],
        [
            "Демонстрация 4: Ограничение глубины",
            ["py", "KONF2_3.py", "--package", "A", "--file-repo", "test_repo.json", "--test-mode",
             "--max-depth", "2"]
        ],
        [
            "Демонстрация 5: Встроенный тестовый репозиторий",
            ["py", "KONF2_3.py", "--package", "serde", "--test-mode"]
        ]
    ]

    print("Демонстрация этапа 3: Основные операции с графом зависимостей")
    print("=" * 70)

    for description, command in examples:
        print(f"\n{description}")
        print(">" * 70)
        try:
            result = subprocess.run(command, capture_output=True, text=True)
            print(result.stdout)
            if result.stderr:
                print("STDERR:", result.stderr)
        except Exception as e:
            print(f"Ошибка выполнения: {e}")


if __name__ == "__main__":
    run_demo()