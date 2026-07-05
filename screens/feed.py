# screens/feed.py
"""Feed TikTok-style — STRIP TUI 2026"""

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Label, Static, Button, ListView, ListItem, Rule
from textual.containers import Horizontal, Vertical, Container
from textual import events
from rich.text import Text


def fmt_count(n: int) -> str:
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n/1_000:.1f}K"
    return str(n)


class VideoCard(ListItem):
    """Carte vidéo pleine largeur style TikTok"""

    def __init__(self, video: dict, current_user_id: str = ""):
        super().__init__()
        self.video = video
        self.current_user_id = current_user_id
        self._liked = video.get("liked", False)

    def render(self) -> Text:
        v = self.video
        username = v.get("username", "?")
        verified = " ✅" if v.get("is_verified") else ""
        desc = (v.get("description") or "")[:80]
        likes = fmt_count(v.get("likes", 0))
        views = fmt_count(v.get("views", 0))
        liked_icon = "❤️ " if self._liked else "🤍 "
        duration = v.get("duration")
        dur_str = f" • ⏱ {int(duration)}s" if duration else ""

        t = Text()
        t.append(f"  @{username}", style="bold #e94560")
        t.append(f"{verified}", style="#4dabf7")
        t.append(f"  {dur_str}\n", style="#555577")
        t.append(f"  {desc}\n", style="#e0e0e0")
        t.append(f"\n  {liked_icon}{likes}  ", style="dim")
        t.append("👁  ", style="dim")
        t.append(f"{views}  ", style="dim")
        t.append("💬 Commenter  ", style="dim")
        t.append("📤 Partager", style="dim")
        return t


class FeedScreen(Screen):
    """Fil d'actualité style TikTok"""

    CSS = """
    FeedScreen {
        background: $background;
    }

    #feed-header {
        height: 3;
        background: #13131f;
        border-bottom: solid #1e1e2e;
        padding: 0 2;
    }

    #feed-title {
        color: #e94560;
        text-style: bold;
        width: 1fr;
    }

    #feed-status {
        color: #555577;
        text-align: right;
        width: 30;
    }

    #feed-tabs {
        height: 3;
        background: #0d0d18;
        border-bottom: solid #1e1e2e;
    }

    #feed-tabs Button {
        width: 1fr;
        height: 3;
        background: transparent;
        color: #555577;
        border: none;
        margin: 0;
    }

    #feed-tabs Button.tab-active {
        color: #e94560;
        border-bottom: solid #e94560;
    }

    #feed-list {
        height: 1fr;
        overflow-y: auto;
        padding: 1 2;
    }

    VideoCard {
        background: #13131f;
        border: solid #1e1e2e;
        margin-bottom: 1;
        padding: 1;
        height: 8;
    }

    VideoCard:hover {
        border: solid #e94560;
        background: #16161f;
    }

    VideoCard.--highlight {
        border: solid #e94560;
    }

    #feed-bottom {
        height: 3;
        background: #13131f;
        border-top: solid #1e1e2e;
        padding: 0 2;
    }

    #feed-bottom Button {
        width: 20;
        height: 3;
        margin: 0 1;
    }

    #hint-bar {
        color: #333355;
        text-align: center;
        height: 1;
        background: #0d0d18;
    }
    """

    BINDINGS = [
        ("j", "next_video", "Suivant"),
        ("k", "prev_video", "Précédent"),
        ("l", "like_current", "Liker"),
        ("r", "reload", "Rafraîchir"),
        ("escape", "back", "Retour"),
    ]

    def __init__(self):
        super().__init__()
        self._videos = []
        self._current_idx = 0
        self._tab = "for_you"  # for_you | following | trending

    def compose(self) -> ComposeResult:
        with Horizontal(id="feed-header"):
            yield Label("📹  Feed", id="feed-title")
            yield Label("", id="feed-status")

        with Horizontal(id="feed-tabs"):
            yield Button("✨ Pour Toi", id="tab-for-you", classes="tab-active")
            yield Button("👥 Abonnements", id="tab-following")
            yield Button("🔥 Tendances", id="tab-trending")

        yield ListView(id="feed-list")

        with Horizontal(id="feed-bottom"):
            yield Button("🔄 Rafraîchir", id="btn-refresh", variant="primary")
            yield Button("📤 Upload", id="btn-upload")
            yield Button("🔙 Retour", id="btn-back")

        yield Static(
            "  ↑↓ / j·k  naviguer  •  L  liker  •  R  rafraîchir  •  Esc  retour",
            id="hint-bar",
        )

    def on_mount(self) -> None:
        self.load_feed()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        bid = event.button.id
        if bid == "btn-refresh":
            self.action_reload()
        elif bid == "btn-back":
            self.action_back()
        elif bid == "btn-upload":
            pass  # TODO: upload screen
        elif bid == "tab-for-you":
            self._tab = "for_you"
            self._set_tab("tab-for-you")
            self.load_feed()
        elif bid == "tab-following":
            self._tab = "following"
            self._set_tab("tab-following")
            self.load_feed()
        elif bid == "tab-trending":
            self._tab = "trending"
            self._set_tab("tab-trending")
            self.load_feed()

    def _set_tab(self, active_id: str) -> None:
        for tid in ["tab-for-you", "tab-following", "tab-trending"]:
            try:
                btn = self.query_one(f"#{tid}", Button)
                if tid == active_id:
                    btn.add_class("tab-active")
                else:
                    btn.remove_class("tab-active")
            except Exception:
                pass

    def action_reload(self) -> None:
        self.load_feed()

    def action_back(self) -> None:
        self.app.pop_screen()

    def action_next_video(self) -> None:
        lv = self.query_one("#feed-list", ListView)
        if self._current_idx < len(self._videos) - 1:
            self._current_idx += 1
            lv.index = self._current_idx

    def action_prev_video(self) -> None:
        lv = self.query_one("#feed-list", ListView)
        if self._current_idx > 0:
            self._current_idx -= 1
            lv.index = self._current_idx

    def action_like_current(self) -> None:
        if not self._videos:
            return
        v = self._videos[self._current_idx]
        vid_id = v.get("id")
        if not vid_id or not self.app.auth.token:
            return
        result = self.app.api.like_video(vid_id, self.app.auth.token)
        if result is not None:
            liked = result.get("liked", not v.get("liked"))
            self._videos[self._current_idx]["liked"] = liked
            self._refresh_card(self._current_idx, liked)

    def _refresh_card(self, idx: int, liked: bool) -> None:
        try:
            lv = self.query_one("#feed-list", ListView)
            # Rebuild the list
            self.load_feed()
        except Exception:
            pass

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        try:
            lv = self.query_one("#feed-list", ListView)
            idx = lv.index
            if idx is not None:
                self._current_idx = idx
                v = self._videos[idx]
                vid_id = v.get("id")
                if vid_id:
                    self.app.api.increment_view(vid_id)
        except Exception:
            pass

    def load_feed(self) -> None:
        lv = self.query_one("#feed-list", ListView)
        lv.clear()
        self._videos = []
        self.query_one("#feed-status").update("🔄  Chargement...")

        try:
            videos = self.app.api.get_feed(self.app.auth.token, limit=20) or []
            self._videos = videos
            uid = self.app.auth.get_user_id() or ""

            if videos:
                for v in videos:
                    lv.append(VideoCard(v, uid))
                self.query_one("#feed-status").update(
                    f"✅  {len(videos)} vidéos"
                )
            else:
                lv.append(ListItem(Static("  📭  Aucune vidéo pour l'instant")))
                self.query_one("#feed-status").update("📭  Vide")
        except Exception as e:
            self.query_one("#feed-status").update(f"❌  Erreur")
            lv.append(ListItem(Static(f"  ❌  Impossible de charger le feed\n  {e}")))
