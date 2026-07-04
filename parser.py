# parser.py
"""Analyseur de commandes"""

from typing import List, Tuple, Optional
import shlex

class CommandParser:
    """Analyseur de commandes"""
    
    @staticmethod
    def parse(input_str: str) -> Tuple[Optional[str], List[str]]:
        """
        Parse une ligne de commande
        Retourne (commande, arguments)
        """
        if not input_str or not input_str.strip():
            return None, []
        
        try:
            parts = shlex.split(input_str)
        except ValueError:
            # Fallback: split simple
            parts = input_str.strip().split()
        
        if not parts:
            return None, []
        
        return parts[0], parts[1:]
    
    @staticmethod
    def parse_with_pipe(input_str: str) -> List[Tuple[str, List[str]]]:
        """Parse avec pipes (commande1 | commande2)"""
        if '|' not in input_str:
            cmd, args = CommandParser.parse(input_str)
            return [(cmd, args)] if cmd else []
        
        commands = []
        for part in input_str.split('|'):
            cmd, args = CommandParser.parse(part)
            if cmd:
                commands.append((cmd, args))
        
        return commands
