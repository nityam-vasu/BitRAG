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
            config_func = _get_config()
            self._config = config_func()  # Call the function to get config instance
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


# Predefined models for quick selection
PREDEFINED_MODELS = [
    "llama3.2:1b",
    "llama3.2:3b",
    "llama3.1:8b",
    "mistral:7b",
    "phi3:14b",
    "gemma2:2b",
    "qwen2.5:0.5b",
    "qwen2.5:3b",
]


class OllamaManager:
    """Manages Ollama operations (list, pull, delete models)."""

    @staticmethod
    def list_models() -> list[str]:
        """List available Ollama models."""
        try:
            result = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")[1:]  # Skip header
                models = []
                for line in lines:
                    if line.strip():
                        parts = line.split()
                        if parts:
                            models.append(parts[0])
                return models
        except Exception as e:
            print(f"[WARN] Could not list models: {e}")
        return []

    @staticmethod
    def pull_model(
        model_name: str, progress_callback: Callable[[float], None] | None = None
    ) -> bool:
        """Pull a model from Ollama registry."""
        try:
            process = subprocess.Popen(
                ["ollama", "pull", model_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            while True:
                line = process.stdout.readline()
                if not line and process.poll() is not None:
                    break
                if line and "%" in line:
                    try:
                        pct = float(line.split("%")[0].split()[-1])
                        if progress_callback:
                            progress_callback(pct)
                    except:
                        pass

            return process.returncode == 0
        except Exception as e:
            print(f"[ERROR] Could not pull model: {e}")
            return False

    @staticmethod
    def delete_model(model_name: str) -> bool:
        """Delete an Ollama model."""
        try:
            result = subprocess.run(
                ["ollama", "rm", model_name], capture_output=True, text=True, timeout=30
            )
            return result.returncode == 0
        except Exception as e:
            print(f"[ERROR] Could not delete model: {e}")
            return False

    @staticmethod
    def is_running() -> bool:
        """Check if Ollama is running."""
        try:
            result = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except:
            return False


class ModelDownloadDialog:
    """Dialog for downloading models with progress."""

    def __init__(self, model_name: str):
        self.model_name = model_name
        self.progress = 0.0
        self.status = "pending"

    def start_download(self) -> bool:
        """Start the model download."""
        self.status = "downloading"
        print(f"[Download] Starting: {self.model_name}")

        def update_progress(pct: float):
            self.progress = pct

        success = OllamaManager.pull_model(self.model_name, update_progress)

        if success:
            self.status = "complete"
            print(f"[Download] Complete: {self.model_name}")
        else:
            self.status = "error"
            print(f"[Download] Failed: {self.model_name}")

        return success


class ModelDeleteDialog:
    """Dialog for deleting models."""

    def __init__(self):
        self.models = OllamaManager.list_models()

    def delete_model(self, model: str) -> bool:
        """Delete a model."""
        print(f"[BitRAG] Deleting model: {model}")

        if OllamaManager.delete_model(model):
            print(f"[BitRAG] Model deleted: {model}")
            if model in self.models:
                self.models.remove(model)
            return True
        else:
            print(f"[BitRAG] Failed to delete model: {model}")
            return False


# Extended SettingsManager with model management
class SettingsManagerExtended(SettingsManager):
    """Extended settings manager with model management."""

    def get_ollama_port(self) -> str:
        """Get Ollama port from URL."""
        url = self.config.ollama_base_url
        if ":" in url:
            return url.rsplit(":", 1)[-1]
        return "11434"

    def set_ollama_port(self, port: str) -> bool:
        """Set Ollama port in URL."""
        try:
            base_url = f"http://localhost:{port}"
            self.config.ollama_base_url = base_url
            self.config.save()
            self._settings = None
            if self.on_settings_changed:
                self.on_settings_changed(self.get_settings())
            return True
        except Exception as e:
            print(f"Error saving port: {e}")
            return False

    def download_model(self, model_name: str) -> ModelDownloadDialog:
        """Download a model."""
        return ModelDownloadDialog(model_name)

    def delete_model(self, model_name: str) -> bool:
        """Delete a model."""
        return ModelDeleteDialog().delete_model(model_name)

    def get_predefined_models(self) -> list[str]:
        """Get list of predefined models."""
        return PREDEFINED_MODELS


# Extended SettingsDialog with full UI
class SettingsDialogExtended:
    """
    Extended settings dialog with full TUI features.

    Features:
    - Ollama port configuration
    - Model selection from available Ollama models
    - Model download with progress
    - Model delete
    - Dual model mode toggle
    - Hybrid retrieval slider (-1 to 1)
    - Document management navigation
    """

    def __init__(
        self,
        manager: SettingsManagerExtended | None = None,
        on_show_documents: Callable | None = None,
    ):
        self.manager = manager or SettingsManagerExtended()
        self.on_show_documents = on_show_documents
        self.dual_model_enabled = False
        self.hybrid_alpha = 0.0

    def show_port_config(self) -> None:
        """Show Ollama port configuration."""
        port = self.manager.get_ollama_port()
        print(f"\n[Ollama Port]")
        print(f"  Current: {port}")
        print(f"  Default: 11434")

    def show_model_selection(self) -> None:
        """Show model selection."""
        current = self.manager.get_settings().default_model
        available = self.manager.list_ollama_models()

        print(f"\n[Model Selection]")
        print(f"  Current: {current}")
        print(f"  Available models:")
        if available:
            for model in available:
                marker = " *" if model == current else ""
                print(f"    - {model}{marker}")
        else:
            print("    (No models installed)")

        print(f"\n  Predefined models:")
        for model in PREDEFINED_MODELS:
            print(f"    - {model}")

    def show_model_download(self) -> None:
        """Show model download options."""
        print(f"\n[Download Model]")
        print(f"  Enter model name or select from predefined list")
        print(f"  Example: ollama pull llama3.2:1b")

    def show_model_delete(self) -> None:
        """Show model delete options."""
        installed = self.manager.list_ollama_models()

        print(f"\n[Delete Model]")
        if installed:
            print(f"  Installed models:")
            for model in installed:
                print(f"    - {model}")
                print(f"      [Delete]")
        else:
            print("  No models installed")

    def show_dual_model_mode(self) -> None:
        """Show dual model mode options."""
        status = "Enabled" if self.dual_model_enabled else "Disabled"

        print(f"\n[Dual Model Mode]")
        print(f"  Status: {status}")
        if self.dual_model_enabled:
            print(f"  Warning: Using two models increases inference time and resource usage")
            print(f"  Model 1: ______")
            print(f"  Model 2: ______")

    def show_hybrid_slider(self) -> None:
        """Show hybrid retrieval slider."""
        labels = {-1: "Pure Vector", 0: "Hybrid", 1: "Pure Keyword"}

        print(f"\n[Hybrid Retrieval]")
        print(f"  Current: {self.hybrid_alpha} ({labels.get(int(self.hybrid_alpha), 'Hybrid')})")
        print(f"  Vector <----|----> Keyword")
        print(f"         -1    0     1")

    def show_documents(self) -> None:
        """Navigate to document management."""
        if self.on_show_documents:
            self.on_show_documents()

    def show_full_settings(self) -> None:
        """Show all settings."""
        print("\n" + "=" * 50)
        print("  ⚙ Settings")
        print("=" * 50)

        self.show_port_config()
        self.show_model_selection()
        self.show_model_download()
        self.show_model_delete()
        self.show_dual_model_mode()
        self.show_hybrid_slider()

        print("\n[Document Management]")
        print("  [Open Documents] - Manage indexed documents")

        print("\n" + "=" * 50)
        print("  [Save Settings]  [Cancel]")
        print("=" * 50)


# Export all
__all__ = [
    "AppSettings",
    "SettingsManager",
    "SettingsDialog",
    "OllamaManager",
    "ModelDownloadDialog",
    "ModelDeleteDialog",
    "SettingsManagerExtended",
    "SettingsDialogExtended",
    "PREDEFINED_MODELS",
]
