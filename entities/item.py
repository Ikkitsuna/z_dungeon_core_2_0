#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Item - Classe représentant les objets du monde
"""

from typing import Dict, List, Any, Optional, Callable

from .entity import Entity

class Item(Entity):
    """
    Classe représentant un objet dans le monde du jeu.
    Étend Entity avec des fonctionnalités spécifiques aux objets.
    """
    
    def __init__(
            self, 
            name: str, 
            description: str = "", 
            entity_id: Optional[str] = None,
            item_type: str = "common",
            value: int = 0
        ):
        """
        Initialise un nouvel objet.
        
        Args:
            name: Nom de l'objet
            description: Description de l'objet
            entity_id: Identifiant unique (généré automatiquement si non fourni)
            item_type: Type d'objet (common, quest, key, weapon, armor, etc.)
            value: Valeur de l'objet (en monnaie du jeu)
        """
        super().__init__(name, description, entity_id)
        
        # Propriétés de base
        self.item_type = item_type
        self.value = value
        
        # État de l'objet
        self.condition = 100  # Pourcentage de l'état (100 = neuf, 0 = détruit)
        self.durability = -1  # -1 = indestructible, sinon nombre d'utilisations restantes
        
        # Localisation de l'objet
        self.location_id = None  # ID de la localisation où se trouve l'objet
        
        # Propriétés spéciales
        self.properties = {}
        self.usable = False
        self.use_effect = ""
        self.equippable = False
        self.equipped = False
        self.slot = ""  # Emplacement d'équipement (main, tête, torse, etc.)
        
        # Si l'objet est un conteneur
        self.is_container = False
        self.container_capacity = 0
        self.contained_items = []
        
        # Restrictions
        self.use_requirements = {}
        
        # Histoire de l'objet
        self.origin = ""
        self.previous_owners = []
    
    def set_condition(self, condition: int) -> None:
        """
        Définit l'état physique de l'objet.
        
        Args:
            condition: Nouvel état (0-100)
        """
        self.condition = max(0, min(100, condition))
        self._mark_modified()
    
    def damage(self, amount: int) -> bool:
        """
        Endommage l'objet. Retourne True si l'objet est détruit.
        
        Args:
            amount: Quantité de dégâts (0-100)
            
        Returns:
            bool: True si l'objet est détruit (condition = 0)
        """
        self.condition = max(0, self.condition - amount)
        self._mark_modified()
        return self.condition <= 0
    
    def repair(self, amount: int) -> None:
        """
        Répare l'objet.
        
        Args:
            amount: Quantité de réparation (0-100)
        """
        self.condition = min(100, self.condition + amount)
        self._mark_modified()
    
    def set_durability(self, uses: int) -> None:
        """
        Définit la durabilité de l'objet.
        
        Args:
            uses: Nombre d'utilisations (-1 = indestructible)
        """
        self.durability = uses
        self._mark_modified()
    
    def use(self) -> Dict[str, Any]:
        """
        Utilise l'objet, diminue sa durabilité et retourne l'effet.
        
        Returns:
            Dict[str, Any]: Résultat de l'utilisation avec les champs:
                - success: True si l'utilisation a réussi
                - effect: Description de l'effet
                - destroyed: True si l'objet est détruit
        """
        # Si l'objet n'est pas utilisable
        if not self.usable:
            return {
                'success': False,
                'effect': "Cet objet n'est pas utilisable.",
                'destroyed': False
            }
        
        # Si l'objet a une durabilité limitée
        if self.durability > 0:
            self.durability -= 1
            destroyed = self.durability <= 0
        else:
            destroyed = False
        
        self._mark_modified()
        
        return {
            'success': True,
            'effect': self.use_effect,
            'destroyed': destroyed
        }
    
    def set_usable(self, usable: bool, effect: str = "") -> None:
        """
        Définit si l'objet est utilisable et son effet.
        
        Args:
            usable: True si l'objet est utilisable
            effect: Description de l'effet lors de l'utilisation
        """
        self.usable = usable
        self.use_effect = effect
        self._mark_modified()
    
    def set_equippable(self, equippable: bool, slot: str = "") -> None:
        """
        Définit si l'objet est équipable et son emplacement.
        
        Args:
            equippable: True si l'objet est équipable
            slot: Emplacement d'équipement (main, tête, torse, etc.)
        """
        self.equippable = equippable
        self.slot = slot
        self._mark_modified()
    
    def equip(self) -> bool:
        """
        Équipe l'objet. Retourne True si l'équipement a réussi.
        
        Returns:
            bool: True si l'objet a été équipé, False sinon
        """
        if not self.equippable:
            return False
        
        self.equipped = True
        self._mark_modified()
        return True
    
    def unequip(self) -> None:
        """
        Déséquipe l'objet.
        """
        self.equipped = False
        self._mark_modified()
    
    def set_property(self, key: str, value: Any) -> None:
        """
        Définit une propriété spéciale pour l'objet.
        
        Args:
            key: Nom de la propriété
            value: Valeur de la propriété
        """
        self.properties[key] = value
        self._mark_modified()
    
    def get_property(self, key: str, default: Any = None) -> Any:
        """
        Récupère une propriété spéciale de l'objet.
        
        Args:
            key: Nom de la propriété
            default: Valeur par défaut si la propriété n'existe pas
            
        Returns:
            Any: Valeur de la propriété ou valeur par défaut
        """
        return self.properties.get(key, default)
    
    def set_as_container(self, is_container: bool, capacity: int = 0) -> None:
        """
        Définit l'objet comme conteneur.
        
        Args:
            is_container: True si l'objet est un conteneur
            capacity: Capacité du conteneur (nombre d'objets)
        """
        self.is_container = is_container
        self.container_capacity = capacity
        self._mark_modified()
    
    def add_to_container(self, item_id: str) -> bool:
        """
        Ajoute un objet au conteneur.
        
        Args:
            item_id: ID de l'objet à ajouter
            
        Returns:
            bool: True si l'objet a été ajouté, False si le conteneur est plein
        """
        if not self.is_container:
            return False
        
        if self.container_capacity > 0 and len(self.contained_items) >= self.container_capacity:
            return False
        
        if item_id not in self.contained_items:
            self.contained_items.append(item_id)
            self._mark_modified()
        
        return True
    
    def remove_from_container(self, item_id: str) -> bool:
        """
        Retire un objet du conteneur.
        
        Args:
            item_id: ID de l'objet à retirer
            
        Returns:
            bool: True si l'objet a été retiré, False sinon
        """
        if item_id in self.contained_items:
            self.contained_items.remove(item_id)
            self._mark_modified()
            return True
        return False
    
    def get_container_contents(self) -> List[str]:
        """
        Récupère le contenu du conteneur.
        
        Returns:
            List[str]: Liste des IDs des objets contenus
        """
        return self.contained_items.copy()
    
    def set_use_requirement(self, req_type: str, value: Any) -> None:
        """
        Définit une condition requise pour utiliser l'objet.
        
        Args:
            req_type: Type de condition (skill, level, quest, etc.)
            value: Valeur requise
        """
        self.use_requirements[req_type] = value
        self._mark_modified()
    
    def can_use(self, entity_data: Dict[str, Any]) -> bool:
        """
        Vérifie si une entité peut utiliser cet objet selon les restrictions.
        
        Args:
            entity_data: Données de l'entité tentant d'utiliser l'objet
            
        Returns:
            bool: True si l'utilisation est autorisée, False sinon
        """
        # Si pas de restrictions, l'utilisation est toujours autorisée
        if not self.use_requirements:
            return True
        
        # Si l'objet n'est pas utilisable
        if not self.usable:
            return False
        
        # Vérifier chaque condition d'utilisation
        for req_type, value in self.use_requirements.items():
            # Si la condition concerne un niveau minimum
            if req_type == 'min_level':
                if entity_data.get('level', 0) < value:
                    return False
            
            # Si la condition concerne une compétence requise
            elif req_type == 'skill':
                skills = entity_data.get('skills', {})
                if skills.get(value, 0) <= 0:
                    return False
            
            # Si la condition concerne une quête complétée
            elif req_type == 'completed_quest':
                quests = entity_data.get('quests', {})
                if not quests.get(value, {}).get('status') == 'completed':
                    return False
            
            # Autres conditions personnalisées...
        
        # Si toutes les conditions sont satisfaites
        return True
    
    def set_origin(self, origin: str) -> None:
        """
        Définit l'origine de l'objet.
        
        Args:
            origin: Description de l'origine
        """
        self.origin = origin
        self._mark_modified()
    
    def add_previous_owner(self, owner_id: str, owner_name: str) -> None:
        """
        Ajoute un propriétaire précédent à l'historique de l'objet.
        
        Args:
            owner_id: ID du propriétaire
            owner_name: Nom du propriétaire
        """
        self.previous_owners.append({
            'id': owner_id,
            'name': owner_name,
            'timestamp': self._get_current_time()
        })
        self._mark_modified()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convertit l'objet en dictionnaire sérialisable.
        
        Returns:
            Dict[str, Any]: Représentation dictionnaire de l'objet
        """
        # Obtenir le dictionnaire de base de l'entité
        data = super().to_dict()
        
        # Ajouter les propriétés spécifiques à l'objet
        data.update({
            'item_type': self.item_type,
            'value': self.value,
            'condition': self.condition,
            'durability': self.durability,
            'location_id': self.location_id,  # Inclure l'ID de localisation
            'properties': self.properties.copy(),
            'usable': self.usable,
            'use_effect': self.use_effect,
            'equippable': self.equippable,
            'equipped': self.equipped,
            'slot': self.slot,
            'is_container': self.is_container,
            'container_capacity': self.container_capacity,
            'contained_items': self.contained_items.copy(),
            'use_requirements': self.use_requirements.copy(),
            'origin': self.origin,
            'previous_owners': self.previous_owners.copy()
        })
        
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Item':
        """
        Crée un objet à partir d'un dictionnaire sérialisé.
        
        Args:
            data: Dictionnaire contenant les données de l'objet
            
        Returns:
            Item: Instance d'objet créée
        """
        # Créer l'instance avec les propriétés de base
        item = cls(
            name=data.get('name', 'Objet sans nom'),
            description=data.get('description', ''),
            entity_id=data.get('id'),
            item_type=data.get('item_type', 'common'),
            value=data.get('value', 0)
        )
        
        # Définir les propriétés spécifiques à l'objet
        item.condition = data.get('condition', 100)
        item.durability = data.get('durability', -1)
        item.location_id = data.get('location_id', None)  # Charger la localisation
        item.properties = data.get('properties', {}).copy()
        item.usable = data.get('usable', False)
        item.use_effect = data.get('use_effect', '')
        item.equippable = data.get('equippable', False)
        item.equipped = data.get('equipped', False)
        item.slot = data.get('slot', '')
        item.is_container = data.get('is_container', False)
        item.container_capacity = data.get('container_capacity', 0)
        item.contained_items = data.get('contained_items', []).copy()
        item.use_requirements = data.get('use_requirements', {}).copy()
        item.origin = data.get('origin', '')
        item.previous_owners = data.get('previous_owners', []).copy()
        
        # Définir les propriétés héritées
        item.tags = data.get('tags', []).copy()
        item.metadata = data.get('metadata', {}).copy()
        item.created_at = data.get('created_at', item.created_at)
        item.modified_at = data.get('modified_at', item.modified_at)
        
        return item
    
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
        Méthode générique pour récupérer un attribut de l'objet.
        Utile pour les interactions génériques comme la commande 'regarder'.
        
        Args:
            attribute: Nom de l'attribut à récupérer
            default: Valeur par défaut si l'attribut n'existe pas
            
        Returns:
            Any: Valeur de l'attribut ou valeur par défaut
        """
        return getattr(self, attribute, default)