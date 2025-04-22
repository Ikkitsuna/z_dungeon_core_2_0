#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LocalMemory - Système de mémoire locale pour chaque entité
"""

import time
import json
import os
from typing import Dict, List, Any, Optional, Tuple, Union

class LocalMemory:
    """
    Gère la mémoire locale d'une entité (PNJ, lieu, objet).
    Stocke les souvenirs, interactions et connaissances propres à cette entité.
    """
    
    def __init__(self, entity_id: str, entity_type: str, entity_name: str, max_memory_size: int = 100):
        """
        Initialise une nouvelle mémoire locale.
        
        Args:
            entity_id: ID unique de l'entité
            entity_type: Type d'entité (npc, location, item, player)
            entity_name: Nom de l'entité
            max_memory_size: Nombre maximum de souvenirs à stocker
        """
        self.entity_id = entity_id
        self.entity_type = entity_type
        self.entity_name = entity_name
        self.max_memory_size = max_memory_size
        
        # Stockage des souvenirs
        self.memories = []
        
        # Connaissances spécifiques à l'entité
        self.knowledge = {}
        
        # Cache des entités connues
        self.known_entities = {
            'npcs': {},      # ID -> niveau de familiarité (0-10)
            'locations': {}, # ID -> niveau de familiarité (0-10)
            'items': {}      # ID -> niveau de familiarité (0-10)
        }
        
        # Dernière mise à jour
        self.last_updated = time.time()
    
    def add_memory(self, 
                  description: str, 
                  importance: int = 5,
                  memory_type: str = "event",
                  location_id: Optional[str] = None,
                  involved_entities: Optional[Dict[str, str]] = None,
                  timestamp: Optional[float] = None,
                  tags: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Ajoute un nouveau souvenir à la mémoire locale.
        
        Args:
            description: Description détaillée du souvenir
            importance: Importance du souvenir (1-10)
            memory_type: Type de souvenir (event, interaction, observation)
            location_id: ID du lieu où le souvenir s'est formé
            involved_entities: Dict des entités impliquées {id: rôle_dans_le_souvenir}
            timestamp: Horodatage du souvenir (utilise l'heure actuelle si non fourni)
            tags: Liste de tags pour catégoriser le souvenir
            
        Returns:
            Dict[str, Any]: Le souvenir créé
        """
        memory = {
            'id': self._generate_memory_id(),
            'description': description,
            'importance': min(10, max(1, importance)),  # Limiter entre 1 et 10
            'memory_type': memory_type,
            'location_id': location_id,
            'involved_entities': involved_entities or {},
            'timestamp': timestamp or time.time(),
            'created_at': time.time(),
            'tags': tags or [],
            'decay_rate': 0.1,  # Taux de dégradation du souvenir (peut être ajusté)
            'recall_count': 0    # Nombre de fois que le souvenir a été rappelé
        }
        
        # Ajouter à la mémoire
        self.memories.append(memory)
        
        # Trier par importance et chronologie (les plus récents et importants en premier)
        self.memories.sort(key=lambda x: (x['importance'], x['timestamp']), reverse=True)
        
        # Limiter la taille de la mémoire
        if len(self.memories) > self.max_memory_size:
            # Trier par importance ajustée par dégradation et rappels
            adjusted_memories = self._get_adjusted_memories()
            # Conserver seulement les max_memory_size souvenirs les plus importants
            self.memories = adjusted_memories[:self.max_memory_size]
        
        # Mettre à jour le timestamp de dernière mise à jour
        self.last_updated = time.time()
        
        # Si des entités sont impliquées, mettre à jour les connaissances
        if involved_entities:
            for entity_id, role in involved_entities.items():
                if ':' in entity_id:  # Format attendu: "type:id"
                    entity_type, clean_id = entity_id.split(':', 1)
                    self.update_entity_familiarity(clean_id, entity_type)
        
        return memory
    
    def recall_memory(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """
        Rappelle un souvenir spécifique et incrémente son compteur de rappels.
        
        Args:
            memory_id: ID du souvenir à rappeler
            
        Returns:
            Optional[Dict[str, Any]]: Le souvenir rappelé ou None s'il n'existe pas
        """
        for memory in self.memories:
            if memory['id'] == memory_id:
                # Incrémenter le compteur de rappels
                memory['recall_count'] += 1
                # Mettre à jour l'horodatage de dernière mise à jour
                self.last_updated = time.time()
                return memory
        return None
    
    def get_memories(self, 
                    memory_type: Optional[str] = None,
                    min_importance: int = 0,
                    location_id: Optional[str] = None,
                    entity_id: Optional[str] = None,
                    tags: Optional[List[str]] = None,
                    time_range: Optional[Tuple[float, float]] = None,
                    limit: int = 10,
                    adjust_for_decay: bool = True) -> List[Dict[str, Any]]:
        """
        Récupère des souvenirs filtrés par type, importance, lieu, etc.
        
        Args:
            memory_type: Filtrer par type de souvenir
            min_importance: Importance minimale requise
            location_id: Filtrer par lieu
            entity_id: Filtrer par entité impliquée
            tags: Filtrer par tags
            time_range: Tuple (début, fin) pour filtrer par période
            limit: Nombre maximum de souvenirs à retourner
            adjust_for_decay: Considérer la dégradation des souvenirs dans le tri
            
        Returns:
            List[Dict[str, Any]]: Liste des souvenirs correspondants
        """
        # Obtenir les souvenirs avec importance ajustée si nécessaire
        if adjust_for_decay:
            filtered_memories = self._get_adjusted_memories()
        else:
            filtered_memories = self.memories.copy()
        
        # Filtrer par type
        if memory_type:
            filtered_memories = [m for m in filtered_memories if m['memory_type'] == memory_type]
        
        # Filtrer par importance minimale
        if adjust_for_decay:
            # Si on ajuste pour la dégradation, on utilise l'importance ajustée
            filtered_memories = [m for m in filtered_memories if m['adjusted_importance'] >= min_importance]
        else:
            filtered_memories = [m for m in filtered_memories if m['importance'] >= min_importance]
        
        # Filtrer par lieu
        if location_id:
            filtered_memories = [m for m in filtered_memories if m['location_id'] == location_id]
        
        # Filtrer par entité impliquée
        if entity_id:
            filtered_memories = [m for m in filtered_memories if entity_id in m.get('involved_entities', {})]
        
        # Filtrer par tags
        if tags:
            filtered_memories = [m for m in filtered_memories if all(tag in m.get('tags', []) for tag in tags)]
        
        # Filtrer par période
        if time_range:
            start, end = time_range
            filtered_memories = [m for m in filtered_memories if start <= m['timestamp'] <= end]
        
        # Limiter le nombre de résultats
        return filtered_memories[:limit]
    
    def search_memories(self, 
                       query: str, 
                       min_importance: int = 0,
                       adjust_for_decay: bool = True,
                       limit: int = 10) -> List[Dict[str, Any]]:
        """
        Recherche des souvenirs contenant certains mots-clés.
        Cette fonction est simplifiée et pourrait être améliorée avec un vrai moteur de recherche.
        
        Args:
            query: Termes de recherche
            min_importance: Importance minimale requise
            adjust_for_decay: Ajuster l'importance en fonction de la dégradation
            limit: Nombre maximum de souvenirs à retourner
            
        Returns:
            List[Dict[str, Any]]: Liste des souvenirs correspondants
        """
        # Obtenir les souvenirs avec importance ajustée si nécessaire
        if adjust_for_decay:
            memories = self._get_adjusted_memories()
        else:
            memories = self.memories.copy()
        
        # Convertir la requête en mots-clés
        keywords = query.lower().split()
        
        # Filtrer les souvenirs contenant au moins un des mots-clés
        matches = []
        for memory in memories:
            description = memory['description'].lower()
            tags = [tag.lower() for tag in memory.get('tags', [])]
            
            # Vérifier si l'un des mots-clés est présent dans la description ou les tags
            if any(keyword in description for keyword in keywords) or any(keyword in tags for keyword in keywords):
                if adjust_for_decay:
                    if memory['adjusted_importance'] >= min_importance:
                        matches.append(memory)
                else:
                    if memory['importance'] >= min_importance:
                        matches.append(memory)
        
        # Trier par pertinence (nombre de mots-clés trouvés) puis par importance
        matches.sort(key=lambda m: (
            sum(1 for keyword in keywords if keyword in m['description'].lower()),
            m['adjusted_importance'] if adjust_for_decay else m['importance']
        ), reverse=True)
        
        return matches[:limit]
    
    def add_knowledge(self, category: str, key: str, value: Any, importance: int = 5) -> None:
        """
        Ajoute une connaissance spécifique à la mémoire de l'entité.
        
        Args:
            category: Catégorie de la connaissance (géographie, histoire, personnes, etc.)
            key: Clé de la connaissance
            value: Valeur de la connaissance
            importance: Importance de cette connaissance (1-10)
        """
        if category not in self.knowledge:
            self.knowledge[category] = {}
        
        self.knowledge[category][key] = {
            'value': value,
            'importance': importance,
            'learned_at': time.time(),
            'last_accessed': time.time()
        }
        
        # Mettre à jour le timestamp de dernière mise à jour
        self.last_updated = time.time()
    
    def get_knowledge(self, 
                     category: Optional[str] = None, 
                     key: Optional[str] = None, 
                     min_importance: int = 0) -> Any:
        """
        Récupère des connaissances spécifiques.
        
        Args:
            category: Catégorie de connaissance (ou None pour toutes)
            key: Clé spécifique (ou None pour toutes les clés de la catégorie)
            min_importance: Importance minimale requise
            
        Returns:
            Any: Connaissance demandée, dictionnaire de connaissances, ou None
        """
        # Mettre à jour l'accès
        current_time = time.time()
        
        # Cas 1: Catégorie et clé spécifiques
        if category and key:
            if category in self.knowledge and key in self.knowledge[category]:
                knowledge = self.knowledge[category][key]
                if knowledge['importance'] >= min_importance:
                    # Mettre à jour le timestamp d'accès
                    self.knowledge[category][key]['last_accessed'] = current_time
                    return knowledge['value']
            return None
        
        # Cas 2: Catégorie spécifique, toutes les clés
        elif category:
            if category not in self.knowledge:
                return {}
            
            result = {}
            for k, v in self.knowledge[category].items():
                if v['importance'] >= min_importance:
                    # Mettre à jour le timestamp d'accès
                    self.knowledge[category][k]['last_accessed'] = current_time
                    result[k] = v['value']
            return result
        
        # Cas 3: Toutes les catégories et clés
        else:
            result = {}
            for cat in self.knowledge:
                cat_result = {}
                for k, v in self.knowledge[cat].items():
                    if v['importance'] >= min_importance:
                        # Mettre à jour le timestamp d'accès
                        self.knowledge[cat][k]['last_accessed'] = current_time
                        cat_result[k] = v['value']
                if cat_result:
                    result[cat] = cat_result
            return result
    
    def update_entity_familiarity(self, entity_id: str, entity_type: str, familiarity_change: int = 1) -> int:
        """
        Met à jour le niveau de familiarité avec une entité.
        
        Args:
            entity_id: ID de l'entité
            entity_type: Type d'entité (npc, location, item)
            familiarity_change: Modification du niveau de familiarité (+/-)
            
        Returns:
            int: Nouveau niveau de familiarité
        """
        if entity_type not in self.known_entities:
            return 0
        
        # Initialiser à 0 si l'entité n'est pas déjà connue
        if entity_id not in self.known_entities[entity_type]:
            self.known_entities[entity_type][entity_id] = 0
        
        # Mettre à jour la familiarité (entre 0 et 10)
        current = self.known_entities[entity_type][entity_id]
        self.known_entities[entity_type][entity_id] = max(0, min(10, current + familiarity_change))
        
        # Mettre à jour le timestamp de dernière mise à jour
        self.last_updated = time.time()
        
        return self.known_entities[entity_type][entity_id]
    
    def get_entity_familiarity(self, entity_id: str, entity_type: str) -> int:
        """
        Récupère le niveau de familiarité avec une entité.
        
        Args:
            entity_id: ID de l'entité
            entity_type: Type d'entité (npc, location, item)
            
        Returns:
            int: Niveau de familiarité (0-10) ou 0 si inconnue
        """
        if entity_type not in self.known_entities or entity_id not in self.known_entities[entity_type]:
            return 0
        
        return self.known_entities[entity_type][entity_id]
    
    def get_known_entities(self, 
                          entity_type: Optional[str] = None, 
                          min_familiarity: int = 0) -> Dict[str, Dict[str, int]]:
        """
        Récupère les entités connues filtrées par type et niveau de familiarité.
        
        Args:
            entity_type: Type d'entité à récupérer (ou None pour tous)
            min_familiarity: Niveau de familiarité minimum requis
            
        Returns:
            Dict[str, Dict[str, int]]: Entités connues groupées par type
        """
        result = {}
        
        # Filtrer par type si spécifié
        entity_types = [entity_type] if entity_type else list(self.known_entities.keys())
        
        for etype in entity_types:
            if etype in self.known_entities:
                # Filtrer par niveau de familiarité
                entities = {eid: level for eid, level in self.known_entities[etype].items() if level >= min_familiarity}
                if entities:
                    result[etype] = entities
        
        return result
    
    def forget_old_memories(self, threshold_days: int = 30, min_importance: int = 8, max_to_forget: int = 10) -> int:
        """
        Oublie les souvenirs les plus anciens et les moins importants.
        
        Args:
            threshold_days: Âge minimum (en jours) pour considérer un souvenir comme ancien
            min_importance: Importance minimale pour protéger un souvenir
            max_to_forget: Nombre maximum de souvenirs à oublier
            
        Returns:
            int: Nombre de souvenirs oubliés
        """
        current_time = time.time()
        threshold_time = current_time - (threshold_days * 24 * 60 * 60)
        
        # Identifier les souvenirs candidats à l'oubli
        candidates = [
            (i, m) for i, m in enumerate(self.memories) 
            if m['timestamp'] < threshold_time and m['importance'] < min_importance
        ]
        
        # Trier par importance ajustée (les moins importants d'abord)
        candidates.sort(key=lambda x: self._calculate_adjusted_importance(x[1]))
        
        # Limiter le nombre de souvenirs à oublier
        to_forget = candidates[:max_to_forget]
        
        # Supprimer les souvenirs (en commençant par les indices les plus élevés)
        for i, _ in sorted(to_forget, key=lambda x: x[0], reverse=True):
            del self.memories[i]
        
        # Mettre à jour le timestamp de dernière mise à jour
        if to_forget:
            self.last_updated = time.time()
        
        return len(to_forget)
    
    def save_to_file(self, file_path: str) -> bool:
        """
        Sauvegarde la mémoire locale dans un fichier JSON.
        
        Args:
            file_path: Chemin du fichier où sauvegarder
            
        Returns:
            bool: True si la sauvegarde a réussi, False sinon
        """
        try:
            # Préparer les données sérialisables
            data = self.to_dict()
            
            # Créer le répertoire si nécessaire
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Écrire dans le fichier
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"Erreur lors de la sauvegarde de la mémoire locale: {e}")
            return False
    
    @classmethod
    def load_from_file(cls, file_path: str) -> Optional['LocalMemory']:
        """
        Charge la mémoire locale depuis un fichier JSON.
        
        Args:
            file_path: Chemin du fichier à charger
            
        Returns:
            Optional[LocalMemory]: Instance de mémoire locale chargée, ou None si erreur
        """
        try:
            # Lire le fichier
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Créer l'instance à partir des données
            return cls.from_dict(data)
        except Exception as e:
            print(f"Erreur lors du chargement de la mémoire locale: {e}")
            return None
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convertit la mémoire locale en dictionnaire sérialisable.
        
        Returns:
            Dict[str, Any]: Représentation dictionnaire de la mémoire
        """
        return {
            'entity_id': self.entity_id,
            'entity_type': self.entity_type,
            'entity_name': self.entity_name,
            'max_memory_size': self.max_memory_size,
            'memories': self.memories.copy(),
            'knowledge': self.knowledge.copy(),
            'known_entities': self.known_entities.copy(),
            'last_updated': self.last_updated
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LocalMemory':
        """
        Crée une mémoire locale à partir d'un dictionnaire sérialisé.
        
        Args:
            data: Dictionnaire contenant les données de la mémoire
            
        Returns:
            LocalMemory: Instance de mémoire locale créée
        """
        memory = cls(
            entity_id=data['entity_id'],
            entity_type=data['entity_type'],
            entity_name=data['entity_name'],
            max_memory_size=data.get('max_memory_size', 100)
        )
        
        memory.memories = data.get('memories', []).copy()
        memory.knowledge = data.get('knowledge', {}).copy()
        memory.known_entities = data.get('known_entities', {'npcs': {}, 'locations': {}, 'items': {}}).copy()
        memory.last_updated = data.get('last_updated', time.time())
        
        return memory
    
    def _generate_memory_id(self) -> str:
        """
        Génère un ID unique pour un souvenir.
        
        Returns:
            str: ID unique
        """
        import uuid
        return f"mem_{uuid.uuid4().hex[:8]}"
    
    def _calculate_adjusted_importance(self, memory: Dict[str, Any]) -> float:
        """
        Calcule l'importance ajustée d'un souvenir en tenant compte de l'âge et des rappels.
        
        Args:
            memory: Souvenir à évaluer
            
        Returns:
            float: Importance ajustée
        """
        current_time = time.time()
        memory_age = (current_time - memory['timestamp']) / (60 * 60 * 24)  # Âge en jours
        
        # Facteur de dégradation basé sur l'âge (décroissance exponentielle)
        decay_factor = memory['decay_rate'] * memory_age
        
        # Facteur de renforcement basé sur les rappels
        recall_boost = min(2.0, 0.2 * memory['recall_count'])
        
        # Calculer l'importance ajustée (min 0.5, max importance d'origine)
        adjusted = memory['importance'] * max(0.1, 1.0 - decay_factor + recall_boost)
        return max(0.5, min(memory['importance'], adjusted))
    
    def _get_adjusted_memories(self) -> List[Dict[str, Any]]:
        """
        Obtient tous les souvenirs avec leur importance ajustée calculée.
        
        Returns:
            List[Dict[str, Any]]: Liste des souvenirs avec importance ajustée
        """
        # Copier les souvenirs
        memories = self.memories.copy()
        
        # Calculer l'importance ajustée pour chaque souvenir
        for memory in memories:
            memory['adjusted_importance'] = self._calculate_adjusted_importance(memory)
        
        # Trier par importance ajustée
        memories.sort(key=lambda x: x['adjusted_importance'], reverse=True)
        
        return memories

    # ====== MÉTHODES POUR LES LLMs LÉGERS ======
    
    def get_summary(self, max_size: int = 800, include_recent: bool = True, include_important: bool = True) -> Dict[str, Any]:
        """
        Génère un résumé compact de la mémoire de l'entité, optimisé pour les LLMs légers.
        
        Args:
            max_size: Taille maximale approximative du résumé en caractères
            include_recent: Inclure les souvenirs récents
            include_important: Inclure les souvenirs importants
            
        Returns:
            Dict[str, Any]: Résumé de la mémoire locale
        """
        result = {
            "entity": {
                "id": self.entity_id,
                "type": self.entity_type,
                "name": self.entity_name
            },
            "memories": [],
            "knowledge_categories": list(self.knowledge.keys()),
            "relationships": []
        }
        char_count = len(json.dumps(result["entity"])) + 50
        
        # Souvenirs importants
        if include_important:
            important_memories = self.get_memories(min_importance=7, limit=5)
            
            for memory in important_memories:
                if char_count < max_size:
                    memory_entry = {
                        "description": memory['description'],
                        "importance": memory['importance'],
                        "type": memory['memory_type']
                    }
                    
                    memory_json = json.dumps(memory_entry)
                    if char_count + len(memory_json) < max_size:
                        result["memories"].append(memory_entry)
                        char_count += len(memory_json)
                    else:
                        break
                else:
                    break
        
        # Souvenirs récents
        if include_recent:
            recent_memories = self.get_memories(limit=3)
            memory_ids = {m.get('id') for m in result["memories"]}
            
            for memory in recent_memories:
                if memory.get('id') not in memory_ids and char_count < max_size:
                    memory_entry = {
                        "description": memory['description'],
                        "importance": memory['importance'],
                        "type": memory['memory_type']
                    }
                    
                    memory_json = json.dumps(memory_entry)
                    if char_count + len(memory_json) < max_size:
                        result["memories"].append(memory_entry)
                        char_count += len(memory_json)
                    else:
                        break
                else:
                    continue
        
        # Relations importantes
        for entity_type, entities in self.known_entities.items():
            for entity_id, familiarity in entities.items():
                if familiarity >= 5 and char_count < max_size:  # Seulement les relations significatives
                    relation = {
                        "entity_id": entity_id,
                        "entity_type": entity_type,
                        "familiarity": familiarity
                    }
                    
                    relation_json = json.dumps(relation)
                    if char_count + len(relation_json) < max_size:
                        result["relationships"].append(relation)
                        char_count += len(relation_json)
                    else:
                        break
        
        return result
    
    def generate_response_context(self, max_tokens: int = 500) -> str:
        """
        Génère un contexte textuel formaté pour l'entité, optimisé pour alimenter un prompt de LLM léger.
        
        Args:
            max_tokens: Estimation du nombre maximum de tokens (1 token ≈ 4 caractères)
            
        Returns:
            str: Contexte formaté pour l'entité
        """
        # Estimer la taille maximale en caractères
        max_size = max_tokens * 4
        
        # Récupérer le résumé
        summary = self.get_summary(max_size=max_size)
        
        # Formater en texte
        text = f"Tu es {summary['entity']['name']}"
        
        if summary.get('memories'):
            text += "\n\nTes souvenirs marquants :\n"
            for memory in summary['memories']:
                text += f"- {memory['description']}\n"
        
        if summary.get('knowledge_categories'):
            text += "\n\nTu possèdes des connaissances sur : " + ", ".join(summary['knowledge_categories'])
        
        if summary.get('relationships'):
            text += "\n\nTes relations importantes :\n"
            for relation in summary['relationships']:
                level = ""
                if relation['familiarity'] >= 8:
                    level = "très bien"
                elif relation['familiarity'] >= 5:
                    level = "bien"
                else:
                    level = "assez bien"
                
                text += f"- Tu connais {level} une entité de type {relation['entity_type']} (ID: {relation['entity_id']})\n"
        
        return text
    
    def explain_memories(self, query: str, max_results: int = 3) -> List[Dict[str, Any]]:
        """
        Recherche et explique les souvenirs liés à une requête spécifique,
        utile pour donner du contexte ciblé à un LLM.
        
        Args:
            query: Termes de recherche ou sujet
            max_results: Nombre maximum de souvenirs à retourner
            
        Returns:
            List[Dict[str, Any]]: Souvenirs pertinents et explications
        """
        # Rechercher les souvenirs pertinents
        memories = self.search_memories(query, min_importance=2, limit=max_results)
        
        # Structurer les résultats
        results = []
        for memory in memories:
            # Extraire les entités impliquées
            involved_entities = []
            for entity_id, role in memory.get('involved_entities', {}).items():
                involved_entities.append(f"{entity_id} ({role})")
            
            # Construire l'explication
            explanation = {
                "description": memory['description'],
                "when": self._format_relative_time(memory['timestamp']),
                "importance": memory['importance'],
                "type": memory['memory_type']
            }
            
            if involved_entities:
                explanation["involved"] = involved_entities
            
            if memory.get('location_id'):
                explanation["where"] = memory['location_id']
            
            if memory.get('tags'):
                explanation["tags"] = memory['tags']
            
            results.append(explanation)
        
        return results
    
    def _format_relative_time(self, timestamp: float) -> str:
        """
        Formate un timestamp en description relative ("récemment", "il y a longtemps", etc.)
        
        Args:
            timestamp: Horodatage à formater
            
        Returns:
            str: Description relative du temps
        """
        now = time.time()
        delta = now - timestamp
        
        if delta < 60*60:  # Moins d'une heure
            return "très récemment"
        elif delta < 24*60*60:  # Moins d'un jour
            return "aujourd'hui"
        elif delta < 7*24*60*60:  # Moins d'une semaine
            return "cette semaine"
        elif delta < 30*24*60*60:  # Moins d'un mois
            return "ce mois-ci"
        elif delta < 365*24*60*60:  # Moins d'un an
            return "cette année"
        else:
            return "il y a longtemps"