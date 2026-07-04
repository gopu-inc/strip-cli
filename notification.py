# notification.py
"""Gestion des notifications"""

from theme import console, print_header, print_success, print_error, print_info, create_table

class Notification:
    """Gestionnaire de notifications"""
    
    def __init__(self, api, auth):
        self.api = api
        self.auth = auth
    
    def list(self, limit: int = 20) -> bool:
        """Liste les notifications"""
        token = self.auth.token
        if not token:
            print_error("Veuillez vous connecter d'abord")
            return False
        
        notifications = self.api.get_notifications(token, limit)
        
        if not notifications:
            print_info("Aucune notification")
            return True
        
        table = create_table("🔔 Notifications", ["Type", "Message", "Date"])
        for notif in notifications:
            table.add_row(
                notif.get('type', ''),
                notif.get('message', '')[:40],
                notif.get('created_at', '')[:16]
            )
        
        console.print(table)
        return True
    
    def mark_read(self, notification_id: str) -> bool:
        """Marque une notification comme lue"""
        # À implémenter côté API
        print_info("Fonctionnalité à implémenter")
        return True
    
    def clear(self) -> bool:
        """Efface toutes les notifications"""
        # À implémenter côté API
        print_info("Fonctionnalité à implémenter")
        return True
