#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ConfigManager - Gestionnaire de configuration pour Z-Dungeon Core
"""

import os
import yaml
import logging
from typing import Dict, Any, Optional

# Configuration du système de logging
logger = logging.getLogger('ConfigManager')

class ConfigManager:
    """
    Gestionnaire de configuration pour Z-Dungeon Core.
    Charge, valide et fournit un accès à la configuration globale.
    """
    
    _instance = None  # Singleton
    
    @classmethod
    def get_instance(cls, config_path: Optional[str] = None) -> 'ConfigManager':
        """
        Récupère l'instance unique du ConfigManager (singleton).
        
        Args:
            config_path: Chemin vers le fichier de configuration (pour la première initialisation)
            
        Returns:
            ConfigManager: Instance unique du ConfigManager
        """
        if cls._instance is None:
            cls._instance = ConfigManager(config_path)
        return cls._instance
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialise le gestionnaire de configuration.
        
        Args:
            config_path: Chemin vers le fichier de configuration
        """
        self.config_path = config_path or os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.yaml')
        self.config = self._load_config()
        self._validate_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """
        Charge la configuration depuis le fichier YAML.
        
        Returns:
            Dict[str, Any]: Configuration chargée
        """
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as file:
                    config = yaml.safe_load(file)
                logger.info(f"Configuration chargée depuis {self.config_path}")
                return config
            else:
                logger.warning(f"Fichier de configuration {self.config_path} non trouvé. Utilisation des valeurs par défaut.")
                return self._get_default_config()
        except Exception as e:
            logger.error(f"Erreur lors du chargement de la configuration: {str(e)}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """
        Retourne une configuration par défaut.
        
        Returns:
            Dict[str, Any]: Configuration par défaut
        """
        return {
            "game": {
                "name": "Z-Dungeon Core 2.0",
                "version": "2.0",
                "save_dir": "saves",
                "worlds_dir": "worlds",
                "debug_mode": False
            },
            "llm": {
                "provider": "ollama",
                "model": "llama3",
                "temperature": 0.7,
                "max_tokens": 500
            },
            "memory": {
                "decay_rate": 0.1,
                "summary_interval": 10,
                "max_memory_items": 50,
                "importance_threshold": 3
            },
            "logging": {
                "level": "INFO",
                "narrative_log": True,
                "log_dir": "logs"
            },
            "ui": {
                "use_colors": True,
                "text_speed": "normal",
                "ascii_art": True
            }
        }
    
    def _validate_config(self) -> None:
        """
        Valide la configuration et applique les valeurs par défaut si nécessaire.
        """
        default_config = self._get_default_config()
        
        # Vérification de chaque section principale
        for section in default_config:
            if section not in self.config:
                logger.warning(f"Section '{section}' manquante dans la configuration. Utilisation des valeurs par défaut.")
                self.config[section] = default_config[section]
            else:
                # Vérification de chaque paramètre dans la section
                for param in default_config[section]:
                    if param not in self.config[section]:
                        logger.warning(f"Paramètre '{param}' manquant dans la section '{section}'. Utilisation de la valeur par défaut.")
                        self.config[section][param] = default_config[section][param]
    
    def get(self, section: str, param: Optional[str] = None, default: Any = None) -> Any:
        """
        Récupère une valeur de configuration.
        
        Args:
            section: Section de la configuration
            param: Paramètre à récupérer (None pour toute la section)
            default: Valeur par défaut si le paramètre n'existe pas
            
        Returns:
            Any: Valeur du paramètre ou section complète
        """
        if section not in self.config:
            return default
        
        if param is None:
            return self.config[section]
        
        return self.config[section].get(param, default)
    
    def save(self) -> bool:
        """
        Sauvegarde la configuration actuelle dans le fichier.
        
        Returns:
            bool: True si la sauvegarde a réussi, False sinon
        """
        try:
            with open(self.config_path, 'w', encoding='utf-8') as file:
                yaml.dump(self.config, file, default_flow_style=False, allow_unicode=True)
            logger.info(f"Configuration sauvegardée dans {self.config_path}")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde de la configuration: {str(e)}")
            return False
    
    def update(self, section: str, param: str, value: Any) -> bool:
        """
        Met à jour une valeur de configuration.
        
        Args:
            section: Section de la configuration
            param: Paramètre à mettre à jour
            value: Nouvelle valeur
            
        Returns:
            bool: True si la mise à jour a réussi, False sinon
        """
        if section not in self.config:
            self.config[section] = {}
        
        try:
            self.config[section][param] = value
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour de la configuration: {str(e)}")
            return False

# Pour faciliter l'accès à la configuration depuis n'importe quel module
def get_config(section: str = None, param: str = None, default: Any = None) -> Any:
    """
    Fonction utilitaire pour accéder à la configuration globale.
    
    Args:
        section: Section de la configuration (None pour toute la configuration)
        param: Paramètre à récupérer (None pour toute la section)
        default: Valeur par défaut si le paramètre n'existe pas
        
    Returns:
        Any: Valeur de configuration demandée
    """
    config_manager = ConfigManager.get_instance()
    
    if section is None:
        return config_manager.config
    
    return config_manager.get(section, param, default)