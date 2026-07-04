# constants.py
"""Constantes globales du CLI"""

VERSION = "1.0.0"
APP_NAME = "STRIP"
APP_ICON = "🐬"

API_BASE_URL = "https://hoosthubs-g.onrender.com"
WS_BASE_URL = "wss://hoosthubs-g.onrender.com"

COLORS = {
    "primary": "#e94560",
    "secondary": "#4dabf7",
    "success": "#51cf66",
    "warning": "#f59f00",
    "danger": "#ff6b6b",
    "info": "#845ef7",
    "dark": "#0f0f1a",
    "darker": "#1a1a2e",
    "light": "#e0e0e0",
    "muted": "#888",
}

COMMANDS = {
    "login": "Se connecter",
    "logout": "Se déconnecter",
    "profile": "Voir/mettre à jour son profil",
    "feed": "Voir le fil d'actualité",
    "actfile": "Publier un ActFile (Markdown)",
    "upload": "Envoyer une vidéo",
    "download": "Télécharger une vidéo",
    "story": "Publier une story",
    "live": "Gérer les lives",
    "sound": "Gérer les sons",
    "remix": "Créer un remix audio",
    "chat": "Ouvrir la messagerie",
    "message": "Envoyer un message",
    "notification": "Voir les notifications",
    "follow": "Suivre un utilisateur",
    "unfollow": "Ne plus suivre",
    "search": "Rechercher",
    "explore": "Explorer le contenu",
    "trends": "Voir les tendances",
    "verify": "Demander la vérification",
    "settings": "Paramètres",
    "config": "Configurer le CLI",
    "plugins": "Gérer les plugins",
    "doctor": "Diagnostiquer",
    "update": "Mettre à jour",
    "cache": "Gérer le cache",
    "history": "Voir l'historique",
    "clear": "Effacer l'écran",
    "help": "Afficher l'aide",
    "exit": "Quitter",
}
