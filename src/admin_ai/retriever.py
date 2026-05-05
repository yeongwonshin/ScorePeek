from __future__ import annotations

from dataclasses import asdict

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .document_loader import DocumentChunk


class LocalRetriever:
    """Small local retriever for demo RAG.

    It uses TF-IDF, so it runs without external embedding APIs. For production,
    replace this class with OpenAI embeddings, bge-m3, or other multilingual embeddings.
    """

    def __init__(self, chunks: list[DocumentChunk]):
        self.chunks = chunks
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=1)
        corpus = [chunk.text for chunk in chunks] or [""]
        self.matrix = self.vectorizer.fit_transform(corpus)

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        if not self.chunks:
            return []
        query_vector = self.vectorizer.transform([query])
        scores = cosine_similarity(query_vector, self.matrix).flatten()
        ranked = scores.argsort()[::-1][:top_k]
        results: list[dict] = []
        for rank in ranked:
            score = float(scores[rank])
            if score <= 0:
                continue
            item = asdict(self.chunks[int(rank)])
            item["score"] = round(score, 4)
            results.append(item)
        if not results:
            # Fallback: return first few chunks so the answer still shows grounding.
            for chunk in self.chunks[:top_k]:
                item = asdict(chunk)
                item["score"] = 0.0
                results.append(item)
        return results
