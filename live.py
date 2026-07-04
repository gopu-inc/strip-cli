# live.py
"""Gestion des lives"""

from typing import Optional, List, Dict
from theme import console, print_header, print_success, print_error, print_info, create_table

class Live:
    """Gestionnaire des lives"""
    
    def __init__(self, api, auth):
        self.api = api
        self.auth = auth
    
    def list_active(self) -> bool:
        """Liste les lives actifs"""
        token = self.auth.token
        if not token:
            print_error("Veuillez vous connecter d'abord")
            return False
        
        lives = self.api.get_active_lives(token)
        
        if not lives:
            print_info("Aucun live actif pour le moment")
            return True
        
        table = create_table("🔴 Lives actifs", ["Streamer", "Titre", "Spectateurs", "Statut"])
        for live in lives:
            table.add_row(
                live.get('username', 'Inconnu'),
                live.get('title', 'Sans titre')[:30],
                str(live.get('viewer_count', 0)),
                "🔴 En direct" if live.get('is_live') else "⏹ Arrêté"
            )
        
        console.print(table)
        return True
    
    def start(self, title: str = "Live STRIP") -> bool:
        """Démarre un live"""
        token = self.auth.token
        if not token:
            print_error("Veuillez vous connecter d'abord")
            return False
        
        print_info(f"Démarrage du live: {title}")
        
        data = self.api.post("/api/lives/start", 
                            data={"title": title, "description": "", "is_private": False},
                            token=token)
        
        if data:
            print_success(f"✅ Live démarré !")
            print_info(f"Stream Key: {data.get('stream_key', 'N/A')}")
            print_info(f"RTMP URL: {data.get('rtmp_url', 'N/A')}")
            print_info("Configurez OBS avec ces informations")
            return True
        
        return False
    
    def stop(self) -> bool:
        """Arrête un live"""
        token = self.auth.token
        if not token:
            print_error("Veuillez vous connecter d'abord")
            return False
        
        # Récupérer le live actif de l'utilisateur
        lives = self.api.get_active_lives(token)
        
        if not lives:
            print_info("Aucun live actif à arrêter")
            return True
        
        # Trouver le live de l'utilisateur
        user_id = self.auth.get_user_id()
        my_live = None
        
        for live in lives:
            if live.get('user_id') == user_id:
                my_live = live
                break
        
        if not my_live:
            print_error("Vous n'avez pas de live en cours")
            return False
        
        live_id = my_live.get('id')
        data = self.api.post(f"/api/lives/{live_id}/stop", token=token)
        
        if data:
            print_success("✅ Live arrêté")
            return True
        
        return False
    
    def watch(self, live_id: str) -> bool:
        """Regarde un live"""
        print_info(f"Connexion au live {live_id}...")
        # Ici on pourrait ouvrir un player ou afficher le stream
        print_info("Fonctionnalité de visionnage à implémenter")
        return True
