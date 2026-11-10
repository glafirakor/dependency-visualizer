"""Настройки приложения: разбор и проверка опций командной строки."""

import argparse
import os
import re

MAVEN_NAME_RE = re.compile(r"^[\w.\-]+:[\w.\-]+$")
TEST_NAME_RE = re.compile(r"^[A-Z]+$")
VERSION_RE = re.compile(r"^[\w.\-]+$")
URL_PREFIXES = ("http://", "https://")


class ConfigError(Exception):
	"""Ошибка в параметрах командной строки (содержит список сообщений)."""


def build_parser():
	"""Создать парсер опций командной строки."""
	parser = argparse.ArgumentParser(
		description="Визуализатор графа зависимостей пакетов Maven")
	parser.add_argument(
		"--package", default="",
		help="имя пакета: groupId:artifactId (в тестовом режиме A-Z)")
	parser.add_argument(
		"--repo", default="",
		help="URL репозитория или путь к файлу тестового репозитория")
	parser.add_argument(
		"--test-mode", action="store_true",
		help="режим работы с тестовым репозиторием")
	parser.add_argument(
		"--version", default="", help="версия пакета")
	parser.add_argument(
		"--ascii-tree", action="store_true",
		help="вывод зависимостей в формате ASCII-дерева")
	return parser


def check_package(name, test_mode):
	"""Проверить имя пакета; вернуть текст ошибки или None."""
	if not name:
		return "не задано имя пакета (--package)"
	if test_mode and not TEST_NAME_RE.match(name):
		return (
			"в тестовом режиме имя пакета состоит из больших "
			f"латинских букв: {name}")
	if not test_mode and not MAVEN_NAME_RE.match(name):
		return f"имя пакета должно иметь вид groupId:artifactId: {name}"
	return None


def check_repo(repo, test_mode):
	"""Проверить URL репозитория или путь к файлу; вернуть ошибку или None."""
	if not repo:
		return "не задан репозиторий (--repo)"
	if test_mode and not os.path.isfile(repo):
		return f"файл тестового репозитория не найден: {repo}"
	if not test_mode and not repo.startswith(URL_PREFIXES):
		return f"URL должен начинаться с http:// или https://: {repo}"
	return None


def check_version(version, test_mode):
	"""Проверить версию пакета; вернуть текст ошибки или None."""
	if not version:
		if test_mode:
			return None
		return "не задана версия пакета (--version)"
	if not VERSION_RE.match(version):
		return f"недопустимая версия пакета: {version}"
	return None


def load_config(argv=None):
	"""Разобрать и проверить опции; вернуть словарь настроек."""
	args = build_parser().parse_args(argv)
	config = {
		"package": args.package,
		"repo": args.repo,
		"test_mode": args.test_mode,
		"version": args.version,
		"ascii_tree": args.ascii_tree,
	}
	checks = (
		check_package(args.package, args.test_mode),
		check_repo(args.repo, args.test_mode),
		check_version(args.version, args.test_mode),
	)
	errors = [message for message in checks if message]
	if errors:
		raise ConfigError(errors)
	return config
