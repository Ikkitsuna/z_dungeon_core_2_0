#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ConsoleUI - Interface utilisateur console pour Z-Dungeon Core
"""

import os
import sys
import time
import logging
import textwrap
import shutil
from typing import Dict, List, Any, Optional, Callable

# Configuration du système de logging
logger = logging.getLogger('ConsoleUI')

class ConsoleUI:
    """
    Interface utilisateur en console pour Z-Dungeon Core.
    Gère l'affichage du texte, des menus et l'interaction avec l'utilisateur.
    """
    
    def __init__(self, prompt_symbol: str = ">", width: Optional[int] = None):
        """
        Initialise l'interface console.
        
        Args:
            prompt_symbol: Symbole utilisé pour le prompt d'entrée
            width: Largeur de l'affichage (automatique si None)
        """
        self.prompt_symbol = prompt_symbol
        
        # Détermine automatiquement la largeur du terminal si non spécifiée
        if width is None:
            try:
                terminal_size = shutil.get_terminal_size()
                self.width = terminal_size.columns
            except Exception:
                # Valeur par défaut si impossible de déterminer
                self.width = 80
        else:
            self.width = width
        
        # Historique des commandes
        self.command_history = []
        
        # Couleurs ANSI (pour les terminaux qui les supportent)
        self.use_colors = True
        self.colors = {
            'reset': '\033[0m',
            'bold': '\033[1m',
            'underline': '\033[4m',
            'black': '\033[30m',
            'red': '\033[31m',
            'green': '\033[32m',
            'yellow': '\033[33m',
            'blue': '\033[34m',
            'magenta': '\033[35m',
            'cyan': '\033[36m',
            'white': '\033[37m',
            'bg_black': '\033[40m',
            'bg_red': '\033[41m',
            'bg_green': '\033[42m',
            'bg_yellow': '\033[43m',
            'bg_blue': '\033[44m',
            'bg_magenta': '\033[45m',
            'bg_cyan': '\033[46m',
            'bg_white': '\033[47m'
        }
    
    def clear_screen(self) -> None:
        """
        Efface l'écran de la console.
        """
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def disable_colors(self) -> None:
        """
        Désactive l'utilisation des couleurs ANSI.
        """
        self.use_colors = False
    
    def enable_colors(self) -> None:
        """
        Active l'utilisation des couleurs ANSI.
        """
        self.use_colors = True
    
    def _color_text(self, text: str, color: str) -> str:
        """
        Applique une couleur à un texte.
        
        Args:
            text: Texte à colorer
            color: Nom de la couleur à appliquer
            
        Returns:
            str: Texte coloré (si les couleurs sont activées)
        """
        if not self.use_colors:
            return text
        
        color_code = self.colors.get(color.lower(), '')
        if not color_code:
            return text
        
        return f"{color_code}{text}{self.colors['reset']}"
    
    def print(self, text: str, color: Optional[str] = None, bold: bool = False, 
             underline: bool = False, centered: bool = False, wrap: bool = True,
             delay: float = 0.0) -> None:
        """
        Affiche du texte formaté dans la console.
        
        Args:
            text: Texte à afficher
            color: Couleur à appliquer (optionnel)
            bold: Si le texte doit être en gras
            underline: Si le texte doit être souligné
            centered: Si le texte doit être centré
            wrap: Si le texte doit être adapté à la largeur de l'écran
            delay: Délai entre l'affichage de chaque caractère (effet de frappe)
        """
        formatted_text = text
        
        # Application des styles
        if self.use_colors:
            if bold:
                formatted_text = f"{self.colors['bold']}{formatted_text}"
            if underline:
                formatted_text = f"{self.colors['underline']}{formatted_text}"
            if color and color in self.colors:
                formatted_text = f"{self.colors[color]}{formatted_text}"
            
            # Réinitialiser les styles à la fin
            if bold or underline or color:
                formatted_text = f"{formatted_text}{self.colors['reset']}"
        
        # Découpage du texte
        if wrap:
            lines = []
            for paragraph in formatted_text.split('\n'):
                if paragraph.strip():
                    wrapped = textwrap.wrap(paragraph, width=self.width)
                    lines.extend(wrapped)
                else:
                    lines.append('')
        else:
            lines = formatted_text.split('\n')
        
        # Centrage du texte
        if centered:
            lines = [line.center(self.width) for line in lines]
        
        # Affichage des lignes
        for line in lines:
            if delay > 0:
                # Effet de frappe progressive
                for char in line:
                    sys.stdout.write(char)
                    sys.stdout.flush()
                    time.sleep(delay)
                sys.stdout.write('\n')
                sys.stdout.flush()
            else:
                print(line)
    
    def print_header(self, title: str, width: Optional[int] = None) -> None:
        """
        Affiche un en-tête avec un titre centré.
        
        Args:
            title: Titre à afficher
            width: Largeur personnalisée (utilise la largeur par défaut si None)
        """
        w = width or self.width
        
        self.print('=' * w, color='cyan', wrap=False)
        self.print(title.upper(), color='cyan', bold=True, centered=True)
        self.print('=' * w, color='cyan', wrap=False)
        self.print('')  # Ligne vide après l'en-tête
    
    def print_subheader(self, title: str) -> None:
        """
        Affiche un sous-en-tête.
        
        Args:
            title: Titre du sous-en-tête
        """
        self.print(f"--- {title} ---", color='yellow', bold=True)
        self.print('')  # Ligne vide après le sous-en-tête
    
    def print_divider(self, char: str = '-') -> None:
        """
        Affiche une ligne de séparation.
        
        Args:
            char: Caractère à utiliser pour la ligne
        """
        self.print(char * self.width, wrap=False)
    
    def print_error(self, message: str) -> None:
        """
        Affiche un message d'erreur.
        
        Args:
            message: Message d'erreur à afficher
        """
        self.print(f"ERREUR: {message}", color='red', bold=True)
    
    def print_warning(self, message: str) -> None:
        """
        Affiche un message d'avertissement.
        
        Args:
            message: Message d'avertissement à afficher
        """
        self.print(f"AVERTISSEMENT: {message}", color='yellow')
    
    def print_success(self, message: str) -> None:
        """
        Affiche un message de succès.
        
        Args:
            message: Message de succès à afficher
        """
        self.print(f"SUCCÈS: {message}", color='green')
    
    def print_info(self, message: str) -> None:
        """
        Affiche un message d'information.
        
        Args:
            message: Message d'information à afficher
        """
        self.print(f"INFO: {message}", color='blue')
    
    def print_scene(self, text: str, delay: float = 0.03) -> None:
        """
        Affiche une scène narrative avec un effet de frappe progressive.
        
        Args:
            text: Texte de la scène
            delay: Délai entre les caractères
        """
        self.print('')
        self.print(text, color='cyan', delay=delay)
        self.print('')
    
    def print_dialogue(self, speaker: str, text: str, color: str = 'yellow', delay: float = 0.02) -> None:
        """
        Affiche un dialogue avec le nom du locuteur.
        
        Args:
            speaker: Nom du locuteur
            text: Texte du dialogue
            color: Couleur du dialogue
            delay: Délai entre les caractères
        """
        self.print(f"{speaker}: ", color=color, bold=True, delay=0, wrap=False)
        self.print(text, delay=delay)
        self.print('')
    
    def input(self, prompt: Optional[str] = None) -> str:
        """
        Demande une entrée à l'utilisateur avec un prompt personnalisé.
        
        Args:
            prompt: Texte du prompt (utilise le symbole par défaut si None)
            
        Returns:
            str: Entrée de l'utilisateur
        """
        if prompt:
            prompt_text = f"{prompt} {self.prompt_symbol} "
        else:
            prompt_text = f"{self.prompt_symbol} "
        
        if self.use_colors:
            prompt_text = f"{self.colors['green']}{prompt_text}{self.colors['reset']}"
        
        user_input = input(prompt_text).strip()
        
        # Enregistrer la commande dans l'historique (si non vide)
        if user_input:
            self.command_history.append(user_input)
        
        return user_input
    
    def display_menu(self, title: str, options: List[str], 
                    prompt: str = "Choisissez une option", 
                    color: str = 'cyan') -> int:
        """
        Affiche un menu d'options et retourne le choix de l'utilisateur.
        
        Args:
            title: Titre du menu
            options: Liste des options à afficher
            prompt: Texte du prompt
            color: Couleur du menu
            
        Returns:
            int: Indice de l'option choisie (0-indexed)
        """
        self.print_subheader(title)
        
        for i, option in enumerate(options):
            self.print(f"{i+1}. {option}", color=color)
        
        self.print('')
        
        while True:
            try:
                choice = int(self.input(prompt))
                if 1 <= choice <= len(options):
                    return choice - 1  # Convertir en 0-indexed
                else:
                    self.print_error(f"Veuillez entrer un nombre entre 1 et {len(options)}")
            except ValueError:
                self.print_error("Veuillez entrer un nombre valide")
    
    def display_paged_content(self, content: List[str], 
                             items_per_page: int = 10,
                             title: str = "Résultats") -> None:
        """
        Affiche du contenu paginé avec navigation.
        
        Args:
            content: Liste des éléments à afficher
            items_per_page: Nombre d'éléments par page
            title: Titre de l'affichage
        """
        if not content:
            self.print_info("Aucun contenu à afficher.")
            return
        
        total_items = len(content)
        total_pages = (total_items + items_per_page - 1) // items_per_page
        current_page = 1
        
        while True:
            self.clear_screen()
            self.print_header(f"{title} - Page {current_page}/{total_pages}")
            
            # Calculer les éléments de la page courante
            start_idx = (current_page - 1) * items_per_page
            end_idx = min(start_idx + items_per_page, total_items)
            
            # Afficher les éléments
            for i in range(start_idx, end_idx):
                self.print(f"{i+1}. {content[i]}")
            
            self.print_divider()
            self.print("Navigation: (n)ext page, (p)revious page, (q)uit", color='green')
            
            choice = self.input().lower()
            
            if choice == 'n' or choice == 'next':
                if current_page < total_pages:
                    current_page += 1
            elif choice == 'p' or choice == 'prev' or choice == 'previous':
                if current_page > 1:
                    current_page -= 1
            elif choice == 'q' or choice == 'quit' or choice == 'exit':
                break
    
    def display_item_details(self, item: Dict[str, Any], title: str = "Détails") -> None:
        """
        Affiche les détails d'un élément (objet, PNJ, lieu, etc.).
        
        Args:
            item: Dictionnaire contenant les détails de l'élément
            title: Titre de l'affichage
        """
        self.print_subheader(title)
        
        # Afficher les attributs de l'élément
        for key, value in item.items():
            # Formater la clé (convertir snake_case en titre)
            formatted_key = key.replace('_', ' ').title()
            
            # Si la valeur est une liste
            if isinstance(value, list):
                self.print(f"{formatted_key}:", color='yellow', bold=True)
                for item in value:
                    self.print(f"  - {item}")
            # Si la valeur est un dictionnaire
            elif isinstance(value, dict):
                self.print(f"{formatted_key}:", color='yellow', bold=True)
                for k, v in value.items():
                    formatted_k = k.replace('_', ' ').title()
                    self.print(f"  {formatted_k}: {v}")
            # Valeur simple
            else:
                self.print(f"{formatted_key}: {value}", color='yellow', bold=True)
        
        self.print_divider()
    
    def display_progress_bar(self, progress: float, total: float = 100.0, 
                            width: int = 40, char: str = '█', empty: str = '░', 
                            prefix: str = '', suffix: str = '') -> None:
        """
        Affiche une barre de progression.
        
        Args:
            progress: Valeur actuelle
            total: Valeur totale
            width: Largeur de la barre
            char: Caractère pour la partie remplie
            empty: Caractère pour la partie vide
            prefix: Texte avant la barre
            suffix: Texte après la barre
        """
        progress_ratio = min(1.0, max(0.0, progress / float(total)))
        filled_length = int(width * progress_ratio)
        
        # Créer la barre
        bar = char * filled_length + empty * (width - filled_length)
        
        # Pourcentage
        percent = int(100 * progress_ratio)
        
        # Afficher
        output = f"\r{prefix} |{bar}| {percent}% {suffix}"
        sys.stdout.write(output)
        sys.stdout.flush()
    
    def wait_for_keypress(self, message: str = "Appuyez sur Entrée pour continuer...") -> None:
        """
        Attend que l'utilisateur appuie sur une touche pour continuer.
        
        Args:
            message: Message à afficher
        """
        self.print('')
        input(message)
    
    def ask_yes_no(self, question: str, default: Optional[bool] = None) -> bool:
        """
        Pose une question oui/non à l'utilisateur.
        
        Args:
            question: Question à poser
            default: Valeur par défaut (None pour forcer un choix)
            
        Returns:
            bool: True pour oui, False pour non
        """
        if default is None:
            prompt = f"{question} (o/n): "
        elif default:
            prompt = f"{question} (O/n): "
        else:
            prompt = f"{question} (o/N): "
        
        while True:
            response = self.input(prompt).lower()
            
            if not response and default is not None:
                return default
            
            if response in ('o', 'oui', 'y', 'yes'):
                return True
            elif response in ('n', 'non', 'no'):
                return False
            
            self.print_error("Veuillez répondre par 'o' ou 'n'")
    
    def ask_for_string(self, prompt: str, min_length: int = 0, max_length: Optional[int] = None,
                      default: Optional[str] = None) -> str:
        """
        Demande une chaîne de caractères à l'utilisateur avec validation.
        
        Args:
            prompt: Texte du prompt
            min_length: Longueur minimale acceptée
            max_length: Longueur maximale acceptée (None pour illimité)
            default: Valeur par défaut (None pour aucune)
            
        Returns:
            str: Chaîne entrée par l'utilisateur
        """
        if default:
            full_prompt = f"{prompt} [{default}]: "
        else:
            full_prompt = f"{prompt}: "
        
        while True:
            response = self.input(full_prompt)
            
            if not response and default:
                return default
            
            if len(response) < min_length:
                self.print_error(f"La réponse doit contenir au moins {min_length} caractères")
                continue
            
            if max_length and len(response) > max_length:
                self.print_error(f"La réponse doit contenir au plus {max_length} caractères")
                continue
            
            return response
    
    def ask_for_integer(self, prompt: str, min_value: Optional[int] = None, 
                       max_value: Optional[int] = None, default: Optional[int] = None) -> int:
        """
        Demande un entier à l'utilisateur avec validation.
        
        Args:
            prompt: Texte du prompt
            min_value: Valeur minimale acceptée (None pour illimité)
            max_value: Valeur maximale acceptée (None pour illimité)
            default: Valeur par défaut (None pour aucune)
            
        Returns:
            int: Entier entré par l'utilisateur
        """
        if default is not None:
            full_prompt = f"{prompt} [{default}]: "
        else:
            full_prompt = f"{prompt}: "
        
        while True:
            response = self.input(full_prompt)
            
            if not response and default is not None:
                return default
            
            try:
                value = int(response)
                
                if min_value is not None and value < min_value:
                    self.print_error(f"La valeur doit être au moins {min_value}")
                    continue
                
                if max_value is not None and value > max_value:
                    self.print_error(f"La valeur doit être au plus {max_value}")
                    continue
                
                return value
            except ValueError:
                self.print_error("Veuillez entrer un nombre entier valide")
    
    def display_help(self, commands: Dict[str, str], title: str = "Aide") -> None:
        """
        Affiche l'aide avec la liste des commandes disponibles.
        
        Args:
            commands: Dictionnaire des commandes et leurs descriptions
            title: Titre de l'affichage
        """
        self.print_header(title)
        
        # Trouver la longueur maximale des commandes pour l'alignement
        max_length = max(len(cmd) for cmd in commands.keys())
        
        for cmd, desc in commands.items():
            # Aligner les descriptions
            padding = ' ' * (max_length - len(cmd))
            self.print(f"{cmd}{padding}  : {desc}", color='cyan')
        
        self.print_divider()
    
    def display_loading(self, message: str = "Chargement", iterations: int = 3, 
                       delay: float = 0.5) -> None:
        """
        Affiche une animation de chargement simple.
        
        Args:
            message: Message à afficher
            iterations: Nombre d'itérations
            delay: Délai entre les itérations
        """
        symbols = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        
        for _ in range(iterations):
            for symbol in symbols:
                sys.stdout.write(f"\r{message} {symbol}")
                sys.stdout.flush()
                time.sleep(delay)
        
        sys.stdout.write("\r" + " " * (len(message) + 2) + "\r")
        sys.stdout.flush()
    
    def register_command_handler(self, command_parser) -> None:
        """
        Enregistre un gestionnaire de commandes pour l'interface.
        
        Args:
            command_parser: Instance de CommandParser à utiliser
        """
        self.command_parser = command_parser
    
    def run_command_loop(self, prompt: str = "Que voulez-vous faire?", 
                        exit_commands: List[str] = ["exit", "quit", "q"]) -> None:
        """
        Exécute une boucle de commandes jusqu'à ce que l'utilisateur entre une commande de sortie.
        
        Args:
            prompt: Texte du prompt
            exit_commands: Liste des commandes qui terminent la boucle
        """
        if not hasattr(self, 'command_parser'):
            raise RuntimeError("Aucun gestionnaire de commandes enregistré. Utilisez register_command_handler d'abord.")
        
        while True:
            command = self.input(prompt)
            
            if command.lower() in exit_commands:
                self.print("Au revoir!")
                break
            
            try:
                result = self.command_parser.parse_and_execute(command)
                if result and isinstance(result, str):
                    self.print(result)
            except Exception as e:
                self.print_error(f"Erreur lors de l'exécution de la commande: {str(e)}")
    
    def display_title_screen(self, title: str, subtitle: Optional[str] = None, 
                            version: Optional[str] = None, ascii_art: Optional[str] = None) -> None:
        """
        Affiche un écran titre pour le jeu.
        
        Args:
            title: Titre principal
            subtitle: Sous-titre (optionnel)
            version: Numéro de version (optionnel)
            ascii_art: Art ASCII à afficher (optionnel)
        """
        self.clear_screen()
        
        if ascii_art:
            self.print(ascii_art, color='cyan', wrap=False, centered=True)
        
        self.print('')
        self.print(title, color='magenta', bold=True, centered=True)
        
        if subtitle:
            self.print('')
            self.print(subtitle, color='yellow', centered=True)
        
        if version:
            self.print('')
            self.print(f"Version {version}", color='cyan', centered=True)
        
        self.print('')
        self.print_divider('=')
        self.print("Appuyez sur Entrée pour commencer...", centered=True)
        input()
        self.clear_screen()
    
    def display_game_over(self, message: str = "Fin de partie", 
                         reason: Optional[str] = None,
                         ascii_art: Optional[str] = None) -> None:
        """
        Affiche un écran de fin de partie.
        
        Args:
            message: Message principal
            reason: Raison de la fin (optionnel)
            ascii_art: Art ASCII à afficher (optionnel)
        """
        self.clear_screen()
        
        if ascii_art:
            self.print(ascii_art, color='red', wrap=False, centered=True)
        
        self.print('')
        self.print(message, color='red', bold=True, centered=True)
        
        if reason:
            self.print('')
            self.print(reason, centered=True)
        
        self.print('')
        self.print_divider('=')
        self.print("Appuyez sur Entrée pour continuer...", centered=True)
        input()