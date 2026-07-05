# screens/profile.py
"""Profil complet — STRIP TUI 2026"""

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import (
    Label, Static, Button, ListView, ListItem, Rule,
    TabbedContent, TabPane
)
from textual.containers import Horizontal, Vertical, Container, Grid
from textual import events
from rich.text import Text


def fmt_count(n: int) -> str:
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n/1_000:.1f}K"
    return str(n)


class ProfileScreen(Screen):
    """Profil utilisateur complet"""

    CSS = """
    ProfileScreen {
        background: $background;
    }

    #profile-header {
        height: 12;
        background: #13131f;
        border-bottom: solid #1e1e2e;
        padding: 1 2;
    }

    #avatar-box {
        width: 14;
        height: 10;
        border: solid #e94560;
        align: center middle;
        text-align: center;
        background: #1e1e2e;
        margin-right: 2;
    }

    #avatar-icon {
        color: #e94560;
        text-align: center;
    }

    #profile-info {
        width: 1fr;
        height: 10;
        padding: 1 0;
    }

    #username-line {
        text-style: bold;
        color: #e94560;
        height: 2;
    }

    #badge-line {
        color: #4dabf7;
        height: 2;
    }

    #bio-line {
        color: #888;
        height: 3;
        overflow: hidden;
    }

    #profile-actions {
        width: 25;
        height: 10;
        padding: 1 0;
    }

    #profile-actions Button {
        width: 100%;
        margin-bottom: 1;
        height: 3;
    }

    #stats-row {
        height: 5;
        background: #0d0d18;
        border-bottom: solid #1e1e2e;
        padding: 0 2;
    }

    .stat-col {
        width: 1fr;
        align: center middle;
        text-align: center;
        height: 5;
        border-right: solid #1e1e2e;
    }

    .stat-number {
        color: #e94560;
        text-style: bold;
    }

    .stat-label {
        color: #555577;
    }

    #profile-tabs {
        height: 1fr;
    }

    #tab-videos-list, #tab-sounds-list, #tab-actfiles-list {
        height: 1fr;
        overflow-y: auto;
        padding: 1;
    }

    .content-card {
        background: #13131f;
        border: solid #1e1e2e;
        padding: 1;
        margin-bottom: 1;
        height: 6;
    }

    .content-card:hover {
        border: solid #e94560;
    }

    #profile-bottom {
        height: 3;
        background: #13131f;
        border-top: solid #1e1e2e;
        padding: 0 2;
    }

    #profile-bottom Button {
        width: 20;
        margin: 0 1;
        height: 3;
    }
    """

    BINDINGS = [
        ("escape", "back", "Retour"),
        ("r", "reload", "Rafraîchir"),
    ]

    def __init__(self, user_id: str = "", username: str = ""):
        super().__init__()
        self.target_user_id = user_id
        self.target_username = username
        self._profile = {}
        self._is_own = True
        self._is_following = False

    def compose(self) -> ComposeResult:
        user = self.app.current_user or {}

        # Header profil
        with Horizontal(id="profile-header"):
            with Container(id="avatar-box"):
                yield Static("🐬\n\n@me", id="avatar-icon")

            with Vertical(id="profile-info"):
                yield Static("", id="username-line")
                yield Static("", id="badge-line")
                yield Static("", id="bio-line")

            with Vertical(id="profile-actions"):
                yield Button("✏️  Éditer", id="btn-edit")
                yield Button("✅  Vérification", id="btn-verify")

        # Barre stats
        with Horizontal(id="stats-row"):
            with Container(classes="stat-col"):
                yield Static("", id="stat-followers-num", classes="stat-number")
                yield Static("Abonnés", classes="stat-label")
            with Container(classes="stat-col"):
                yield Static("", id="stat-following-num", classes="stat-number")
                yield Static("Abonnements", classes="stat-label")
            with Container(classes="stat-col"):
                yield Static("", id="stat-videos-num", classes="stat-number")
                yield Static("Vidéos", classes="stat-label")
            with Container(classes="stat-col"):
                yield Static("", id="stat-likes-num", classes="stat-number")
                yield Static("Likes", classes="stat-label")

        # Onglets contenu
        with TabbedContent(id="profile-tabs"):
            with TabPane("🎬 Vidéos", id="tab-videos"):
                yield ListView(id="tab-videos-list")
            with TabPane("🎵 Sons", id="tab-sounds"):
                yield ListView(id="tab-sounds-list")
            with TabPane("📄 Posts", id="tab-actfiles"):
                yield ListView(id="tab-actfiles-list")

        # Bas de page
        with Horizontal(id="profile-bottom"):
            yield Button("🔄 Rafraîchir", id="btn-refresh", variant="primary")
            yield Button("🔙 Retour", id="btn-back")

    def on_mount(self) -> None:
        self._load_profile()

    def action_back(self) -> None:
        self.app.pop_screen()

    def action_reload(self) -> None:
        self._load_profile()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        bid = event.button.id
        if bid == "btn-back":
            self.action_back()
        elif bid == "btn-refresh":
            self.action_reload()
        elif bid == "btn-follow":
            self._toggle_follow()
        elif bid == "btn-verify":
            self.app.push_screen("settings")
        elif bid == "btn-edit":
            pass  # TODO: edit screen

    def _load_profile(self) -> None:
        user = self.app.current_user or {}
        my_id = self.app.auth.get_user_id() or ""

        # Determine which profile to show
        uid = self.target_user_id or my_id
        self._is_own = uid == my_id

        # Fetch full profile
        try:
            data = self.app.api.get_my_profile(self.app.auth.token) if self._is_own else \
                   self.app.api.get_user_profile(uid, self.app.auth.token)
            if data:
                self._profile = data
                self._update_ui()
        except Exception:
            pass

        self._load_videos(uid)
        self._load_sounds(uid)
        self._load_actfiles()

    def _update_ui(self) -> None:
        p = self._profile
        username = p.get("username", "?")
        verified = p.get("is_verified", False)
        zodiac = p.get("zodiac_sign", "")
        bio = p.get("bio") or "Aucune bio renseignée"
        followers = int(p.get("followers_count", 0))
        following = int(p.get("following_count", 0))
        videos = int(p.get("videos_count", 0))
        likes = int(p.get("likes_received", 0))

        # Avatar area
        try:
            self.query_one("#avatar-icon").update(f"🐬\n\n@{username[:8]}")
        except Exception:
            pass

        # Name line
        try:
            badge = " ✅" if verified else ""
            zodiac_str = f"  {zodiac}" if zodiac else ""
            self.query_one("#username-line").update(f"@{username}{badge}{zodiac_str}")
        except Exception:
            pass

        # Badge line
        try:
            if verified:
                self.query_one("#badge-line").update("🏅  Compte vérifié STRIP")
            else:
                self.query_one("#badge-line").update("○  Non vérifié")
        except Exception:
            pass

        # Bio
        try:
            self.query_one("#bio-line").update(f"📝  {bio[:80]}")
        except Exception:
            pass

        # Stats
        for wid, val in [
            ("stat-followers-num", fmt_count(followers)),
            ("stat-following-num", fmt_count(following)),
            ("stat-videos-num", fmt_count(videos)),
            ("stat-likes-num", fmt_count(likes)),
        ]:
            try:
                self.query_one(f"#{wid}", Static).update(val)
            except Exception:
                pass

        # Show follow btn if not own profile
        if not self._is_own:
            try:
                btn_edit = self.query_one("#btn-edit", Button)
                btn_edit.label = "👥  Suivre" if not self._is_following else "✓  Abonné"
                btn_edit.id = "btn-follow"
            except Exception:
                pass

    def _load_videos(self, user_id: str) -> None:
        lv = self.query_one("#tab-videos-list", ListView)
        lv.clear()
        try:
            videos = self.app.api.get("/api/profile/{}/wings".format(user_id),
                                      self.app.auth.token) or {}
            wings = videos.get("wings", []) if isinstance(videos, dict) else []
            if wings:
                for v in wings[:15]:
                    desc = (v.get("description") or "")[:60]
                    views = fmt_count(v.get("views_count", 0))
                    likes = fmt_count(v.get("likes_count", 0))
                    item = Static(
                        f"  🎬  {desc or '(sans titre)'}\n"
                        f"  👁 {views}  ❤️ {likes}"
                    )
                    lv.append(ListItem(item))
            else:
                lv.append(ListItem(Static("  📭  Aucune vidéo publiée")))
        except Exception:
            lv.append(ListItem(Static("  📭  Aucune vidéo")))

    def _load_sounds(self, user_id: str) -> None:
        lv = self.query_one("#tab-sounds-list", ListView)
        lv.clear()
        try:
            sounds = self.app.api.get(f"/api/users/{user_id}/sounds", self.app.auth.token) or []
            if sounds:
                for s in sounds[:15]:
                    title = s.get("title", "?")
                    cat = s.get("category", "")
                    plays = fmt_count(s.get("plays_count", 0))
                    item = Static(f"  🎵  {title}  [{cat}]\n  ▶ {plays} écoutes")
                    lv.append(ListItem(item))
            else:
                lv.append(ListItem(Static("  📭  Aucun son publié")))
        except Exception:
            lv.append(ListItem(Static("  📭  Aucun son")))

    def _load_actfiles(self) -> None:
        lv = self.query_one("#tab-actfiles-list", ListView)
        lv.clear()
        try:
            posts = self.app.api.get_actfiles(self.app.auth.token, limit=10) or []
            # Filter to current user's posts if own profile
            if posts:
                my_id = self.app.auth.get_user_id()
                my_posts = [p for p in posts if p.get("user_id") == my_id] if self._is_own else posts
                for p in my_posts[:10]:
                    content = (p.get("content") or "")[:80]
                    likes = fmt_count(p.get("likes_count", 0))
                    item = Static(f"  📄  {content}\n  ❤️ {likes}")
                    lv.append(ListItem(item))
                if not my_posts:
                    lv.append(ListItem(Static("  📭  Aucun post")))
            else:
                lv.append(ListItem(Static("  📭  Aucun post")))
        except Exception:
            lv.append(ListItem(Static("  📭  Aucun post")))

    def _toggle_follow(self) -> None:
        uid = self.target_user_id
        if not uid:
            return
        try:
            result = self.app.api.follow_user(uid, self.app.auth.token) or {}
            self._is_following = result.get("following", not self._is_following)
        except Exception:
            pass
