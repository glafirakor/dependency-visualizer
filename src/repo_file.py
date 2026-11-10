"""Тестовый репозиторий: граф пакетов с именами из больших латинских букв.

Формат файла: одна строка на пакет, 'ПАКЕТ: ЗАВИСИМОСТЬ1 ЗАВИСИМОСТЬ2'.
Пустые строки и текст после # пропускаются.
"""

import re

NAME_RE = re.compile(r"^[A-Z]+$")
COMMENT_CHAR = "#"


class RepoFileError(Exception):
	"""Ошибка чтения файла тестового репозитория."""


def parse_line(line, number):
	"""Разобрать строку файла; вернуть (пакет, зависимости) или None."""
	text = line.split(COMMENT_CHAR)[0].strip()
	if not text:
		return None
	name, separator, rest = text.partition(":")
	name = name.strip()
	deps = rest.split()
	names_ok = all(NAME_RE.match(item) for item in [name] + deps)
	if not separator or not names_ok:
		raise RepoFileError(f"строка {number}: неверный формат: {text}")
	return name, deps


def load_repo_file(path):
	"""Загрузить граф тестового репозитория: пакет -> зависимости."""
	repo = {}
	try:
		with open(path, encoding="utf-8") as file:
			lines = file.read().splitlines()
	except OSError as error:
		raise RepoFileError(f"не удалось прочитать файл: {error}") from error
	for number, line in enumerate(lines, start=1):
		parsed = parse_line(line, number)
		if parsed:
			repo[parsed[0]] = parsed[1]
	return repo
