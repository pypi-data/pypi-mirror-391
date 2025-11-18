import json
import os
from pathlib import Path
from typing import Optional, Dict, Any, Literal
from pydantic import BaseModel, Field
from enum import Enum


class APIProvider(str, Enum):
    JARVIS = "jarvis"
    OPENAI = "openai"
    CLAUDE = "claude"


class DisplayConfig(BaseModel):
    show_thinking: bool = True
    show_tools: bool = True
    show_knowledge_sources: bool = True
    markdown: bool = True
    colors: bool = True
    live_mode: bool = False
    theme: str = "claude_dark"


class JarvisConfig(BaseModel):
    api_base_url: str = ""
    login_code: str = ""
    user_id: str = ""
    jwt_token: Optional[str] = None
    token_expires_at: Optional[str] = None

    @property
    def effective_user_id(self) -> str:
        return self.login_code or self.user_id


class OpenAIConfig(BaseModel):
    api_key: Optional[str] = None
    model: str = "gpt-4-turbo"


class ClaudeConfig(BaseModel):
    api_key: Optional[str] = None
    model: str = "claude-haiku-4-5-20251001"


class Config(BaseModel):
    # Current API provider
    api_provider: APIProvider = APIProvider.JARVIS

    # Provider-specific configurations
    jarvis: JarvisConfig = Field(default_factory=JarvisConfig)
    openai: OpenAIConfig = Field(default_factory=OpenAIConfig)
    claude: ClaudeConfig = Field(default_factory=ClaudeConfig)

    # Display settings (shared across all providers)
    display: DisplayConfig = Field(default_factory=DisplayConfig)

    # Legacy fields for backward compatibility
    api_base_url: str = ""
    login_code: str = ""
    user_id: str = ""
    api_keys: Optional[Dict[str, Optional[str]]] = None

    def model_post_init(self, __context):
        """Migrate legacy config to new structure"""
        # Migrate Jarvis settings
        if self.api_base_url and not self.jarvis.api_base_url:
            self.jarvis.api_base_url = self.api_base_url
        if self.login_code and not self.jarvis.login_code:
            self.jarvis.login_code = self.login_code
        if self.user_id and not self.jarvis.user_id:
            self.jarvis.user_id = self.user_id

        # Migrate API keys
        if self.api_keys:
            if self.api_keys.get("openai_api_key") and not self.openai.api_key:
                self.openai.api_key = self.api_keys["openai_api_key"]
            if self.api_keys.get("claude_api_key") and not self.claude.api_key:
                self.claude.api_key = self.api_keys["claude_api_key"]

    def to_clean_dict(self) -> Dict[str, Any]:
        """Export config without legacy fields"""
        return {
            "api_provider": self.api_provider.value,
            "jarvis": self.jarvis.model_dump(),
            "openai": self.openai.model_dump(),
            "claude": self.claude.model_dump(),
            "display": self.display.model_dump(),
        }

    @property
    def effective_user_id(self) -> str:
        return self.jarvis.effective_user_id


class ConfigManager:
    def __init__(self, config_path: Optional[Path] = None):
        if config_path is None:
            config_path = Path.home() / ".jvs-cli" / "config.json"

        self.config_path = config_path
        self.config_dir = config_path.parent
        self._config: Optional[Config] = None

    def _ensure_config_dir(self) -> None:
        if not self.config_dir.exists():
            self.config_dir.mkdir(parents=True, exist_ok=True)

    def load(self) -> Config:
        if not self.config_path.exists():
            return Config()
        try:
            with open(self.config_path, "r") as f:
                data = json.load(f)
            self._config = Config(**data)
            return self._config
        except Exception as e:
            raise RuntimeError(f"Failed to load config from {self.config_path}: {e}")

    def save(self, config: Config) -> None:
        self._ensure_config_dir()
        try:
            with open(self.config_path, "w") as f:
                json.dump(config.to_clean_dict(), f, indent=2)
            self._config = config
        except Exception as e:
            raise RuntimeError(f"Failed to save config to {self.config_path}: {e}")

    def get(self) -> Config:
        if self._config is None:
            self._config = self.load()
        return self._config

    def set_value(self, key_path: str, value: Any) -> None:
        config = self.get()
        config_dict = config.model_dump()
        keys = key_path.split(".")
        current = config_dict
        for key in keys[:-1]:
            if key not in current:
                raise ValueError(f"Invalid config key path: {key_path}")
            current = current[key]
        final_key = keys[-1]
        if final_key not in current:
            raise ValueError(f"Invalid config key: {final_key}")
        if isinstance(current[final_key], bool):
            value = value.lower() in ("true", "1", "yes", "on") if isinstance(value, str) else bool(value)
        current[final_key] = value
        updated_config = Config(**config_dict)
        self.save(updated_config)

    def exists(self) -> bool:
        return self.config_path.exists()

    def init_interactive(self) -> Config:
        from rich.console import Console
        from rich.prompt import Prompt

        console = Console()
        console.print("\n[bold cyan]JVS CLI Configuration[/bold cyan]\n")

        api_url = ""
        while not api_url:
            api_url = Prompt.ask("API URL").strip()
            if not api_url:
                console.print("[red]Required[/red]")
            elif not (api_url.startswith("http://") or api_url.startswith("https://")):
                console.print("[red]Must start with http:// or https://[/red]")
                api_url = ""

        login_code = Prompt.ask("Login Code").strip()

        theme = Prompt.ask(
            "Theme",
            choices=["claude_dark", "github_dark", "monokai", "dracula", "nord"],
            default="claude_dark"
        )

        config = Config(
            api_provider=APIProvider.JARVIS,
            jarvis=JarvisConfig(
                api_base_url=api_url,
                login_code=login_code
            ),
            display=DisplayConfig(
                show_thinking=True,
                show_tools=True,
                show_knowledge_sources=True,
                markdown=True,
                colors=True,
                live_mode=True,
                theme=theme
            )
        )

        self.save(config)

        console.print(f"\n[green]✓[/green] Saved to: {self.config_path}")

        return config


# Global config manager instance
_config_manager: Optional[ConfigManager] = None


def get_config_manager() -> ConfigManager:
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager
