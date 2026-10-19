"""Local knowledge base store backed by Chroma."""

from __future__ import annotations

from typing import Any

from agentic_ai.environment.stores.config import StoreConfig, load_store_config


class KnowledgeBaseStore:
    """Read/write interface over data/knowledge_base via Chroma."""

    def __init__(self, config: StoreConfig | None = None) -> None:
        self.config = config or load_store_config("knowledge_base")
        self.config.path.mkdir(parents=True, exist_ok=True)
        self._client = None
        self._collection = None

    def _get_collection(self):
        if self._collection is not None:
            return self._collection
        import chromadb
        from chromadb.utils import embedding_functions

        self._client = chromadb.PersistentClient(path=str(self.config.path))
        # Built-in ONNX MiniLM — no PyTorch / sentence-transformers required
        ef = embedding_functions.DefaultEmbeddingFunction()
        self._collection = self._client.get_or_create_collection(
            name=self.config.collection,
            metadata={"hnsw:space": "cosine"},
            embedding_function=ef,
        )
        return self._collection

    def index(self, document_id: str, payload: dict[str, Any]) -> None:
        text = str(payload.get("text") or "")
        if not text.strip():
            raise ValueError(f"Cannot index empty text for {document_id}")
        metadata = {
            str(k): (v if isinstance(v, (str, int, float, bool)) else str(v))
            for k, v in (payload.get("metadata") or {}).items()
        }
        metadata.setdefault("source", str(payload.get("source", "")))
        collection = self._get_collection()
        collection.upsert(
            ids=[document_id],
            documents=[text],
            metadatas=[metadata],
        )

    def get(self, document_id: str) -> dict[str, Any] | None:
        collection = self._get_collection()
        result = collection.get(ids=[document_id], include=["documents", "metadatas"])
        if not result["ids"]:
            return None
        return {
            "id": result["ids"][0],
            "text": (result["documents"] or [""])[0],
            "metadata": (result["metadatas"] or [{}])[0],
        }

    def query(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """Return ranked hits: id, score, snippet, metadata."""
        collection = self._get_collection()
        if collection.count() == 0:
            return []
        result = collection.query(
            query_texts=[query],
            n_results=min(top_k, collection.count()),
            include=["documents", "metadatas", "distances"],
        )
        hits: list[dict[str, Any]] = []
        ids = (result.get("ids") or [[]])[0]
        docs = (result.get("documents") or [[]])[0]
        metas = (result.get("metadatas") or [[]])[0]
        distances = (result.get("distances") or [[]])[0]
        for doc_id, doc, meta, distance in zip(ids, docs, metas, distances):
            score = max(0.0, 1.0 - float(distance))
            snippet = (doc or "")[:400]
            hits.append(
                {
                    "id": doc_id,
                    "score": score,
                    "snippet": snippet,
                    "metadata": meta or {},
                }
            )
        return hits
