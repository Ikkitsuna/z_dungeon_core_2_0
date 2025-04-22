#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NPC - Classe représentant les personnages non-joueurs
"""

from typing import Dict, List, Any, Optional, Set

from .entity import Entity

class NPC(Entity):
    """
    Classe représentant un personnage non-joueur (PNJ) dans le monde du jeu.
    Étend Entity avec des fonctionnalités spécifiques aux PNJ.
    """
    
    def __init__(
            self, 
            name: str, 
            description: str = "", 
            entity_id: Optional[str] = None,
            role: str = "",
            personality: str = "",
            location_id: Optional[str] = None
        ):
        """
        Initialise un nouveau PNJ.
        
        Args:
            name: Nom du PNJ
            description: Description physique du PNJ
            entity_id: Identifiant unique (généré automatiquement si non fourni)
            role: Rôle ou occupation du PNJ
            personality: Traits de personnalité du PNJ
            location_id: ID du lieu où se trouve le PNJ
        """
        super().__init__(name, description, entity_id)
        
        # Informations de base du PNJ
        self.role = role
        self.personality = personality
        self.location_id = location_id
        
        # Inventaire et connaissances
        self.inventory = []
        self.knowledge = {}
        
        # Relations avec les autres entités
        self.relationships = {}
        
        # État et comportement
        self.state = "normal"  # État actuel (normal, hostile, amical, etc.)
        self.mood = "neutre"   # Humeur actuelle
        self.goals = []        # Objectifs et motivations
        self.routine = {}      # Routines quotidiennes
        
        # Dialogues et réponses prédéfinies
        self.dialogue_options = {}
        
        # Histoire et passé
        self.backstory = ""
        self.secrets = []
    
    def add_to_inventory(self, item_id: str) -> None:
        """
        Ajoute un objet à l'inventaire du PNJ.
        
        Args:
            item_id: ID de l'objet à ajouter
        """
        if item_id not in self.inventory:
            self.inventory.append(item_id)
            self._mark_modified()
    
    def remove_from_inventory(self, item_id: str) -> bool:
        """
        Supprime un objet de l'inventaire du PNJ.
        
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
        Vérifie si le PNJ possède un objet spécifique.
        
        Args:
            item_id: ID de l'objet à vérifier
            
        Returns:
            bool: True si l'objet est dans l'inventaire, False sinon
        """
        return item_id in self.inventory
    
    def set_location(self, location_id: str) -> None:
        """
        Définit la localisation actuelle du PNJ.
        
        Args:
            location_id: ID du nouveau lieu
        """
        self.location_id = location_id
        self._mark_modified()
    
    def add_knowledge(self, topic: str, info: str, importance: int = 5) -> None:
        """
        Ajoute une connaissance au PNJ.
        
        Args:
            topic: Sujet de la connaissance
            info: Information connue
            importance: Importance de cette connaissance (1-10)
        """
        if topic not in self.knowledge:
            self.knowledge[topic] = []
        
        # Éviter les doublons
        for entry in self.knowledge[topic]:
            if entry['info'] == info:
                # Mettre à jour l'importance si entrée existante
                entry['importance'] = max(entry['importance'], importance)
                self._mark_modified()
                return
        
        # Ajouter la nouvelle connaissance
        self.knowledge[topic].append({
            'info': info,
            'importance': importance,
            'timestamp': self._get_current_time()
        })
        self._mark_modified()
    
    def knows_about(self, topic: str) -> bool:
        """
        Vérifie si le PNJ a des connaissances sur un sujet donné.
        
        Args:
            topic: Sujet à vérifier
            
        Returns:
            bool: True si le PNJ a des connaissances sur ce sujet, False sinon
        """
        return topic in self.knowledge and len(self.knowledge[topic]) > 0
    
    def get_knowledge(self, topic: str, min_importance: int = 0) -> List[Dict[str, Any]]:
        """
        Récupère les connaissances du PNJ sur un sujet donné.
        
        Args:
            topic: Sujet des connaissances
            min_importance: Importance minimale requise (0-10)
            
        Returns:
            List[Dict[str, Any]]: Liste des connaissances sur ce sujet
        """
        if not self.knows_about(topic):
            return []
        
        return [
            entry for entry in self.knowledge[topic]
            if entry['importance'] >= min_importance
        ]
    
    def add_relationship(self, entity_id: str, relation_type: str, attitude: str, strength: int = 5) -> None:
        """
        Définit ou met à jour la relation avec une autre entité.
        
        Args:
            entity_id: ID de l'entité
            relation_type: Type de relation (ami, famille, ennemi, etc.)
            attitude: Attitude envers l'entité (positive, neutre, négative)
            strength: Force de la relation (1-10)
        """
        self.relationships[entity_id] = {
            'type': relation_type,
            'attitude': attitude,
            'strength': strength,
            'last_updated': self._get_current_time()
        }
        self._mark_modified()
    
    def get_relationship(self, entity_id: str) -> Dict[str, Any]:
        """
        Obtient les détails d'une relation avec une entité.
        
        Args:
            entity_id: ID de l'entité
            
        Returns:
            Dict[str, Any]: Détails de la relation, ou relation neutre par défaut
        """
        default_relation = {
            'type': 'inconnu',
            'attitude': 'neutre',
            'strength': 1,
            'last_updated': self._get_current_time()
        }
        return self.relationships.get(entity_id, default_relation)
    
    def set_state(self, state: str) -> None:
        """
        Définit l'état actuel du PNJ.
        
        Args:
            state: Nouvel état
        """
        self.state = state
        self._mark_modified()
    
    def set_mood(self, mood: str) -> None:
        """
        Définit l'humeur actuelle du PNJ.
        
        Args:
            mood: Nouvelle humeur
        """
        self.mood = mood
        self._mark_modified()
    
    def add_goal(self, goal: str, priority: int = 5) -> None:
        """
        Ajoute un objectif ou une motivation au PNJ.
        
        Args:
            goal: Description de l'objectif
            priority: Priorité de cet objectif (1-10)
        """
        self.goals.append({
            'description': goal,
            'priority': priority,
            'achieved': False
        })
        self._mark_modified()
    
    def set_routine(self, time_of_day: str, activity: str, location_id: Optional[str] = None) -> None:
        """
        Définit une routine quotidienne pour le PNJ.
        
        Args:
            time_of_day: Moment de la journée (matin, midi, soir, nuit)
            activity: Description de l'activité
            location_id: ID du lieu où l'activité se déroule (optionnel)
        """
        self.routine[time_of_day] = {
            'activity': activity,
            'location_id': location_id
        }
        self._mark_modified()
    
    def get_current_activity(self, time_of_day: str) -> Optional[Dict[str, Any]]:
        """
        Récupère l'activité prévue à un moment donné de la journée.
        
        Args:
            time_of_day: Moment de la journée (matin, midi, soir, nuit)
            
        Returns:
            Optional[Dict[str, Any]]: Activité prévue, ou None si aucune
        """
        return self.routine.get(time_of_day)
    
    def add_dialogue_option(self, topic: str, response: str, conditions: Optional[Dict[str, Any]] = None) -> None:
        """
        Ajoute une option de dialogue au PNJ.
        
        Args:
            topic: Sujet ou mot-clé du dialogue
            response: Réponse du PNJ
            conditions: Conditions pour que cette réponse soit disponible
        """
        if topic not in self.dialogue_options:
            self.dialogue_options[topic] = []
        
        self.dialogue_options[topic].append({
            'response': response,
            'conditions': conditions or {}
        })
        self._mark_modified()
    
    def get_dialogue_responses(self, topic: str, context: Optional[Dict[str, Any]] = None) -> List[str]:
        """
        Récupère les réponses possibles pour un sujet de dialogue.
        
        Args:
            topic: Sujet ou mot-clé du dialogue
            context: Contexte actuel pour évaluer les conditions
            
        Returns:
            List[str]: Liste des réponses possibles
        """
        if topic not in self.dialogue_options:
            return []
        
        context = context or {}
        responses = []
        
        for option in self.dialogue_options[topic]:
            # Vérifier si toutes les conditions sont remplies
            conditions_met = True
            for key, value in option.get('conditions', {}).items():
                if context.get(key) != value:
                    conditions_met = False
                    break
            
            if conditions_met:
                responses.append(option['response'])
        
        return responses
    
    def set_backstory(self, backstory: str) -> None:
        """
        Définit l'histoire personnelle du PNJ.
        
        Args:
            backstory: Histoire personnelle
        """
        self.backstory = backstory
        self._mark_modified()
    
    def add_secret(self, secret: str, importance: int = 5) -> None:
        """
        Ajoute un secret au PNJ.
        
        Args:
            secret: Description du secret
            importance: Importance de ce secret (1-10)
        """
        self.secrets.append({
            'description': secret,
            'importance': importance,
            'revealed': False
        })
        self._mark_modified()
    
    def get_secrets(self, include_revealed: bool = False) -> List[Dict[str, Any]]:
        """
        Récupère les secrets du PNJ.
        
        Args:
            include_revealed: Si True, inclut aussi les secrets déjà révélés
            
        Returns:
            List[Dict[str, Any]]: Liste des secrets
        """
        if include_revealed:
            return self.secrets.copy()
        else:
            return [secret for secret in self.secrets if not secret.get('revealed', False)]
    
    def reveal_secret(self, index: int) -> None:
        """
        Marque un secret comme révélé.
        
        Args:
            index: Indice du secret dans la liste des secrets
        """
        if 0 <= index < len(self.secrets):
            self.secrets[index]['revealed'] = True
            self._mark_modified()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convertit le PNJ en dictionnaire sérialisable.
        
        Returns:
            Dict[str, Any]: Représentation dictionnaire du PNJ
        """
        # Obtenir le dictionnaire de base de l'entité
        data = super().to_dict()
        
        # Ajouter les propriétés spécifiques au PNJ
        data.update({
            'role': self.role,
            'personality': self.personality,
            'location_id': self.location_id,
            'inventory': self.inventory.copy(),
            'knowledge': self.knowledge.copy(),
            'relationships': self.relationships.copy(),
            'state': self.state,
            'mood': self.mood,
            'goals': self.goals.copy(),
            'routine': self.routine.copy(),
            'dialogue_options': self.dialogue_options.copy(),
            'backstory': self.backstory,
            'secrets': self.secrets.copy()
        })
        
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NPC':
        """
        Crée un PNJ à partir d'un dictionnaire sérialisé.
        
        Args:
            data: Dictionnaire contenant les données du PNJ
            
        Returns:
            NPC: Instance de PNJ créée
        """
        # Créer l'instance avec les propriétés de base
        npc = cls(
            name=data.get('name', 'PNJ sans nom'),
            description=data.get('description', ''),
            entity_id=data.get('id'),
            role=data.get('role', ''),
            personality=data.get('personality', ''),
            location_id=data.get('location_id')
        )
        
        # Définir les propriétés spécifiques au PNJ
        npc.inventory = data.get('inventory', []).copy()
        npc.knowledge = data.get('knowledge', {}).copy()
        npc.relationships = data.get('relationships', {}).copy()
        npc.state = data.get('state', 'normal')
        npc.mood = data.get('mood', 'neutre')
        npc.goals = data.get('goals', []).copy()
        npc.routine = data.get('routine', {}).copy()
        npc.dialogue_options = data.get('dialogue_options', {}).copy()
        npc.backstory = data.get('backstory', '')
        npc.secrets = data.get('secrets', []).copy()
        
        # Définir les propriétés héritées
        npc.tags = data.get('tags', []).copy()
        npc.metadata = data.get('metadata', {}).copy()
        npc.created_at = data.get('created_at', npc.created_at)
        npc.modified_at = data.get('modified_at', npc.modified_at)
        
        return npc
    
    def _get_current_time(self) -> float:
        """
        Obtient l'horodatage actuel.
        
        Returns:
            float: Horodatage actuel
        """
        import time
        return time.time()
    
    def get(self, attribute: str, default=None):
        """
        Méthode générique pour récupérer un attribut du PNJ.
        Utile pour les interactions génériques comme la commande 'regarder'.
        
        Args:
            attribute: Nom de l'attribut à récupérer
            default: Valeur par défaut si l'attribut n'existe pas
            
        Returns:
            Any: Valeur de l'attribut ou valeur par défaut
        """
        return getattr(self, attribute, default)