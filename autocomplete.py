# autocomplete.py
"""Auto-complétion intelligente avec NLTK"""

from typing import List, Optional, Set
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Télécharger les ressources NLTK si nécessaires
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')

class AutoCompleter:
    """Gestionnaire d'auto-complétion avec NLTK"""
    
    def __init__(self):
        self.commands = [
            'login', 'logout', 'profile', 'feed', 'actfile', 'upload',
            'download', 'story', 'live', 'sound', 'remix', 'chat',
            'message', 'notification', 'follow', 'unfollow', 'search',
            'explore', 'trends', 'verify', 'settings', 'config',
            'plugins', 'doctor', 'update', 'cache', 'history',
            'clear', 'help', 'exit'
        ]
        
        # Charger les stopwords français
        try:
            self.stop_words = set(stopwords.words('french'))
        except:
            self.stop_words = set()
        
        # Fréquence d'utilisation des commandes
        self.command_frequency = {cmd: 0 for cmd in self.commands}
        self.history = []
    
    def get_suggestions(self, text: str) -> List[str]:
        """
        Retourne les suggestions pour le texte donné
        Utilise NLTK pour l'analyse sémantique
        """
        if not text:
            return self.commands[:10]
        
        text_lower = text.lower()
        suggestions = []
        
        # 1. Suggestions basées sur les commandes exactes
        for cmd in self.commands:
            if cmd.startswith(text_lower):
                suggestions.append(cmd)
        
        # 2. Suggestions basées sur NLTK (si la recherche est plus longue)
        if len(text_lower) > 3 and not suggestions:
            # Tokeniser et analyser
            try:
                tokens = word_tokenize(text_lower, language='french')
                # Filtrer les stopwords
                filtered_tokens = [t for t in tokens if t not in self.stop_words]
                
                for token in filtered_tokens:
                    for cmd in self.commands:
                        if token in cmd and cmd not in suggestions:
                            suggestions.append(cmd)
            except:
                pass
        
        # 3. Suggestions basées sur la fréquence d'utilisation
        # Trier par fréquence d'utilisation
        if suggestions:
            suggestions.sort(key=lambda x: self.command_frequency.get(x, 0), reverse=True)
        
        return suggestions[:10]
    
    def get_command_description(self, cmd: str) -> Optional[str]:
        """Retourne la description d'une commande"""
        descriptions = {
            'login': 'Se connecter à STRIP',
            'logout': 'Se déconnecter de STRIP',
            'profile': 'Voir ou modifier son profil utilisateur',
            'feed': 'Voir le fil d\'actualité (vidéos)',
            'actfile': 'Publier un ActFile (publication Markdown)',
            'upload': 'Uploader une vidéo sur STRIP',
            'download': 'Télécharger une vidéo depuis STRIP',
            'story': 'Publier une story (image/vidéo)',
            'live': 'Gérer les lives (start/stop/list)',
            'sound': 'Gérer les sons audio',
            'remix': 'Créer un remix audio',
            'chat': 'Ouvrir la messagerie',
            'message': 'Envoyer un message à un utilisateur',
            'notification': 'Voir les notifications',
            'follow': 'Suivre un utilisateur',
            'unfollow': 'Ne plus suivre un utilisateur',
            'search': 'Rechercher des utilisateurs ou contenus',
            'explore': 'Explorer le contenu tendance',
            'trends': 'Voir les tendances du moment',
            'verify': 'Demander la vérification du compte',
            'settings': 'Afficher ou modifier les paramètres',
            'config': 'Configurer le CLI',
            'plugins': 'Gérer les plugins du CLI',
            'doctor': 'Diagnostiquer la connexion et l\'état',
            'update': 'Mettre à jour le CLI',
            'cache': 'Gérer le cache local',
            'history': 'Voir l\'historique des commandes',
            'clear': 'Effacer l\'écran du terminal',
            'help': 'Afficher l\'aide',
            'exit': 'Quitter STRIP CLI'
        }
        return descriptions.get(cmd, None)
    
    def record_command(self, cmd: str):
        """Enregistre l'utilisation d'une commande pour l'apprentissage"""
        if cmd in self.command_frequency:
            self.command_frequency[cmd] += 1
        self.history.append(cmd)
    
    def get_most_used(self, limit: int = 5) -> List[str]:
        """Retourne les commandes les plus utilisées"""
        sorted_cmds = sorted(
            self.command_frequency.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return [cmd for cmd, _ in sorted_cmds[:limit]]
    
    def get_nltk_suggestions(self, text: str) -> List[str]:
        """
        Suggestions basées sur NLTK pour des requêtes en langage naturel
        Ex: "poster une video" -> "upload"
        """
        try:
            tokens = word_tokenize(text.lower(), language='french')
            filtered = [t for t in tokens if t not in self.stop_words and t.isalnum()]
            
            # Mapping sémantique simple
            semantic_map = {
                'post': 'actfile',
                'publier': 'actfile',
                'envoyer': 'upload',
                'upload': 'upload',
                'video': 'upload',
                'regarder': 'feed',
                'voir': 'feed',
                'suivre': 'follow',
                'abonner': 'follow',
                'parler': 'chat',
                'message': 'message',
                'live': 'live',
                'stream': 'live',
                'rechercher': 'search',
                'trouver': 'search',
                'son': 'sound',
                'musique': 'sound',
                'remix': 'remix',
                'profil': 'profile',
                'compte': 'profile'
            }
            
            suggestions = []
            for token in filtered:
                if token in semantic_map:
                    suggestions.append(semantic_map[token])
            
            return list(set(suggestions))[:5]
        except:
            return []
