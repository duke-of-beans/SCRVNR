"""
Retrieval System Tier 1 — SCRVNR v2.0 Subsystem 3 (RETRIEVE)

Before generating, selects corpus examples most likely to produce
high-quality personalized output when injected as few-shot context.

Research basis:
    PEARL (Microsoft, ACL 2024): Generation-calibrated retrieval
    dramatically outperforms random or topic-matched retrieval.

Tier 1 uses embedding similarity via nomic-embed-text (same infrastructure
as brain.db). Register-scoped first, topic-keyed second.

Usage:
    from core.retrieval import VoiceRetriever
    ret = VoiceRetriever()

    # Index the corpus (one-time, or after new intake)
    ret.build_index()

    # Retrieve examples for a generation prompt
    examples = ret.retrieve("check the websocket endpoint config", register='TECH', k=3)

    # Format for prompt injection
    context = ret.format_for_prompt(examples, register='TECH')
"""

import hashlib
import json
import os
import re
import sqlite3
import struct
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


# Ollama embedding endpoint (same as brain.db infrastructure)
OLLAMA_URL = "http://localhost:11434/api/embed"
EMBED_MODEL = "nomic-embed-text"
EMBED_DIM = 768

# Retrieval parameters
DEFAULT_K = 3
MAX_K = 5
MIN_SIMILARITY = 0.3
MIN_EXAMPLE_WORDS = 10
MAX_EXAMPLE_WORDS = 200
MAX_TOTAL_EXAMPLE_WORDS = 500

# Word tokenizer
WORD_PATTERN = re.compile(r"[a-zA-Z']+")


def _cosine_similarity(a: List[float], b: List[float]) -> float:
    """Compute cosine similarity between two vectors."""
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(x * x for x in b) ** 0.5
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def _embed_text(text: str) -> Optional[List[float]]:
    """Get embedding from Ollama. Returns None if unavailable."""
    if not HAS_REQUESTS:
        return None
    try:
        resp = requests.post(OLLAMA_URL, json={
            "model": EMBED_MODEL,
            "input": text
        }, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            embeddings = data.get("embeddings", [])
            if embeddings:
                return embeddings[0]
        return None
    except Exception:
        return None


def _pack_embedding(vec: List[float]) -> bytes:
    """Pack embedding vector as binary for SQLite storage."""
    return struct.pack(f'{len(vec)}f', *vec)


def _unpack_embedding(blob: bytes) -> List[float]:
    """Unpack binary embedding from SQLite."""
    count = len(blob) // 4
    return list(struct.unpack(f'{count}f', blob))


class VoiceRetriever:
    """Retrieve voice examples for generation prompt injection."""

    def __init__(self, db_path: str = None, corpus_path: str = None):
        project_root = Path(__file__).parent.parent

        if db_path is None:
            db_path = str(project_root / 'learning' / 'voice.db')
        if corpus_path is None:
            corpus_path = str(project_root / 'research' / 'voice_fingerprint' / 'final_corpus.jsonl')

        self.db_path = db_path
        self.corpus_path = corpus_path
        self._ollama_available = None

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _check_ollama(self) -> bool:
        """Check if Ollama is running and nomic-embed-text is available."""
        if self._ollama_available is not None:
            return self._ollama_available

        test = _embed_text("test")
        self._ollama_available = test is not None
        return self._ollama_available

    def _ensure_table(self, conn: sqlite3.Connection):
        """Create the corpus_embeddings table if it doesn't exist."""
        conn.execute("""
        CREATE TABLE IF NOT EXISTS corpus_embeddings (
            msg_id TEXT PRIMARY KEY,
            register TEXT,
            text_preview TEXT,
            word_count INTEGER,
            embedding BLOB,
            indexed_at TEXT DEFAULT (datetime('now'))
        )
        """)
        conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_ce_register
        ON corpus_embeddings(register)
        """)
        conn.commit()

    # ------------------------------------------------------------------
    # Index building
    # ------------------------------------------------------------------

    def build_index(self, max_messages: int = 5000,
                     registers: List[str] = None,
                     force: bool = False) -> Dict:
        """
        Build embedding index from corpus JSONL.

        Reads final_corpus.jsonl, filters by register and word count,
        embeds with nomic-embed-text, stores in corpus_embeddings table.

        Args:
            max_messages: Max messages to index (per register)
            registers: Which registers to index, or None for all
            force: Re-index even if embeddings exist

        Returns:
            Stats dict
        """
        if not self._check_ollama():
            return {"error": "Ollama not available", "indexed": 0}

        if not os.path.exists(self.corpus_path):
            return {"error": f"Corpus not found: {self.corpus_path}", "indexed": 0}

        conn = self._get_conn()
        self._ensure_table(conn)

        try:
            cur = conn.cursor()

            # Check existing count
            if not force:
                cur.execute("SELECT COUNT(*) FROM corpus_embeddings")
                existing = cur.fetchone()[0]
                if existing > 0:
                    return {"status": "already_indexed", "count": existing}

            # Read corpus and filter
            messages_by_register = {}
            with open(self.corpus_path, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        msg = json.loads(line.strip())
                    except json.JSONDecodeError:
                        continue

                    register = msg.get('register', 'UNTAGGED')
                    if registers and register not in registers:
                        continue
                    if register == 'UNTAGGED':
                        continue

                    text = msg.get('text', '')
                    words = len(WORD_PATTERN.findall(text))

                    if words < MIN_EXAMPLE_WORDS or words > MAX_EXAMPLE_WORDS:
                        continue

                    if register not in messages_by_register:
                        messages_by_register[register] = []

                    if len(messages_by_register[register]) < max_messages:
                        messages_by_register[register].append({
                            'msg_id': msg.get('msg_id', hashlib.md5(text.encode()).hexdigest()[:12]),
                            'register': register,
                            'text': text,
                            'word_count': words,
                        })

            # Embed and store
            total_indexed = 0
            for register, messages in messages_by_register.items():
                for msg in messages:
                    embedding = _embed_text(msg['text'])
                    if embedding is None:
                        continue

                    cur.execute("""
                    INSERT OR REPLACE INTO corpus_embeddings
                    (msg_id, register, text_preview, word_count, embedding)
                    VALUES (?,?,?,?,?)
                    """, (
                        msg['msg_id'],
                        msg['register'],
                        msg['text'][:500],  # preview
                        msg['word_count'],
                        _pack_embedding(embedding),
                    ))
                    total_indexed += 1

                    # Batch commit every 100
                    if total_indexed % 100 == 0:
                        conn.commit()

            conn.commit()

            # Update schema version
            cur.execute("""
            INSERT OR IGNORE INTO schema_version (version, description)
            VALUES ('3.1.0', 'v2.0 Sprint V2-03: corpus_embeddings table')
            """)
            conn.commit()

            return {
                "status": "indexed",
                "total": total_indexed,
                "by_register": {r: len(msgs) for r, msgs in messages_by_register.items()}
            }
        finally:
            conn.close()

    def get_index_stats(self) -> Dict:
        """Get statistics about the current index."""
        conn = self._get_conn()
        try:
            self._ensure_table(conn)
            cur = conn.cursor()

            cur.execute("SELECT COUNT(*) FROM corpus_embeddings")
            total = cur.fetchone()[0]

            cur.execute("""
            SELECT register, COUNT(*) as cnt
            FROM corpus_embeddings
            GROUP BY register
            ORDER BY cnt DESC
            """)
            by_register = {row['register']: row['cnt'] for row in cur.fetchall()}

            return {
                "total_indexed": total,
                "by_register": by_register,
                "ollama_available": self._check_ollama(),
            }
        finally:
            conn.close()

    # ------------------------------------------------------------------
    # Retrieval
    # ------------------------------------------------------------------

    def retrieve(self, prompt: str, register: str = 'TECH',
                  k: int = DEFAULT_K,
                  include_corrections: bool = True) -> List[Dict]:
        """
        Retrieve the k most similar corpus examples for a generation prompt.

        Register-scoped first: only retrieves from the target register.

        Args:
            prompt: The generation prompt text
            register: Target register
            k: Number of examples to retrieve
            include_corrections: Whether to include correction pair examples

        Returns:
            List of {'text': str, 'similarity': float, 'register': str, 'source': str}
        """
        k = min(k, MAX_K)

        if not self._check_ollama():
            return self._fallback_retrieve(prompt, register, k)

        # Embed the prompt
        prompt_embedding = _embed_text(prompt)
        if prompt_embedding is None:
            return self._fallback_retrieve(prompt, register, k)

        conn = self._get_conn()
        try:
            self._ensure_table(conn)
            cur = conn.cursor()

            # Load all embeddings for the target register
            cur.execute("""
            SELECT msg_id, register, text_preview, word_count, embedding
            FROM corpus_embeddings
            WHERE register = ?
            """, (register,))

            candidates = []
            for row in cur.fetchall():
                if row['embedding'] is None:
                    continue
                vec = _unpack_embedding(row['embedding'])
                sim = _cosine_similarity(prompt_embedding, vec)
                if sim >= MIN_SIMILARITY:
                    candidates.append({
                        'text': row['text_preview'],
                        'similarity': round(sim, 4),
                        'register': row['register'],
                        'word_count': row['word_count'],
                        'source': 'corpus',
                        'msg_id': row['msg_id'],
                    })

            # Sort by similarity descending
            candidates.sort(key=lambda x: x['similarity'], reverse=True)

            results = candidates[:k]

            # Optionally include correction pair examples
            if include_corrections and len(results) < k:
                corrections = self._retrieve_corrections(prompt_embedding, register, k - len(results))
                results.extend(corrections)

            return results
        finally:
            conn.close()

    def _retrieve_corrections(self, prompt_embedding: List[float],
                                register: str, k: int) -> List[Dict]:
        """Retrieve relevant correction pairs as examples."""
        conn = self._get_conn()
        try:
            cur = conn.cursor()
            cur.execute("""
            SELECT corrected_text, register
            FROM correction_pairs
            WHERE register = ?
            ORDER BY timestamp DESC
            LIMIT 20
            """, (register,))

            candidates = []
            for row in cur.fetchall():
                text = row['corrected_text']
                if not text or len(text) < 20:
                    continue

                emb = _embed_text(text)
                if emb is None:
                    continue

                sim = _cosine_similarity(prompt_embedding, emb)
                if sim >= MIN_SIMILARITY:
                    candidates.append({
                        'text': text,
                        'similarity': round(sim, 4),
                        'register': row['register'],
                        'word_count': len(WORD_PATTERN.findall(text)),
                        'source': 'correction',
                    })

            candidates.sort(key=lambda x: x['similarity'], reverse=True)
            return candidates[:k]
        except sqlite3.OperationalError:
            return []
        finally:
            conn.close()

    def _fallback_retrieve(self, prompt: str, register: str, k: int) -> List[Dict]:
        """
        Fallback retrieval when Ollama is unavailable.
        Uses keyword overlap instead of embeddings.
        """
        if not os.path.exists(self.corpus_path):
            return []

        prompt_words = set(w.lower() for w in WORD_PATTERN.findall(prompt) if len(w) > 2)
        if not prompt_words:
            return []

        candidates = []
        with open(self.corpus_path, 'r', encoding='utf-8') as f:
            count = 0
            for line in f:
                if count > 10000:
                    break
                count += 1

                try:
                    msg = json.loads(line.strip())
                except json.JSONDecodeError:
                    continue

                if msg.get('register') != register:
                    continue

                text = msg.get('text', '')
                words = len(WORD_PATTERN.findall(text))
                if words < MIN_EXAMPLE_WORDS or words > MAX_EXAMPLE_WORDS:
                    continue

                msg_words = set(w.lower() for w in WORD_PATTERN.findall(text) if len(w) > 2)
                overlap = len(prompt_words & msg_words)
                if overlap > 0:
                    candidates.append({
                        'text': text[:500],
                        'similarity': round(overlap / max(len(prompt_words), 1), 4),
                        'register': register,
                        'word_count': words,
                        'source': 'fallback_keyword',
                    })

        candidates.sort(key=lambda x: x['similarity'], reverse=True)
        return candidates[:k]

    # ------------------------------------------------------------------
    # Prompt formatting
    # ------------------------------------------------------------------

    def format_for_prompt(self, examples: List[Dict],
                           register: str = 'TECH',
                           voice_description: str = None) -> str:
        """
        Format retrieved examples for injection into a generation prompt.

        Args:
            examples: Retrieved examples from retrieve()
            register: Target register
            voice_description: Register-specific voice description text

        Returns:
            Formatted string ready for prompt injection
        """
        if not examples:
            return ""

        parts = [f'<voice_examples register="{register}">']
        parts.append(f"David's actual writing in this register:")
        parts.append("")

        total_words = 0
        for i, ex in enumerate(examples, 1):
            text = ex['text']
            words = ex.get('word_count', len(WORD_PATTERN.findall(text)))

            if total_words + words > MAX_TOTAL_EXAMPLE_WORDS:
                break

            source_tag = f" [{ex['source']}]" if ex.get('source') == 'correction' else ""
            parts.append(f'Example {i}{source_tag}:')
            parts.append(f'"{text}"')
            parts.append("")
            total_words += words

        parts.append("</voice_examples>")

        if voice_description:
            parts.append("")
            parts.append("<voice_description>")
            parts.append(voice_description)
            parts.append("</voice_description>")

        return '\n'.join(parts)

    def retrieve_and_format(self, prompt: str, register: str = 'TECH',
                              k: int = DEFAULT_K,
                              voice_description: str = None) -> str:
        """
        Convenience: retrieve examples and format for prompt injection.
        """
        examples = self.retrieve(prompt, register, k)
        return self.format_for_prompt(examples, register, voice_description)


if __name__ == "__main__":
    ret = VoiceRetriever()
    print("VoiceRetriever initialized")
    print(f"  DB: {ret.db_path}")
    print(f"  Corpus: {ret.corpus_path}")
    print(f"  Ollama: {'available' if ret._check_ollama() else 'NOT available'}")

    stats = ret.get_index_stats()
    print(f"\nIndex stats: {stats}")

    if stats['total_indexed'] == 0 and stats['ollama_available']:
        print("\nBuilding index (this may take a few minutes)...")
        result = ret.build_index(max_messages=500)
        print(f"  Result: {result}")
    elif stats['total_indexed'] > 0:
        print(f"\nTesting retrieval...")
        examples = ret.retrieve("check the websocket endpoint config", register='TECH', k=3)
        print(f"  Retrieved: {len(examples)} examples")
        for ex in examples:
            print(f"    [{ex['similarity']:.3f}] ({ex['word_count']}w) {ex['text'][:80]}...")

        formatted = ret.format_for_prompt(examples, register='TECH')
        print(f"\n  Formatted prompt context: {len(formatted)} chars")
