# app.py
"""Application Textual principale"""

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer
from textual.containers import Container

from screens import (
    LoginScreen,
    DashboardScreen,
    FeedScreen,
    ChatScreen,
    ProfileScreen,
    LiveScreen,
    SettingsScreen
)

from api import APIClient
from auth import Auth
from config import Config

class StripApp(App):
    """Application STRIP CLI"""
    
    CSS_PATH = "styles/app.tcss"
    BINDINGS = [
        ("ctrl+q", "quit", "Quitter"),
        ("ctrl+l", "logout", "Déconnexion"),
        ("ctrl+d", "dashboard", "Dashboard"),
        ("ctrl+f", "feed", "Feed"),
        ("ctrl+c", "chat", "Chat"),
        ("ctrl+p", "profile", "Profil"),
        ("ctrl+v", "live", "Lives"),
        ("ctrl+s", "settings", "Paramètres"),
        ("ctrl+h", "help", "Aide"),
    ]
    
    # Enregistrement des écrans
    SCREENS = {
        "login": LoginScreen,
        "dashboard": DashboardScreen,
        "feed": FeedScreen,
        "chat": ChatScreen,
        "profile": ProfileScreen,
        "live": LiveScreen,
        "settings": SettingsScreen,
    }
    
    def __init__(self):
        super().__init__()
        self.config = Config()
        self.auth = Auth()
        self.api = APIClient()
        self.current_user = None
        
    def on_mount(self) -> None:
        """Montage de l'application"""
        # Vérifier si l'utilisateur est déjà connecté
        if self.auth.is_authenticated():
            self.current_user = self.auth.user_data
            self.push_screen("dashboard")
        else:
            self.push_screen("login")
    
    def compose(self) -> ComposeResult:
        """Composition de l'application"""
        yield Header(show_clock=True)
        yield Container(id="main-container")
        yield Footer()
    
    def action_dashboard(self) -> None:
        """Action: Dashboard"""
        self.push_screen("dashboard")
    
    def action_feed(self) -> None:
        """Action: Feed"""
        self.push_screen("feed")
    
    def action_chat(self) -> None:
        """Action: Chat"""
        self.push_screen("chat")
    
    def action_profile(self) -> None:
        """Action: Profil"""
        self.push_screen("profile")
    
    def action_live(self) -> None:
        """Action: Lives"""
        self.push_screen("live")
    
    def action_settings(self) -> None:
        """Action: Paramètres"""
        self.push_screen("settings")
    
    def action_logout(self) -> None:
        """Action: Déconnexion"""
        self.auth.logout()
        self.current_user = None
        self.pop_screen()
        self.push_screen("login")
    
    def action_help(self) -> None:
        """Action: Aide"""
        # TODO: Écran d'aide
        pass
    
    def get_user(self):
        """Retourne l'utilisateur courant"""
        return self.current_user
    
    def set_user(self, user):
        """Définit l'utilisateur courant"""
        self.current_user = user
        self.auth.user_data = user
