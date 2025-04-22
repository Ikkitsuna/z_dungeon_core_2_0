#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NarrativeEngine - Moteur narratif pour générer des réponses textuelles
"""

import os
import json
import logging
import time
from typing import Dict, Any, List, Optional
from concurrent.futures import ThreadPoolExecutor

from .llm_interface import LLMInterface, create_llm

# Configuration du système de logging
logger = logging.getLogger('NarrativeEngine')

class NarrativeEngine:
    """
    Moteur narratif responsable de la génération de texte via un modèle de langage.
    Cette classe abstraite toutes les interactions avec l'IA pour permettre
    une modularité et faciliter les changements de modèle.
    """
    
    def __init__(self, model: str = "llama3", temperature: float = 0.7, max_tokens: int = 500, llm_config: Dict[str, Any] = None):
        """
        Initialise le moteur narratif.
        
        Args:
            model: Le modèle à utiliser (pour compatibilité avec l'ancienne API)
            temperature: Contrôle la créativité (0.0-1.0)
            max_tokens: Nombre maximum de tokens pour la réponse
            llm_config: Configuration complète du LLM (remplace les paramètres individuels si fourni)
        """
        # Configuration LLM par défaut
        self.llm_config = llm_config or {
            "provider": "ollama",
            "model": model,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        # Création de l'instance LLM
        self.llm = create_llm(self.llm_config)
        
        # Cache des templates
        self.template_cache = {}
        
        # Charger les templates narratifs
        self._load_templates()
        
        # Vérifier si le LLM est disponible
        if not self.llm.is_available():
            logger.warning(f"Le modèle {self.llm_config.get('model')} n'est pas disponible. Certaines fonctionnalités narratives seront limitées.")
    
    def _load_templates(self):
        """Charge les templates narratifs depuis les fichiers."""
        template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')
        template_file = os.path.join(template_dir, 'narrative_templates.json')
        
        try:
            if os.path.exists(template_file):
                with open(template_file, 'r', encoding='utf-8') as file:
                    self.template_cache = json.load(file)
                logger.info(f"Templates narratifs chargés depuis {template_file}")
            else:
                logger.warning(f"Fichier de templates {template_file} non trouvé. Utilisation des templates par défaut.")
                # Création des templates par défaut
                self.template_cache = {
                    "welcome": "Bienvenue dans le monde de {world_name}! {world_description}",
                    "location_description": "Vous êtes à {location_name}. {location_description}",
                    "npc_description": "{npc_name} est ici. {npc_description}",
                    "item_description": "Vous voyez {item_name}. {item_description}",
                    "correction": "Vous ne pouvez pas faire cela parce que {reason}.",
                    "default_response": "Le MJ réfléchit à votre action et considère le monde actuel..."
                }
                
                # Sauvegarder les templates par défaut
                os.makedirs(template_dir, exist_ok=True)
                with open(template_file, 'w', encoding='utf-8') as file:
                    json.dump(self.template_cache, file, indent=2, ensure_ascii=False)
                logger.info(f"Templates par défaut créés et sauvegardés dans {template_file}")
        except Exception as e:
            logger.error(f"Erreur lors du chargement des templates: {str(e)}")
            self.template_cache = {}
    
    def _format_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """
        Formate un template avec le contexte fourni.
        
        Args:
            template_name: Nom du template à utiliser
            context: Dictionnaire de variables pour le formattage
            
        Returns:
            str: Template formaté avec les variables du contexte
        """
        template = self.template_cache.get(template_name, "{}")
        try:
            # Tentative de formattage simple avec les variables du contexte
            return template.format(**context)
        except KeyError as e:
            logger.warning(f"Variable manquante dans le template '{template_name}': {str(e)}")
            return template
    
    def _prepare_context_prompt(self, action_text: str, context: Dict[str, Any]) -> str:
        """
        Prépare un prompt complet avec le contexte du jeu pour l'IA.
        
        Args:
            action_text: Le texte de l'action du joueur
            context: Contexte actuel du jeu
            
        Returns:
            str: Prompt formaté pour l'IA
        """
        player = context.get('player', {})
        location = context.get('location', {})
        npcs = context.get('npcs', [])
        items = context.get('items', [])
        world_config = context.get('world_config', {})
        history = context.get('history', [])
        
        # Formatage du contexte pour l'IA
        prompt = f"""Tu es le Maître du Jeu (MJ) d'un jeu de rôle textuel se déroulant dans un monde appelé "{world_config.get('nom', 'Monde inconnu')}".
IMPORTANT: Tu dois répondre UNIQUEMENT en français. Ne réponds JAMAIS en anglais.
Ambiance: {world_config.get('ambiance', 'Indéterminée')}
Objectif: {world_config.get('objectif', 'Explorer et survivre')}

CONTEXTE ACTUEL:
Le joueur ({player.get('name', 'Aventurier')}) se trouve à {location.get('name', 'un lieu inconnu')}.
Description du lieu: {location.get('description', 'Aucune description disponible')}

Personnages présents:
"""
        
        if npcs:
            for npc in npcs:
                prompt += f"- {npc.get('name')}: {npc.get('description', 'Aucune description')}. "
                if npc.get('personality'):
                    prompt += f"Personnalité: {npc.get('personality')}. "
                prompt += "\n"
        else:
            prompt += "- Aucun personnage présent.\n"
        
        prompt += "\nObjets visibles:\n"
        if items:
            for item in items:
                prompt += f"- {item.get('name')}: {item.get('description', 'Aucune description')}\n"
        else:
            prompt += "- Aucun objet visible.\n"
        
        # Historique récent des actions
        if history:
            prompt += "\nHistorique récent:\n"
            for entry in history[-5:]:
                if entry.get('type') == 'player_action':
                    prompt += f"- Joueur: {entry.get('text')}\n"
                elif entry.get('type') == 'gm_response':
                    prompt += f"- MJ: {entry.get('text')}\n"
        
        # Règles du monde
        prompt += "\nRÈGLES:\n"
        if world_config.get('règles', {}).get('les_pnj_ne_savent_pas_tout', True):
            prompt += "- Les PNJ ont une connaissance limitée du monde et ne savent pas tout.\n"
        if world_config.get('règles', {}).get('cohérence_stricte', True):
            prompt += "- Maintenir une cohérence stricte avec l'histoire et le monde.\n"
        
        # Action du joueur et instruction pour le modèle
        prompt += f"""
ACTION DU JOUEUR: {action_text}

En tant que MJ, réponds de manière immersive et narrative à l'action du joueur.
- Réponds UNIQUEMENT en français.
- Décris ce qui se passe de manière vivante et engageante.
- Reste cohérent avec le contexte, l'ambiance et les personnages présents.
- Utilise un langage descriptif et évocateur.
- N'inclus pas de balises comme "MJ:" ou similaires, réponds directement comme un MJ.
- Si l'action du joueur est impossible ou incohérente, explique pourquoi de manière immersive (sans dire explicitement que c'est impossible).

Réponse du MJ en français:
"""
        
        return prompt
    
    def generate_response(self, action_text: str, context: Dict[str, Any]) -> str:
        """
        Génère une réponse narrative pour une action du joueur.
        
        Args:
            action_text: Le texte de l'action du joueur
            context: Contexte actuel du jeu
            
        Returns:
            str: La réponse narrative du MJ
        """
        prompt = self._prepare_context_prompt(action_text, context)
        
        # Mesure du temps de réponse
        start_time = time.time()
        response = self.llm.generate_text(prompt)
        elapsed_time = time.time() - start_time
        
        logger.info(f"Réponse générée en {elapsed_time:.2f} secondes")
        
        return response
    
    def generate_correction(self, action_text: str, reason: str, context: Dict[str, Any]) -> str:
        """
        Génère une correction narrative lorsque l'action du joueur n'est pas cohérente.
        
        Args:
            action_text: Le texte de l'action du joueur
            reason: La raison pour laquelle l'action n'est pas cohérente
            context: Contexte actuel du jeu
            
        Returns:
            str: La réponse corrective du MJ
        """
        prompt = f"""Tu es le Maître du Jeu d'un jeu de rôle textuel.
IMPORTANT: Tu dois répondre UNIQUEMENT en français, jamais en anglais.

Le joueur a tenté une action qui n'est pas cohérente ou impossible à réaliser: "{action_text}"
Raison: {reason}

CONTEXTE ACTUEL:
Lieu: {context.get('location', {}).get('name', 'Lieu inconnu')}
Personnages présents: {', '.join([npc.get('name', 'Inconnu') for npc in context.get('npcs', [])])}
Objets visibles: {', '.join([item.get('name', 'Inconnu') for item in context.get('items', [])])}

Génère une réponse narrative qui:
1. Explique de manière immersive pourquoi l'action n'est pas possible
2. Suggère subtilement des alternatives possibles
3. Maintient l'ambiance du jeu et le roleplaying
4. N'utilise PAS de formulations comme "tu ne peux pas faire ça" ou "cette action est impossible"
5. Reste dans le ton de l'univers de jeu
6. Est OBLIGATOIREMENT rédigée en français, pas en anglais

Réponse du MJ en français:
"""
        
        return self.llm.generate_text(prompt)
    
    def generate_world_description(self, world_config: Dict[str, Any]) -> str:
        """
        Génère une description complète du monde basée sur la configuration.
        
        Args:
            world_config: Configuration du monde
            
        Returns:
            str: Description narrative du monde
        """
        prompt = f"""Tu es un maître conteur spécialisé dans la création de mondes imaginaires.
IMPORTANT: Tu dois répondre UNIQUEMENT en français, jamais en anglais.

Génère une description riche et évocatrice d'un monde pour un jeu de rôle textuel basé sur les informations suivantes:

Nom du monde: {world_config.get('nom', 'Monde sans nom')}
Ambiance générale: {world_config.get('ambiance', 'Non spécifiée')}
Objectif principal: {world_config.get('objectif', 'Explorer et survivre')}
Lieux importants: {', '.join(world_config.get('lieux', ['Non spécifiés']))}

La description doit:
1. Captiver l'imagination du joueur
2. Établir une atmosphère cohérente avec l'ambiance indiquée
3. Donner un aperçu de l'histoire et des enjeux du monde
4. Faire référence aux lieux principaux de manière intrigante
5. Rester entre 150 et 250 mots
6. Être OBLIGATOIREMENT rédigée en français

Description du monde en français:
"""
        
        return self.llm.generate_text(prompt)
    
    def generate_location_description(self, location_name: str, location_type: str, world_config: Dict[str, Any]) -> str:
        """
        Génère une description détaillée d'un lieu.
        
        Args:
            location_name: Nom du lieu
            location_type: Type de lieu (village, forêt, donjon, etc.)
            world_config: Configuration du monde
            
        Returns:
            str: Description narrative du lieu
        """
        prompt = f"""Tu es un maître conteur spécialisé dans la description de lieux imaginaires.
IMPORTANT: Tu dois répondre UNIQUEMENT en français, jamais en anglais.

Génère une description riche et évocatrice du lieu suivant dans le monde "{world_config.get('nom', 'Monde inconnu')}":

Nom du lieu: {location_name}
Type de lieu: {location_type}
Ambiance générale du monde: {world_config.get('ambiance', 'Non spécifiée')}

La description doit:
1. Faire appel aux cinq sens (vue, ouïe, odorat, toucher, goût si pertinent)
2. Évoquer l'atmosphère particulière de ce lieu
3. Mentionner des détails architecturaux, naturels ou mystiques selon le type de lieu
4. Suggérer des histoires ou événements passés liés à ce lieu
5. Rester entre 100 et 150 mots
6. Être OBLIGATOIREMENT rédigée en français

Description du lieu en français:
"""
        
        return self.llm.generate_text(prompt)
    
    def generate_npc(self, location_name: str, npc_role: str, world_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Génère un PNJ complet avec personnalité, apparence et intentions.
        
        Args:
            location_name: Nom du lieu où se trouve le PNJ
            npc_role: Rôle général du PNJ (marchand, garde, etc.)
            world_config: Configuration du monde
            
        Returns:
            Dict[str, Any]: Données complètes du PNJ généré
        """
        prompt = f"""Tu es un créateur de personnages pour un jeu de rôle narratif.
IMPORTANT: Tu dois répondre UNIQUEMENT en français, jamais en anglais.

Génère un personnage non-joueur (PNJ) complet pour le lieu "{location_name}" dans le monde "{world_config.get('nom', 'Monde inconnu')}".

Rôle du PNJ: {npc_role}
Ambiance du monde: {world_config.get('ambiance', 'Non spécifiée')}

Génère un JSON avec les informations suivantes:
1. name: Nom complet du PNJ
2. gender: Genre du PNJ
3. age: Âge approximatif
4. description: Description physique détaillée (30-50 mots)
5. personality: Traits de personnalité dominants (3-5 traits)
6. motivation: Ce qui motive ce personnage, son objectif principal
7. secret: Un secret que ce personnage cache aux autres
8. knowledge: Ce que ce personnage sait sur le monde ou l'intrigue principale (limité à son rôle)
9. speech_pattern: Style de langage caractéristique de ce personnage
10. relationships: Relations avec d'autres PNJ ou groupes (au moins 1-2 relations)

Le format JSON attendu est:
{{
  "name": "...",
  "gender": "...",
  "age": ...,
  "description": "...",
  "personality": "...",
  "motivation": "...",
  "secret": "...",
  "knowledge": "...",
  "speech_pattern": "...",
  "relationships": [
    {{
      "target": "...",
      "type": "...",
      "description": "..."
    }}
  ]
}}

Assure-toi que le personnage:
- Est cohérent avec l'ambiance du monde
- A une personnalité distincte et mémorable
- Possède des motivations crédibles liées à son rôle
- A un secret intéressant qui pourrait être découvert par le joueur
- Toutes les descriptions et textes sont OBLIGATOIREMENT en français

JSON du PNJ en français:
"""
        
        response = self.llm.generate_text(prompt)
        
        try:
            # Tentative d'extraction du JSON de la réponse
            import re
            json_match = re.search(r'```json\n(.*?)\n```', response, re.DOTALL)
            if json_match:
                response = json_match.group(1)
            elif response.strip().startswith('{') and response.strip().endswith('}'):
                response = response.strip()
                
            npc_data = json.loads(response)
            return npc_data
        except (json.JSONDecodeError, Exception) as e:
            logger.error(f"Erreur lors du parsing du JSON du PNJ: {str(e)}")
            logger.debug(f"Réponse brute: {response}")
            
            # Fallback avec un PNJ par défaut
            return {
                "name": f"PNJ {npc_role}",
                "gender": "Indéterminé",
                "age": 30,
                "description": f"Un {npc_role} typique de {location_name}.",
                "personality": "Réservé, prudent",
                "motivation": "Survivre au jour le jour",
                "secret": "Cache quelque chose d'important",
                "knowledge": f"Connaît bien {location_name}",
                "speech_pattern": "Parle peu et directement",
                "relationships": [
                    {
                        "target": "Habitants",
                        "type": "Neutre",
                        "description": "Relations professionnelles uniquement"
                    }
                ]
            }
    
    def generate_introduction(self) -> str:
        """
        Génère une introduction au jeu.
        
        Returns:
            str: Texte d'introduction
        """
        prompt = """Génère une introduction immersive pour le début d'une aventure de jeu de rôle textuel.
IMPORTANT: Tu dois répondre UNIQUEMENT en français, jamais en anglais.

Cette introduction doit:
1. Établir une ambiance mystérieuse et engageante
2. Inviter le joueur à explorer le monde
3. Suggérer qu'il y a des secrets à découvrir
4. Rester ouverte pour s'adapter à différents types de mondes
5. Être écrite à la seconde personne (vous) pour impliquer directement le joueur
6. Être OBLIGATOIREMENT rédigée en français

Introduction en français:
"""
        return self.llm.generate_text(prompt)