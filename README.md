# Визуализатор графа зависимостей Maven (вариант 9)

## Описание

Консольная программа на Python для анализа зависимостей пакетов Maven.
Сделаны этапы 1-2: программа принимает параметры из командной строки, проверяет их, скачивает POM-файл пакета из репозитория Maven и выводит его прямые зависимости. Менеджеры пакетов и сторонние библиотеки не используются: только стандартные модули Python (urllib, xml.etree).

Структура:

- src/main.py - точка входа
- src/config.py - разбор и проверка параметров
- src/maven.py - загрузка и разбор POM-файлов Maven
- tests/test_config.py, tests/test_maven.py - тесты
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
- print_direct() - выводит прямые зависимости
- main() - запуск программы

Как ищется версия зависимости: сначала берется из тега version (с подстановкой свойств, например ${lib.version}), если версии нет - из dependencyManagement этого или родительского POM. Если версию определить не удалось, выводится "?".

## Настройки

- --package ИМЯ - имя пакета в виде groupId:artifactId (в тестовом режиме большие латинские буквы, например A)
- --repo URL_ИЛИ_ПУТЬ - URL репозитория (http/https) или путь к файлу тестового репозитория
- --test-mode - режим работы с тестовым репозиторием
- --version ВЕРСИЯ - версия пакета (в тестовом режиме не обязательна)
- --ascii-tree - вывод зависимостей в виде ASCII-дерева

Ошибки: не задано имя пакета, неверный формат имени, не задан репозиторий, URL не http/https, файл тестового репозитория не найден, не задана или неверная версия. Выводятся все найденные ошибки сразу.

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

Прямые зависимости пакета (формат: groupId:artifactId:версия [scope]):

```
$ ./run.sh --package org.demo:app --repo http://localhost:8765/maven2 --version 1.0
Прямые зависимости org.demo:app:1.0:
  org.demo:lib:2.5 [compile]
  org.demo:managed:3.0 [compile]
  junit:junit:4.13 [test]
  org.demo:extra:1.1 [compile] (optional)
```

Реальный пакет из Maven Central:

```
./run.sh --package com.google.guava:guava --repo https://repo1.maven.org/maven2 --version 33.0.0-jre
```

Пакета нет в репозитории:

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
