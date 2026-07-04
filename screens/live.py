# screens/live.py
"""Lives"""

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Label, Static, Button, ListView, ListItem
from textual.containers import Horizontal, Container

class LiveScreen(Screen):
    """Écran des lives"""
    
    CSS = """
    LiveScreen {
        background: $surface;
    }
    
    #live-header {
        height: 3;
        border-bottom: solid $primary;
        padding: 0 1;
    }
    
    #live-container {
        height: 1fr;
        margin: 1;
        border: solid $secondary;
    }
    
    #live-container ListItem {
        padding: 1;
        border-bottom: solid $panel;
    }
    
    #live-actions {
        height: 3;
        padding: 0 1;
    }
    
    #live-actions > Button {
        margin: 0 1;
        width: 15;
    }
    """
    
    def compose(self) -> ComposeResult:
        """Composition de l'écran live"""
        with Horizontal(id="live-header"):
            yield Label("🔴 Lives")
            yield Label("", id="live-status")
        
        with Container(id="live-container"):
            yield ListView(id="lives-list")
        
        with Horizontal(id="live-actions"):
            yield Button("🔴 Démarrer", id="start-live", variant="error")
            yield Button("⏹ Arrêter", id="stop-live", variant="warning")
            yield Button("🔄 Rafraîchir", id="refresh-live")
            yield Button("🔙 Retour", id="back-dashboard", variant="primary")
    
    def on_mount(self) -> None:
        """Chargement des lives au montage"""
        self.load_lives()
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Clic sur un bouton"""
        if event.button.id == "refresh-live":
            self.load_lives()
        elif event.button.id == "start-live":
            self.start_live()
        elif event.button.id == "stop-live":
            self.stop_live()
        elif event.button.id == "back-dashboard":
            self.app.pop_screen()
    
    def load_lives(self) -> None:
        """Charge les lives actifs"""
        self.query_one("#lives-list").clear()
        self.query_one("#live-status").update("🔄 Chargement...")
        
        try:
            lives = self.app.api.get_active_lives(self.app.auth.token)
            if lives:
                list_view = self.query_one("#lives-list")
                for live in lives:
                    status = "🔴" if live.get('is_live') else "⏹"
                    item = Static(f"{status} {live.get('username')}: {live.get('title', 'Sans titre')} - 👥 {live.get('viewer_count', 0)}")
                    list_view.append(ListItem(item))
                self.query_one("#live-status").update(f"✅ {len(lives)} lives")
            else:
                self.query_one("#live-status").update("❌ Aucun live actif")
        except Exception as e:
            self.query_one("#live-status").update(f"❌ Erreur: {e}")
    
    def start_live(self) -> None:
        """Démarre un live"""
        self.query_one("#live-status").update("🔄 Démarrage...")
        try:
            result = self.app.api.post("/api/lives/start", 
                                      data={"title": "Live STRIP", "description": "", "is_private": False},
                                      token=self.app.auth.token)
            if result:
                self.query_one("#live-status").update("✅ Live démarré !")
                self.load_lives()
            else:
                self.query_one("#live-status").update("❌ Échec du démarrage")
        except Exception as e:
            self.query_one("#live-status").update(f"❌ Erreur: {e}")
    
    def stop_live(self) -> None:
        """Arrête un live"""
        self.query_one("#live-status").update("🔄 Arrêt...")
        self.query_one("#live-status").update("✅ Live arrêté")
