from dataclasses import dataclass
from typing import Dict


@dataclass
class ColorTheme:
    name: str
    description: str

    # Phase colors
    phase_senser: str = "cyan"
    phase_planner: str = "yellow"
    phase_actor: str = "magenta"
    phase_complete: str = "blue"

    # Status colors
    status_pending: str = "dim"
    status_running: str = "yellow"
    status_complete: str = "green"
    status_error: str = "red"
    status_warning: str = "yellow"

    # UI element colors
    user_text: str = "cyan"
    assistant_text: str = "green"
    system_text: str = "dim"
    thinking_text: str = "yellow dim"
    tool_text: str = "blue"
    knowledge_text: str = "cyan"

    # Accent colors
    accent_primary: str = "bright_cyan"
    accent_secondary: str = "bright_magenta"
    accent_success: str = "bright_green"
    accent_error: str = "bright_red"

    # Border styles
    border_main: str = "cyan"
    border_secondary: str = "blue dim"
    border_success: str = "green"
    border_error: str = "red"


# Predefined themes
CLAUDE_DARK = ColorTheme(
    name="claude_dark",
    description="Default Claude Code inspired theme",
    phase_senser="bright_cyan",
    phase_planner="bright_yellow",
    phase_actor="bright_magenta",
    phase_complete="bright_blue",
    status_running="yellow bold",
    status_complete="green bold",
    status_error="red bold",
    user_text="bright_cyan",
    assistant_text="bright_green",
    thinking_text="bright_black italic",
    tool_text="bright_blue",
    border_main="bright_cyan",
)

GITHUB_DARK = ColorTheme(
    name="github_dark",
    description="GitHub dark theme",
    phase_senser="blue",
    phase_planner="purple",
    phase_actor="green",
    phase_complete="cyan",
    status_running="orange3",
    status_complete="green",
    status_error="red",
    user_text="blue",
    assistant_text="white",
    thinking_text="gray dim",
    tool_text="purple",
    border_main="blue",
)

MONOKAI = ColorTheme(
    name="monokai",
    description="Monokai inspired theme",
    phase_senser="bright_magenta",
    phase_planner="bright_yellow",
    phase_actor="bright_green",
    phase_complete="bright_cyan",
    status_running="bright_yellow",
    status_complete="bright_green",
    status_error="bright_red",
    user_text="bright_magenta",
    assistant_text="bright_white",
    thinking_text="bright_yellow dim",
    tool_text="bright_cyan",
    border_main="bright_magenta",
)

DRACULA = ColorTheme(
    name="dracula",
    description="Dracula theme",
    phase_senser="bright_cyan",
    phase_planner="bright_yellow",
    phase_actor="bright_magenta",
    phase_complete="bright_blue",
    status_running="bright_yellow",
    status_complete="bright_green",
    status_error="bright_red",
    user_text="bright_cyan",
    assistant_text="bright_white",
    thinking_text="bright_yellow dim",
    tool_text="bright_magenta",
    border_main="bright_magenta",
)

NORD = ColorTheme(
    name="nord",
    description="Nord theme",
    phase_senser="cyan",
    phase_planner="blue",
    phase_actor="green",
    phase_complete="magenta",
    status_running="blue",
    status_complete="green",
    status_error="red",
    user_text="cyan",
    assistant_text="white",
    thinking_text="blue dim",
    tool_text="magenta",
    border_main="blue",
)


# Theme registry
THEMES: Dict[str, ColorTheme] = {
    "claude_dark": CLAUDE_DARK,
    "github_dark": GITHUB_DARK,
    "monokai": MONOKAI,
    "dracula": DRACULA,
    "nord": NORD,
}


def get_theme(theme_name: str = "claude_dark") -> ColorTheme:
    return THEMES.get(theme_name, CLAUDE_DARK)


def list_themes() -> Dict[str, str]:
    return {name: theme.description for name, theme in THEMES.items()}
