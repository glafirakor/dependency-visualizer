"""Точка входа: визуализатор графа зависимостей пакетов Maven."""

import sys

from config import ConfigError, load_config

EXIT_OK = 0
EXIT_CONFIG_ERROR = 2


def print_errors(messages):
	"""Вывести сообщения об ошибках в поток ошибок."""
	for message in messages:
		print(f"ошибка: {message}", file=sys.stderr)


def print_config(config):
	"""Вывести параметры в формате ключ=значение."""
	for key, value in config.items():
		print(f"{key}={value}")


def main(argv=None):
	"""Запустить приложение и вернуть код завершения."""
	try:
		config = load_config(argv)
	except ConfigError as error:
		print_errors(error.args[0])
		return EXIT_CONFIG_ERROR
	print_config(config)
	return EXIT_OK


if __name__ == "__main__":
	sys.exit(main())
