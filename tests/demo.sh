#!/bin/sh
# Демонстрация работы с тестовыми репозиториями
cd "$(dirname "$0")/.." || exit 1
for case in simple diamond complex cycle; do
	echo "=== $case.txt ==="
	./run.sh --test-mode --package A --repo "tests/repos/$case.txt"
done
echo "=== Пакета нет в репозитории ==="
./run.sh --test-mode --package Z --repo tests/repos/simple.txt
echo "=== Неверный формат файла ==="
./run.sh --test-mode --package A --repo tests/repos/bad.txt
echo "=== Пакет начинается не с корня: C ==="
./run.sh --test-mode --package C --repo tests/repos/complex.txt
echo "=== Порядок загрузки: complex.txt ==="
./run.sh --test-mode --package A --repo tests/repos/complex.txt --load-order
echo "=== Порядок загрузки: diamond.txt ==="
./run.sh --test-mode --package A --repo tests/repos/diamond.txt --load-order
echo "=== Порядок загрузки при циклах: cycle.txt ==="
./run.sh --test-mode --package A --repo tests/repos/cycle.txt --load-order
