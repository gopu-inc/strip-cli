# screens/notifications.py
"""Notifications — STRIP TUI 2026"""

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Label, Static, Button, ListView, ListItem
from textual.containers import Horizontal, Vertical, Container
from textual import events
from rich.text import Text
from datetime import datetime


TYPE_ICONS = {
    "like":          "❤️",
    "follow":        "👥",
    "message":       "💬",
    "sound_like":    "🎵",
    "actfile_like":  "📄",
    "live":          "🔴",
    "project_invite":"🎛",
    "sound_comment": "🗨",
    "actfile_like":  "📄",
}


def fmt_time(ts) -> str:
    try:
        if isinstance(ts, str):
            dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            return dt.strftime("%d/%m %H:%M")
        return ""
    except Exception:
        return ""


class NotifItem(ListItem):
    def __init__(self, notif: dict):
        super().__init__()
        self.notif = notif

    def render(self) -> Text:
        n = self.notif
        icon = TYPE_ICONS.get(n.get("type", ""), "🔔")
        user = n.get("from_username", "?")
        msg = n.get("message", "")
        time_str = fmt_time(n.get("created_at"))
        read = n.get("read", True)
        unread_dot = "●  " if not read else "   "

        t = Text()
        t.append(f"  {unread_dot}", style="bold #e94560" if not read else "")
        t.append(f"{icon}  ", style="bold")
        t.append(f"@{user}", style="bold #4dabf7")
        t.append(f"\n    {msg}", style="#e0e0e0")
        t.append(f"  {time_str}", style="#555577")
        return t


class NotificationsScreen(Screen):
    """Écran des notifications"""

    CSS = """
    NotificationsScreen {
        background: $background;
    }

    #notif-header {
        height: 3;
        background: #13131f;
        border-bottom: solid #1e1e2e;
        padding: 0 2;
    }

    #notif-title {
        color: #e94560;
        text-style: bold;
        width: 1fr;
    }

    #notif-count {
        color: #555577;
        text-align: right;
        width: 20;
    }

    #filter-bar {
        height: 3;
        background: #0d0d18;
        border-bottom: solid #1e1e2e;
    }

    #filter-bar Button {
        width: 1fr;
        height: 3;
        background: transparent;
        color: #555577;
        border: none;
        margin: 0;
    }

    #filter-bar Button.filter-active {
        color: #e94560;
        border-bottom: solid #e94560;
    }

    #notif-list {
        height: 1fr;
        overflow-y: auto;
        padding: 1 2;
    }

    NotifItem {
        background: #13131f;
        border: solid #1e1e2e;
        margin-bottom: 1;
        padding: 1;
        height: 6;
    }

    NotifItem:hover {
        border: solid #e94560;
    }

    NotifItem.unread {
        border-left: solid #e94560;
    }

    #notif-bottom {
        height: 3;
        background: #13131f;
        border-top: solid #1e1e2e;
        padding: 0 2;
    }

    #notif-bottom Button {
        width: 20;
        margin: 0 1;
        height: 3;
    }
    """

    BINDINGS = [
        ("escape", "back", "Retour"),
        ("r", "reload", "Rafraîchir"),
    ]

    def __init__(self):
        super().__init__()
        self._filter = "all"

    def compose(self) -> ComposeResult:
        with Horizontal(id="notif-header"):
            yield Label("🔔  Notifications", id="notif-title")
            yield Label("", id="notif-count")

        with Horizontal(id="filter-bar"):
            yield Button("🔔 Toutes", id="filter-all", classes="filter-active")
            yield Button("🔴 Non lues", id="filter-unread")
            yield Button("❤️ Likes", id="filter-likes")
            yield Button("👥 Abonnés", id="filter-follows")

        yield ListView(id="notif-list")

        with Horizontal(id="notif-bottom"):
            yield Button("🔄 Rafraîchir", id="btn-refresh", variant="primary")
            yield Button("🔙 Retour", id="btn-back")

    def on_mount(self) -> None:
        self.load_notifications()

    def action_back(self) -> None:
        self.app.pop_screen()

    def action_reload(self) -> None:
        self.load_notifications()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        bid = event.button.id
        if bid == "btn-back":
            self.action_back()
        elif bid == "btn-refresh":
            self.load_notifications()
        elif bid.startswith("filter-"):
            self._filter = bid[7:]
            self._update_filter_btns(bid)
            self.load_notifications()

    def _update_filter_btns(self, active: str) -> None:
        for fid in ["filter-all", "filter-unread", "filter-likes", "filter-follows"]:
            try:
                btn = self.query_one(f"#{fid}", Button)
                if fid == active:
                    btn.add_class("filter-active")
                else:
                    btn.remove_class("filter-active")
            except Exception:
                pass

    def load_notifications(self) -> None:
        lv = self.query_one("#notif-list", ListView)
        lv.clear()
        self.query_one("#notif-count").update("🔄  Chargement...")
        try:
            notifs = self.app.api.get_notifications(self.app.auth.token, 50) or []

            # Apply filter
            if self._filter == "unread":
                notifs = [n for n in notifs if not n.get("read")]
            elif self._filter == "likes":
                notifs = [n for n in notifs if "like" in n.get("type", "")]
            elif self._filter == "follows":
                notifs = [n for n in notifs if n.get("type") == "follow"]

            unread_count = sum(1 for n in notifs if not n.get("read"))
            self.query_one("#notif-count").update(
                f"{'🔴 ' + str(unread_count) + ' non lues' if unread_count else '✅ À jour'}"
            )

            if notifs:
                for n in notifs:
                    item = NotifItem(n)
                    if not n.get("read"):
                        item.add_class("unread")
                    lv.append(item)
            else:
                lv.append(
                    ListItem(
                        Static("  📭  Aucune notification\n  Vous êtes à jour !")
                    )
                )
        except Exception:
            self.query_one("#notif-count").update("❌  Erreur réseau")
