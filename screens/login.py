# screens/login.py
"""Écran de connexion"""

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Label, Input, Button, Static, LoadingIndicator
from textual.containers import Vertical, Center, Container
from textual import events
from rich.text import Text

class LoginScreen(Screen):
    """Écran de connexion"""
    
    CSS = """
    LoginScreen {
        align: center middle;
    }
    
    #login-box {
        width: 50;
        height: auto;
        border: solid $primary;
        padding: 2 3;
        background: $surface;
    }
    
    #login-box > Label {
        text-align: center;
        padding: 1 0;
    }
    
    #login-box > Input {
        margin: 1 0;
    }
    
    #login-box > Button {
        margin: 1 0;
    }
    
    #error {
        color: $error;
        text-align: center;
        height: 3;
    }
    
    #status {
        color: $success;
        text-align: center;
        height: 3;
    }
    """
    
    def compose(self) -> ComposeResult:
        """Composition de l'écran"""
        with Container(id="login-box"):
            yield Label("🐬 STRIP CLI", classes="title")
            yield Label("Connectez-vous à votre compte", classes="subtitle")
            
            yield Input(placeholder="👤 Nom d'utilisateur", id="username")
            yield Input(placeholder="🔒 Mot de passe", id="password", password=True)
            
            yield Button("🚀 Se connecter", id="login-btn", variant="primary")
            yield Static("", id="error")
            yield Static("", id="status")
    
    def on_mount(self) -> None:
        """Focus sur le champ username au démarrage"""
        self.query_one("#username").focus()
    
    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Soumission d'un champ input"""
        if event.input.id == "username":
            self.query_one("#password").focus()
        elif event.input.id == "password":
            self.do_login()
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Clic sur un bouton"""
        if event.button.id == "login-btn":
            self.do_login()
    
    def on_key(self, event: events.Key) -> None:
        """Touche Escape pour quitter"""
        if event.key == "escape":
            self.app.exit()
    
    def do_login(self) -> None:
        """Tente de se connecter"""
        username = self.query_one("#username").value
        password = self.query_one("#password").value
        
        if not username or not password:
            self.query_one("#error").update("⚠️ Veuillez remplir tous les champs")
            return
        
        # Effacer les messages précédents
        self.query_one("#error").update("")
        self.query_one("#status").update("🔄 Connexion en cours...")
        
        # Tenter la connexion
        success = self.app.auth.login(username, password)
        
        if success:
            self.app.current_user = self.app.auth.user_data
            self.query_one("#status").update("✅ Connexion réussie !")
            self.app.push_screen("dashboard")
            self.query_one("#status").update("")
        else:
            self.query_one("#status").update("")
            self.query_one("#error").update("❌ Identifiants incorrects")
