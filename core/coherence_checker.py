#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CoherenceChecker - Vérificateur de cohérence narrative pour Z-Dungeon Core
"""

import logging
from typing import Dict, List, Any, Optional, Tuple

# Configuration du système de logging
logger = logging.getLogger('CoherenceChecker')

class CoherenceChecker:
    """
    Vérificateur de cohérence narrative pour Z-Dungeon Core.
    S'assure que les actions du joueur et les réponses du système
    sont cohérentes avec l'univers du jeu et la continuité narrative.
    """
    
    def __init__(self):
        """
        Initialise le vérificateur de cohérence.
        """
        # Règles de cohérence pour différents types d'actions
        self.rules = {
            "movement": [
                "Le joueur ne peut se déplacer que vers des lieux connectés à sa position actuelle.",
                "Le joueur ne peut pas entrer dans un lieu verrouillé sans la clé appropriée.",
                "Le joueur ne peut pas traverser un obstacle sans le surmonter d'abord."
            ],
            "interaction": [
                "Le joueur ne peut interagir qu'avec des objets présents dans le lieu actuel ou dans son inventaire.",
                "Le joueur ne peut interagir qu'avec des PNJ présents dans le lieu actuel.",
                "Les objets ne peuvent être utilisés que selon leur fonction prévue ou de manière créative mais plausible."
            ],
            "inventory": [
                "Le joueur ne peut prendre que des objets présents dans le lieu actuel.",
                "Le joueur ne peut pas prendre des objets trop lourds ou fixés.",
                "Le joueur ne peut pas donner un objet qu'il ne possède pas."
            ],
            "dialogue": [
                "Les PNJ répondent selon leur personnalité et leurs connaissances.",
                "Les PNJ ne peuvent révéler que des informations qu'ils sont censés connaître.",
                "Les réactions des PNJ sont cohérentes avec leurs relations avec le joueur."
            ],
            "world": [
                "Les événements respectent les lois physiques et magiques établies dans le monde.",
                "Les descriptions des lieux restent cohérentes au fil du temps, sauf changement explicite.",
                "Le temps s'écoule de manière cohérente, sans sauts inexpliqués."
            ]
        }
    
    def check_action(self, action_text: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Vérifie si une action du joueur est cohérente avec le contexte actuel.
        
        Args:
            action_text: Texte de l'action du joueur
            context: Contexte actuel du jeu
            
        Returns:
            Dict[str, Any]: Résultat de la vérification avec les clés:
                - is_coherent: booléen indiquant si l'action est cohérente
                - reason: raison de l'incohérence (si applicable)
                - action_type: type d'action détecté
                - modified_action: action modifiée pour être cohérente (si applicable)
        """
        # Déterminer le type d'action
        action_type = self._determine_action_type(action_text)
        
        # Effectuer les vérifications spécifiques au type d'action
        if action_type == "movement":
            return self._check_movement_action(action_text, context)
        elif action_type == "interaction":
            return self._check_interaction_action(action_text, context)
        elif action_type == "inventory":
            return self._check_inventory_action(action_text, context)
        elif action_type == "dialogue":
            return self._check_dialogue_action(action_text, context)
        else:
            # Pour les actions non catégorisées, effectuer une vérification générale
            return self._check_general_action(action_text, context)
    
    def _determine_action_type(self, action_text: str) -> str:
        """
        Détermine le type d'action basé sur le texte de l'action.
        
        Args:
            action_text: Texte de l'action du joueur
            
        Returns:
            str: Type d'action détecté
        """
        action_lower = action_text.lower()
        
        # Mots-clés pour les actions de mouvement
        movement_keywords = ["aller", "se déplacer", "entrer", "sortir", "monter", "descendre", 
                            "marcher", "courir", "sauter", "grimper", "ramper"]
        
        # Mots-clés pour les actions d'interaction
        interaction_keywords = ["utiliser", "activer", "pousser", "tirer", "ouvrir", "fermer", 
                              "examiner", "regarder", "toucher", "frapper", "casser"]
        
        # Mots-clés pour les actions d'inventaire
        inventory_keywords = ["prendre", "ramasser", "lâcher", "déposer", "donner", "équiper", 
                            "déséquiper", "mettre", "enlever", "porter", "inventaire"]
        
        # Mots-clés pour les actions de dialogue
        dialogue_keywords = ["parler", "discuter", "questionner", "demander", "répondre", 
                           "saluer", "remercier", "insulter", "convaincre", "mentir"]
        
        # Vérifier les mots-clés pour déterminer le type d'action
        for keyword in movement_keywords:
            if keyword in action_lower:
                return "movement"
        
        for keyword in interaction_keywords:
            if keyword in action_lower:
                return "interaction"
        
        for keyword in inventory_keywords:
            if keyword in action_lower:
                return "inventory"
        
        for keyword in dialogue_keywords:
            if keyword in action_lower:
                return "dialogue"
        
        # Si aucun mot-clé spécifique n'est trouvé, considérer comme une action générale
        return "general"
    
    def _check_movement_action(self, action_text: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Vérifie la cohérence d'une action de mouvement.
        
        Args:
            action_text: Texte de l'action du joueur
            context: Contexte actuel du jeu
            
        Returns:
            Dict[str, Any]: Résultat de la vérification
        """
        player = context.get('player')
        location = context.get('location')
        
        if not location:
            return {
                'is_coherent': False,
                'reason': "Impossible de déterminer votre position actuelle.",
                'action_type': "movement",
                'modified_action': None
            }
        
        # Extraire la destination potentielle de l'action
        destination_name = self._extract_destination(action_text)
        
        if not destination_name:
            return {
                'is_coherent': True,  # Pas assez d'information pour déterminer une incohérence
                'action_type': "movement"
            }
        
        # Vérifier si la destination est connectée au lieu actuel
        connected_locations = []
        for loc_id in location.connected_locations:
            connected_loc = None
            # Rechercher le lieu connecté dans le contexte
            for loc in context.get('world_config', {}).get('locations', []):
                if loc.get('id') == loc_id:
                    connected_loc = loc
                    break
            
            if connected_loc:
                connected_locations.append(connected_loc)
        
        # Vérifier si la destination est dans les lieux connectés
        destination_found = False
        for connected_loc in connected_locations:
            if destination_name.lower() in connected_loc.get('name', '').lower():
                destination_found = True
                break
        
        if not destination_found:
            return {
                'is_coherent': False,
                'reason': f"Vous ne pouvez pas aller à '{destination_name}' depuis votre position actuelle.",
                'action_type': "movement",
                'modified_action': None
            }
        
        # Vérifier les obstacles potentiels
        # (porte verrouillée, pont effondré, etc. - à implémenter selon les besoins du jeu)
        
        return {
            'is_coherent': True,
            'action_type': "movement"
        }
    
    def _extract_destination(self, action_text: str) -> Optional[str]:
        """
        Extrait la destination d'une action de mouvement.
        
        Args:
            action_text: Texte de l'action du joueur
            
        Returns:
            Optional[str]: Nom de la destination, ou None si non trouvée
        """
        action_lower = action_text.lower()
        
        # Liste des prépositions et verbes de mouvement à rechercher
        movement_prepositions = [
            "à", "au", "aux", "vers", "en direction de", "dans", "en"
        ]
        
        movement_verbs = [
            "aller", "se déplacer", "entrer", "sortir", "monter", "descendre"
        ]
        
        # Rechercher les motifs "verbe [préposition] destination"
        for verb in movement_verbs:
            if verb in action_lower:
                # Diviser l'action après le verbe
                parts = action_lower.split(verb, 1)[1].strip()
                
                # Rechercher une préposition ou directement la destination
                for prep in movement_prepositions:
                    if parts.startswith(prep + " "):
                        # Retourner tout ce qui suit la préposition
                        return parts[len(prep):].strip()
                
                # Si aucune préposition n'est trouvée, considérer le reste comme la destination
                return parts
        
        # Si aucun motif clair n'est trouvé
        return None
    
    def _check_interaction_action(self, action_text: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Vérifie la cohérence d'une action d'interaction.
        
        Args:
            action_text: Texte de l'action du joueur
            context: Contexte actuel du jeu
            
        Returns:
            Dict[str, Any]: Résultat de la vérification
        """
        action_lower = action_text.lower()
        player = context.get('player')
        location = context.get('location')
        items = context.get('items', [])
        npcs = context.get('npcs', [])
        
        # Extraire l'objet de l'interaction
        interaction_target = self._extract_interaction_target(action_text)
        
        if not interaction_target:
            return {
                'is_coherent': True,  # Pas assez d'information pour déterminer une incohérence
                'action_type': "interaction"
            }
        
        # Vérifier si la cible de l'interaction est présente
        target_found = False
        
        # Vérifier parmi les objets du lieu
        for item in items:
            if interaction_target.lower() in item.get('name', '').lower():
                target_found = True
                break
        
        # Vérifier parmi les PNJ du lieu
        if not target_found:
            for npc in npcs:
                if interaction_target.lower() in npc.get('name', '').lower():
                    target_found = True
                    break
        
        # Vérifier dans l'inventaire du joueur
        if not target_found and player and hasattr(player, 'inventory'):
            for item_id in player.inventory:
                item = None
                # Rechercher l'objet dans le contexte
                for i in context.get('world_config', {}).get('items', []):
                    if i.get('id') == item_id:
                        item = i
                        break
                
                if item and interaction_target.lower() in item.get('name', '').lower():
                    target_found = True
                    break
        
        if not target_found:
            return {
                'is_coherent': False,
                'reason': f"Vous ne voyez pas '{interaction_target}' ici.",
                'action_type': "interaction",
                'modified_action': None
            }
        
        # Vérifications supplémentaires spécifiques au type d'interaction pourraient être ajoutées ici
        
        return {
            'is_coherent': True,
            'action_type': "interaction"
        }
    
    def _extract_interaction_target(self, action_text: str) -> Optional[str]:
        """
        Extrait la cible d'une action d'interaction.
        
        Args:
            action_text: Texte de l'action du joueur
            
        Returns:
            Optional[str]: Nom de la cible, ou None si non trouvée
        """
        action_lower = action_text.lower()
        
        # Liste des verbes d'interaction à rechercher
        interaction_verbs = [
            "utiliser", "activer", "pousser", "tirer", "ouvrir", "fermer", 
            "examiner", "regarder", "toucher", "frapper", "casser"
        ]
        
        # Rechercher les motifs "verbe [préposition] cible"
        for verb in interaction_verbs:
            if verb in action_lower:
                # Diviser l'action après le verbe
                parts = action_lower.split(verb, 1)[1].strip()
                
                # Rechercher une préposition optionnelle
                prepositions = ["le", "la", "les", "un", "une", "des", "avec", "sur", "dans"]
                for prep in prepositions:
                    if parts.startswith(prep + " "):
                        # Retourner tout ce qui suit la préposition
                        return parts[len(prep):].strip()
                
                # Si aucune préposition n'est trouvée, considérer le reste comme la cible
                return parts
        
        # Si aucun motif clair n'est trouvé
        return None
    
    def _check_inventory_action(self, action_text: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Vérifie la cohérence d'une action d'inventaire.
        
        Args:
            action_text: Texte de l'action du joueur
            context: Contexte actuel du jeu
            
        Returns:
            Dict[str, Any]: Résultat de la vérification
        """
        action_lower = action_text.lower()
        player = context.get('player')
        location = context.get('location')
        items = context.get('items', [])
        
        # Détecter si c'est une action de prise ou de dépôt
        is_take_action = any(keyword in action_lower for keyword in ["prendre", "ramasser", "saisir", "récupérer"])
        is_drop_action = any(keyword in action_lower for keyword in ["lâcher", "déposer", "jeter", "donner"])
        
        if is_take_action:
            # Extraire l'objet à prendre
            item_name = self._extract_inventory_item(action_text)
            
            if not item_name:
                return {
                    'is_coherent': True,  # Pas assez d'information pour déterminer une incohérence
                    'action_type': "inventory"
                }
            
            # Vérifier si l'objet est présent dans le lieu
            item_found = False
            for item in items:
                if item_name.lower() in item.get('name', '').lower():
                    item_found = True
                    
                    # Vérifier si l'objet peut être pris
                    if item.get('fixed', False) or item.get('too_heavy', False):
                        return {
                            'is_coherent': False,
                            'reason': f"Vous ne pouvez pas prendre '{item_name}', car {item.get('fixed_reason') or 'il est fixé ou trop lourd'}.",
                            'action_type': "inventory",
                            'modified_action': None
                        }
                    break
            
            if not item_found:
                return {
                    'is_coherent': False,
                    'reason': f"Vous ne voyez pas '{item_name}' ici.",
                    'action_type': "inventory",
                    'modified_action': None
                }
            
        elif is_drop_action:
            # Extraire l'objet à déposer
            item_name = self._extract_inventory_item(action_text)
            
            if not item_name:
                return {
                    'is_coherent': True,  # Pas assez d'information pour déterminer une incohérence
                    'action_type': "inventory"
                }
            
            # Vérifier si l'objet est dans l'inventaire du joueur
            if not player or not hasattr(player, 'inventory') or not player.inventory:
                return {
                    'is_coherent': False,
                    'reason': f"Vous n'avez pas '{item_name}' dans votre inventaire.",
                    'action_type': "inventory",
                    'modified_action': None
                }
            
            item_found = False
            for item_id in player.inventory:
                item = None
                # Rechercher l'objet dans le contexte
                for i in context.get('world_config', {}).get('items', []):
                    if i.get('id') == item_id:
                        item = i
                        break
                
                if item and item_name.lower() in item.get('name', '').lower():
                    item_found = True
                    break
            
            if not item_found:
                return {
                    'is_coherent': False,
                    'reason': f"Vous n'avez pas '{item_name}' dans votre inventaire.",
                    'action_type': "inventory",
                    'modified_action': None
                }
        
        return {
            'is_coherent': True,
            'action_type': "inventory"
        }
    
    def _extract_inventory_item(self, action_text: str) -> Optional[str]:
        """
        Extrait le nom de l'objet d'une action d'inventaire.
        
        Args:
            action_text: Texte de l'action du joueur
            
        Returns:
            Optional[str]: Nom de l'objet, ou None si non trouvé
        """
        action_lower = action_text.lower()
        
        # Liste des verbes d'inventaire à rechercher
        inventory_verbs = [
            "prendre", "ramasser", "lâcher", "déposer", "donner", "équiper", 
            "déséquiper", "mettre", "enlever", "porter"
        ]
        
        # Rechercher les motifs "verbe [préposition] objet"
        for verb in inventory_verbs:
            if verb in action_lower:
                # Diviser l'action après le verbe
                parts = action_lower.split(verb, 1)[1].strip()
                
                # Rechercher une préposition optionnelle
                prepositions = ["le", "la", "les", "un", "une", "des", "ce", "cette", "ces"]
                for prep in prepositions:
                    if parts.startswith(prep + " "):
                        # Retourner tout ce qui suit la préposition
                        return parts[len(prep):].strip()
                
                # Si aucune préposition n'est trouvée, considérer le reste comme l'objet
                return parts
        
        # Si aucun motif clair n'est trouvé
        return None
    
    def _check_dialogue_action(self, action_text: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Vérifie la cohérence d'une action de dialogue.
        
        Args:
            action_text: Texte de l'action du joueur
            context: Contexte actuel du jeu
            
        Returns:
            Dict[str, Any]: Résultat de la vérification
        """
        action_lower = action_text.lower()
        location = context.get('location')
        npcs = context.get('npcs', [])
        
        # Extraire le PNJ avec qui parler
        npc_name = self._extract_dialogue_target(action_text)
        
        if not npc_name:
            return {
                'is_coherent': True,  # Pas assez d'information pour déterminer une incohérence
                'action_type': "dialogue"
            }
        
        # Vérifier si le PNJ est présent dans le lieu
        npc_found = False
        for npc in npcs:
            if npc_name.lower() in npc.get('name', '').lower():
                npc_found = True
                break
        
        if not npc_found:
            return {
                'is_coherent': False,
                'reason': f"Vous ne voyez pas '{npc_name}' ici pour lui parler.",
                'action_type': "dialogue",
                'modified_action': None
            }
        
        return {
            'is_coherent': True,
            'action_type': "dialogue"
        }
    
    def _extract_dialogue_target(self, action_text: str) -> Optional[str]:
        """
        Extrait la cible d'une action de dialogue.
        
        Args:
            action_text: Texte de l'action du joueur
            
        Returns:
            Optional[str]: Nom du PNJ, ou None si non trouvé
        """
        action_lower = action_text.lower()
        
        # Liste des verbes de dialogue à rechercher
        dialogue_verbs = [
            "parler", "discuter", "questionner", "demander", "répondre", 
            "saluer", "remercier", "insulter", "convaincre", "mentir"
        ]
        
        # Liste des prépositions pour le dialogue
        dialogue_prepositions = ["à", "avec", "au", "aux"]
        
        # Rechercher les motifs "verbe préposition cible"
        for verb in dialogue_verbs:
            if verb in action_lower:
                # Diviser l'action après le verbe
                parts = action_lower.split(verb, 1)[1].strip()
                
                # Rechercher une préposition
                for prep in dialogue_prepositions:
                    if parts.startswith(prep + " "):
                        # Retourner tout ce qui suit la préposition
                        return parts[len(prep):].strip()
                
                # Si aucune préposition n'est trouvée, considérer le reste comme la cible
                return parts
        
        # Si aucun motif clair n'est trouvé
        return None
    
    def _check_general_action(self, action_text: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Effectue une vérification générale de cohérence pour les actions non catégorisées.
        
        Args:
            action_text: Texte de l'action du joueur
            context: Contexte actuel du jeu
            
        Returns:
            Dict[str, Any]: Résultat de la vérification
        """
        # Pour les actions générales, nous faisons confiance au traitement narratif
        # mais vérifions quelques règles de base
        
        # Vérifier si l'action est vide ou trop courte
        if not action_text or len(action_text.strip()) < 3:
            return {
                'is_coherent': False,
                'reason': "Veuillez spécifier une action plus détaillée.",
                'action_type': "general",
                'modified_action': None
            }
        
        # Vérifier la longueur maximale pour éviter les abus
        if len(action_text) > 500:
            return {
                'is_coherent': False,
                'reason': "Votre action est trop longue. Veuillez la simplifier.",
                'action_type': "general",
                'modified_action': action_text[:497] + "..."
            }
        
        # Vérifications supplémentaires pourraient être ajoutées ici
        
        return {
            'is_coherent': True,
            'action_type': "general"
        }
    
    def check_narrative_consistency(self, narrative_text: str, history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Vérifie la cohérence d'une réponse narrative avec l'historique du jeu.
        
        Args:
            narrative_text: Texte narratif à vérifier
            history: Historique des actions et réponses précédentes
            
        Returns:
            Dict[str, Any]: Résultat de la vérification
        """
        # Implémentation de base, à enrichir selon les besoins
        
        # Vérifier si la narration est vide
        if not narrative_text:
            return {
                'is_coherent': False,
                'reason': "La réponse narrative est vide.",
                'modified_narrative': "..."
            }
        
        # Vérifier les contradictions évidentes avec l'historique récent
        # Cette logique devrait être enrichie avec des techniques plus avancées
        
        return {
            'is_coherent': True
        }
    
    def suggest_correction(self, action_text: str, incoherence_reason: str) -> str:
        """
        Suggère une correction pour une action incohérente.
        
        Args:
            action_text: Texte de l'action originale
            incoherence_reason: Raison de l'incohérence
            
        Returns:
            str: Suggestion de correction
        """
        # Suggestion simple basée sur la raison de l'incohérence
        if "ne voyez pas" in incoherence_reason:
            return "Regardez autour de vous pour voir ce qui est disponible."
        elif "ne pouvez pas aller" in incoherence_reason:
            return "Essayez d'aller dans une direction ou un lieu accessible."
        elif "n'avez pas" in incoherence_reason and "inventaire" in incoherence_reason:
            return "Vérifiez votre inventaire pour voir ce que vous possédez."
        else:
            return "Essayez une action différente ou plus précise."