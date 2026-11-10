"""Построение графа зависимостей обходом в глубину (DFS) с рекурсией."""


def build_graph(root, get_deps):
	"""Построить граф с учётом транзитивности.

	get_deps(пакет) возвращает список прямых зависимостей пакета.
	Результат: словарь пакет -> прямые зависимости (в порядке обхода)
	и список найденных циклов (каждый цикл - список пакетов).
	"""
	graph = {}
	cycles = []
	path = []

	def visit(node):
		"""Рекурсивно обойти пакет и все его зависимости."""
		if node in path:
			cycles.append(path[path.index(node):] + [node])
			return
		if node in graph:
			return
		path.append(node)
		graph[node] = get_deps(node)
		for dep in graph[node]:
			visit(dep)
		path.pop()

	visit(root)
	return graph, cycles


def format_graph(graph):
	"""Вернуть строки вида 'пакет -> зависимость1, зависимость2'."""
	lines = []
	for node, deps in graph.items():
		targets = ", ".join(deps) if deps else "(нет зависимостей)"
		lines.append(f"{node} -> {targets}")
	return lines


def format_cycle(cycle):
	"""Вернуть цикл в виде строки 'A -> B -> A'."""
	return " -> ".join(cycle)
