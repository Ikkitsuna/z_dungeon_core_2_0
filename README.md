# Z‑Dungeon Core 2.0

&#x20;&#x20;

> **Z‑Dungeon Core** est un moteur de jeu de rôle narratif textuel auto‑hébergé en français, doté d’un Maître du Jeu (MJ) alimenté par une intelligence artificielle locale (Ollama). Créez, explorez et vivez des aventures cohérentes dans des mondes entièrement persistants.

---

## Sommaire&#x20;

- [🌟 Fonctionnalités](#🌟-fonctionnalités)
- [📋 Prérequis](#📋-prérequis)
- [🚀 Installation](#🚀-installation)
  - [Démarrage rapide (](#démarrage-rapide-run_demosh)[`run_demo.sh`](#démarrage-rapide-run_demosh)[)](#démarrage-rapide-run_demosh)
  - [Installation manuelle](#installation-manuelle)
- [🎮 Utilisation](#🎮-utilisation)
  - [Options en ligne de commande](#options-en-ligne-de-commande)
  - [Commandes en jeu](#commandes-en-jeu)
- [🏗️ Architecture du projet](#🏗️-architecture-du-projet)
- [🧠 Système de mémoire](#🧠-système-de-mémoire)
- [🛠️ Configuration](#🛠️-configuration)
- [🧪 Tests](#🧪-tests)
- [🤝 Contribution](#🤝-contribution)
- [📜 Licence](#📜-licence)
- [🙏 Remerciements](#🙏-remerciements)

---

## 🌟 Fonctionnalités

- ✨ **Boucle de jeu complète** : state machine gérant le tour du joueur, la génération IA, la mise à jour du monde et l’auto‑sauvegarde toutes les 10 actions.
- 🧠 **Moteur narratif IA** : génération de texte cohérente via [**Ollama**](https://ollama.ai/) (modèle par défaut : *llama3*). Option *dummy* pour les tests hors‑ligne.
- 📖 **Systèmes de mémoire avancés** : mémoire *globale*, *locale* et *sociale* pour que le monde se souvienne de vos actions.
- 🏘️ **Monde de démonstration “Village maudit”** : 10 lieux, 6 PNJ, 5 objets et une atmosphère sombre de village hanté.
- ⌨️ **Interface console immersive** : couleurs Rich, ASCII‑art, dialogue MJ dédié.
- 🔄 **Monde persistant** : sauvegarde horodatée, gestion de versions, lien symbolique vers la dernière partie.
- 🧩 **Architecture modulaire** : facile à étendre (LLM, UI web, nouveaux mondes…).
- 🇫🇷 **Entièrement en français** : interface et narration natives.

## 📋 Prérequis

- **Python ≥ 3.8** (`python --version` pour vérifier)
- **Ollama** installé et lancé (`ollama serve`)
- Libs Python listées dans `requirements.txt` (installation automatique ci‑dessous)

> **Systèmes testés :** Ubuntu 22.04, macOS 14, Windows 11 (WSL 2).

## 🚀 Installation

### Démarrage rapide (`run_demo.sh`)

```bash
# Clone & lance la démo (UNIX‑like)
git clone https://github.com/Ikkitsuna/z_dungeon_core_2_0.git
cd z_dungeon_core_2_0
./run_demo.sh
```

Le script :

1. Vérifie Python 3, propose un virtualenv et installe les dépendances.
2. Vérifie la présence du monde *Village maudit*.
3. Lance automatiquement le jeu avec ce monde.

### Installation manuelle

```bash
# 1. Clone
$ git clone https://github.com/Ikkitsuna/z_dungeon_core_2_0.git
$ cd z_dungeon_core_2_0

# 2. Environnement virtuel (facultatif mais recommandé)
$ python -m venv .venv && source .venv/bin/activate  # Windows : .venv\Scripts\activate

# 3. Dépendances
$ pip install -r requirements.txt

# 4. Télécharger un modèle LLM (ex. Llama 3 8B)
$ ollama pull llama3:8b
```

## 🎮 Utilisation

```bash
python main.py            # Assistant interactif
python main.py --world worlds/village_maudit.yaml   # Charge le monde de démo
```

### Options en ligne de commande

| Option             | Effet                                              |
| ------------------ | -------------------------------------------------- |
| `--new`            | Créer un nouveau monde interactif                  |
| `--list`           | Lister les mondes existants                        |
| `--world <chemin>` | Charger un monde spécifique                        |
| `--model <nom>`    | Surcharger le modèle LLM défini dans `config.yaml` |

### Commandes en jeu

| Commande            | Effet                            |
| ------------------- | -------------------------------- |
| `regarder`          | Examiner le lieu actuel          |
| `aller <direction>` | Se déplacer                      |
| `parler à <pnj>`    | Engager une conversation         |
| `prendre <objet>`   | Ramasser un objet                |
| `inventaire`        | Afficher votre inventaire        |
| `sauvegarder`       | Sauvegarde immédiate             |
| `quitter`           | Quitter puis reprendre plus tard |
| `aide`              | Afficher toutes les commandes    |

## 🏗️ Architecture du projet

```
z_dungeon_core_2_0/
│
├── core/            # Moteur (GameMaster, NarrativeEngine, …)
├── entities/        # Player, NPC, Item, Location…
├── memory/          # Global, Local, Social, + manager
├── interface/       # console_ui.py, game_console_ui.py, command_parser.py
├── worlds/          # Fichiers YAML/JSON des mondes (Village maudit inclus)
├── saves/           # Sauvegardes auto & manuelles
├── templates/       # Prompts & narrative templates
├── tests/           # PyTest + intégration
├── run_demo.sh      # Script zéro‑config
├── main.py          # Point d’entrée
└── config.yaml      # Paramètres globaux
```

## 🧠 Système de mémoire

| Niveau      | Portée        | Exemple                                       |
| ----------- | ------------- | --------------------------------------------- |
| **Globale** | Monde entier  | "Le maire a déclaré le couvre‑feu."           |
| **Locale**  | Entité / lieu | Un PNJ se souvient que le joueur l’a aidé.    |
| **Sociale** | Relations     | Score d’amitié/hostilité entre PNJ et joueur. |

Les souvenirs décroissent (paramètre `decay_rate`) et sont résumés périodiquement (`summary_interval`).

## 🛠️ Configuration

Extrait du `config.yaml` :

```yaml
llm:
  provider: "ollama"
  model: "llama3"
  temperature: 0.7
  max_tokens: 500
memory:
  decay_rate: 0.1
  summary_interval: 10
  max_memory_items: 50
```

## 🧪 Tests

```bash
# Tous les tests
python -m pytest -q

# Intégration : monde + boucle de jeu (exemple)
python -m pytest tests/test_integration.py -q
```

## 🤝 Contribution

1. Fork ; créez une branche (`git checkout -b feature/NouvelleFonction`).
2. Codez, testez (`pytest`).
3. Ouvrez une Pull Request.

### Standards

- **PEP 8** vérifié par *ruff* & *black* (pré‑commit).
- Commits conventionnels (`feat:`, `fix:`, `docs:` …).

## 📜 Licence

MIT © 2025 **Ikkitsuna**

## 🙏 Remerciements

- [Ollama](https://ollama.ai/) pour le moteur LLM self‑host.
- Bibliothèques Python : Rich, PyYAML, Requests…
- Les testeurs et contributrices de la communauté.

*Créé avec ❤️ par ****Ikkitsuna***
