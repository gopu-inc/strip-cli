# screens/sounds.py
"""STRIP Sounds — bibliothèque audio TUI 2026"""

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Label, Static, Button, ListView, ListItem, Input
from textual.containers import Horizontal, Vertical, Container
from textual import events
from rich.text import Text


CATEGORIES = ["Tous", "Afro", "Rap", "Gospel", "Amapiano", "Rumba", "Électro", "Podcast", "Autres"]


def fmt_count(n: int) -> str:
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n/1_000:.1f}K"
    return str(n)


class SoundCard(ListItem):
    """Carte son dans la liste"""

    def __init__(self, sound: dict):
        super().__init__()
        self.sound = sound
        self._liked = sound.get("liked", False)

    def render(self) -> Text:
        s = self.sound
        title = s.get("title", "?")[:40]
        author = s.get("author_username") or s.get("username", "?")
        category = s.get("category", "")
        plays = fmt_count(s.get("plays_count") or s.get("plays", 0))
        likes = fmt_count(s.get("likes_count") or s.get("likes", 0))
        uses = fmt_count(s.get("uses_count") or s.get("uses", 0))
        verified = " ✅" if (s.get("author_is_verified") or s.get("is_verified")) else ""
        liked = "❤️" if self._liked else "🤍"

        t = Text()
        t.append(f"  🎵  ", style="bold")
        t.append(f"{title}\n", style="bold #e0e0e0")
        t.append(f"  @{author}", style="#e94560")
        t.append(f"{verified}", style="#4dabf7")
        t.append(f"  [{category}]\n", style="#555577")
        t.append(f"  ▶ {plays}  {liked} {likes}  🔁 {uses}", style="dim")
        return t


class SoundsScreen(Screen):
    """STRIP Sounds — bibliothèque musicale"""

    CSS = """
    SoundsScreen {
        background: $background;
    }

    #sounds-header {
        height: 3;
        background: #13131f;
        border-bottom: solid #1e1e2e;
        padding: 0 2;
    }

    #sounds-title {
        color: #e94560;
        text-style: bold;
        width: 1fr;
    }

    #sounds-status {
        color: #555577;
        text-align: right;
        width: 25;
    }

    #cat-bar {
        height: 3;
        background: #0d0d18;
        border-bottom: solid #1e1e2e;
        overflow-x: auto;
    }

    #cat-bar Button {
        width: auto;
        height: 3;
        background: transparent;
        color: #555577;
        border: none;
        margin: 0;
        padding: 0 2;
    }

    #cat-bar Button.cat-active {
        color: #e94560;
        border-bottom: solid #e94560;
    }

    #search-row {
        height: 3;
        padding: 0 2;
        background: #0d0d18;
        border-bottom: solid #1e1e2e;
    }

    #sound-search {
        width: 1fr;
    }

    #sounds-list {
        height: 1fr;
        overflow-y: auto;
        padding: 1 2;
    }

    SoundCard {
        background: #13131f;
        border: solid #1e1e2e;
        margin-bottom: 1;
        padding: 1;
        height: 7;
    }

    SoundCard:hover {
        border: solid #e94560;
        background: #16161f;
    }

    SoundCard.--highlight {
        border: solid #e94560;
    }

    #player-bar {
        height: 4;
        background: #0d0d18;
        border-top: solid #e94560;
        padding: 0 2;
    }

    #player-info {
        width: 1fr;
        color: #e0e0e0;
        padding: 1 0;
    }

    #player-controls Button {
        width: 6;
        height: 3;
        margin: 0 1;
        background: #1e1e2e;
    }

    #sounds-bottom {
        height: 3;
        background: #13131f;
        border-top: solid #1e1e2e;
        padding: 0 2;
    }

    #sounds-bottom Button {
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
        ("l", "like_current", "Liker"),
        ("p", "play_current", "Écouter"),
        ("r", "reload", "Rafraîchir"),
    ]

    def __init__(self):
        super().__init__()
        self._sounds = []
        self._category = "Tous"
        self._playing_title = "Aucun son sélectionné"
        self._current_idx = 0

    def compose(self) -> ComposeResult:
        with Horizontal(id="sounds-header"):
            yield Label("🎵  STRIP Sounds", id="sounds-title")
            yield Label("", id="sounds-status")

        # Category bar
        with Horizontal(id="cat-bar"):
            for cat in CATEGORIES:
                cls = "cat-active" if cat == "Tous" else ""
                yield Button(
                    cat,
                    id=f"cat-{cat.lower().replace(' ', '_').replace('é', 'e')}",
                    classes=cls,
                )

        # Search
        with Horizontal(id="search-row"):
            yield Input(placeholder="🔍  Rechercher un son...", id="sound-search")

        yield ListView(id="sounds-list")

        # Mini player bar
        with Horizontal(id="player-bar"):
            with Container(id="player-info"):
                yield Static("▶  Aucun son sélectionné", id="player-now")
            with Horizontal(id="player-controls"):
                yield Button("⏮", id="btn-prev")
                yield Button("▶", id="btn-play")
                yield Button("⏭", id="btn-next")
                yield Button("🤍", id="btn-like-player")

        with Horizontal(id="sounds-bottom"):
            yield Button("🔄 Rafraîchir", id="btn-refresh", variant="primary")
            yield Button("🔙 Retour", id="btn-back")

        yield Static(
            "  ↑↓  naviguer  •  P  écouter  •  L  liker  •  Esc  retour",
            id="hint-bar",
        )

    def on_mount(self) -> None:
        self.load_sounds()
        self.query_one("#sound-search").focus()

    def action_back(self) -> None:
        self.app.pop_screen()

    def action_reload(self) -> None:
        self.load_sounds()

    def action_play_current(self) -> None:
        if self._sounds:
            s = self._sounds[self._current_idx]
            self._play_sound(s)

    def action_like_current(self) -> None:
        if self._sounds and self.app.auth.token:
            s = self._sounds[self._current_idx]
            self.app.api.like_sound(s.get("id", ""), self.app.auth.token)
            self.query_one("#sounds-status").update("❤️  Liké !")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        bid = event.button.id
        if bid == "btn-back":
            self.action_back()
        elif bid == "btn-refresh":
            self.load_sounds()
        elif bid == "btn-play":
            self.action_play_current()
        elif bid == "btn-prev":
            if self._current_idx > 0:
                self._current_idx -= 1
                self._play_sound(self._sounds[self._current_idx])
        elif bid == "btn-next":
            if self._current_idx < len(self._sounds) - 1:
                self._current_idx += 1
                self._play_sound(self._sounds[self._current_idx])
        elif bid == "btn-like-player":
            self.action_like_current()
        elif bid and bid.startswith("cat-"):
            # Category filter
            raw = bid[4:].replace("_", " ")
            for cat in CATEGORIES:
                if cat.lower().replace(" ", "_").replace("é", "e") == bid[4:]:
                    self._category = cat
                    break
            self._update_cat_buttons(bid)
            self.load_sounds()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "sound-search":
            self._search_sounds(event.input.value)

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        item = event.item
        if hasattr(item, "sound"):
            try:
                lv = self.query_one("#sounds-list", ListView)
                self._current_idx = lv.index or 0
            except Exception:
                pass
            self._play_sound(item.sound)

    def _update_cat_buttons(self, active_id: str) -> None:
        for cat in CATEGORIES:
            cat_id = f"cat-{cat.lower().replace(' ', '_').replace('é', 'e')}"
            try:
                btn = self.query_one(f"#{cat_id}", Button)
                if cat_id == active_id:
                    btn.add_class("cat-active")
                else:
                    btn.remove_class("cat-active")
            except Exception:
                pass

    def _play_sound(self, sound: dict) -> None:
        title = sound.get("title", "?")
        author = sound.get("author_username") or sound.get("username", "?")
        sound_id = sound.get("id", "")
        self.query_one("#player-now").update(f"▶  {title}  @{author}")
        self.query_one("#sounds-status").update(f"🎵  {title}")
        if sound_id:
            self.app.api.play_sound(sound_id)

    def _search_sounds(self, query: str) -> None:
        if not query or len(query) < 2:
            self.load_sounds()
            return
        lv = self.query_one("#sounds-list", ListView)
        lv.clear()
        self._sounds = []
        try:
            results = self.app.api.search(query, "sounds", self.app.auth.token) or {}
            sounds = results.get("results", [])
            if sounds:
                self._sounds = sounds
                for s in sounds:
                    lv.append(SoundCard(s))
                self.query_one("#sounds-status").update(f"🔍  {len(sounds)} résultats")
            else:
                lv.append(ListItem(Static("  ❌  Aucun son trouvé")))
        except Exception:
            self.query_one("#sounds-status").update("❌  Erreur")

    def load_sounds(self) -> None:
        lv = self.query_one("#sounds-list", ListView)
        lv.clear()
        self._sounds = []
        self.query_one("#sounds-status").update("🔄  Chargement...")
        try:
            if self._category == "Tous":
                sounds = self.app.api.get_recommended_sounds(self.app.auth.token, 30) or []
            else:
                sounds = self.app.api.get_sounds_by_category(
                    self._category, self.app.auth.token
                ) or []
            self._sounds = sounds
            if sounds:
                for s in sounds:
                    lv.append(SoundCard(s))
                self.query_one("#sounds-status").update(
                    f"✅  {len(sounds)} sons"
                )
            else:
                lv.append(ListItem(Static("  📭  Aucun son dans cette catégorie")))
                self.query_one("#sounds-status").update("📭  Vide")
        except Exception:
            self.query_one("#sounds-status").update("❌  Erreur réseau")
            lv.append(ListItem(Static("  ❌  Impossible de charger les sons")))
