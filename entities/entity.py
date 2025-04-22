#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Entity - Classe de base pour toutes les entités du jeu
"""

import uuid
from typing import Dict, List, Any, Optional

class Entity:
    """
    Classe de base pour toutes les entités du jeu (PNJ, lieux, objets, etc.).
    Fournit des fonctionnalités communes à toutes les entités.
    """
    
    def __init__(
            self, 
            name: str, 
            description: str = "", 
            entity_id: Optional[str] = None
        ):
        """
        Initialise une nouvelle entité.
        
        Args:
            name: Nom de l'entité
            description: Description de l'entité
            entity_id: Identifiant unique de l'entité (généré automatiquement si non fourni)
        """
        self.id = entity_id or str(uuid.uuid4())
        self.name = name
        self.description = description
        self.tags = []
        self.metadata = {}
        
        # Horodatage de création et dernière modification
        import time
        self.created_at = time.time()
        self.modified_at = self.created_at
    
    def update_description(self, description: str) -> None:
        """
        Met à jour la description de l'entité.
        
        Args:
            description: Nouvelle description
        """
        self.description = description
        self._mark_modified()
    
    def add_tag(self, tag: str) -> None:
        """
        Ajoute un tag à l'entité.
        
        Args:
            tag: Tag à ajouter
        """
        if tag not in self.tags:
            self.tags.append(tag)
            self._mark_modified()
    
    def remove_tag(self, tag: str) -> None:
        """
        Supprime un tag de l'entité.
        
        Args:
            tag: Tag à supprimer
        """
        if tag in self.tags:
            self.tags.remove(tag)
            self._mark_modified()
    
    def has_tag(self, tag: str) -> bool:
        """
        Vérifie si l'entité possède un tag spécifique.
        
        Args:
            tag: Tag à vérifier
            
        Returns:
            bool: True si l'entité possède le tag, False sinon
        """
        return tag in self.tags
    
    def set_metadata(self, key: str, value: Any) -> None:
        """
        Définit une métadonnée pour l'entité.
        
        Args:
            key: Clé de la métadonnée
            value: Valeur de la métadonnée
        """
        self.metadata[key] = value
        self._mark_modified()
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """
        Récupère une métadonnée de l'entité.
        
        Args:
            key: Clé de la métadonnée
            default: Valeur par défaut si la clé n'existe pas
            
        Returns:
            Any: Valeur de la métadonnée ou valeur par défaut
        """
        return self.metadata.get(key, default)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convertit l'entité en dictionnaire sérialisable.
        
        Returns:
            Dict[str, Any]: Représentation dictionnaire de l'entité
        """
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'tags': self.tags.copy(),
            'metadata': self.metadata.copy(),
            'created_at': self.created_at,
            'modified_at': self.modified_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Entity':
        """
        Crée une entité à partir d'un dictionnaire sérialisé.
        
        Args:
            data: Dictionnaire contenant les données de l'entité
            
        Returns:
            Entity: Instance d'entité créée
        """
        entity = cls(
            name=data.get('name', 'Entité sans nom'),
            description=data.get('description', ''),
            entity_id=data.get('id')
        )
        
        entity.tags = data.get('tags', []).copy()
        entity.metadata = data.get('metadata', {}).copy()
        entity.created_at = data.get('created_at', entity.created_at)
        entity.modified_at = data.get('modified_at', entity.modified_at)
        
        return entity
    
    def _mark_modified(self) -> None:
        """
        Marque l'entité comme modifiée en mettant à jour l'horodatage.
        """
        import time
        self.modified_at = time.time()
    
    def __str__(self) -> str:
        """
        Représentation textuelle de l'entité.
        
        Returns:
            str: Représentation textuelle
        """
        return f"{self.name} (ID: {self.id})"
    
    def __repr__(self) -> str:
        """
        Représentation de débogage de l'entité.
        
        Returns:
            str: Représentation de débogage
        """
        return f"{self.__class__.__name__}(id='{self.id}', name='{self.name}')"