# account.py
"""Gestion du compte utilisateur"""

from pathlib import Path
from theme import print_success, print_error, print_info

class Account:
    """Gestionnaire du compte"""
    
    def __init__(self, api, auth):
        self.api = api
        self.auth = auth
    
    def upload_video(self, file_path: str, description: str = "") -> bool:
        """Upload une vidéo"""
        if not Path(file_path).exists():
            print_error(f"Fichier introuvable: {file_path}")
            return False
        
        token = self.auth.token
        if not token:
            print_error("Veuillez vous connecter d'abord")
            return False
        
        print_info(f"Upload de {file_path}...")
        
        result = self.api.upload_video(file_path, description, True, token)
        
        if result:
            print_success("✅ Vidéo uploadée avec succès !")
            print_info(f"URL: {result.get('video_url', 'N/A')}")
            return True
        
        return False
    
    def verify(self) -> bool:
        """Demande la vérification"""
        token = self.auth.token
        if not token:
            print_error("Veuillez vous connecter d'abord")
            return False
        
        print_info("Demande de vérification...")
        print_info("Veuillez fournir votre date de naissance (YYYY-MM-DD)")
        
        birth_date = input("Date de naissance: ")
        
        data = self.api.post("/api/users/me/verify", 
                            data={"birth_date": birth_date},
                            token=token)
        
        if data:
            if data.get('verified'):
                print_success("✅ Vous êtes maintenant vérifié !")
                print_info(f"Signe astrologique: {data.get('zodiac_sign', 'Inconnu')}")
            else:
                print_error(f"❌ Vérification échouée: {data.get('reason', '')}")
            return True
        
        return False
    
    def update_profile(self, bio: str = None, phone: str = None) -> bool:
        """Met à jour le profil"""
        token = self.auth.token
        if not token:
            print_error("Veuillez vous connecter d'abord")
            return False
        
        data = {}
        if bio:
            data['bio'] = bio
        if phone:
            data['phone_number'] = phone
        
        if not data:
            print_info("Aucune modification à apporter")
            return True
        
        result = self.api.put("/api/users/me", data=data, token=token)
        
        if result:
            print_success("✅ Profil mis à jour")
            return True
        
        return False
