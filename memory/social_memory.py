#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SocialMemory - Gestion de la mémoire sociale (interactions entre entités)
"""

import uuid
import logging
from typing import Dict, List, Any, Optional, Tuple, Set
from datetime import datetime

# Configuration du système de logging
logger = logging.getLogger('SocialMemory')

class SocialMemory:
    """
    Gère la mémoire sociale, c'est-à-dire les interactions et relations entre entités.
    Stocke l'historique des interactions et permet de comprendre le réseau social du monde.
    """
    
    def __init__(self, world_id: str):
        """
        Initialise une nouvelle mémoire sociale.
        
        Args:
            world_id: Identifiant du monde auquel cette mémoire sociale appartient
        """
        self.world_id = world_id
        self.interactions: List[Dict[str, Any]] = []
        self.relationships: Dict[str, Dict[str, Dict[str, Any]]] = {}  # entity1_id -> entity2_id -> relation_data
        
        # Métadonnées
        self.meta = {
            'created_at': datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat(),
            'interaction_count': 0,
            'relationship_count': 0
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convertit la mémoire sociale en dictionnaire pour la sérialisation.
        
        Returns:
            Dict[str, Any]: Représentation de la mémoire sociale sous forme de dictionnaire
        """
        return {
            'world_id': self.world_id,
            'interactions': self.interactions,
            'relationships': self.relationships,
            'meta': self.meta
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SocialMemory':
        """
        Crée une instance de mémoire sociale à partir d'un dictionnaire.
        
        Args:
            data: Dictionnaire contenant les données de la mémoire sociale
            
        Returns:
            SocialMemory: Instance de mémoire sociale créée
        """
        memory = cls(world_id=data.get('world_id', ''))
        memory.interactions = data.get('interactions', [])
        memory.relationships = data.get('relationships', {})
        memory.meta = data.get('meta', {
            'created_at': datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat(),
            'interaction_count': 0,
            'relationship_count': 0
        })
        
        return memory
    
    def add_interaction(self, 
                       entity1_id: str, 
                       entity1_name: str,
                       entity2_id: str, 
                       entity2_name: str,
                       interaction_type: str,
                       description: str,
                       impact: int = 0,
                       location_id: Optional[str] = None,
                       witnesses: Optional[List[str]] = None,
                       context: Optional[Dict[str, Any]] = None) -> str:
        """
        Ajoute une nouvelle interaction entre deux entités.
        
        Args:
            entity1_id: Identifiant de la première entité
            entity1_name: Nom de la première entité
            entity2_id: Identifiant de la seconde entité
            entity2_name: Nom de la seconde entité
            interaction_type: Type d'interaction (conversation, combat, commerce, etc.)
            description: Description de l'interaction
            impact: Impact de l'interaction sur la relation (-10 à +10)
            location_id: Identifiant du lieu où s'est produite l'interaction
            witnesses: Liste des identifiants des témoins de l'interaction
            context: Contexte additionnel de l'interaction
            
        Returns:
            str: Identifiant de l'interaction ajoutée
        """
        # Générer un identifiant unique pour l'interaction
        interaction_id = str(uuid.uuid4())
        
        # Normaliser l'impact entre -10 et +10
        impact = max(-10, min(10, impact))
        
        # Créer l'entrée d'interaction
        interaction = {
            'id': interaction_id,
            'entity1_id': entity1_id,
            'entity1_name': entity1_name,
            'entity2_id': entity2_id,
            'entity2_name': entity2_name,
            'type': interaction_type,
            'description': description,
            'impact': impact,
            'timestamp': datetime.now().isoformat(),
            'location_id': location_id,
            'witnesses': witnesses or [],
            'context': context or {}
        }
        
        # Ajouter à la liste des interactions
        self.interactions.append(interaction)
        
        # Mettre à jour les relations entre les entités
        self._update_relationship(entity1_id, entity2_id, interaction_type, impact)
        
        # Mettre à jour les métadonnées
        self.meta['last_updated'] = datetime.now().isoformat()
        self.meta['interaction_count'] = len(self.interactions)
        self.meta['relationship_count'] = self._count_relationships()
        
        logger.debug(f"Interaction ajoutée: {entity1_name} -> {entity2_name} ({interaction_type})")
        return interaction_id
    
    def _update_relationship(self, entity1_id: str, entity2_id: str, interaction_type: str, impact: int) -> None:
        """
        Met à jour la relation entre deux entités suite à une interaction.
        
        Args:
            entity1_id: Identifiant de la première entité
            entity2_id: Identifiant de la seconde entité
            interaction_type: Type d'interaction
            impact: Impact de l'interaction sur la relation
        """
        # Initialiser les structures de données si nécessaire
        if entity1_id not in self.relationships:
            self.relationships[entity1_id] = {}
        
        if entity2_id not in self.relationships:
            self.relationships[entity2_id] = {}
        
        # Créer ou mettre à jour la relation dans les deux sens
        # Relation de entity1 vers entity2
        if entity2_id not in self.relationships[entity1_id]:
            self.relationships[entity1_id][entity2_id] = {
                'affinity': impact,
                'interaction_count': 1,
                'last_interaction': datetime.now().isoformat(),
                'interaction_types': {interaction_type: 1}
            }
        else:
            relation = self.relationships[entity1_id][entity2_id]
            relation['affinity'] = max(-100, min(100, relation['affinity'] + impact))
            relation['interaction_count'] += 1
            relation['last_interaction'] = datetime.now().isoformat()
            
            if interaction_type in relation['interaction_types']:
                relation['interaction_types'][interaction_type] += 1
            else:
                relation['interaction_types'][interaction_type] = 1
        
        # Relation de entity2 vers entity1 (avec un impact potentiellement différent)
        # L'impact sur la relation inverse pourrait être différent selon le type d'interaction
        inverse_impact = impact  # Par défaut, même impact
        
        # Ajuster l'impact inverse selon le type d'interaction
        if interaction_type in ['agression', 'vol', 'menace']:
            inverse_impact = -abs(impact)  # Impact négatif assuré pour la cible
        elif interaction_type in ['aide', 'cadeau', 'soin']:
            inverse_impact = abs(impact)  # Impact positif assuré pour la cible
        
        if entity1_id not in self.relationships[entity2_id]:
            self.relationships[entity2_id][entity1_id] = {
                'affinity': inverse_impact,
                'interaction_count': 1,
                'last_interaction': datetime.now().isoformat(),
                'interaction_types': {interaction_type: 1}
            }
        else:
            relation = self.relationships[entity2_id][entity1_id]
            relation['affinity'] = max(-100, min(100, relation['affinity'] + inverse_impact))
            relation['interaction_count'] += 1
            relation['last_interaction'] = datetime.now().isoformat()
            
            if interaction_type in relation['interaction_types']:
                relation['interaction_types'][interaction_type] += 1
            else:
                relation['interaction_types'][interaction_type] = 1
    
    def _count_relationships(self) -> int:
        """
        Compte le nombre total de relations.
        
        Returns:
            int: Nombre de relations
        """
        count = 0
        for entity_id, relations in self.relationships.items():
            count += len(relations)
        
        return count
    
    def get_relationship(self, entity1_id: str, entity2_id: str) -> Optional[Dict[str, Any]]:
        """
        Récupère les détails de la relation entre deux entités.
        
        Args:
            entity1_id: Identifiant de la première entité
            entity2_id: Identifiant de la seconde entité
            
        Returns:
            Optional[Dict[str, Any]]: Détails de la relation ou None si elle n'existe pas
        """
        if entity1_id in self.relationships and entity2_id in self.relationships[entity1_id]:
            return self.relationships[entity1_id][entity2_id]
        
        return None
    
    def get_affinity(self, entity1_id: str, entity2_id: str) -> int:
        """
        Récupère l'affinité d'une entité envers une autre.
        
        Args:
            entity1_id: Identifiant de l'entité qui a l'affinité
            entity2_id: Identifiant de l'entité envers laquelle l'affinité est mesurée
            
        Returns:
            int: Valeur d'affinité (-100 à +100), 0 par défaut si relation inexistante
        """
        relation = self.get_relationship(entity1_id, entity2_id)
        
        if relation:
            return relation.get('affinity', 0)
        
        return 0
    
    def get_entity_relationships(self, entity_id: str) -> Dict[str, Dict[str, Any]]:
        """
        Récupère toutes les relations d'une entité.
        
        Args:
            entity_id: Identifiant de l'entité
            
        Returns:
            Dict[str, Dict[str, Any]]: Dictionnaire des relations (entity_id -> relation_data)
        """
        if entity_id in self.relationships:
            return self.relationships[entity_id]
        
        return {}
    
    def get_entity_interactions(self, entity_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Récupère les interactions impliquant une entité spécifique.
        
        Args:
            entity_id: Identifiant de l'entité
            limit: Nombre maximum d'interactions à retourner
            
        Returns:
            List[Dict[str, Any]]: Liste des interactions impliquant l'entité
        """
        # Filtrer les interactions impliquant l'entité
        entity_interactions = [
            interaction for interaction in self.interactions
            if interaction['entity1_id'] == entity_id or interaction['entity2_id'] == entity_id
        ]
        
        # Trier par date (plus récent d'abord)
        entity_interactions.sort(key=lambda i: i['timestamp'], reverse=True)
        
        # Retourner les interactions limitées
        return entity_interactions[:limit]
    
    def get_witness_interactions(self, witness_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Récupère les interactions dont une entité a été témoin.
        
        Args:
            witness_id: Identifiant du témoin
            limit: Nombre maximum d'interactions à retourner
            
        Returns:
            List[Dict[str, Any]]: Liste des interactions dont l'entité a été témoin
        """
        # Filtrer les interactions dont l'entité a été témoin
        witnessed_interactions = [
            interaction for interaction in self.interactions
            if witness_id in interaction.get('witnesses', [])
        ]
        
        # Trier par date (plus récent d'abord)
        witnessed_interactions.sort(key=lambda i: i['timestamp'], reverse=True)
        
        # Retourner les interactions limitées
        return witnessed_interactions[:limit]
    
    def get_location_interactions(self, location_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Récupère les interactions qui se sont produites dans un lieu spécifique.
        
        Args:
            location_id: Identifiant du lieu
            limit: Nombre maximum d'interactions à retourner
            
        Returns:
            List[Dict[str, Any]]: Liste des interactions dans le lieu
        """
        # Filtrer les interactions par lieu
        location_interactions = [
            interaction for interaction in self.interactions
            if interaction.get('location_id') == location_id
        ]
        
        # Trier par date (plus récent d'abord)
        location_interactions.sort(key=lambda i: i['timestamp'], reverse=True)
        
        # Retourner les interactions limitées
        return location_interactions[:limit]
    
    def get_social_network(self, min_interaction_count: int = 1) -> Dict[str, Set[str]]:
        """
        Construit un réseau social sous forme de graphe.
        
        Args:
            min_interaction_count: Nombre minimum d'interactions pour considérer une relation
            
        Returns:
            Dict[str, Set[str]]: Graphe du réseau social (entity_id -> {connected_entity_ids})
        """
        network = {}
        
        for entity1_id, relations in self.relationships.items():
            if entity1_id not in network:
                network[entity1_id] = set()
            
            for entity2_id, relation_data in relations.items():
                if relation_data.get('interaction_count', 0) >= min_interaction_count:
                    network[entity1_id].add(entity2_id)
                    
                    # Assurer que l'autre entité est aussi dans le graphe
                    if entity2_id not in network:
                        network[entity2_id] = set()
        
        return network
    
    def get_social_groups(self, affinity_threshold: int = 20) -> List[Set[str]]:
        """
        Identifie des groupes sociaux basés sur les affinités entre entités.
        Utilise un algorithme simple de clustering basé sur les affinités positives.
        
        Args:
            affinity_threshold: Seuil d'affinité pour considérer deux entités comme liées
            
        Returns:
            List[Set[str]]: Liste des groupes sociaux (chaque groupe est un ensemble d'identifiants d'entités)
        """
        # Construire un graphe d'affinités positives
        graph = {}
        
        for entity1_id, relations in self.relationships.items():
            if entity1_id not in graph:
                graph[entity1_id] = set()
            
            for entity2_id, relation_data in relations.items():
                if relation_data.get('affinity', 0) >= affinity_threshold:
                    graph[entity1_id].add(entity2_id)
                    
                    # Assurer que l'autre entité est aussi dans le graphe
                    if entity2_id not in graph:
                        graph[entity2_id] = set()
        
        # Identifier les composantes connexes du graphe
        visited = set()
        groups = []
        
        for entity_id in graph:
            if entity_id not in visited:
                # Faire un parcours en largeur à partir de cette entité
                group = set()
                queue = [entity_id]
                visited.add(entity_id)
                
                while queue:
                    current = queue.pop(0)
                    group.add(current)
                    
                    for neighbor in graph.get(current, set()):
                        if neighbor not in visited:
                            visited.add(neighbor)
                            queue.append(neighbor)
                
                groups.append(group)
        
        return groups
    
    def get_influential_entities(self, top_n: int = 5) -> List[Tuple[str, int]]:
        """
        Identifie les entités les plus influentes du réseau social,
        basé sur le nombre de relations et interactions.
        
        Args:
            top_n: Nombre d'entités à retourner
            
        Returns:
            List[Tuple[str, int]]: Liste de tuples (entity_id, score) des entités les plus influentes
        """
        # Calculer un score d'influence pour chaque entité
        influence_scores = {}
        
        for entity_id, relations in self.relationships.items():
            if entity_id not in influence_scores:
                influence_scores[entity_id] = 0
            
            # Ajouter un point par relation
            influence_scores[entity_id] += len(relations)
            
            # Ajouter des points basés sur le nombre d'interactions
            for relation_data in relations.values():
                influence_scores[entity_id] += relation_data.get('interaction_count', 0) // 2
        
        # Trier par score décroissant
        sorted_scores = sorted(
            influence_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return sorted_scores[:top_n]
    
    def clear_interactions(self) -> int:
        """
        Supprime toutes les interactions, mais conserve les relations.
        
        Returns:
            int: Nombre d'interactions supprimées
        """
        count = len(self.interactions)
        self.interactions = []
        
        # Mettre à jour les métadonnées
        self.meta['interaction_count'] = 0
        self.meta['last_updated'] = datetime.now().isoformat()
        
        return count
    
    def reset(self) -> None:
        """
        Réinitialise complètement la mémoire sociale (interactions et relations).
        """
        self.interactions = []
        self.relationships = {}
        
        # Mettre à jour les métadonnées
        self.meta['interaction_count'] = 0
        self.meta['relationship_count'] = 0
        self.meta['last_updated'] = datetime.now().isoformat()