# social.py
"""Gestion des fonctionnalités sociales"""

from typing import Optional, Dict, List
from theme import print_success, print_error, print_info, console, create_table

class Social:
    """Gestionnaire des fonctionnalités sociales"""
    
    def __init__(self, api, auth):
        self.api = api
        self.auth = auth
    
    def follow(self, user_id: str) -> bool:
        """Suivre un utilisateur"""
        if not self.auth.token:
            print_error("Veuillez vous connecter d'abord")
            return False
        
        result = self.api.follow_user(user_id, self.auth.token)
        if result:
            print_success(f"Vous suivez maintenant l'utilisateur {user_id}")
            return True
        return False
    
    def unfollow(self, user_id: str) -> bool:
        """Ne plus suivre un utilisateur"""
        if not self.auth.token:
            print_error("Veuillez vous connecter d'abord")
            return False
        
        # Utiliser la même API avec un toggle
        result = self.api.follow_user(user_id, self.auth.token)
        if result:
            print_success(f"Vous ne suivez plus l'utilisateur {user_id}")
            return True
        return False
    
    def get_followers(self, user_id: Optional[str] = None) -> bool:
        """Afficher les abonnés"""
        print_info("Fonctionnalité à implémenter")
        return True
    
    def get_following(self, user_id: Optional[str] = None) -> bool:
        """Afficher les abonnements"""
        print_info("Fonctionnalité à implémenter")
        return True
