#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MemoryManager - Gestionnaire centralisé des différents systèmes de mémoire
"""

import time
import json
import os
from typing import Dict, List, Any, Optional, Tuple, Union, Set

from .global_memory import GlobalMemory
from .local_memory import LocalMemory
from .social_memory import SocialMemory

class MemoryManager:
    """
    Gestionnaire centralisé des différents systèmes de mémoire.
    Coordonne les interactions entre mémoire globale, locale et sociale.
    Optimisé pour fournir un contexte synthétique aux LLMs légers.
    """
    
    def __init__(self, world_id: str, world_name: str):
        """
        Initialise un nouveau gestionnaire de mémoire.
        
        Args:
            world_id: ID du monde
            world_name: Nom du monde
        """
        self.world_id = world_id
        self.world_name = world_name
        
        # Initialiser les systèmes de mémoire
        self.global_memory = GlobalMemory(world_id, world_name)
        self.social_memory = SocialMemory(world_id)
        
        # Dictionnaire des mémoires locales par entité
        self.local_memories: Dict[str, LocalMemory] = {}
        
        # Cache pour les résumés (optimisation)
        self._summary_cache = {}
        self._cache_timestamp = time.time()
        self._cache_lifetime = 60  # Durée de vie du cache en secondes
    
    def register_entity(self, entity_id: str, entity_type: str, entity_name: str, 
                        max_memory_size: int = 100) -> LocalMemory:
        """
        Enregistre une nouvelle entité et crée sa mémoire locale.
        
        Args:
            entity_id: ID de l'entité
            entity_type: Type d'entité (npc, location, item, player)
            entity_name: Nom de l'entité
            max_memory_size: Taille maximale de la mémoire locale
            
        Returns:
            LocalMemory: La mémoire locale créée
        """
        local_memory = LocalMemory(entity_id, entity_type, entity_name, max_memory_size)
        self.local_memories[entity_id] = local_memory
        return local_memory
    
    def get_local_memory(self, entity_id: str) -> Optional[LocalMemory]:
        """
        Récupère la mémoire locale d'une entité.
        
        Args:
            entity_id: ID de l'entité
            
        Returns:
            Optional[LocalMemory]: La mémoire locale ou None si non trouvée
        """
        return self.local_memories.get(entity_id)
    
    # ====== MÉTHODES DE SYNCHRONISATION ENTRE MÉMOIRES ======
    
    def memorize_global_event(self, 
                             description: str, 
                             importance: int = 5,
                             event_type: str = "world_event",
                             location_id: Optional[str] = None,
                             involved_entities: Optional[List[str]] = None,
                             local_importance_modifier: int = 0,
                             also_memorize_locally: bool = True) -> Dict[str, Any]:
        """
        Mémorise un événement dans la mémoire globale et optionnellement dans les mémoires locales.
        
        Args:
            description: Description de l'événement
            importance: Importance globale (1-10)
            event_type: Type d'événement
            location_id: ID du lieu
            involved_entities: Liste des IDs des entités impliquées
            local_importance_modifier: Modificateur d'importance pour les mémoires locales
            also_memorize_locally: Si True, ajoute aussi l'événement aux mémoires locales des entités impliquées
            
        Returns:
            Dict[str, Any]: L'événement créé
        """
        # Ajouter à la mémoire globale
        event = self.global_memory.add_event(
            description=description,
            importance=importance,
            event_type=event_type,
            location_id=location_id,
            involved_entities=involved_entities
        )
        
        # Ajouter aux mémoires locales si demandé
        if also_memorize_locally and involved_entities:
            local_importance = min(10, max(1, importance + local_importance_modifier))
            
            for entity_id in involved_entities:
                local_memory = self.get_local_memory(entity_id)
                if local_memory:
                    involved = {e: "participant" for e in involved_entities if e != entity_id}
                    local_memory.add_memory(
                        description=description,
                        importance=local_importance,
                        memory_type="global_event",
                        location_id=location_id,
                        involved_entities=involved,
                        timestamp=event['timestamp'],
                        tags=[event_type]
                    )
        
        # Invalider le cache des résumés
        self._invalidate_cache()
        
        return event
    
    def sync_world_fact(self, 
                       category: str, 
                       fact: str, 
                       importance: int = 5,
                       relevant_entity_ids: Optional[List[str]] = None,
                       knowledge_category: Optional[str] = None) -> None:
        """
        Synchronise un fait entre la mémoire globale et les mémoires locales.
        
        Args:
            category: Catégorie du fait dans la mémoire globale
            fact: Description du fait
            importance: Importance du fait (1-10)
            relevant_entity_ids: IDs des entités pour lesquelles ce fait est pertinent
            knowledge_category: Catégorie de connaissance pour les mémoires locales (utilise category si None)
        """
        # Ajouter à la mémoire globale
        self.global_memory.add_world_fact(category, fact, importance)
        
        # Ajouter aux mémoires locales des entités pertinentes
        if relevant_entity_ids:
            local_knowledge_category = knowledge_category or category
            
            for entity_id in relevant_entity_ids:
                local_memory = self.get_local_memory(entity_id)
                if local_memory:
                    # Générer une clé unique pour cette connaissance
                    fact_key = f"fact_{hash(fact) % 10000}"
                    local_memory.add_knowledge(local_knowledge_category, fact_key, fact, importance)
        
        # Invalider le cache des résumés
        self._invalidate_cache()
    
    def record_interaction(self,
                          entity1_id: str, 
                          entity2_id: str,
                          interaction_type: str,
                          description: str,
                          impact: int = 0,
                          location_id: Optional[str] = None,
                          witnesses: Optional[List[str]] = None,
                          global_importance: int = 5) -> str:
        """
        Enregistre une interaction entre deux entités dans tous les systèmes de mémoire pertinents.
        
        Args:
            entity1_id: ID de la première entité
            entity2_id: ID de la seconde entité
            interaction_type: Type d'interaction
            description: Description de l'interaction
            impact: Impact sur la relation (-10 à +10)
            location_id: ID du lieu
            witnesses: Liste des IDs des témoins
            global_importance: Importance pour la mémoire globale (1-10)
            
        Returns:
            str: ID de l'interaction créée
        """
        # Récupérer les noms des entités
        entity1_name = (self.get_local_memory(entity1_id).entity_name 
                        if self.get_local_memory(entity1_id) else "Entity 1")
        entity2_name = (self.get_local_memory(entity2_id).entity_name 
                        if self.get_local_memory(entity2_id) else "Entity 2")
        
        # Enregistrer dans la mémoire sociale
        interaction_id = self.social_memory.add_interaction(
            entity1_id=entity1_id,
            entity1_name=entity1_name,
            entity2_id=entity2_id,
            entity2_name=entity2_name,
            interaction_type=interaction_type,
            description=description,
            impact=impact,
            location_id=location_id,
            witnesses=witnesses
        )
        
        # Enregistrer dans les mémoires locales des entités impliquées
        # Pour l'entité 1
        local_memory1 = self.get_local_memory(entity1_id)
        if local_memory1:
            involved = {f"entity:{entity2_id}": "target"}
            local_memory1.add_memory(
                description=description,
                importance=max(3, abs(impact) + 3),  # Plus grand impact => plus important
                memory_type="interaction",
                location_id=location_id,
                involved_entities=involved,
                tags=[interaction_type]
            )
            # Mise à jour de la familiarité
            local_memory1.update_entity_familiarity(entity2_id, "npcs", 1)
        
        # Pour l'entité 2
        local_memory2 = self.get_local_memory(entity2_id)
        if local_memory2:
            involved = {f"entity:{entity1_id}": "initiator"}
            local_memory2.add_memory(
                description=description,
                importance=max(3, abs(impact) + 3),
                memory_type="interaction",
                location_id=location_id,
                involved_entities=involved,
                tags=[interaction_type]
            )
            # Mise à jour de la familiarité
            local_memory2.update_entity_familiarity(entity1_id, "npcs", 1)
        
        # Pour les témoins
        if witnesses:
            for witness_id in witnesses:
                if witness_id not in [entity1_id, entity2_id]:  # Éviter les doublons
                    witness_memory = self.get_local_memory(witness_id)
                    if witness_memory:
                        involved = {
                            f"entity:{entity1_id}": "initiator",
                            f"entity:{entity2_id}": "target"
                        }
                        witness_memory.add_memory(
                            description=f"J'ai vu: {description}",
                            importance=max(2, abs(impact) + 1),  # Moins important pour les témoins
                            memory_type="observation",
                            location_id=location_id,
                            involved_entities=involved,
                            tags=["witnessed", interaction_type]
                        )
        
        # Si l'interaction est assez importante, l'ajouter à la mémoire globale
        if global_importance >= 4:
            self.global_memory.add_event(
                description=f"Interaction: {description}",
                importance=global_importance,
                event_type=f"interaction_{interaction_type}",
                location_id=location_id,
                involved_entities=[entity1_id, entity2_id]
            )
        
        # Invalider le cache des résumés
        self._invalidate_cache()
        
        return interaction_id
    
    def update_entity_state(self,
                           entity_id: str,
                           entity_type: str,
                           property_name: str,
                           old_value: Any,
                           new_value: Any,
                           change_reason: str = "",
                           global_importance: int = 3) -> None:
        """
        Met à jour l'état d'une entité et enregistre ce changement.
        
        Args:
            entity_id: ID de l'entité
            entity_type: Type d'entité
            property_name: Nom de la propriété modifiée
            old_value: Ancienne valeur
            new_value: Nouvelle valeur
            change_reason: Raison du changement
            global_importance: Importance pour la mémoire globale (1-10)
        """
        # Enregistrer le changement dans la mémoire globale
        self.global_memory.add_world_state_change(
            entity_id=entity_id,
            entity_type=entity_type,
            property_name=property_name,
            old_value=old_value,
            new_value=new_value,
            change_reason=change_reason
        )
        
        # Si le changement est significatif, l'ajouter comme événement
        if global_importance >= 4:
            entity_name = (self.get_local_memory(entity_id).entity_name 
                           if self.get_local_memory(entity_id) else f"{entity_type}:{entity_id}")
            
            self.global_memory.add_event(
                description=f"Changement d'état: {entity_name} - {property_name} a changé de {old_value} à {new_value}. {change_reason}",
                importance=global_importance,
                event_type="state_change",
                involved_entities=[entity_id]
            )
        
        # Mettre à jour la mémoire locale de l'entité
        local_memory = self.get_local_memory(entity_id)
        if local_memory:
            local_memory.add_memory(
                description=f"Mon attribut {property_name} a changé de {old_value} à {new_value}. {change_reason}",
                importance=min(7, global_importance + 2),  # Plus important pour l'entité elle-même
                memory_type="self_change",
                tags=["state_change", property_name]
            )
        
        # Invalider le cache des résumés
        self._invalidate_cache()
    
    # ====== MÉTHODES POUR LES LLMs LÉGERS ======
    
    def get_entity_context(self, 
                          entity_id: str, 
                          max_size: int = 1500,
                          include_global_events: bool = True,
                          include_knowledge: bool = True) -> Dict[str, Any]:
        """
        Génère un contexte compact pour une entité spécifique, optimisé pour les LLMs légers.
        
        Args:
            entity_id: ID de l'entité
            max_size: Taille maximale approximative du contexte en caractères
            include_global_events: Inclure les événements globaux pertinents
            include_knowledge: Inclure les connaissances de l'entité
            
        Returns:
            Dict[str, Any]: Contexte formaté pour l'entité
        """
        result = {"entity": None, "memories": [], "knowledge": {}, "relationships": [], "global_context": []}
        char_count = 0
        
        # Info de base sur l'entité
        local_memory = self.get_local_memory(entity_id)
        if not local_memory:
            return {"error": f"Entité {entity_id} non trouvée"}
        
        result["entity"] = {
            "id": entity_id,
            "type": local_memory.entity_type,
            "name": local_memory.entity_name
        }
        char_count += len(json.dumps(result["entity"]))
        
        # Souvenirs importants et récents
        important_memories = local_memory.get_memories(min_importance=7, limit=3)
        recent_memories = local_memory.get_memories(limit=5)
        
        # Fusionner et dédupliquer
        memories = []
        memory_ids = set()
        for memory in important_memories + recent_memories:
            if memory['id'] not in memory_ids and char_count < max_size:
                memories.append({
                    "description": memory['description'],
                    "importance": memory['importance'],
                    "type": memory['memory_type']
                })
                memory_ids.add(memory['id'])
                char_count += len(memory['description']) + 30
        
        result["memories"] = memories
        
        # Connaissances importantes
        if include_knowledge and char_count < max_size:
            knowledge = local_memory.get_knowledge()
            filtered_knowledge = {}
            
            for category, items in knowledge.items():
                filtered_items = {}
                for key, value in items.items():
                    # Convertir en string si ce n'est pas déjà le cas
                    if not isinstance(value, str):
                        value = str(value)
                    
                    if char_count + len(value) + len(category) + len(key) < max_size:
                        filtered_items[key] = value
                        char_count += len(value) + len(category) + len(key) + 10
                    else:
                        break
                
                if filtered_items:
                    filtered_knowledge[category] = filtered_items
            
            result["knowledge"] = filtered_knowledge
        
        # Relations significatives
        social_relations = self.social_memory.get_entity_relationships(entity_id)
        relationships = []
        
        for other_id, relation in social_relations.items():
            if char_count < max_size:
                other_name = (self.get_local_memory(other_id).entity_name 
                              if self.get_local_memory(other_id) else f"Entity {other_id}")
                
                relationships.append({
                    "entity": other_name,
                    "affinity": relation['affinity'],
                    "interaction_count": relation['interaction_count']
                })
                
                char_count += len(other_name) + 30
            else:
                break
        
        result["relationships"] = relationships
        
        # Contexte global pertinent
        if include_global_events and char_count < max_size:
            # Événements globaux récents
            global_events = self.global_memory.get_events(min_importance=6, entity_id=entity_id, limit=3)
            global_events.extend(self.global_memory.get_events(min_importance=8, limit=2))
            
            event_ids = set()
            global_context = []
            
            for event in global_events:
                if event['id'] not in event_ids and char_count < max_size:
                    global_context.append({
                        "description": event['description'],
                        "importance": event['importance']
                    })
                    event_ids.add(event['id'])
                    char_count += len(event['description']) + 20
            
            result["global_context"] = global_context
        
        return result
    
    def get_world_summary(self, max_size: int = 2000) -> Dict[str, Any]:
        """
        Génère un résumé compact du monde actuel, optimisé pour les LLMs légers.
        
        Args:
            max_size: Taille maximale approximative du résumé en caractères
            
        Returns:
            Dict[str, Any]: Résumé du monde
        """
        # Vérifier si le cache est valide
        if "world_summary" in self._summary_cache and time.time() - self._cache_timestamp < self._cache_lifetime:
            cached = self._summary_cache["world_summary"]
            if len(json.dumps(cached)) <= max_size:
                return cached
        
        result = {
            "world": {
                "id": self.world_id,
                "name": self.world_name
            },
            "global_facts": {},
            "recent_events": [],
            "active_quests": [],
            "key_entities": {}
        }
        char_count = len(json.dumps(result["world"]))
        
        # Faits globaux importants
        facts = self.global_memory.get_world_facts(min_importance=6)
        filtered_facts = {}
        
        for category, fact_list in facts.items():
            if char_count < max_size:
                cat_facts = []
                for fact in fact_list:
                    if char_count + len(fact['fact']) < max_size:
                        cat_facts.append(fact['fact'])
                        char_count += len(fact['fact']) + 5
                    else:
                        break
                
                if cat_facts:
                    filtered_facts[category] = cat_facts
        
        result["global_facts"] = filtered_facts
        
        # Événements récents importants
        events = self.global_memory.get_events(min_importance=7, limit=5)
        for event in events:
            if char_count < max_size:
                result["recent_events"].append({
                    "description": event['description'],
                    "importance": event['importance']
                })
                char_count += len(event['description']) + 20
            else:
                break
        
        # Quêtes actives
        quests = self.global_memory.get_quests(status="active", min_importance=5)
        for quest in quests:
            if char_count < max_size:
                result["active_quests"].append({
                    "title": quest['title'],
                    "description": quest['description']
                })
                char_count += len(quest['title']) + len(quest['description']) + 10
            else:
                break
        
        # Entités clés (en se basant sur la mémoire sociale)
        influential = self.social_memory.get_influential_entities(top_n=5)
        for entity_id, score in influential:
            if char_count < max_size:
                local_memory = self.get_local_memory(entity_id)
                if local_memory:
                    result["key_entities"][local_memory.entity_name] = {
                        "type": local_memory.entity_type,
                        "influence": score
                    }
                    char_count += len(local_memory.entity_name) + 30
            else:
                break
        
        # Mettre en cache
        self._summary_cache["world_summary"] = result
        self._cache_timestamp = time.time()
        
        return result
    
    def explain_last_events(self, max_events: int = 5, max_size: int = 1000) -> Dict[str, Any]:
        """
        Génère une explication des derniers événements importants.
        
        Args:
            max_events: Nombre maximum d'événements à inclure
            max_size: Taille maximale approximative de l'explication en caractères
            
        Returns:
            Dict[str, Any]: Explication des derniers événements
        """
        # Vérifier si le cache est valide
        if "last_events" in self._summary_cache and time.time() - self._cache_timestamp < self._cache_lifetime:
            cached = self._summary_cache["last_events"]
            if len(json.dumps(cached)) <= max_size and len(cached["events"]) <= max_events:
                return cached
        
        result = {
            "timestamp": time.time(),
            "events": []
        }
        char_count = 20
        
        # Récupérer les événements récents
        events = self.global_memory.get_events(min_importance=4, limit=max_events*2)
        
        for event in events:
            if len(result["events"]) < max_events and char_count < max_size:
                # Enrichir l'événement avec des détails sur les entités impliquées
                involved_details = []
                
                if event.get('involved_entities'):
                    for entity_id in event['involved_entities']:
                        local_memory = self.get_local_memory(entity_id)
                        if local_memory:
                            involved_details.append(local_memory.entity_name)
                
                event_entry = {
                    "description": event['description'],
                    "importance": event['importance'],
                    "type": event['event_type']
                }
                
                if involved_details:
                    event_entry["involved"] = involved_details
                
                event_json = json.dumps(event_entry)
                if char_count + len(event_json) < max_size:
                    result["events"].append(event_entry)
                    char_count += len(event_json)
                else:
                    break
            else:
                break
        
        # Mettre en cache
        self._summary_cache["last_events"] = result
        self._cache_timestamp = time.time()
        
        return result
    
    def get_narrative_context(self, max_size: int = 3000) -> Dict[str, Any]:
        """
        Génère un contexte narratif complet mais compact pour le MJ IA.
        
        Args:
            max_size: Taille maximale approximative du contexte en caractères
            
        Returns:
            Dict[str, Any]: Contexte narratif formaté
        """
        # Vérifier si le cache est valide
        if "narrative_context" in self._summary_cache and time.time() - self._cache_timestamp < self._cache_lifetime:
            cached = self._summary_cache["narrative_context"]
            if len(json.dumps(cached)) <= max_size:
                return cached
        
        # Récupérer des composants du contexte narratif
        world_summary = self.get_world_summary(max_size=max_size//3)
        char_count = len(json.dumps(world_summary))
        
        result = {
            "world_state": world_summary,
            "narrative_elements": {
                "recent_decisions": [],
                "themes": [],
                "tensions": []
            },
            "social_dynamics": {}
        }
        
        # Décisions narratives récentes
        if char_count < max_size:
            decisions = self.global_memory.get_narrative_decisions(min_impact=5, limit=3)
            
            for decision in decisions:
                decision_entry = {
                    "description": decision['description'],
                    "rationale": decision['rationale']
                }
                
                decision_json = json.dumps(decision_entry)
                if char_count + len(decision_json) < max_size:
                    result["narrative_elements"]["recent_decisions"].append(decision_entry)
                    char_count += len(decision_json)
                else:
                    break
        
        # Groupes sociaux
        if char_count < max_size:
            social_groups = self.social_memory.get_social_groups(affinity_threshold=30)
            
            group_entries = []
            for group in social_groups[:3]:  # Limiter à 3 groupes maximum
                group_members = []
                
                for entity_id in group:
                    local_memory = self.get_local_memory(entity_id)
                    if local_memory:
                        group_members.append(local_memory.entity_name)
                
                if group_members:
                    group_entry = {
                        "members": group_members
                    }
                    
                    group_json = json.dumps(group_entry)
                    if char_count + len(group_json) < max_size:
                        group_entries.append(group_entry)
                        char_count += len(group_json)
                    else:
                        break
            
            result["social_dynamics"]["groups"] = group_entries
        
        # Mettre en cache
        self._summary_cache["narrative_context"] = result
        self._cache_timestamp = time.time()
        
        return result
    
    def generate_prompt_context(self, 
                               context_type: str = "narrative", 
                               entity_id: Optional[str] = None,
                               max_tokens: int = 1000) -> str:
        """
        Génère un contexte formaté en texte pour un prompt de LLM.
        
        Args:
            context_type: Type de contexte ("narrative", "entity", "summary")
            entity_id: ID de l'entité (pour contexte "entity")
            max_tokens: Estimation du nombre maximum de tokens
            
        Returns:
            str: Contexte formaté en texte
        """
        # Estimation approximative: 1 token ≈ 4 caractères
        max_size = max_tokens * 4
        
        if context_type == "narrative":
            context_data = self.get_narrative_context(max_size=max_size)
            return self._format_narrative_context(context_data)
        
        elif context_type == "entity" and entity_id:
            context_data = self.get_entity_context(entity_id, max_size=max_size)
            return self._format_entity_context(context_data)
        
        elif context_type == "summary":
            context_data = self.get_world_summary(max_size=max_size)
            return self._format_world_summary(context_data)
        
        else:
            return "Type de contexte non valide."
    
    def _format_narrative_context(self, context_data: Dict[str, Any]) -> str:
        """Formate le contexte narratif en texte"""
        text = f"# Monde: {context_data['world_state']['world']['name']}\n\n"
        
        # Faits globaux
        if context_data['world_state'].get('global_facts'):
            text += "## Faits établis\n"
            for category, facts in context_data['world_state']['global_facts'].items():
                text += f"### {category}\n"
                for fact in facts:
                    text += f"- {fact}\n"
            text += "\n"
        
        # Événements récents
        if context_data['world_state'].get('recent_events'):
            text += "## Événements récents\n"
            for event in context_data['world_state']['recent_events']:
                text += f"- {event['description']}\n"
            text += "\n"
        
        # Quêtes actives
        if context_data['world_state'].get('active_quests'):
            text += "## Quêtes actives\n"
            for quest in context_data['world_state']['active_quests']:
                text += f"- {quest['title']}: {quest['description']}\n"
            text += "\n"
        
        # Décisions narratives
        if context_data['narrative_elements'].get('recent_decisions'):
            text += "## Décisions narratives récentes\n"
            for decision in context_data['narrative_elements']['recent_decisions']:
                text += f"- {decision['description']}\n"
                if decision.get('rationale'):
                    text += f"  Raison: {decision['rationale']}\n"
            text += "\n"
        
        # Groupes sociaux
        if context_data['social_dynamics'].get('groups'):
            text += "## Groupes sociaux\n"
            for i, group in enumerate(context_data['social_dynamics']['groups'], 1):
                text += f"### Groupe {i}\n"
                text += "Membres: " + ", ".join(group['members']) + "\n\n"
        
        return text
    
    def _format_entity_context(self, context_data: Dict[str, Any]) -> str:
        """Formate le contexte d'entité en texte"""
        if context_data.get('error'):
            return f"Erreur: {context_data['error']}"
        
        entity = context_data['entity']
        text = f"# {entity['name']}\n"
        text += f"Type: {entity['type']}\n\n"
        
        # Souvenirs
        if context_data.get('memories'):
            text += "## Souvenirs\n"
            for memory in context_data['memories']:
                text += f"- {memory['description']}\n"
            text += "\n"
        
        # Connaissances
        if context_data.get('knowledge'):
            text += "## Connaissances\n"
            for category, items in context_data['knowledge'].items():
                text += f"### {category}\n"
                for key, value in items.items():
                    text += f"- {value}\n"
            text += "\n"
        
        # Relations
        if context_data.get('relationships'):
            text += "## Relations\n"
            for relation in context_data['relationships']:
                affect = "positive" if relation['affinity'] > 20 else ("négative" if relation['affinity'] < -20 else "neutre")
                text += f"- {relation['entity']}: relation {affect} ({relation['affinity']})\n"
            text += "\n"
        
        # Contexte global
        if context_data.get('global_context'):
            text += "## Événements globaux pertinents\n"
            for event in context_data['global_context']:
                text += f"- {event['description']}\n"
            text += "\n"
        
        return text
    
    def _format_world_summary(self, context_data: Dict[str, Any]) -> str:
        """Formate le résumé du monde en texte"""
        text = f"# Résumé du monde: {context_data['world']['name']}\n\n"
        
        # Faits globaux
        if context_data.get('global_facts'):
            text += "## Faits établis\n"
            for category, facts in context_data['global_facts'].items():
                text += f"### {category}\n"
                for fact in facts:
                    text += f"- {fact}\n"
            text += "\n"
        
        # Événements récents
        if context_data.get('recent_events'):
            text += "## Événements récents\n"
            for event in context_data['recent_events']:
                text += f"- {event['description']}\n"
            text += "\n"
        
        # Quêtes actives
        if context_data.get('active_quests'):
            text += "## Quêtes actives\n"
            for quest in context_data['active_quests']:
                text += f"- {quest['title']}: {quest['description']}\n"
            text += "\n"
        
        # Entités clés
        if context_data.get('key_entities'):
            text += "## Personnages clés\n"
            for name, info in context_data['key_entities'].items():
                text += f"- {name} ({info['type']})\n"
            text += "\n"
        
        return text
    
    def _invalidate_cache(self) -> None:
        """Invalide le cache de résumés"""
        self._summary_cache = {}
    
    # ====== MÉTHODES DE PERSISTANCE ======
    
    def save_all(self, base_dir: str = "saves") -> bool:
        """
        Sauvegarde tous les systèmes de mémoire.
        
        Args:
            base_dir: Répertoire de base pour la sauvegarde
            
        Returns:
            bool: True si la sauvegarde a réussi
        """
        try:
            # Créer les répertoires
            save_dir = os.path.join(base_dir, self.world_id)
            os.makedirs(save_dir, exist_ok=True)
            os.makedirs(os.path.join(save_dir, "local"), exist_ok=True)
            
            # Sauvegarder la mémoire globale
            global_path = os.path.join(save_dir, "global_memory.json")
            self.global_memory.save_to_file(global_path)
            
            # Sauvegarder la mémoire sociale
            social_path = os.path.join(save_dir, "social_memory.json")
            with open(social_path, 'w', encoding='utf-8') as f:
                json.dump(self.social_memory.to_dict(), f, ensure_ascii=False, indent=2)
            
            # Sauvegarder les mémoires locales
            for entity_id, local_memory in self.local_memories.items():
                local_path = os.path.join(save_dir, "local", f"{entity_id}.json")
                local_memory.save_to_file(local_path)
            
            return True
        except Exception as e:
            print(f"Erreur lors de la sauvegarde des mémoires: {e}")
            return False
    
    @classmethod
    def load_all(cls, world_id: str, world_name: str, base_dir: str = "saves") -> Optional['MemoryManager']:
        """
        Charge tous les systèmes de mémoire.
        
        Args:
            world_id: ID du monde
            world_name: Nom du monde
            base_dir: Répertoire de base pour le chargement
            
        Returns:
            Optional[MemoryManager]: MemoryManager ou None si erreur
        """
        try:
            # Vérifier si le répertoire existe
            save_dir = os.path.join(base_dir, world_id)
            if not os.path.exists(save_dir):
                return None
            
            # Créer un nouveau MemoryManager
            manager = cls(world_id, world_name)
            
            # Charger la mémoire globale
            global_path = os.path.join(save_dir, "global_memory.json")
            if os.path.exists(global_path):
                manager.global_memory = GlobalMemory.load_from_file(global_path)
            
            # Charger la mémoire sociale
            social_path = os.path.join(save_dir, "social_memory.json")
            if os.path.exists(social_path):
                with open(social_path, 'r', encoding='utf-8') as f:
                    social_data = json.load(f)
                    manager.social_memory = SocialMemory.from_dict(social_data)
            
            # Charger les mémoires locales
            local_dir = os.path.join(save_dir, "local")
            if os.path.exists(local_dir):
                for file_name in os.listdir(local_dir):
                    if file_name.endswith(".json"):
                        local_path = os.path.join(local_dir, file_name)
                        entity_id = os.path.splitext(file_name)[0]
                        local_memory = LocalMemory.load_from_file(local_path)
                        if local_memory:
                            manager.local_memories[entity_id] = local_memory
            
            return manager
        except Exception as e:
            print(f"Erreur lors du chargement des mémoires: {e}")
            return None