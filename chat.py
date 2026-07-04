# chat.py
"""Gestion de la messagerie"""

from typing import Optional, List, Dict
from theme import console, print_header, print_success, print_error, print_info, create_table

class Chat:
    """Gestionnaire de messagerie"""
    
    def __init__(self, api, auth):
        self.api = api
        self.auth = auth
    
    def list_conversations(self) -> bool:
        """Liste les conversations"""
        token = self.auth.token
        if not token:
            print_error("Veuillez vous connecter d'abord")
            return False
        
        conversations = self.api.get("/api/messages/conversations", token=token)
        
        if not conversations:
            print_info("Aucune conversation")
            return True
        
        table = create_table("💬 Conversations", ["Utilisateur", "Dernier message", "Non lus", "En ligne"])
        for conv in conversations:
            table.add_row(
                conv.get('username', 'Inconnu'),
                conv.get('last_message', '')[:40],
                str(conv.get('unread_count', 0)),
                "🟢 Oui" if conv.get('is_online') else "🔴 Non"
            )
        
        console.print(table)
        return True
    
    def open(self, user_id: str) -> bool:
        """Ouvre une conversation"""
        token = self.auth.token
        if not token:
            print_error("Veuillez vous connecter d'abord")
            return False
        
        print_info(f"Conversation avec {user_id}")
        print_info("Tapez 'message <id> <texte>' pour envoyer un message")
        print_info("Tapez 'exit' pour quitter")
        
        messages = self.api.get(f"/api/messages/{user_id}?limit=20", token=token)
        
        if messages:
            print_header("Historique des messages")
            for msg in messages:
                sender = msg.get('sender_username', 'Inconnu')
                content = msg.get('content', '')
                print(f"  {sender}: {content}")
        
        return True
    
    def send(self, user_id: str, content: str) -> bool:
        """Envoie un message"""
        token = self.auth.token
        if not token:
            print_error("Veuillez vous connecter d'abord")
            return False
        
        data = self.api.post("/api/messages/send", 
                            data={"receiver_id": user_id, "content": content},
                            token=token)
        
        if data:
            print_success("✅ Message envoyé")
            return True
        
        return False
