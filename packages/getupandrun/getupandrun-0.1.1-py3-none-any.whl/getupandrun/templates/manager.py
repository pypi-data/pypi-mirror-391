"""Template manager for caching and retrieving templates."""

import json
from pathlib import Path
from typing import Any, Optional

from getupandrun.gpt.integration import StackConfig
from getupandrun.templates.definitions import (
    TEMPLATES,
    get_template,
    list_templates,
    search_templates,
)
from getupandrun.utils.logger import print_info, print_warning


class TemplateManager:
    """Manages template caching and retrieval."""

    CACHE_DIR = Path.home() / ".getupandrun" / "templates"
    CACHE_FILE = CACHE_DIR / "cache.json"

    def __init__(self) -> None:
        """Initialize template manager."""
        self.cache_dir = TemplateManager.CACHE_DIR
        self.cache_file = TemplateManager.CACHE_FILE
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def get_template(self, key: str, use_cache: bool = True) -> StackConfig:
        """
        Get a template, optionally from cache.

        Args:
            key: Template key
            use_cache: Whether to use cached version

        Returns:
            StackConfig instance
        """
        if use_cache:
            cached = self._load_from_cache(key)
            if cached:
                print_info(f"Using cached template: {key}")
                return cached

        template = get_template(key)
        self._save_to_cache(key, template)
        return template

    def list_templates(self) -> list[dict[str, str]]:
        """
        List all available templates.

        Returns:
            List of template info dictionaries
        """
        return list_templates()

    def search_templates(self, query: str) -> list[dict[str, str]]:
        """
        Search templates by query.

        Args:
            query: Search query

        Returns:
            List of matching templates
        """
        return search_templates(query)

    def _save_to_cache(self, key: str, config: StackConfig) -> None:
        """
        Save template to cache.

        Args:
            key: Template key
            config: StackConfig to cache
        """
        try:
            cache = self._load_cache()
            cache[key] = config.to_dict()
            with open(self.cache_file, "w") as f:
                json.dump(cache, f, indent=2)
        except Exception as e:
            print_warning(f"Failed to cache template: {e}")

    def _load_from_cache(self, key: str) -> Optional[StackConfig]:
        """
        Load template from cache.

        Args:
            key: Template key

        Returns:
            StackConfig if found in cache, None otherwise
        """
        try:
            cache = self._load_cache()
            if key in cache:
                return StackConfig.from_dict(cache[key])
        except Exception as e:
            print_warning(f"Failed to load from cache: {e}")

        return None

    def _load_cache(self) -> dict[str, Any]:
        """
        Load entire cache from file.

        Returns:
            Cache dictionary
        """
        try:
            if self.cache_file.exists():
                with open(self.cache_file, "r") as f:
                    return json.load(f)
        except Exception as e:
            print_warning(f"Failed to load cache: {e}")

        return {}

    def clear_cache(self) -> None:
        """Clear template cache."""
        try:
            if self.cache_file.exists():
                self.cache_file.unlink()
            print_info("Template cache cleared.")
        except Exception as e:
            print_warning(f"Failed to clear cache: {e}")


def get_template_manager() -> TemplateManager:
    """
    Get a TemplateManager instance.

    Returns:
        TemplateManager instance
    """
    return TemplateManager()

