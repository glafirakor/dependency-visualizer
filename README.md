# Визуализатор графа зависимостей Maven (вариант 9)

## Описание

Консольная программа на Python для анализа зависимостей пакетов Maven.
Сделаны этапы 1-3: программа принимает параметры из командной строки, проверяет их, скачивает POM-файлы пакетов из репозитория Maven и строит полный граф зависимостей (с учетом транзитивности) обходом в глубину. Циклические зависимости находятся и выводятся. Есть режим тестового репозитория: граф описывается в текстовом файле, пакеты называются большими латинскими буквами. Менеджеры пакетов и сторонние библиотеки не используются: только стандартные модули Python (urllib, xml.etree).

Структура:

- src/main.py - точка входа
- src/config.py - разбор и проверка параметров
- src/maven.py - загрузка и разбор POM-файлов Maven
- src/graph.py - построение графа обходом в глубину
- src/repo_file.py - чтение файла тестового репозитория
- tests/test_config.py, tests/test_maven.py, tests/test_graph.py - тесты
- tests/repos/ - тестовые репозитории (simple, diamond, complex, cycle, bad)
- tests/demo.sh - демонстрация работы на тестовых репозиториях
- run.sh, run.bat - скрипты запуска (macOS/Linux и Windows)

## Функции

- build_parser() - описывает опции командной строки (argparse)
- check_package() - проверяет имя пакета
- check_repo() - проверяет URL репозитория или путь к файлу
- check_version() - проверяет версию пакета
- load_config() - разбирает опции, проверяет их и возвращает словарь настроек
- pom_url() - строит адрес POM-файла: репозиторий/groupId/artifactId/версия/artifactId-версия.pom
- fetch_text() - скачивает POM-файл (с кешем)
- parse_pom() - разбирает XML POM-файла
- resolve() - подставляет свойства вида ${имя}
- load_model() - загружает POM вместе с родительскими POM (свойства и dependencyManagement)
- read_dependency() - читает одну зависимость: имя, версия, scope, optional
- direct_dependencies() - возвращает прямые зависимости пакета заданной версии
- is_transitive() - проверяет, передается ли зависимость дальше (scope compile или runtime и не optional)
- build_graph() - строит граф рекурсивным обходом в глубину (DFS), находит циклы
- load_repo_file() - читает граф тестового репозитория из файла
- maven_provider() - функция получения транзитивных зависимостей из Maven
- make_graph() - строит граф для тестового или Maven-репозитория
- print_graph() - выводит граф и циклы
- main() - запуск программы

Как работает обход: для пакета берутся его прямые зависимости, и для каждой рекурсивно повторяется то же самое. Уже обработанный пакет второй раз не обходится. Пакеты на текущем пути рекурсии хранятся в списке path: если зависимость уже есть в path, значит найден цикл, он запоминается, а обход по нему дальше не идет.

В граф Maven попадают только зависимости, которые Maven передает транзитивно: scope compile и runtime, без optional. Зависимости test, provided и optional показываются только у самого пакета.

Как ищется версия зависимости: сначала берется из тега version (с подстановкой свойств, например ${lib.version}), если версии нет - из dependencyManagement этого или родительского POM. Если версию определить не удалось, выводится "?".

## Настройки

- --package ИМЯ - имя пакета в виде groupId:artifactId (в тестовом режиме большие латинские буквы, например A)
- --repo URL_ИЛИ_ПУТЬ - URL репозитория (http/https) или путь к файлу тестового репозитория
- --test-mode - режим работы с тестовым репозиторием
- --version ВЕРСИЯ - версия пакета (в тестовом режиме не обязательна)
- --ascii-tree - вывод зависимостей в виде ASCII-дерева

Ошибки: не задано имя пакета, неверный формат имени, не задан репозиторий, URL не http/https, файл тестового репозитория не найден, не задана или неверная версия. Выводятся все найденные ошибки сразу.

Формат файла тестового репозитория:

```
# комментарий
A: B C
B: D
C: D
D:
```

## Запуск

Нужен Python 3. Собирать ничего не надо.

macOS/Linux:

```
./run.sh --package com.google.guava:guava --repo https://repo1.maven.org/maven2 --version 33.0.0-jre
./run.sh test
```

Windows:

```
run.bat --package com.google.guava:guava --repo https://repo1.maven.org/maven2 --version 33.0.0-jre
run.bat test
```

## Примеры

Тестовый репозиторий с циклами (tests/repos/cycle.txt):

```
$ ./run.sh --test-mode --package A --repo tests/repos/cycle.txt
Граф зависимостей (с учётом транзитивности):
  A -> B, D
  B -> C
  C -> A
  D -> D
Найдены циклические зависимости:
  A -> B -> C -> A
  D -> D
```

Ромб (tests/repos/diamond.txt), общая зависимость D обходится один раз:

```
$ ./run.sh --test-mode --package A --repo tests/repos/diamond.txt
Граф зависимостей (с учётом транзитивности):
  A -> B, C
  B -> D
  D -> (нет зависимостей)
  C -> D
Циклических зависимостей нет
```

Все случаи тестового репозитория: `sh tests/demo.sh`

Реальный пакет из Maven Central:

```
./run.sh --package com.google.guava:guava --repo https://repo1.maven.org/maven2 --version 33.0.0-jre
```

Ошибки:

```
$ ./run.sh --test-mode --package Z --repo tests/repos/simple.txt
ошибка: пакет Z не найден в тестовом репозитории
$ ./run.sh --test-mode --package A --repo tests/repos/bad.txt
ошибка: строка 2: неверный формат: A: b c
```

```
$ ./run.sh --package org.demo:nope --repo http://localhost:8765/maven2 --version 1.0
ошибка: пакет не найден в репозитории (404): http://localhost:8765/maven2/org/demo/nope/1.0/nope-1.0.pom
```

```
$ ./run.sh --package guava --repo ftp://repo
ошибка: имя пакета должно иметь вид groupId:artifactId: guava
ошибка: URL должен начинаться с http:// или https://: ftp://repo
ошибка: не задана версия пакета (--version)
```
