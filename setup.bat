@echo off
echo === Установка code-review-agent ===

python --version >nul 2>&1
if errorlevel 1 (
    echo Ошибка: Python не найден. Установите Python 3.11+
    exit /b 1
)

echo Создание виртуального окружения...
python -m venv .venv

echo Активация окружения...
call .venv\Scripts\activate

echo Обновление pip...
pip install --upgrade pip

echo Установка зависимостей...
pip install -e .

echo.
echo === Установка завершена ===
echo.
echo Для использования:
echo   .venv\Scripts\activate
echo   code-review-agent --help
