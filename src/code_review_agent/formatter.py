"""Форматирование вывода ревью."""

from __future__ import annotations

from pathlib import Path

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table
from rich.text import Text


console = Console()


def print_review(review_text: str, output_file: str | None = None) -> None:
    """Выводит ревью в консоль и/или сохраняет в файл.

    Args:
        review_text: Текст ревью.
        output_file: Путь для сохранения (опционально).
    """
    # Сохранение в файл
    if output_file:
        Path(output_file).write_text(review_text, encoding="utf-8")
        console.print(f"\n[green]✓[/green] Ревью сохранено в {output_file}")

    # Вывод в консоль
    console.print()
    console.print(Panel(
        Markdown(review_text),
        title="[bold blue]Результат ревью[/bold blue]",
        border_style="blue",
        padding=(1, 2),
    ))


def print_error(message: str) -> None:
    """Выводит сообщение об ошибке."""
    console.print(f"\n[red]✗[/red] {message}")


def print_info(message: str) -> None:
    """Выводит информационное сообщение."""
    console.print(f"[dim]ℹ[/dim] {message}")


def print_success(message: str) -> None:
    """Выводит сообщение об успехе."""
    console.print(f"[green]✓[/green] {message}")


def print_check_result(checks: list[dict[str, str | bool]]) -> None:
    """Выводит результаты проверки окружения.

    Args:
        checks: Список проверок [{name, status, detail}].
    """
    table = Table(title="Проверка окружения", border_style="blue")
    table.add_column("Компонент", style="cyan")
    table.add_column("Статус")
    table.add_column("Детали", style="dim")

    for check in checks:
        status = check["status"]
        if status is True:
            status_text = Text("✓ OK", style="green")
        elif status is False:
            status_text = Text("✗ ОШИБКА", style="red")
        else:
            status_text = Text(str(status), style="yellow")

        table.add_row(
            check["name"],
            status_text,
            check.get("detail", ""),
        )

    console.print(table)


def print_file_list(files: list[str], title: str = "Изменённые файлы") -> None:
    """Выводит список файлов."""
    if not files:
        return

    table = Table(title=title, border_style="dim")
    table.add_column("Файл", style="cyan")

    for f in files:
        table.add_row(f)

    console.print(table)
