#!/usr/bin/env python3
# strip.py
"""Point d'entrée principal"""

import sys
import os
from pathlib import Path

# Ajouter le répertoire courant au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import StripApp
from textual import __version__

def main():
    """Point d'entrée"""
    try:
        app = StripApp()
        app.run()
    except KeyboardInterrupt:
        print("\n👋 Au revoir !")
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
