# commands.py
"""Commandes disponibles"""

import sys
import os
from typing import Optional, List, Dict
from datetime import datetime

from theme import console, print_header, print_success, print_error, print_info, print_warning, create_table
from auth import Auth
from api import APIClient
from config import Config
from social import Social
from live import Live
from chat import Chat
from actfile import ActFile
from search import Search
from notification import Notification
from account import Account

class Commands:
    """Gestionnaire de commandes"""
    
    def __init__(self):
        self.auth = Auth()
        self.api = APIClient()
        self.config = Config()
        self.social = Social(self.api, self.auth)
        self.live = Live(self.api, self.auth)
        self.chat = Chat(self.api, self.auth)
        self.actfile = ActFile(self.api, self.auth)
        self.search = Search(self.api, self.auth)
        self.notification = Notification(self.api, self.auth)
        self.account = Account(self.api, self.auth)
    
    def login(self, args: List[str]) -> bool:
        """Se connecter"""
        if len(args) < 2:
            username = input("Nom d'utilisateur: ")
            password = input("Mot de passe: ")
        else:
            username = args[0]
            password = args[1]
        
        return self.auth.login(username, password)
    
    def logout(self, args: List[str]) -> bool:
        """Se déconnecter"""
        self.auth.logout()
        return True
    
    def profile(self, args: List[str]) -> bool:
        """Afficher le profil"""
        if not self.auth.is_authenticated():
            print_error("Veuillez vous connecter d'abord")
            return False
        
        if args:
            user_id = args[0]
            data = self.api.get_user_profile(user_id)
        else:
            data = self.auth.user_data
        
        if data:
            table = create_table("Profil utilisateur", ["Champ", "Valeur"])
            table.add_row("ID", data.get('id', 'N/A'))
            table.add_row("Nom", data.get('username', 'N/A'))
            table.add_row("Email", data.get('email', 'N/A'))
            table.add_row("Bio", data.get('bio', 'Non renseignée'))
            table.add_row("Vérifié", "✅" if data.get('is_verified') else "❌")
            table.add_row("Abonnés", str(data.get('followers_count', 0)))
            table.add_row("Abonnements", str(data.get('following_count', 0)))
            table.add_row("Vidéos", str(data.get('videos_count', 0)))
            console.print(table)
            return True
        
        return False
    
    def feed(self, args: List[str]) -> bool:
        """Afficher le feed"""
        if not self.auth.is_authenticated():
            print_error("Veuillez vous connecter d'abord")
            return False
        
        limit = int(args[0]) if args else 10
        videos = self.api.get_feed(self.auth.token, limit)
        
        if videos:
            for i, video in enumerate(videos, 1):
                print_header(f"🎬 #{i}")
                table = create_table()
                table.add_column("Champ", style="primary")
                table.add_column("Valeur")
                table.add_row("Auteur", video.get('username', 'Inconnu'))
                table.add_row("Description", video.get('description', 'Sans description'))
                table.add_row("Vues", str(video.get('views', 0)))
                table.add_row("Likes", str(video.get('likes', 0)))
                table.add_row("Publié", video.get('created_at', 'N/A'))
                console.print(table)
                console.print()
            return True
        
        return False

    # Dans la classe Commands, ajouter :

def chat(self, args: List[str]) -> bool:
    """Ouvrir la messagerie améliorée"""
    if not self.auth.is_authenticated():
        print_error("Veuillez vous connecter d'abord")
        return False

    # L'écran de chat amélioré sera géré par Textual
    # Cette méthode est appelée depuis l'interface TUI
    return True

def voice(self, args: List[str]) -> bool:
    """Envoyer un message vocal"""
    if not self.auth.is_authenticated():
        print_error("Veuillez vous connecter d'abord")
        return False

    if len(args) < 1:
        print_error("Usage: voice <utilisateur_id>")
        return False

    user_id = args[0]
    print_info(f"Enregistrement vocal pour {user_id}...")
    print_info("Appuyez sur Ctrl+C pour arrêter")

    # Simuler un enregistrement
    audio_file = Path("/tmp/voice_message.wav")
    try:
        # Simulation d'enregistrement
        print_info("🎤 Enregistrement en cours... (simulation)")
        time.sleep(3)

        # Créer un fichier factice
        audio_file.touch()
        print_info("⏹ Enregistrement terminé")

        # Envoyer
        with open(audio_file, 'rb') as f:
            audio_data = base64.b64encode(f.read()).decode()

        self.api.post("/api/messages/send",
                     data={"receiver_id": user_id, "content": audio_data[:100], "type": "audio"},
                     token=self.auth.token)

        print_success("✅ Message vocal envoyé")
        audio_file.unlink(missing_ok=True)
        return True

    except KeyboardInterrupt:
        print_info("⏹ Enregistrement arrêté")
        audio_file.unlink(missing_ok=True)
        return False
    except Exception as e:
        print_error(f"Erreur: {e}")
        return False
    def actfile(self, args: List[str]) -> bool:
        """Publier un ActFile"""
        if not self.auth.is_authenticated():
            print_error("Veuillez vous connecter d'abord")
            return False
        
        if args:
            content = ' '.join(args)
        else:
            print_info("Entrez votre texte (Ctrl+D pour terminer):")
            lines = []
            try:
                while True:
                    line = input()
                    lines.append(line)
            except EOFError:
                content = '\n'.join(lines)
        
        if content:
            return self.actfile.create(content)
        return False
    
    def upload(self, args: List[str]) -> bool:
        """Uploader une vidéo"""
        if not self.auth.is_authenticated():
            print_error("Veuillez vous connecter d'abord")
            return False
        
        if not args:
            print_error("Usage: upload <fichier> [description]")
            return False
        
        file_path = args[0]
        description = ' '.join(args[1:]) if len(args) > 1 else ""
        
        return self.account.upload_video(file_path, description)
    
    def live(self, args: List[str]) -> bool:
        """Gérer les lives"""
        if not self.auth.is_authenticated():
            print_error("Veuillez vous connecter d'abord")
            return False
        
        if not args:
            # Afficher les lives actifs
            return self.live.list_active()
        
        subcmd = args[0].lower()
        
        if subcmd == "start":
            title = ' '.join(args[1:]) if len(args) > 1 else "Live STRIP"
            return self.live.start(title)
        elif subcmd == "stop":
            return self.live.stop()
        elif subcmd == "list":
            return self.live.list_active()
        else:
            print_error(f"Commande live inconnue: {subcmd}")
            return False
    
    def chat(self, args: List[str]) -> bool:
        """Ouvrir la messagerie"""
        if not self.auth.is_authenticated():
            print_error("Veuillez vous connecter d'abord")
            return False
        
        if args:
            user_id = args[0]
            return self.chat.open(user_id)
        else:
            return self.chat.list_conversations()
    
    def message(self, args: List[str]) -> bool:
        """Envoyer un message"""
        if not self.auth.is_authenticated():
            print_error("Veuillez vous connecter d'abord")
            return False
        
        if len(args) < 2:
            print_error("Usage: message <utilisateur_id> <message>")
            return False
        
        user_id = args[0]
        content = ' '.join(args[1:])
        return self.chat.send(user_id, content)
    
    def notification(self, args: List[str]) -> bool:
        """Voir les notifications"""
        if not self.auth.is_authenticated():
            print_error("Veuillez vous connecter d'abord")
            return False
        
        return self.notification.list()
    
    def follow(self, args: List[str]) -> bool:
        """Suivre un utilisateur"""
        if not self.auth.is_authenticated():
            print_error("Veuillez vous connecter d'abord")
            return False
        
        if not args:
            print_error("Usage: follow <utilisateur_id>")
            return False
        
        return self.social.follow(args[0])
    
    def unfollow(self, args: List[str]) -> bool:
        """Ne plus suivre"""
        if not self.auth.is_authenticated():
            print_error("Veuillez vous connecter d'abord")
            return False
        
        if not args:
            print_error("Usage: unfollow <utilisateur_id>")
            return False
        
        return self.social.unfollow(args[0])
    
    def search(self, args: List[str]) -> bool:
        """Rechercher"""
        if not args:
            print_error("Usage: search <requête>")
            return False
        
        query = ' '.join(args)
        return self.search.search(query)
    
    def explore(self, args: List[str]) -> bool:
        """Explorer le contenu"""
        return self.search.explore()
    
    def trends(self, args: List[str]) -> bool:
        """Voir les tendances"""
        return self.search.trends()
    
    def verify(self, args: List[str]) -> bool:
        """Demander la vérification"""
        if not self.auth.is_authenticated():
            print_error("Veuillez vous connecter d'abord")
            return False
        
        return self.account.verify()
    
    def settings(self, args: List[str]) -> bool:
        """Paramètres"""
        if not args:
            print_info("Configuration actuelle:")
            for key, value in self.config._config.items():
                print(f"  {key}: {value}")
            return True
        
        if len(args) >= 2:
            key = args[0]
            value = ' '.join(args[1:])
            self.config.set(key, value)
            print_success(f"{key} = {value}")
            return True
        
        print_error("Usage: settings <clé> <valeur>")
        return False
    
    def config(self, args: List[str]) -> bool:
        """Configurer le CLI"""
        return self.settings(args)
    
    def cache(self, args: List[str]) -> bool:
        """Gérer le cache"""
        if args and args[0] == "clear":
            # Nettoyer le cache
            import shutil
            from config import CACHE_DIR
            shutil.rmtree(CACHE_DIR, ignore_errors=True)
            CACHE_DIR.mkdir(exist_ok=True)
            print_success("Cache nettoyé")
        else:
            print_info(f"Dossier cache: {CACHE_DIR}")
        return True
    
    def history(self, args: List[str]) -> bool:
        """Voir l'historique"""
        from history import History
        hist = History()
        commands = hist.get_all()
        
        if commands:
            table = create_table("Historique des commandes", ["#", "Commande"])
            for i, cmd in enumerate(commands[-50:], 1):
                table.add_row(str(i), cmd)
            console.print(table)
        else:
            print_info("Aucune commande dans l'historique")
        return True
    
    def clear(self, args: List[str]) -> bool:
        """Effacer l'écran"""
        os.system('clear' if os.name == 'posix' else 'cls')
        return True
    
    def help(self, args: List[str]) -> bool:
        """Afficher l'aide"""
        from constants import COMMANDS
        
        if args and args[0] in COMMANDS:
            cmd = args[0]
            print_info(f"{cmd}: {COMMANDS[cmd]}")
            return True
        
        table = create_table("Commandes disponibles", ["Commande", "Description"])
        for cmd, desc in sorted(COMMANDS.items()):
            table.add_row(cmd, desc)
        console.print(table)
        return True
    
    def exit(self, args: List[str]) -> bool:
        """Quitter"""
        print_info("Au revoir ! 🐬")
        return True
    
    def doctor(self, args: List[str]) -> bool:
        """Diagnostiquer"""
        print_header("🔧 Diagnostic STRIP")
        
        # Vérifier la connexion
        print_info("Vérification de la connexion...")
        try:
            import requests
            response = requests.get(f"{self.config.get('api_url')}/health", timeout=5)
            if response.status_code == 200:
                print_success("✅ Serveur accessible")
            else:
                print_error(f"❌ Serveur inaccessible: {response.status_code}")
        except:
            print_error("❌ Impossible de contacter le serveur")
        
        # Vérifier l'authentification
        if self.auth.is_authenticated():
            print_success(f"✅ Authentifié en tant que {self.auth.get_username()}")
        else:
            print_warning("⚠️ Non authentifié")
        
        # Vérifier la configuration
        print_info(f"API: {self.config.get('api_url')}")
        print_info(f"Cache: {self.config.get('cache_enabled')}")
        print_info(f"Timeout: {self.config.get('timeout')}s")
        
        return True
    
    def update(self, args: List[str]) -> bool:
        """Mettre à jour"""
        print_info("Vérification des mises à jour...")
        # À implémenter
        return True
    
    def plugins(self, args: List[str]) -> bool:
        """Gérer les plugins"""
        print_info("Fonctionnalité à implémenter")
        return True
