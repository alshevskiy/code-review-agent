"""Авто-определение языка программирования по расширению файла."""

from __future__ import annotations

EXTENSION_TO_LANGUAGE: dict[str, str] = {
    ".py": "python",
    ".pyw": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".mjs": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".go": "go",
    ".java": "java",
    ".kt": "kotlin",
    ".kts": "kotlin",
    ".rs": "rust",
    ".cs": "csharp",
    ".php": "php",
    ".rb": "ruby",
    ".swift": "swift",
    ".scala": "scala",
    ".clj": "clojure",
    ".ex": "elixir",
    ".exs": "elixir",
    ".hs": "haskell",
    ".lua": "lua",
    ".r": "r",
    ".R": "r",
    ".sql": "sql",
    ".sh": "bash",
    ".bash": "bash",
    ".zsh": "bash",
    ".ps1": "powershell",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".json": "json",
    ".xml": "xml",
    ".html": "html",
    ".css": "css",
    ".scss": "scss",
    ".less": "less",
    ".md": "markdown",
    ".toml": "toml",
    ".ini": "ini",
    ".cfg": "ini",
    ".dockerfile": "dockerfile",
    ".tf": "terraform",
    ".hcl": "terraform",
}

# Маппинг для определения языка по содержимому (shebang)
SHEBANG_TO_LANGUAGE: dict[str, str] = {
    "python3": "python",
    "python": "python",
    "node": "javascript",
    "bash": "bash",
    "sh": "bash",
    "zsh": "bash",
}


def detect_language(file_path: str) -> str | None:
    """Определяет язык программирования по пути файла.

    Args:
        file_path: Путь к файлу или имя файла.

    Returns:
        Название языка или None, если язык не определён.
    """
    path = file_path.lower()

    # Проверка по расширению
    for ext, lang in EXTENSION_TO_LANGUAGE.items():
        if path.endswith(ext):
            return lang

    # Проверка на Dockerfile
    if path.endswith("dockerfile"):
        return "dockerfile"

    # Проверка на Makefile
    if path.endswith("makefile") or path.endswith(".mk"):
        return "makefile"

    return None


def detect_languages_from_files(file_paths: list[str]) -> dict[str, list[str]]:
    """Определяет языки для списка файлов.

    Args:
        file_paths: Список путей к файлам.

    Returns:
        Словарь {язык: [список файлов]}.
    """
    result: dict[str, list[str]] = {}

    for file_path in file_paths:
        lang = detect_language(file_path)
        if lang:
            if lang not in result:
                result[lang] = []
            result[lang].append(file_path)

    return result
