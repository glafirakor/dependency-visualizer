#!/bin/sh
# Запуск программы: ./run.sh --package ... --repo ... --version ...
# Запуск тестов:    ./run.sh test
cd "$(dirname "$0")" || exit 1
if [ "$1" = "test" ]; then
	PYTHONPATH=src python3 -m unittest discover -s tests -v
else
	python3 src/main.py "$@"
fi
