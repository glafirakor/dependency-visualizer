"""Тесты графа, тестового репозитория и порядка загрузки (этапы 3-4)."""

import os
import unittest

from graph import build_graph, load_order
from repo_file import RepoFileError, load_repo_file

REPOS = os.path.join(os.path.dirname(__file__), "repos")


def load(name):
	"""Загрузить тестовый репозиторий из папки tests/repos."""
	return load_repo_file(os.path.join(REPOS, name))


def graph_of(name, root="A"):
	"""Построить граф пакета root по тестовому репозиторию name."""
	repo = load(name)
	return build_graph(root, lambda node: repo.get(node, []))


class RepoFileTest(unittest.TestCase):
	"""Проверки чтения файла тестового репозитория."""

	def test_load(self):
		"""Комментарии пропускаются, пакеты читаются со списками."""
		self.assertEqual(load("simple.txt"), {"A": ["B"], "B": ["C"], "C": []})

	def test_bad_format(self):
		"""Маленькие буквы в именах вызывают ошибку формата."""
		with self.assertRaises(RepoFileError):
			load("bad.txt")

	def test_missing_file(self):
		"""Отсутствующий файл вызывает ошибку чтения."""
		with self.assertRaises(RepoFileError):
			load("no_such_file.txt")


class GraphTest(unittest.TestCase):
	"""Проверки обхода графа в глубину."""

	def test_transitive(self):
		"""В граф попадают и транзитивные зависимости."""
		graph, cycles = graph_of("simple.txt")
		self.assertEqual(list(graph), ["A", "B", "C"])
		self.assertEqual(cycles, [])

	def test_diamond(self):
		"""Общая зависимость обходится только один раз."""
		graph, _ = graph_of("diamond.txt")
		self.assertEqual(list(graph), ["A", "B", "D", "C"])

	def test_cycles(self):
		"""Циклы находятся, а обход не зацикливается."""
		graph, cycles = graph_of("cycle.txt")
		self.assertEqual(sorted(graph), ["A", "B", "C", "D"])
		self.assertIn(["A", "B", "C", "A"], cycles)
		self.assertIn(["D", "D"], cycles)

	def test_subgraph(self):
		"""Для пакета из середины строится только его часть графа."""
		graph, _ = graph_of("complex.txt", "C")
		self.assertEqual(sorted(graph), ["C", "E", "F", "G", "H"])


class LoadOrderTest(unittest.TestCase):
	"""Проверки порядка загрузки зависимостей (этап 4)."""

	def order_of(self, name, root="A"):
		"""Вернуть порядок загрузки для тестового репозитория."""
		graph, _ = graph_of(name, root)
		return load_order(graph, root)

	def test_chain(self):
		"""В цепочке сначала загружается самый нижний пакет."""
		self.assertEqual(self.order_of("simple.txt"), ["C", "B", "A"])

	def test_diamond(self):
		"""Общая зависимость загружается один раз и раньше всех."""
		self.assertEqual(self.order_of("diamond.txt"), ["D", "B", "C", "A"])

	def test_dependencies_first(self):
		"""Каждый пакет идет после всех своих зависимостей."""
		graph, _ = graph_of("complex.txt")
		order = load_order(graph, "A")
		for node, deps in graph.items():
			for dep in deps:
				self.assertLess(order.index(dep), order.index(node))

	def test_cycle(self):
		"""При циклах каждый пакет все равно входит один раз."""
		self.assertEqual(self.order_of("cycle.txt"), ["C", "B", "D", "A"])


if __name__ == "__main__":
	unittest.main()
