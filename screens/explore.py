# screens/explore.py
"""Explore & Search — STRIP TUI 2026"""

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Label, Static, Button, ListView, ListItem, Input
from textual.containers import Horizontal, Vertical, Container
from textual import events
from rich.text import Text


def fmt_count(n: int) -> str:
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n/1_000:.1f}K"
    return str(n)


class UserResult(ListItem):
    def __init__(self, user: dict):
        super().__init__()
        self.user = user

    def render(self) -> Text:
        u = self.user
        verified = " ✅" if u.get("is_verified") else ""
        zodiac = f"  {u.get('zodiac_sign', '')}" if u.get("zodiac_sign") else ""
        bio = (u.get("bio") or "")[:60]
        t = Text()
        t.append(f"  👤  @{u.get('username', '?')}", style="bold #e94560")
        t.append(f"{verified}{zodiac}\n", style="#4dabf7")
        if bio:
            t.append(f"  {bio}", style="#888")
        return t


class VideoResult(ListItem):
    def __init__(self, video: dict):
        super().__init__()
        self.video = video

    def render(self) -> Text:
        v = self.video
        desc = (v.get("description") or "")[:70]
        likes = fmt_count(v.get("likes_count") or v.get("likes", 0))
        verified = " ✅" if v.get("is_verified") else ""
        t = Text()
        t.append(f"  🎬  @{v.get('username', '?')}", style="bold #e94560")
        t.append(f"{verified}\n", style="#4dabf7")
        t.append(f"  {desc}\n", style="#c8c8c8")
        t.append(f"  ❤️ {likes}", style="dim")
        return t


class SoundResult(ListItem):
    def __init__(self, sound: dict):
        super().__init__()
        self.sound = sound

    def render(self) -> Text:
        s = self.sound
        plays = fmt_count(s.get("plays_count") or s.get("plays", 0))
        cat = s.get("category", "")
        verified = " ✅" if s.get("is_verified") else ""
        t = Text()
        t.append(f"  🎵  {s.get('title', '?')}", style="bold #e0e0e0")
        t.append(f"  [{cat}]\n", style="#555577")
        t.append(f"  @{s.get('username', '?')}", style="#e94560")
        t.append(f"{verified}  ", style="#4dabf7")
        t.append(f"▶ {plays}", style="dim")
        return t


class ExploreScreen(Screen):
    """Écran de recherche/explore"""

    CSS = """
    ExploreScreen {
        background: $background;
    }

    #exp-header {
        height: 3;
        background: #13131f;
        border-bottom: solid #1e1e2e;
        padding: 0 2;
    }

    #exp-title {
        color: #e94560;
        text-style: bold;
        width: 1fr;
    }

    #exp-status {
        color: #555577;
        text-align: right;
        width: 25;
    }

    #search-row {
        height: 3;
        background: #0d0d18;
        border-bottom: solid #1e1e2e;
        padding: 0 2;
    }

    #exp-search {
        width: 1fr;
        margin-right: 1;
    }

    #btn-go {
        width: 12;
    }

    #type-bar {
        height: 3;
        background: #0d0d18;
        border-bottom: solid #1e1e2e;
    }

    #type-bar Button {
        width: 1fr;
        height: 3;
        background: transparent;
        color: #555577;
        border: none;
        margin: 0;
    }

    #type-bar Button.type-active {
        color: #e94560;
        border-bottom: solid #e94560;
    }

    #results-area {
        height: 1fr;
    }

    #results-panel {
        width: 1fr;
        height: 1fr;
        overflow-y: auto;
        padding: 1 2;
    }

    #trending-panel {
        width: 25;
        background: #0d0d18;
        border-left: solid #1e1e2e;
        padding: 1;
    }

    #trending-title {
        color: #4dabf7;
        text-style: bold;
        height: 2;
    }

    #trending-list {
        height: 1fr;
    }

    #trending-list ListItem {
        height: 3;
        border: none;
        border-bottom: solid #1e1e2e;
        background: transparent;
        padding: 0 1;
        margin: 0;
    }

    UserResult, VideoResult, SoundResult {
        background: #13131f;
        border: solid #1e1e2e;
        margin-bottom: 1;
        padding: 1;
        height: 6;
    }

    UserResult:hover, VideoResult:hover, SoundResult:hover {
        border: solid #e94560;
    }

    #exp-bottom {
        height: 3;
        background: #13131f;
        border-top: solid #1e1e2e;
        padding: 0 2;
    }

    #exp-bottom Button {
        width: 20;
        margin: 0 1;
        height: 3;
    }

    #hint-bar {
        color: #222244;
        text-align: center;
        height: 1;
        background: #0d0d18;
    }
    """

    BINDINGS = [
        ("escape", "back", "Retour"),
    ]

    def __init__(self):
        super().__init__()
        self._type = "users"

    def compose(self) -> ComposeResult:
        with Horizontal(id="exp-header"):
            yield Label("🔍  Explorer", id="exp-title")
            yield Label("", id="exp-status")

        with Horizontal(id="search-row"):
            yield Input(
                placeholder="Rechercher des utilisateurs, vidéos, sons...",
                id="exp-search",
            )
            yield Button("🔍 Go", id="btn-go", variant="primary")

        with Horizontal(id="type-bar"):
            yield Button("👥 Utilisateurs", id="type-users", classes="type-active")
            yield Button("🎬 Vidéos", id="type-videos")
            yield Button("🎵 Sons", id="type-sounds")

        with Horizontal(id="results-area"):
            with Vertical(id="results-panel"):
                yield ListView(id="results-list")

            with Vertical(id="trending-panel"):
                yield Label("🔥  Tendances", id="trending-title")
                yield ListView(id="trending-list")

        with Horizontal(id="exp-bottom"):
            yield Button("🔙 Retour", id="btn-back")

        yield Static(
            "  Tapez votre recherche et appuyez sur Entrée",
            id="hint-bar",
        )

    def on_mount(self) -> None:
        self._load_trending()
        self.query_one("#exp-search").focus()

    def action_back(self) -> None:
        self.app.pop_screen()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "exp-search":
            self._do_search(event.input.value)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        bid = event.button.id
        if bid == "btn-back":
            self.action_back()
        elif bid == "btn-go":
            q = self.query_one("#exp-search", Input).value
            self._do_search(q)
        elif bid == "type-users":
            self._type = "users"
            self._update_type_btns("type-users")
        elif bid == "type-videos":
            self._type = "videos"
            self._update_type_btns("type-videos")
        elif bid == "type-sounds":
            self._type = "sounds"
            self._update_type_btns("type-sounds")

    def _update_type_btns(self, active: str) -> None:
        for tid in ["type-users", "type-videos", "type-sounds"]:
            try:
                btn = self.query_one(f"#{tid}", Button)
                if tid == active:
                    btn.add_class("type-active")
                else:
                    btn.remove_class("type-active")
            except Exception:
                pass
        # Re-run search with new type if query exists
        q = self.query_one("#exp-search", Input).value
        if q and len(q) >= 2:
            self._do_search(q)

    def _do_search(self, query: str) -> None:
        if not query or len(query) < 2:
            self.query_one("#exp-status").update("⚠️  Min 2 caractères")
            return
        lv = self.query_one("#results-list", ListView)
        lv.clear()
        self.query_one("#exp-status").update(f"🔍  Recherche: {query}")
        try:
            results = self.app.api.search(query, self._type, self.app.auth.token) or {}
            items = results.get("results", [])
            if items:
                for item in items:
                    if self._type == "users":
                        lv.append(UserResult(item))
                    elif self._type == "videos":
                        lv.append(VideoResult(item))
                    elif self._type == "sounds":
                        lv.append(SoundResult(item))
                self.query_one("#exp-status").update(f"✅  {len(items)} résultats")
            else:
                lv.append(ListItem(Static(f"  ❌  Aucun résultat pour «{query}»")))
                self.query_one("#exp-status").update("📭  Rien trouvé")
        except Exception:
            self.query_one("#exp-status").update("❌  Erreur réseau")

    def _load_trending(self) -> None:
        try:
            lv = self.query_one("#trending-list", ListView)
            lv.clear()
            # Use general search to get trending users
            data = self.app.api.get(
                "/api/search?q=a&type=users&limit=8", self.app.auth.token
            ) or {}
            users = data.get("results", [])
            for u in users[:8]:
                uname = u.get("username", "?")[:12]
                lv.append(
                    ListItem(Static(f"  🔥  @{uname}"))
                )
        except Exception:
            pass
