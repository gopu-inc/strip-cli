# screens/dashboard.py
"""Dashboard STRIP — hub central style 2026"""

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Label, Static, Button, Rule, ListItem, ListView
from textual.containers import Horizontal, Vertical, Container, Grid
from rich.text import Text
from rich.panel import Panel


class StatCard(Static):
    """Carte statistique animée"""

    def __init__(self, icon: str, value: str, label: str, **kwargs):
        super().__init__(**kwargs)
        self.icon = icon
        self._value = value
        self._label = label

    def on_mount(self) -> None:
        self._render()

    def _render(self) -> None:
        self.update(
            Text.assemble(
                (f"  {self.icon}\n", "bold"),
                (f"  {self._value}\n", "bold #e94560"),
                (f"  {self._label}", "#555577"),
            )
        )

    def set_value(self, value: str) -> None:
        self._value = value
        self._render()


class DashboardScreen(Screen):
    """Tableau de bord principal"""

    CSS = """
    DashboardScreen {
        background: $background;
    }

    #dash-header {
        height: 4;
        background: #13131f;
        border-bottom: solid #1e1e2e;
        padding: 0 2;
    }

    #welcome-line {
        color: #e0e0e0;
        text-style: bold;
        padding: 1 0 0 0;
        height: 2;
    }

    #user-meta {
        color: #555577;
        height: 2;
    }

    #dash-body {
        height: 1fr;
        overflow-y: auto;
        padding: 1 2;
    }

    #stats-grid {
        grid-size: 3 2;
        grid-gutter: 1 2;
        height: 14;
        margin-bottom: 1;
    }

    StatCard {
        background: #13131f;
        border: solid #1e1e2e;
        padding: 1;
        height: 6;
    }

    StatCard:hover {
        border: solid #e94560;
    }

    #stories-section {
        height: 7;
        margin-bottom: 1;
    }

    #stories-title {
        color: #4dabf7;
        text-style: bold;
        height: 2;
    }

    #stories-row {
        height: 5;
        overflow-x: auto;
    }

    .story-circle {
        background: #1e1e2e;
        border: solid #e94560;
        width: 12;
        height: 5;
        padding: 1;
        margin: 0 1 0 0;
        text-align: center;
    }

    #quick-nav {
        height: 5;
        margin-bottom: 1;
    }

    #quick-nav Button {
        height: 3;
        width: 1fr;
        margin: 0 1 0 0;
    }

    #activity-section {
        height: auto;
        min-height: 10;
    }

    #activity-title {
        color: #4dabf7;
        text-style: bold;
        height: 2;
    }

    #notif-list {
        height: auto;
        max-height: 15;
    }

    #notif-list ListItem {
        padding: 0 1;
        border: none;
        border-bottom: solid #1e1e2e;
        background: transparent;
        margin: 0;
        height: 3;
    }

    #notif-list ListItem:hover {
        background: #13131f;
        border-bottom: solid #e94560;
    }

    #dash-nav {
        dock: bottom;
        height: 3;
        background: #0d0d18;
        border-top: solid #1e1e2e;
    }

    #dash-nav Button {
        width: 1fr;
        height: 3;
        background: transparent;
        color: #555577;
        border: none;
        margin: 0;
        padding: 0;
    }

    #dash-nav Button:hover {
        color: #e0e0e0;
        background: #1e1e2e;
    }
    """

    def compose(self) -> ComposeResult:
        user = self.app.current_user or {}
        username = user.get("username", "Utilisateur")
        verified = " ✅" if user.get("is_verified") else ""
        zodiac = f" {user.get('zodiac_sign', '')}" if user.get("zodiac_sign") else ""
        followers = user.get("followers_count", 0)
        videos = user.get("videos_count", 0)

        # Header
        with Horizontal(id="dash-header"):
            with Vertical():
                yield Static(
                    f"🐬  Bienvenue, @{username}{verified}{zodiac}",
                    id="welcome-line",
                )
                yield Static(
                    f"👥 {followers:,} abonnés  •  🎬 {videos} vidéos  •  🔑 STRIP v2.0",
                    id="user-meta",
                )

        with Container(id="dash-body"):
            # Stats grid
            with Grid(id="stats-grid"):
                yield StatCard("👥", "...", "Utilisateurs", id="stat-users")
                yield StatCard("🎬", "...", "Vidéos", id="stat-videos")
                yield StatCard("🔴", "...", "Lives actifs", id="stat-lives")
                yield StatCard("✅", "...", "Vérifiés", id="stat-verified")
                yield StatCard("💬", "...", "Messages", id="stat-messages")
                yield StatCard("🌐", "...", "En ligne", id="stat-online")

            # Stories
            with Container(id="stories-section"):
                yield Label("📸  Stories", id="stories-title")
                with Horizontal(id="stories-row"):
                    yield Static("➕\n\nNouvelle", classes="story-circle")
                    for i in range(6):
                        yield Static(
                            f"🐬\n\nUser {i+1}", classes="story-circle", id=f"story-{i}"
                        )

            # Navigation rapide
            with Horizontal(id="quick-nav"):
                yield Button("📹  Feed", id="btn-feed", variant="primary")
                yield Button("💬  Chat", id="btn-chat")
                yield Button("🎵  Sons", id="btn-sounds")
                yield Button("📄  Posts", id="btn-actfiles")
                yield Button("🔴  Lives", id="btn-live")

            Rule()

            # Activité / Notifications
            with Container(id="activity-section"):
                yield Label("🔔  Activité récente", id="activity-title")
                yield ListView(id="notif-list")

        # Barre de nav bottom
        with Horizontal(id="dash-nav"):
            yield Button("🏠\nHome", id="nav-home")
            yield Button("🔍\nExplore", id="nav-explore")
            yield Button("🔔\nNotifs", id="nav-notifs")
            yield Button("👤\nProfil", id="nav-profile")
            yield Button("⚙️\nParamètres", id="nav-settings")

    def on_mount(self) -> None:
        self.load_stats()
        self.load_stories()
        self.load_notifications()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        nav = {
            "btn-feed": "feed",
            "btn-chat": "chat",
            "btn-sounds": "sounds",
            "btn-actfiles": "actfiles",
            "btn-live": "live",
            "nav-home": None,  # already home
            "nav-explore": "explore",
            "nav-notifs": "notifications",
            "nav-profile": "profile",
            "nav-settings": "settings",
        }
        screen = nav.get(event.button.id)
        if screen:
            self.app.push_screen(screen)

    def load_stats(self) -> None:
        try:
            stats = self.app.api.get_stats(self.app.auth.token)
            if stats:
                mapping = {
                    "stat-users": (stats.get("total_users", 0), "Utilisateurs"),
                    "stat-videos": (stats.get("total_videos", 0), "Vidéos"),
                    "stat-lives": (stats.get("active_lives", 0), "Lives actifs"),
                    "stat-verified": (stats.get("verified_users", 0), "Vérifiés"),
                    "stat-messages": (stats.get("total_messages", 0), "Messages"),
                    "stat-online": (stats.get("online_users", 0), "En ligne"),
                }
                for widget_id, (value, _) in mapping.items():
                    try:
                        card = self.query_one(f"#{widget_id}", StatCard)
                        card.set_value(f"{int(value):,}")
                    except Exception:
                        pass
        except Exception:
            pass

    def load_stories(self) -> None:
        try:
            stories = self.app.api.get_stories() or []
            row = self.query_one("#stories-row")
            # Update the existing placeholders with real data
            for i, story in enumerate(stories[:6]):
                try:
                    card = self.query_one(f"#story-{i}", Static)
                    user = story.get("user", {})
                    uname = user.get("username", "")[:8]
                    card.update(f"🐬\n\n{uname}")
                except Exception:
                    pass
        except Exception:
            pass

    def load_notifications(self) -> None:
        try:
            notifs = self.app.api.get_notifications(self.app.auth.token, limit=10) or []
            lv = self.query_one("#notif-list")
            lv.clear()
            if not notifs:
                lv.append(ListItem(Static("  📭  Aucune notification récente", classes="muted")))
                return
            type_icons = {
                "like": "❤️",
                "follow": "👥",
                "message": "💬",
                "sound_like": "🎵",
                "actfile_like": "📄",
                "live": "🔴",
            }
            for n in notifs[:8]:
                icon = type_icons.get(n.get("type", ""), "🔔")
                msg = n.get("message", "")[:60]
                read = "" if n.get("read") else "● "
                lv.append(ListItem(Static(f"  {read}{icon}  {msg}")))
        except Exception:
            pass
