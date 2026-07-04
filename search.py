# search.py
"""Recherche et exploration"""

from typing import Optional, List, Dict
from theme import console, print_header, print_success, print_error, print_info, create_table

class Search:
    """Gestionnaire de recherche"""
    
    def __init__(self, api, auth):
        self.api = api
        self.auth = auth
    
    def search(self, query: str) -> bool:
        """Recherche des utilisateurs"""
        token = self.auth.token
        if not token:
            print_error("Veuillez vous connecter d'abord")
            return False
        
        print_info(f"Recherche de '{query}'...")
        data = self.api.search(query, token)
        
        if not data:
            print_info("Aucun résultat trouvé")
            return True
        
        results = data.get('results', [])
        
        if not results:
            print_info("Aucun résultat trouvé")
            return True
        
        table = create_table(f"🔍 Résultats pour '{query}'", ["Utilisateur", "Bio", "Vérifié"])
        for user in results:
            table.add_row(
                user.get('username', 'Inconnu'),
                user.get('bio', '')[:30],
                "✅" if user.get('is_verified') else "❌"
            )
        
        console.print(table)
        return True
    
    def explore(self) -> bool:
        """Explore le contenu"""
        token = self.auth.token
        if not token:
            print_error("Veuillez vous connecter d'abord")
            return False
        
        print_header("🌍 EXPLORER")
        
        # Récupérer le feed
        videos = self.api.get_feed(token, 10)
        
        if videos:
            print_info("📹 Vidéos tendances:")
            for i, video in enumerate(videos[:5], 1):
                print(f"  {i}. {video.get('username')}: {video.get('description', '')[:40]}...")
        
        # Récupérer les lives actifs
        lives = self.api.get_active_lives(token)
        
        if lives:
            print_info("🔴 Lives actifs:")
            for live in lives[:3]:
                print(f"  - {live.get('username')}: {live.get('title', 'Sans titre')}")
        
        return True
    
    def trends(self) -> bool:
        """Affiche les tendances"""
        token = self.auth.token
        if not token:
            print_error("Veuillez vous connecter d'abord")
            return False
        
        print_header("🔥 TENDANCES")
        
        # Récupérer le feed pour analyser les tendances
        videos = self.api.get_feed(token, 20)
        
        if videos:
            # Simuler des tendances
            print_info("📈 Vidéos populaires:")
            
            # Trier par likes
            sorted_videos = sorted(videos, key=lambda x: x.get('likes', 0), reverse=True)
            
            for i, video in enumerate(sorted_videos[:5], 1):
                likes = video.get('likes', 0)
                username = video.get('username', 'Inconnu')
                desc = video.get('description', '')[:30]
                print(f"  #{i} 🔥 {likes} likes - {username}: {desc}")
        
        # Suggestions de sons populaires (simulé)
        print_info("🎵 Sons populaires:")
        popular_sounds = [
            "Afro Beat 2024",
            "Amapiano Summer",
            "Rumba Gold",
            "Gospel Choir",
            "Electro Wave"
        ]
        for sound in popular_sounds:
            print(f"  🎵 {sound}")
        
        return True
