# history.py
"""Gestion de l'historique des commandes"""

import json
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from config import HISTORY_FILE

class History:
    """Gestionnaire d'historique"""
    
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self._history: List[str] = []
        self._position = -1
        self._load()
    
    def _load(self):
        """Charge l'historique depuis le fichier"""
        if HISTORY_FILE.exists():
            try:
                with open(HISTORY_FILE, 'r') as f:
                    data = json.load(f)
                    self._history = data.get('commands', [])
            except:
                self._history = []
    
    def save(self):
        """Sauvegarde l'historique"""
        try:
            with open(HISTORY_FILE, 'w') as f:
                json.dump({'commands': self._history[-self.max_size:]}, f)
        except:
            pass
    
    def add(self, command: str):
        """Ajoute une commande à l'historique"""
        if command and command.strip():
            self._history.append(command.strip())
            if len(self._history) > self.max_size:
                self._history = self._history[-self.max_size:]
            self.save()
            self._position = len(self._history)
    
    def previous(self) -> Optional[str]:
        """Retourne la commande précédente"""
        if self._position > 0:
            self._position -= 1
            return self._history[self._position]
        return None
    
    def next(self) -> Optional[str]:
        """Retourne la commande suivante"""
        if self._position < len(self._history) - 1:
            self._position += 1
            return self._history[self._position]
        self._position = len(self._history)
        return None
    
    def reset_position(self):
        """Réinitialise la position"""
        self._position = len(self._history)
    
    def search(self, query: str) -> List[str]:
        """Recherche dans l'historique"""
        return [cmd for cmd in self._history if query.lower() in cmd.lower()]
    
    def clear(self):
        """Efface l'historique"""
        self._history = []
        self._position = -1
        self.save()
    
    def get_all(self) -> List[str]:
        """Retourne tout l'historique"""
        return self._history.copy()
