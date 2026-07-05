# screens/login.py
"""Écran de connexion STRIP — style 2026"""

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Label, Input, Button, Static, LoadingIndicator
from textual.containers import Vertical, Center, Container, Horizontal
from textual import events
from textual.reactive import reactive

LOGO = """\
 ░██████╗████████╗██████╗ ██╗██████╗ 
 ██╔════╝╚══██╔══╝██╔══██╗██║██╔══██╗
 ╚█████╗    ██║   ██████╔╝██║██████╔╝
  ╚═══██╗   ██║   ██╔══██╗██║██╔═══╝ 
 ██████╔╝   ██║   ██║  ██║██║██║     
 ╚═════╝    ╚═╝   ╚═╝  ╚═╝╚═╝╚═╝     """

TAGLINE = "🐬  La plateforme de streaming TUI #1  🐬"


class LoginScreen(Screen):
    """Écran de connexion"""

    CSS = """
    LoginScreen {
        align: center middle;
        background: $background;
    }

    #wrap {
        width: 60;
        height: auto;
    }

    #logo-box {
        text-align: center;
        padding: 1 2;
    }

    #logo-text {
        color: #e94560;
        text-style: bold;
        text-align: center;
    }

    #tagline {
        color: #555577;
        text-align: center;
        padding: 0 0 1 0;
    }

    #login-box {
        border: solid #e94560;
        padding: 2 3;
        background: #13131f;
        margin: 1 0;
    }

    #login-box Label {
        color: #888;
        margin-bottom: 0;
    }

    #login-box Input {
        margin-bottom: 1;
    }

    #login-btn {
        width: 100%;
        margin-top: 1;
    }

    #register-link {
        text-align: center;
        color: #555577;
        padding: 1 0;
    }

    #msg-error {
        color: #ff6b6b;
        text-align: center;
        height: 2;
    }

    #msg-ok {
        color: #51cf66;
        text-align: center;
        height: 2;
    }

    #loading-box {
        align: center middle;
        height: 3;
        display: none;
    }
    """

    loading: reactive[bool] = reactive(False)

    def compose(self) -> ComposeResult:
        with Container(id="wrap"):
            with Container(id="logo-box"):
                yield Static(LOGO, id="logo-text")
                yield Static(TAGLINE, id="tagline")

            with Container(id="login-box"):
                yield Label("👤 Nom d'utilisateur")
                yield Input(
                    placeholder="ex: @dolphin_user",
                    id="username",
                    name="username",
                )
                yield Label("🔒 Mot de passe")
                yield Input(
                    placeholder="••••••••",
                    id="password",
                    password=True,
                    name="password",
                )
                yield Static("", id="msg-error")
                yield Static("", id="msg-ok")

                with Container(id="loading-box"):
                    yield LoadingIndicator()
                    yield Label(" Connexion...")

                yield Button("🚀  Se connecter", id="login-btn", variant="primary")

            yield Static(
                "Ctrl+Q pour quitter", id="register-link"
            )

    def on_mount(self) -> None:
        self.query_one("#username").focus()

    def watch_loading(self, loading: bool) -> None:
        self.query_one("#loading-box").styles.display = "block" if loading else "none"
        self.query_one("#login-btn").disabled = loading

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "username":
            self.query_one("#password").focus()
        elif event.input.id == "password":
            self.do_login()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "login-btn":
            self.do_login()

    def on_key(self, event: events.Key) -> None:
        if event.key == "escape":
            self.app.exit()

    def do_login(self) -> None:
        username = self.query_one("#username").value.strip()
        password = self.query_one("#password").value

        if not username or not password:
            self.query_one("#msg-error").update("⚠️  Remplissez tous les champs")
            return

        self.query_one("#msg-error").update("")
        self.query_one("#msg-ok").update("🔄  Connexion en cours...")
        self.loading = True

        success = self.app.auth.login(username, password)
        self.loading = False

        if success:
            self.app.current_user = self.app.auth.user_data
            # refresh full profile data
            try:
                profile = self.app.api.get_my_profile(self.app.auth.token)
                if profile:
                    self.app.current_user = profile
                    self.app.auth.user_data = profile
            except Exception:
                pass
            self.query_one("#msg-ok").update("✅  Connexion réussie !")
            self.app.push_screen("dashboard")
        else:
            self.query_one("#msg-ok").update("")
            self.query_one("#msg-error").update("❌  Identifiants incorrects")
            self.query_one("#password").value = ""
            self.query_one("#username").focus()
