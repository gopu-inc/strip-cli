# actfile.py
"""Gestion des ActFiles (publications Markdown)"""

from typing import Optional
from theme import console, print_header, print_success, print_error, print_info, create_table

class ActFile:
    """Gestionnaire des ActFiles"""
    
    def __init__(self, api, auth):
        self.api = api
        self.auth = auth
    
    def create(self, content: str) -> bool:
        """Publie un ActFile"""
        token = self.auth.token
        if not token:
            print_error("Veuillez vous connecter d'abord")
            return False
        
        data = self.api.post("/api/actfile", 
                            data={"content": content},
                            token=token)
        
        if data:
            print_success("✅ ActFile publié !")
            print_info(f"Contenu: {content[:100]}...")
            return True
        
        return False
    
    def list(self, limit: int = 20) -> bool:
        """Liste les ActFiles"""
        token = self.auth.token
        if not token:
            print_error("Veuillez vous connecter d'abord")
            return False
        
        posts = self.api.get(f"/api/actfile?limit={limit}", token=token)
        
        if not posts:
            print_info("Aucun ActFile trouvé")
            return True
        
        for post in posts:
            print_header("📝 ActFile")
            print(f"  Auteur: {post.get('username', 'Inconnu')}")
            print(f"  Contenu: {post.get('content', '')[:200]}...")
            print(f"  ❤️ {post.get('likes_count', 0)} | 👁️ {post.get('views_count', 0)}")
            print()
        
        return True
    
    def like(self, actfile_id: str) -> bool:
        """Like un ActFile"""
        token = self.auth.token
        if not token:
            print_error("Veuillez vous connecter d'abord")
            return False
        
        data = self.api.post(f"/api/actfile/{actfile_id}/like", token=token)
        
        if data:
            if data.get('liked'):
                print_success("✅ ActFile liké")
            else:
                print_info("ActFile unliké")
            return True
        
        return False
