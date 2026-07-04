# screens/feed.py
"""Fil d'actualité"""

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Label, Static, Button, ListView, ListItem
from textual.containers import Horizontal, Container

class VideoItem(ListItem):
    """Élément vidéo dans le feed"""
    
    def __init__(self, video_data):
        super().__init__()
        self.video_data = video_data
    
    def render(self):
        data = self.video_data
        username = data.get('username', 'Inconnu')
        description = data.get('description', '')[:50]
        likes = data.get('likes', 0)
        views = data.get('views', 0)
        verified = "✅ " if data.get('is_verified') else ""
        
        return f"{verified}{username}\n  {description}\n  ❤️ {likes}  👁️ {views}"

class FeedScreen(Screen):
    """Fil d'actualité"""
    
    CSS = """
    FeedScreen {
        background: $surface;
    }
    
    #feed-header {
        height: 3;
        border-bottom: solid $primary;
        padding: 0 1;
    }
    
    #feed-container {
        height: 1fr;
        margin: 1;
        border: solid $secondary;
    }
    
    #feed-container ListItem {
        padding: 1;
        border-bottom: solid $panel;
    }
    
    #feed-actions {
        height: 3;
        padding: 0 1;
    }
    
    #feed-actions > Button {
        margin: 0 1;
        width: 15;
    }
    """
    
    def compose(self) -> ComposeResult:
        """Composition du feed"""
        with Horizontal(id="feed-header"):
            yield Label("📹 Fil d'actualité")
            yield Label("", id="feed-status")
        
        with Container(id="feed-container"):
            yield ListView(id="feed-list")
        
        with Horizontal(id="feed-actions"):
            yield Button("🔄 Rafraîchir", id="refresh-feed")
            yield Button("🔙 Retour", id="back-dashboard", variant="primary")
    
    def on_mount(self) -> None:
        """Chargement du feed au montage"""
        self.load_feed()
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Clic sur un bouton"""
        if event.button.id == "refresh-feed":
            self.load_feed()
        elif event.button.id == "back-dashboard":
            self.app.pop_screen()
    
    def load_feed(self) -> None:
        """Charge le feed"""
        self.query_one("#feed-list").clear()
        self.query_one("#feed-status").update("🔄 Chargement...")
        
        try:
            videos = self.app.api.get_feed(self.app.auth.token, 20)
            if videos:
                list_view = self.query_one("#feed-list")
                for video in videos:
                    list_view.append(VideoItem(video))
                self.query_one("#feed-status").update(f"✅ {len(videos)} vidéos")
            else:
                self.query_one("#feed-status").update("❌ Aucune vidéo")
        except Exception as e:
            self.query_one("#feed-status").update(f"❌ Erreur: {e}")
