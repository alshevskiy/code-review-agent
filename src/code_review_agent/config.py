"""Конфигурация провайдера LLM."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass
class ProviderConfig:
    """Настройки LLM провайдера."""

    base_url: str = "https://api.openai.com/v1"
    api_key: str = ""
    api_key_env: str = "OPENAI_API_KEY"
    model: str = "gpt-4o"
    temperature: float = 0.1

    @property
    def resolved_api_key(self) -> str:
        """Возвращает API ключ из переменной окружения или напрямую."""
        if self.api_key:
            return self.api_key
        return os.environ.get(self.api_key_env, "")


@dataclass
class ReviewConfig:
    """Настройки ревью."""

    exclude_patterns: list[str] = field(default_factory=lambda: [
        "vendor/**",
        "*.lock",
        "package-lock.json",
        "node_modules/**",
        "*.min.js",
        "*.min.css",
    ])
    max_diff_tokens: int = 30000


@dataclass
class AppConfig:
    """Общая конфигурация приложения."""

    provider: ProviderConfig = field(default_factory=ProviderConfig)
    review: ReviewConfig = field(default_factory=ReviewConfig)


def load_config(config_path: str | Path | None = None) -> AppConfig:
    """Загружает конфигурацию из YAML файла."""
    config = AppConfig()

    if config_path is None:
        config_path = Path(".code-review-agent.yaml")
    else:
        config_path = Path(config_path)

    if not config_path.exists():
        return config

    with open(config_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    if "provider" in data:
        p = data["provider"]
        config.provider.base_url = p.get("base_url", config.provider.base_url)
        config.provider.api_key = p.get("api_key", config.provider.api_key)
        config.provider.api_key_env = p.get("api_key_env", config.provider.api_key_env)
        config.provider.model = p.get("model", config.provider.model)
        config.provider.temperature = p.get("temperature", config.provider.temperature)

    if "review" in data:
        r = data["review"]
        config.review.exclude_patterns = r.get("exclude_patterns", config.review.exclude_patterns)
        config.review.max_diff_tokens = r.get("max_diff_tokens", config.review.max_diff_tokens)

    return config
