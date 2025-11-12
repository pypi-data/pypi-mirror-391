import os
import sys
import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

project_root = os.path.dirname(os.path.abspath(__file__))
MEMORY_DIR = os.path.join(project_root, "memory")
MEMORY_JSON = os.path.join(MEMORY_DIR, "memories.json")
MEMORY_INDEX = os.path.join(MEMORY_DIR, "index.faiss")


def resolve_resource_path(*parts):
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, *parts)
    return os.path.join(os.path.dirname(__file__), *parts)

class MemoryManager:
    def __init__(self):
        os.makedirs(MEMORY_DIR, exist_ok=True)
        try:
            model_path = resolve_resource_path('models', 'all-MiniLM-L6-v2')
            self.model = SentenceTransformer(model_path)
        except FileNotFoundError:
            print("[Memory] Local model not found, loading from Hugging Face...")
            self.model = SentenceTransformer('all-MiniLM-L6-v2')

        self.memories = self._load_memories()
        self.index = self._build_or_load_index()
        print(f"[Memory] Saving to: {MEMORY_JSON}")


    def _load_memories(self):
        if os.path.exists(MEMORY_JSON):
            with open(MEMORY_JSON, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def _save_memories(self):
        with open(MEMORY_JSON, "w", encoding="utf-8") as f:
            json.dump(self.memories, f, indent=2)

    def _build_or_load_index(self):
        dim = 384  # dimension of MiniLM embeddings
        index = faiss.IndexFlatIP(dim)

        if self.memories:
            embeds = self.model.encode(self.memories, convert_to_numpy=True).astype("float32")
            faiss.normalize_L2(embeds)
            index.add(embeds)

        return index

    def add_memory(self, fact: str):
        self.memories.append(fact)
        self._save_memories()
        embed = self.model.encode([fact], convert_to_numpy=True).astype("float32")
        faiss.normalize_L2(embed)
        self.index.add(embed)

    def recall(self, query: str, top_k: int = 3):
        if not self.memories:
            return []

        query_vec = self.model.encode([query], convert_to_numpy=True).astype("float32")
        faiss.normalize_L2(query_vec)
        scores, indices = self.index.search(query_vec, top_k)
        return [self.memories[i] for i in indices[0] if i < len(self.memories)]

    def clear_all(self):
        self.memories = []
        self._save_memories()
        self.index.reset()

_manager = None

def initialize_memory():
    """
    Instantiate the MemoryManager (which will build/load your index),
    and stash it in a module-level variable so it can be used later.
    Any print()s here will be caught by suppress_stderr in main.py.
    """
    global _manager
    _manager = MemoryManager()
    return _manager
