# api.py
"""Client HTTP pour l'API"""

import requests
from typing import Optional, Dict, Any, List
from pathlib import Path

from config import Config
from theme import print_error

class APIClient:
    """Client HTTP pour l'API STRIP"""
    
    def __init__(self):
        self.config = Config()
        self.base_url = self.config.get('api_url')
        self.timeout = self.config.get('timeout', 30)
    
    def _request(self, method: str, endpoint: str, 
                 data: Optional[Dict] = None,
                 files: Optional[Dict] = None,
                 headers: Optional[Dict] = None,
                 token: Optional[str] = None) -> Optional[Dict]:
        """Effectue une requête HTTP"""
        url = f"{self.base_url}{endpoint}"
        headers = headers or {}
        
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        try:
            if method == "GET":
                response = requests.get(url, headers=headers, timeout=self.timeout)
            elif method == "POST":
                if files:
                    response = requests.post(url, data=data, files=files, 
                                           headers=headers, timeout=self.timeout)
                else:
                    response = requests.post(url, json=data, headers=headers, 
                                           timeout=self.timeout)
            elif method == "PUT":
                response = requests.put(url, json=data, headers=headers, 
                                      timeout=self.timeout)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers, timeout=self.timeout)
            else:
                return None
            
            if response.status_code in [200, 201]:
                return response.json() if response.content else {}
            else:
                error = response.json().get('detail', f"Erreur {response.status_code}")
                print_error(error)
                return None
                
        except requests.exceptions.ConnectionError:
            print_error("Impossible de contacter le serveur")
            return None
        except requests.exceptions.Timeout:
            print_error("Délai d'attente dépassé")
            return None
        except Exception as e:
            print_error(f"Erreur: {str(e)}")
            return None
    
    def get(self, endpoint: str, token: Optional[str] = None) -> Optional[Dict]:
        """Requête GET"""
        return self._request("GET", endpoint, token=token)
    
    def post(self, endpoint: str, data: Optional[Dict] = None,
             files: Optional[Dict] = None,
             token: Optional[str] = None) -> Optional[Dict]:
        """Requête POST"""
        return self._request("POST", endpoint, data=data, files=files, token=token)
    
    def put(self, endpoint: str, data: Optional[Dict] = None,
            token: Optional[str] = None) -> Optional[Dict]:
        """Requête PUT"""
        return self._request("PUT", endpoint, data=data, token=token)
    
    def delete(self, endpoint: str, token: Optional[str] = None) -> Optional[Dict]:
        """Requête DELETE"""
        return self._request("DELETE", endpoint, token=token)
    
    # Endpoints spécifiques
    
    def get_feed(self, token: str, limit: int = 10) -> Optional[List[Dict]]:
        """Récupère le feed"""
        return self.get(f"/api/feed?limit={limit}", token=token)
    
    def get_user_profile(self, user_id: str, token: Optional[str] = None) -> Optional[Dict]:
        """Récupère le profil d'un utilisateur"""
        return self.get(f"/api/users/{user_id}", token=token)
    
    def get_my_profile(self, token: str) -> Optional[Dict]:
        """Récupère son propre profil"""
        return self.get("/api/users/me", token=token)
    
    def follow_user(self, user_id: str, token: str) -> Optional[Dict]:
        """Suit un utilisateur"""
        return self.post(f"/api/users/{user_id}/follow", token=token)
    
    def get_notifications(self, token: str, limit: int = 20) -> Optional[List[Dict]]:
        """Récupère les notifications"""
        return self.get(f"/api/notifications?limit={limit}", token=token)
    
    def get_active_lives(self, token: Optional[str] = None) -> Optional[List[Dict]]:
        """Récupère les lives actifs"""
        return self.get("/api/lives/active", token=token)
    
    def search(self, query: str, token: Optional[str] = None) -> Optional[Dict]:
        """Recherche"""
        return self.get(f"/api/search?q={query}&type=users", token=token)
    
    def upload_video(self, file_path: str, description: str, 
                     is_public: bool = True, token: str = None) -> Optional[Dict]:
        """Upload une vidéo"""
        if not Path(file_path).exists():
            print_error(f"Fichier introuvable: {file_path}")
            return None
        
        with open(file_path, 'rb') as f:
            files = {'video': f}
            data = {'description': description, 'is_public': str(is_public).lower()}
            return self.post("/api/videos/upload", data=data, files=files, token=token)
