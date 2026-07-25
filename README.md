# Code Review Agent

AI-агент для ревью кода на основе LLM. Поддерживает кастомные URL провайдеров (корпоративные модели).

## Возможности

- Ревью веток и диапазонов коммитов
- Поиск багов, улучшений, проблем стиля и безопасности
- Поддержка 8+ языков программирования с авто-определением
- Файлы стилевых требований (`.code-review-style.md`)
- Экспорт отчётов в файл
- Кастомные URL провайдеров (корпоративные LLM)

## Требования

- Python 3.11+
- Git
- Доступ к LLM API (OpenAI-совместимый)

## Установка

### Шаг 1: Клонирование

```bash
git clone <url-repo>
cd code-review-agent
```

### Шаг 2: Установка

**Linux / macOS:**

```bash
chmod +x setup.sh
./setup.sh
source .venv/bin/activate
```

**Windows:**

```cmd
setup.bat
.venv\Scripts\activate
```

### Шаг 3: Проверка установки

```bash
code-review-agent check
```

Вывод:

```
┌──────────────────┬────────┬────────────────────────────┐
│ Компонент        │ Статус │ Детали                     │
├──────────────────┼────────┼────────────────────────────┤
│ Python           │ ✓ OK   │ 3.11.4                     │
│ Git              │ ✓ OK   │ 2.42.0                     │
│ OpenAI клиент    │ ✓ OK   │ 1.35.0                     │
│ GitPython        │ ✓ OK   │ 3.1.43                     │
│ Провайдер        │ ✓ OK   │ https://corp-llm.internal  │
│ Модель           │ ✓ OK   │ gpt-4o                     │
└──────────────────┴────────┴────────────────────────────┘
```

## Конфигурация

### Вариант 1: Файл конфигурации

Создайте файл `.code-review-agent.yaml` в корне вашего проекта:

```yaml
provider:
  base_url: "https://your-corporate-llm.com/v1"
  api_key_env: "CORP_API_KEY"    # имя переменной окружения с ключом
  model: "gpt-4o"
  temperature: 0.1

review:
  exclude_patterns:
    - "vendor/**"
    - "*.lock"
    - "node_modules/**"
  max_diff_tokens: 30000
```

### Вариант 2: Переменные окружения

```bash
export CORP_API_KEY="ваш-ключ"
```

### Вариант 3: Параметры CLI

Все параметры можно передать при запуске (см. ниже).

## Использование

### Ревью ветки (сравнение с main)

```bash
code-review-agent review feature/auth
```

### Ревью диапазона коммитов

```bash
code-review-agent review main..feature/auth
```

### С кастомным URL провайдера

```bash
code-review-agent review feature/auth \
  --base-url "https://corp-llm.internal/v1" \
  --model "claude-3-5-sonnet"
```

### Сохранение отчёта в файл

```bash
code-review-agent review feature/auth --output report.md
```

### Указание языка явно

```bash
code-review-agent review feature/auth --lang java
```

### Фокус на тестах

```bash
code-review-agent review feature/auth --focus tests
```

### Ревью каждого файла отдельно

```bash
code-review-agent review feature/auth --all
```

### Использование файла стилей

Агент автоматически ищет `.code-review-style.md` в корне проекта:

```bash
code-review-agent review feature/auth
```

Или укажите явно:

```bash
code-review-agent review feature/auth --style ./my-styles/conventions.md
```

### Полный пример

```bash
code-review-agent review main..feature/new-api \
  --base-url "https://corp-llm.internal/v1" \
  --model "gpt-4o" \
  --lang java \
  --focus tests \
  --output report.md
```

## Файл стилевых требований

Создайте `.code-review-style.md` в корне проекта:

```markdown
# Требования к стилю кода

## Именование
- snake_case для переменных и функций
- PascalCase для классов
- UPPER_SNAKE_CASE для констант

## Примеры кода

### Правильно

```python
def get_user_by_id(user_id: int) -> User:
    return db.query(User).filter(User.id == user_id).first()
```

### Неправильно

```python
def GetUser(userId):
    return db.query(User).filter(User.id == userId).first()
```

## Требования
- Все функции должны иметь type hints
- Обязательная обработка ошибок
- Никаких магических чисел
```

## Поддерживаемые языки

| Язык       | Расширения       | Особенности                            |
|------------|------------------|----------------------------------------|
| Python     | `.py`            | Type hints, async/await, PEP 8         |
| JavaScript | `.js`, `.jsx`    | const/let, async/await, ES modules     |
| TypeScript | `.ts`, `.tsx`    | Строгая типизация, generics            |
| Go         | `.go`            | Error handling, goroutines             |
| Java       | `.java`          | Optional, Stream API, @DisplayName     |
| Kotlin     | `.kt`            | Coroutines, null-safety                |
| Rust       | `.rs`            | Ownership, Result/Option               |
| C#         | `.cs`            | Nullable, async/await, LINQ            |
| PHP        | `.php`           | Type declarations, PSR-12              |

## Структура проекта

```text
code-review-agent/
├── setup.sh                          # скрипт установки (Linux/macOS)
├── setup.bat                         # скрипт установки (Windows)
├── pyproject.toml                    # зависимости и сборка
├── README.md
├── src/
│   └── code_review_agent/
│       ├── __init__.py
│       ├── cli.py                    # CLI точка входа
│       ├── config.py                 # конфигурация провайдера
│       ├── git_utils.py              # получение diff из git
│       ├── reviewer.py               # логика LLM-ревью
│       ├── formatter.py              # форматирование вывода
│       └── languages/
│           ├── __init__.py
│           ├── prompts.py            # промпты для каждого языка
│           └── detector.py           # авто-определение языка
└── tests/
```

## Лицензия

MIT
