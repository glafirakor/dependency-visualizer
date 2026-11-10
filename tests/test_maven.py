"""Тесты получения прямых зависимостей Maven (этап 2) без сети."""

import unittest

import maven

REPO = "https://repo.example/maven2"

PARENT_POM = """<project xmlns="http://maven.apache.org/POM/4.0.0">
	<groupId>org.demo</groupId>
	<artifactId>parent</artifactId>
	<version>1</version>
	<properties><lib.version>2.5</lib.version></properties>
	<dependencyManagement><dependencies>
		<dependency>
			<groupId>org.demo</groupId>
			<artifactId>managed</artifactId>
			<version>3.0</version>
		</dependency>
	</dependencies></dependencyManagement>
</project>"""

APP_POM = """<project xmlns="http://maven.apache.org/POM/4.0.0">
	<parent>
		<groupId>org.demo</groupId>
		<artifactId>parent</artifactId>
		<version>1</version>
	</parent>
	<artifactId>app</artifactId>
	<version>1.0</version>
	<dependencies>
		<dependency>
			<groupId>org.demo</groupId>
			<artifactId>lib</artifactId>
			<version>${lib.version}</version>
		</dependency>
		<dependency>
			<groupId>org.demo</groupId>
			<artifactId>managed</artifactId>
		</dependency>
		<dependency>
			<groupId>junit</groupId>
			<artifactId>junit</artifactId>
			<version>4.13</version>
			<scope>test</scope>
		</dependency>
		<dependency>
			<groupId>org.demo</groupId>
			<artifactId>extra</artifactId>
			<version>1.1</version>
			<optional>true</optional>
		</dependency>
	</dependencies>
</project>"""


def seed(group, artifact, version, text):
	"""Положить POM-файл в кеш, чтобы тест не ходил в сеть."""
	maven.POM_CACHE[maven.pom_url(REPO, group, artifact, version)] = text


class MavenTest(unittest.TestCase):
	"""Проверки чтения POM-файлов."""

	def setUp(self):
		"""Заполнить кеш тестовыми POM-файлами."""
		maven.POM_CACHE.clear()
		seed("org.demo", "parent", "1", PARENT_POM)
		seed("org.demo", "app", "1.0", APP_POM)

	def test_pom_url(self):
		"""URL POM-файла строится по правилам репозитория Maven."""
		url = maven.pom_url(REPO + "/", "org.demo", "app", "1.0")
		self.assertEqual(url, REPO + "/org/demo/app/1.0/app-1.0.pom")

	def test_direct_dependencies(self):
		"""Находятся все прямые зависимости с версиями и scope."""
		deps = maven.direct_dependencies(REPO, "org.demo:app", "1.0")
		names = [f"{dep['name']}:{dep['version']}" for dep in deps]
		self.assertEqual(names, [
			"org.demo:lib:2.5", "org.demo:managed:3.0",
			"junit:junit:4.13", "org.demo:extra:1.1"])

	def test_scope_and_optional(self):
		"""Тестовые и необязательные зависимости не транзитивны."""
		deps = maven.direct_dependencies(REPO, "org.demo:app", "1.0")
		flags = [maven.is_transitive(dep) for dep in deps]
		self.assertEqual(flags, [True, True, False, False])

	def test_bad_xml(self):
		"""Повреждённый POM-файл вызывает ошибку репозитория."""
		with self.assertRaises(maven.RepoError):
			maven.parse_pom("<project>")

	def test_resolve(self):
		"""Свойства ${...} подставляются, неизвестные остаются."""
		props = {"a": "1", "b": "${a}.2"}
		self.assertEqual(maven.resolve("${b}-${x}", props), "1.2-${x}")


if __name__ == "__main__":
	unittest.main()
