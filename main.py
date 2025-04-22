#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Z-Dungeon Core 2.0
=================
Un moteur de jeu de rôle narratif textuel avec un MJ IA
"""

import os
import sys
import argparse
import yaml
import json
from rich.console import Console
from rich.theme import Theme
from rich.prompt import Prompt

from core.game_master import GameMaster
from interface.game_console_ui import GameConsoleUI

custom_theme = Theme({
    "info": "cyan",
    "warning": "yellow",
    "danger": "bold red",
    "mj": "green",
    "player": "bold white",
    "location": "blue",
    "npc": "magenta",
    "item": "yellow",
})

console = Console(theme=custom_theme)

def load_world_config(world_file):
    """Charge une configuration de monde depuis un fichier YAML ou JSON."""
    try:
        extension = os.path.splitext(world_file)[1].lower()
        
        if extension == '.yaml' or extension == '.yml':
            with open(world_file, 'r', encoding='utf-8') as file:
                return yaml.safe_load(file)
        elif extension == '.json':
            with open(world_file, 'r', encoding='utf-8') as file:
                return json.load(file)
        else:
            console.print("[danger]Format de fichier non pris en charge. Utilisez YAML ou JSON.[/danger]")
            sys.exit(1)
    except Exception as e:
        console.print(f"[danger]Erreur lors du chargement du monde: {str(e)}[/danger]")
        sys.exit(1)

def create_new_world():
    """Assistant de création d'un nouveau monde."""
    console.print("[info]Assistant de création d'un nouveau monde[/info]")
    
    world = {}
    world["nom"] = Prompt.ask("Nom du monde")
    world["ambiance"] = Prompt.ask("Description de l'ambiance")
    world["objectif"] = Prompt.ask("Objectif principal de l'aventure")
    
    lieux = []
    console.print("[info]Ajoutez des lieux (entrée vide pour terminer)[/info]")
    while True:
        lieu = Prompt.ask("Nom d'un lieu", default="")
        if not lieu:
            break
        lieux.append(lieu)
    world["lieux"] = lieux
    
    world["pnj_initiaux"] = int(Prompt.ask("Nombre de PNJ initiaux", default="5"))
    
    world["règles"] = {
        "les_pnj_ne_savent_pas_tout": True,
        "cohérence_stricte": True
    }
    
    filename = f"worlds/{world['nom'].lower().replace(' ', '_')}.yaml"
    os.makedirs("worlds", exist_ok=True)
    
    with open(filename, 'w', encoding='utf-8') as file:
        yaml.dump(world, file, allow_unicode=True, sort_keys=False)
    
    console.print(f"[info]Monde '{world['nom']}' créé et sauvegardé dans {filename}[/info]")
    return filename

def main():
    """Point d'entrée principal de l'application."""
    parser = argparse.ArgumentParser(description="Z-Dungeon Core 2.0 - Un moteur de jeu de rôle narratif textuel avec un MJ IA")
    parser.add_argument("-w", "--world", help="Chemin vers le fichier de configuration du monde (YAML/JSON)")
    parser.add_argument("-n", "--new", action="store_true", help="Créer un nouveau monde")
    parser.add_argument("-l", "--list", action="store_true", help="Lister les mondes disponibles")
    args = parser.parse_args()
    
    # Afficher l'en-tête
    console.print("""
[bold cyan]
⚔️ Z-DUNGEON CORE 2.0 ⚔️
Un moteur de jeu de rôle narratif textuel avec un MJ IA
[/bold cyan]
    """)
    
    # Lister les mondes disponibles
    if args.list:
        world_files = []
        for ext in ['.yaml', '.yml', '.json']:
            world_files.extend(list(os.path.join('worlds', f) for f in os.listdir('worlds') if f.endswith(ext)))
        
        if world_files:
            console.print("[info]Mondes disponibles:[/info]")
            for i, world_file in enumerate(world_files, 1):
                console.print(f"  {i}. {os.path.splitext(os.path.basename(world_file))[0]}")
        else:
            console.print("[warning]Aucun monde disponible. Créez-en un avec l'option --new[/warning]")
        return
    
    # Créer un nouveau monde
    if args.new:
        world_file = create_new_world()
    else:
        world_file = args.world
    
    # Si aucun monde n'est spécifié, proposer de créer un nouveau monde ou d'en choisir un existant
    if not world_file:
        world_files = []
        os.makedirs('worlds', exist_ok=True)
        for ext in ['.yaml', '.yml', '.json']:
            world_files.extend(list(os.path.join('worlds', f) for f in os.listdir('worlds') if f.endswith(ext)))
        
        if world_files:
            console.print("[info]Mondes disponibles:[/info]")
            for i, wf in enumerate(world_files, 1):
                console.print(f"  {i}. {os.path.splitext(os.path.basename(wf))[0]}")
            
            choice = Prompt.ask(
                "Choisissez un monde par son numéro ou tapez 'n' pour en créer un nouveau", 
                default="1"
            )
            
            if choice.lower() == 'n':
                world_file = create_new_world()
            else:
                try:
                    index = int(choice) - 1
                    world_file = world_files[index]
                except (ValueError, IndexError):
                    console.print("[danger]Choix invalide. Utilisation du premier monde.[/danger]")
                    world_file = world_files[0]
        else:
            console.print("[info]Aucun monde trouvé. Création d'un nouveau monde...[/info]")
            world_file = create_new_world()
    
    # Charger la configuration du monde
    world_config = load_world_config(world_file)
    console.print(f"[info]Monde chargé: {world_config['nom']}[/info]")
    
    # Initialiser le GameMaster
    game_master = GameMaster(world_config)
    
    # Initialiser l'interface utilisateur avancée
    ui = GameConsoleUI()
    
    # Configurer l'interface avec le GameMaster
    if not game_master.player:
        # Demander au joueur de créer un personnage
        console.print("[info]Vous devez créer un personnage pour commencer à jouer.[/info]")
        player_name = Prompt.ask("Nom de votre personnage")
        player_desc = Prompt.ask("Description de votre personnage (optionnelle)", default="")
        game_master.create_player(player_name, player_desc)
    
    # Connexion du GameMaster à l'interface
    ui.set_player(game_master.player)
    ui.set_current_location(game_master.get_current_location())
    ui.set_narrative_engine(game_master.narrative_engine)
    
    # Configurer le parseur de commandes avec les actions du GameMaster
    configure_command_parser(ui.command_parser, game_master, ui)
    
    # Démarrer le jeu
    ui.start_game(title=world_config['nom'], subtitle=world_config.get('ambiance', ''), version="2.0")

def configure_command_parser(command_parser, game_master, ui):
    """Configure le parseur de commandes avec les actions spécifiques du jeu."""
    
    # Action: Regarder
    def look_action(args):
        if not args:
            # Regarder les alentours
            return game_master.process_player_action("regarder autour")
        else:
            # Regarder un objet/PNJ spécifique
            return game_master.process_player_action(f"examiner {args}")
    
    # Action: Aller
    def go_action(args):
        if not args:
            return "Où voulez-vous aller?"
        
        direction = args.lower()
        current_location = game_master.get_current_location()
        if not current_location:
            return "Erreur: Position actuelle inconnue."
        
        exits = current_location.get_exits() if hasattr(current_location, 'get_exits') else {}
        
        if direction in exits:
            success, message = game_master.move_player_to(exits[direction].id)
            if success:
                ui.set_current_location(game_master.get_current_location())
                ui.update_game_state()
            return message
        else:
            return game_master.process_player_action(f"aller vers {direction}")
    
    # Action: Parler
    def talk_action(args):
        if not args:
            return "À qui voulez-vous parler?"
        return game_master.process_player_action(f"parler à {args}")
    
    # Action: Prendre
    def take_action(args):
        if not args:
            return "Que voulez-vous prendre?"
        return game_master.process_player_action(f"prendre {args}")
    
    # Action: Utiliser
    def use_action(args):
        if not args:
            return "Que voulez-vous utiliser?"
        return game_master.process_player_action(f"utiliser {args}")
    
    # Action: Inventaire
    def inventory_action(args):
        ui.display_inventory()
        return ""
    
    # Action: Statut
    def status_action(args):
        ui.display_player_status()
        return ""
    
    # Action: Sauvegarder
    def save_action(args):
        save_path = args if args else None
        if game_master.save_game(save_path):
            return "Partie sauvegardée avec succès."
        else:
            return "Erreur lors de la sauvegarde."
    
    # Action par défaut: traiter comme une action narrative
    def default_action(action_text):
        return game_master.process_player_action(action_text)
    
    # Enregistrer les commandes
    command_parser.register_command("regarder", look_action, 
                                   "Examine votre environnement ou un objet spécifique.",
                                   ["look", "voir", "examiner", "observer"])
    
    command_parser.register_command("aller", go_action,
                                   "Vous déplace dans la direction indiquée.",
                                   ["go", "move", "déplacer", "direction"])
    
    command_parser.register_command("parler", talk_action,
                                   "Engage une conversation avec un PNJ.",
                                   ["talk", "discuter", "dialogue"])
    
    command_parser.register_command("prendre", take_action,
                                   "Prend un objet et le met dans votre inventaire.",
                                   ["take", "ramasser", "get"])
    
    command_parser.register_command("utiliser", use_action,
                                   "Utilise un objet de votre inventaire ou de l'environnement.",
                                   ["use", "employer", "activer"])
    
    command_parser.register_command("inventaire", inventory_action,
                                   "Affiche le contenu de votre inventaire.",
                                   ["inventory", "inv", "i", "sac"])
    
    command_parser.register_command("statut", status_action,
                                   "Affiche le statut actuel de votre personnage.",
                                   ["status", "état", "stats"])
    
    command_parser.register_command("sauvegarder", save_action,
                                   "Sauvegarde la partie en cours.",
                                   ["save", "enregistrer"])
    
    # Remplacer la fonction de traitement par défaut
    command_parser._handle_narrative_action = default_action

if __name__ == "__main__":
    main()