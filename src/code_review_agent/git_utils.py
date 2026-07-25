"""Утилиты для работы с git: получение diff, список файлов."""

from __future__ import annotations

import subprocess
from pathlib import Path

from git import Repo


class GitError(Exception):
    """Ошибка git-операции."""


def get_repo(path: str | Path | None = None) -> Repo:
    """Получает git-репозиторий по указанному пути.

    Args:
        path: Путь к директории. Если None — текущая директория.

    Returns:
        Объект Repo.

    Raises:
        GitError: Если директория не является git-репозиторием.
    """
    try:
        return Repo(path, search_parent_directories=True)
    except Exception as e:
        raise GitError(f"Не удалось найти git-репозиторий: {e}") from e


def get_diff(repo: Repo, target: str) -> str:
    """Получает diff для указанной ветки или диапазона коммитов.

    Поддерживает два формата:
    - Имя ветки: 'feature/auth' — сравнение с main
    - Диапазон коммитов: 'main..feature/auth'

    Args:
        repo: Git-репозиторий.
        target: Ветка или диапазон коммитов.

    Returns:
        Текст diff.
    """
    # Определяем базовую ветку
    base = _get_base_branch(repo)

    if ".." in target:
        # Диапазон коммитов: main..feature/auth
        try:
            diff = repo.git.diff(target)
            return diff
        except Exception as e:
            raise GitError(f"Ошибка получения diff для диапазона '{target}': {e}") from e
    else:
        # Имя ветки: сравнение с base
        try:
            diff = repo.git.diff(f"{base}...{target}")
            return diff
        except Exception as e:
            raise GitError(f"Ошибка получения diff для ветки '{target}': {e}") from e


def get_diff_files(repo: Repo, target: str) -> list[str]:
    """Получает список изменённых файлов.

    Args:
        repo: Git-репозиторий.
        target: Ветка или диапазон коммитов.

    Returns:
        Список имён файлов.
    """
    base = _get_base_branch(repo)

    if ".." in target:
        try:
            files = repo.git.diff("--name-only", target).splitlines()
            return [f for f in files if f.strip()]
        except Exception:
            return []
    else:
        try:
            files = repo.git.diff("--name-only", f"{base}...{target}").splitlines()
            return [f for f in files if f.strip()]
        except Exception:
            return []


def get_file_content(repo: Repo, file_path: str, ref: str = "HEAD") -> str | None:
    """Получает содержимое файла из определённого коммита.

    Args:
        repo: Git-репозиторий.
        file_path: Путь к файлу.
        ref: Ссылка на коммит (по умолчанию HEAD).

    Returns:
        Содержимое файла или None.
    """
    try:
        return repo.git.show(f"{ref}:{file_path}")
    except Exception:
        return None


def get_diff_with_content(repo: Repo, target: str) -> list[dict[str, str]]:
    """Получает diff с содержимым изменённых файлов.

    Args:
        repo: Git-репозиторий.
        target: Ветка или диапазон коммитов.

    Returns:
        Список словарей с путём и содержимым diff для каждого файла.
    """
    base = _get_base_branch(repo)
    result = []

    if ".." in target:
        range_spec = target
    else:
        range_spec = f"{base}...{target}"

    try:
        # Получаем список файлов с их статусами
        output = repo.git.diff("--name-status", range_spec)
        for line in output.splitlines():
            if not line.strip():
                continue
            parts = line.split("\t", 1)
            if len(parts) < 2:
                continue
            status, file_path = parts[0], parts[1]

            # Получаем diff для конкретного файла
            try:
                file_diff = repo.git.diff(range_spec, "--", file_path)
                result.append({
                    "path": file_path,
                    "status": status,
                    "diff": file_diff,
                })
            except Exception:
                continue

    except Exception as e:
        raise GitError(f"Ошибка получения diff: {e}") from e

    return result


def _get_base_branch(repo: Repo) -> str:
    """Определяет базовую ветку для сравнения.

    Пытается найти main или master.
    """
    # Проверяем وجود main
    try:
        repo.git.rev_parse("--verify", "refs/heads/main")
        return "main"
    except Exception:
        pass

    # Проверяем наличие master
    try:
        repo.git.rev-parse("--verify", "refs/heads/master")
        return "master"
    except Exception:
        pass

    # Fallback — используем HEAD
    return "HEAD"


def get_current_branch(repo: Repo) -> str:
    """Получает имя текущей ветки."""
    try:
        return repo.active_branch.name
    except Exception:
        return "HEAD"
