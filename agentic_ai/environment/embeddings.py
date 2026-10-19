"""Embedding helpers.

The knowledge base uses Chroma's DefaultEmbeddingFunction (ONNX MiniLM).
This module is kept as a thin note for future custom embedders.
"""

from __future__ import annotations


def describe_default() -> str:
    return "chromadb.utils.embedding_functions.DefaultEmbeddingFunction"
