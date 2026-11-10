@echo off
rem Запуск программы: run.bat --package ... --repo ... --version ...
rem Запуск тестов:    run.bat test
cd /d "%~dp0"
if "%1"=="test" (
	set PYTHONPATH=src
	python -m unittest discover -s tests -v
) else (
	python src\main.py %*
)
