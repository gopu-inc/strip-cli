# screens/actfiles.py
"""ActFiles — Posts Markdown — STRIP TUI 2026"""

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import (
    Label, Static, Button, ListView, ListItem,
    Input, TextArea, Markdown
)
from textual.containers import Horizontal, Vertical, Container
from textual import events
from rich.text import Text
from datetime import datetime


def fmt_count(n: int) -> str:
    if n >= 1_000:
        return f"{n/1_000:.1f}K"
    return str(n)


def fmt_time(ts) -> str:
    try:
        if isinstance(ts, str):
            dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            return dt.strftime("%d/%m %H:%M")
        return ""
    except Exception:
        return ""


class PostCard(ListItem):
    """Carte post Markdown"""

    def __init__(self, post: dict):
        super().__init__()
        self.post = post

    def render(self) -> Text:
        p = self.post
        author = p.get("username", "?")
        verified = " ✅" if p.get("is_verified") else ""
        content = (p.get("content") or "")[:120].replace("\n", " ")
        likes = fmt_count(p.get("likes_count", 0))
        views = fmt_count(p.get("views_count", 0))
        comments = 0  # Would need a separate call
        time_str = fmt_time(p.get("created_at"))
        liked = "❤️" if p.get("liked") else "🤍"

        t = Text()
        t.append(f"  @{author}", style="bold #e94560")
        t.append(f"{verified}", style="#4dabf7")
        t.append(f"  {time_str}\n", style="#555577")
        t.append(f"  {content}...\n", style="#c8c8c8")
        t.append(f"\n  {liked} {likes}  👁 {views}  💬 {comments}", style="dim")
        return t


class ActFilesScreen(Screen):
    """Publications Markdown — style TikTok posts"""

    CSS = """
    ActFilesScreen {
        background: $background;
    }

    #af-header {
        height: 3;
        background: #13131f;
        border-bottom: solid #1e1e2e;
        padding: 0 2;
    }

    #af-title {
        color: #e94560;
        text-style: bold;
        width: 1fr;
    }

    #af-status {
        color: #555577;
        text-align: right;
        width: 25;
    }

    #af-body {
        height: 1fr;
    }

    /* Feed panel */
    #feed-panel {
        width: 1fr;
        background: #0a0a0f;
    }

    #af-list {
        height: 1fr;
        overflow-y: auto;
        padding: 1 2;
    }

    PostCard {
        background: #13131f;
        border: solid #1e1e2e;
        margin-bottom: 1;
        padding: 1;
        height: 8;
    }

    PostCard:hover {
        border: solid #e94560;
        background: #16161f;
    }

    PostCard.--highlight {
        border: solid #e94560;
    }

    /* Viewer panel */
    #viewer-panel {
        width: 45;
        background: #0d0d18;
        border-left: solid #1e1e2e;
        display: none;
    }

    #viewer-header {
        height: 3;
        background: #13131f;
        border-bottom: solid #1e1e2e;
        padding: 0 1;
    }

    #viewer-author {
        color: #e94560;
        text-style: bold;
        width: 1fr;
    }

    #viewer-close {
        width: 5;
        height: 3;
        background: transparent;
        border: none;
        margin: 0;
    }

    #viewer-content {
        height: 1fr;
        overflow-y: auto;
        padding: 1 2;
    }

    #viewer-actions {
        height: 3;
        background: #13131f;
        border-top: solid #1e1e2e;
        padding: 0 1;
    }

    #comment-input {
        height: 3;
        margin: 1;
        padding: 0 1;
        border-bottom: solid #1e1e2e;
    }

    /* Write panel */
    #write-panel {
        width: 45;
        background: #0d0d18;
        border-left: solid #1e1e2e;
        display: none;
    }

    #write-header {
        height: 3;
        background: #13131f;
        border-bottom: solid #1e1e2e;
        padding: 0 1;
    }

    #write-area {
        height: 1fr;
        padding: 1;
    }

    #post-editor {
        height: 1fr;
    }

    #write-actions {
        height: 3;
        background: #13131f;
        border-top: solid #1e1e2e;
        padding: 0 1;
    }

    #af-bottom {
        height: 3;
        background: #13131f;
        border-top: solid #1e1e2e;
        padding: 0 2;
    }

    #af-bottom Button {
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
        ("n", "new_post", "Nouveau post"),
        ("r", "reload", "Rafraîchir"),
        ("l", "like_current", "Liker"),
    ]

    def __init__(self):
        super().__init__()
        self._posts = []
        self._current_post = None
        self._current_idx = 0
        self._panel_mode = None  # None | "view" | "write"

    def compose(self) -> ComposeResult:
        with Horizontal(id="af-header"):
            yield Label("📄  ActFiles — Posts", id="af-title")
            yield Label("", id="af-status")

        with Horizontal(id="af-body"):
            # Feed
            with Vertical(id="feed-panel"):
                yield ListView(id="af-list")

            # Viewer panel
            with Vertical(id="viewer-panel"):
                with Horizontal(id="viewer-header"):
                    yield Label("", id="viewer-author")
                    yield Button("✕", id="btn-close-viewer")
                with Container(id="viewer-content"):
                    yield Static("", id="viewer-markdown")
                with Horizontal(id="viewer-actions"):
                    yield Button("❤️ Liker", id="btn-like-post", variant="primary")
                    yield Button("💬 Commenter", id="btn-open-comment")
                with Horizontal(id="comment-input"):
                    yield Input(placeholder="Votre commentaire...", id="comment-text")
                    yield Button("📤", id="btn-send-comment")

            # Write panel
            with Vertical(id="write-panel"):
                with Horizontal(id="write-header"):
                    yield Label("✏️  Nouveau post Markdown")
                with Container(id="write-area"):
                    yield TextArea(
                        "# Mon post\n\nÉcrivez votre post en **Markdown**...\n",
                        id="post-editor",
                        language="markdown",
                    )
                with Horizontal(id="write-actions"):
                    yield Button("📤 Publier", id="btn-publish", variant="primary")
                    yield Button("✕ Annuler", id="btn-cancel-write")

        with Horizontal(id="af-bottom"):
            yield Button("✏️ Nouveau post", id="btn-new", variant="primary")
            yield Button("🔄 Rafraîchir", id="btn-refresh")
            yield Button("🔙 Retour", id="btn-back")

        yield Static(
            "  ↑↓  naviguer  •  Entrée  voir  •  N  nouveau  •  L  liker  •  Esc  retour",
            id="hint-bar",
        )

    def on_mount(self) -> None:
        self.load_posts()

    def action_back(self) -> None:
        if self._panel_mode:
            self._close_panels()
        else:
            self.app.pop_screen()

    def action_reload(self) -> None:
        self.load_posts()

    def action_new_post(self) -> None:
        self._open_write()

    def action_like_current(self) -> None:
        if self._posts and self.app.auth.token:
            post = self._posts[self._current_idx]
            self.app.api.like_actfile(post.get("id", ""), self.app.auth.token)
            self.query_one("#af-status").update("❤️  Liké !")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        bid = event.button.id
        if bid == "btn-back":
            self.action_back()
        elif bid == "btn-refresh":
            self.load_posts()
        elif bid == "btn-new":
            self._open_write()
        elif bid == "btn-publish":
            self._publish_post()
        elif bid == "btn-cancel-write":
            self._close_panels()
        elif bid == "btn-close-viewer":
            self._close_panels()
        elif bid == "btn-like-post":
            if self._current_post:
                self.app.api.like_actfile(
                    self._current_post.get("id", ""), self.app.auth.token
                )
                self.query_one("#af-status").update("❤️  Liké !")
        elif bid == "btn-send-comment":
            self._send_comment()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        item = event.item
        if hasattr(item, "post"):
            try:
                lv = self.query_one("#af-list", ListView)
                self._current_idx = lv.index or 0
            except Exception:
                pass
            self._current_post = item.post
            self._open_viewer(item.post)
            # increment view
            post_id = item.post.get("id")
            if post_id:
                try:
                    self.app.api.post(f"/api/actfile/{post_id}/view")
                except Exception:
                    pass

    def _open_viewer(self, post: dict) -> None:
        self._panel_mode = "view"
        try:
            self.query_one("#viewer-panel").styles.display = "block"
            self.query_one("#write-panel").styles.display = "none"
        except Exception:
            pass
        author = post.get("username", "?")
        verified = " ✅" if post.get("is_verified") else ""
        content = post.get("content", "")
        try:
            self.query_one("#viewer-author").update(f"@{author}{verified}")
            self.query_one("#viewer-markdown").update(content[:500])
        except Exception:
            pass

    def _open_write(self) -> None:
        self._panel_mode = "write"
        try:
            self.query_one("#write-panel").styles.display = "block"
            self.query_one("#viewer-panel").styles.display = "none"
            self.query_one("#post-editor").focus()
        except Exception:
            pass

    def _close_panels(self) -> None:
        self._panel_mode = None
        self._current_post = None
        try:
            self.query_one("#viewer-panel").styles.display = "none"
            self.query_one("#write-panel").styles.display = "none"
        except Exception:
            pass

    def _publish_post(self) -> None:
        try:
            editor = self.query_one("#post-editor", TextArea)
            content = editor.text.strip()
        except Exception:
            content = ""
        if not content:
            self.query_one("#af-status").update("⚠️  Contenu vide")
            return
        self.query_one("#af-status").update("📤  Publication...")
        try:
            result = self.app.api.create_actfile(content, self.app.auth.token)
            if result:
                self.query_one("#af-status").update("✅  Publié !")
                self._close_panels()
                self.load_posts()
            else:
                self.query_one("#af-status").update("❌  Erreur de publication")
        except Exception:
            self.query_one("#af-status").update("❌  Erreur réseau")

    def _send_comment(self) -> None:
        if not self._current_post:
            return
        try:
            inp = self.query_one("#comment-text", Input)
            text = inp.value.strip()
            if not text:
                return
            self.app.api.comment_actfile(
                self._current_post.get("id", ""), text, self.app.auth.token
            )
            inp.value = ""
            self.query_one("#af-status").update("✅  Commentaire envoyé !")
        except Exception:
            self.query_one("#af-status").update("❌  Erreur")

    def load_posts(self) -> None:
        lv = self.query_one("#af-list", ListView)
        lv.clear()
        self._posts = []
        self.query_one("#af-status").update("🔄  Chargement...")
        try:
            posts = self.app.api.get_actfiles(self.app.auth.token, limit=30) or []
            self._posts = posts
            if posts:
                for p in posts:
                    lv.append(PostCard(p))
                self.query_one("#af-status").update(f"✅  {len(posts)} posts")
            else:
                lv.append(ListItem(Static("  📭  Aucun post pour l'instant")))
                self.query_one("#af-status").update("📭  Vide")
        except Exception:
            self.query_one("#af-status").update("❌  Erreur réseau")
