#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLMInterface - Interface abstraite pour les modèles de langage
"""

import os
import json
import logging
import requests
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

# Configuration du système de logging
logger = logging.getLogger('LLMInterface')

class LLMInterface(ABC):
    """
    Interface abstraite pour les modèles de langage.
    Cette classe définit l'API commune à tous les LLMs utilisés dans le jeu.
    """
    
    @abstractmethod
    def generate_text(self, prompt: str, **kwargs) -> str:
        """
        Génère du texte à partir d'un prompt.
        
        Args:
            prompt: Le texte du prompt pour le modèle
            **kwargs: Arguments supplémentaires spécifiques à l'implémentation
            
        Returns:
            str: Le texte généré par le modèle
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Vérifie si le modèle est disponible.
        
        Returns:
            bool: True si le modèle est disponible, False sinon
        """
        pass

class OllamaLLM(LLMInterface):
    """
    Implémentation de LLMInterface pour Ollama.
    """
    
    def __init__(self, model: str = "llama3", temperature: float = 0.7, max_tokens: int = 500):
        """
        Initialise le modèle Ollama.
        
        Args:
            model: Le modèle Ollama à utiliser
            temperature: Contrôle la créativité (0.0-1.0)
            max_tokens: Nombre maximum de tokens pour la réponse
        """
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.api_url = "http://localhost:11434/api/generate"
    
    def generate_text(self, prompt: str, **kwargs) -> str:
        """
        Génère du texte à partir d'un prompt en utilisant Ollama.
        
        Args:
            prompt: Le texte du prompt pour le modèle
            **kwargs: Arguments supplémentaires pour l'API Ollama
            
        Returns:
            str: Le texte généré par Ollama
        """
        try:
            # Fusionner les kwargs avec les paramètres par défaut
            payload = {
                "model": self.model,
                "prompt": prompt,
                "temperature": kwargs.get("temperature", self.temperature),
                "max_tokens": kwargs.get("max_tokens", self.max_tokens),
                "stream": False
            }
            
            # Ajouter des paramètres supplémentaires si présents
            if "system_prompt" in kwargs:
                payload["system"] = kwargs["system_prompt"]
            
            response = requests.post(self.api_url, json=payload, timeout=30)
            
            if response.status_code == 200:
                return response.json().get("response", "")
            else:
                logger.error(f"Erreur API Ollama: {response.status_code}, {response.text}")
                return "Désolé, je ne peux pas générer de réponse pour le moment."
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur lors de l'appel à Ollama: {str(e)}")
            return "Désolé, je ne peux pas me connecter au service Ollama. Vérifiez qu'il est bien démarré."
    
    def is_available(self) -> bool:
        """
        Vérifie si Ollama est disponible et si le modèle est chargé.
        
        Returns:
            bool: True si Ollama est disponible et le modèle est chargé, False sinon
        """
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                available_models = response.json().get("models", [])
                if any(model["name"] == self.model for model in available_models):
                    logger.info(f"Modèle {self.model} disponible sur Ollama")
                    return True
                else:
                    logger.warning(f"Modèle {self.model} non trouvé. Modèles disponibles: {[m['name'] for m in available_models]}")
                    return False
            else:
                logger.warning("Impossible de récupérer la liste des modèles Ollama")
                return False
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur de connexion à Ollama: {str(e)}")
            logger.info("Vous pouvez installer Ollama depuis https://ollama.ai/")
            return False

class DummyLLM(LLMInterface):
    """
    Implémentation factice de LLMInterface pour les tests.
    """
    
    def __init__(self, responses: Dict[str, str] = None):
        """
        Initialise le modèle factice.
        
        Args:
            responses: Dictionnaire de réponses prédéfinies (clé: mot-clé, valeur: réponse)
        """
        self.responses = responses or {
            "regarder": "Vous regardez autour de vous. Tout semble calme.",
            "parler": "Personne ne semble vous entendre.",
            "prendre": "Vous ne pouvez pas prendre cela.",
            "default": "Vous ne pouvez pas faire cette action pour le moment."
        }
    
    def generate_text(self, prompt: str, **kwargs) -> str:
        """
        Renvoie une réponse prédéfinie en fonction du prompt.
        
        Args:
            prompt: Le texte du prompt
            **kwargs: Arguments ignorés
            
        Returns:
            str: Réponse prédéfinie
        """
        # Chercher une correspondance dans les réponses prédéfinies
        for keyword, response in self.responses.items():
            if keyword.lower() in prompt.lower():
                return response
        
        # Réponse par défaut
        return self.responses.get("default", "Aucune réponse disponible.")
    
    def is_available(self) -> bool:
        """
        Le modèle factice est toujours disponible.
        
        Returns:
            bool: True
        """
        return True

# Factory function to create LLM instances based on configuration
def create_llm(config: Dict[str, Any]) -> LLMInterface:
    """
    Crée une instance de LLM basée sur la configuration.
    
    Args:
        config: Configuration du LLM (provider, model, etc.)
        
    Returns:
        LLMInterface: Instance de LLM
    """
    provider = config.get("provider", "ollama").lower()
    
    if provider == "ollama":
        return OllamaLLM(
            model=config.get("model", "llama3"),
            temperature=config.get("temperature", 0.7),
            max_tokens=config.get("max_tokens", 500)
        )
    elif provider == "dummy" or provider == "test":
        return DummyLLM(config.get("responses", None))
    else:
        logger.warning(f"Provider LLM inconnu: {provider}. Utilisation d'Ollama par défaut.")
        return OllamaLLM()