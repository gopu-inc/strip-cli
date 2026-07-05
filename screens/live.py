# screens/live.py
"""Lives — STRIP TUI 2026"""

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Label, Static, Button, ListView, ListItem, Input
from textual.containers import Horizontal, Vertical, Container
from textual import events
from rich.text import Text


def fmt_count(n: int) -> str:
    if n >= 1_000:
        return f"{n/1_000:.1f}K"
    return str(n)


class LiveCard(ListItem):
    """Carte live dans la liste"""

    def __init__(self, live: dict):
        super().__init__()
        self.live = live

    def render(self) -> Text:
        lv = self.live
        streamer = lv.get("username", "?")
        title = lv.get("title", "Sans titre")[:50]
        viewers = fmt_count(lv.get("viewer_count", 0))
        is_live = lv.get("is_live", False)
        private = " 🔒" if lv.get("is_private") else ""
        verified = " ✅" if lv.get("is_verified") else ""
        dot = "🔴" if is_live else "⚫"

        t = Text()
        t.append(f"  {dot}  ", style="bold")
        t.append(f"@{streamer}", style="bold #e94560")
        t.append(f"{verified}{private}\n", style="#4dabf7")
        t.append(f"  {title}\n", style="#e0e0e0")
        t.append(f"  👥 {viewers} spectateurs", style="dim")
        return t


class LiveScreen(Screen):
    """Écran des lives — voir + démarrer"""

    CSS = """
    LiveScreen {
        background: $background;
    }

    #live-header {
        height: 3;
        background: #13131f;
        border-bottom: solid #1e1e2e;
        padding: 0 2;
    }

    #live-title {
        color: #e94560;
        text-style: bold;
        width: 1fr;
    }

    #live-status {
        color: #555577;
        text-align: right;
        width: 25;
    }

    #live-body {
        height: 1fr;
    }

    /* Liste des lives */
    #lives-panel {
        width: 1fr;
        background: #0a0a0f;
    }

    #lives-list {
        height: 1fr;
        overflow-y: auto;
        padding: 1 2;
    }

    LiveCard {
        background: #13131f;
        border: solid #1e1e2e;
        margin-bottom: 1;
        padding: 1;
        height: 7;
    }

    LiveCard:hover {
        border: solid #e94560;
    }

    /* Mon live */
    #my-live-panel {
        width: 40;
        background: #0d0d18;
        border-left: solid #1e1e2e;
        padding: 2;
    }

    #my-live-title {
        color: #e94560;
        text-style: bold;
        height: 2;
    }

    #my-live-status {
        color: #555577;
        height: 3;
    }

    #stream-info-box {
        background: #13131f;
        border: solid #1e1e2e;
        padding: 1;
        margin: 1 0;
        height: auto;
    }

    #stream-key-label {
        color: #888;
        height: 2;
    }

    #live-title-input {
        margin: 1 0;
    }

    #live-actions-box Button {
        width: 100%;
        margin-bottom: 1;
        height: 3;
    }

    #live-bottom {
        height: 3;
        background: #13131f;
        border-top: solid #1e1e2e;
        padding: 0 2;
    }

    #live-bottom Button {
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
        ("r", "reload", "Rafraîchir"),
    ]

    def __init__(self):
        super().__init__()
        self._live_id = None
        self._is_live = False

    def compose(self) -> ComposeResult:
        with Horizontal(id="live-header"):
            yield Label("🔴  Lives", id="live-title")
            yield Label("", id="live-status")

        with Horizontal(id="live-body"):
            # Liste des lives actifs
            with Vertical(id="lives-panel"):
                yield ListView(id="lives-list")

            # Mon live panel
            with Vertical(id="my-live-panel"):
                yield Label("🎙  Mon Live", id="my-live-title")
                yield Label("Statut: ⚫  Hors ligne", id="my-live-status")

                with Container(id="stream-info-box"):
                    yield Label("📡  Infos de stream", classes="section-title")
                    yield Label("", id="stream-key-label")

                yield Input(placeholder="📝  Titre du live...", id="live-title-input")

                with Container(id="live-actions-box"):
                    yield Button("🔴  Démarrer le live", id="btn-start", variant="primary")
                    yield Button("⏹  Arrêter le live", id="btn-stop", variant="error")
                    yield Button("🔄  Rafraîchir", id="btn-refresh-my")

        with Horizontal(id="live-bottom"):
            yield Button("🔄 Rafraîchir liste", id="btn-refresh", variant="primary")
            yield Button("🔙 Retour", id="btn-back")

        yield Static(
            "  ↑↓  naviguer  •  R  rafraîchir  •  Esc  retour",
            id="hint-bar",
        )

    def on_mount(self) -> None:
        self.load_lives()
        self.query_one("#btn-stop", Button).disabled = True

    def action_back(self) -> None:
        self.app.pop_screen()

    def action_reload(self) -> None:
        self.load_lives()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        bid = event.button.id
        if bid == "btn-back":
            self.action_back()
        elif bid in ("btn-refresh", "btn-refresh-my"):
            self.load_lives()
        elif bid == "btn-start":
            self._start_live()
        elif bid == "btn-stop":
            self._stop_live()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        item = event.item
        if hasattr(item, "live"):
            lv = item.live
            title = lv.get("title", "?")
            viewers = lv.get("viewer_count", 0)
            self.query_one("#live-status").update(
                f"👁  {lv.get('username')} — {title} — {viewers} spectateurs"
            )

    def load_lives(self) -> None:
        lv = self.query_one("#lives-list", ListView)
        lv.clear()
        self.query_one("#live-status").update("🔄  Chargement...")
        try:
            lives = self.app.api.get_active_lives(self.app.auth.token) or []
            if lives:
                for live in lives:
                    lv.append(LiveCard(live))
                self.query_one("#live-status").update(
                    f"✅  {len(lives)} live{'s' if len(lives) > 1 else ''} actif{'s' if len(lives) > 1 else ''}"
                )
            else:
                lv.append(ListItem(Static("  📭  Aucun live en cours\n  Soyez le premier !")))
                self.query_one("#live-status").update("📭  Aucun live")
        except Exception:
            lv.append(ListItem(Static("  ❌  Impossible de charger les lives")))
            self.query_one("#live-status").update("❌  Erreur réseau")

    def _start_live(self) -> None:
        title = self.query_one("#live-title-input", Input).value.strip() or "Live STRIP"
        self.query_one("#live-status").update("🔄  Démarrage du live...")
        try:
            result = self.app.api.start_live(title, token=self.app.auth.token) or {}
            if result:
                self._live_id = result.get("id")
                stream_key = result.get("stream_key", "N/A")
                rtmp = result.get("rtmp_url", "")
                self._is_live = True
                self.query_one("#my-live-status").update("Statut: 🔴  En live !")
                self.query_one("#stream-key-label").update(
                    f"🔑  Clé: {stream_key[:30]}...\n📡  RTMP: {rtmp[:40]}"
                )
                self.query_one("#btn-start", Button).disabled = True
                self.query_one("#btn-stop", Button).disabled = False
                self.query_one("#live-status").update("✅  Live démarré !")
                self.load_lives()
            else:
                self.query_one("#live-status").update("❌  Échec du démarrage")
        except Exception:
            self.query_one("#live-status").update("❌  Erreur réseau")

    def _stop_live(self) -> None:
        if not self._live_id:
            self.query_one("#live-status").update("⚠️  Aucun live actif")
            return
        self.query_one("#live-status").update("🔄  Arrêt du live...")
        try:
            self.app.api.stop_live(self._live_id, self.app.auth.token)
            self._live_id = None
            self._is_live = False
            self.query_one("#my-live-status").update("Statut: ⚫  Hors ligne")
            self.query_one("#stream-key-label").update("")
            self.query_one("#btn-start", Button).disabled = False
            self.query_one("#btn-stop", Button).disabled = True
            self.query_one("#live-status").update("✅  Live arrêté")
            self.load_lives()
        except Exception:
            self.query_one("#live-status").update("❌  Erreur réseau")
