#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CommandParser - Analyseur de commandes pour Z-Dungeon Core
"""

import re
import logging
from typing import Dict, List, Any, Optional, Callable, Tuple

# Configuration du système de logging
logger = logging.getLogger('CommandParser')

class CommandParser:
    """
    Analyseur de commandes pour Z-Dungeon Core.
    Interprète les commandes textuelles des joueurs et les convertit en actions de jeu.
    """
    
    def __init__(self):
        """
        Initialise le parseur de commandes.
        """
        # Dictionnaire des commandes enregistrées
        # La clé est le nom de la commande, la valeur est un dictionnaire avec:
        # - func: la fonction à exécuter
        # - help: le texte d'aide
        # - aliases: aliases de la commande
        self.commands = {}
        
        # Dictionnaire des patterns de commandes
        # Utilisé pour des commandes plus complexes avec regex
        self.command_patterns = {}
        
        # Enregistrement des commandes de base
        self._register_default_commands()
    
    def _register_default_commands(self) -> None:
        """
        Enregistre les commandes par défaut du système.
        """
        # Commande d'aide
        self.register_command(
            name="aide",
            func=self._help_command,
            help="Affiche l'aide du jeu.",
            aliases=["help", "?"]
        )
        
        # Commande pour quitter
        self.register_command(
            name="quitter",
            func=self._quit_command,
            help="Quitte le jeu.",
            aliases=["exit", "quit", "q"]
        )
        
        # Commande de regarde
        self.register_command(
            name="regarder",
            func=self._look_command,
            help="Examine votre environnement ou un objet spécifique.",
            aliases=["look", "voir", "examiner", "observer"]
        )
        
        # Commande d'inventaire
        self.register_command(
            name="inventaire",
            func=self._inventory_command,
            help="Affiche le contenu de votre inventaire.",
            aliases=["inventory", "inv", "i"]
        )
    
    def register_command(self, name: str, func: Callable, help: str, aliases: List[str] = None) -> None:
        """
        Enregistre une nouvelle commande.
        
        Args:
            name: Nom principal de la commande
            func: Fonction à exécuter quand la commande est appelée
            help: Texte d'aide pour la commande
            aliases: Liste des aliases pour cette commande
        """
        self.commands[name.lower()] = {
            'func': func,
            'help': help,
            'aliases': aliases or []
        }
        
        # Enregistrer les aliases
        if aliases:
            for alias in aliases:
                self.commands[alias.lower()] = {
                    'func': func,
                    'help': help,
                    'aliases': []  # Ne pas dupliquer les aliases
                }
        
        logger.debug(f"Commande enregistrée: {name}")
    
    def register_command_pattern(self, pattern: str, func: Callable, help: str) -> None:
        """
        Enregistre un pattern de commande (expression régulière).
        
        Args:
            pattern: Expression régulière pour reconnaître la commande
            func: Fonction à exécuter quand le pattern est reconnu
            help: Texte d'aide pour cette commande
        """
        try:
            regex = re.compile(pattern, re.IGNORECASE)
            self.command_patterns[pattern] = {
                'regex': regex,
                'func': func,
                'help': help
            }
            logger.debug(f"Pattern de commande enregistré: {pattern}")
        except re.error as e:
            logger.error(f"Erreur lors de la compilation du pattern {pattern}: {e}")
    
    def parse_and_execute(self, command_text: str) -> Any:
        """
        Analyse et exécute une commande.
        
        Args:
            command_text: Texte de la commande à analyser et exécuter
            
        Returns:
            Any: Résultat de l'exécution de la commande
        """
        if not command_text:
            return None
        
        # Normaliser la commande (supprimer les espaces superflus, convertir en minuscules)
        command_text = command_text.strip()
        
        # Extraire le premier mot (commande principale)
        parts = command_text.split(maxsplit=1)
        main_command = parts[0].lower()
        
        # Récupérer les arguments (s'il y en a)
        args = parts[1] if len(parts) > 1 else ""
        
        # Vérifier si la commande existe
        if main_command in self.commands:
            command_info = self.commands[main_command]
            try:
                return command_info['func'](args)
            except Exception as e:
                logger.error(f"Erreur lors de l'exécution de la commande {main_command}: {e}")
                return f"Erreur lors de l'exécution de la commande: {str(e)}"
        
        # Si la commande directe n'est pas trouvée, vérifier les patterns
        for pattern_info in self.command_patterns.values():
            match = pattern_info['regex'].match(command_text)
            if match:
                try:
                    # Passer les groupes capturés comme arguments à la fonction
                    return pattern_info['func'](*match.groups())
                except Exception as e:
                    logger.error(f"Erreur lors de l'exécution du pattern {pattern_info['regex'].pattern}: {e}")
                    return f"Erreur lors de l'exécution de la commande: {str(e)}"
        
        # Si aucune commande n'est reconnue, considérer comme une action narrative
        return self._handle_narrative_action(command_text)
    
    def get_commands_help(self) -> Dict[str, str]:
        """
        Récupère un dictionnaire des commandes et leur aide.
        
        Returns:
            Dict[str, str]: Dictionnaire avec les noms de commandes comme clés et l'aide comme valeurs
        """
        help_dict = {}
        
        # Ajouter les commandes directes
        for cmd_name, cmd_info in self.commands.items():
            # Ne pas inclure les aliases dans la liste principale
            if not any(cmd_name == alias.lower() for cmd_other in self.commands.values() for alias in cmd_other['aliases']):
                # Formater avec les aliases
                aliases_str = ""
                if cmd_info['aliases']:
                    aliases_str = f" (aliases: {', '.join(cmd_info['aliases'])})"
                
                help_dict[cmd_name] = f"{cmd_info['help']}{aliases_str}"
        
        # Ajouter les patterns de commandes
        for pattern, pattern_info in self.command_patterns.items():
            # Utiliser une version simplifiée du pattern comme clé
            simple_pattern = pattern.replace('(', '[').replace(')', ']').replace('\\b', '')
            help_dict[simple_pattern] = pattern_info['help']
        
        return help_dict
    
    def _help_command(self, args: str) -> str:
        """
        Implémentation de la commande d'aide.
        
        Args:
            args: Arguments de la commande
            
        Returns:
            str: Texte d'aide
        """
        # Si un argument est spécifié, afficher l'aide pour cette commande spécifique
        if args:
            cmd_name = args.lower().strip()
            if cmd_name in self.commands:
                cmd_info = self.commands[cmd_name]
                aliases_str = ""
                if cmd_info['aliases']:
                    aliases_str = f"\nAliases: {', '.join(cmd_info['aliases'])}"
                return f"Aide pour '{cmd_name}':\n{cmd_info['help']}{aliases_str}"
            else:
                # Chercher dans les patterns
                for pattern, pattern_info in self.command_patterns.items():
                    if cmd_name in pattern:
                        return f"Aide pour '{pattern}':\n{pattern_info['help']}"
                
                return f"Commande '{cmd_name}' non reconnue."
        
        # Sans argument, retourner la liste des commandes
        help_text = "Liste des commandes disponibles:\n\n"
        
        for cmd_name, help_str in self.get_commands_help().items():
            help_text += f"{cmd_name}: {help_str}\n"
        
        help_text += "\nUtilisez 'aide [commande]' pour plus de détails sur une commande spécifique."
        
        return help_text
    
    def _quit_command(self, args: str) -> str:
        """
        Implémentation de la commande pour quitter.
        
        Args:
            args: Arguments de la commande
            
        Returns:
            str: Message de confirmation
        """
        # Cette fonction ne fait rien de spécial, car la gestion de la sortie est faite
        # au niveau de la boucle principale du jeu
        return "Vous quittez le jeu..."
    
    def _look_command(self, args: str) -> str:
        """
        Implémentation de la commande regarder.
        
        Args:
            args: Arguments de la commande (objet à examiner)
            
        Returns:
            str: Description de l'environnement ou de l'objet
        """
        # Cette implémentation est un placeholder
        # Dans un vrai jeu, cette fonction appellerait un gestionnaire de monde
        # pour obtenir les descriptions appropriées
        if not args:
            return "Vous regardez autour de vous..."
        else:
            return f"Vous examinez {args}..."
    
    def _inventory_command(self, args: str) -> str:
        """
        Implémentation de la commande inventaire.
        
        Args:
            args: Arguments de la commande
            
        Returns:
            str: Description du contenu de l'inventaire
        """
        # Cette implémentation est un placeholder
        # Dans un vrai jeu, cette fonction récupérerait l'inventaire du joueur
        return "Vous consultez votre inventaire..."
    
    def _handle_narrative_action(self, action_text: str) -> str:
        """
        Gère une action narrative non reconnue comme commande.
        
        Args:
            action_text: Texte de l'action narrative
            
        Returns:
            str: Réponse à l'action narrative
        """
        # Cette implémentation est un placeholder
        # Dans un vrai jeu, cette fonction transmettrait l'action au moteur narratif
        # pour générer une réponse appropriée
        return f"Vous tentez de {action_text}..."