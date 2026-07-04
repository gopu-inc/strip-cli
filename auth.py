# auth.py
"""Gestion de l'authentification"""

import requests
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

from config import Config
from theme import print_success, print_error, print_info

class Auth:
    """Gestionnaire d'authentification"""
    
    def __init__(self):
        self.config = Config()
        self.token = self.config.get_token()
        self.user_data = None
        self._expiry = None
        
    def is_authenticated(self) -> bool:
        """Vérifie si l'utilisateur est authentifié"""
        if not self.token:
            return False
        if self._expiry and datetime.now() > self._expiry:
            return False
        return True
    
    def login(self, username: str, password: str) -> bool:
        """Tente de se connecter"""
        try:
            response = requests.post(
                f"{self.config.get('api_url')}/api/token",
                data={"username": username, "password": password},
                timeout=self.config.get('timeout', 30)
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get('access_token')
                self.config.set_token(self.token)
                
                # Récupérer les infos utilisateur
                self._fetch_user_data()
                
                # Expiration (10080 min = 7 jours)
                self._expiry = datetime.now() + timedelta(minutes=10080)
                
                print_success(f"Connecté en tant que {self.user_data.get('username', username)}")
                return True
            else:
                print_error("Identifiants incorrects")
                return False
                
        except requests.exceptions.ConnectionError:
            print_error("Impossible de contacter le serveur")
            return False
        except Exception as e:
            print_error(f"Erreur: {str(e)}")
            return False
    
    def logout(self):
        """Se déconnecte"""
        self.token = None
        self.user_data = None
        self._expiry = None
        self.config.clear_token()
        print_info("Déconnecté")
    
    def _fetch_user_data(self):
        """Récupère les données de l'utilisateur"""
        if not self.token:
            return
        
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(
                f"{self.config.get('api_url')}/api/users/me",
                headers=headers,
                timeout=self.config.get('timeout', 30)
            )
            
            if response.status_code == 200:
                self.user_data = response.json()
        except:
            pass
    
    def get_headers(self) -> Dict[str, str]:
        """Retourne les headers d'authentification"""
        if self.token:
            return {"Authorization": f"Bearer {self.token}"}
        return {}
    
    def get_user_id(self) -> Optional[str]:
        """Retourne l'ID de l'utilisateur"""
        if self.user_data:
            return self.user_data.get('id')
        return None
    
    def get_username(self) -> Optional[str]:
        """Retourne le nom d'utilisateur"""
        if self.user_data:
            return self.user_data.get('username')
        return None
