"""Логика ревью кода через LLM."""

from __future__ import annotations

from openai import OpenAI

from .config import AppConfig
from .languages.prompts import get_system_prompt


class ReviewerError(Exception):
    """Ошибка при ревью."""


class CodeReviewer:
    """AI-ревьюер кода."""

    def __init__(self, config: AppConfig) -> None:
        """Инициализирует ревьюер.

        Args:
            config: Конфигурация приложения.
        """
        self.config = config
        self.client = OpenAI(
            base_url=config.provider.base_url,
            api_key=config.provider.resolved_api_key or "not-set",
        )

    def review_code(
        self,
        diff: str,
        language: str | None = None,
        focus: str | None = None,
        style_guide: str | None = None,
    ) -> str:
        """Отправляет diff в LLM и получает ревью.

        Args:
            diff: Текст diff.
            language: Язык программирования (опционально).
            focus: Фокус ревью ('tests', 'production').
            style_guide: Содержимое файла стиля.

        Returns:
            Текст ревью от LLM.

        Raises:
            ReviewerError: При ошибке запроса к LLM.
        """
        if not diff.strip():
            return "Нет изменений для ревью."

        system_prompt = get_system_prompt(
            language=language,
            focus=focus,
            style_guide=style_guide,
        )

        user_prompt = f"Проведи ревью следующего diff:\n\n```diff\n{diff}\n```"

        # Обрезаем, если превышен лимит токенов (примерная оценка)
        max_chars = self.config.review.max_diff_tokens * 4
        if len(user_prompt) > max_chars:
            user_prompt = user_prompt[:max_chars] + "\n\n... (diff обрезан из-за ограничения по размеру)"

        try:
            response = self.client.chat.completions.create(
                model=self.config.provider.model,
                temperature=self.config.provider.temperature,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
            return response.choices[0].message.content or "Пустой ответ от LLM."
        except Exception as e:
            raise ReviewerError(f"Ошибка при вызове LLM: {e}") from e

    def review_files(
        self,
        file_diffs: list[dict[str, str]],
        language: str | None = None,
        focus: str | None = None,
        style_guide: str | None = None,
    ) -> str:
        """Ревьюит список файлов по отдельности.

        Args:
            file_diffs: Список словарей с путём и diff.
            language: Язык программирования.
            focus: Фокус ревью.
            style_guide: Содержимое файла стиля.

        Returns:
            Объединённый текст ревью.
        """
        reviews = []

        for file_info in file_diffs:
            file_path = file_info["path"]
            file_diff = file_info["diff"]

            if not file_diff.strip():
                continue

            review = self.review_code(
                diff=file_diff,
                language=language,
                focus=focus,
                style_guide=style_guide,
            )
            reviews.append(f"### {file_path}\n\n{review}")

        return "\n\n---\n\n".join(reviews) if reviews else "Нет изменений для ревью."
