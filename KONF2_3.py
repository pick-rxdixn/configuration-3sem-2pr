import argparse
import sys
import json
import urllib.request
import urllib.error
from typing import Dict, List, Optional, Any, Set, Tuple
from urllib.parse import urljoin


class DependencyGraph:

    def __init__(self):
        self.graph: Dict[str, List[str]] = {}
        self.visited: Set[str] = set()
        self.recursion_stack: Set[str] = set()
        self.cycles: List[List[str]] = []

    def add_dependency(self, package: str, dependency: str):
        if package not in self.graph:
            self.graph[package] = []
        if dependency not in self.graph[package]:
            self.graph[package].append(dependency)

    def build_graph_dfs(self, start_package: str,
                        dependency_fetcher: Any,
                        version: str = "latest",
                        exclude_filter: Optional[str] = None,
                        max_depth: int = 10) -> Dict[str, Any]:
        self.visited.clear()
        self.recursion_stack.clear()
        self.cycles.clear()

        result = {
            'graph': {},
            'cycles': [],
            'packages_count': 0,
            'max_depth': 0
        }

        def dfs(current_package: str, depth: int = 0, path: List[str] = None) -> Set[str]:
            if path is None:
                path = []

            nonlocal result
            result['max_depth'] = max(result['max_depth'], depth)

            if current_package in self.recursion_stack:
                cycle_start = path.index(current_package)
                cycle = path[cycle_start:] + [current_package]
                if cycle not in self.cycles:
                    self.cycles.append(cycle)
                return set()

            if current_package in self.visited:
                return set([current_package])

            self.visited.add(current_package)
            self.recursion_stack.add(current_package)
            path.append(current_package)

            all_dependencies: Set[str] = set()

            try:
                dependencies_data = dependency_fetcher.get_dependencies(current_package, version)

                for dep in dependencies_data:
                    dep_name = dep['name']

                    if exclude_filter and exclude_filter.lower() in dep_name.lower():
                        continue

                    self.add_dependency(current_package, dep_name)
                    all_dependencies.add(dep_name)

                    if depth < max_depth:
                        child_deps = dfs(dep_name, depth + 1, path.copy())
                        all_dependencies.update(child_deps)

            except Exception as e:
                print(f"Ошибка при обработке пакета {current_package}: {e}", file=sys.stderr)

            self.recursion_stack.remove(current_package)
            path.pop()

            return all_dependencies

        dfs(start_package)

        result['graph'] = self.graph
        result['cycles'] = self.cycles
        result['packages_count'] = len(self.visited)

        return result


class CargoDependencyFetcher:

    def __init__(self):
        self.api_url = "https://crates.io/api/v1/crates"

    def get_crate_data(self, package_name: str) -> Optional[Dict[str, Any]]:
        try:
            url = f"{self.api_url}/{package_name}"

            req = urllib.request.Request(
                url,
                headers={'User-Agent': 'DependencyGraphVisualizer/1.0'}
            )

            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status == 200:
                    return json.loads(response.read().decode('utf-8'))
                else:
                    return None

        except Exception:
            return None

    def get_dependencies(self, package_name: str, version: str = "latest") -> List[Dict[str, str]]:
        crate_data = self.get_crate_data(package_name)
        if not crate_data:
            return []

        try:
            versions = crate_data.get('versions', [])
            version_data = versions[0] if versions else {}

            deps = version_data.get('dependencies', [])
            dependencies = []

            for dep in deps:
                dep_info = {
                    'name': dep.get('crate_id', ''),
                    'version': dep.get('req', '*'),
                    'kind': dep.get('kind', 'normal')
                }

                if dep_info['name']:
                    dependencies.append(dep_info)

            return dependencies

        except Exception:
            return []


class TestRepositoryFetcher:

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.repository_data: Dict[str, List[str]] = {}
        self.load_repository()

    def load_repository(self):
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if isinstance(data, dict):
                if 'packages' in data:
                    for pkg_info in data['packages']:
                        pkg_name = pkg_info['name']
                        dependencies = pkg_info.get('dependencies', [])
                        self.repository_data[pkg_name] = dependencies
                else:
                    self.repository_data = data

            print(f"Загружен тестовый репозиторий: {len(self.repository_data)} пакетов")

        except Exception as e:
            print(f"Ошибка загрузки тестового репозитория: {e}", file=sys.stderr)
            self.repository_data = self.create_sample_repository()

    def create_sample_repository(self) -> Dict[str, List[str]]:
        print("Создан примерный тестовый репозиторий")

        # Пример графа с циклами и сложными зависимостями
        return {
            "A": ["B", "C"],
            "B": ["D", "E"],
            "C": ["F", "G"],
            "D": ["H", "I"],
            "E": ["B", "J"],  # Цикл: B -> E -> B
            "F": ["G", "K"],
            "G": ["L"],
            "H": ["M"],
            "I": ["N"],
            "J": ["O"],
            "K": ["A", "P"],  # Цикл: A -> C -> F -> K -> A
            "L": ["Q"],
            "M": [],
            "N": ["O"],
            "O": [],
            "P": ["R"],
            "Q": [],
            "R": ["S"],
            "S": ["T"],
            "T": []
        }

    def get_dependencies(self, package_name: str, version: str = "latest") -> List[Dict[str, str]]:
        dependencies = []

        if package_name in self.repository_data:
            for dep_name in self.repository_data[package_name]:
                dependencies.append({
                    'name': dep_name,
                    'version': '1.0',
                    'kind': 'normal'
                })

        return dependencies


class TestDependencyFetcher:

    def get_dependencies(self, package_name: str, version: str = "latest") -> List[Dict[str, str]]:
        test_dependencies = {
            "serde": [
                {"name": "serde_derive", "version": "1.0", "kind": "normal"},
                {"name": "proc-macro2", "version": "1.0", "kind": "normal"},
            ],
            "serde_derive": [
                {"name": "proc-macro2", "version": "1.0", "kind": "normal"},
                {"name": "quote", "version": "1.0", "kind": "normal"},
            ],
            "proc-macro2": [
                {"name": "unicode-ident", "version": "1.0", "kind": "normal"},
            ],
            "quote": [
                {"name": "proc-macro2", "version": "1.0", "kind": "normal"},  # Цикл
            ],
            "unicode-ident": [],
            "tokio": [
                {"name": "tokio-macros", "version": "1.0", "kind": "normal"},
                {"name": "futures", "version": "0.3", "kind": "normal"},
            ],
            "tokio-macros": [
                {"name": "proc-macro2", "version": "1.0", "kind": "normal"},
            ],
            "futures": [
                {"name": "futures-core", "version": "0.3", "kind": "normal"},
            ],
            "futures-core": [],
        }

        return test_dependencies.get(package_name, [])


class DependencyGraphVisualizer:

    def __init__(self):
        self.config = {}
        self.cargo_fetcher = CargoDependencyFetcher()
        self.test_fetcher = TestDependencyFetcher()
        self.graph_analyzer = DependencyGraph()

    def parse_arguments(self) -> argparse.Namespace:
        parser = argparse.ArgumentParser(
            description='Инструмент визуализации графа зависимостей пакетов (Cargo/Rust) - Этап 3',
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )

        parser.add_argument(
            '--package',
            type=str,
            required=True,
            help='Имя анализируемого пакета (обязательно)'
        )

        source_group = parser.add_mutually_exclusive_group()
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

        # Остальные параметры
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
            '--exclude',
            type=str,
            dest='exclude_filter',
            help='Подстрока для исключения пакетов из анализа'
        )
        parser.add_argument(
            '--max-depth',
            type=int,
            default=10,
            help='Максимальная глубина обхода графа (по умолчанию: 10)'
        )

        return parser.parse_args()

    def validate_arguments(self, args: argparse.Namespace) -> bool:
        try:
            if not args.package or not args.package.strip():
                raise ValueError("Имя пакета не может быть пустым")

            if len(args.package.strip()) < 1:
                raise ValueError("Имя пакета должно содержать хотя бы 1 символ")

            if args.file_repo and not args.test_mode:
                raise ValueError("Файловый репозиторий требует включения --test-mode")

            if not args.repository and not args.file_repo:
                if not args.test_mode:
                    raise ValueError("Необходимо указать источник данных или использовать --test-mode")

            if args.max_depth < 1:
                raise ValueError("Максимальная глубина должна быть положительным числом")

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
            ("Фильтр исключения", args.exclude_filter or "Не указан"),
            ("Максимальная глубина", args.max_depth)
        ]

        for key, value in config_items:
            print(f"{key:<25}: {value}")

        print("=" * 50)

    def display_graph_results(self, result: Dict[str, Any], start_package: str):
        graph = result['graph']
        cycles = result['cycles']
        packages_count = result['packages_count']
        max_depth = result['max_depth']

        print(f"\nРезультаты анализа графа зависимостей:")
        print("=" * 60)
        print(f"Начальный пакет: {start_package}")
        print(f"Всего пакетов в графе: {packages_count}")
        print(f"Максимальная глубина зависимостей: {max_depth}")
        print(f"Найдено циклов: {len(cycles)}")

        if cycles:
            print(f"\nОбнаруженные циклические зависимости:")
            for i, cycle in enumerate(cycles, 1):
                print(f"  Цикл {i}: {' -> '.join(cycle)}")

        print(f"\nГраф зависимостей (транзитивные зависимости):")
        print("-" * 40)

        for package, dependencies in sorted(graph.items()):
            if dependencies:
                deps_str = ", ".join(sorted(dependencies))
                print(f"  {package} -> {deps_str}")
            else:
                print(f"  {package} -> (нет зависимостей)")

        print("=" * 60)

    def run(self):
        try:
            args = self.parse_arguments()

            if not self.validate_arguments(args):
                print("\nИсправьте ошибки и попробуйте снова.", file=sys.stderr)
                sys.exit(1)

            self.display_configuration(args)

            dependency_fetcher = None

            if args.test_mode and args.file_repo:
                dependency_fetcher = TestRepositoryFetcher(args.file_repo)
                print(f"\nИспользуется тестовый репозиторий из файла: {args.file_repo}")
            elif args.test_mode:
                dependency_fetcher = self.test_fetcher
                print(f"\nИспользуется встроенный тестовый репозиторий")
            elif args.repository and "crates.io" in args.repository:
                dependency_fetcher = self.cargo_fetcher
                print(f"\nИспользуется Cargo репозиторий (crates.io)")
            else:
                dependency_fetcher = self.test_fetcher
                print(f"\nИспользуется встроенный тестовый репозиторий")

            print(f"\nПостроение графа зависимостей (DFS)...")
            if args.exclude_filter:
                print(f"Исключаются пакеты, содержащие: '{args.exclude_filter}'")

            result = self.graph_analyzer.build_graph_dfs(
                start_package=args.package,
                dependency_fetcher=dependency_fetcher,
                version=args.version,
                exclude_filter=args.exclude_filter,
                max_depth=args.max_depth
            )

            self.display_graph_results(result, args.package)

        except Exception as e:
            print(f"Неожиданная ошибка: {e}", file=sys.stderr)
            sys.exit(1)


def create_test_repository_file():
    test_data = {
        "A": ["B", "C"],
        "B": ["D", "E"],
        "C": ["F", "G"],
        "D": ["H"],
        "E": ["B", "I"],  # Цикл: B -> E -> B
        "F": ["G", "J"],
        "G": ["K"],
        "H": [],
        "I": ["L"],
        "J": ["A", "M"],  # Цикл: A -> C -> F -> J -> A
        "K": [],
        "L": [],
        "M": ["N"],
        "N": ["O"],
        "O": []
    }

    with open('test_repo.json', 'w', encoding='utf-8') as f:
        json.dump(test_data, f, indent=2)

    print("Создан тестовый файл репозитория: test_repo.json")


def main():
    visualizer = DependencyGraphVisualizer()
    visualizer.run()


if __name__ == "__main__":
    try:
        open('test_repo.json', 'r').close()
    except FileNotFoundError:
        create_test_repository_file()

    main()