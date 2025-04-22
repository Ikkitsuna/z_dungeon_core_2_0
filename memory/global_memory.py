#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GlobalMemory - Système de mémoire globale pour le MJ
"""

import time
import json
import os
from typing import Dict, List, Any, Optional, Set, Tuple, Union

class GlobalMemory:
    """
    Gère la mémoire globale du Maître du Jeu.
    Stocke l'évolution du monde, les événements majeurs et l'état des quêtes.
    """
    
    def __init__(self, world_id: str, world_name: str):
        """
        Initialise une nouvelle mémoire globale.
        
        Args:
            world_id: ID du monde
            world_name: Nom du monde
        """
        self.world_id = world_id
        self.world_name = world_name
        
        # Stockage des événements globaux
        self.events = []
        
        # Stockage des faits établis sur le monde
        self.world_facts = {}
        
        # Stockage des quêtes et intrigues
        self.quests = {}
        
        # Stockage des décisions narratives importantes
        self.narrative_decisions = []
        
        # Journal des modifications d'état du monde
        self.world_state_changes = []
        
        # Stockage des PNJ, lieux, objets importants
        self.tracked_entities = {
            'npcs': set(),
            'locations': set(),
            'items': set()
        }
        
        # Dernière mise à jour 
        self.last_updated = time.time()
    
    def add_event(self, 
                 description: str, 
                 importance: int = 5,
                 event_type: str = "world_event",
                 location_id: Optional[str] = None,
                 involved_entities: Optional[List[str]] = None,
                 timestamp: Optional[float] = None) -> Dict[str, Any]:
        """
        Ajoute un nouvel événement à la mémoire globale.
        
        Args:
            description: Description détaillée de l'événement
            importance: Importance de l'événement (1-10)
            event_type: Type d'événement (world_event, quest_update, etc.)
            location_id: ID du lieu où s'est produit l'événement
            involved_entities: Liste des IDs d'entités impliquées
            timestamp: Horodatage de l'événement (utilise l'heure actuelle si non fourni)
            
        Returns:
            Dict[str, Any]: L'événement créé
        """
        event = {
            'id': self._generate_event_id(),
            'description': description,
            'importance': min(10, max(1, importance)),  # Limiter entre 1 et 10
            'event_type': event_type,
            'location_id': location_id,
            'involved_entities': involved_entities or [],
            'timestamp': timestamp or time.time(),
            'created_at': time.time()
        }
        
        # Ajouter à la mémoire
        self.events.append(event)
        
        # Trier par importance et chronologie (les plus récents et importants en premier)
        self.events.sort(key=lambda x: (x['importance'], x['timestamp']), reverse=True)
        
        # Mettre à jour le timestamp de dernière mise à jour
        self.last_updated = time.time()
        
        return event
    
    def get_events(self, 
                  event_type: Optional[str] = None,
                  min_importance: int = 0,
                  location_id: Optional[str] = None,
                  entity_id: Optional[str] = None,
                  time_range: Optional[Tuple[float, float]] = None,
                  limit: int = 10) -> List[Dict[str, Any]]:
        """
        Récupère des événements filtrés par type, importance, lieu, etc.
        
        Args:
            event_type: Filtrer par type d'événement
            min_importance: Importance minimale requise
            location_id: Filtrer par lieu
            entity_id: Filtrer par entité impliquée
            time_range: Tuple (début, fin) pour filtrer par période
            limit: Nombre maximum d'événements à retourner
            
        Returns:
            List[Dict[str, Any]]: Liste des événements correspondants
        """
        # Filtrer les événements
        filtered_events = self.events.copy()
        
        # Filtrer par type
        if event_type:
            filtered_events = [e for e in filtered_events if e['event_type'] == event_type]
        
        # Filtrer par importance minimale
        filtered_events = [e for e in filtered_events if e['importance'] >= min_importance]
        
        # Filtrer par lieu
        if location_id:
            filtered_events = [e for e in filtered_events if e['location_id'] == location_id]
        
        # Filtrer par entité impliquée
        if entity_id:
            filtered_events = [e for e in filtered_events if entity_id in e.get('involved_entities', [])]
        
        # Filtrer par période
        if time_range:
            start, end = time_range
            filtered_events = [e for e in filtered_events if start <= e['timestamp'] <= end]
        
        # Limiter le nombre de résultats
        return filtered_events[:limit]
    
    def add_world_fact(self, category: str, fact: str, importance: int = 5) -> None:
        """
        Ajoute un fait établi sur le monde.
        
        Args:
            category: Catégorie du fait (géographie, histoire, magie, etc.)
            fact: Description du fait
            importance: Importance du fait (1-10)
        """
        if category not in self.world_facts:
            self.world_facts[category] = []
        
        # Éviter les doublons
        for existing in self.world_facts[category]:
            if existing['fact'] == fact:
                # Mettre à jour l'importance si le fait existe déjà
                existing['importance'] = max(existing['importance'], importance)
                return
        
        # Ajouter le nouveau fait
        self.world_facts[category].append({
            'fact': fact,
            'importance': importance,
            'established_at': time.time()
        })
        
        # Mettre à jour le timestamp de dernière mise à jour
        self.last_updated = time.time()
    
    def get_world_facts(self, category: Optional[str] = None, min_importance: int = 0) -> Dict[str, List[Dict[str, Any]]]:
        """
        Récupère des faits sur le monde, filtrés par catégorie et importance.
        
        Args:
            category: Catégorie des faits (ou None pour toutes)
            min_importance: Importance minimale requise
            
        Returns:
            Dict[str, List[Dict[str, Any]]]: Dictionnaire des faits par catégorie
        """
        if category:
            # Retourner uniquement la catégorie demandée
            if category not in self.world_facts:
                return {category: []}
            
            # Filtrer par importance
            facts = [f for f in self.world_facts[category] if f['importance'] >= min_importance]
            return {category: facts}
        else:
            # Retourner toutes les catégories, filtrées par importance
            result = {}
            for cat, facts in self.world_facts.items():
                result[cat] = [f for f in facts if f['importance'] >= min_importance]
            return result
    
    def add_quest(self, 
                 quest_id: str,
                 title: str, 
                 description: str,
                 status: str = "inactive",
                 importance: int = 5,
                 location_ids: Optional[List[str]] = None,
                 involved_entities: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Ajoute ou met à jour une quête dans la mémoire globale.
        
        Args:
            quest_id: Identifiant unique de la quête
            title: Titre de la quête
            description: Description de la quête
            status: État de la quête (inactive, active, completed, failed)
            importance: Importance de la quête (1-10)
            location_ids: Liste des IDs des lieux associés à la quête
            involved_entities: Liste des IDs des entités impliquées
            
        Returns:
            Dict[str, Any]: La quête créée ou mise à jour
        """
        # Créer ou mettre à jour la quête
        if quest_id in self.quests:
            # Mettre à jour la quête existante
            quest = self.quests[quest_id]
            quest['title'] = title
            quest['description'] = description
            quest['status'] = status
            quest['importance'] = importance
            quest['location_ids'] = location_ids or quest.get('location_ids', [])
            quest['involved_entities'] = involved_entities or quest.get('involved_entities', [])
            quest['last_updated'] = time.time()
        else:
            # Créer une nouvelle quête
            quest = {
                'id': quest_id,
                'title': title,
                'description': description,
                'status': status,
                'importance': importance,
                'location_ids': location_ids or [],
                'involved_entities': involved_entities or [],
                'updates': [],
                'created_at': time.time(),
                'last_updated': time.time()
            }
            self.quests[quest_id] = quest
        
        # Mettre à jour le timestamp de dernière mise à jour
        self.last_updated = time.time()
        
        return quest
    
    def add_quest_update(self, quest_id: str, update: str, update_type: str = "progress") -> bool:
        """
        Ajoute une mise à jour à une quête existante.
        
        Args:
            quest_id: ID de la quête à mettre à jour
            update: Description de la mise à jour
            update_type: Type de mise à jour (progress, obstacle, resolution)
            
        Returns:
            bool: True si la mise à jour a été ajoutée, False si la quête n'existe pas
        """
        if quest_id not in self.quests:
            return False
        
        # Ajouter la mise à jour
        self.quests[quest_id]['updates'].append({
            'description': update,
            'type': update_type,
            'timestamp': time.time()
        })
        
        # Mettre à jour le timestamp de dernière mise à jour de la quête
        self.quests[quest_id]['last_updated'] = time.time()
        
        # Mettre à jour le timestamp de dernière mise à jour globale
        self.last_updated = time.time()
        
        return True
    
    def update_quest_status(self, quest_id: str, status: str) -> bool:
        """
        Met à jour le statut d'une quête.
        
        Args:
            quest_id: ID de la quête
            status: Nouveau statut (inactive, active, completed, failed)
            
        Returns:
            bool: True si le statut a été mis à jour, False si la quête n'existe pas
        """
        if quest_id not in self.quests:
            return False
        
        # Mettre à jour le statut
        self.quests[quest_id]['status'] = status
        
        # Mettre à jour le timestamp de dernière mise à jour de la quête
        self.quests[quest_id]['last_updated'] = time.time()
        
        # Ajouter une mise à jour automatique
        self.quests[quest_id]['updates'].append({
            'description': f"La quête est maintenant '{status}'.",
            'type': "status_change",
            'timestamp': time.time()
        })
        
        # Mettre à jour le timestamp de dernière mise à jour globale
        self.last_updated = time.time()
        
        return True
    
    def get_quests(self, 
                  status: Optional[str] = None, 
                  min_importance: int = 0,
                  location_id: Optional[str] = None,
                  entity_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Récupère des quêtes filtrées par statut, importance, lieu, etc.
        
        Args:
            status: Filtrer par statut
            min_importance: Importance minimale requise
            location_id: Filtrer par lieu associé
            entity_id: Filtrer par entité impliquée
            
        Returns:
            List[Dict[str, Any]]: Liste des quêtes correspondantes
        """
        filtered_quests = list(self.quests.values())
        
        # Filtrer par statut
        if status:
            filtered_quests = [q for q in filtered_quests if q['status'] == status]
        
        # Filtrer par importance minimale
        filtered_quests = [q for q in filtered_quests if q['importance'] >= min_importance]
        
        # Filtrer par lieu
        if location_id:
            filtered_quests = [q for q in filtered_quests if location_id in q.get('location_ids', [])]
        
        # Filtrer par entité impliquée
        if entity_id:
            filtered_quests = [q for q in filtered_quests if entity_id in q.get('involved_entities', [])]
        
        # Trier par importance
        filtered_quests.sort(key=lambda x: x['importance'], reverse=True)
        
        return filtered_quests
    
    def add_narrative_decision(self, 
                              description: str, 
                              decision_type: str = "world_building",
                              rationale: str = "",
                              alternatives: Optional[List[str]] = None,
                              impact_level: int = 5) -> Dict[str, Any]:
        """
        Enregistre une décision narrative importante prise par le MJ.
        
        Args:
            description: Description de la décision
            decision_type: Type de décision (world_building, character_fate, quest_direction)
            rationale: Justification de la décision
            alternatives: Alternatives envisagées mais non retenues
            impact_level: Niveau d'impact de la décision (1-10)
            
        Returns:
            Dict[str, Any]: La décision enregistrée
        """
        decision = {
            'id': self._generate_decision_id(),
            'description': description,
            'type': decision_type,
            'rationale': rationale,
            'alternatives': alternatives or [],
            'impact_level': impact_level,
            'timestamp': time.time()
        }
        
        # Ajouter à la liste des décisions
        self.narrative_decisions.append(decision)
        
        # Mettre à jour le timestamp de dernière mise à jour
        self.last_updated = time.time()
        
        return decision
    
    def get_narrative_decisions(self, 
                               decision_type: Optional[str] = None,
                               min_impact: int = 0,
                               limit: int = 10) -> List[Dict[str, Any]]:
        """
        Récupère des décisions narratives filtrées par type et impact.
        
        Args:
            decision_type: Filtrer par type de décision
            min_impact: Impact minimal requis
            limit: Nombre maximum de décisions à retourner
            
        Returns:
            List[Dict[str, Any]]: Liste des décisions correspondantes
        """
        filtered_decisions = self.narrative_decisions.copy()
        
        # Filtrer par type
        if decision_type:
            filtered_decisions = [d for d in filtered_decisions if d['type'] == decision_type]
        
        # Filtrer par impact minimal
        filtered_decisions = [d for d in filtered_decisions if d['impact_level'] >= min_impact]
        
        # Trier par niveau d'impact et chronologie (du plus récent au plus ancien)
        filtered_decisions.sort(key=lambda x: (x['impact_level'], x['timestamp']), reverse=True)
        
        # Limiter le nombre de résultats
        return filtered_decisions[:limit]
    
    def add_world_state_change(self, 
                              entity_id: str,
                              entity_type: str,
                              property_name: str,
                              old_value: Any,
                              new_value: Any,
                              change_reason: str = "") -> Dict[str, Any]:
        """
        Enregistre un changement d'état significatif dans le monde.
        
        Args:
            entity_id: ID de l'entité modifiée
            entity_type: Type d'entité (npc, location, item)
            property_name: Nom de la propriété modifiée
            old_value: Ancienne valeur
            new_value: Nouvelle valeur
            change_reason: Raison du changement
            
        Returns:
            Dict[str, Any]: Le changement enregistré
        """
        change = {
            'id': self._generate_change_id(),
            'entity_id': entity_id,
            'entity_type': entity_type,
            'property': property_name,
            'old_value': old_value,
            'new_value': new_value,
            'reason': change_reason,
            'timestamp': time.time()
        }
        
        # Ajouter à la liste des changements
        self.world_state_changes.append(change)
        
        # Mettre à jour le timestamp de dernière mise à jour
        self.last_updated = time.time()
        
        return change
    
    def get_world_state_changes(self,
                               entity_id: Optional[str] = None,
                               entity_type: Optional[str] = None,
                               property_name: Optional[str] = None,
                               limit: int = 20) -> List[Dict[str, Any]]:
        """
        Récupère l'historique des changements d'état du monde.
        
        Args:
            entity_id: Filtrer par ID d'entité
            entity_type: Filtrer par type d'entité
            property_name: Filtrer par nom de propriété
            limit: Nombre maximum de changements à retourner
            
        Returns:
            List[Dict[str, Any]]: Liste des changements correspondants
        """
        filtered_changes = self.world_state_changes.copy()
        
        # Filtrer par ID d'entité
        if entity_id:
            filtered_changes = [c for c in filtered_changes if c['entity_id'] == entity_id]
        
        # Filtrer par type d'entité
        if entity_type:
            filtered_changes = [c for c in filtered_changes if c['entity_type'] == entity_type]
        
        # Filtrer par nom de propriété
        if property_name:
            filtered_changes = [c for c in filtered_changes if c['property'] == property_name]
        
        # Trier par chronologie (du plus récent au plus ancien)
        filtered_changes.sort(key=lambda x: x['timestamp'], reverse=True)
        
        # Limiter le nombre de résultats
        return filtered_changes[:limit]
    
    def track_entity(self, entity_id: str, entity_type: str) -> None:
        """
        Ajoute une entité à la liste des entités importantes à suivre.
        
        Args:
            entity_id: ID de l'entité
            entity_type: Type d'entité (npc, location, item)
        """
        if entity_type in self.tracked_entities:
            self.tracked_entities[entity_type].add(entity_id)
            self.last_updated = time.time()
    
    def untrack_entity(self, entity_id: str, entity_type: str) -> bool:
        """
        Retire une entité de la liste des entités importantes à suivre.
        
        Args:
            entity_id: ID de l'entité
            entity_type: Type d'entité (npc, location, item)
            
        Returns:
            bool: True si l'entité a été retirée, False sinon
        """
        if entity_type in self.tracked_entities and entity_id in self.tracked_entities[entity_type]:
            self.tracked_entities[entity_type].remove(entity_id)
            self.last_updated = time.time()
            return True
        return False
    
    def get_tracked_entities(self, entity_type: Optional[str] = None) -> Dict[str, Set[str]]:
        """
        Récupère la liste des entités importantes suivies.
        
        Args:
            entity_type: Type d'entité à récupérer (ou None pour tous)
            
        Returns:
            Dict[str, Set[str]]: Dictionnaire des entités suivies par type
        """
        if entity_type:
            return {entity_type: self.tracked_entities.get(entity_type, set())}
        else:
            return {k: v.copy() for k, v in self.tracked_entities.items()}
    
    def summarize_world_state(self) -> Dict[str, Any]:
        """
        Génère un résumé de l'état actuel du monde.
        
        Returns:
            Dict[str, Any]: Résumé de l'état du monde
        """
        # Compter les quêtes par statut
        quest_stats = {'active': 0, 'completed': 0, 'failed': 0, 'inactive': 0}
        for quest in self.quests.values():
            status = quest['status']
            if status in quest_stats:
                quest_stats[status] += 1
        
        # Récupérer les événements récents importants
        recent_events = self.get_events(min_importance=7, limit=5)
        
        # Récupérer les changements d'état récents
        recent_changes = self.get_world_state_changes(limit=10)
        
        # Récupérer les décisions narratives importantes
        important_decisions = self.get_narrative_decisions(min_impact=8, limit=3)
        
        return {
            'world_id': self.world_id,
            'world_name': self.world_name,
            'last_updated': self.last_updated,
            'total_events': len(self.events),
            'total_quests': len(self.quests),
            'quest_stats': quest_stats,
            'fact_categories': list(self.world_facts.keys()),
            'tracked_entities_count': {k: len(v) for k, v in self.tracked_entities.items()},
            'recent_important_events': recent_events,
            'recent_state_changes': recent_changes,
            'important_decisions': important_decisions
        }
    
    def save_to_file(self, file_path: str) -> bool:
        """
        Sauvegarde la mémoire globale dans un fichier JSON.
        
        Args:
            file_path: Chemin du fichier où sauvegarder
            
        Returns:
            bool: True si la sauvegarde a réussi, False sinon
        """
        try:
            # Préparer les données sérialisables (convertir les sets en listes)
            data = self.to_dict()
            
            # Créer le répertoire si nécessaire
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Écrire dans le fichier
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"Erreur lors de la sauvegarde de la mémoire globale: {e}")
            return False
    
    @classmethod
    def load_from_file(cls, file_path: str) -> Optional['GlobalMemory']:
        """
        Charge la mémoire globale depuis un fichier JSON.
        
        Args:
            file_path: Chemin du fichier à charger
            
        Returns:
            Optional[GlobalMemory]: Instance de mémoire globale chargée, ou None si erreur
        """
        try:
            # Lire le fichier
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Créer l'instance à partir des données
            return cls.from_dict(data)
        except Exception as e:
            print(f"Erreur lors du chargement de la mémoire globale: {e}")
            return None
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convertit la mémoire globale en dictionnaire sérialisable.
        
        Returns:
            Dict[str, Any]: Représentation dictionnaire de la mémoire
        """
        # Convertir les sets en listes pour la sérialisation
        tracked_entities = {k: list(v) for k, v in self.tracked_entities.items()}
        
        return {
            'world_id': self.world_id,
            'world_name': self.world_name,
            'events': self.events.copy(),
            'world_facts': self.world_facts.copy(),
            'quests': self.quests.copy(),
            'narrative_decisions': self.narrative_decisions.copy(),
            'world_state_changes': self.world_state_changes.copy(),
            'tracked_entities': tracked_entities,
            'last_updated': self.last_updated
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GlobalMemory':
        """
        Crée une mémoire globale à partir d'un dictionnaire sérialisé.
        
        Args:
            data: Dictionnaire contenant les données de la mémoire
            
        Returns:
            GlobalMemory: Instance de mémoire globale créée
        """
        memory = cls(
            world_id=data['world_id'],
            world_name=data['world_name']
        )
        
        memory.events = data.get('events', []).copy()
        memory.world_facts = data.get('world_facts', {}).copy()
        memory.quests = data.get('quests', {}).copy()
        memory.narrative_decisions = data.get('narrative_decisions', []).copy()
        memory.world_state_changes = data.get('world_state_changes', []).copy()
        
        # Convertir les listes en sets pour les entités suivies
        tracked_entities = data.get('tracked_entities', {})
        for entity_type, entities in tracked_entities.items():
            memory.tracked_entities[entity_type] = set(entities)
        
        memory.last_updated = data.get('last_updated', time.time())
        
        return memory
    
    def _generate_event_id(self) -> str:
        """
        Génère un ID unique pour un événement.
        
        Returns:
            str: ID unique
        """
        import uuid
        return f"evt_{uuid.uuid4().hex[:8]}"
    
    def _generate_decision_id(self) -> str:
        """
        Génère un ID unique pour une décision narrative.
        
        Returns:
            str: ID unique
        """
        import uuid
        return f"dec_{uuid.uuid4().hex[:8]}"
    
    def _generate_change_id(self) -> str:
        """
        Génère un ID unique pour un changement d'état.
        
        Returns:
            str: ID unique
        """
        import uuid
        return f"chg_{uuid.uuid4().hex[:8]}"

    # ====== MÉTHODES POUR LES LLMs LÉGERS ======
    
    def get_concise_summary(self, max_size: int = 1000) -> Dict[str, Any]:
        """
        Génère un résumé concis de la mémoire globale, optimisé pour les LLMs légers.
        
        Args:
            max_size: Taille maximale approximative du résumé en caractères
            
        Returns:
            Dict[str, Any]: Résumé condensé de la mémoire globale
        """
        # Structure de base du résumé
        summary = {
            "world": {
                "id": self.world_id,
                "name": self.world_name,
                "last_updated": self.last_updated
            },
            "events": [],
            "facts": {},
            "quests": [],
            "state": {}
        }
        
        # Estimation de la taille initiale
        char_count = len(json.dumps(summary["world"]))
        
        # Événements importants récents
        recent_major_events = self.get_events(min_importance=7, limit=3)
        
        for event in recent_major_events:
            if char_count < max_size:
                event_entry = {
                    "description": event['description'],
                    "importance": event['importance']
                }
                
                event_json = json.dumps(event_entry)
                if char_count + len(event_json) < max_size:
                    summary["events"].append(event_entry)
                    char_count += len(event_json)
                else:
                    break
        
        # Faits importants par catégorie
        all_facts = self.get_world_facts(min_importance=6)
        
        for category, facts in all_facts.items():
            if char_count < max_size:
                category_facts = []
                
                for fact in facts:
                    fact_text = fact['fact']
                    if char_count + len(fact_text) < max_size:
                        category_facts.append(fact_text)
                        char_count += len(fact_text) + 5
                    else:
                        break
                
                if category_facts:
                    summary["facts"][category] = category_facts
        
        # Quêtes actives
        active_quests = self.get_quests(status="active", min_importance=5)
        
        for quest in active_quests:
            if char_count < max_size:
                quest_entry = {
                    "title": quest['title'],
                    "status": quest['status']
                }
                
                # Ajouter une description courte si possible
                if 'description' in quest and char_count + len(quest['description']) < max_size:
                    quest_entry["description"] = quest['description']
                    char_count += len(quest['description'])
                
                quest_json = json.dumps(quest_entry)
                if char_count + len(quest_json) < max_size:
                    summary["quests"].append(quest_entry)
                    char_count += len(quest_json)
                else:
                    break
        
        # Statistiques synthétiques sur l'état du monde
        summary["state"] = {
            "total_events": len(self.events),
            "active_quests": sum(1 for q in self.quests.values() if q['status'] == 'active'),
            "completed_quests": sum(1 for q in self.quests.values() if q['status'] == 'completed'),
            "tracked_entities": {k: len(v) for k, v in self.tracked_entities.items()}
        }
        
        return summary
    
    def generate_world_context(self, max_tokens: int = 800) -> str:
        """
        Génère un contexte textuel formaté sur l'état du monde, 
        optimisé pour alimenter un prompt de LLM léger.
        
        Args:
            max_tokens: Estimation du nombre maximum de tokens (1 token ≈ 4 caractères)
            
        Returns:
            str: Contexte formaté sur l'état du monde
        """
        # Estimer la taille maximale en caractères
        max_size = max_tokens * 4
        
        # Récupérer le résumé
        summary = self.get_concise_summary(max_size=max_size)
        
        # Formater en texte pour un contexte narratif
        text = f"# {summary['world']['name']}\n\n"
        
        # Événements
        if summary.get('events'):
            text += "## Événements récents importants\n"
            for event in summary['events']:
                text += f"- {event['description']}\n"
            text += "\n"
        
        # Faits
        if summary.get('facts'):
            text += "## Faits établis sur le monde\n"
            for category, facts in summary['facts'].items():
                text += f"### {category.capitalize()}\n"
                for fact in facts:
                    text += f"- {fact}\n"
                text += "\n"
        
        # Quêtes
        if summary.get('quests'):
            text += "## Quêtes en cours\n"
            for quest in summary['quests']:
                if 'description' in quest:
                    text += f"- {quest['title']}: {quest['description']}\n"
                else:
                    text += f"- {quest['title']}\n"
            text += "\n"
        
        # État du monde
        if summary.get('state'):
            state = summary['state']
            text += "## État actuel du monde\n"
            text += f"- Total d'événements: {state['total_events']}\n"
            text += f"- Quêtes actives: {state['active_quests']}\n"
            text += f"- Quêtes terminées: {state['completed_quests']}\n"
            
            if 'tracked_entities' in state:
                entities = state['tracked_entities']
                text += "- Entités suivies:\n"
                for entity_type, count in entities.items():
                    if count > 0:
                        text += f"  • {entity_type}: {count}\n"
        
        return text
    
    def explain_quest_context(self, quest_id: str, max_size: int = 800) -> Dict[str, Any]:
        """
        Génère un contexte explicatif pour une quête spécifique,
        optimisé pour les LLMs légers.
        
        Args:
            quest_id: ID de la quête
            max_size: Taille maximale approximative du contexte en caractères
            
        Returns:
            Dict[str, Any]: Contexte de la quête
        """
        # Vérifier si la quête existe
        if quest_id not in self.quests:
            return {"error": f"Quête {quest_id} non trouvée"}
        
        # Récupérer la quête
        quest = self.quests[quest_id]
        
        # Structure de base du contexte
        context = {
            "quest": {
                "id": quest_id,
                "title": quest['title'],
                "status": quest['status'],
                "importance": quest['importance']
            },
            "history": [],
            "related_events": [],
            "involved_entities": []
        }
        
        # Estimation de la taille initiale
        char_count = len(json.dumps(context["quest"]))
        
        # Ajouter la description si possible
        if 'description' in quest and char_count + len(quest['description']) < max_size:
            context["quest"]["description"] = quest['description']
            char_count += len(quest['description'])
        
        # Ajouter l'historique des mises à jour
        if 'updates' in quest:
            for update in reversed(quest['updates']):  # Du plus récent au plus ancien
                if char_count < max_size:
                    update_entry = {
                        "description": update['description'],
                        "type": update['type']
                    }
                    
                    update_json = json.dumps(update_entry)
                    if char_count + len(update_json) < max_size:
                        context["history"].append(update_entry)
                        char_count += len(update_json)
                    else:
                        break
                else:
                    break
        
        # Ajouter les événements liés à la quête
        quest_events = self.get_events(event_type=f"quest_{quest_id}", limit=5)
        
        for event in quest_events:
            if char_count < max_size:
                event_entry = {
                    "description": event['description'],
                    "importance": event['importance']
                }
                
                event_json = json.dumps(event_entry)
                if char_count + len(event_json) < max_size:
                    context["related_events"].append(event_entry)
                    char_count += len(event_json)
                else:
                    break
            else:
                break
        
        # Ajouter les entités impliquées
        if 'involved_entities' in quest and quest['involved_entities']:
            for entity_id in quest['involved_entities']:
                if char_count < max_size:
                    # Cette partie serait mieux gérée par MemoryManager qui a accès aux noms des entités
                    entity_entry = {
                        "id": entity_id
                    }
                    
                    entity_json = json.dumps(entity_entry)
                    if char_count + len(entity_json) < max_size:
                        context["involved_entities"].append(entity_entry)
                        char_count += len(entity_json)
                    else:
                        break
                else:
                    break
        
        return context
    
    def get_recent_narrative_arc(self, max_events: int = 5, max_size: int = 1200) -> Dict[str, Any]:
        """
        Génère un arc narratif récent basé sur les événements importants et les décisions,
        optimisé pour les LLMs légers.
        
        Args:
            max_events: Nombre maximum d'événements à inclure
            max_size: Taille maximale approximative de l'arc en caractères
            
        Returns:
            Dict[str, Any]: Arc narratif récent
        """
        arc = {
            "title": f"Arc narratif récent - {self.world_name}",
            "timestamp": time.time(),
            "key_events": [],
            "narrative_decisions": [],
            "current_state": {},
            "emerging_themes": []
        }
        
        char_count = len(json.dumps(arc["title"])) + 50
        
        # Événements clés récents par importance
        recent_events = self.get_events(min_importance=6, limit=max_events*2)
        
        for event in recent_events:
            if len(arc["key_events"]) < max_events and char_count < max_size:
                event_entry = {
                    "description": event['description'],
                    "importance": event['importance']
                }
                
                event_json = json.dumps(event_entry)
                if char_count + len(event_json) < max_size:
                    arc["key_events"].append(event_entry)
                    char_count += len(event_json)
                else:
                    break
            else:
                break
        
        # Décisions narratives
        recent_decisions = self.get_narrative_decisions(min_impact=6, limit=3)
        
        for decision in recent_decisions:
            if char_count < max_size:
                decision_entry = {
                    "description": decision['description']
                }
                
                # Ajouter la justification si l'espace le permet
                if 'rationale' in decision and char_count + len(decision['rationale']) < max_size:
                    decision_entry["rationale"] = decision['rationale']
                    char_count += len(decision['rationale'])
                
                decision_json = json.dumps(decision_entry)
                if char_count + len(decision_json) < max_size:
                    arc["narrative_decisions"].append(decision_entry)
                    char_count += len(decision_json)
                else:
                    break
            else:
                break
        
        # État actuel (quêtes actives, etc.)
        arc["current_state"] = {
            "active_quests": len(self.get_quests(status="active")),
            "pending_resolutions": len(self.get_quests(status="active", min_importance=7))
        }
        
        # Cette partie devrait idéalement être déterminée par une analyse plus complexe
        # Pour l'instant, c'est plus un espace réservé pour une future implémentation
        arc["emerging_themes"] = ["conflit", "exploration", "mystère"]
        
        return arc
    
    def generate_prompt_template(self, template_type: str = "narrative_continuation") -> str:
        """
        Génère un template de prompt prêt à l'emploi pour un LLM léger,
        en utilisant les données de la mémoire globale.
        
        Args:
            template_type: Type de template ("narrative_continuation", "quest_generation", "world_building")
            
        Returns:
            str: Template de prompt formaté
        """
        if template_type == "narrative_continuation":
            # Récupérer les éléments nécessaires
            summary = self.get_concise_summary(max_size=1200)
            
            # Construire le template
            prompt = f"""Tu es le maître du jeu pour un monde nommé "{self.world_name}".

Voici l'état actuel du monde :
"""
            
            # Ajouter les événements récents
            if summary.get('events'):
                prompt += "\nÉvénements récents importants :\n"
                for event in summary['events']:
                    prompt += f"- {event['description']}\n"
            
            # Ajouter les quêtes actives
            if summary.get('quests'):
                prompt += "\nQuêtes en cours :\n"
                for quest in summary['quests']:
                    if 'description' in quest:
                        prompt += f"- {quest['title']}: {quest['description']}\n"
                    else:
                        prompt += f"- {quest['title']}\n"
            
            # Compléter le template
            prompt += """
En te basant sur ces éléments, continue la narration de manière cohérente. 
Tu peux introduire de nouveaux éléments, mais ils doivent s'intégrer logiquement avec les faits établis.

La suite de l'histoire :
"""
            
            return prompt
            
        elif template_type == "quest_generation":
            # Récupérer faits et événements
            facts = self.get_world_facts(min_importance=7)
            fact_examples = []
            
            for category, fact_list in facts.items():
                for fact in fact_list[:2]:  # Limiter à 2 faits par catégorie
                    fact_examples.append(f"- {fact['fact']}")
            
            # Construire le template
            prompt = f"""Génère une nouvelle quête pour le monde "{self.world_name}" en te basant sur ces faits établis :

{chr(10).join(fact_examples)}

La quête doit inclure :
1. Un titre accrocheur
2. Une description du problème ou de l'objectif
3. Les étapes principales pour la compléter
4. Les récompenses potentielles

Nouvelle quête :
"""
            
            return prompt
            
        elif template_type == "world_building":
            prompt = f"""Développe un nouvel aspect du monde "{self.world_name}" qui n'a pas encore été exploré.
Cela peut être une région, une tradition, une faction, ou un aspect culturel.

Ton développement doit :
1. Être cohérent avec l'univers existant
2. Ajouter de la profondeur au monde
3. Offrir des opportunités d'intrigue
4. Être mémorable et unique

Nouvel élément du monde :
"""
            
            return prompt
            
        else:
            return f"Type de template '{template_type}' non reconnu."