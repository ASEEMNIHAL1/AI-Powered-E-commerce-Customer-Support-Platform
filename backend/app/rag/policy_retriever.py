"""
Policy retrieval using TF-IDF keyword search over the local return_policy.md.
No paid vector DB required. The policy file is inspectable at backend/policies/return_policy.md.
"""
import re
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

POLICY_PATH = Path(__file__).parent.parent.parent / "policies" / "return_policy.md"


def _load_sections() -> list[tuple[str, str]]:
    """Split policy into sections by ## headings."""
    text = POLICY_PATH.read_text(encoding="utf-8")
    sections = re.split(r"\n## ", text)
    result = []
    for section in sections:
        lines = section.strip().splitlines()
        if lines:
            title = lines[0].lstrip("# ").strip()
            body = "\n".join(lines).strip()
            result.append((title, body))
    return result


_SECTIONS = _load_sections()
_TEXTS = [f"{t}\n{b}" for t, b in _SECTIONS]
_VECTORIZER = TfidfVectorizer(stop_words="english")
_MATRIX = _VECTORIZER.fit_transform(_TEXTS)


def search_return_policy(query: str, top_k: int = 3) -> str:
    """
    Retrieve the most relevant policy sections for the given query.
    Returns combined text of top_k sections.
    """
    query_vec = _VECTORIZER.transform([query])
    scores = cosine_similarity(query_vec, _MATRIX).flatten()
    top_indices = np.argsort(scores)[::-1][:top_k]

    results = []
    for idx in top_indices:
        if scores[idx] > 0.01:  # relevance threshold
            title, body = _SECTIONS[idx]
            results.append(f"### {title}\n{body}")

    if not results:
        return "No specific policy found for this query. Please contact support for assistance."

    return "\n\n---\n\n".join(results)
