#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GameMaster - Le MJ IA qui gère le monde du jeu
"""

import os
import json
import time
import logging
from typing import Dict, List, Any, Optional, Tuple

from core.narrative_engine import NarrativeEngine
from core.world_generator import WorldGenerator
from core.coherence_checker import CoherenceChecker
from entities.player import Player
from entities.npc import NPC
from entities.location import Location
from entities.item import Item
from memory.global_memory import GlobalMemory

# Configuration du système de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='z_dungeon_core.log'
)
logger = logging.getLogger('GameMaster')

class GameMaster:
    """
    Le Maître du Jeu qui gère tous les aspects du monde de jeu.
    Il coordonne les différents composants du système et maintient la cohérence narrative.
    """
    
    def __init__(self, world_config: Dict[str, Any], save_path: Optional[str] = None):
        """
        Initialise le GameMaster avec une configuration de monde.
        
        Args:
            world_config: Configuration du monde (nom, ambiance, règles, etc.)
            save_path: Chemin vers un fichier de sauvegarde pour reprendre une partie existante
        """
        self.world_config = world_config
        self.save_path = save_path
        self.name = world_config.get('nom', 'Monde sans nom')
        
        # Initialisation des composants centraux
        self.narrative_engine = NarrativeEngine()
        self.world_generator = WorldGenerator(world_config)
        self.coherence_checker = CoherenceChecker()
        
        # Préparation de l'ID du monde pour la mémoire globale
        world_id = self.world_config.get('id')
        if not world_id:
            # Créer un slug à partir du nom (plus stable que hash())
            import re
            world_id = re.sub('[^a-z0-9]+','_', self.name.lower()).strip('_')
            logger.info(f"ID de monde non défini dans le fichier de configuration. Utilisation de '{world_id}' comme fallback.")
        
        # Initialisation de la mémoire globale avec les identifiants du monde
        self.global_memory = GlobalMemory(world_id=world_id, world_name=self.name)
        
        # Collections d'entités
        self.locations: Dict[str, Location] = {}
        self.npcs: Dict[str, NPC] = {}
        self.items: Dict[str, Item] = {}
        self.player: Optional[Player] = None
        
        # État du jeu
        self.current_location_id: Optional[str] = None
        self.game_start_time = None
        self.session_history = []
        
        # Si un fichier de sauvegarde est fourni, charger l'état du jeu
        if save_path and os.path.exists(save_path):
            self._load_game_state(save_path)
        else:
            self._initialize_new_game()
    
    def _initialize_new_game(self):
        """Initialise un nouveau jeu en générant le monde et les entités."""
        logger.info(f"Initialisation d'un nouveau jeu dans le monde: {self.name}")
        
        # Initialisation de la mémoire globale avec les identifiants du monde
        # Utiliser l'ID défini dans le fichier YAML, ou générer un slug basé sur le nom si non défini
        world_id = self.world_config.get('id')
        if not world_id:
            # Créer un slug à partir du nom (plus stable que hash())
            import re
            world_id = re.sub('[^a-z0-9]+','_', self.name.lower()).strip('_')
            logger.info(f"ID de monde non défini dans le fichier de configuration. Utilisation de '{world_id}' comme fallback.")
            
        self.global_memory = GlobalMemory(world_id=world_id, world_name=self.name)
        
        # Génération du monde initial
        generated_world = self.world_generator.generate()
        
        # Création des lieux
        for location_data in generated_world.get('locations', []):
            location = Location.from_dict(location_data)
            self.locations[location.id] = location
        
        # Création des PNJ
        for npc_data in generated_world.get('npcs', []):
            npc = NPC.from_dict(npc_data)
            self.npcs[npc.id] = npc
            
            # Ajouter le PNJ à son lieu de départ
            if npc.location_id and npc.location_id in self.locations:
                self.locations[npc.location_id].add_npc(npc.id)
        
        # Création des objets
        for item_data in generated_world.get('items', []):
            item = Item.from_dict(item_data)
            self.items[item.id] = item
            
            # Ajouter l'objet à son lieu de départ
            if item.location_id and item.location_id in self.locations:
                self.locations[item.location_id].add_item(item.id)
        
        # Sélection du lieu de départ
        if self.locations:
            self.current_location_id = list(self.locations.keys())[0]
        
        # Initialisation de l'horodatage de début de jeu
        self.game_start_time = time.time()
        
        logger.info(f"Monde initialisé avec {len(self.locations)} lieux, {len(self.npcs)} PNJ et {len(self.items)} objets")
    
    def _load_game_state(self, save_path: str):
        """Charge l'état du jeu à partir d'un fichier de sauvegarde."""
        try:
            with open(save_path, 'r', encoding='utf-8') as file:
                saved_state = json.load(file)
            
            # Charger les lieux
            for location_data in saved_state.get('locations', []):
                location = Location.from_dict(location_data)
                self.locations[location.id] = location
            
            # Charger les PNJ
            for npc_data in saved_state.get('npcs', []):
                npc = NPC.from_dict(npc_data)
                self.npcs[npc.id] = npc
            
            # Charger les objets
            for item_data in saved_state.get('items', []):
                item = Item.from_dict(item_data)
                self.items[item.id] = item
            
            # Charger le joueur
            if 'player' in saved_state:
                self.player = Player.from_dict(saved_state['player'])
            
            # Charger les autres états
            self.current_location_id = saved_state.get('current_location_id')
            self.game_start_time = saved_state.get('game_start_time', time.time())
            self.session_history = saved_state.get('session_history', [])
            
            # Charger la mémoire globale
            if 'global_memory' in saved_state:
                self.global_memory.load_from_dict(saved_state['global_memory'])
            
            logger.info(f"Jeu chargé depuis {save_path}")
        except Exception as e:
            logger.error(f"Erreur lors du chargement de la sauvegarde: {str(e)}")
            # En cas d'erreur, initialiser un nouveau jeu
            self._initialize_new_game()
    
    def save_game(self, save_path: Optional[str] = None):
        """
        Sauvegarde l'état actuel du jeu avec gestion des versions.
        
        Args:
            save_path: Chemin vers le fichier de sauvegarde (optionnel)
            
        Returns:
            bool: True si la sauvegarde a réussi, False sinon
        """
        # Générer un nom de fichier si aucun n'est spécifié
        if not save_path:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            world_name = self.name.lower().replace(' ', '_')
            save_path = os.path.join('saves', f"{world_name}_{timestamp}.json")
        
        # Créer le dossier saves s'il n'existe pas
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        # Créer un dictionnaire avec toutes les données du jeu
        state = {
            'game_version': "2.0",  # Version du jeu pour compatibilité future
            'save_date': time.strftime("%Y-%m-%d %H:%M:%S"),
            'world_config': self.world_config,
            'locations': [location.to_dict() for location in self.locations.values()],
            'npcs': [npc.to_dict() for npc in self.npcs.values()],
            'items': [item.to_dict() for item in self.items.values()],
            'current_location_id': self.current_location_id,
            'game_start_time': self.game_start_time,
            'game_time': time.time() - self.game_start_time,  # Durée de jeu en secondes
            'session_history': self.session_history[-100:],  # Limiter pour éviter des fichiers trop gros
            'global_memory': self.global_memory.to_dict()
        }
        
        if self.player:
            state['player'] = self.player.to_dict()
        
        try:
            # Sauvegarde avec formatage lisible
            with open(save_path, 'w', encoding='utf-8') as file:
                json.dump(state, file, ensure_ascii=False, indent=2)
            
            logger.info(f"Jeu sauvegardé dans {save_path}")
            
            # Créer également un lien symbolique vers la dernière sauvegarde
            latest_save = os.path.join('saves', f"{world_name}_latest.json")
            if os.path.exists(latest_save):
                os.remove(latest_save)
            os.symlink(os.path.basename(save_path), latest_save)
            
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde: {str(e)}")
            return False
    
    def load_game(self, save_path: str):
        """
        Charge l'état du jeu à partir d'un fichier de sauvegarde.
        
        Args:
            save_path: Chemin vers le fichier de sauvegarde
            
        Returns:
            bool: True si le chargement a réussi, False sinon
        """
        if not os.path.exists(save_path):
            logger.error(f"Le fichier de sauvegarde {save_path} n'existe pas")
            return False
        
        try:
            with open(save_path, 'r', encoding='utf-8') as file:
                saved_state = json.load(file)
            
            # Vérifier la compatibilité des versions
            save_version = saved_state.get('game_version', '1.0')
            if save_version != "2.0":
                logger.warning(f"Version de sauvegarde {save_version} différente de la version actuelle 2.0")
                # TODO: Implémenter une migration de version si nécessaire
            
            # Réinitialiser l'état actuel
            self.locations = {}
            self.npcs = {}
            self.items = {}
            self.player = None
            self.session_history = []
            
            # Charger la configuration du monde
            self.world_config = saved_state.get('world_config', {})
            self.name = self.world_config.get('nom', 'Monde sans nom')
            
            # Charger les lieux
            for location_data in saved_state.get('locations', []):
                location = Location.from_dict(location_data)
                self.locations[location.id] = location
            
            # Charger les PNJ
            for npc_data in saved_state.get('npcs', []):
                npc = NPC.from_dict(npc_data)
                self.npcs[npc.id] = npc
            
            # Charger les objets
            for item_data in saved_state.get('items', []):
                item = Item.from_dict(item_data)
                self.items[item.id] = item
            
            # Charger le joueur
            if 'player' in saved_state:
                self.player = Player.from_dict(saved_state['player'])
            
            # Charger les autres états
            self.current_location_id = saved_state.get('current_location_id')
            self.game_start_time = saved_state.get('game_start_time', time.time())
            self.session_history = saved_state.get('session_history', [])
            
            # Charger la mémoire globale
            if 'global_memory' in saved_state:
                self.global_memory = GlobalMemory()
                self.global_memory.load_from_dict(saved_state['global_memory'])
            
            logger.info(f"Jeu chargé depuis {save_path}")
            return True
        except Exception as e:
            logger.error(f"Erreur lors du chargement de la sauvegarde: {str(e)}")
            # En cas d'erreur, initialiser un nouveau jeu
            return False
    
    def list_saves(self):
        """
        Liste toutes les sauvegardes disponibles.
        
        Returns:
            List[Dict]: Liste des sauvegardes avec leurs métadonnées
        """
        saves = []
        saves_dir = 'saves'
        
        if not os.path.exists(saves_dir):
            return saves
            
        for file in os.listdir(saves_dir):
            if not file.endswith('.json'):
                continue
                
            path = os.path.join(saves_dir, file)
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                saves.append({
                    'filename': file,
                    'path': path,
                    'date': data.get('save_date', 'Inconnue'),
                    'world_name': data.get('world_config', {}).get('nom', 'Monde inconnu'),
                    'player_name': data.get('player', {}).get('name', 'Joueur inconnu'),
                    'game_time': data.get('game_time', 0)
                })
            except:
                # Si le fichier est corrompu, l'ajouter quand même avec des données partielles
                saves.append({
                    'filename': file,
                    'path': path,
                    'date': 'Fichier corrompu',
                    'world_name': 'Erreur',
                    'player_name': 'Erreur',
                    'game_time': 0
                })
                
        # Tri par date, du plus récent au plus ancien
        saves.sort(key=lambda x: x['date'], reverse=True)
        return saves
    
    def create_player(self, name: str, description: str = ""):
        """Crée un nouveau personnage joueur."""
        self.player = Player(name=name, description=description)
        self.player.location_id = self.current_location_id
        logger.info(f"Nouveau joueur créé: {name}")
        return self.player
    
    def get_current_location(self) -> Optional[Location]:
        """Retourne le lieu actuel où se trouve le joueur."""
        if not self.current_location_id:
            return None
        return self.locations.get(self.current_location_id)
    
    def move_player_to(self, location_id: str) -> Tuple[bool, str]:
        """
        Déplace le joueur vers un nouveau lieu.
        
        Returns:
            Tuple[bool, str]: (Succès, Message)
        """
        if location_id not in self.locations:
            return False, f"Le lieu '{location_id}' n'existe pas."
        
        old_location = self.get_current_location()
        if old_location:
            old_location.remove_character(self.player.id)
        
        self.current_location_id = location_id
        self.locations[location_id].add_character(self.player.id)
        
        if self.player:
            self.player.location_id = location_id
        
        return True, f"Vous êtes maintenant à {self.locations[location_id].name}."
    
    def process_player_action(self, action_text: str) -> str:
        """
        Traite une action du joueur et retourne la réponse narrative.
        
        Args:
            action_text: Le texte décrivant l'action du joueur
            
        Returns:
            str: La réponse narrative générée par le MJ
        """
        if not self.player:
            return "Vous devez d'abord créer un personnage."
        
        # Enregistrer l'action dans l'historique
        self.session_history.append({
            'type': 'player_action',
            'text': action_text,
            'timestamp': time.time()
        })
        
        # Récupérer le contexte actuel du jeu
        current_location = self.get_current_location()
        if not current_location:
            return "Erreur: Position actuelle inconnue."
        
        # Construire le contexte pour le moteur narratif
        context = {
            'player': self.player,
            'location': current_location,
            'npcs': [self.npcs[npc_id] for npc_id in current_location.npc_ids if npc_id in self.npcs],
            'items': [self.items[item_id] for item_id in current_location.item_ids if item_id in self.items],
            'world_config': self.world_config,
            'history': self.session_history[-10:] if len(self.session_history) > 10 else self.session_history
        }
        
        # Vérifier la cohérence de l'action
        coherence_check = self.coherence_checker.check_action(action_text, context)
        
        # Si l'action n'est pas cohérente, générer une correction narrative
        if not coherence_check['is_coherent']:
            response = self.narrative_engine.generate_correction(
                action_text, 
                coherence_check['reason'],
                context
            )
        else:
            # Sinon, générer une réponse standard
            response = self.narrative_engine.generate_response(action_text, context)
        
        # Enregistrer la réponse dans l'historique
        self.session_history.append({
            'type': 'gm_response',
            'text': response,
            'timestamp': time.time()
        })
        
        # Mettre à jour la mémoire globale
        self.global_memory.add_memory(action_text, response)
        
        return response
    
    def get_available_commands(self) -> List[str]:
        """
        Retourne la liste des commandes disponibles pour le joueur.
        Ces commandes sont basées sur les actions possibles dans le contexte actuel.
        """
        commands = [
            "regarder", "examiner [objet/personne]", "parler à [personne]",
            "prendre [objet]", "utiliser [objet]", "aller à [lieu]",
            "inventaire", "aide", "quitter", "sauvegarder"
        ]
        return commands
        
    def game_loop(self, ui_callback=None):
        """
        Gère la boucle principale du jeu en suivant une state machine claire:
        1. Tour du joueur (entrée)
        2. Analyse de l'action
        3. Réponse du LLM
        4. Mise à jour de la mémoire et du monde
        5. Retour au joueur
        
        Args:
            ui_callback: Fonction à appeler pour mettre à jour l'interface après chaque tour
        """
        logger.info("Démarrage de la boucle de jeu")
        
        # Vérifier que le joueur existe
        if not self.player:
            logger.error("Impossible de démarrer la boucle de jeu: aucun joueur créé")
            return False
            
        # Message d'introduction
        current_location = self.get_current_location()
        if current_location:
            intro_context = {
                'player': self.player,
                'location': current_location,
                'npcs': [self.npcs[npc_id] for npc_id in current_location.npc_ids if npc_id in self.npcs],
                'items': [self.items[item_id] for item_id in current_location.item_ids if item_id in self.items],
                'world_config': self.world_config
            }
            intro = self.narrative_engine.generate_introduction(intro_context)
            
            # Ajouter l'introduction à l'historique
            self.session_history.append({
                'type': 'intro',
                'text': intro,
                'timestamp': time.time()
            })
            
            # Mettre à jour la mémoire globale
            self.global_memory.add_memory("début de l'aventure", intro)
            
        # Démarrer la state machine du jeu
        self.game_running = True
        
        # Notifier l'interface
        if ui_callback:
            ui_callback(self)
            
        return True
    
    def update_game_state(self, action_result=None):
        """
        Met à jour l'état du jeu après une action du joueur.
        Cette méthode peut être utilisée pour déclencher des événements basés sur l'état du monde,
        les conditions temporelles, ou les objectifs de quête.
        
        Args:
            action_result: Le résultat de la dernière action du joueur
        """
        # Mise à jour des PNJ (comportements, déplacements)
        # TODO: Implémenter les comportements des PNJ
        
        # Vérification des conditions de quête/progression
        # TODO: Implémenter un système de quêtes
        
        # Événements temporels/programmés
        # TODO: Implémenter un système d'événements basé sur le temps ou les actions
        
        # Vérifier la cohérence globale du monde
        coherence_issues = self.coherence_checker.check_world_state({
            'player': self.player,
            'current_location': self.get_current_location(),
            'npcs': self.npcs,
            'items': self.items,
            'history': self.session_history[-20:] if len(self.session_history) > 20 else self.session_history
        })
        
        if coherence_issues:
            logger.warning(f"Problèmes de cohérence détectés: {coherence_issues}")
            # TODO: Corriger automatiquement les incohérences mineures
        
        # Sauvegarder l'état du jeu à intervalles réguliers (auto-save)
        if len(self.session_history) % 10 == 0:  # Tous les 10 tours
            autosave_path = os.path.join('saves', f"autosave_{self.name.lower().replace(' ', '_')}.json")
            self.save_game(autosave_path)
            
        return True