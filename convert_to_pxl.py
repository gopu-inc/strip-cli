#!/usr/bin/env python3
# convert_to_pxl.py
"""Convertir des images en format .pxl pour StoreApp.TUI"""

import os
import sys
from pathlib import Path
from PIL import Image
import requests
from rich_pixels import Pixels
from rich.console import Console
import argparse


def download_image(url: str, output_path: Path) -> bool:
    """Télécharge une image depuis une URL"""
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            output_path.write_bytes(response.content)
            print(f"✅ Téléchargé: {output_path}")
            return True
        else:
            print(f"❌ Erreur {response.status_code}: {url}")
            return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False


def convert_to_pxl(image_path: Path, output_path: Path, width: int = 40, height: int = 20) -> bool:
    """Convertit une image en format ANSI .pxl"""
    try:
        # Ouvrir l'image
        img = Image.open(image_path)
        
        # Redimensionner
        img.thumbnail((width, height), Image.Resampling.LANCZOS)
        
        # Convertir en pixels ANSI
        pixels = Pixels.from_image(img)
        
        # Créer la sortie
        console = Console(file=open(output_path, "w", encoding="utf-8"), width=width)
        console.print(pixels)
        console.file.close()
        
        print(f"✅ Converti: {output_path} ({width}x{height})")
        return True
    except Exception as e:
        print(f"❌ Erreur de conversion: {e}")
        return False


def create_app_icons(bundle: str, icon_url: str, screenshots_urls: list):
    """Crée toutes les icônes et captures pour une application"""
    
    # Dossiers
    cache_dir = Path.home() / ".store" / "cache" / bundle
    cache_dir.mkdir(parents=True, exist_ok=True)
    
    # Icône
    print(f"\n📦 Traitement de l'icône pour {bundle}")
    icon_path = cache_dir / "icon.png"
    if download_image(icon_url, icon_path):
        convert_to_pxl(icon_path, cache_dir / "icon.pxl", width=20, height=20)
    
    # Captures d'écran
    print(f"\n📸 Traitement des captures d'écran pour {bundle}")
    for i, url in enumerate(screenshots_urls, 1):
        screenshot_path = cache_dir / f"screenshot_{i}.png"
        if download_image(url, screenshot_path):
            convert_to_pxl(screenshot_path, cache_dir / f"screenshot_{i}.pxl", width=40, height=20)


def main():
    parser = argparse.ArgumentParser(description="Convertir des images en format .pxl")
    parser.add_argument("input", help="Fichier image ou URL")
    parser.add_argument("-o", "--output", help="Fichier de sortie .pxl")
    parser.add_argument("-w", "--width", type=int, default=40, help="Largeur en caractères")
    parser.add_argument("-H", "--height", type=int, default=20, help="Hauteur en caractères")
    parser.add_argument("--bundle", help="Bundle de l'application")
    parser.add_argument("--icon", action="store_true", help="Traiter comme une icône")
    parser.add_argument("--screenshot", action="store_true", help="Traiter comme une capture d'écran")
    
    args = parser.parse_args()
    
    # Si c'est une URL
    if args.input.startswith(("http://", "https://")):
        if not args.output:
            args.output = "downloaded.png"
        download_image(args.input, Path(args.output))
        args.input = args.output
    
    # Convertir
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"❌ Fichier introuvable: {input_path}")
        return 1
    
    output_path = Path(args.output) if args.output else input_path.with_suffix(".pxl")
    
    if convert_to_pxl(input_path, output_path, args.width, args.height):
        print(f"✅ Conversion réussie: {output_path}")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
