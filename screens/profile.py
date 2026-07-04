# screens/profile.py
"""Profil utilisateur"""

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Label, Static, Button
from textual.containers import Horizontal, Container

class ProfileScreen(Screen):
    """Écran de profil"""
    
    CSS = """
    ProfileScreen {
        background: $surface;
    }
    
    #profile-header {
        height: 3;
        border-bottom: solid $primary;
        padding: 0 1;
    }
    
    #profile-content {
        margin: 2;
        padding: 2;
        border: solid $secondary;
    }
    
    #profile-content > Label {
        padding: 1;
    }
    """
    
    def compose(self) -> ComposeResult:
        """Composition du profil"""
        with Horizontal(id="profile-header"):
            yield Label("👤 Profil")
        
        with Container(id="profile-content"):
            user = self.app.current_user or {}
            yield Label(f"📛 Nom: {user.get('username', 'Inconnu')}")
            yield Label(f"📧 Email: {user.get('email', 'Non renseigné')}")
            yield Label(f"📝 Bio: {user.get('bio', 'Non renseignée')}")
            yield Label(f"✅ Vérifié: {'Oui' if user.get('is_verified') else 'Non'}")
            yield Label(f"👥 Abonnés: {user.get('followers_count', 0)}")
            yield Label(f"📹 Vidéos: {user.get('videos_count', 0)}")
            
            yield Button("🔙 Retour", id="back-dashboard", variant="primary")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Clic sur un bouton"""
        if event.button.id == "back-dashboard":
            self.app.pop_screen()
