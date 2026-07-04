# dolphin.py
"""Animation du dauphin au démarrage"""

import time
from rich.console import Console
from rich.text import Text

console = Console()

DOLPHIN = """
        .,,uod8B8bou,,.
   ..,uodBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBo,.
  ,dBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBb.
,dBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBb.
dBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBb
BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB
BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB
BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB
BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB
BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB
`BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB'
 `BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB'
  `BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB'
   `dBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBd'
     `dBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBd'
       `dBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBd'
         `dBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBd'
           `dBBBBBBBBBBBBBBBBBBBBBBBBBBBd'
             `dBBBBBBBBBBBBBBBBBBBBBBd'
               `dBBBBBBBBBBBBBBBBBBd'
                 `dBBBBBBBBBBBBBBd'
                   `dBBBBBBBBBBd'
                     `dBBBBBBd'
                       `dBBBd'
                        `d'
"""

def show_dolphin():
    """Affiche le dauphin avec animation"""
    lines = DOLPHIN.split('\n')
    total = len(lines)
    
    # Effet de fondu
    for i in range(total):
        console.print(Text(lines[i], style="primary"))
        time.sleep(0.02)
    
    # Petit saut
    for _ in range(3):
        console.clear()
        for i in range(total):
            if i < total - 1:
                console.print(Text(" " * 2 + lines[i], style="primary"))
            else:
                console.print(Text(" " * 4 + lines[i], style="primary"))
        time.sleep(0.1)
        console.clear()
        for i in range(total):
            console.print(Text(lines[i], style="primary"))
        time.sleep(0.1)
    
    console.print()
    console.print(Text("🐬 STRIP CLI", style="title"))
    console.print(Text("Version 1.0.0", style="muted"))
    console.print()
