#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Player - Classe du personnage joueur
"""

import uuid
from typing import Dict, List, Any, Optional, Set

from entities.entity import Entity

class Player(Entity):
    """
    Classe représentant le personnage du joueur.
    Étend Entity avec des fonctionnalités supplémentaires spécifiques au joueur.
    """
    
    def __init__(
            self, 
            name: str, 
            description: str = "", 
            entity_id: Optional[str] = None,
            inventory: Optional[List[str]] = None,
            location_id: Optional[str] = None
        ):
        """
        Initialise un nouveau personnage joueur.
        
        Args:
            name: Nom du joueur
            description: Description du joueur
            entity_id: Identifiant unique (généré automatiquement si non fourni)
            inventory: Liste des IDs d'objets dans l'inventaire
            location_id: ID du lieu où se trouve le joueur
        """
        super().__init__(name, description, entity_id)
        
        # Inventaire (liste d'IDs d'objets)
        self.inventory = inventory or []
        
        # Lieu actuel
        self.location_id = location_id
        
        # Mémoire du joueur (souvenirs importants)
        self.memories = []
        
        # Relations avec les PNJ
        self.relationships = {}
        
        # Statistiques de base
        self.health = 100
        self.max_health = 100
        self.energy = 100
        self.max_energy = 100
        
        # Progression
        self.level = 1
        self.experience = 0
        self.experience_to_level = 100
        
        # Quêtes et objectifs
        self.quests = {}
        self.objectives = []
        
        # Capacités et connaissances
        self.skills = {}
        self.knowledge = {}
    
    def add_to_inventory(self, item_id: str) -> None:
        """
        Ajoute un objet à l'inventaire du joueur.
        
        Args:
            item_id: ID de l'objet à ajouter
        """
        if item_id not in self.inventory:
            self.inventory.append(item_id)
            self._mark_modified()
    
    def remove_from_inventory(self, item_id: str) -> bool:
        """
        Supprime un objet de l'inventaire du joueur.
        
        Args:
            item_id: ID de l'objet à supprimer
            
        Returns:
            bool: True si l'objet a été supprimé, False sinon
        """
        if item_id in self.inventory:
            self.inventory.remove(item_id)
            self._mark_modified()
            return True
        return False
    
    def has_item(self, item_id: str) -> bool:
        """
        Vérifie si le joueur possède un objet spécifique.
        
        Args:
            item_id: ID de l'objet à vérifier
            
        Returns:
            bool: True si l'objet est dans l'inventaire, False sinon
        """
        return item_id in self.inventory
    
    def get_inventory(self) -> List[str]:
        """
        Récupère la liste des objets dans l'inventaire du joueur.
        
        Returns:
            List[str]: Liste des IDs d'objets dans l'inventaire
        """
        return self.inventory.copy()
    
    def add_memory(self, memory_text: str, importance: int = 5) -> None:
        """
        Ajoute un souvenir au joueur.
        
        Args:
            memory_text: Texte du souvenir
            importance: Importance du souvenir (1-10)
        """
        self.memories.append({
            'text': memory_text,
            'importance': importance,
            'timestamp': self._get_current_time()
        })
        self._mark_modified()
    
    def add_relationship(self, npc_id: str, attitude: str, strength: int = 5) -> None:
        """
        Définit ou met à jour la relation avec un PNJ.
        
        Args:
            npc_id: ID du PNJ
            attitude: Attitude envers le PNJ (positive, neutre, négative)
            strength: Force de la relation (1-10)
        """
        self.relationships[npc_id] = {
            'attitude': attitude,
            'strength': strength,
            'last_updated': self._get_current_time()
        }
        self._mark_modified()
    
    def get_relationship(self, npc_id: str) -> Dict[str, Any]:
        """
        Obtient les détails d'une relation avec un PNJ.
        
        Args:
            npc_id: ID du PNJ
            
        Returns:
            Dict[str, Any]: Détails de la relation, ou relation neutre par défaut
        """
        default_relation = {
            'attitude': 'neutre',
            'strength': 1,
            'last_updated': self._get_current_time()
        }
        return self.relationships.get(npc_id, default_relation)
    
    def gain_experience(self, amount: int) -> bool:
        """
        Fait gagner de l'expérience au joueur et le fait monter de niveau si nécessaire.
        
        Args:
            amount: Quantité d'expérience à gagner
            
        Returns:
            bool: True si le joueur a gagné un niveau, False sinon
        """
        self.experience += amount
        self._mark_modified()
        
        # Vérifier si le joueur monte de niveau
        if self.experience >= self.experience_to_level:
            self.level_up()
            return True
        
        return False
    
    def level_up(self) -> Dict[str, int]:
        """
        Fait monter le joueur d'un niveau.
        
        Returns:
            Dict[str, int]: Statistiques gagnées avec la montée de niveau
        """
        # Calculer les gains de statistiques
        health_gain = 10
        energy_gain = 5
        
        # Appliquer les gains
        self.level += 1
        self.max_health += health_gain
        self.health = self.max_health  # Restaurer la santé au maximum
        self.max_energy += energy_gain
        self.energy = self.max_energy  # Restaurer l'énergie au maximum
        
        # Réinitialiser l'expérience et augmenter le seuil pour le niveau suivant
        self.experience = 0
        self.experience_to_level = int(self.experience_to_level * 1.5)
        
        self._mark_modified()
        
        # Retourner les gains pour affichage
        return {
            'niveau': self.level,
            'santé_max': health_gain,
            'énergie_max': energy_gain
        }
    
    def learn_skill(self, skill_name: str, level: int = 1) -> None:
        """
        Apprend ou améliore une compétence.
        
        Args:
            skill_name: Nom de la compétence
            level: Niveau de la compétence
        """
        current_level = self.skills.get(skill_name, 0)
        self.skills[skill_name] = max(current_level, level)
        self._mark_modified()
    
    def add_knowledge(self, topic: str, info: str) -> None:
        """
        Ajoute une connaissance au joueur.
        
        Args:
            topic: Sujet de la connaissance
            info: Information connue
        """
        if topic not in self.knowledge:
            self.knowledge[topic] = []
        
        # Éviter les doublons
        if info not in self.knowledge[topic]:
            self.knowledge[topic].append(info)
            self._mark_modified()
    
    def add_quest(self, quest_id: str, quest_data: Dict[str, Any]) -> None:
        """
        Ajoute une quête au journal du joueur.
        
        Args:
            quest_id: Identifiant de la quête
            quest_data: Données de la quête
        """
        self.quests[quest_id] = quest_data
        self._mark_modified()
    
    def update_quest_status(self, quest_id: str, status: str) -> bool:
        """
        Met à jour le statut d'une quête.
        
        Args:
            quest_id: Identifiant de la quête
            status: Nouveau statut (active, completed, failed)
            
        Returns:
            bool: True si la mise à jour a réussi, False sinon
        """
        if quest_id in self.quests:
            self.quests[quest_id]['status'] = status
            self._mark_modified()
            return True
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convertit le joueur en dictionnaire sérialisable.
        
        Returns:
            Dict[str, Any]: Représentation dictionnaire du joueur
        """
        # Obtenir le dictionnaire de base de l'entité
        data = super().to_dict()
        
        # Ajouter les propriétés spécifiques au joueur
        data.update({
            'inventory': self.inventory.copy(),
            'location_id': self.location_id,
            'memories': self.memories.copy(),
            'relationships': self.relationships.copy(),
            'health': self.health,
            'max_health': self.max_health,
            'energy': self.energy,
            'max_energy': self.max_energy,
            'level': self.level,
            'experience': self.experience,
            'experience_to_level': self.experience_to_level,
            'quests': self.quests.copy(),
            'objectives': self.objectives.copy(),
            'skills': self.skills.copy(),
            'knowledge': self.knowledge.copy()
        })
        
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Player':
        """
        Crée un joueur à partir d'un dictionnaire sérialisé.
        
        Args:
            data: Dictionnaire contenant les données du joueur
            
        Returns:
            Player: Instance de joueur créée
        """
        player = super().from_dict(data)
        
        # Définir les propriétés spécifiques au joueur
        player.inventory = data.get('inventory', []).copy()
        player.location_id = data.get('location_id')
        player.memories = data.get('memories', []).copy()
        player.relationships = data.get('relationships', {}).copy()
        player.health = data.get('health', 100)
        player.max_health = data.get('max_health', 100)
        player.energy = data.get('energy', 100)
        player.max_energy = data.get('max_energy', 100)
        player.level = data.get('level', 1)
        player.experience = data.get('experience', 0)
        player.experience_to_level = data.get('experience_to_level', 100)
        player.quests = data.get('quests', {}).copy()
        player.objectives = data.get('objectives', []).copy()
        player.skills = data.get('skills', {}).copy()
        player.knowledge = data.get('knowledge', {}).copy()
        
        return player
    
    def _get_current_time(self) -> float:
        """
        Obtient l'horodatage actuel.
        
        Returns:
            float: Horodatage actuel
        """
        import time
        return time.time()