"""Получение прямых зависимостей пакета Maven из POM-файлов репозитория.

Используются только стандартные модули Python: urllib для загрузки
POM-файла и xml.etree для его разбора.
"""

import re
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET

PROPERTY_RE = re.compile(r"\$\{([^}]+)\}")
TIMEOUT_SECONDS = 15
MAX_PARENT_DEPTH = 10
MAX_RESOLVE_STEPS = 10
DEFAULT_SCOPE = "compile"
TRANSITIVE_SCOPES = ("compile", "runtime")
UNKNOWN_VERSION = "?"

POM_CACHE = {}


class RepoError(Exception):
	"""Ошибка получения или разбора данных из репозитория."""


def pom_url(repo, group, artifact, version):
	"""Вернуть URL POM-файла пакета в репозитории Maven."""
	path = group.replace(".", "/")
	base = repo.rstrip("/")
	return f"{base}/{path}/{artifact}/{version}/{artifact}-{version}.pom"


def fetch_text(url):
	"""Скачать POM-файл по URL (с кешем); вернуть текст."""
	if url in POM_CACHE:
		return POM_CACHE[url]
	try:
		with urllib.request.urlopen(url, timeout=TIMEOUT_SECONDS) as answer:
			text = answer.read().decode("utf-8")
	except urllib.error.HTTPError as error:
		raise RepoError(
			f"пакет не найден в репозитории ({error.code}): {url}"
		) from error
	except (urllib.error.URLError, OSError) as error:
		raise RepoError(
			f"не удалось подключиться к репозиторию: {error}") from error
	POM_CACHE[url] = text
	return text


def parse_pom(text):
	"""Разобрать текст POM-файла в XML-дерево без пространств имён."""
	try:
		root = ET.fromstring(text)
	except ET.ParseError as error:
		raise RepoError(f"неверный формат POM-файла: {error}") from error
	for element in root.iter():
		element.tag = element.tag.split("}")[-1]
	return root


def child_text(element, path):
	"""Вернуть текст дочернего элемента по пути или пустую строку."""
	node = element.find(path)
	if node is None or node.text is None:
		return ""
	return node.text.strip()


def resolve(value, props):
	"""Подставить в строку значения свойств вида ${имя}."""
	for _ in range(MAX_RESOLVE_STEPS):
		new_value = PROPERTY_RE.sub(
			lambda match: props.get(match.group(1), match.group(0)), value)
		if new_value == value:
			break
		value = new_value
	return value


def read_properties(root):
	"""Собрать свойства POM: блок properties и версию/группу проекта."""
	props = {}
	block = root.find("properties")
	if block is not None:
		for prop in block:
			props[prop.tag] = (prop.text or "").strip()
	version = child_text(root, "version") or child_text(root, "parent/version")
	group = child_text(root, "groupId") or child_text(root, "parent/groupId")
	props["project.version"] = version
	props["version"] = version
	props["project.groupId"] = group
	props["project.parent.version"] = child_text(root, "parent/version")
	return props


def read_managed(root, props):
	"""Собрать версии из dependencyManagement: имя пакета -> версия."""
	managed = {}
	path = "dependencyManagement/dependencies/dependency"
	for dep in root.findall(path):
		name = resolve_name(dep, props)
		managed[name] = resolve(child_text(dep, "version"), props)
	return managed


def resolve_name(dep, props):
	"""Вернуть имя зависимости в виде groupId:artifactId."""
	group = resolve(child_text(dep, "groupId"), props)
	artifact = resolve(child_text(dep, "artifactId"), props)
	return f"{group}:{artifact}"


def load_parent(repo, root, model, depth):
	"""Добавить в модель свойства и версии из родительского POM."""
	parent = root.find("parent")
	if parent is None or depth >= MAX_PARENT_DEPTH:
		return
	coords = (
		child_text(parent, "groupId"),
		child_text(parent, "artifactId"),
		child_text(parent, "version"),
	)
	try:
		parent_model = load_model(repo, coords, depth + 1)
	except RepoError:
		return
	model["props"].update(parent_model["props"])
	model["managed"].update(parent_model["managed"])


def load_model(repo, coords, depth=0):
	"""Загрузить POM пакета с учётом родительских POM."""
	root = parse_pom(fetch_text(pom_url(repo, *coords)))
	model = {"root": root, "props": {}, "managed": {}}
	load_parent(repo, root, model, depth)
	model["props"].update(read_properties(root))
	model["managed"].update(read_managed(root, model["props"]))
	return model


def read_dependency(dep, model):
	"""Прочитать одну зависимость: имя, версию, scope и optional."""
	props = model["props"]
	name = resolve_name(dep, props)
	version = resolve(child_text(dep, "version"), props)
	if not version:
		version = model["managed"].get(name, "")
	if not version or "${" in version:
		version = UNKNOWN_VERSION
	return {
		"name": name,
		"version": version,
		"scope": child_text(dep, "scope") or DEFAULT_SCOPE,
		"optional": child_text(dep, "optional") == "true",
	}


def direct_dependencies(repo, package, version):
	"""Вернуть список прямых зависимостей пакета заданной версии."""
	group, artifact = package.split(":")
	model = load_model(repo, (group, artifact, version))
	return [
		read_dependency(dep, model)
		for dep in model["root"].findall("dependencies/dependency")
	]


def is_transitive(dep):
	"""Проверить, передаётся ли зависимость дальше по цепочке."""
	return dep["scope"] in TRANSITIVE_SCOPES and not dep["optional"]
