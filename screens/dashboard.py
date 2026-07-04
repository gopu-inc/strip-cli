# screens/dashboard.py
"""Tableau de bord"""

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Label, Static, Button
from textual.containers import Horizontal, Grid, Container

class DashboardScreen(Screen):
    """Tableau de bord principal"""
    
    CSS = """
    DashboardScreen {
        background: $surface;
    }
    
    #stats-grid {
        grid-size: 3 2;
        grid-gutter: 1 1;
        margin: 1 1;
        height: 10;
    }
    
    #stats-grid > Static {
        border: solid $primary;
        padding: 1;
        background: $panel;
        text-align: center;
    }
    
    #recent-activity {
        margin: 1 1;
        height: 1fr;
        border: solid $secondary;
        padding: 1;
    }
    
    #quick-actions {
        height: 5;
        margin: 1 1;
    }
    
    #quick-actions > Button {
        margin: 0 1;
        width: 20;
    }
    
    .welcome {
        text-align: center;
        padding: 1 0;
    }
    """
    
    def compose(self) -> ComposeResult:
        """Composition du tableau de bord"""
        username = self.app.current_user.get("username", "Utilisateur") if self.app.current_user else "Utilisateur"
        yield Static(f"🐬 Bienvenue {username} !", classes="welcome")
        
        with Grid(id="stats-grid"):
            yield Static("👥 ...\nUtilisateurs")
            yield Static("🎬 ...\nVidéos")
            yield Static("🔴 ...\nLives")
            yield Static("✅ ...\nVérifiés")
            yield Static("💬 ...\nMessages")
            yield Static("🚨 ...\nSignalements")
        
        with Horizontal(id="quick-actions"):
            yield Button("📹 Feed", id="action-feed", variant="primary")
            yield Button("💬 Chat", id="action-chat", variant="success")
            yield Button("🔴 Live", id="action-live", variant="warning")
            yield Button("👤 Profil", id="action-profile", variant="primary")
            yield Button("⚙️ Paramètres", id="action-settings")
        
        with Container(id="recent-activity"):
            yield Static("📋 Activité récente", classes="subtitle")
            yield Static("Chargement...", id="activity-content")
    
    def on_mount(self) -> None:
        """Chargement des données au montage"""
        self.load_stats()
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Clic sur un bouton"""
        button_id = event.button.id
        if button_id == "action-feed":
            self.app.push_screen("feed")
        elif button_id == "action-chat":
            self.app.push_screen("chat")
        elif button_id == "action-live":
            self.app.push_screen("live")
        elif button_id == "action-profile":
            self.app.push_screen("profile")
        elif button_id == "action-settings":
            self.app.push_screen("settings")
    
    def load_stats(self) -> None:
        """Charge les statistiques"""
        try:
            stats = self.app.api.get("/api/stats", token=self.app.auth.token)
            if stats:
                cards = self.query("#stats-grid > Static")
                data = [
                    f"👥 {stats.get('total_users', 0)}\nUtilisateurs",
                    f"🎬 {stats.get('total_videos', 0)}\nVidéos",
                    f"🔴 {stats.get('active_lives', 0)}\nLives",
                    f"✅ {stats.get('verified_users', 0)}\nVérifiés",
                    f"💬 {stats.get('total_messages', 0)}\nMessages",
                    f"🚨 {stats.get('pending_reports', 0)}\nSignalements"
                ]
                for i, card in enumerate(cards):
                    if i < len(data):
                        card.update(data[i])
        except Exception as e:
            self.query_one("#activity-content").update(f"❌ Erreur: {e}")
