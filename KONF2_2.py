import argparse
import sys
import json
import urllib.request
import urllib.error
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin


class CargoDependencyFetcher:

    def __init__(self):
        self.base_url = "https://crates.io"
        self.api_url = "https://crates.io/api/v1/crates"

    def get_crate_data(self, package_name: str, version: str = "latest") -> Optional[Dict[str, Any]]:
        try:
            url = f"{self.api_url}/{package_name}"

            print(f"Запрос данных из: {url}")

            req = urllib.request.Request(
                url,
                headers={'User-Agent': 'DependencyGraphVisualizer/1.0'}
            )

            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode('utf-8'))
                    return data
                else:
                    print(f"Ошибка HTTP: {response.status}", file=sys.stderr)
                    return None

        except urllib.error.HTTPError as e:
            if e.code == 404:
                print(f"Пакет '{package_name}' не найден", file=sys.stderr)
            else:
                print(f"Ошибка HTTP при запросе пакета: {e.code}", file=sys.stderr)
            return None
        except urllib.error.URLError as e:
            print(f"Ошибка сети: {e.reason}", file=sys.stderr)
            return None
        except json.JSONDecodeError as e:
            print(f"Ошибка парсинга JSON: {e}", file=sys.stderr)
            return None
        except Exception as e:
            print(f"Неожиданная ошибка при получении данных: {e}", file=sys.stderr)
            return None

    def find_version_data(self, crate_data: Dict[str, Any], target_version: str) -> Optional[Dict[str, Any]]:
        try:
            versions = crate_data.get('versions', [])

            if target_version == "latest":
                return versions[0] if versions else None

            for version_data in versions:
                if version_data.get('num') == target_version:
                    return version_data

            print(f"Версия '{target_version}' не найдена для пакета", file=sys.stderr)
            return None

        except Exception as e:
            print(f"Ошибка при поиске версии: {e}", file=sys.stderr)
            return None

    def extract_dependencies(self, version_data: Dict[str, Any]) -> List[Dict[str, str]]:
        dependencies = []

        try:
            deps = version_data.get('dependencies', [])

            for dep in deps:
                dep_info = {
                    'name': dep.get('crate_id', ''),
                    'version': dep.get('req', '*'),
                    'kind': dep.get('kind', 'normal')
                }

                if dep_info['name']:
                    dependencies.append(dep_info)

            return dependencies

        except Exception as e:
            print(f"Ошибка при извлечении зависимостей: {e}", file=sys.stderr)
            return []

    def get_dependencies(self, package_name: str, version: str = "latest") -> List[Dict[str, str]]:
        print(f"Получение зависимостей для пакета: {package_name} (версия: {version})")

        crate_data = self.get_crate_data(package_name)
        if not crate_data:
            return []

        version_data = self.find_version_data(crate_data, version)
        if not version_data:
            return []

        dependencies = self.extract_dependencies(version_data)
        return dependencies


class TestDependencyFetcher:

    def get_dependencies(self, package_name: str, version: str = "latest") -> List[Dict[str, str]]:
        print(f"Используются тестовые данные для пакета: {package_name}")

        test_dependencies = {
            "serde": [
                {"name": "serde_derive", "version": "1.0", "kind": "normal"},
                {"name": "serde_json", "version": "1.0", "kind": "dev"},
                {"name": "serde_yaml", "version": "0.8", "kind": "normal"}
            ],
            "tokio": [
                {"name": "tokio-macros", "version": "1.0", "kind": "normal"},
                {"name": "tokio-stream", "version": "0.1", "kind": "normal"},
                {"name": "tokio-util", "version": "0.7", "kind": "normal"},
                {"name": "futures", "version": "0.3", "kind": "normal"}
            ],
            "reqwest": [
                {"name": "tokio", "version": "1.0", "kind": "normal"},
                {"name": "hyper", "version": "0.14", "kind": "normal"},
                {"name": "serde", "version": "1.0", "kind": "normal"},
                {"name": "serde_json", "version": "1.0", "kind": "normal"}
            ],
            "clap": [
                {"name": "clap_derive", "version": "3.0", "kind": "normal"},
                {"name": "clap_lex", "version": "0.2", "kind": "normal"},
                {"name": "strum", "version": "0.24", "kind": "normal"}
            ]
        }

        return test_dependencies.get(package_name, [])


class DependencyGraphVisualizer:

    def __init__(self):
        self.config = {}
        self.cargo_fetcher = CargoDependencyFetcher()
        self.test_fetcher = TestDependencyFetcher()

    def parse_arguments(self) -> argparse.Namespace:
        parser = argparse.ArgumentParser(
            description='Инструмент визуализации графа зависимостей пакетов (Cargo/Rust)',
            formatter_class=argparse.RawDescriptionHelpFormatter,

        )

        parser.add_argument(
            '--package',
            type=str,
            required=True,
            help='Имя анализируемого пакета (обязательно)'
        )

        source_group = parser.add_mutually_exclusive_group(required=True)
        source_group.add_argument(
            '--repository',
            type=str,
            help='URL-адрес репозитория пакетов (только https://crates.io)'
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

            if len(args.package.strip()) < 2:
                raise ValueError("Имя пакета должно содержать хотя бы 2 символа")

            if args.repository:
                if not args.repository.startswith(('http://', 'https://')):
                    raise ValueError("URL репозитория должен начинаться с http:// или https://")

            if args.version != 'latest':
                if not all(c.isalnum() or c in '.-_' for c in args.version):
                    raise ValueError("Версия пакета содержит недопустимые символы")

            if args.filter_substring:
                if len(args.filter_substring.strip()) < 2:
                    raise ValueError("Подстрока для фильтрации должна содержать хотя бы 2 символа")

            return True

        except ValueError as e:
            print(f"Ошибка валидации параметров: {e}", file=sys.stderr)
            return False

    def display_configuration(self, args: argparse.Namespace):
        print("Конфигурация приложения:")
        print("=" * 50)

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

        print("=" * 50)

    def display_dependencies(self, dependencies: List[Dict[str, str]], filter_substring: Optional[str] = None):
        if not dependencies:
            print("Прямые зависимости не найдены")
            return

        filtered_deps = dependencies
        if filter_substring:
            filtered_deps = [
                dep for dep in dependencies
                if filter_substring.lower() in dep['name'].lower()
            ]
            print(f"Отфильтровано зависимостей: {len(filtered_deps)} (из {len(dependencies)})")

        print(f"\nПрямые зависимости пакета ({len(filtered_deps)} найдено):")
        print("-" * 60)

        for i, dep in enumerate(filtered_deps, 1):
            kind_display = {
                'normal': 'обычная',
                'dev': 'для разработки',
                'build': 'для сборки'
            }.get(dep['kind'], dep['kind'])

            print(f"{i:2}. {dep['name']:<25} {dep['version']:<15} [{kind_display}]")

        print("-" * 60)

    def run(self):
        try:
            args = self.parse_arguments()

            if not self.validate_arguments(args):
                print("\nИсправьте ошибки и попробуйте снова.", file=sys.stderr)
                sys.exit(1)

            self.display_configuration(args)

            dependencies = []

            if args.test_mode:
                dependencies = self.test_fetcher.get_dependencies(args.package, args.version)
            elif args.repository and "crates.io" in args.repository:
                dependencies = self.cargo_fetcher.get_dependencies(args.package, args.version)

                if not dependencies:
                    print("Не удалось получить данные из API, используем тестовые данные...")
                    dependencies = self.test_fetcher.get_dependencies(args.package, args.version)
            elif args.file_repo:
                print("Работа с файловым репозиторием будет реализована на следующих этапах")
                dependencies = self.test_fetcher.get_dependencies(args.package, args.version)
            else:
                print("Неизвестный источник данных, используем тестовые данные...")
                dependencies = self.test_fetcher.get_dependencies(args.package, args.version)

            self.display_dependencies(dependencies, args.filter_substring)

            if not dependencies:
                print(f"\nНе удалось получить зависимости для пакета '{args.package}'")
                sys.exit(1)

        except argparse.ArgumentError as e:
            print(f"Ошибка в аргументах командной строки: {e}", file=sys.stderr)
            print("\nИспользуйте --help для просмотра справки.", file=sys.stderr)
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