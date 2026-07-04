# screens/chat.py
"""Messagerie améliorée avec recherche d'amis, messages vocaux et écran responsive"""

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import (
    Label, Static, Button, ListView, ListItem, 
    Input
)
from textual.containers import Horizontal, Vertical, Container
from textual import events
from rich.text import Text
import time
import base64
from pathlib import Path

class ChatUserItem(ListItem):
    """Élément utilisateur dans la liste des amis"""
    
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.username = user_data.get('username', 'Inconnu')
        self.is_online = user_data.get('is_online', False)
        self.is_verified = user_data.get('is_verified', False)
        self.last_message = user_data.get('last_message', '')
        self.unread = user_data.get('unread_count', 0)
    
    def render(self) -> Text:
        status = "🟢" if self.is_online else "🔴"
        verified = "✅" if self.is_verified else ""
        unread = f" [{self.unread}]" if self.unread > 0 else ""
        msg = self.last_message[:30] + "..." if len(self.last_message) > 30 else self.last_message
        
        return Text(f"{status} {verified} {self.username}{unread}\n  {msg}")

class MessageItem(ListItem):
    """Élément message dans la conversation"""
    
    def __init__(self, message_data, is_mine=False):
        super().__init__()
        self.message_data = message_data
        self.is_mine = is_mine
        self.content = message_data.get('content', '')
        self.sender = message_data.get('sender_username', 'Inconnu')
        self.created_at = message_data.get('created_at', '')
        self.msg_type = message_data.get('type', 'text')
    
    def render(self) -> Text:
        align = "→" if self.is_mine else "←"
        color = "green" if self.is_mine else "blue"
        msg_type_icon = "🎤" if self.msg_type == "audio" else "✍️"
        
        return Text(f"{align} {self.sender}: {msg_type_icon} {self.content[:50]}", style=color)

class ChatScreen(Screen):
    """Écran de messagerie amélioré"""
    
    CSS = """
    ChatScreen {
        background: $surface;
    }
    
    #chat-header {
        height: 3;
        border-bottom: solid $primary;
        padding: 0 1;
        background: $panel;
    }
    
    #chat-header > Label {
        text-style: bold;
    }
    
    #chat-body {
        height: 1fr;
        padding: 0;
    }
    
    #friends-panel {
        width: 35;
        border-right: solid $secondary;
        background: $panel;
        overflow-y: auto;
    }
    
    #friends-panel > Input {
        margin: 1;
    }
    
    #friends-list {
        height: 1fr;
        margin: 0 1;
    }
    
    #friends-list ListItem {
        padding: 1;
        border-bottom: solid $panel;
    }
    
    #friends-list ListItem:hover {
        background: $primary-darken-1;
    }
    
    #chat-panel {
        width: 1fr;
        background: $surface;
    }
    
    #chat-messages {
        height: 1fr;
        margin: 0 1;
        border: solid $secondary;
        padding: 1;
        overflow-y: auto;
    }
    
    #chat-messages ListItem {
        padding: 1;
        border-bottom: solid $panel;
    }
    
    #chat-input-area {
        height: 5;
        margin: 1;
        border-top: solid $secondary;
        padding: 1;
    }
    
    #chat-input-area > Input {
        width: 1fr;
        margin: 0 1;
    }
    
    #chat-input-area > Button {
        width: 15;
        margin: 0 1;
    }
    
    #voice-recording {
        height: 3;
        margin: 1;
        background: $error-darken-1;
        padding: 1;
        text-align: center;
        display: none;
    }
    
    #chat-actions {
        height: 3;
        padding: 0 1;
    }
    
    #chat-actions > Button {
        margin: 0 1;
        width: 15;
    }
    
    .status-bar {
        color: $text-muted;
        text-align: right;
        padding: 0 1;
    }
    
    #current-chat-label {
        text-style: bold;
        color: $primary;
        padding: 0 1;
        height: 3;
    }
    """
    
    def __init__(self):
        super().__init__()
        self.current_chat = None
        self.friends = []
        self.messages = []
        self.is_recording = False
        self.audio_file = None
        self.recording_timer = 0
    
    def compose(self) -> ComposeResult:
        """Composition du chat amélioré"""
        # Header
        with Horizontal(id="chat-header"):
            yield Label("💬 Messagerie")
            yield Label("", id="chat-status", classes="status-bar")
        
        # Body
        with Horizontal(id="chat-body"):
            # Panneau des amis
            with Vertical(id="friends-panel"):
                yield Label("👥 Mes contacts", classes="subtitle")
                yield Input(placeholder="🔍 Rechercher un ami...", id="search-friends")
                yield ListView(id="friends-list")
            
            # Panneau de chat
            with Vertical(id="chat-panel"):
                yield Label("", id="current-chat-label")
                with Container(id="chat-messages"):
                    yield ListView(id="messages-list")
                
                # Zone d'enregistrement vocal
                with Container(id="voice-recording"):
                    yield Label("🎤 Enregistrement en cours...", id="recording-status")
                    yield Button("⏹ Arrêter", id="stop-recording", variant="error")
                
                # Zone de saisie
                with Horizontal(id="chat-input-area"):
                    yield Input(placeholder="Tapez votre message...", id="message-input")
                    yield Button("🎤", id="voice-record", variant="warning")
                    yield Button("📤 Envoyer", id="send-message", variant="primary")
        
        # Actions
        with Horizontal(id="chat-actions"):
            yield Button("🔄 Rafraîchir", id="refresh-chat")
            yield Button("🔙 Retour", id="back-dashboard", variant="primary")
    
    def on_mount(self) -> None:
        """Chargement au montage"""
        self.load_friends()
        self.query_one("#search-friends").focus()
    
    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Soumission d'un champ input"""
        if event.input.id == "search-friends":
            self.search_friends(event.input.value)
        elif event.input.id == "message-input":
            self.send_message()
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Clic sur un bouton"""
        btn_id = event.button.id
        
        if btn_id == "refresh-chat":
            self.load_friends()
            if self.current_chat:
                self.load_messages(self.current_chat)
        elif btn_id == "back-dashboard":
            self.app.pop_screen()
        elif btn_id == "send-message":
            self.send_message()
        elif btn_id == "voice-record":
            self.toggle_recording()
        elif btn_id == "stop-recording":
            self.stop_recording()
    
    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Sélection d'un ami"""
        item = event.item
        if hasattr(item, 'user_data'):
            user_id = item.user_data.get('id')
            username = item.user_data.get('username')
            self.current_chat = user_id
            self.query_one("#current-chat-label").update(f"💬 Conversation avec {username}")
            self.load_messages(user_id)
            self.query_one("#message-input").focus()
    
    def load_friends(self) -> None:
        """Charge la liste des amis"""
        self.query_one("#friends-list").clear()
        self.query_one("#chat-status").update("🔄 Chargement des contacts...")
        
        try:
            conversations = self.app.api.get("/api/messages/conversations", 
                                           token=self.app.auth.token)
            
            if conversations:
                list_view = self.query_one("#friends-list")
                for conv in conversations:
                    item = ChatUserItem(conv)
                    list_view.append(item)
                    self.friends.append(conv)
                self.query_one("#chat-status").update(f"✅ {len(conversations)} contacts")
            else:
                self.query_one("#chat-status").update("📭 Aucun contact")
                
        except Exception as e:
            self.query_one("#chat-status").update(f"❌ Erreur: {e}")
    
    def search_friends(self, query: str) -> None:
        """Recherche d'amis"""
        if not query or len(query) < 2:
            self.load_friends()
            return
        
        self.query_one("#friends-list").clear()
        self.query_one("#chat-status").update(f"🔍 Recherche: {query}")
        
        try:
            results = self.app.api.search(query, token=self.app.auth.token)
            
            if results and results.get('results'):
                list_view = self.query_one("#friends-list")
                for user in results['results'][:20]:
                    item = ChatUserItem(user)
                    list_view.append(item)
                self.query_one("#chat-status").update(f"✅ {len(results['results'])} résultats")
            else:
                self.query_one("#chat-status").update("❌ Aucun résultat")
                
        except Exception as e:
            self.query_one("#chat-status").update(f"❌ Erreur: {e}")
    
    def load_messages(self, user_id: str) -> None:
        """Charge les messages d'une conversation"""
        self.query_one("#messages-list").clear()
        self.query_one("#chat-status").update("🔄 Chargement des messages...")
        
        try:
            messages = self.app.api.get(f"/api/messages/{user_id}?limit=50", 
                                      token=self.app.auth.token)
            
            if messages:
                list_view = self.query_one("#messages-list")
                current_user_id = self.app.auth.get_user_id()
                
                for msg in messages:
                    is_mine = msg.get('sender_id') == current_user_id
                    item = MessageItem(msg, is_mine)
                    list_view.append(item)
                
                self.query_one("#chat-status").update(f"✅ {len(messages)} messages")
                list_view.scroll_end()
            else:
                self.query_one("#chat-status").update("📭 Aucun message")
                
        except Exception as e:
            self.query_one("#chat-status").update(f"❌ Erreur: {e}")
    
    def send_message(self) -> None:
        """Envoie un message"""
        if not self.current_chat:
            self.query_one("#chat-status").update("⚠️ Sélectionnez un contact")
            return
        
        input_widget = self.query_one("#message-input")
        message = input_widget.value.strip()
        
        if not message:
            return
        
        self.query_one("#chat-status").update("📤 Envoi en cours...")
        
        try:
            result = self.app.api.post("/api/messages/send",
                                     data={
                                         "receiver_id": self.current_chat,
                                         "content": message
                                     },
                                     token=self.app.auth.token)
            
            if result:
                input_widget.value = ""
                self.query_one("#chat-status").update("✅ Message envoyé")
                self.load_messages(self.current_chat)
            else:
                self.query_one("#chat-status").update("❌ Échec de l'envoi")
                
        except Exception as e:
            self.query_one("#chat-status").update(f"❌ Erreur: {e}")
    
    def toggle_recording(self) -> None:
        """Active/désactive l'enregistrement vocal"""
        if not self.current_chat:
            self.query_one("#chat-status").update("⚠️ Sélectionnez un contact")
            return
        
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()
    
    def start_recording(self) -> None:
        """Démarre l'enregistrement vocal"""
        self.is_recording = True
        self.query_one("#voice-recording").styles.display = "block"
        self.query_one("#recording-status").update("🎤 Enregistrement en cours...")
        self.query_one("#chat-status").update("🔴 Enregistrement vocal...")
        
        self.audio_file = Path("/tmp/voice_message.wav")
        self.audio_file.touch()
        self.recording_timer = 0
        
        def update_recording():
            if self.is_recording:
                self.recording_timer += 1
                self.query_one("#recording-status").update(f"🎤 Enregistrement... {self.recording_timer}s")
                self.set_timer(1, update_recording)
        
        self.set_timer(1, update_recording)
    
    def stop_recording(self) -> None:
        """Arrête l'enregistrement vocal"""
        self.is_recording = False
        self.query_one("#voice-recording").styles.display = "none"
        self.query_one("#chat-status").update("⏹ Enregistrement terminé")
        
        if self.audio_file and self.audio_file.exists():
            self.send_voice_message()
    
    def send_voice_message(self) -> None:
        """Envoie un message vocal"""
        if not self.current_chat:
            return
        
        self.query_one("#chat-status").update("📤 Envoi du vocal...")
        
        try:
            if self.audio_file and self.audio_file.exists():
                with open(self.audio_file, 'rb') as f:
                    audio_data = base64.b64encode(f.read()).decode()
                
                self.app.api.post("/api/messages/send",
                                data={
                                    "receiver_id": self.current_chat,
                                    "content": "[Message vocal]",
                                    "type": "audio"
                                },
                                token=self.app.auth.token)
                
                self.query_one("#chat-status").update("✅ Vocal envoyé")
                self.load_messages(self.current_chat)
                
                if self.audio_file and self.audio_file.exists():
                    self.audio_file.unlink()
                self.audio_file = None
                
        except Exception as e:
            self.query_one("#chat-status").update(f"❌ Erreur vocal: {e}")
    
    def on_key(self, event: events.Key) -> None:
        """Gestion des touches rapides"""
        if event.key == "escape":
            self.app.pop_screen()
        elif event.key == "enter" and self.query_one("#message-input").has_focus:
            self.send_message()
        elif event.key == "ctrl+r":
            self.load_friends()
            if self.current_chat:
                self.load_messages(self.current_chat)
