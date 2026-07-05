# screens/stories.py
"""Stories — STRIP TUI 2026"""

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Label, Static, Button, ListView, ListItem
from textual.containers import Horizontal, Vertical, Container
from textual import events
from rich.text import Text
from datetime import datetime


def _age(ts) -> str:
    """Returns a human-readable age like '2h' or '45m'."""
    try:
        if isinstance(ts, str):
            dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            from datetime import timezone
            now = datetime.now(timezone.utc)
            diff = now - dt
            total_seconds = int(diff.total_seconds())
            if total_seconds < 60:
                return f"{total_seconds}s"
            if total_seconds < 3600:
                return f"{total_seconds // 60}m"
            return f"{total_seconds // 3600}h"
    except Exception:
        pass
    return ""


class StoryBubble(Static):
    """Bulles de story style Instagram"""

    def __init__(self, story: dict, **kwargs):
        super().__init__(**kwargs)
        self.story = story

    def on_mount(self) -> None:
        s = self.story
        user = s.get("user", {})
        uname = (user.get("username") or "?")[:10]
        age = _age(s.get("created_at"))
        media_type = s.get("media_type", "image")
        icon = "🖼" if media_type == "image" else ("🎬" if media_type == "video" else "🎤")

        self.update(
            f"{icon}\n\n@{uname}\n{age} ago"
        )


class StoriesScreen(Screen):
    """Écran des Stories (24h)"""

    CSS = """
    StoriesScreen {
        background: $background;
    }

    #stories-header {
        height: 3;
        background: #13131f;
        border-bottom: solid #1e1e2e;
        padding: 0 2;
    }

    #stories-title {
        color: #e94560;
        text-style: bold;
        width: 1fr;
    }

    #stories-status {
        color: #555577;
        text-align: right;
        width: 20;
    }

    #stories-body {
        height: 1fr;
    }

    /* Story bubbles row */
    #bubbles-panel {
        height: 12;
        background: #0d0d18;
        border-bottom: solid #1e1e2e;
        overflow-x: auto;
        padding: 1 2;
    }

    StoryBubble {
        width: 14;
        height: 9;
        background: #1e1e2e;
        border: solid #e94560;
        text-align: center;
        margin-right: 1;
        padding: 1;
        color: #e0e0e0;
    }

    StoryBubble:hover {
        background: #2a2a3e;
    }

    #add-story-btn {
        width: 14;
        height: 9;
        background: #13131f;
        border: dashed #555577;
        text-align: center;
        margin-right: 1;
        color: #555577;
    }

    /* Story viewer */
    #story-viewer {
        height: 1fr;
        background: #0a0a0f;
        align: center middle;
        padding: 2;
    }

    #viewer-box {
        width: 60;
        height: 25;
        border: solid #e94560;
        background: #13131f;
        padding: 2;
        align: center middle;
    }

    #viewer-user {
        color: #e94560;
        text-style: bold;
        text-align: center;
        height: 2;
    }

    #viewer-age {
        color: #555577;
        text-align: center;
        height: 2;
    }

    #viewer-media {
        height: 10;
        text-align: center;
        align: center middle;
        color: #888;
        border: solid #2a2a3e;
        margin: 1 0;
    }

    #viewer-nav {
        height: 3;
        align: center middle;
    }

    #viewer-nav Button {
        width: 12;
        margin: 0 2;
    }

    #no-stories {
        align: center middle;
        color: #333355;
        text-align: center;
        height: 1fr;
    }

    #stories-bottom {
        height: 3;
        background: #13131f;
        border-top: solid #1e1e2e;
        padding: 0 2;
    }

    #stories-bottom Button {
        width: 20;
        margin: 0 1;
        height: 3;
    }
    """

    BINDINGS = [
        ("escape", "back", "Retour"),
        ("r", "reload", "Rafraîchir"),
        ("left", "prev_story", "Précédente"),
        ("right", "next_story", "Suivante"),
    ]

    def __init__(self):
        super().__init__()
        self._stories = []
        self._current_idx = 0

    def compose(self) -> ComposeResult:
        with Horizontal(id="stories-header"):
            yield Label("📸  Stories — 24h", id="stories-title")
            yield Label("", id="stories-status")

        with Container(id="stories-body"):
            # Bubbles row
            with Horizontal(id="bubbles-panel"):
                yield Static("➕\n\nAjouter\nune story", id="add-story-btn")

            # Story viewer
            with Container(id="story-viewer"):
                yield Static(
                    "📸\n\nSélectionnez une story\npour la voir",
                    id="no-stories",
                )
                with Container(id="viewer-box"):
                    yield Label("", id="viewer-user")
                    yield Label("", id="viewer-age")
                    with Container(id="viewer-media"):
                        yield Static("", id="viewer-content")
                    with Horizontal(id="viewer-nav"):
                        yield Button("◀  Préc.", id="btn-prev-story")
                        yield Button("Suiv.  ▶", id="btn-next-story")

        with Horizontal(id="stories-bottom"):
            yield Button("🔄 Rafraîchir", id="btn-refresh", variant="primary")
            yield Button("🔙 Retour", id="btn-back")

    def on_mount(self) -> None:
        # Hide viewer initially
        try:
            self.query_one("#viewer-box").styles.display = "none"
        except Exception:
            pass
        self.load_stories()

    def action_back(self) -> None:
        self.app.pop_screen()

    def action_reload(self) -> None:
        self.load_stories()

    def action_prev_story(self) -> None:
        if self._stories and self._current_idx > 0:
            self._current_idx -= 1
            self._show_story(self._current_idx)

    def action_next_story(self) -> None:
        if self._stories and self._current_idx < len(self._stories) - 1:
            self._current_idx += 1
            self._show_story(self._current_idx)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        bid = event.button.id
        if bid == "btn-back":
            self.action_back()
        elif bid == "btn-refresh":
            self.load_stories()
        elif bid == "btn-prev-story":
            self.action_prev_story()
        elif bid == "btn-next-story":
            self.action_next_story()

    def on_static_click(self, event) -> None:
        # When clicking a story bubble
        widget = event.widget
        if hasattr(widget, "story"):
            idx = self._stories.index(widget.story) if widget.story in self._stories else -1
            if idx >= 0:
                self._current_idx = idx
                self._show_story(idx)

    def _show_story(self, idx: int) -> None:
        if not self._stories:
            return
        story = self._stories[idx]
        user = story.get("user", {})
        uname = user.get("username", "?")
        media_type = story.get("media_type", "image")
        media_url = story.get("media_url", "")
        age = _age(story.get("created_at"))
        icon = "🖼️  Image" if media_type == "image" else ("🎬  Vidéo" if media_type == "video" else "🎤  Audio")

        try:
            self.query_one("#no-stories").styles.display = "none"
            self.query_one("#viewer-box").styles.display = "block"
            self.query_one("#viewer-user").update(f"@{uname}")
            self.query_one("#viewer-age").update(f"il y a {age}")
            self.query_one("#viewer-content").update(
                f"{icon}\n\n[Contenu disponible sur l'app web]\n{media_url[:50]}..."
            )
            self.query_one("#stories-status").update(
                f"{idx+1}/{len(self._stories)}"
            )
        except Exception:
            pass

    def load_stories(self) -> None:
        self.query_one("#stories-status").update("🔄  Chargement...")
        try:
            stories = self.app.api.get_stories() or []
            self._stories = stories

            # Rebuild bubbles
            panel = self.query_one("#bubbles-panel")
            # Remove old bubbles
            for child in list(panel.children):
                if isinstance(child, StoryBubble):
                    child.remove()

            if stories:
                for s in stories:
                    bubble = StoryBubble(s)
                    panel.mount(bubble)
                self.query_one("#stories-status").update(
                    f"✅  {len(stories)} stories"
                )
                # Auto-show first
                self._current_idx = 0
                self._show_story(0)
            else:
                self.query_one("#stories-status").update("📭  Aucune story")
                try:
                    self.query_one("#no-stories").styles.display = "block"
                    self.query_one("#viewer-box").styles.display = "none"
                except Exception:
                    pass
        except Exception:
            self.query_one("#stories-status").update("❌  Erreur réseau")
