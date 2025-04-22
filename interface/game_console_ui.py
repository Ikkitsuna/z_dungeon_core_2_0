#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GameConsoleUI - Interface console spécifique au jeu Z-Dungeon Core
"""

import os
import logging
import time
import random
from typing import Dict, List, Any, Optional, Callable

from .console_ui import ConsoleUI
from .command_parser import CommandParser

# Changement des imports relatifs en imports absolus
from entities.player import Player
from entities.location import Location
from core.narrative_engine import NarrativeEngine

# Configuration du système de logging
logger = logging.getLogger('GameConsoleUI')

class GameConsoleUI(ConsoleUI):
    """
    Interface console spécifique au jeu Z-Dungeon Core.
    Étend la classe ConsoleUI de base avec des fonctionnalités propres au jeu.
    """
    
    def __init__(self, prompt_symbol: str = ">", width: Optional[int] = None):
        """
        Initialise l'interface console de jeu.
        
        Args:
            prompt_symbol: Symbole utilisé pour le prompt d'entrée
            width: Largeur de l'affichage (automatique si None)
        """
        super().__init__(prompt_symbol, width)
        
        # Initialiser le parseur de commandes
        self.command_parser = CommandParser()
        self.register_command_handler(self.command_parser)
        
        # Référence vers le joueur et le monde (à définir après l'initialisation)
        self.player = None
        self.current_location = None
        self.narrative_engine = None
        
        # État du jeu
        self.game_running = False
        
        # Délais pour les affichages textuels
        self.scene_delay = 0.03  # Délai par défaut pour les scènes (normal)
        self.dialogue_delay = 0.02  # Délai par défaut pour les dialogues (normal)
        self._text_speed = 'normal'  # Vitesse de texte par défaut
        
        # Charger les ressources graphiques
        self.ascii_art = self._load_ascii_art()
    
    def _load_ascii_art(self) -> Dict[str, str]:
        """
        Charge les fichiers d'art ASCII utilisés dans le jeu.
        
        Returns:
            Dict[str, str]: Dictionnaire des arts ASCII
        """
        art_dict = {
            'title': r"""
   ______    ____                                          
  / ____/   / __ \__  ______  ____ ____  ____  ____  ____ 
 /___ /    / / / / / / / __ \/ __ `/ _ \/ __ \/ __ \/ __ \
/___  /   / /_/ / /_/ / / / / /_/ /  __/ /_/ / /_/ / / / /
/_____/  /_____/\__,_/_/ /_/\__, /\___/\____/\____/_/ /_/ 
                           /____/                          
  ______               
 / ____/___  ________ 
/ /   / __ \/ ___/ _ \
/ /___/ /_/ / /  /  __/
\____/\____/_/   \___/ 
""",
            'game_over': r"""
  _____                         ____                 
 / ___/__ ___ _  ___  ___     / __ \_  _____ ____   
/ (_ / _ `/  ' \/ _ \/ _ \   / /_/ / |/ / -_) __/   
\___/\_,_/_/_/_/\___/\___/   \____/|___/\__/_/      
""",
            'victory': r"""
 __   ___      _                   _ 
 \ \ / (_)__ _| |_ ___ _ _ _  _   | |
  \ V /| / _` |  _/ _ \ '_| || |  |_|
   \_/ |_\__, |\__\___/_|  \_, |  (_)
         |___/             |__/      
"""
        }
        
        return art_dict
    
    def set_player(self, player: Player) -> None:
        """
        Définit le joueur pour cette interface.
        
        Args:
            player: Instance du joueur
        """
        self.player = player
    
    def set_current_location(self, location: Location) -> None:
        """
        Définit la localisation actuelle pour l'interface.
        
        Args:
            location: Instance de la localisation actuelle
        """
        self.current_location = location
    
    def set_narrative_engine(self, engine: NarrativeEngine) -> None:
        """
        Définit le moteur narratif pour cette interface.
        
        Args:
            engine: Instance du moteur narratif
        """
        self.narrative_engine = engine
    
    def start_game(self, title: str, subtitle: Optional[str] = None, version: str = "1.0") -> None:
        """
        Démarre le jeu avec un écran titre.
        
        Args:
            title: Titre du jeu
            subtitle: Sous-titre (optionnel)
            version: Version du jeu
        """
        self.game_running = True
        
        # Afficher l'écran titre
        self.display_title_screen(
            title=title,
            subtitle=subtitle,
            version=version,
            ascii_art=self.ascii_art.get('title')
        )
        
        # Afficher l'introduction
        self._display_introduction()
        
        # Démarrer la boucle de jeu
        self._game_loop()
    
    def _display_introduction(self) -> None:
        """
        Affiche l'introduction du jeu.
        """
        if not self.narrative_engine:
            self.print_warning("Moteur narratif non initialisé, impossible d'afficher l'introduction.")
            return
        
        # Générer une introduction avec le moteur narratif
        intro_text = self.narrative_engine.generate_introduction()
        
        # Afficher l'introduction
        self.clear_screen()
        self.print_header("Introduction")
        self.print_scene(intro_text)
        self.wait_for_keypress()
    
    def _game_loop(self) -> None:
        """
        Boucle principale du jeu.
        """
        if not self.player or not self.current_location:
            self.print_error("Joueur ou localisation non définis, impossible de démarrer le jeu.")
            return
        
        # Récupérer la référence au GameMaster (via narrative_engine qui est défini par set_narrative_engine)
        game_master = getattr(self.narrative_engine, 'game_master', None)
        
        # Démarrer la boucle de jeu du GameMaster s'il existe
        if game_master:
            game_master.game_loop(ui_callback=self.update_game_state)
        
        # Afficher la description initiale de la localisation
        self._display_current_location()
        
        # Démarrer la boucle de commandes
        exit_commands = ["quitter", "exit", "quit", "q"]
        
        while self.game_running:
            command = self.input("Que voulez-vous faire")
            
            # Vérifier si c'est une commande de sortie
            if command.lower() in exit_commands:
                if self.ask_yes_no("Êtes-vous sûr de vouloir quitter le jeu?", False):
                    self.print("Au revoir!")
                    self.game_running = False
                    break
                else:
                    continue
            
            # Exécuter la commande
            try:
                result = self.command_parser.parse_and_execute(command)
                if result and isinstance(result, str):
                    self.print_mj(result)  # Utilisez print_mj pour les réponses narratives
                    
                    # Mettre à jour l'état du jeu après chaque action si game_master existe
                    if game_master:
                        game_master.update_game_state(result)
                        
            except Exception as e:
                self.print_error(f"Erreur lors de l'exécution de la commande: {str(e)}")
                
    def print_mj(self, text: str) -> None:
        """
        Affiche un message provenant du Maître du Jeu avec formatage spécial.
        
        Args:
            text: Texte à afficher
        """
        self.print(text, color="mj", bold=False, delay=self.scene_delay)
    
    def display_saves(self, saves: List[Dict]) -> str:
        """
        Affiche la liste des sauvegardes et permet d'en choisir une.
        
        Args:
            saves: Liste des dictionnaires contenant les métadonnées des sauvegardes
            
        Returns:
            str: Chemin de la sauvegarde choisie, ou None si annulé
        """
        if not saves:
            self.print("Aucune sauvegarde disponible.")
            return None
            
        self.print_header("Sauvegardes disponibles")
        
        # Formater les options d'affichage
        options = []
        for save in saves:
            # Extraire la durée de jeu en format lisible
            game_time = save.get('game_time', 0)
            hours = int(game_time // 3600)
            minutes = int((game_time % 3600) // 60)
            time_str = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"
            
            # Format: "Monde - Joueur - Date (durée)"
            save_info = f"{save['world_name']} - {save['player_name']} - {save['date']} ({time_str})"
            options.append(save_info)
            
        # Ajouter l'option d'annulation
        options.append("Annuler")
        
        # Afficher le menu et récupérer le choix
        choice = self.display_menu(
            title="Choisissez une sauvegarde",
            options=options,
            prompt="Sauvegarde",
            color="cyan"
        )
        
        # Si l'utilisateur a choisi "Annuler" (dernière option)
        if choice == len(options) - 1:
            return None
            
        # Retourner le chemin de la sauvegarde choisie
        return saves[choice]['path']
        
    def load_game_dialog(self, game_master) -> bool:
        """
        Affiche un dialogue pour charger une partie sauvegardée.
        
        Args:
            game_master: Instance du GameMaster
            
        Returns:
            bool: True si une partie a été chargée, False sinon
        """
        # Lister les sauvegardes disponibles
        saves = game_master.list_saves()
        
        if not saves:
            self.print_warning("Aucune sauvegarde disponible.")
            self.wait_for_keypress()
            return False
        
        # Afficher le menu de sélection
        save_path = self.display_saves(saves)
        
        if not save_path:
            return False
            
        # Essayer de charger la sauvegarde
        success = game_master.load_game(save_path)
        
        if success:
            self.print_success(f"Partie chargée depuis {save_path}")
            
            # Mettre à jour l'interface avec le nouveau joueur et la nouvelle localisation
            self.set_player(game_master.player)
            self.set_current_location(game_master.get_current_location())
            
            # Afficher la localisation actuelle
            self._display_current_location()
            return True
        else:
            self.print_error("Échec du chargement de la sauvegarde.")
            return False
    
    def _display_current_location(self) -> None:
        """
        Affiche la description de la localisation actuelle.
        """
        if not self.current_location:
            self.print_warning("Aucune localisation définie.")
            return
        
        self.clear_screen()
        self.print_header(self.current_location.name)

        # Débogage: Afficher le type de lieu
        print(f"DEBUG - Type de lieu: {self.current_location.location_type}")
        print(f"DEBUG - Description brute: {self.current_location.description}")
        
        
        # Afficher la description - Utiliser get_formatted_description() au lieu de get_description()
        self.print_scene(self.current_location.get_formatted_description())
        
        # Afficher les sorties disponibles
        exits = self.current_location.get_exits()
        if exits:
            self.print("Sorties disponibles:", color="yellow", bold=True)
            for direction, location in exits.items():
                self.print(f"  {direction}: {location.name}")
        else:
            self.print("Aucune sortie visible.", color="yellow")
        
        # Afficher les objets présents
        items = self.current_location.get_items()
        if items:
            self.print("Objets visibles:", color="cyan", bold=True)
            for item in items:
                self.print(f"  - {item.name}")
        
        # Afficher les personnages présents
        npcs = self.current_location.get_npcs()
        if npcs:
            self.print("Personnages présents:", color="green", bold=True)
            for npc in npcs:
                self.print(f"  - {npc.name}")
        
        self.print_divider()
    
    def update_game_state(self) -> None:
        """
        Met à jour l'affichage de l'état du jeu.
        À appeler après des changements importants.
        """
        self._display_current_location()
    
    def display_player_status(self) -> None:
        """
        Affiche le statut actuel du joueur.
        """
        if not self.player:
            self.print_warning("Aucun joueur défini.")
            return
        
        self.print_subheader(f"Statut de {self.player.name}")
        
        # Afficher les attributs principaux
        self.print(f"Santé: {self.player.health}/{self.player.max_health}", color="red", bold=True)
        self.print(f"Énergie: {self.player.energy}/{self.player.max_energy}", color="blue", bold=True)
        
        # Afficher les compétences
        if hasattr(self.player, 'skills') and self.player.skills:
            self.print("Compétences:", color="magenta", bold=True)
            for skill, level in self.player.skills.items():
                self.print(f"  {skill}: {level}")
        
        self.print_divider()
    
    def display_inventory(self) -> None:
        """
        Affiche l'inventaire du joueur.
        """
        if not self.player:
            self.print_warning("Aucun joueur défini.")
            return
        
        items = self.player.get_inventory()
        
        self.print_subheader("Inventaire")
        
        if not items:
            self.print("Votre inventaire est vide.")
            return
        
        # Regrouper les objets par catégorie
        categories = {}
        for item in items:
            category = item.category if hasattr(item, 'category') else "Divers"
            if category not in categories:
                categories[category] = []
            categories[category].append(item)
        
        # Afficher par catégorie
        for category, cat_items in categories.items():
            self.print(f"{category}:", color="yellow", bold=True)
            for item in cat_items:
                desc = f" - {item.description}" if hasattr(item, 'description') else ""
                self.print(f"  {item.name}{desc}")
        
        self.print_divider()
    
    def display_combat(self, enemy_name: str, enemy_health: int, player_health: int) -> None:
        """
        Affiche une scène de combat.
        
        Args:
            enemy_name: Nom de l'ennemi
            enemy_health: Points de vie de l'ennemi
            player_health: Points de vie du joueur
        """
        self.clear_screen()
        self.print_header("COMBAT")
        
        # Afficher la situation
        self.print(f"Vous affrontez {enemy_name}!", color="red", bold=True)
        
        # Afficher les barres de vie
        self.print(f"Votre santé: ", wrap=False)
        self.display_progress_bar(
            progress=player_health,
            total=self.player.max_health if self.player else 100,
            width=20,
            char='♥',
            empty='♡',
            suffix=f" {player_health}/{self.player.max_health if self.player else 100}"
        )
        print()  # Nouvelle ligne
        
        self.print(f"Santé de {enemy_name}: ", wrap=False)
        self.display_progress_bar(
            progress=enemy_health,
            total=100,  # Valeur par défaut
            width=20,
            char='♦',
            empty='♢',
            suffix=f" {enemy_health}/100"
        )
        print()  # Nouvelle ligne
        
        self.print_divider()
    
    def display_combat_action(self, actor: str, action: str, result: str) -> None:
        """
        Affiche une action de combat.
        
        Args:
            actor: Nom de l'acteur (joueur ou ennemi)
            action: Description de l'action
            result: Résultat de l'action
        """
        self.print(f"{actor}: {action}", color="yellow", bold=True)
        self.print(f"Résultat: {result}", color="cyan")
        time.sleep(1)  # Pause dramatique
    
    def display_loot(self, items: List[Any]) -> None:
        """
        Affiche les objets récupérés.
        
        Args:
            items: Liste des objets récupérés
        """
        if not items:
            return
        
        self.print_subheader("Objets récupérés")
        
        for item in items:
            self.print(f"- {item.name}", color="green")
            if hasattr(item, 'description') and item.description:
                self.print(f"  {item.description}")
        
        self.print_divider()
    
    def display_game_over(self, reason: str = "Vous avez succombé à vos blessures.") -> None:
        """
        Affiche l'écran de fin de partie (défaite).
        
        Args:
            reason: Raison de la défaite
        """
        super().display_game_over(
            message="GAME OVER",
            reason=reason,
            ascii_art=self.ascii_art.get('game_over')
        )
        self.game_running = False
    
    def display_victory(self, message: str = "Félicitations, vous avez réussi!") -> None:
        """
        Affiche l'écran de victoire.
        
        Args:
            message: Message de victoire
        """
        self.clear_screen()
        
        if 'victory' in self.ascii_art:
            self.print(self.ascii_art['victory'], color='green', wrap=False, centered=True)
        
        self.print('')
        self.print("VICTOIRE!", color='green', bold=True, centered=True)
        
        self.print('')
        self.print(message, centered=True)
        
        self.print('')
        self.print_divider('=')
        self.print("Appuyez sur Entrée pour continuer...", centered=True)
        input()
        
        self.game_running = False
    
    def display_conversation(self, npc_name: str, dialogue_options: List[str]) -> int:
        """
        Affiche une conversation avec un PNJ et des options de dialogue.
        
        Args:
            npc_name: Nom du PNJ
            dialogue_options: Liste des options de dialogue
            
        Returns:
            int: Indice de l'option choisie
        """
        self.print_subheader(f"Conversation avec {npc_name}")
        
        return self.display_menu(
            title=f"{npc_name} attend votre réponse",
            options=dialogue_options,
            prompt="Choisissez votre réponse",
            color="cyan"
        )
    
    def display_npc_speech(self, npc_name: str, text: str) -> None:
        """
        Affiche un discours de PNJ.
        
        Args:
            npc_name: Nom du PNJ
            text: Texte du discours
        """
        self.print_dialogue(npc_name, text, color="cyan", delay=0.02)
    
    def display_player_speech(self, text: str) -> None:
        """
        Affiche un discours du joueur.
        
        Args:
            text: Texte du discours
        """
        player_name = self.player.name if self.player else "Vous"
        self.print_dialogue(player_name, text, color="green", delay=0.01)
    
    def display_quest_update(self, quest_title: str, update_text: str, completed: bool = False) -> None:
        """
        Affiche une mise à jour de quête.
        
        Args:
            quest_title: Titre de la quête
            update_text: Texte de mise à jour
            completed: Si la quête est terminée
        """
        if completed:
            self.print_subheader(f"Quête terminée: {quest_title}")
            self.print(update_text, color="green", bold=True)
        else:
            self.print_subheader(f"Mise à jour de quête: {quest_title}")
            self.print(update_text, color="yellow")
        
        self.print_divider()
        self.wait_for_keypress()
    
    def display_level_up(self, new_level: int, gained_stats: Dict[str, int]) -> None:
        """
        Affiche une notification de montée de niveau.
        
        Args:
            new_level: Nouveau niveau
            gained_stats: Statistiques gagnées
        """
        self.print_subheader("NIVEAU SUPÉRIEUR!")
        
        self.print(f"Vous êtes maintenant niveau {new_level}!", color="magenta", bold=True)
        
        if gained_stats:
            self.print("Vous avez gagné:", color="yellow")
            for stat, value in gained_stats.items():
                self.print(f"  {stat}: +{value}", color="green")
        
        self.print_divider()
        self.wait_for_keypress()
    
    def display_save_game_menu(self, save_slots: List[Dict[str, Any]]) -> Optional[int]:
        """
        Affiche le menu de sauvegarde du jeu.
        
        Args:
            save_slots: Liste des emplacements de sauvegarde avec leurs informations
            
        Returns:
            Optional[int]: Indice de l'emplacement choisi, ou None si annulé
        """
        self.clear_screen()
        self.print_header("Sauvegarder la partie")
        
        # Créer les options d'affichage
        options = []
        for slot in save_slots:
            if slot['used']:
                # Format: "1. [Date] - Niveau 5 - Localisation"
                options.append(f"[{slot['date']}] - {slot['player_info']} - {slot['location_info']}")
            else:
                options.append("<Emplacement vide>")
        
        # Ajouter une option pour annuler
        options.append("Annuler")
        
        # Afficher le menu
        choice = self.display_menu(
            title="Choisissez un emplacement de sauvegarde",
            options=options,
            prompt="Emplacement",
            color="cyan"
        )
        
        # Si l'utilisateur a choisi "Annuler" (dernière option)
        if choice == len(options) - 1:
            return None
        
        # Confirmation si l'emplacement est déjà utilisé
        if save_slots[choice]['used']:
            if not self.ask_yes_no(f"Écraser la sauvegarde existante?", False):
                return None
        
        return choice
    
    def display_load_game_menu(self, save_slots: List[Dict[str, Any]]) -> Optional[int]:
        """
        Affiche le menu de chargement du jeu.
        
        Args:
            save_slots: Liste des emplacements de sauvegarde avec leurs informations
            
        Returns:
            Optional[int]: Indice de l'emplacement choisi, ou None si annulé
        """
        self.clear_screen()
        self.print_header("Charger une partie")
        
        # Filtrer les emplacements utilisés
        used_slots = [(i, slot) for i, slot in enumerate(save_slots) if slot['used']]
        
        if not used_slots:
            self.print("Aucune sauvegarde disponible.", color="yellow")
            self.wait_for_keypress()
            return None
        
        # Créer les options d'affichage
        options = []
        for _, slot in used_slots:
            # Format: "[Date] - Niveau 5 - Localisation"
            options.append(f"[{slot['date']}] - {slot['player_info']} - {slot['location_info']}")
        
        # Ajouter une option pour annuler
        options.append("Annuler")
        
        # Afficher le menu
        choice = self.display_menu(
            title="Choisissez une sauvegarde à charger",
            options=options,
            prompt="Sauvegarde",
            color="cyan"
        )
        
        # Si l'utilisateur a choisi "Annuler" (dernière option)
        if choice == len(options) - 1:
            return None
        
        # Retourner l'indice réel
        return used_slots[choice][0]
    
    def display_main_menu(self) -> str:
        """
        Affiche le menu principal du jeu.
        
        Returns:
            str: Option choisie ('new', 'load', 'options', 'quit')
        """
        self.clear_screen()
        
        # Afficher le logo du jeu
        if 'title' in self.ascii_art:
            self.print(self.ascii_art['title'], color='cyan', wrap=False, centered=True)
        
        options = [
            "Nouvelle partie",
            "Charger une partie",
            "Options",
            "Quitter"
        ]
        
        choice = self.display_menu(
            title="Menu Principal",
            options=options,
            prompt="Choisissez une option",
            color="magenta"
        )
        
        # Convertir le choix en valeur de retour
        menu_actions = ['new', 'load', 'options', 'quit']
        return menu_actions[choice]
    
    def display_options_menu(self) -> None:
        """
        Affiche le menu des options du jeu.
        """
        while True:
            self.clear_screen()
            self.print_header("Options")
            
            options = [
                f"Couleurs: {'Activées' if self.use_colors else 'Désactivées'}",
                f"Vitesse de texte: {'Rapide' if self.text_speed == 'fast' else 'Normale' if self.text_speed == 'normal' else 'Lente'}",
                "Retour au menu principal"
            ]
            
            choice = self.display_menu(
                title="Options du jeu",
                options=options,
                prompt="Choisissez une option",
                color="cyan"
            )
            
            if choice == 0:  # Couleurs
                self.use_colors = not self.use_colors
            elif choice == 1:  # Vitesse de texte
                speeds = ['fast', 'normal', 'slow']
                current_index = speeds.index(getattr(self, 'text_speed', 'normal'))
                next_index = (current_index + 1) % len(speeds)
                self.text_speed = speeds[next_index]
            elif choice == 2:  # Retour
                break
    
    @property
    def text_speed(self) -> str:
        """
        Récupère la vitesse de texte actuelle.
        
        Returns:
            str: Vitesse de texte ('fast', 'normal', 'slow')
        """
        if not hasattr(self, '_text_speed'):
            self._text_speed = 'normal'
        return self._text_speed
    
    @text_speed.setter
    def text_speed(self, value: str) -> None:
        """
        Définit la vitesse de texte.
        
        Args:
            value: Nouvelle vitesse ('fast', 'normal', 'slow')
        """
        if value not in ('fast', 'normal', 'slow'):
            raise ValueError("Vitesse de texte invalide. Valeurs acceptées: 'fast', 'normal', 'slow'")
        
        self._text_speed = value
        
        # Ajuster les délais en fonction de la vitesse
        if value == 'fast':
            self.scene_delay = 0.01
            self.dialogue_delay = 0.005
        elif value == 'normal':
            self.scene_delay = 0.03
            self.dialogue_delay = 0.02
        else:  # slow
            self.scene_delay = 0.05
            self.dialogue_delay = 0.03