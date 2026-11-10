"""Точка входа: визуализатор графа зависимостей пакетов Maven."""

import sys

from config import ConfigError, load_config
from graph import build_graph, format_cycle, format_graph, load_order
from maven import (
	UNKNOWN_VERSION, RepoError, direct_dependencies, is_transitive)
from repo_file import RepoFileError, load_repo_file

EXIT_OK = 0
EXIT_REPO_ERROR = 1
EXIT_CONFIG_ERROR = 2


def print_errors(messages, prefix="ошибка"):
	"""Вывести сообщения об ошибках в поток ошибок."""
	for message in messages:
		print(f"{prefix}: {message}", file=sys.stderr)


def maven_provider(repo):
	"""Вернуть функцию получения транзитивных зависимостей из Maven."""

	def get_deps(node):
		"""Вернуть зависимости пакета groupId:artifactId:версия."""
		group, artifact, version = node.split(":")
		if version == UNKNOWN_VERSION:
			return []
		try:
			deps = direct_dependencies(repo, f"{group}:{artifact}", version)
		except RepoError as error:
			print_errors([str(error)], "предупреждение")
			return []
		return [
			f"{dep['name']}:{dep['version']}"
			for dep in deps if is_transitive(dep)
		]

	return get_deps


def make_graph(config):
	"""Построить граф зависимостей для тестового или Maven-репозитория."""
	if config["test_mode"]:
		repo = load_repo_file(config["repo"])
		if config["package"] not in repo:
			raise RepoError(
				f"пакет {config['package']} не найден в тестовом репозитории")
		return build_graph(config["package"], lambda node: repo.get(node, []))
	direct_dependencies(config["repo"], config["package"], config["version"])
	root = f"{config['package']}:{config['version']}"
	return build_graph(root, maven_provider(config["repo"]))


def print_graph(graph, cycles):
	"""Вывести граф зависимостей и найденные циклы."""
	print("Граф зависимостей (с учётом транзитивности):")
	for line in format_graph(graph):
		print(f"  {line}")
	if not cycles:
		print("Циклических зависимостей нет")
		return
	print("Найдены циклические зависимости:")
	for cycle in cycles:
		print(f"  {format_cycle(cycle)}")


def print_load_order(graph, cycles):
	"""Вывести порядок загрузки зависимостей корневого пакета."""
	root = next(iter(graph))
	print(f"Порядок загрузки зависимостей {root}:")
	for number, node in enumerate(load_order(graph, root), start=1):
		print(f"  {number}. {node}")
	if cycles:
		print("Внимание: есть циклы, для них строгого порядка нет:")
		for cycle in cycles:
			print(f"  {format_cycle(cycle)}")


def main(argv=None):
	"""Запустить приложение и вернуть код завершения."""
	try:
		config = load_config(argv)
	except ConfigError as error:
		print_errors(error.args[0])
		return EXIT_CONFIG_ERROR
	try:
		graph, cycles = make_graph(config)
	except (RepoError, RepoFileError) as error:
		print_errors([str(error)])
		return EXIT_REPO_ERROR
	if config["load_order"]:
		print_load_order(graph, cycles)
	else:
		print_graph(graph, cycles)
	return EXIT_OK


if __name__ == "__main__":
	sys.exit(main())
