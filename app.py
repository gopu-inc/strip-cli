# app.py
"""STRIP TUI — Application principale v2.0 — 2026"""

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer
from textual.containers import Container

from screens import (
    LoginScreen,
    DashboardScreen,
    FeedScreen,
    ChatScreen,
    ProfileScreen,
    LiveScreen,
    SettingsScreen,
    SoundsScreen,
    ActFilesScreen,
    ExploreScreen,
    NotificationsScreen,
    StoriesScreen,
)

from api import APIClient
from auth import Auth
from config import Config


class StripApp(App):
    """Application STRIP TUI v2.0"""

    TITLE = "STRIP — Plateforme de streaming terminal"
    SUB_TITLE = "v2.0 · 2026"
    CSS_PATH = "styles/app.tcss"

    BINDINGS = [
        ("ctrl+q", "quit", "Quitter"),
        ("ctrl+l", "action_logout", "Déconnexion"),
        ("ctrl+d", "go_dashboard", "Dashboard"),
        ("ctrl+f", "go_feed", "Feed"),
        ("ctrl+g", "go_chat", "Chat"),
        ("ctrl+m", "go_sounds", "Sounds"),
        ("ctrl+p", "go_profile", "Profil"),
        ("ctrl+v", "go_live", "Lives"),
        ("ctrl+e", "go_explore", "Explorer"),
        ("ctrl+n", "go_notifications", "Notifs"),
        ("ctrl+t", "go_stories", "Stories"),
        ("ctrl+comma", "go_settings", "Paramètres"),
    ]

    SCREENS = {
        "login":         LoginScreen,
        "dashboard":     DashboardScreen,
        "feed":          FeedScreen,
        "chat":          ChatScreen,
        "profile":       ProfileScreen,
        "live":          LiveScreen,
        "settings":      SettingsScreen,
        "sounds":        SoundsScreen,
        "actfiles":      ActFilesScreen,
        "explore":       ExploreScreen,
        "notifications": NotificationsScreen,
        "stories":       StoriesScreen,
    }

    def __init__(self):
        super().__init__()
        self.config = Config()
        self.auth = Auth()
        self.api = APIClient()
        self.current_user = None

    def on_mount(self) -> None:
        """Démarrage — applique le thème sauvegardé et route vers le bon écran"""
        # Apply saved theme
        saved_theme = self.config.get("theme", "dark")
        if saved_theme and saved_theme != "dark":
            self.add_class(f"theme-{saved_theme}")

        # Route vers login ou dashboard
        if self.auth.is_authenticated():
            # Try to refresh user data
            try:
                profile = self.api.get_my_profile(self.auth.token)
                if profile:
                    self.current_user = profile
                    self.auth.user_data = profile
                else:
                    self.current_user = self.auth.user_data
            except Exception:
                self.current_user = self.auth.user_data
            self.push_screen("dashboard")
        else:
            self.push_screen("login")

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Footer()

    # ─── Navigation actions ────────────────────────────────────────────────────

    def action_go_dashboard(self) -> None:
        self._safe_push("dashboard")

    def action_go_feed(self) -> None:
        self._safe_push("feed")

    def action_go_chat(self) -> None:
        self._safe_push("chat")

    def action_go_sounds(self) -> None:
        self._safe_push("sounds")

    def action_go_profile(self) -> None:
        self._safe_push("profile")

    def action_go_live(self) -> None:
        self._safe_push("live")

    def action_go_explore(self) -> None:
        self._safe_push("explore")

    def action_go_notifications(self) -> None:
        self._safe_push("notifications")

    def action_go_stories(self) -> None:
        self._safe_push("stories")

    def action_go_settings(self) -> None:
        self._safe_push("settings")

    def _safe_push(self, screen_name: str) -> None:
        """Push screen only if authenticated"""
        if not self.auth.is_authenticated() and screen_name != "login":
            self.push_screen("login")
            return
        # Avoid duplicate screens at top of stack
        if self.screen.__class__.__name__.lower().startswith(screen_name.replace("_", "")):
            return
        self.push_screen(screen_name)

    # ─── Auth ─────────────────────────────────────────────────────────────────

    def action_action_logout(self) -> None:
        self.auth.logout()
        self.current_user = None
        # Clear stack back to login
        self.push_screen("login")

    def get_user(self):
        return self.current_user

    def set_user(self, user):
        self.current_user = user
        self.auth.user_data = user


def main():
    app = StripApp()
    app.run()


if __name__ == "__main__":
    main()
