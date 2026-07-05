# screens/settings.py
"""Paramètres & Thèmes — STRIP TUI 2026"""

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Label, Static, Button, Switch, Rule
from textual.containers import Horizontal, Vertical, Container
from textual import events

THEMES = {
    "dark":   ("🌑", "Dark Neon", "#e94560", "TikTok vibes — rouge & noir"),
    "cyber":  ("💚", "Cyber",     "#00ff41", "Matrix green — hacker vibes"),
    "ocean":  ("🌊", "Ocean",     "#4dabf7", "Deep blue — vibes océan"),
    "sunset": ("🌅", "Sunset",    "#f59f00", "Warm amber & violet"),
}


class ThemeCard(Static):
    """Carte de thème sélectionnable"""

    def __init__(self, key: str, active: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.theme_key = key
        self._active = active

    def on_mount(self) -> None:
        self._render()

    def _render(self) -> None:
        icon, name, color, desc = THEMES[self.theme_key]
        active_str = "  ✓ Actif" if self._active else ""
        self.update(
            f"{icon}  {name}{active_str}\n"
            f"   {color}  —  {desc}"
        )

    def set_active(self, active: bool) -> None:
        self._active = active
        self._render()


class SettingsScreen(Screen):
    """Paramètres complets — thèmes, compte, app"""

    CSS = """
    SettingsScreen {
        background: $background;
    }

    #settings-header {
        height: 3;
        background: #13131f;
        border-bottom: solid #1e1e2e;
        padding: 0 2;
    }

    #settings-title {
        color: #e94560;
        text-style: bold;
        width: 1fr;
    }

    #settings-body {
        height: 1fr;
        overflow-y: auto;
        padding: 1 3;
    }

    .section-header {
        color: #4dabf7;
        text-style: bold;
        padding: 1 0;
        height: 3;
    }

    /* Theme cards */
    #theme-grid {
        height: 16;
        margin-bottom: 1;
    }

    #theme-grid-inner {
        height: 14;
    }

    ThemeCard {
        background: #13131f;
        border: solid #1e1e2e;
        padding: 1;
        height: 6;
        margin: 0 1 1 0;
        width: 1fr;
    }

    ThemeCard:hover {
        border: solid #e94560;
        background: #16161f;
    }

    ThemeCard.theme-selected {
        border: solid #e94560;
        background: #1e1e2e;
    }

    /* Theme buttons */
    #theme-btns {
        height: 3;
        margin-bottom: 1;
    }

    #theme-btns Button {
        width: 1fr;
        height: 3;
        margin: 0 1 0 0;
        background: #13131f;
        border: solid #1e1e2e;
    }

    #theme-btns Button.theme-btn-active {
        background: #e94560;
        color: #fff;
        border: solid #e94560;
    }

    /* Settings rows */
    .setting-row {
        height: 4;
        border-bottom: solid #1e1e2e;
        padding: 1 0;
    }

    .setting-label {
        width: 1fr;
        color: #e0e0e0;
    }

    .setting-desc {
        color: #555577;
        height: 2;
    }

    /* Account section */
    #account-section {
        margin-top: 1;
        background: #13131f;
        border: solid #1e1e2e;
        padding: 1 2;
    }

    #account-section Label {
        padding: 0 0 1 0;
        height: 2;
    }

    #account-section Button {
        width: 20;
        margin: 1 1 0 0;
        height: 3;
    }

    /* Version */
    #version-info {
        color: #333355;
        text-align: center;
        padding: 1;
        height: 3;
    }

    #settings-bottom {
        height: 3;
        background: #13131f;
        border-top: solid #1e1e2e;
        padding: 0 2;
    }

    #settings-bottom Button {
        width: 20;
        margin: 0 1;
        height: 3;
    }
    """

    BINDINGS = [
        ("escape", "back", "Retour"),
    ]

    def compose(self) -> ComposeResult:
        current_theme = self.app.config.get("theme", "dark")
        user = self.app.current_user or {}

        with Horizontal(id="settings-header"):
            yield Label("⚙️  Paramètres", id="settings-title")

        with Container(id="settings-body"):
            # ── Thèmes ──
            yield Label("🎨  Thème de l'interface", classes="section-header")
            with Horizontal(id="theme-btns"):
                for key, (icon, name, color, _) in THEMES.items():
                    active_cls = "theme-btn-active" if key == current_theme else ""
                    yield Button(
                        f"{icon} {name}",
                        id=f"theme-{key}",
                        classes=active_cls,
                    )

            Rule()

            # ── Préférences ──
            yield Label("🔧  Préférences", classes="section-header")

            with Horizontal(classes="setting-row"):
                with Vertical():
                    yield Label("🔔  Notifications", classes="setting-label")
                    yield Label("Activer les alertes en temps réel", classes="setting-desc")
                yield Switch(
                    value=self.app.config.get("notifications", True),
                    id="sw-notifications",
                )

            with Horizontal(classes="setting-row"):
                with Vertical():
                    yield Label("⚡  Auto-complétion", classes="setting-label")
                    yield Label("Suggestions de commandes intelligentes", classes="setting-desc")
                yield Switch(
                    value=self.app.config.get("autocomplete", True),
                    id="sw-autocomplete",
                )

            with Horizontal(classes="setting-row"):
                with Vertical():
                    yield Label("🔇  Effets sonores", classes="setting-label")
                    yield Label("Sons de l'interface", classes="setting-desc")
                yield Switch(
                    value=self.app.config.get("sound_effects", False),
                    id="sw-sounds",
                )

            Rule()

            # ── Compte ──
            yield Label("👤  Compte", classes="section-header")
            with Container(id="account-section"):
                username = user.get("username", "N/A")
                email = user.get("email") or "Non renseigné"
                verified = "✅ Vérifié" if user.get("is_verified") else "○ Non vérifié"
                zodiac = user.get("zodiac_sign", "")
                yield Label(f"@{username}  —  {verified}  {zodiac}")
                yield Label(f"📧  {email}", classes="setting-desc")
                yield Label(f"👥  {user.get('followers_count', 0):,} abonnés  •  🎬  {user.get('videos_count', 0)} vidéos", classes="setting-desc")

                with Horizontal():
                    yield Button("✅  Demander vérification", id="btn-verify")
                    yield Button("🚪  Déconnexion", id="btn-logout", variant="error")

            Rule()

            # ── Version ──
            yield Static(
                "STRIP TUI v2.0  —  Plateforme de streaming terminal  —  2026",
                id="version-info",
            )

        with Horizontal(id="settings-bottom"):
            yield Button("💾 Sauvegarder", id="btn-save", variant="primary")
            yield Button("🔙 Retour", id="btn-back")

    def action_back(self) -> None:
        self.app.pop_screen()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        bid = event.button.id
        if bid == "btn-back":
            self.action_back()
        elif bid == "btn-save":
            self._save_settings()
            self.action_back()
        elif bid == "btn-logout":
            self.app.auth.logout()
            self.app.current_user = None
            # Clear screen stack and go to login
            while self.app.screen_stack:
                try:
                    self.app.pop_screen()
                except Exception:
                    break
            self.app.push_screen("login")
        elif bid == "btn-verify":
            self.app.push_screen("profile")
        elif bid and bid.startswith("theme-"):
            theme_key = bid[6:]
            if theme_key in THEMES:
                self._apply_theme(theme_key)

    def on_switch_changed(self, event: Switch.Changed) -> None:
        sw_id = event.switch.id
        val = event.value
        if sw_id == "sw-notifications":
            self.app.config.set("notifications", val)
        elif sw_id == "sw-autocomplete":
            self.app.config.set("autocomplete", val)
        elif sw_id == "sw-sounds":
            self.app.config.set("sound_effects", val)

    def _apply_theme(self, theme_key: str) -> None:
        # Remove all theme classes
        for key in THEMES:
            self.app.remove_class(f"theme-{key}")
        # Apply new theme
        if theme_key != "dark":
            self.app.add_class(f"theme-{theme_key}")
        # Save to config
        self.app.config.set("theme", theme_key)
        # Update button visuals
        for key in THEMES:
            try:
                btn = self.query_one(f"#theme-{key}", Button)
                if key == theme_key:
                    btn.add_class("theme-btn-active")
                else:
                    btn.remove_class("theme-btn-active")
            except Exception:
                pass

    def _save_settings(self) -> None:
        self.app.config.save()
