"""
🧠 GANGU - Query Info Agent (RAG-based)
=========================================
The knowledge brain of GANGU.
Uses Retrieval-Augmented Generation (RAG) to answer user queries about
products, GANGU features, Indian groceries, and more.

When the user asks something that isn't a purchase intent — or when
the intent is unclear — this agent retrieves relevant knowledge and
generates a helpful, elderly-friendly response in Hindi/Hinglish.

Pipeline Position:
    Intent Agent → Task Planner → (if inquiry/unclear) → Query Info Agent (YOU)

Architecture:
    1. Knowledge Base Loader  – loads JSON documents from knowledge_base/
    2. Chunker                – splits docs into searchable text chunks
    3. Embedder               – embeds chunks using Gemini Embedding API
    4. Vector Store            – numpy-based cosine similarity search
    5. RAG Generator          – retrieves top-k chunks → feeds to Gemini → generates answer

Author: GANGU Team
"""

import json
import os
import sys
import hashlib
import pickle
import time
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dotenv import load_dotenv

# Load .env from the GANGU root directory
gangu_root = Path(__file__).parent.parent
env_path = gangu_root / ".env"
load_dotenv(dotenv_path=env_path)
load_dotenv()

# Google GenAI
from google import genai

# ─────────────────── API CONFIGURATION ─────────────────── #

api_key = (
    os.environ.get("GEMINI_API_KEY_RAG")
    or os.environ.get("GEMINI_API_KEY")
    or os.environ.get("GOOGLE_API_KEY")
)
if not api_key:
    raise ValueError("❌ GEMINI_API_KEY environment variable not set")

print(f"🔑 Query Info (RAG) Agent using API key: ...{api_key[-8:]}")

client = genai.Client(api_key=api_key)

# ─────────────────── CONSTANTS ─────────────────── #

KNOWLEDGE_BASE_DIR = gangu_root / "knowledge_base"
EMBEDDING_CACHE_PATH = KNOWLEDGE_BASE_DIR / ".embedding_cache.pkl"
EMBEDDING_MODEL = "gemini-embedding-001"  # Gemini embedding model
GENERATION_MODEL = "gemini-2.5-flash"
TOP_K = 5  # Number of chunks to retrieve
CHUNK_MAX_TOKENS = 300  # Rough max tokens per chunk

# ─────────────────── KNOWLEDGE BASE LOADER ─────────────────── #


def _load_json_file(filepath: Path) -> Any:
    """Safely load a JSON file."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"  ⚠️ Failed to load {filepath.name}: {e}")
        return None


def load_knowledge_base() -> List[Dict[str, str]]:
    """
    Load all knowledge-base JSON files and convert them into
    a flat list of text chunks with metadata.

    Returns:
        List of {"id": str, "text": str, "source": str, "metadata": dict}
    """
    chunks: List[Dict[str, str]] = []

    if not KNOWLEDGE_BASE_DIR.exists():
        print(f"  ⚠️ Knowledge base directory not found: {KNOWLEDGE_BASE_DIR}")
        return chunks

    for json_file in sorted(KNOWLEDGE_BASE_DIR.glob("*.json")):
        data = _load_json_file(json_file)
        if data is None:
            continue

        source = json_file.stem  # e.g. "indian_groceries"

        if isinstance(data, list):
            # Array of documents (indian_groceries, gangu_features)
            for doc in data:
                chunk_text = _doc_to_chunk_text(doc, source)
                if chunk_text:
                    chunks.append({
                        "id": doc.get("id", hashlib.md5(chunk_text.encode()).hexdigest()[:12]),
                        "text": chunk_text,
                        "source": source,
                        "metadata": doc,
                    })
        elif isinstance(data, dict):
            # Mapping/dictionary files (hindi_english_mapping)
            for section_key, section_val in data.items():
                chunk_text = _mapping_to_chunk_text(section_key, section_val, source)
                if chunk_text:
                    chunks.append({
                        "id": f"{source}_{section_key}",
                        "text": chunk_text,
                        "source": source,
                        "metadata": {section_key: section_val},
                    })

    print(f"  📚 Loaded {len(chunks)} knowledge chunks from {KNOWLEDGE_BASE_DIR}")
    return chunks


def _doc_to_chunk_text(doc: dict, source: str) -> Optional[str]:
    """Convert a knowledge-base document to a searchable text chunk."""
    parts: List[str] = []

    if source == "indian_groceries":
        parts.append(f"Product: {doc.get('name_en', '')} ({doc.get('name_hi', '')})")
        parts.append(f"Category: {doc.get('category', '')}")
        if doc.get("aliases"):
            parts.append(f"Also known as: {', '.join(doc['aliases'])}")
        if doc.get("description"):
            parts.append(f"Description: {doc['description']}")
        if doc.get("typical_price_range"):
            parts.append(f"Price range: {doc['typical_price_range']}")
        if doc.get("storage_tip"):
            parts.append(f"Storage: {doc['storage_tip']}")
        if doc.get("nutritional_info"):
            parts.append(f"Nutrition: {doc['nutritional_info']}")
        if doc.get("common_brands"):
            parts.append(f"Brands: {', '.join(doc['common_brands'])}")
        if doc.get("substitutes"):
            parts.append(f"Substitutes: {', '.join(doc['substitutes'])}")
        if doc.get("platforms_available"):
            parts.append(f"Available on: {', '.join(doc['platforms_available'])}")

    elif source == "gangu_features":
        parts.append(f"Topic: {doc.get('topic', '')}")
        parts.append(f"Question: {doc.get('question', '')}")
        parts.append(f"Answer (Hindi): {doc.get('answer', '')}")
        parts.append(f"Answer (English): {doc.get('answer_en', '')}")
        if doc.get("tags"):
            parts.append(f"Tags: {', '.join(doc['tags'])}")

    else:
        # Generic fallback
        for key, value in doc.items():
            if isinstance(value, str):
                parts.append(f"{key}: {value}")
            elif isinstance(value, list):
                parts.append(f"{key}: {', '.join(str(v) for v in value)}")

    return "\n".join(parts) if parts else None


def _mapping_to_chunk_text(section_key: str, section_val: Any, source: str) -> Optional[str]:
    """Convert mapping-style data (dict of translations, patterns) into text chunks."""
    parts: List[str] = []

    if section_key == "hindi_to_english" and isinstance(section_val, dict):
        parts.append("Hindi to English Grocery Translations:")
        for hi, en in list(section_val.items())[:40]:  # cap for chunk size
            parts.append(f"  {hi} = {en}")

    elif section_key == "indirect_speech_patterns" and isinstance(section_val, dict):
        parts.append("Indirect Speech Patterns (Elderly Indian users):")
        for phrase, info in section_val.items():
            meaning = info.get("meaning", "")
            urgency = info.get("urgency", "")
            explanation = info.get("explanation", "")
            parts.append(f"  '{phrase}' → {meaning} (urgency: {urgency}) — {explanation}")

    elif section_key == "quantity_defaults" and isinstance(section_val, dict):
        parts.append("Default Quantities for Common Items:")
        for item, qty in section_val.items():
            parts.append(f"  {item}: {qty}")

    elif section_key == "category_keywords" and isinstance(section_val, dict):
        parts.append("Category Keywords for Intent Detection:")
        for cat, keywords in section_val.items():
            parts.append(f"  {cat}: {', '.join(keywords)}")

    else:
        # Generic dict → text
        parts.append(f"{section_key}:")
        if isinstance(section_val, dict):
            for k, v in list(section_val.items())[:30]:
                parts.append(f"  {k}: {v}")
        elif isinstance(section_val, list):
            for item in section_val[:20]:
                parts.append(f"  - {item}")
        else:
            parts.append(f"  {section_val}")

    return "\n".join(parts) if parts else None


# ─────────────────── EMBEDDING ENGINE ─────────────────── #


def _compute_content_hash(chunks: List[Dict]) -> str:
    """Hash all chunk texts to detect when knowledge base changes."""
    combined = "||".join(c["text"] for c in chunks)
    return hashlib.sha256(combined.encode()).hexdigest()[:16]


def embed_texts(texts: List[str], task_type: str = "RETRIEVAL_DOCUMENT") -> np.ndarray:
    """
    Embed a list of texts using Gemini Embedding API.
    Returns numpy array of shape (len(texts), embedding_dim).
    """
    embeddings = []
    batch_size = 20  # Gemini embedding batch limit

    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        try:
            result = client.models.embed_content(
                model=EMBEDDING_MODEL,
                contents=batch,
                config={
                    "task_type": task_type,
                }
            )
            for emb in result.embeddings:
                embeddings.append(emb.values)
        except Exception as e:
            print(f"  ⚠️ Embedding batch {i // batch_size} failed: {e}")
            # Fill with zero vectors as fallback
            dim = embeddings[0].shape[0] if embeddings else 768
            for _ in batch:
                embeddings.append(np.zeros(dim))

    return np.array(embeddings, dtype=np.float32)


def embed_query(text: str) -> np.ndarray:
    """Embed a single query text."""
    try:
        result = client.models.embed_content(
            model=EMBEDDING_MODEL,
            contents=[text],
            config={
                "task_type": "RETRIEVAL_QUERY",
            }
        )
        return np.array(result.embeddings[0].values, dtype=np.float32)
    except Exception as e:
        print(f"  ⚠️ Query embedding failed: {e}")
        return np.zeros(768, dtype=np.float32)


# ─────────────────── VECTOR STORE (numpy) ─────────────────── #


class SimpleVectorStore:
    """
    Lightweight in-memory vector store using numpy cosine similarity.
    Caches embeddings to disk so re-embedding is only done when knowledge base changes.
    """

    def __init__(self):
        self.chunks: List[Dict] = []
        self.embeddings: Optional[np.ndarray] = None  # (n_chunks, dim)
        self._content_hash: str = ""

    def build(self, chunks: List[Dict], force_rebuild: bool = False) -> None:
        """Build or load cached vector store."""
        self.chunks = chunks
        current_hash = _compute_content_hash(chunks)

        # Try loading cache
        if not force_rebuild and EMBEDDING_CACHE_PATH.exists():
            try:
                with open(EMBEDDING_CACHE_PATH, "rb") as f:
                    cache = pickle.load(f)
                if cache.get("hash") == current_hash:
                    self.embeddings = cache["embeddings"]
                    self._content_hash = current_hash
                    print(f"  ⚡ Loaded embedding cache ({len(chunks)} chunks)")
                    return
            except Exception as e:
                print(f"  ⚠️ Cache load failed: {e}")

        # Embed all chunks
        print(f"  🔄 Embedding {len(chunks)} knowledge chunks...")
        texts = [c["text"] for c in chunks]
        self.embeddings = embed_texts(texts)
        self._content_hash = current_hash

        # Save cache
        try:
            with open(EMBEDDING_CACHE_PATH, "wb") as f:
                pickle.dump({"hash": current_hash, "embeddings": self.embeddings}, f)
            print(f"  💾 Saved embedding cache")
        except Exception as e:
            print(f"  ⚠️ Cache save failed: {e}")

    def search(self, query: str, top_k: int = TOP_K) -> List[Tuple[Dict, float]]:
        """
        Search for most relevant chunks using cosine similarity.

        Returns:
            List of (chunk_dict, similarity_score) sorted by relevance.
        """
        if self.embeddings is None or len(self.chunks) == 0:
            return []

        query_emb = embed_query(query)

        # Cosine similarity
        norms = np.linalg.norm(self.embeddings, axis=1) * np.linalg.norm(query_emb)
        norms = np.where(norms == 0, 1e-10, norms)  # avoid division by zero
        similarities = np.dot(self.embeddings, query_emb) / norms

        # Top-k indices
        top_indices = np.argsort(similarities)[::-1][:top_k]

        results = []
        for idx in top_indices:
            score = float(similarities[idx])
            if score > 0.1:  # minimum relevance threshold
                results.append((self.chunks[idx], score))

        return results


# ─────────────────── RAG GENERATOR ─────────────────── #

RAG_SYSTEM_PROMPT = """
You are the **Query Info Agent** of GANGU — an AI grocery assistant for elderly Indian users.

## YOUR ROLE
You answer informational queries using the RETRIEVED CONTEXT provided below.
You are NOT a purchase agent. You provide helpful knowledge and guidance.

## RULES
1. Answer primarily in Hindi/Hinglish (mix Hindi+English naturally) — this is for elderly Indian users
2. If the user asked in English, respond in English but keep it simple
3. Use ONLY the retrieved context to answer. If context is insufficient, say so politely
4. Be warm, respectful, and helpful — like talking to a family elder
5. If the query is about a product: share price range, storage tips, substitutes, brands
6. If the query is about GANGU features: explain simply how to use the feature
7. If the user's meaning is unclear: gently ask for clarification in Hindi
8. Keep answers concise but complete — elderly users prefer clear, direct answers
9. Use bullet points or numbered lists for multi-part answers
10. If the user seems to want to BUY something, suggest they say "order karo" or "mangao"

## FORMAT
- Respond naturally in Hindi/Hinglish (or English if user asked in English)
- No JSON output — plain text response
- No technical jargon
- Include relevant emojis sparingly for visual clarity

## SPECIAL CASES
- If user asks "yeh kya hota hai" (what is this) → explain the item from knowledge base
- If user asks for alternatives → list substitutes and explain differences
- If user asks about storage → give storage tips in simple language
- If user asks about nutrition → share nutritional info simply
- If user asks about GANGU itself → explain the feature warmly
- If nothing relevant found → say "Maaf kijiye, is baare mein mere paas jankari nahi hai. Kya aap thoda aur bata sakte hain?"
"""


def generate_rag_response(
    query: str,
    retrieved_chunks: List[Tuple[Dict, float]],
    language_hint: str = "hinglish",
) -> str:
    """
    Generate a response using retrieved context + Gemini.

    Args:
        query: The user's original query
        retrieved_chunks: List of (chunk, score) from vector search
        language_hint: Detected language preference

    Returns:
        Natural language response string
    """
    # Build context from retrieved chunks
    context_parts = []
    for i, (chunk, score) in enumerate(retrieved_chunks, 1):
        context_parts.append(f"--- Retrieved Context #{i} (relevance: {score:.2f}) ---")
        context_parts.append(chunk["text"])
        context_parts.append(f"Source: {chunk['source']}")
        context_parts.append("")

    context_text = "\n".join(context_parts) if context_parts else "No relevant context found in knowledge base."

    # Build the prompt
    user_prompt = f"""
## RETRIEVED CONTEXT
{context_text}

## USER QUERY
"{query}"

## LANGUAGE PREFERENCE
{language_hint}

Now respond to the user's query using the retrieved context above.
"""

    try:
        response = client.models.generate_content(
            model=GENERATION_MODEL,
            contents=[
                {"role": "user", "parts": [{"text": RAG_SYSTEM_PROMPT}]},
                {"role": "model", "parts": [{"text": "Samajh gaya. Main Query Info Agent hoon. Retrieved context ke basis par user ko respectfully jawab dunga Hindi/Hinglish mein."}]},
                {"role": "user", "parts": [{"text": user_prompt}]},
            ],
            config={
                "temperature": 0.4,
                "top_p": 0.9,
                "max_output_tokens": 1024,
            },
        )
        return response.text.strip()

    except Exception as e:
        print(f"  ❌ RAG generation failed: {e}")
        return "Maaf kijiye, abhi jawab dene mein dikkat aa rahi hai. Kya aap thodi der baad phir try karenge?"


# ─────────────────── MAIN AGENT CLASS ─────────────────── #


class QueryInfoAgent:
    """
    RAG-based Query Info Agent for GANGU.

    Usage:
        agent = QueryInfoAgent()
        agent.initialize()  # loads KB + builds vectors
        result = agent.answer("haldi kya hoti hai?")
    """

    def __init__(self):
        self.vector_store = SimpleVectorStore()
        self._initialized = False

    def initialize(self, force_rebuild: bool = False) -> None:
        """Load knowledge base and build vector store."""
        print("\n📚 [Query Info Agent] Initializing RAG system...")
        chunks = load_knowledge_base()
        if not chunks:
            print("  ⚠️ No knowledge chunks loaded. RAG will have limited capability.")
        self.vector_store.build(chunks, force_rebuild=force_rebuild)
        self._initialized = True
        print(f"  ✅ RAG system ready with {len(chunks)} knowledge chunks")

    def answer(self, query: str, language_hint: str = "hinglish") -> Dict[str, Any]:
        """
        Answer a user query using RAG.

        Args:
            query: User's question/query text
            language_hint: Detected language (hindi/english/hinglish)

        Returns:
            Dict with response, retrieved sources, and metadata
        """
        if not self._initialized:
            self.initialize()

        start_time = time.time()

        # Step 1: Retrieve relevant chunks
        retrieved = self.vector_store.search(query, top_k=TOP_K)

        # Step 2: Generate response
        response_text = generate_rag_response(query, retrieved, language_hint)

        elapsed = time.time() - start_time

        # Step 3: Build result
        sources = []
        for chunk, score in retrieved:
            sources.append({
                "id": chunk["id"],
                "source": chunk["source"],
                "relevance": round(score, 3),
                "preview": chunk["text"][:150] + "..." if len(chunk["text"]) > 150 else chunk["text"],
            })

        return {
            "status": "success",
            "response": response_text,
            "query": query,
            "language": language_hint,
            "sources_used": len(sources),
            "sources": sources,
            "retrieval_time_ms": round(elapsed * 1000, 1),
            "timestamp": datetime.now().isoformat(),
            "agent": "query_info_agent",
            "method": "rag",
        }

    def search_only(self, query: str, top_k: int = 5) -> List[Dict]:
        """Search knowledge base without generating a response. Useful for debugging."""
        if not self._initialized:
            self.initialize()
        results = self.vector_store.search(query, top_k=top_k)
        return [
            {"id": c["id"], "source": c["source"], "score": round(s, 3), "text": c["text"]}
            for c, s in results
        ]


# ─────────────────── SINGLETON INSTANCE ─────────────────── #

_agent_instance: Optional[QueryInfoAgent] = None


def get_agent() -> QueryInfoAgent:
    """Get or create the singleton QueryInfoAgent."""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = QueryInfoAgent()
        _agent_instance.initialize()
    return _agent_instance


# ─────────────────── PUBLIC API (for orchestration) ─────────────────── #


def query_info(query: str, language_hint: str = "hinglish") -> Dict[str, Any]:
    """
    Main entry point called by the orchestration layer.

    Args:
        query: User's question
        language_hint: Detected language

    Returns:
        Dict with response and metadata
    """
    agent = get_agent()
    return agent.answer(query, language_hint)


# ─────────────────── CLI INTERACTIVE MODE ─────────────────── #

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════╗
║        📚 GANGU - Query Info Agent (RAG)                     ║
║        ─────────────────────────────────────────             ║
║        Knowledge-powered answers for Indian groceries        ║
║        Supports: Hindi | English | Hinglish                  ║
╚══════════════════════════════════════════════════════════════╝
    """)

    agent = QueryInfoAgent()
    agent.initialize()

    print("\n🚀 Interactive Mode — Ask anything about groceries or GANGU!")
    print("(Type 'quit' or 'exit' to stop)\n")

    while True:
        try:
            user_input = input("🗣️  You: ").strip()

            if not user_input:
                continue

            if user_input.lower() in ["quit", "exit", "q", "bye"]:
                print("\n👋 Namaste! GANGU Query Info Agent signing off.")
                break

            result = agent.answer(user_input)

            print(f"\n🤖 GANGU: {result['response']}")
            print(f"\n   📎 Sources: {result['sources_used']} chunks | ⏱️  {result['retrieval_time_ms']}ms")
            for src in result["sources"]:
                print(f"      ↳ [{src['source']}] {src['id']} (relevance: {src['relevance']})")
            print()

        except KeyboardInterrupt:
            print("\n\n👋 Namaste! GANGU Query Info Agent signing off.")
            break
        except Exception as e:
            print(f"   ❌ Error: {e}")
