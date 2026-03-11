#!/usr/bin/env python3
"""
BitRAG PyTermGUI - Settings

Settings management and UI for the TUI.
"""

from __future__ import annotations

import os
import subprocess
from typing import Callable, Optional
from dataclasses import dataclass


# Lazy imports
def _get_config():
    """Lazy import of get_config."""
    from bitrag.core.config import get_config

    return get_config


@dataclass
class AppSettings:
    """Application settings."""

    default_model: str
    embedding_model: str
    ollama_base_url: str
    chroma_dir: str
    data_dir: str
    sessions_dir: str
    hybrid_alpha: float = 0.5
    hybrid_search_enabled: bool = True


class SettingsManager:
    """
    Manages application settings for TUI.

    Features:
    - Load/save settings
    - Model selection
    - Alpha parameter adjustment
    - Directory configuration
    - List available Ollama models
    """

    def __init__(self):
        self._config = None
        self._settings = None

        # Callbacks
        self.on_settings_changed: Callable[[AppSettings], None] | None = None

    @property
    def config(self):
        """Lazy load config."""
        if self._config is None:
            self._config = _get_config()
        return self._config

    def get_settings(self) -> AppSettings:
        """Get current settings."""
        if self._settings is None:
            self._settings = AppSettings(
                default_model=self.config.default_model,
                embedding_model=self.config.embedding_model,
                ollama_base_url=self.config.ollama_base_url,
                chroma_dir=self.config.chroma_dir,
                data_dir=self.config.data_dir,
                sessions_dir=self.config.sessions_dir,
                hybrid_alpha=getattr(self.config, "hybrid_alpha", 0.5),
                hybrid_search_enabled=getattr(self.config, "hybrid_search_enabled", True),
            )
        return self._settings

    def set_default_model(self, model: str) -> bool:
        """Set the default model."""
        try:
            self.config.default_model = model
            self.config.save()
            self._settings = None  # Reset cached
            if self.on_settings_changed:
                self.on_settings_changed(self.get_settings())
            return True
        except Exception as e:
            print(f"Error saving model: {e}")
            return False

    def set_hybrid_alpha(self, alpha: float) -> bool:
        """Set hybrid search alpha (0-1)."""
        alpha = max(0.0, min(1.0, alpha))
        try:
            self.config.hybrid_alpha = alpha
            self.config.save()
            self._settings = None
            if self.on_settings_changed:
                self.on_settings_changed(self.get_settings())
            return True
        except Exception as e:
            print(f"Error saving alpha: {e}")
            return False

    def set_hybrid_enabled(self, enabled: bool) -> bool:
        """Enable/disable hybrid search."""
        try:
            self.config.hybrid_search_enabled = enabled
            self.config.save()
            self._settings = None
            if self.on_settings_changed:
                self.on_settings_changed(self.get_settings())
            return True
        except Exception as e:
            print(f"Error saving: {e}")
            return False

    def list_ollama_models(self) -> list[str]:
        """List available Ollama models."""
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode != 0:
                return []

            models = []
            lines = result.stdout.strip().split("\n")[1:]  # Skip header
            for line in lines:
                if line.strip():
                    parts = line.split()
                    if parts:
                        models.append(parts[0])
            return models
        except Exception:
            return []

    def format_settings(self) -> str:
        """Format settings for display."""
        settings = self.get_settings()

        lines = [
            "[bold]Current Settings:[/]",
            "",
            f"Model: {settings.default_model}",
            f"Embedding: {settings.embedding_model}",
            f"Ollama URL: {settings.ollama_base_url}",
            "",
            f"Hybrid Search: {'Enabled' if settings.hybrid_search_enabled else 'Disabled'}",
            f"Alpha: {settings.hybrid_alpha}",
            "",
            "[bold]Directories:[/]",
            f"Data: {settings.data_dir}",
            f"Chroma: {settings.chroma_dir}",
            f"Sessions: {settings.sessions_dir}",
        ]

        return "\n".join(lines)

    def format_ollama_models(self) -> str:
        """Format available models for display."""
        models = self.list_ollama_models()

        if not models:
            return "No Ollama models found."

        lines = ["[bold]Available Models:[/]"]
        for i, model in enumerate(models, 1):
            current = " (current)" if model == self.get_settings().default_model else ""
            lines.append(f"  {i}. {model}{current}")

        return "\n".join(lines)


class SettingsDialog:
    """
    Settings dialog for TUI.

    Provides UI for:
    - Viewing current settings
    - Selecting model
    - Adjusting alpha
    - Saving changes
    """

    def __init__(self, manager: SettingsManager | None = None):
        self.manager = manager or SettingsManager()

    def show(self) -> bool:
        """
        Show settings dialog.

        Returns:
            True if settings changed
        """
        # This would be integrated with the actual TUI
        # For now, just return settings info
        print("\n" + self.manager.format_settings())
        print("\n" + self.manager.format_ollama_models())
        return False

    def prompt_model_selection(self) -> str | None:
        """Prompt user to select a model."""
        models = self.manager.list_ollama_models()
        if not models:
            print("No models available")
            return None

        print("\nSelect a model:")
        for i, model in enumerate(models, 1):
            print(f"  {i}. {model}")
        print("  0. Cancel")

        try:
            choice = int(input("\nChoice: "))
            if 0 < choice <= len(models):
                return models[choice - 1]
        except ValueError:
            pass

        return None

    def prompt_alpha(self) -> float | None:
        """Prompt user to enter alpha value."""
        print("\nEnter hybrid search alpha (0.0 - 1.0):")
        print("  0.0 = keyword only")
        print("  1.0 = vector only")
        print("  0.5 = balanced (default)")

        try:
            value = input("Alpha: ")
            alpha = float(value)
            if 0.0 <= alpha <= 1.0:
                return alpha
        except ValueError:
            pass

        return None


# Export
__all__ = [
    "AppSettings",
    "SettingsManager",
    "SettingsDialog",
]
