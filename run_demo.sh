#!/bin/bash
# Script de démarrage rapide pour Z-Dungeon Core 2.0
# Lancement de la démonstration avec le monde "Village maudit"

# Coloration pour les messages
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}======================================${NC}"
echo -e "${GREEN}Z-DUNGEON CORE 2.0 - DÉMO${NC}"
echo -e "${BLUE}======================================${NC}"

# Vérifier que Python est installé
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Erreur: Python 3 n'est pas installé.${NC}"
    exit 1
fi

# Vérifier que les dépendances sont installées
if [ ! -f "requirements.txt" ]; then
    echo -e "${RED}Erreur: Le fichier requirements.txt est manquant.${NC}"
    exit 1
fi

# Proposer d'installer les dépendances si nécessaire
if [ ! -d "venv" ]; then
    echo -e "${BLUE}Environnement virtuel non détecté. Voulez-vous en créer un et installer les dépendances? (o/n)${NC}"
    read -r response
    if [[ "$response" =~ ^([oO][uU][iI]|[oO])$ ]]; then
        echo -e "${GREEN}Création d'un environnement virtuel...${NC}"
        python3 -m venv venv
        source venv/bin/activate
        echo -e "${GREEN}Installation des dépendances...${NC}"
        pip install -r requirements.txt
    else
        echo -e "${BLUE}Utilisation de l'environnement Python système.${NC}"
        echo -e "${GREEN}Installation des dépendances...${NC}"
        pip install -r requirements.txt
    fi
else
    source venv/bin/activate
fi

# Vérifier si le monde de démo existe
if [ ! -f "worlds/village_maudit.yaml" ]; then
    echo -e "${RED}Erreur: Le monde de démonstration 'village_maudit.yaml' est manquant.${NC}"
    exit 1
fi

# Créer le dossier saves s'il n'existe pas
mkdir -p saves

# Lancer le jeu avec le monde de démonstration
# Utilisation de -m pour exécuter en tant que module - cela résout les problèmes d'imports relatifs
echo -e "${GREEN}Lancement de la démo avec le monde 'Village Maudit'...${NC}"
PYTHONPATH=. python3 main.py --world worlds/village_maudit.yaml

exit 0