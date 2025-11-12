# telugu_engine/suggest_sentence.py
from __future__ import annotations
from typing import List, Tuple
from .suggest import suggestions as word_suggestions

def per_token_suggestions(text: str, limit: int = 6) -> List[List[str]]:
    tokens = [t for t in (text or "").strip().split() if t]
    return [word_suggestions(t, limit=limit) for t in tokens]

def sentence_variants(text: str, topn: int = 5, per_word: int = 4, beam: int = 6) -> List[str]:
    """
    Produce top-N Telugu sentence variants from a Roman sentence using a tiny beam search.
    """
    tokens = [t for t in (text or "").strip().split() if t]
    if not tokens:
        return []

    beams: List[Tuple[str, int]] = [("", 0)]  # (assembled, score)

    for tok in tokens:
        cands = word_suggestions(tok, limit=per_word)
        if not cands:
            cands = [tok]  # fallback

        next_beams: List[Tuple[str, int]] = []
        for sent, sc in beams:
            for w in cands:
                bonus = -1 if any(ch in w for ch in "ళఋృషఠఢ") else 0
                next_beams.append((f"{sent} {w}".strip(), sc + len(w) - bonus))

        next_beams.sort(key=lambda x: x[1])
        beams = next_beams[:max(beam, topn)]

    beams.sort(key=lambda x: x[1])
    return [s for s, _ in beams[:topn]]