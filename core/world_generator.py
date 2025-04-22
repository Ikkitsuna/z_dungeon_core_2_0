#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WorldGenerator - Générateur de monde pour Z-Dungeon Core 2.0
"""

import os
import json
import logging
import random
import uuid
from typing import Dict, List, Any, Optional

# Configuration du système de logging
logger = logging.getLogger('WorldGenerator')

class WorldGenerator:
    """
    Générateur de monde qui crée l'univers complet à partir d'une carte racine.
    Cette classe est responsable de générer les lieux, les PNJ et les objets
    qui constituent le monde de jeu.
    """
    
    def __init__(self, world_config: Dict[str, Any]):
        """
        Initialise le générateur de monde avec une configuration.
        
        Args:
            world_config: Configuration du monde (nom, ambiance, règles, etc.)
        """
        self.world_config = world_config
        self.name = world_config.get('nom', 'Monde sans nom')
        self.ambiance = world_config.get('ambiance', 'Indéterminée')
        self.objectif = world_config.get('objectif', 'Explorer et survivre')
        self.lieux = world_config.get('lieux', [])
        self.pnj_initiaux = world_config.get('pnj_initiaux', 5)
        
        # Variables pour la génération aléatoire
        self.location_types = {
            'village': ['place centrale', 'marché', 'taverne', 'forge', 'temple', 'maison', 'ferme'],
            'forêt': ['clairière', 'ruisseau', 'grotte', 'ancien arbre', 'campement', 'sentier'],
            'donjon': ['entrée', 'salle du trône', 'salle des gardes', 'trésorerie', 'cellules', 'armurerie'],
            'ruines': ['hall effondré', 'temple abandonné', 'bibliothèque', 'tour', 'crypte', 'jardin sauvage'],
            'ville': ['place du marché', 'quartier noble', 'port', 'guilde', 'taverne', 'cathédrale', 'université'],
            'montagne': ['pic', 'caverne', 'mine', 'col', 'refuge', 'cascade'],
            'plage': ['côte', 'port', 'phare', 'grotte marine', 'épave'],
            'désert': ['oasis', 'temple enfoui', 'dunes', 'caravansérail', 'ruines antiques']
        }
        
        self.npc_roles = {
            'village': ['fermier', 'aubergiste', 'forgeron', 'marchand', 'prêtre', 'garde', 'chasseur'],
            'forêt': ['druide', 'chasseur', 'ermite', 'ranger', 'bûcheron', 'bandit'],
            'donjon': ['garde', 'serviteur', 'prisonnier', 'conseiller', 'magicien', 'noble'],
            'ruines': ['archéologue', 'pilleur', 'fantôme', 'gardien', 'érudit', 'créature'],
            'ville': ['noble', 'marchand', 'garde', 'artisan', 'érudit', 'voleur', 'prêtre', 'mendiant'],
            'montagne': ['mineur', 'ermite', 'guide', 'bandit', 'créature', 'réfugié'],
            'plage': ['pêcheur', 'marin', 'contrebandier', 'naufragé', 'marchand'],
            'désert': ['nomade', 'marchand', 'guide', 'bandit', 'ermite', 'gardien de temple']
        }
        
        self.item_types = {
            'arme': ['épée', 'arc', 'dague', 'hache', 'lance', 'bâton', 'marteau'],
            'armure': ['cuir', 'cotte de mailles', 'bouclier', 'casque', 'gants', 'bottes'],
            'potion': ['soin', 'force', 'résistance', 'invisibilité', 'antidote'],
            'outil': ['pioche', 'corde', 'lanterne', 'grappin', 'pelle', 'sac'],
            'artefact': ['amulette', 'anneau', 'gemme', 'parchemin', 'livre', 'clé'],
            'nourriture': ['pain', 'viande', 'fruit', 'eau', 'vin', 'fromage'],
            'trésor': ['pièces', 'gemmes', 'couronne', 'statue', 'tableau']
        }
    
    def generate(self) -> Dict[str, Any]:
        """
        Génère un monde complet basé sur la configuration.
        
        Returns:
            Dict[str, Any]: Données complètes du monde généré
        """
        logger.info(f"Génération du monde: {self.name}")
        
        world_data = {
            'name': self.name,
            'description': f"Un monde de {self.ambiance} où l'objectif est de {self.objectif}.",
            'locations': [],
            'npcs': [],
            'items': []
        }
        
        # Générer les lieux
        locations_data = self._generate_locations()
        world_data['locations'] = locations_data
        
        # Générer les PNJ
        npcs_data = self._generate_npcs(locations_data)
        world_data['npcs'] = npcs_data
        
        # Générer les objets
        items_data = self._generate_items(locations_data)
        world_data['items'] = items_data
        
        logger.info(f"Monde généré avec {len(locations_data)} lieux, {len(npcs_data)} PNJ et {len(items_data)} objets")
        
        return world_data
    
    def _generate_locations(self) -> List[Dict[str, Any]]:
        """
        Génère les lieux du monde basés sur la configuration.
        
        Returns:
            List[Dict[str, Any]]: Liste des lieux générés
        """
        locations = []
        
        # Utiliser les lieux définis dans la configuration
        for location_type in self.lieux:
            # Déterminer le nombre de sous-lieux pour ce type
            sub_location_count = random.randint(2, 5)
            
            # Identifier la liste des sous-types possibles pour ce lieu
            sub_location_types = self.location_types.get(location_type, ['section'])
            
            # Générer le lieu principal
            main_location_id = str(uuid.uuid4())
            main_location = {
                'id': main_location_id,
                'name': self._generate_location_name(location_type),
                'type': location_type,
                'description': self._generate_location_description(location_type),
                'connected_locations': [],
                'npc_ids': [],
                'item_ids': [],
                'character_ids': [],
                'is_main': True
            }
            locations.append(main_location)
            
            # Générer les sous-lieux
            for i in range(sub_location_count):
                sub_type = random.choice(sub_location_types)
                sub_location_id = str(uuid.uuid4())
                sub_location_name = f"{sub_type.capitalize()} de {main_location['name']}"
                
                sub_location = {
                    'id': sub_location_id,
                    'name': sub_location_name,
                    'type': sub_type,
                    'description': self._generate_location_description(sub_type),
                    'connected_locations': [main_location_id],  # Connecté au lieu principal
                    'npc_ids': [],
                    'item_ids': [],
                    'character_ids': [],
                    'is_main': False
                }
                locations.append(sub_location)
                
                # Ajouter le sous-lieu à la liste des connexions du lieu principal
                main_location['connected_locations'].append(sub_location_id)
        
        # Connecter les lieux principaux entre eux pour former un monde connecté
        main_locations = [loc for loc in locations if loc.get('is_main', False)]
        for i, location in enumerate(main_locations):
            if i > 0:
                # Connecter avec le lieu principal précédent
                prev_location = main_locations[i - 1]
                if prev_location['id'] not in location['connected_locations']:
                    location['connected_locations'].append(prev_location['id'])
                if location['id'] not in prev_location['connected_locations']:
                    prev_location['connected_locations'].append(location['id'])
        
        # Fermer le cercle si nous avons plus d'un lieu principal
        if len(main_locations) > 1:
            first_location = main_locations[0]
            last_location = main_locations[-1]
            if last_location['id'] not in first_location['connected_locations']:
                first_location['connected_locations'].append(last_location['id'])
            if first_location['id'] not in last_location['connected_locations']:
                last_location['connected_locations'].append(first_location['id'])
        
        return locations
    
    def _generate_location_name(self, location_type: str) -> str:
        """
        Génère un nom pour un lieu basé sur son type.
        
        Args:
            location_type: Type de lieu (village, forêt, etc.)
            
        Returns:
            str: Nom généré pour le lieu
        """
        # Préfixes et suffixes pour enrichir les noms
        prefixes = {
            'village': ['Petit', 'Grand', 'Vieux', 'Nouveau', 'Saint', 'Bas', 'Haut'],
            'forêt': ['Sombre', 'Verte', 'Ancienne', 'Profonde', 'Mystique', 'Sauvage'],
            'donjon': ['Noir', 'Ancien', 'Perdu', 'Royal', 'Maudit', 'Oublié'],
            'ruines': ['Anciennes', 'Perdues', 'Oubliées', 'Sacrées', 'Maudites'],
            'ville': ['Port', 'Fort', 'Mont', 'Sainte', 'Nouvelle', 'Haute'],
            'montagne': ['Pic', 'Mont', 'Crête', 'Dent', 'Sommet'],
            'plage': ['Baie', 'Côte', 'Anse', 'Cap', 'Rive'],
            'désert': ['Dunes', 'Plaine', 'Étendue', 'Vallée']
        }
        
        suffixes = {
            'village': ['Bourg', 'sur-Mer', 'les-Bains', 'du-Lac', 'en-Haut', 'la-Forêt'],
            'forêt': ['des Murmures', 'des Ombres', 'Éternelle', 'des Fées', 'des Anciens'],
            'donjon': ['de l\'Oubli', 'des Ombres', 'du Roi', 'de la Nuit', 'des Âmes'],
            'ruines': ['des Anciens', 'du Temps', 'Perdues', 'de l\'Empire', 'Sacrées'],
            'ville': ['des Marchands', 'Royale', 'du Commerce', 'des Arts', 'des Guildes'],
            'montagne': ['de Feu', 'de Glace', 'des Géants', 'des Vents', 'des Nuages'],
            'plage': ['d\'Or', 'des Sirènes', 'des Épaves', 'du Couchant', 'des Perles'],
            'désert': ['de Feu', 'des Mirages', 'sans Fin', 'des Ossements', 'du Silence']
        }
        
        # Racines pour les noms (syllabes)
        roots = ['al', 'ar', 'bel', 'car', 'dar', 'el', 'fal', 'gal', 'har', 'ir', 
                'kal', 'lor', 'mal', 'nor', 'or', 'par', 'qar', 'ral', 'sal', 'tal', 
                'ul', 'val', 'wal', 'xal', 'yal', 'zar']
        
        # Générer le nom de base
        if random.random() < 0.7:  # 70% de chance d'utiliser un nom composé
            name_root = random.choice(roots) + random.choice(['a', 'e', 'i', 'o', 'u']) + random.choice(roots)
        else:  # 30% de chance d'utiliser un nom simple
            name_root = random.choice(roots) + random.choice(['and', 'end', 'ind', 'ond', 'und', 'or', 'ar', 'ir', 'ur'])
        
        # Capitaliser la première lettre
        name_root = name_root.capitalize()
        
        # 50% de chance d'ajouter un préfixe ou un suffixe
        if random.random() < 0.5:
            if random.random() < 0.5 and location_type in prefixes:  # Préfixe
                prefix = random.choice(prefixes[location_type])
                name = f"{prefix}-{name_root}"
            elif location_type in suffixes:  # Suffixe
                suffix = random.choice(suffixes[location_type])
                name = f"{name_root} {suffix}"
            else:
                name = name_root
        else:
            name = name_root
        
        return name
    
    def _generate_location_description(self, location_type: str) -> str:
        """
        Génère une description basique pour un lieu basé sur son type.
        Une description plus détaillée sera générée par le NarrativeEngine si nécessaire.
        
        Args:
            location_type: Type de lieu (village, forêt, etc.)
            
        Returns:
            str: Description générée pour le lieu
        """
        descriptions = {
            'village': [
                "Un petit village paisible avec des maisons en bois et des toits de chaume.",
                "Un village rural entouré de champs cultivés et de vergers.",
                "Un village modeste mais accueillant, avec une place centrale où les habitants se rassemblent."
            ],
            'forêt': [
                "Une forêt dense aux arbres anciens, où la lumière peine à percer la canopée.",
                "Une forêt mystérieuse remplie de bruits étranges et de créatures sauvages.",
                "Une forêt ancienne aux arbres immenses, traversée de sentiers à peine visibles."
            ],
            'donjon': [
                "Une structure imposante de pierre sombre, avec des tours qui s'élèvent vers le ciel.",
                "Un donjon ancien aux murs épais et aux fenêtres étroites, parfait pour se défendre.",
                "Une forteresse massive entourée de douves, avec un pont-levis et des remparts."
            ],
            'ruines': [
                "Les vestiges d'une civilisation oubliée, avec des colonnes brisées et des murs effondrés.",
                "Des ruines anciennes envahies par la végétation, témoins silencieux d'une grandeur passée.",
                "Un site archéologique fascinant, avec des structures à moitié effondrées et des artefacts éparpillés."
            ],
            'place centrale': [
                "Le cœur du village, où se déroulent les marchés et les célébrations.",
                "Une place pavée entourée de bâtiments importants, avec une fontaine en son centre.",
                "Un lieu de rassemblement pour les habitants, avec un arbre ancien qui offre de l'ombre."
            ],
            'marché': [
                "Un lieu animé où les marchands présentent leurs marchandises sur des étals colorés.",
                "Un marché bruyant rempli d'odeurs d'épices, de nourriture et de parfums exotiques.",
                "Un espace commercial où l'on peut trouver toutes sortes de biens, des plus communs aux plus rares."
            ],
            'taverne': [
                "Un établissement chaleureux avec une cheminée crépitante et l'odeur de la bière et du ragoût.",
                "Un lieu de rencontre populaire où les voyageurs échangent des histoires autour de bonnes chopes.",
                "Une auberge accueillante avec des tables en bois usé et un comptoir bien garni."
            ],
            'forge': [
                "Un atelier chaud et bruyant où le forgeron façonne le métal à coups de marteau.",
                "Une forge dont la cheminée crache constamment de la fumée noire, remplie d'outils et d'armes.",
                "Un lieu de travail du métal, où l'on entend le bruit rythmique de l'enclume du matin au soir."
            ],
            'temple': [
                "Un bâtiment sacré dédié aux dieux, avec des vitraux colorés et une atmosphère sereine.",
                "Un lieu de culte orné de symboles religieux et de bougies votives.",
                "Un sanctuaire paisible où les fidèles viennent prier et méditer."
            ]
        }
        
        # Utiliser une description par défaut si le type de lieu n'est pas dans notre dictionnaire
        if location_type not in descriptions:
            return f"Un {location_type} typique, sans caractéristiques particulièrement remarquables."
        
        return random.choice(descriptions[location_type])
    
    def _generate_npcs(self, locations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Génère les PNJ du monde basés sur les lieux existants.
        
        Args:
            locations: Liste des lieux générés
            
        Returns:
            List[Dict[str, Any]]: Liste des PNJ générés
        """
        npcs = []
        
        # Générer des PNJ pour chaque lieu principal
        main_locations = [loc for loc in locations if loc.get('is_main', False)]
        
        # Répartir les PNJ entre les lieux principaux
        npcs_per_location = max(1, self.pnj_initiaux // len(main_locations))
        
        for location in main_locations:
            location_type = location['type']
            location_id = location['id']
            
            # Déterminer les rôles possibles pour ce type de lieu
            possible_roles = self.npc_roles.get(location_type, ['habitant'])
            
            # Générer les PNJ pour ce lieu
            for _ in range(npcs_per_location):
                npc_id = str(uuid.uuid4())
                role = random.choice(possible_roles)
                
                npc = {
                    'id': npc_id,
                    'name': self._generate_npc_name(),
                    'role': role,
                    'description': self._generate_npc_description(role),
                    'personality': self._generate_npc_personality(),
                    'location_id': location_id,
                    'inventory': [],
                    'knowledge': {},
                    'relationships': {}
                }
                
                npcs.append(npc)
                
                # Ajouter le PNJ à la liste des PNJ du lieu
                location['npc_ids'].append(npc_id)
        
        # Générer des PNJ pour certains sous-lieux
        sub_locations = [loc for loc in locations if not loc.get('is_main', False)]
        selected_sub_locations = random.sample(sub_locations, min(len(sub_locations), self.pnj_initiaux // 2))
        
        for location in selected_sub_locations:
            location_type = location['type']
            location_id = location['id']
            
            # Déterminer les rôles possibles pour ce type de lieu
            parent_type = next((loc['type'] for loc in locations if loc['id'] in location['connected_locations']), 'village')
            possible_roles = self.npc_roles.get(parent_type, ['habitant'])
            
            npc_id = str(uuid.uuid4())
            role = random.choice(possible_roles)
            
            npc = {
                'id': npc_id,
                'name': self._generate_npc_name(),
                'role': role,
                'description': self._generate_npc_description(role),
                'personality': self._generate_npc_personality(),
                'location_id': location_id,
                'inventory': [],
                'knowledge': {},
                'relationships': {}
            }
            
            npcs.append(npc)
            
            # Ajouter le PNJ à la liste des PNJ du lieu
            location['npc_ids'].append(npc_id)
        
        # Générer des relations entre les PNJ
        self._generate_npc_relationships(npcs)
        
        return npcs
    
    def _generate_npc_name(self) -> str:
        """
        Génère un nom aléatoire pour un PNJ.
        
        Returns:
            str: Nom généré
        """
        first_names = [
            'Alaric', 'Bram', 'Cedric', 'Darian', 'Elric', 'Faron', 'Galen', 'Hector',
            'Ivo', 'Jareth', 'Kevan', 'Lucan', 'Milo', 'Nolan', 'Osric', 'Phelan',
            'Quentin', 'Rowan', 'Silas', 'Tristan', 'Ulric', 'Varian', 'Weston', 'Xavier',
            'Adela', 'Brenna', 'Cora', 'Delia', 'Elara', 'Fiona', 'Giselle', 'Helena',
            'Ivy', 'Jenna', 'Kira', 'Lyra', 'Mira', 'Nora', 'Ophelia', 'Phoebe',
            'Quinn', 'Rhea', 'Selene', 'Thea', 'Una', 'Vera', 'Willa', 'Xandra'
        ]
        
        last_names = [
            'Ashford', 'Blackwood', 'Caldwell', 'Drake', 'Elderwood', 'Frost', 'Greymane',
            'Hawthorne', 'Ironheart', 'Jagger', 'Kingsley', 'Lowell', 'Marsh', 'Nightshade',
            'Oakhart', 'Pierce', 'Quill', 'Ravenwood', 'Silverstone', 'Thornfield',
            'Underhill', 'Vale', 'Whitehorn', 'Yewridge', 'Zephyr'
        ]
        
        # 20% de chance d'avoir juste un prénom
        if random.random() < 0.2:
            return random.choice(first_names)
        else:
            return f"{random.choice(first_names)} {random.choice(last_names)}"
    
    def _generate_npc_description(self, role: str) -> str:
        """
        Génère une description basique pour un PNJ basé sur son rôle.
        Une description plus détaillée sera générée par le NarrativeEngine si nécessaire.
        
        Args:
            role: Rôle du PNJ (marchand, forgeron, etc.)
            
        Returns:
            str: Description générée pour le PNJ
        """
        descriptions = {
            'fermier': [
                "Un homme robuste aux mains calleuses, habitué au travail difficile.",
                "Une personne simple et travailleuse, avec un visage tanné par le soleil.",
                "Un individu patient et persévérant, qui connaît les cycles de la nature."
            ],
            'aubergiste': [
                "Une personne joviale et accueillante, toujours prête à servir une bonne chope.",
                "Un individu qui connaît toutes les rumeurs locales et sait écouter.",
                "Une personne entreprenante qui maintient son établissement impeccable."
            ],
            'forgeron': [
                "Un homme musclé aux bras puissants, avec des traces de brûlures sur ses avant-bras.",
                "Une personne déterminée et précise, fière de son art du métal.",
                "Un artisan respecté pour ses compétences et sa force impressionnante."
            ],
            'marchand': [
                "Une personne vive et alerte, avec un sourire commercial bien rodé.",
                "Un individu rusé qui sait reconnaître une bonne affaire à des lieues.",
                "Une personne éloquente qui peut vendre n'importe quoi à n'importe qui."
            ],
            'garde': [
                "Une personne vigilante au regard perçant, toujours à l'affût du danger.",
                "Un individu discipliné, avec une posture droite et une main jamais loin de son arme.",
                "Une personne déterminée à maintenir l'ordre, quoi qu'il en coûte."
            ],
            'prêtre': [
                "Une personne sereine au regard bienveillant, vêtue de robes religieuses.",
                "Un individu réfléchi qui parle avec sagesse et mesure.",
                "Une personne dévouée à sa foi, respectée pour sa sagesse spirituelle."
            ]
        }
        
        if role in descriptions:
            return random.choice(descriptions[role])
        else:
            return f"Un {role} typique, avec l'apparence et l'attitude que l'on pourrait attendre de quelqu'un exerçant cette profession."
    
    def _generate_npc_personality(self) -> str:
        """
        Génère des traits de personnalité pour un PNJ.
        
        Returns:
            str: Traits de personnalité générés
        """
        traits_positifs = [
            'amical', 'généreux', 'honnête', 'courageux', 'patient', 'loyal', 'sage',
            'optimiste', 'compatissant', 'curieux', 'déterminé', 'créatif', 'humble',
            'serviable', 'respectueux', 'énergique', 'réfléchi', 'confiant'
        ]
        
        traits_neutres = [
            'prudent', 'réservé', 'pragmatique', 'stoïque', 'traditionnel', 'méthodique',
            'indépendant', 'perfectionniste', 'analytique', 'observateur', 'formel',
            'sérieux', 'mystérieux', 'nostalgique', 'rêveur'
        ]
        
        traits_négatifs = [
            'méfiant', 'têtu', 'impatient', 'orgueilleux', 'impulsif', 'nerveux',
            'cynique', 'irritable', 'rancunier', 'avare', 'envieux', 'pessimiste',
            'manipulateur', 'paresseux', 'égoïste', 'colérique'
        ]
        
        # Sélectionner des traits de personnalité
        num_traits = random.randint(2, 4)
        personality_traits = []
        
        # Au moins un trait positif ou neutre
        if random.random() < 0.7:  # 70% de chance d'avoir un trait positif
            personality_traits.append(random.choice(traits_positifs))
        else:
            personality_traits.append(random.choice(traits_neutres))
        
        # Possibilité d'avoir un trait négatif
        if random.random() < 0.6:  # 60% de chance d'avoir un trait négatif
            personality_traits.append(random.choice(traits_négatifs))
        
        # Compléter avec des traits aléatoires
        all_traits = traits_positifs + traits_neutres + traits_négatifs
        while len(personality_traits) < num_traits:
            trait = random.choice(all_traits)
            if trait not in personality_traits:
                personality_traits.append(trait)
        
        return ", ".join(personality_traits)
    
    def _generate_npc_relationships(self, npcs: List[Dict[str, Any]]) -> None:
        """
        Génère des relations entre les PNJ.
        
        Args:
            npcs: Liste des PNJ générés
        """
        relation_types = [
            'ami', 'famille', 'rival', 'collègue', 'mentor', 'élève',
            'amoureux', 'ennemi', 'allié', 'client', 'employeur'
        ]
        
        # Nombre de relations à générer (environ 1 à 2 par PNJ)
        num_relationships = random.randint(len(npcs) // 2, len(npcs) * 2)
        
        for _ in range(num_relationships):
            if len(npcs) < 2:
                break
                
            # Sélectionner deux PNJ différents
            npc1, npc2 = random.sample(npcs, 2)
            
            # Déterminer le type de relation
            relation_type = random.choice(relation_types)
            
            # Ajouter la relation dans les deux sens
            if 'relationships' not in npc1:
                npc1['relationships'] = {}
            if 'relationships' not in npc2:
                npc2['relationships'] = {}
                
            npc1['relationships'][npc2['id']] = {
                'type': relation_type,
                'attitude': random.choice(['positive', 'neutre', 'négative']),
                'strength': random.randint(1, 10)  # Force de la relation sur 10
            }
            
            # Relation inverse (peut être différente)
            inverse_relations = {
                'ami': 'ami',
                'famille': 'famille',
                'rival': 'rival',
                'collègue': 'collègue',
                'mentor': 'élève',
                'élève': 'mentor',
                'amoureux': 'amoureux',
                'ennemi': 'ennemi',
                'allié': 'allié',
                'client': 'fournisseur',
                'employeur': 'employé'
            }
            
            inverse_type = inverse_relations.get(relation_type, relation_type)
            
            npc2['relationships'][npc1['id']] = {
                'type': inverse_type,
                'attitude': random.choice(['positive', 'neutre', 'négative']),
                'strength': random.randint(1, 10)
            }
    
    def _generate_items(self, locations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Génère les objets du monde basés sur les lieux existants.
        
        Args:
            locations: Liste des lieux générés
            
        Returns:
            List[Dict[str, Any]]: Liste des objets générés
        """
        items = []
        
        # Générer des objets pour chaque lieu
        for location in locations:
            location_type = location['type']
            location_id = location['id']
            
            # Déterminer le nombre d'objets à générer
            num_items = random.randint(0, 3 if location.get('is_main', False) else 1)
            
            for _ in range(num_items):
                item_category = random.choice(list(self.item_types.keys()))
                item_type = random.choice(self.item_types[item_category])
                
                item_id = str(uuid.uuid4())
                
                item = {
                    'id': item_id,
                    'name': self._generate_item_name(item_type),
                    'type': item_type,
                    'category': item_category,
                    'description': self._generate_item_description(item_type, item_category),
                    'properties': self._generate_item_properties(item_category),
                    'location_id': location_id,
                    'owner_id': None
                }
                
                items.append(item)
                
                # Ajouter l'objet à la liste des objets du lieu
                location['item_ids'].append(item_id)
        
        return items
    
    def _generate_item_name(self, item_type: str) -> str:
        """
        Génère un nom pour un objet basé sur son type.
        
        Args:
            item_type: Type d'objet
            
        Returns:
            str: Nom généré
        """
        adjectives = [
            'ancien', 'usé', 'solide', 'fin', 'élégant', 'rustique', 'orné',
            'simple', 'massif', 'léger', 'sombre', 'brillant', 'terni',
            'décoré', 'étrange', 'commun', 'rare', 'exotique', 'magique'
        ]
        
        prefixes = [
            'de qualité', 'du voyageur', 'du guerrier', 'du sage', 'du marchand',
            'royal', 'artisanal', 'traditionnel', 'enchanté', 'béni', 'maudit'
        ]
        
        materials = {
            'arme': ['en acier', 'en fer', 'en bronze', 'en bois', 'en os'],
            'armure': ['en cuir', 'en mailles', 'en plaques', 'en écailles', 'rembourré'],
            'potion': ['rouge', 'bleue', 'verte', 'dorée', 'fumante', 'brillante'],
            'outil': ['en bois', 'en métal', 'en pierre', 'en os', 'renforcé'],
            'artefact': ['gravé', 'incrusté de gemmes', 'scintillant', 'gravé de runes', 'antique'],
            'nourriture': ['frais', 'séché', 'fumé', 'épicé', 'doux', 'amer'],
            'trésor': ['en or', 'en argent', 'serti de gemmes', 'précieux', 'rare']
        }
        
        # 50% de chance d'avoir un adjectif
        if random.random() < 0.5:
            name = f"{random.choice(adjectives)} {item_type}"
        else:
            name = item_type
        
        # 30% de chance d'avoir un matériau
        if random.random() < 0.3 and item_type in materials:
            material = random.choice(materials.get(item_type, ['']))
            if material:
                name = f"{name} {material}"
        
        # 20% de chance d'avoir un préfixe
        if random.random() < 0.2:
            name = f"{name} {random.choice(prefixes)}"
        
        return name.capitalize()
    
    def _generate_item_description(self, item_type: str, item_category: str) -> str:
        """
        Génère une description pour un objet basé sur son type et sa catégorie.
        
        Args:
            item_type: Type d'objet
            item_category: Catégorie d'objet
            
        Returns:
            str: Description générée
        """
        descriptions = {
            'arme': [
                f"Un {item_type} bien équilibré, idéal pour le combat.",
                f"Ce {item_type} a clairement vu de nombreuses batailles.",
                f"Un {item_type} finement travaillé, aussi beau que mortel."
            ],
            'armure': [
                f"Une protection {item_type} offrant un bon équilibre entre mobilité et défense.",
                f"Cette armure {item_type} est usée mais reste fiable.",
                f"Un équipement défensif {item_type} de bonne facture."
            ],
            'potion': [
                f"Un flacon contenant un liquide {item_type} qui dégage une légère odeur.",
                f"Cette potion de {item_type} est scellée avec de la cire.",
                f"Un breuvage {item_type} qui promet des effets intéressants."
            ],
            'outil': [
                f"Un {item_type} pratique pour diverses tâches quotidiennes.",
                f"Cet {item_type} semble avoir été fabriqué par un artisan compétent.",
                f"Un {item_type} bien conçu et durable."
            ],
            'artefact': [
                f"Un {item_type} mystérieux aux origines incertaines.",
                f"Ce {item_type} dégage une étrange aura.",
                f"Un {item_type} ancien qui semble avoir une histoire intéressante."
            ],
            'nourriture': [
                f"Du {item_type} qui semble appétissant et nourrissant.",
                f"Cette portion de {item_type} est suffisante pour un repas.",
                f"Un {item_type} typique de la région."
            ],
            'trésor': [
                f"Un {item_type} qui attirerait certainement l'œil d'un collectionneur.",
                f"Ce {item_type} semble avoir une valeur considérable.",
                f"Un {item_type} qui brillerait dans n'importe quelle collection."
            ]
        }
        
        if item_category in descriptions:
            return random.choice(descriptions[item_category])
        else:
            return f"Un {item_type} standard sans caractéristiques particulièrement remarquables."
    
    def _generate_item_properties(self, item_category: str) -> Dict[str, Any]:
        """
        Génère des propriétés pour un objet basé sur sa catégorie.
        
        Args:
            item_category: Catégorie d'objet
            
        Returns:
            Dict[str, Any]: Propriétés générées
        """
        properties = {
            'value': random.randint(1, 100)  # Valeur de base
        }
        
        if item_category == 'arme':
            properties.update({
                'damage': random.randint(1, 10),
                'weight': random.randint(1, 5)
            })
        elif item_category == 'armure':
            properties.update({
                'defense': random.randint(1, 10),
                'weight': random.randint(1, 10)
            })
        elif item_category == 'potion':
            properties.update({
                'effect': random.choice(['healing', 'strength', 'speed', 'invisibility', 'resistance']),
                'duration': random.randint(1, 60)  # En minutes
            })
        elif item_category == 'outil':
            properties.update({
                'durability': random.randint(10, 100),
                'effectiveness': random.randint(1, 10)
            })
        elif item_category == 'artefact':
            properties.update({
                'magical': random.choice([True, False]),
                'age': random.randint(10, 1000)  # En années
            })
        elif item_category == 'nourriture':
            properties.update({
                'nutrition': random.randint(1, 10),
                'spoils_in': random.randint(1, 30)  # En jours
            })
        elif item_category == 'trésor':
            properties.update({
                'rarity': random.choice(['common', 'uncommon', 'rare', 'very rare', 'legendary']),
                'origin': random.choice(['local', 'foreign', 'ancient', 'unknown'])
            })
        
        # 10% de chance d'avoir une propriété spéciale
        if random.random() < 0.1:
            special_properties = [
                'glowing', 'humming', 'warm', 'cold', 'inscribed',
                'fragrant', 'cursed', 'blessed', 'sentient', 'shifting'
            ]
            properties['special'] = random.choice(special_properties)
        
        return properties