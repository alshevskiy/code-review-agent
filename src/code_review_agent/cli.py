"""CLI точка входа для code-review-agent."""

from __future__ import annotations

import sys
from pathlib import Path

import typer
from rich.console import Console

from . import __version__
from .config import AppConfig, load_config
from .formatter import (
    print_check_result,
    print_error,
    print_file_list,
    print_info,
    print_review,
    print_success,
)
from .git_utils import (
    GitError,
    get_current_branch,
    get_diff,
    get_diff_files,
    get_diff_with_content,
    get_repo,
)
from .languages.detector import detect_language
from .reviewer import CodeReviewer, ReviewerError

app = typer.Typer(
    name="code-review-agent",
    help="AI-агент для ревью кода на основе LLM.",
    no_args_is_help=True,
)
console = Console()


@app.command()
def review(
    target: str = typer.Argument(
        help="Ветка или диапазон коммитов (например: feature/auth или main..feature/auth).",
    ),
    base_url: str | None = typer.Option(
        None,
        "--base-url",
        "-u",
        help="URL API провайдера LLM.",
    ),
    model: str | None = typer.Option(
        None,
        "--model",
        "-m",
        help="Название модели.",
    ),
    api_key: str | None = typer.Option(
        None,
        "--api-key",
        "-k",
        help="API ключ (или установите переменную окружения).",
    ),
    config_path: str | None = typer.Option(
        None,
        "--config",
        "-c",
        help="Путь к файлу конфигурации.",
    ),
    output: str | None = typer.Option(
        None,
        "--output",
        "-o",
        help="Путь для сохранения отчёта.",
    ),
    lang: str | None = typer.Option(
        None,
        "--lang",
        "-l",
        help="Язык программирования (авто-определение по умолчанию).",
    ),
    focus: str | None = typer.Option(
        None,
        "--focus",
        "-f",
        help="Фокус ревью: 'tests' или 'production'.",
    ),
    style: str | None = typer.Option(
        None,
        "--style",
        "-s",
        help="Путь к файлу стилевых требований.",
    ),
    all_files: bool = typer.Option(
        False,
        "--all",
        "-a",
        help="Ревьюить все файлы по отдельности.",
    ),
) -> None:
    """Провести ревью кода.

    Примеры:

      code-review-agent review feature/auth

      code-review-agent review main..feature/auth -o report.md

      code-review-agent review feature/auth --focus tests --lang java
    """
    # Загрузка конфигурации
    config = load_config(config_path)

    # Переопределение параметрами CLI
    if base_url:
        config.provider.base_url = base_url
    if model:
        config.provider.model = model
    if api_key:
        config.provider.api_key = api_key

    # Работа с git
    try:
        repo = get_repo()
    except GitError as e:
        print_error(str(e))
        raise typer.Exit(1)

    # Определение текущей ветки
    current = get_current_branch(repo)
    print_info(f"Текущая ветка: {current}")

    # Получение diff
    print_info(f"Получение diff для: {target}")
    try:
        diff = get_diff(repo, target)
    except GitError as e:
        print_error(str(e))
        raise typer.Exit(1)

    if not diff.strip():
        print_success("Нет изменений для ревью.")
        raise typer.Exit(0)

    # Список файлов
    files = get_diff_files(repo, target)
    print_file_list(files)

    # Определение языка
    if not lang and files:
        # Берём язык первого файла
        lang = detect_language(files[0])
        if lang:
            print_info(f"Определён язык: {lang}")

    # Загрузка стилевого гайда
    style_guide = None
    if style:
        style_path = Path(style)
        if style_path.exists():
            style_guide = style_path.read_text(encoding="utf-8")
            print_info(f"Загружен стиль: {style}")
    else:
        # Автопоиск .code-review-style.md в корне проекта
        auto_style = Path(".code-review-style.md")
        if auto_style.exists():
            style_guide = auto_style.read_text(encoding="utf-8")
            print_info(f"Найден стиль: {auto_style}")

    # Ревью
    reviewer = CodeReviewer(config)

    try:
        if all_files and len(files) > 1:
            # Ревью каждого файла отдельно
            file_diffs = get_diff_with_content(repo, target)
            review_text = reviewer.review_files(
                file_diffs,
                language=lang,
                focus=focus,
                style_guide=style_guide,
            )
        else:
            # Общий diff
            review_text = reviewer.review_code(
                diff=diff,
                language=lang,
                focus=focus,
                style_guide=style_guide,
            )
    except ReviewerError as e:
        print_error(str(e))
        raise typer.Exit(1)

    # Вывод результата
    print_review(review_text, output_file=output)


@app.command()
def check(
    config_path: str | None = typer.Option(
        None,
        "--config",
        "-c",
        help="Путь к файлу конфигурации.",
    ),
) -> None:
    """Проверить окружение и конфигурацию."""
    import subprocess

    from git import __version__ as git_version
    from openai import __version__ as openai_version

    config = load_config(config_path)

    checks = []

    # Python
    py_ver = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    checks.append({
        "name": "Python",
        "status": True,
        "detail": py_ver,
    })

    # Git
    try:
        result = subprocess.run(
            ["git", "--version"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        git_ver = result.stdout.strip().replace("git version ", "")
        checks.append({
            "name": "Git",
            "status": True,
            "detail": git_ver,
        })
    except Exception:
        checks.append({
            "name": "Git",
            "status": False,
            "detail": "Не найден",
        })

    # OpenAI клиент
    checks.append({
        "name": "OpenAI клиент",
        "status": True,
        "detail": openai_version,
    })

    # GitPython
    checks.append({
        "name": "GitPython",
        "status": True,
        "detail": git_version,
    })

    # Провайдер
    api_key = config.provider.resolved_api_key
    checks.append({
        "name": "Провайдер",
        "status": bool(api_key),
        "detail": config.provider.base_url,
    })

    # Модель
    checks.append({
        "name": "Модель",
        "status": True,
        "detail": config.provider.model,
    })

    print_check_result(checks)


@app.command()
def version() -> None:
    """Показать версию."""
    console.print(f"code-review-agent v{__version__}")


if __name__ == "__main__":
    app()
