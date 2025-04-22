# Z-Dungeon Core 2.0

![Version](https://img.shields.io/badge/version-2.0-blue)
![Python](https://img.shields.io/badge/python-3.8%2B-green)
![License](https://img.shields.io/badge/license-MIT-orange)

Z-Dungeon Core 2.0 est un moteur de jeu de rôle narratif textuel avec un Maître du Jeu propulsé par Intelligence Artificielle. Ce système permet de créer, explorer et vivre des aventures narratives riches où le joueur interagit avec un monde dynamique et cohérent.

## 🌟 Caractéristiques

- **Moteur narratif IA** - Utilise des modèles de langage locaux via [Ollama](https://ollama.ai/) pour générer du contenu narratif cohérent
- **Systèmes de mémoire avancés** - Trois niveaux de mémoire (globale, locale, sociale) pour une cohérence narrative
- **Interface console immersive** - Interface utilisateur en mode texte riche et colorée
- **Architecture modulaire** - Facilement extensible et adaptable à différents types d'univers
- **Entièrement en français** - Interface, documentation et narration entièrement en français
- **Monde persistant** - Sauvegarde et chargement complet de l'état du monde

## 📋 Prérequis

- Python 3.8 ou supérieur
- [Ollama](https://ollama.ai/) (pour les modèles de langage locaux)
- Bibliothèques Python (voir `requirements.txt`)

## 🚀 Installation

1. Clonez le dépôt :
   ```bash
   git clone https://github.com/votre-nom/z_dungeon_core_2_0.git
   cd z_dungeon_core_2_0
   ```

2. Installez les dépendances :
   ```bash
   pip install -r requirements.txt
   ```

3. Installez Ollama (si non installé) :
   - Consultez [ollama.ai](https://ollama.ai/) pour les instructions d'installation

4. Téléchargez un modèle compatible pour Ollama (llama3 recommandé) :
   ```bash
   ollama pull llama3
   ```

## 🎮 Utilisation

### Démarrage rapide

Lancez le jeu avec la commande :
```bash
python main.py
```

Cela ouvrira l'assistant de création de monde ou vous permettra de choisir un monde existant.

### Options de ligne de commande

- `python main.py --new` : Créer un nouveau monde
- `python main.py --list` : Lister les mondes disponibles
- `python main.py --world <chemin>` : Charger un monde spécifique

### Commandes de jeu

Une fois dans le jeu, vous pouvez utiliser des commandes comme :
- `regarder` - Examiner votre environnement
- `aller <direction>` - Se déplacer dans une direction
- `parler à <personnage>` - Engager une conversation
- `prendre <objet>` - Ramasser un objet
- `inventaire` - Afficher votre inventaire
- `aide` - Afficher la liste des commandes disponibles

## 🏗️ Architecture du projet

```
z_dungeon_core_2_0/
│
├── core/                      # Composants principaux
│   ├── game_master.py         # Coordonne tous les aspects du jeu
│   ├── narrative_engine.py    # Gère la génération de texte via LLM
│   ├── llm_interface.py       # Interface pour les modèles de langage
│   ├── config_manager.py      # Gestion de la configuration
│   └── world_generator.py     # Génération procédurale de monde
│
├── memory/                    # Système de mémoire
│   ├── memory_manager.py      # Gestionnaire central des mémoires
│   ├── global_memory.py       # Mémoire globale du monde
│   ├── local_memory.py        # Mémoire locale des entités
│   └── social_memory.py       # Relations sociales entre entités
│
├── entities/                  # Entités du jeu
│   ├── entity.py              # Classe de base des entités
│   ├── player.py              # Joueur
│   ├── npc.py                 # Personnages non-joueurs
│   ├── location.py            # Lieux
│   └── item.py                # Objets
│
├── interface/                 # Interface utilisateur
│   ├── console_ui.py          # Interface console de base
│   ├── game_console_ui.py     # Interface console spécifique au jeu
│   └── command_parser.py      # Analyseur de commandes textuelles
│
├── templates/                 # Templates pour le moteur narratif
│
├── tests/                     # Tests unitaires
│
├── worlds/                    # Configurations de mondes
│
├── saves/                     # Sauvegardes de parties
│
├── main.py                    # Point d'entrée principal
├── config.yaml                # Configuration globale
└── requirements.txt           # Dépendances Python
```

## 🧠 Système de mémoire

Le système de mémoire à trois niveaux est l'une des fonctionnalités les plus avancées :

1. **Mémoire globale** - Stocke les faits sur le monde, l'historique des événements et les quêtes
2. **Mémoire locale** - Chaque entité (PNJ, lieu) a sa propre mémoire et connaissances
3. **Mémoire sociale** - Gère les relations et interactions entre les entités

Ce système permet une cohérence narrative à long terme et des personnages qui se souviennent des interactions passées avec le joueur.

## 🛠️ Configuration

Le fichier `config.yaml` à la racine du projet permet de configurer tous les aspects du jeu :
- Paramètres du modèle de langage (température, taille des réponses)
- Comportement du système de mémoire
- Chemins des fichiers de sauvegarde
- Options d'interface utilisateur

## 🧪 Tests

Exécutez les tests unitaires avec :
```bash
python -m pytest tests/
```

Des tests spécifiques peuvent être exécutés avec :
```bash
python -m pytest tests/test_memory.py
```

## 🤝 Contribution

Les contributions sont les bienvenues ! Voici comment contribuer :

1. Fork le projet
2. Créez votre branche de fonctionnalité (`git checkout -b feature/AmazingFeature`)
3. Committez vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

## 📜 Licence

Ce projet est sous licence MIT - voir le fichier [LICENSE](LICENSE) pour plus de détails.

## 📚 Documentation

Une documentation plus détaillée est disponible dans le dossier `/docs` (en développement).

## 🙏 Remerciements

- [Ollama](https://ollama.ai/) pour le support des modèles de langage locaux
- La communauté Python pour les bibliothèques utilisées
- Tous les testeurs et contributeurs au projet

---

Créé avec ❤️ par Ikkitsuna
