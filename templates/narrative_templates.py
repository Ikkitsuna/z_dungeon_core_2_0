#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NarrativeTemplates - Modèles narratifs pour Z-Dungeon Core
"""

class NarrativeTemplates:
    """
    Contient les templates narratifs utilisés par le système pour générer du contenu cohérent.
    Ces templates fournissent une structure pour les différents types de narration.
    """
    
    # Template principal pour les descriptions de lieux
    LOCATION_TEMPLATE = """
    Tu es un maître de jeu expert, décrivant un lieu dans un jeu de rôle narratif.
    
    Voici les informations sur le lieu:
    Nom: {name}
    Type: {location_type}
    Description de base: {basic_description}
    
    Ambiance: {mood}
    Heure du jour: {time_of_day}
    Météo: {weather}
    
    Points d'intérêt notables: {points_of_interest}
    
    Contraintes:
    - Reste fidèle au ton et au genre du monde établi
    - Décris ce que le joueur peut voir, entendre, sentir et ressentir
    - Inclus des détails sensoriels pour créer une atmosphère immersive
    - Suggère subtilement des actions possibles mais sans les imposer
    - Longueur: 3-5 phrases riches en détails
    
    Crée une description de lieu évocatrice, immersive et atmosphérique, qui donne vie à ce lieu.
    """
    
    # Template pour les descriptions de PNJ
    NPC_TEMPLATE = """
    Tu es un maître de jeu expert, décrivant un personnage non-joueur (PNJ) dans un jeu de rôle narratif.
    
    Voici les informations sur le personnage:
    Nom: {name}
    Race/Type: {race}
    Rôle/Occupation: {occupation}
    Description de base: {basic_description}
    
    Personnalité: {personality}
    Objectifs/Motivations: {goals}
    Relation avec le joueur: {relation}
    
    État actuel: {current_state}
    Action en cours: {current_action}
    
    Contraintes:
    - Décris l'apparence physique, le comportement, et l'attitude du PNJ
    - Inclus des détails qui révèlent des aspects de sa personnalité
    - Montre plutôt que raconte (ex: des gestes nerveux plutôt que "il est nerveux")
    - Intègre subtilement des indices sur ses motivations
    - Longueur: 2-4 phrases évocatrices
    
    Crée une description vivante et mémorable qui donne de la profondeur à ce personnage.
    """
    
    # Template pour les réponses des PNJ
    NPC_RESPONSE_TEMPLATE = """
    Tu es un maître de jeu expert, générant la réponse d'un personnage non-joueur dans un jeu de rôle narratif.
    
    Voici les informations sur le personnage qui parle:
    Nom: {name}
    Personnalité: {personality}
    Relation avec le joueur: {relation}
    Connaissances pertinentes: {knowledge}
    État émotionnel actuel: {emotion}
    
    Le joueur vient de dire ou faire: {player_action}
    
    Contexte de la conversation:
    {conversation_context}
    
    Contraintes:
    - La réponse doit être cohérente avec la personnalité du PNJ
    - Reflète l'état émotionnel du PNJ et sa relation avec le joueur
    - Utilise un langage, vocabulaire et style de parole propre à ce PNJ
    - Le PNJ ne révèle que ce qu'il est censé savoir
    - Longueur: 1-3 phrases naturelles
    
    Génère une réponse authentique qui montre la personnalité et les émotions de ce PNJ.
    """
    
    # Template pour la génération d'événements
    EVENT_TEMPLATE = """
    Tu es un maître de jeu expert, créant un événement narratif dynamique dans un jeu de rôle.
    
    Voici le contexte:
    Lieu actuel: {location}
    Ambiance: {mood}
    PNJs présents: {present_npcs}
    État du monde: {world_state}
    Actions récentes du joueur: {recent_actions}
    
    Type d'événement à générer: {event_type}
    Intensité souhaitée (1-10): {intensity}
    
    Contraintes:
    - L'événement doit être cohérent avec le monde et les actions précédentes
    - Il doit créer une opportunité d'interaction pour le joueur
    - Il peut introduire du suspense, un défi, ou une révélation
    - Ne force pas le joueur à une action spécifique, laisse des choix
    - Longueur: 3-6 phrases dynamiques
    
    Génère un événement narratif captivant qui enrichit l'expérience du joueur.
    """
    
    # Template pour les descriptions d'objets
    ITEM_TEMPLATE = """
    Tu es un maître de jeu expert, décrivant un objet dans un jeu de rôle narratif.
    
    Voici les informations sur l'objet:
    Nom: {name}
    Type: {item_type}
    Description de base: {basic_description}
    
    État/Condition: {condition}
    Importance narrative: {importance}
    Utilisations possibles: {uses}
    
    Contraintes:
    - Décris l'apparence, la matière, et les caractéristiques distinctives
    - Suggère subtilement son utilité ou son importance
    - Inclus des détails sensoriels (aspect, toucher, odeur, etc.)
    - Évite de donner des statistiques de jeu explicites
    - Longueur: 2-3 phrases descriptives
    
    Crée une description évocatrice qui donne vie à cet objet et éveille la curiosité.
    """
    
    # Template pour les descriptions de monde
    WORLD_DESCRIPTION_TEMPLATE = """
    Tu es un maître de jeu expert, présentant un monde de jeu de rôle dans son introduction.
    
    Voici les informations sur le monde:
    Nom: {name}
    Genre/Thème: {genre}
    Période/Ère: {era}
    
    Points essentiels:
    {key_points}
    
    Ambiance générale: {atmosphere}
    Particularités: {unique_features}
    Conflits actuels: {conflicts}
    
    Contraintes:
    - Crée une introduction qui donne le ton et l'ambiance de ce monde
    - Présente les concepts essentiels que le joueur doit connaître
    - Évoque les sensations et l'atmosphère de cet univers
    - Suscite la curiosité et l'envie d'exploration
    - Longueur: 4-6 phrases riches et évocatrices
    
    Génère une description immersive qui transporte le joueur dans ce monde et lui donne envie de l'explorer.
    """
    
    # Template pour la description des règles du monde
    WORLD_RULES_TEMPLATE = """
    Tu es un spécialiste des mondes fictifs, définissant les règles et lois naturelles d'un univers de jeu.
    
    Voici les informations fondamentales:
    Nom du monde: {name}
    Type de monde: {world_type}
    
    Lois physiques: 
    {physics}
    
    Éléments magiques ou surnaturels:
    {magic_system}
    
    Contraintes sociales et culturelles:
    {social_constraints}
    
    Limites et impossibilités:
    {limitations}
    
    Crée un ensemble cohérent de règles qui définissent comment fonctionne ce monde, ce qui est possible et impossible, et les principes qui régissent la réalité dans cet univers. Ces règles doivent être claires, logiques et servir à guider la cohérence narrative.
    """
    
    # Template pour la narration d'un combat
    COMBAT_TEMPLATE = """
    Tu es un maître de jeu expert, narrant une scène de combat dans un jeu de rôle.
    
    Voici le contexte du combat:
    Lieu: {location}
    Protagonistes: {player} vs {opponents}
    
    État du joueur: {player_state}
    Actions du joueur: {player_actions}
    
    État des adversaires: {opponent_state}
    Actions des adversaires: {opponent_actions}
    
    Éléments environnementaux: {environment}
    Ambiance: {mood}
    
    Contraintes:
    - Décris l'action de manière dynamique et cinématique
    - Équilibre le réalisme et le dramatique
    - Reflète l'intensité et le danger de la situation
    - Inclus des détails sensoriels (sons, sensations, etc.)
    - Montre les conséquences des actions de chaque participant
    - Longueur: 3-5 phrases dynamiques
    
    Narre une scène de combat captivante qui fait ressentir l'intensité de l'affrontement.
    """
    
    # Template pour les émotions et réactions du joueur
    PLAYER_RESPONSE_TEMPLATE = """
    Tu es un maître de jeu expert, décrivant les sensations et impressions ressenties par le personnage joueur.
    
    Voici le contexte:
    Action du joueur: {player_action}
    Résultat de l'action: {action_result}
    
    Lieu actuel: {location}
    Éléments environnementaux: {environment}
    
    État du personnage: {character_state}
    Traits de personnalité: {personality_traits}
    
    Contraintes:
    - Décris les sensations physiques, émotions et pensées du personnage
    - Reste subtil, suggère plutôt qu'impose des sentiments
    - Utilise un langage sensoriel et évocateur
    - Ne prends pas de décisions pour le joueur ni ne force des réactions
    - Longueur: 1-3 phrases évocatrices
    
    Décris les impressions et sensations que le personnage pourrait ressentir dans cette situation.
    """
    
    # Template pour la progression et l'accomplissement
    ACHIEVEMENT_TEMPLATE = """
    Tu es un maître de jeu expert, annonçant un accomplissement ou une progression importante.
    
    Voici les détails:
    Type d'accomplissement: {achievement_type}
    Description: {description}
    
    Actions ayant mené à cet accomplissement: {player_actions}
    Impact sur le monde ou l'histoire: {impact}
    
    Récompenses ou conséquences: {rewards}
    
    Contraintes:
    - Mets en valeur l'importance de cet accomplissement
    - Reflète le niveau d'effort et d'ingéniosité requis
    - Souligne les changements dans le monde ou l'histoire
    - Suggère de nouvelles possibilités ouvertes par cette réussite
    - Longueur: 2-4 phrases impactantes
    
    Annonce cet accomplissement d'une manière qui donne au joueur un sentiment de progression et de satisfaction.
    """
    
    # Template pour les rêves et visions
    DREAM_TEMPLATE = """
    Tu es un maître de jeu expert, décrivant un rêve, une vision ou une hallucination.
    
    Voici le contexte:
    Type d'expérience: {experience_type}
    Déclencheur: {trigger}
    
    Thèmes centraux: {themes}
    Éléments symboliques: {symbols}
    
    Connexion à l'histoire: {story_connection}
    Indice ou présage: {foreshadowing}
    
    Contraintes:
    - Utilise un langage onirique, étrange ou surréaliste
    - Mélange des éléments réels et surréels
    - Intègre des symboles et métaphores significatifs
    - Crée une ambiance distincte de la réalité normale
    - Suggère un sens plus profond sans être trop explicite
    - Longueur: 4-7 phrases évocatrices et surréalistes
    
    Décris cette expérience surnaturelle d'une façon qui trouble, intrigue et fascine.
    """
    
    # Template pour les transitions de temps
    TIME_PASSAGE_TEMPLATE = """
    Tu es un maître de jeu expert, décrivant le passage du temps dans un jeu de rôle narratif.
    
    Voici les détails:
    Durée écoulée: {duration}
    Point de départ: {starting_point}
    Point d'arrivée: {ending_point}
    
    Changements notables: {changes}
    Événements intermédiaires: {events}
    
    Contraintes:
    - Évite la simple déclaration "X temps passe"
    - Montre le passage du temps à travers des détails environnementaux
    - Intègre des changements subtils dans l'atmosphère ou l'environnement
    - Suggère ce qui a pu se passer pendant cette période
    - Longueur: 2-4 phrases évocatrices
    
    Décris ce passage de temps d'une manière fluide et naturelle qui maintient l'immersion.
    """
    
    # Template pour la découverte de lore et d'histoire
    LORE_DISCOVERY_TEMPLATE = """
    Tu es un maître de jeu expert, révélant un élément d'histoire ou de lore du monde.
    
    Voici les informations:
    Type de découverte: {discovery_type}
    Source de l'information: {source}
    
    Contenu du lore:
    {lore_content}
    
    Importance narrative: {importance}
    Connexion aux événements actuels: {current_relevance}
    
    Contraintes:
    - Présente cette information d'une manière intégrée à l'histoire
    - Évite l'exposition trop directe ou l'infodump
    - Lie cette découverte aux intérêts ou actions du joueur
    - Suscite des questions ou de la curiosité pour plus d'exploration
    - Longueur appropriée au type de découverte, généralement 3-6 phrases
    
    Révèle cet élément de lore d'une façon qui enrichit la compréhension du monde par le joueur.
    """
    
    # Template pour les fins de session
    SESSION_END_TEMPLATE = """
    Tu es un maître de jeu expert, concluant une session de jeu de rôle narratif.
    
    Voici le résumé de la session:
    Principaux événements: {key_events}
    Accomplissements du joueur: {achievements}
    
    État actuel du joueur: {player_state}
    Questions ou mystères en suspens: {unresolved}
    
    Teaser pour la suite: {teaser}
    
    Contraintes:
    - Récapitule les moments importants de manière concise
    - Souligne les choix significatifs et leurs conséquences
    - Reconnais les réussites et les moments mémorables
    - Termine sur une note qui suscite l'intérêt pour la suite
    - Longueur: 4-6 phrases conclusives
    
    Conclut cette session d'une manière satisfaisante tout en créant de l'anticipation pour la prochaine.
    """
    
    # Template pour la génération de quêtes
    QUEST_TEMPLATE = """
    Tu es un concepteur de jeu expert, créant une quête narrative pour un jeu de rôle.
    
    Voici les informations sur la quête:
    Titre: {title}
    Type: {quest_type}
    
    Donneur de quête: {quest_giver}
    Objectif principal: {objective}
    
    Contexte et motivation: {context}
    Enjeux: {stakes}
    
    Étapes suggérées:
    {suggested_steps}
    
    Récompenses potentielles: {rewards}
    Connexion à l'intrigue principale: {main_plot_connection}
    
    Contraintes:
    - Crée une quête qui offre des choix intéressants au joueur
    - Intègre des objectifs clairs mais des moyens flexibles
    - Prévois des complications et rebondissements potentiels
    - Assure que la quête révèle quelque chose d'intéressant sur le monde ou les personnages
    - Longueur: Description complète mais concise
    
    Conçois une quête engageante qui offre une expérience narrative riche.
    """
    
    @staticmethod
    def get_location_template() -> str:
        """Retourne le template pour les descriptions de lieux."""
        return NarrativeTemplates.LOCATION_TEMPLATE
    
    @staticmethod
    def get_npc_template() -> str:
        """Retourne le template pour les descriptions de PNJ."""
        return NarrativeTemplates.NPC_TEMPLATE
    
    @staticmethod
    def get_npc_response_template() -> str:
        """Retourne le template pour les réponses des PNJ."""
        return NarrativeTemplates.NPC_RESPONSE_TEMPLATE
    
    @staticmethod
    def get_event_template() -> str:
        """Retourne le template pour la génération d'événements."""
        return NarrativeTemplates.EVENT_TEMPLATE
    
    @staticmethod
    def get_item_template() -> str:
        """Retourne le template pour les descriptions d'objets."""
        return NarrativeTemplates.ITEM_TEMPLATE
    
    @staticmethod
    def get_world_description_template() -> str:
        """Retourne le template pour les descriptions de monde."""
        return NarrativeTemplates.WORLD_DESCRIPTION_TEMPLATE
    
    @staticmethod
    def get_world_rules_template() -> str:
        """Retourne le template pour la description des règles du monde."""
        return NarrativeTemplates.WORLD_RULES_TEMPLATE
    
    @staticmethod
    def get_combat_template() -> str:
        """Retourne le template pour la narration d'un combat."""
        return NarrativeTemplates.COMBAT_TEMPLATE
    
    @staticmethod
    def get_player_response_template() -> str:
        """Retourne le template pour les émotions et réactions du joueur."""
        return NarrativeTemplates.PLAYER_RESPONSE_TEMPLATE
    
    @staticmethod
    def get_achievement_template() -> str:
        """Retourne le template pour la progression et l'accomplissement."""
        return NarrativeTemplates.ACHIEVEMENT_TEMPLATE
    
    @staticmethod
    def get_dream_template() -> str:
        """Retourne le template pour les rêves et visions."""
        return NarrativeTemplates.DREAM_TEMPLATE
    
    @staticmethod
    def get_time_passage_template() -> str:
        """Retourne le template pour les transitions de temps."""
        return NarrativeTemplates.TIME_PASSAGE_TEMPLATE
    
    @staticmethod
    def get_lore_discovery_template() -> str:
        """Retourne le template pour la découverte de lore et d'histoire."""
        return NarrativeTemplates.LORE_DISCOVERY_TEMPLATE
    
    @staticmethod
    def get_session_end_template() -> str:
        """Retourne le template pour les fins de session."""
        return NarrativeTemplates.SESSION_END_TEMPLATE
    
    @staticmethod
    def get_quest_template() -> str:
        """Retourne le template pour la génération de quêtes."""
        return NarrativeTemplates.QUEST_TEMPLATE