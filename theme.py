# theme.py
"""Thème et couleurs du CLI"""

from rich.color import Color
from rich.style import Style
from rich.theme import Theme
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

# Couleurs - Utiliser des couleurs reconnues par Rich
PRIMARY = "red"           # ou "#e94560"
SECONDARY = "blue"        # ou "#4dabf7"
SUCCESS = "green"         # ou "#51cf66"
WARNING = "yellow"        # ou "#f59f00"
DANGER = "red"            # ou "#ff6b6b"
INFO = "magenta"          # ou "#845ef7"
LIGHT = "white"
MUTED = "grey50"          # ou "grey50" au lieu de "#888"

# Styles Rich
STYLES = {
    "primary": Style(color=PRIMARY),
    "secondary": Style(color=SECONDARY),
    "success": Style(color=SUCCESS),
    "warning": Style(color=WARNING),
    "danger": Style(color=DANGER),
    "info": Style(color=INFO),
    "muted": Style(color=MUTED),
    "title": Style(color=PRIMARY, bold=True),
    "header": Style(color=LIGHT, bold=True),
    "error": Style(color=DANGER, bold=True),
    "success_text": Style(color=SUCCESS, bold=True),
    "highlight": Style(color=PRIMARY, bold=True),
}

THEME = Theme({
    "primary": PRIMARY,
    "secondary": SECONDARY,
    "success": SUCCESS,
    "warning": WARNING,
    "danger": DANGER,
    "info": INFO,
    "muted": MUTED,
})

console = Console(theme=THEME)

def print_header(text: str):
    """Affiche un en-tête"""
    console.print(Panel(Text(text, style="title"), border_style=PRIMARY))

def print_success(text: str):
    """Affiche un message de succès"""
    console.print(f"✅ {text}", style="success")

def print_error(text: str):
    """Affiche un message d'erreur"""
    console.print(f"❌ {text}", style="danger")

def print_info(text: str):
    """Affiche un message d'information"""
    console.print(f"ℹ️ {text}", style="muted")

def print_warning(text: str):
    """Affiche un avertissement"""
    console.print(f"⚠️ {text}", style="warning")

def create_table(title: str = None, columns: list = None) -> Table:
    """Crée un tableau stylisé"""
    table = Table(title=title, border_style=PRIMARY, header_style="bold primary")
    if columns:
        for col in columns:
            table.add_column(col)
    return table
