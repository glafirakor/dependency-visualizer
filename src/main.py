"""Точка входа: визуализатор графа зависимостей пакетов Maven."""

import sys

from config import ConfigError, load_config
from maven import RepoError, direct_dependencies

EXIT_OK = 0
EXIT_REPO_ERROR = 1
EXIT_CONFIG_ERROR = 2


def print_errors(messages):
	"""Вывести сообщения об ошибках в поток ошибок."""
	for message in messages:
		print(f"ошибка: {message}", file=sys.stderr)


def format_dependency(dep):
	"""Вернуть строку вида groupId:artifactId:версия [scope]."""
	text = f"{dep['name']}:{dep['version']} [{dep['scope']}]"
	if dep["optional"]:
		text += " (optional)"
	return text


def print_direct(config):
	"""Вывести прямые зависимости пакета из репозитория Maven."""
	deps = direct_dependencies(
		config["repo"], config["package"], config["version"])
	print(f"Прямые зависимости {config['package']}:{config['version']}:")
	if not deps:
		print("  нет зависимостей")
	for dep in deps:
		print(f"  {format_dependency(dep)}")


def main(argv=None):
	"""Запустить приложение и вернуть код завершения."""
	try:
		config = load_config(argv)
	except ConfigError as error:
		print_errors(error.args[0])
		return EXIT_CONFIG_ERROR
	if config["test_mode"]:
		print_errors(["тестовый репозиторий поддерживается с этапа 3"])
		return EXIT_CONFIG_ERROR
	try:
		print_direct(config)
	except RepoError as error:
		print_errors([str(error)])
		return EXIT_REPO_ERROR
	return EXIT_OK


if __name__ == "__main__":
	sys.exit(main())
