# screens/settings.py
"""Paramètres"""

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Label, Static, Button, Switch
from textual.containers import Horizontal, Container

class SettingsScreen(Screen):
    """Écran des paramètres"""
    
    CSS = """
    SettingsScreen {
        background: $surface;
    }
    
    #settings-header {
        height: 3;
        border-bottom: solid $primary;
        padding: 0 1;
    }
    
    #settings-content {
        margin: 2;
        padding: 2;
        border: solid $secondary;
    }
    
    #settings-content > Label {
        padding: 1;
    }
    
    .setting-row {
        padding: 1;
    }
    """
    
    def compose(self) -> ComposeResult:
        """Composition des paramètres"""
        with Horizontal(id="settings-header"):
            yield Label("⚙️ Paramètres")
        
        with Container(id="settings-content"):
            yield Label("Paramètres du CLI", classes="title")
            
            with Horizontal(classes="setting-row"):
                yield Label("🌙 Thème sombre")
                yield Switch(value=True, id="dark-theme")
            
            with Horizontal(classes="setting-row"):
                yield Label("🔔 Notifications")
                yield Switch(value=True, id="notifications")
            
            with Horizontal(classes="setting-row"):
                yield Label("⚡ Auto-complétion")
                yield Switch(value=True, id="autocomplete")
            
            yield Button("🔙 Retour", id="back-dashboard", variant="primary")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Clic sur un bouton"""
        if event.button.id == "back-dashboard":
            self.app.pop_screen()
