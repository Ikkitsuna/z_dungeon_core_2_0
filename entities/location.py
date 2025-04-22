#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Location - Classe représentant les lieux du monde
"""

from typing import Dict, List, Any, Optional, Set

from .entity import Entity

class Location(Entity):
    """
    Classe représentant un lieu dans le monde du jeu.
    Étend Entity avec des fonctionnalités spécifiques aux lieux.
    """
    
    def __init__(
            self, 
            name: str, 
            description: str = "", 
            entity_id: Optional[str] = None,
            location_type: str = "generic",
            is_main: bool = False
        ):
        """
        Initialise un nouveau lieu.
        
        Args:
            name: Nom du lieu
            description: Description du lieu
            entity_id: Identifiant unique (généré automatiquement si non fourni)
            location_type: Type de lieu (village, forêt, donjon, etc.)
            is_main: Indique si c'est un lieu principal
        """
        super().__init__(name, description, entity_id)
        
        # Propriétés du lieu
        self.location_type = location_type
        self.is_main = is_main
        
        # Connexions à d'autres lieux (IDs)
        self.connected_locations = []
        
        # Entités présentes dans ce lieu
        self.npc_ids = []      # IDs des PNJs présents
        self.item_ids = []     # IDs des objets présents
        self.character_ids = []  # IDs des personnages joueurs présents (pour multijoueur)
        
        # État du lieu et ambiance
        self.state = "normal"  # État actuel (normal, danger, sécurité, etc.)
        self.mood = ""         # Ambiance (sombre, joyeuse, mystérieuse, etc.)
        self.time_of_day = ""  # Heure du jour (matin, midi, soir, nuit)
        self.weather = ""      # Météo (ensoleillé, pluvieux, brumeux, etc.)
        
        # Points d'intérêt dans ce lieu
        self.points_of_interest = []
        
        # Événements associés à ce lieu
        self.events = []
        
        # Restrictions d'accès
        self.access_restricted = False
        self.access_requirements = {}
    
    def connect_to(self, location_id: str) -> None:
        """
        Connecte ce lieu à un autre lieu.
        
        Args:
            location_id: ID du lieu à connecter
        """
        if location_id not in self.connected_locations:
            self.connected_locations.append(location_id)
            self._mark_modified()
    
    def disconnect_from(self, location_id: str) -> None:
        """
        Supprime une connexion vers un autre lieu.
        
        Args:
            location_id: ID du lieu à déconnecter
        """
        if location_id in self.connected_locations:
            self.connected_locations.remove(location_id)
            self._mark_modified()
    
    def is_connected_to(self, location_id: str) -> bool:
        """
        Vérifie si ce lieu est connecté à un autre lieu.
        
        Args:
            location_id: ID du lieu à vérifier
            
        Returns:
            bool: True si les lieux sont connectés, False sinon
        """
        return location_id in self.connected_locations
    
    def add_npc(self, npc_id: str) -> None:
        """
        Ajoute un PNJ à ce lieu.
        
        Args:
            npc_id: ID du PNJ à ajouter
        """
        if npc_id not in self.npc_ids:
            self.npc_ids.append(npc_id)
            self._mark_modified()
    
    def remove_npc(self, npc_id: str) -> None:
        """
        Retire un PNJ de ce lieu.
        
        Args:
            npc_id: ID du PNJ à retirer
        """
        if npc_id in self.npc_ids:
            self.npc_ids.remove(npc_id)
            self._mark_modified()
    
    def add_item(self, item_id: str) -> None:
        """
        Ajoute un objet à ce lieu.
        
        Args:
            item_id: ID de l'objet à ajouter
        """
        if item_id not in self.item_ids:
            self.item_ids.append(item_id)
            self._mark_modified()
    
    def remove_item(self, item_id: str) -> None:
        """
        Retire un objet de ce lieu.
        
        Args:
            item_id: ID de l'objet à retirer
        """
        if item_id in self.item_ids:
            self.item_ids.remove(item_id)
            self._mark_modified()
    
    def add_character(self, character_id: str) -> None:
        """
        Ajoute un personnage joueur à ce lieu.
        
        Args:
            character_id: ID du personnage à ajouter
        """
        if character_id not in self.character_ids:
            self.character_ids.append(character_id)
            self._mark_modified()
    
    def remove_character(self, character_id: str) -> None:
        """
        Retire un personnage joueur de ce lieu.
        
        Args:
            character_id: ID du personnage à retirer
        """
        if character_id in self.character_ids:
            self.character_ids.remove(character_id)
            self._mark_modified()
    
    def set_state(self, state: str) -> None:
        """
        Définit l'état actuel du lieu.
        
        Args:
            state: Nouvel état
        """
        self.state = state
        self._mark_modified()
    
    def set_mood(self, mood: str) -> None:
        """
        Définit l'ambiance du lieu.
        
        Args:
            mood: Nouvelle ambiance
        """
        self.mood = mood
        self._mark_modified()
    
    def set_time_of_day(self, time_of_day: str) -> None:
        """
        Définit l'heure du jour dans ce lieu.
        
        Args:
            time_of_day: Nouvelle heure du jour
        """
        self.time_of_day = time_of_day
        self._mark_modified()
    
    def set_weather(self, weather: str) -> None:
        """
        Définit la météo dans ce lieu.
        
        Args:
            weather: Nouvelle météo
        """
        self.weather = weather
        self._mark_modified()
    
    def add_point_of_interest(self, name: str, description: str) -> None:
        """
        Ajoute un point d'intérêt au lieu.
        
        Args:
            name: Nom du point d'intérêt
            description: Description du point d'intérêt
        """
        poi = {
            'name': name,
            'description': description
        }
        self.points_of_interest.append(poi)
        self._mark_modified()
    
    def get_point_of_interest(self, name: str) -> Optional[Dict[str, str]]:
        """
        Récupère un point d'intérêt par son nom.
        
        Args:
            name: Nom du point d'intérêt
            
        Returns:
            Optional[Dict[str, str]]: Point d'intérêt ou None si non trouvé
        """
        for poi in self.points_of_interest:
            if poi['name'].lower() == name.lower():
                return poi
        return None
    
    def add_event(self, event_type: str, description: str, trigger: Optional[str] = None) -> None:
        """
        Ajoute un événement au lieu.
        
        Args:
            event_type: Type d'événement
            description: Description de l'événement
            trigger: Condition de déclenchement (optionnel)
        """
        event = {
            'type': event_type,
            'description': description,
            'trigger': trigger,
            'triggered': False
        }
        self.events.append(event)
        self._mark_modified()
    
    def set_access_restriction(self, restricted: bool, requirements: Optional[Dict[str, Any]] = None) -> None:
        """
        Définit des restrictions d'accès pour ce lieu.
        
        Args:
            restricted: True si l'accès est restreint
            requirements: Conditions requises pour accéder au lieu
        """
        self.access_restricted = restricted
        self.access_requirements = requirements or {}
        self._mark_modified()
    
    def can_access(self, entity_data: Dict[str, Any]) -> bool:
        """
        Vérifie si une entité peut accéder à ce lieu selon les restrictions.
        
        Args:
            entity_data: Données de l'entité tentant d'accéder
            
        Returns:
            bool: True si l'accès est autorisé, False sinon
        """
        # Si pas de restriction, l'accès est toujours autorisé
        if not self.access_restricted:
            return True
        
        # Vérifier chaque condition d'accès
        for key, value in self.access_requirements.items():
            # Si la condition concerne un objet requis
            if key == 'required_items':
                inventory = entity_data.get('inventory', [])
                if not all(item in inventory for item in value):
                    return False
            
            # Si la condition concerne un niveau minimum
            elif key == 'min_level':
                if entity_data.get('level', 0) < value:
                    return False
            
            # Si la condition concerne une quête complétée
            elif key == 'completed_quests':
                quests = entity_data.get('quests', {})
                if not all(quests.get(quest, {}).get('status') == 'completed' for quest in value):
                    return False
            
            # Autres conditions personnalisées...
        
        # Si toutes les conditions sont satisfaites
        return True
    
    def get_formatted_description(self) -> str:
        """
        Génère une description formatée du lieu incluant l'ambiance et la météo.
        
        Returns:
            str: Description formatée
        """
        desc = self.description
        
        # Ajouter l'ambiance si définie
        if self.mood:
            desc += f"\n\nL'ambiance est {self.mood}."
        
        # Ajouter l'heure du jour si définie
        if self.time_of_day:
            desc += f" C'est {self.time_of_day}."
        
        # Ajouter la météo si définie
        if self.weather:
            desc += f" Le temps est {self.weather}."
        
        return desc
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convertit le lieu en dictionnaire sérialisable.
        
        Returns:
            Dict[str, Any]: Représentation dictionnaire du lieu
        """
        # Obtenir le dictionnaire de base de l'entité
        data = super().to_dict()
        
        # Ajouter les propriétés spécifiques au lieu
        data.update({
            'location_type': self.location_type,
            'is_main': self.is_main,
            'connected_locations': self.connected_locations.copy(),
            'npc_ids': self.npc_ids.copy(),
            'item_ids': self.item_ids.copy(),
            'character_ids': self.character_ids.copy(),
            'state': self.state,
            'mood': self.mood,
            'time_of_day': self.time_of_day,
            'weather': self.weather,
            'points_of_interest': self.points_of_interest.copy(),
            'events': self.events.copy(),
            'access_restricted': self.access_restricted,
            'access_requirements': self.access_requirements.copy()
        })
        
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Location':
        """
        Crée un lieu à partir d'un dictionnaire sérialisé.
        
        Args:
            data: Dictionnaire contenant les données du lieu
            
        Returns:
            Location: Instance de lieu créée
        """
        # Créer l'instance avec les propriétés de base
        location = cls(
            name=data.get('name', 'Lieu sans nom'),
            description=data.get('description', ''),
            entity_id=data.get('id'),
            location_type=data.get('location_type', 'generic'),
            is_main=data.get('is_main', False)
        )
        
        # Définir les propriétés spécifiques au lieu
        location.connected_locations = data.get('connected_locations', []).copy()
        location.npc_ids = data.get('npc_ids', []).copy()
        location.item_ids = data.get('item_ids', []).copy()
        location.character_ids = data.get('character_ids', []).copy()
        location.state = data.get('state', 'normal')
        location.mood = data.get('mood', '')
        location.time_of_day = data.get('time_of_day', '')
        location.weather = data.get('weather', '')
        location.points_of_interest = data.get('points_of_interest', []).copy()
        location.events = data.get('events', []).copy()
        location.access_restricted = data.get('access_restricted', False)
        location.access_requirements = data.get('access_requirements', {}).copy()
        
        # Définir les propriétés héritées
        location.tags = data.get('tags', []).copy()
        location.metadata = data.get('metadata', {}).copy()
        location.created_at = data.get('created_at', location.created_at)
        location.modified_at = data.get('modified_at', location.modified_at)
        
        return location