import subprocess
import sys


def run_demo():

    examples = [
        [
            "Демонстрация: получение зависимостей для serde",
            ["py", "KONF2_2.py", "--package", "serde", "--repository", "https://crates.io"]
        ],
        [
            "Демонстрация: получение зависимостей для tokio с фильтром",
            ["py", "KONF2_2.py", "--package", "tokio", "--repository", "https://crates.io", "--filter",
             "time"]
        ],
        [
            "Демонстрация: несуществующий пакет",
            ["py", "KONF2_2.py", "--package", "nonexistent_package_12345", "--repository",
             "https://crates.io"]
        ]
    ]

    print("Демонстрация этапа 2: Сбор данных из Cargo репозитория")
    print("=" * 60)

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
    run_demo()