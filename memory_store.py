import json
import os

MEMORY_FILE = "jarvis_memory.json"

def load_persistent_memory():
    if not os.path.exists(MEMORY_FILE):
        return []
    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def save_persistent_memory(memory):
    try:
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(memory, f, indent=2)
    except:
        pass

def remember_fact(fact: str):
    memory = load_persistent_memory()
    if fact not in memory:
        memory.append(fact)
        save_persistent_memory(memory)

def get_memory_summary():
    memory = load_persistent_memory()
    if not memory:
        return ""
    summary = "Here is what you remember about Dan:\n"
    for item in memory:
        summary += f"- {item}\n"
    return summary