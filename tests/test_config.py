"""Тесты разбора и проверки параметров (этап 1)."""

import os
import tempfile
import unittest

from config import ConfigError, load_config

REPO_URL = "https://repo1.maven.org/maven2"


def errors_of(argv):
	"""Вернуть список ошибок, которые вызывают параметры argv."""
	try:
		load_config(argv)
	except ConfigError as error:
		return error.args[0]
	return []


class ConfigTest(unittest.TestCase):
	"""Проверки параметров командной строки."""

	def test_valid_maven(self):
		"""Корректные параметры Maven разбираются в словарь."""
		config = load_config([
			"--package", "com.google.guava:guava", "--repo", REPO_URL,
			"--version", "33.0.0-jre", "--ascii-tree"])
		self.assertEqual(config["package"], "com.google.guava:guava")
		self.assertEqual(config["version"], "33.0.0-jre")
		self.assertTrue(config["ascii_tree"])
		self.assertFalse(config["test_mode"])

	def test_missing_all(self):
		"""Без параметров сообщается об имени, репозитории и версии."""
		self.assertEqual(len(errors_of([])), 3)

	def test_bad_package(self):
		"""Имя без двоеточия не подходит для Maven."""
		errors = errors_of([
			"--package", "guava", "--repo", REPO_URL, "--version", "1.0"])
		self.assertIn("groupId:artifactId", errors[0])

	def test_bad_url(self):
		"""URL без http/https считается ошибкой."""
		errors = errors_of([
			"--package", "a:b", "--repo", "ftp://x", "--version", "1.0"])
		self.assertIn("http://", errors[0])

	def test_bad_version(self):
		"""Версия с недопустимыми символами считается ошибкой."""
		errors = errors_of([
			"--package", "a:b", "--repo", REPO_URL, "--version", "1 0"])
		self.assertIn("версия", errors[0])

	def test_test_mode(self):
		"""В тестовом режиме нужен существующий файл и имя из A-Z."""
		with tempfile.NamedTemporaryFile("w", delete=False) as file:
			path = file.name
		config = load_config(
			["--package", "A", "--repo", path, "--test-mode"])
		os.remove(path)
		self.assertTrue(config["test_mode"])

	def test_test_mode_errors(self):
		"""В тестовом режиме проверяются имя пакета и наличие файла."""
		errors = errors_of(
			["--package", "a", "--repo", "no_file.txt", "--test-mode"])
		self.assertEqual(len(errors), 2)


if __name__ == "__main__":
	unittest.main()
