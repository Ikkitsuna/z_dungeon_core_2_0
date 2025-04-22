#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests pour les systèmes de mémoire de Z-Dungeon Core 2.0
"""

import os
import sys
import json
import pytest
import time
from typing import Dict, Any, List, Optional

# Ajouter le répertoire parent au path pour pouvoir importer les modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from memory.local_memory import LocalMemory
from memory.global_memory import GlobalMemory
from memory.social_memory import SocialMemory
from memory.memory_manager import MemoryManager

# ====== TESTS DE LOCAL MEMORY ======

def test_local_memory_create():
    """Teste la création d'une mémoire locale"""
    memory = LocalMemory("test_entity", "npc", "Test NPC")
    assert memory.entity_id == "test_entity"
    assert memory.entity_type == "npc"
    assert memory.entity_name == "Test NPC"

def test_local_memory_add_memory():
    """Teste l'ajout d'un souvenir à une mémoire locale"""
    memory = LocalMemory("test_entity", "npc", "Test NPC")
    memory.add_memory("Un souvenir important", importance=5)
    
    memories = memory.get_memories()
    assert len(memories) > 0
    assert memories[0]["description"] == "Un souvenir important"
    assert memories[0]["importance"] == 5

def test_local_memory_get_important_memories():
    """Teste la récupération des souvenirs importants"""
    memory = LocalMemory("test_entity", "npc", "Test NPC")
    memory.add_memory("Souvenir peu important", importance=2)
    memory.add_memory("Souvenir important", importance=8)
    memory.add_memory("Souvenir moyen", importance=5)
    
    important_memories = memory.get_memories(min_importance=7)
    assert len(important_memories) == 1
    assert important_memories[0]["description"] == "Souvenir important"

def test_local_memory_add_knowledge():
    """Teste l'ajout de connaissances"""
    memory = LocalMemory("test_entity", "npc", "Test NPC")
    memory.add_knowledge("géographie", "village", "Le village est au nord de la forêt", 5)
    
    knowledge = memory.get_knowledge()
    assert "géographie" in knowledge
    assert "village" in knowledge["géographie"]
    assert knowledge["géographie"]["village"] == "Le village est au nord de la forêt"

# ====== TESTS DE GLOBAL MEMORY ======

def test_global_memory_create():
    """Teste la création d'une mémoire globale"""
    memory = GlobalMemory("test_world", "Test World")
    assert memory.world_id == "test_world"
    assert memory.world_name == "Test World"

def test_global_memory_add_event():
    """Teste l'ajout d'un événement à la mémoire globale"""
    memory = GlobalMemory("test_world", "Test World")
    event = memory.add_event(
        description="Un événement important s'est produit",
        importance=7,
        event_type="test_event"
    )
    
    assert "id" in event
    assert event["description"] == "Un événement important s'est produit"
    assert event["importance"] == 7
    
    # Vérifier qu'on peut récupérer l'événement
    events = memory.get_events(min_importance=5)
    assert len(events) > 0
    assert events[0]["description"] == "Un événement important s'est produit"

def test_global_memory_add_world_fact():
    """Teste l'ajout d'un fait mondial"""
    memory = GlobalMemory("test_world", "Test World")
    memory.add_world_fact("histoire", "Le royaume a été fondé il y a 500 ans", 6)
    
    facts = memory.get_world_facts()
    assert "histoire" in facts
    assert facts["histoire"][0]["fact"] == "Le royaume a été fondé il y a 500 ans"
    assert facts["histoire"][0]["importance"] == 6

# ====== TESTS DE MEMORY MANAGER ======

def test_memory_manager_create():
    """Teste la création d'un gestionnaire de mémoire"""
    manager = MemoryManager("test_world", "Test World")
    assert manager.world_id == "test_world"
    assert manager.world_name == "Test World"
    assert isinstance(manager.global_memory, GlobalMemory)
    assert isinstance(manager.social_memory, SocialMemory)

def test_memory_manager_register_entity():
    """Teste l'enregistrement d'une entité"""
    manager = MemoryManager("test_world", "Test World")
    local_memory = manager.register_entity("test_npc", "npc", "Test NPC")
    
    assert isinstance(local_memory, LocalMemory)
    assert "test_npc" in manager.local_memories
    assert manager.local_memories["test_npc"] == local_memory

def test_memory_manager_global_event():
    """Teste la mémorisation d'un événement global"""
    manager = MemoryManager("test_world", "Test World")
    npc_memory = manager.register_entity("test_npc", "npc", "Test NPC")
    
    event = manager.memorize_global_event(
        description="Un événement impliquant un PNJ",
        importance=7,
        event_type="test_event",
        involved_entities=["test_npc"]
    )
    
    # Vérifier que l'événement est dans la mémoire globale
    events = manager.global_memory.get_events(min_importance=5)
    assert len(events) > 0
    assert events[0]["description"] == "Un événement impliquant un PNJ"
    
    # Vérifier que l'événement est dans la mémoire locale du PNJ
    npc_memories = npc_memory.get_memories()
    assert len(npc_memories) > 0
    assert npc_memories[0]["description"] == "Un événement impliquant un PNJ"

def test_memory_manager_sync_world_fact():
    """Teste la synchronisation d'un fait entre mémoire globale et locale"""
    manager = MemoryManager("test_world", "Test World")
    npc_memory = manager.register_entity("test_npc", "npc", "Test NPC")
    
    manager.sync_world_fact(
        category="géographie",
        fact="La montagne est à l'est",
        importance=6,
        relevant_entity_ids=["test_npc"]
    )
    
    # Vérifier que le fait est dans la mémoire globale
    facts = manager.global_memory.get_world_facts()
    assert "géographie" in facts
    assert facts["géographie"][0]["fact"] == "La montagne est à l'est"
    
    # Vérifier que la connaissance est dans la mémoire locale du PNJ
    knowledge = npc_memory.get_knowledge()
    assert "géographie" in knowledge
    assert any("La montagne est à l'est" in value for key, value in knowledge["géographie"].items())

def test_memory_manager_get_entity_context():
    """Teste la génération de contexte pour une entité"""
    manager = MemoryManager("test_world", "Test World")
    npc_memory = manager.register_entity("test_npc", "npc", "Test NPC")
    npc_memory.add_memory("Je me souviens de quelque chose d'important", importance=8)
    
    context = manager.get_entity_context("test_npc")
    
    assert context["entity"]["id"] == "test_npc"
    assert context["entity"]["name"] == "Test NPC"
    assert len(context["memories"]) > 0
    assert context["memories"][0]["description"] == "Je me souviens de quelque chose d'important"

def test_memory_manager_save_load():
    """Teste la sauvegarde et le chargement de toutes les mémoires"""
    # Créer un répertoire temporaire pour les tests
    test_save_dir = "test_saves"
    os.makedirs(test_save_dir, exist_ok=True)
    
    try:
        # Créer et configurer un gestionnaire de mémoire
        manager = MemoryManager("test_world", "Test World")
        npc_memory = manager.register_entity("test_npc", "npc", "Test NPC")
        npc_memory.add_memory("Un souvenir pour tester la sauvegarde", importance=5)
        manager.global_memory.add_event("Un événement global test", 6, "test_event")
        
        # Sauvegarder toutes les mémoires
        success = manager.save_all(test_save_dir)
        assert success
        
        # Charger les mémoires
        loaded_manager = MemoryManager.load_all("test_world", "Test World", test_save_dir)
        assert loaded_manager is not None
        assert loaded_manager.world_id == "test_world"
        assert "test_npc" in loaded_manager.local_memories
        
        # Vérifier que les données sont correctes
        loaded_npc_memory = loaded_manager.get_local_memory("test_npc")
        assert loaded_npc_memory is not None
        memories = loaded_npc_memory.get_memories()
        assert len(memories) > 0
        assert memories[0]["description"] == "Un souvenir pour tester la sauvegarde"
        
        events = loaded_manager.global_memory.get_events()
        assert len(events) > 0
        assert events[0]["description"] == "Un événement global test"
    
    finally:
        # Nettoyer les fichiers de test
        import shutil
        if os.path.exists(test_save_dir):
            shutil.rmtree(test_save_dir)

# Exécution manuelle pour les tests
if __name__ == "__main__":
    # Tester LocalMemory
    print("=== Tests de LocalMemory ===")
    test_local_memory_create()
    test_local_memory_add_memory()
    test_local_memory_get_important_memories()
    test_local_memory_add_knowledge()
    
    # Tester GlobalMemory
    print("=== Tests de GlobalMemory ===")
    test_global_memory_create()
    test_global_memory_add_event()
    test_global_memory_add_world_fact()
    
    # Tester MemoryManager
    print("=== Tests de MemoryManager ===")
    test_memory_manager_create()
    test_memory_manager_register_entity()
    test_memory_manager_global_event()
    test_memory_manager_sync_world_fact()
    test_memory_manager_get_entity_context()
    
    # Tester la sauvegarde/chargement
    print("=== Tests de sauvegarde/chargement ===")
    test_memory_manager_save_load()
    
    print("Tous les tests ont réussi!")