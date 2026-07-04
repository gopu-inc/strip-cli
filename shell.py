# shell.py
"""Shell interactif"""

import sys
import signal
from typing import Optional, List

from rich.prompt import Prompt
from rich.console import Console
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.formatted_text import HTML

from commands import Commands
from parser import CommandParser
from history import History
from autocomplete import AutoCompleter
from theme import console, print_error, print_success, print_info
from config import CONFIG_DIR
from dolphin import show_dolphin

class StripCompleter(Completer):
    """Auto-complétion personnalisée"""
    
    def __init__(self):
        self.autocomplete = AutoCompleter()
        self.commands = self.autocomplete.commands
    
    def get_completions(self, document, complete_event):
        text = document.text_before_cursor
        
        if ' ' in text:
            # Compléter les arguments (à implémenter)
            pass
        else:
            # Compléter les commandes
            suggestions = self.autocomplete.get_suggestions(text)
            for cmd in suggestions:
                yield Completion(cmd, start_position=-len(text))

class StripShell:
    """Shell interactif STRIP"""
    
    def __init__(self):
        self.commands = Commands()
        self.history = History()
        self.parser = CommandParser()
        self.completer = StripCompleter()
        self.running = True
        
        # Prompt session
        self.session = PromptSession(
            history=FileHistory(str(CONFIG_DIR / "prompt_history")),
            auto_suggest=AutoSuggestFromHistory(),
            completer=self.completer,
        )
        
        # Gestion des signaux
        signal.signal(signal.SIGINT, self.signal_handler)
    
    def signal_handler(self, sig, frame):
        """Gestionnaire Ctrl+C"""
        print()
        print_info("Appuyez sur Ctrl+D pour quitter")
    
    def get_prompt(self) -> str:
        """Retourne le prompt"""
        if self.commands.auth.is_authenticated():
            username = self.commands.auth.get_username() or "utilisateur"
            return f"🐬 {username} > "
        return "🐬 > "
    
    def run(self):
        """Lance le shell"""
        # Afficher le dauphin
        show_dolphin()
        
        # Afficher le statut
        if self.commands.auth.is_authenticated():
            username = self.commands.auth.get_username()
            print_success(f"Connecté en tant que {username}")
        else:
            print_info("Tapez 'login' pour vous connecter")
        
        print_info("Tapez 'help' pour voir les commandes disponibles")
        print()
        
        # Boucle principale
        while self.running:
            try:
                # Récupérer la commande
                prompt = self.get_prompt()
                input_str = self.session.prompt(HTML(f'<ansicyan>{prompt}</ansicyan>'))
                
                if not input_str:
                    continue
                
                # Ajouter à l'historique
                self.history.add(input_str)
                
                # Parser
                cmd, args = self.parser.parse(input_str)
                
                if not cmd:
                    continue
                
                # Exécuter
                self.execute(cmd, args)
                
            except KeyboardInterrupt:
                print()
                continue
            except EOFError:
                print()
                self.running = False
                break
            except Exception as e:
                print_error(f"Erreur: {str(e)}")
    
    def execute(self, cmd: str, args: List[str]) -> bool:
        """Exécute une commande"""
        cmd = cmd.lower()
        
        # Mapper les commandes vers les méthodes
        handlers = {
            'login': self.commands.login,
            'logout': self.commands.logout,
            'profile': self.commands.profile,
            'feed': self.commands.feed,
            'actfile': self.commands.actfile,
            'upload': self.commands.upload,
            'live': self.commands.live,
            'chat': self.commands.chat,
            'message': self.commands.message,
            'notification': self.commands.notification,
            'follow': self.commands.follow,
            'unfollow': self.commands.unfollow,
            'search': self.commands.search,
            'explore': self.commands.explore,
            'trends': self.commands.trends,
            'verify': self.commands.verify,
            'settings': self.commands.settings,
            'config': self.commands.config,
            'cache': self.commands.cache,
            'history': self.commands.history,
            'clear': self.commands.clear,
            'help': self.commands.help,
            'exit': self.commands.exit,
            'quit': self.commands.exit,
            'doctor': self.commands.doctor,
            'update': self.commands.update,
            'plugins': self.commands.plugins,
        }
        
        handler = handlers.get(cmd)
        
        if handler:
            result = handler(args)
            if cmd == 'exit' or cmd == 'quit':
                self.running = False
            return result
        else:
            print_error(f"Commande inconnue: {cmd}")
            print_info("Tapez 'help' pour voir les commandes disponibles")
            return False
