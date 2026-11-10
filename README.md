# Визуализатор графа зависимостей Maven (вариант 9)

## Описание

Консольная программа на Python для анализа зависимостей пакетов Maven.
Сделан этап 1: программа принимает параметры из командной строки, проверяет их и выводит в формате ключ=значение.

Структура:

- src/main.py - точка входа
- src/config.py - разбор и проверка параметров
- tests/test_config.py - тесты
- run.sh, run.bat - скрипты запуска (macOS/Linux и Windows)

## Функции

- build_parser() - описывает опции командной строки (argparse)
- check_package() - проверяет имя пакета
- check_repo() - проверяет URL репозитория или путь к файлу
- check_version() - проверяет версию пакета
- load_config() - разбирает опции, проверяет их и возвращает словарь настроек
- print_config() - выводит параметры в формате ключ=значение
- main() - запуск программы

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

```
$ ./run.sh --package com.google.guava:guava --repo https://repo1.maven.org/maven2 --version 33.0.0-jre --ascii-tree
package=com.google.guava:guava
repo=https://repo1.maven.org/maven2
test_mode=False
version=33.0.0-jre
ascii_tree=True
```

```
$ ./run.sh --package guava --repo ftp://repo
ошибка: имя пакета должно иметь вид groupId:artifactId: guava
ошибка: URL должен начинаться с http:// или https://: ftp://repo
ошибка: не задана версия пакета (--version)
```
