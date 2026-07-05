# screens/chat.py
"""Chat WhatsApp-style — STRIP TUI 2026"""

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Label, Static, Button, ListView, ListItem, Input, Rule
from textual.containers import Horizontal, Vertical, Container
from textual import events
from rich.text import Text
from datetime import datetime
import base64
from pathlib import Path


def _fmt_time(ts) -> str:
    try:
        if isinstance(ts, str):
            dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            return dt.strftime("%H:%M")
        return ""
    except Exception:
        return ""


class ConvItem(ListItem):
    """Conversation dans la sidebar"""

    def __init__(self, conv: dict):
        super().__init__()
        self.conv = conv

    def render(self) -> Text:
        c = self.conv
        online = "🟢" if c.get("is_online") else "⚪"
        verified = " ✅" if c.get("is_verified") else ""
        uname = c.get("username", "?")
        last_msg = (c.get("last_message") or "")[:35]
        unread = c.get("unread_count", 0)
        time_str = _fmt_time(c.get("last_message_time"))

        t = Text()
        t.append(f"{online} ", style="")
        t.append(f"@{uname}", style="bold #e94560")
        t.append(f"{verified}", style="#4dabf7")
        if unread:
            t.append(f"  [{unread}]", style="bold #51cf66")
        t.append(f"\n   ", style="")
        t.append(f"{last_msg}", style="#888")
        if time_str:
            t.append(f"  {time_str}", style="#555577")
        return t


class MsgItem(ListItem):
    """Message dans la conversation"""

    def __init__(self, msg: dict, is_mine: bool):
        super().__init__()
        self.msg = msg
        self.is_mine = is_mine

    def render(self) -> Text:
        m = self.msg
        content = m.get("content", "")
        msg_type = m.get("type", "text")
        time_str = _fmt_time(m.get("created_at"))
        sender = m.get("sender_username", "")

        t = Text()
        if self.is_mine:
            # Right-aligned style
            if msg_type == "audio":
                t.append("  🎤 ", style="bold")
                t.append("Message vocal", style="#f59f00")
            elif msg_type == "image":
                t.append("  🖼 ", style="bold")
                t.append("Image", style="#4dabf7")
            elif msg_type == "video":
                t.append("  📹 ", style="bold")
                t.append("Vidéo", style="#845ef7")
            else:
                t.append(f"  {content}", style="#e0e0e0")
            t.append(f"\n  {time_str} ✓✓", style="#555577")
        else:
            sender_label = f"@{sender}: " if sender else ""
            if msg_type == "audio":
                t.append(f"  {sender_label}", style="bold #4dabf7")
                t.append("🎤 Message vocal", style="#f59f00")
            elif msg_type == "image":
                t.append(f"  {sender_label}", style="bold #4dabf7")
                t.append("🖼 Image", style="#4dabf7")
            else:
                t.append(f"  {sender_label}", style="bold #4dabf7")
                t.append(f"{content}", style="#c8e6ff")
            t.append(f"\n  {time_str}", style="#555577")
        return t


class ChatScreen(Screen):
    """Chat WhatsApp-style"""

    CSS = """
    ChatScreen {
        background: $background;
    }

    #chat-header {
        height: 3;
        background: #13131f;
        border-bottom: solid #1e1e2e;
        padding: 0 2;
    }

    #chat-title {
        color: #e94560;
        text-style: bold;
        width: 1fr;
    }

    #chat-status {
        color: #555577;
        text-align: right;
        width: 25;
    }

    #chat-body {
        height: 1fr;
    }

    /* ── Sidebar contacts ── */
    #sidebar {
        width: 30;
        background: #0d0d18;
        border-right: solid #1e1e2e;
    }

    #sidebar-search {
        margin: 1;
    }

    #contacts-label {
        color: #4dabf7;
        text-style: bold;
        padding: 0 1;
        height: 2;
    }

    #conv-list {
        height: 1fr;
        background: transparent;
    }

    #conv-list ConvItem {
        height: 5;
        padding: 1;
        border: none;
        border-bottom: solid #1e1e2e;
        background: transparent;
        margin: 0;
    }

    #conv-list ConvItem:hover {
        background: #13131f;
    }

    #conv-list ConvItem.--highlight {
        background: #1a1a2a;
        border-left: solid #e94560;
    }

    /* ── Chat panel ── */
    #chat-panel {
        width: 1fr;
        background: #0a0a0f;
    }

    #conversation-header {
        height: 4;
        background: #13131f;
        border-bottom: solid #1e1e2e;
        padding: 0 2;
    }

    #conv-username {
        color: #e94560;
        text-style: bold;
        height: 2;
    }

    #conv-meta {
        color: #555577;
        height: 2;
    }

    #messages-area {
        height: 1fr;
        overflow-y: auto;
        padding: 1 1;
    }

    #msg-list {
        height: auto;
        background: transparent;
    }

    #msg-list MsgItem {
        height: 5;
        border: none;
        background: transparent;
        margin: 0 0 1 0;
    }

    #msg-list MsgItem.mine {
        background: #13131f;
        border-right: solid #e94560;
        margin-left: 5;
    }

    #msg-list MsgItem.theirs {
        background: #0d0d18;
        border-left: solid #4dabf7;
        margin-right: 5;
    }

    #input-area {
        height: 5;
        background: #13131f;
        border-top: solid #1e1e2e;
        padding: 1;
    }

    #msg-input {
        width: 1fr;
        margin-right: 1;
    }

    #btn-voice {
        width: 5;
        background: #1e1e2e;
    }

    #btn-send {
        width: 12;
    }

    #voice-bar {
        height: 3;
        background: #2a0010;
        border-top: solid #e94560;
        padding: 0 2;
        display: none;
    }

    #voice-status {
        width: 1fr;
        color: #e94560;
    }

    #btn-stop-rec {
        width: 12;
    }

    #no-conv {
        width: 1fr;
        align: center middle;
        color: #333355;
        text-align: center;
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
        ("ctrl+r", "reload", "Rafraîchir"),
    ]

    def __init__(self):
        super().__init__()
        self.current_chat_id = None
        self.current_chat_username = ""
        self.is_recording = False
        self.recording_timer = 0
        self._convs = []

    def compose(self) -> ComposeResult:
        with Horizontal(id="chat-header"):
            yield Label("💬  Messagerie", id="chat-title")
            yield Label("", id="chat-status")

        with Horizontal(id="chat-body"):
            # Sidebar
            with Vertical(id="sidebar"):
                yield Label("👥  Contacts", id="contacts-label")
                yield Input(placeholder="🔍  Rechercher...", id="sidebar-search")
                yield ListView(id="conv-list")

            # Chat panel
            with Vertical(id="chat-panel"):
                # Header conversation
                with Container(id="conversation-header"):
                    yield Label("", id="conv-username")
                    yield Label("Sélectionnez une conversation", id="conv-meta")

                # Messages
                with Container(id="messages-area"):
                    yield Static(
                        "💬\n\nSélectionnez un contact\npour commencer à discuter",
                        id="no-conv",
                    )
                    yield ListView(id="msg-list")

                # Zone vocal active
                with Horizontal(id="voice-bar"):
                    yield Label("🔴  Enregistrement vocal...", id="voice-status")
                    yield Button("⏹  Arrêter", id="btn-stop-rec", variant="error")

                # Input
                with Horizontal(id="input-area"):
                    yield Input(placeholder="Tapez votre message...", id="msg-input")
                    yield Button("🎤", id="btn-voice")
                    yield Button("📤 Envoyer", id="btn-send", variant="primary")

        yield Static(
            "  Tab  navigation  •  Entrée  envoyer  •  Ctrl+R  rafraîchir  •  Esc  retour",
            id="hint-bar",
        )

    def on_mount(self) -> None:
        self.load_conversations()
        self.query_one("#sidebar-search").focus()

    def action_back(self) -> None:
        self.app.pop_screen()

    def action_reload(self) -> None:
        self.load_conversations()
        if self.current_chat_id:
            self.load_messages(self.current_chat_id)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "sidebar-search":
            self.search_contacts(event.input.value)
        elif event.input.id == "msg-input":
            self.send_text_message()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        bid = event.button.id
        if bid == "btn-send":
            self.send_text_message()
        elif bid == "btn-voice":
            self.toggle_recording()
        elif bid == "btn-stop-rec":
            self.stop_recording()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        item = event.item
        if hasattr(item, "conv"):
            c = item.conv
            self.current_chat_id = c.get("user_id") or c.get("id")
            self.current_chat_username = c.get("username", "")
            # Update header
            verified = " ✅" if c.get("is_verified") else ""
            online = "🟢 En ligne" if c.get("is_online") else "⚪ Hors ligne"
            self.query_one("#conv-username").update(
                f"@{self.current_chat_username}{verified}"
            )
            self.query_one("#conv-meta").update(online)
            # Hide no-conv placeholder
            self.query_one("#no-conv").styles.display = "none"
            # Load messages
            self.load_messages(self.current_chat_id)
            self.query_one("#msg-input").focus()

    def load_conversations(self) -> None:
        lv = self.query_one("#conv-list", ListView)
        lv.clear()
        self._convs = []
        self.query_one("#chat-status").update("🔄  Chargement...")
        try:
            convs = self.app.api.get_conversations(self.app.auth.token) or []
            self._convs = convs
            if convs:
                for c in convs:
                    lv.append(ConvItem(c))
                self.query_one("#chat-status").update(f"✅  {len(convs)} contacts")
            else:
                lv.append(ListItem(Static("  📭  Aucune conversation")))
                self.query_one("#chat-status").update("📭  Vide")
        except Exception:
            self.query_one("#chat-status").update("❌  Erreur réseau")

    def search_contacts(self, query: str) -> None:
        if not query or len(query) < 2:
            self.load_conversations()
            return
        lv = self.query_one("#conv-list", ListView)
        lv.clear()
        try:
            results = self.app.api.search(query, "users", self.app.auth.token) or {}
            users = results.get("results", [])
            if users:
                for u in users[:15]:
                    lv.append(ConvItem(u))
                self.query_one("#chat-status").update(f"🔍  {len(users)} résultats")
            else:
                lv.append(ListItem(Static("  ❌  Aucun résultat")))
        except Exception:
            self.query_one("#chat-status").update("❌  Erreur")

    def load_messages(self, user_id: str) -> None:
        lv = self.query_one("#msg-list", ListView)
        lv.clear()
        self.query_one("#chat-status").update("🔄  Messages...")
        try:
            msgs = self.app.api.get_messages(user_id, self.app.auth.token) or []
            my_id = self.app.auth.get_user_id() or ""
            if msgs:
                for m in msgs:
                    is_mine = m.get("sender_id") == my_id
                    item = MsgItem(m, is_mine)
                    if is_mine:
                        item.add_class("mine")
                    else:
                        item.add_class("theirs")
                    lv.append(item)
                lv.scroll_end()
                self.query_one("#chat-status").update(f"✅  {len(msgs)} messages")
            else:
                lv.append(ListItem(Static("  📭  Aucun message\n  Envoyez le premier !")))
                self.query_one("#chat-status").update("📭  Vide")
        except Exception:
            self.query_one("#chat-status").update("❌  Erreur")

    def send_text_message(self) -> None:
        if not self.current_chat_id:
            self.query_one("#chat-status").update("⚠️  Sélectionnez un contact")
            return
        inp = self.query_one("#msg-input", Input)
        content = inp.value.strip()
        if not content:
            return
        self.query_one("#chat-status").update("📤  Envoi...")
        try:
            result = self.app.api.send_message(
                self.current_chat_id, content, token=self.app.auth.token
            )
            if result is not None:
                inp.value = ""
                self.query_one("#chat-status").update("✅  Envoyé")
                self.load_messages(self.current_chat_id)
            else:
                self.query_one("#chat-status").update("❌  Échec d'envoi")
        except Exception:
            self.query_one("#chat-status").update("❌  Erreur réseau")

    def toggle_recording(self) -> None:
        if not self.current_chat_id:
            self.query_one("#chat-status").update("⚠️  Sélectionnez un contact")
            return
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()

    def start_recording(self) -> None:
        self.is_recording = True
        self.recording_timer = 0
        self.query_one("#voice-bar").styles.display = "block"
        self.query_one("#btn-voice").label = "🔴"
        self.query_one("#chat-status").update("🔴  Enregistrement vocal...")

        audio_file = Path("/tmp/strip_voice.wav")
        audio_file.touch()
        self._audio_path = audio_file

        def _tick():
            if self.is_recording:
                self.recording_timer += 1
                try:
                    self.query_one("#voice-status").update(
                        f"🔴  Enregistrement... {self.recording_timer}s"
                    )
                    self.set_timer(1.0, _tick)
                except Exception:
                    pass

        self.set_timer(1.0, _tick)

    def stop_recording(self) -> None:
        self.is_recording = False
        self.query_one("#voice-bar").styles.display = "none"
        self.query_one("#btn-voice").label = "🎤"
        self.query_one("#chat-status").update(
            f"⏹  Vocal {self.recording_timer}s — envoi..."
        )
        self._send_voice_message()

    def _send_voice_message(self) -> None:
        try:
            result = self.app.api.send_message(
                self.current_chat_id,
                f"[Message vocal — {self.recording_timer}s]",
                msg_type="audio",
                token=self.app.auth.token,
            )
            if result is not None:
                self.query_one("#chat-status").update("✅  Vocal envoyé")
                self.load_messages(self.current_chat_id)
            else:
                self.query_one("#chat-status").update("❌  Échec vocal")
        except Exception:
            self.query_one("#chat-status").update("❌  Erreur vocal")
