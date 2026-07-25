#!/bin/bash
set -e

cd "$(dirname "$0")"

echo "=== Установка code-review-agent ==="

if ! command -v python3 &> /dev/null; then
    echo "Ошибка: Python 3 не найден. Установите Python 3.11+"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "Python: $PYTHON_VERSION"

echo "Создание виртуального окружения..."
python3 -m venv .venv

echo "Активация окружения..."
source .venv/bin/activate

echo "Обновление pip..."
pip install --upgrade pip

echo "Установка зависимостей..."
pip install -e .

echo ""
echo "=== Установка завершена ==="
echo ""
echo "Для использования:"
echo "  source .venv/bin/activate"
echo "  code-review-agent --help"
