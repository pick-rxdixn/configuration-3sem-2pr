import argparse
import sys
from typing import Optional


class DependencyGraphVisualizer:

    def __init__(self):
        self.config = {}

    def parse_arguments(self) -> argparse.Namespace:
        parser = argparse.ArgumentParser(
            description='Инструмент визуализации графа зависимостей пакетов',
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )

        parser.add_argument(
            '--package',
            type=str,
            required=True,
            help='Имя анализируемого пакета'
        )

        source_group = parser.add_mutually_exclusive_group(required=True)
        source_group.add_argument(
            '--repository',
            type=str,
            help='URL-адрес репозитория пакетов'
        )
        source_group.add_argument(
            '--file-repo',
            type=str,
            help='Путь к файлу тестового репозитория'
        )

        parser.add_argument(
            '--test-mode',
            action='store_true',
            help='Режим работы с тестовым репозиторием'
        )
        parser.add_argument(
            '--version',
            type=str,
            default='latest',
            help='Версия пакета (по умолчанию: latest)'
        )
        parser.add_argument(
            '--filter',
            type=str,
            dest='filter_substring',
            help='Подстрока для фильтрации пакетов'
        )

        return parser.parse_args()

    def validate_arguments(self, args: argparse.Namespace) -> bool:
        try:
            if not args.package or not args.package.strip():
                raise ValueError("Имя пакета не может быть пустым")

            if args.repository:
                if not args.repository.startswith(('http://', 'https://')):
                    raise ValueError("URL репозитория должен начинаться с http:// или https://")

            if args.file_repo:
                if not args.file_repo.strip():
                    raise ValueError("Путь к файлу репозитория не может быть пустым")

            if args.version != 'latest':
                if not all(c.isdigit() or c == '.' for c in args.version):
                    raise ValueError("Версия пакета должна содержать только цифры и точки")

            return True

        except ValueError as e:
            print(f"Ошибка валидации параметров: {e}", file=sys.stderr)
            return False

    def display_configuration(self, args: argparse.Namespace):
        print("Конфигурация приложения:")
        print("=" * 40)

        config_items = [
            ("Имя пакета", args.package),
            ("URL репозитория", args.repository or "Не указан"),
            ("Файл репозитория", args.file_repo or "Не указан"),
            ("Режим тестирования", "Да" if args.test_mode else "Нет"),
            ("Версия пакета", args.version),
            ("Фильтр пакетов", args.filter_substring or "Не указан")
        ]

        for key, value in config_items:
            print(f"{key:<25}: {value}")

        print("=" * 40)

    def run(self):
        try:
            args = self.parse_arguments()

            if not self.validate_arguments(args):
                sys.exit(1)

            self.display_configuration(args)

            print("\nПриложение успешно запущено с указанной конфигурацией.")
            print("На этапе 1 выполняется только вывод параметров.")

        except argparse.ArgumentError as e:
            print(f"Ошибка в аргументах командной строки: {e}", file=sys.stderr)
            sys.exit(1)
        except KeyboardInterrupt:
            print("\nПриложение прервано пользователем", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Неожиданная ошибка: {e}", file=sys.stderr)
            sys.exit(1)


def main():
    visualizer = DependencyGraphVisualizer()
    visualizer.run()


if __name__ == "__main__":
    main()