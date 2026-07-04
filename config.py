# config.py
"""Gestion de la configuration"""

import os
import json
from pathlib import Path
from typing import Optional, Dict, Any

CONFIG_DIR = Path.home() / ".strip"
CONFIG_FILE = CONFIG_DIR / "config.json"
TOKEN_FILE = CONFIG_DIR / "token"
CACHE_DIR = CONFIG_DIR / "cache"
HISTORY_FILE = CONFIG_DIR / "history.json"

class Config:
    """Gestionnaire de configuration"""
    
    def __init__(self):
        self._ensure_dirs()
        self._config = self._load_config()
        
    def _ensure_dirs(self):
        """Crée les dossiers nécessaires"""
        CONFIG_DIR.mkdir(exist_ok=True)
        CACHE_DIR.mkdir(exist_ok=True)
        
    def _load_config(self) -> Dict[str, Any]:
        """Charge la configuration"""
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, 'r') as f:
                    return json.load(f)
            except:
                pass
        return self._default_config()
    
    def _default_config(self) -> Dict[str, Any]:
        """Configuration par défaut"""
        return {
            "theme": "dark",
            "autocomplete": True,
            "history_size": 1000,
            "cache_enabled": True,
            "cache_ttl": 3600,
            "notifications": True,
            "sound_effects": False,
            "auto_update": True,
            "api_url": "https://hoosthubs-g.onrender.com",
            "ws_url": "wss://hoosthubs-g.onrender.com",
            "timeout": 30,
            "max_upload_size": 100 * 1024 * 1024,  # 100 MB
            "download_dir": str(Path.home() / "Downloads" / "STRIP"),
        }
    
    def get(self, key: str, default=None):
        """Récupère une valeur"""
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any):
        """Définit une valeur"""
        self._config[key] = value
        self.save()
    
    def save(self):
        """Sauvegarde la configuration"""
        with open(CONFIG_FILE, 'w') as f:
            json.dump(self._config, f, indent=2)
    
    def get_token(self) -> Optional[str]:
        """Récupère le token JWT"""
        if TOKEN_FILE.exists():
            try:
                with open(TOKEN_FILE, 'r') as f:
                    return f.read().strip()
            except:
                pass
        return None
    
    def set_token(self, token: str):
        """Sauvegarde le token JWT"""
        with open(TOKEN_FILE, 'w') as f:
            f.write(token)
    
    def clear_token(self):
        """Efface le token"""
        if TOKEN_FILE.exists():
            TOKEN_FILE.unlink()
