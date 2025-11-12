from __future__ import annotations
from typing import List, Callable

# Load both transliterators (standard + legacy), but don't crash if legacy is missing
try:
    from .transliterator import eng_to_telugu as _std_eng_to_te
except Exception:
    # fallback name if module is at top-level
    from transliterator import eng_to_telugu as _std_eng_to_te

try:
    from .transliterator_v4_3_0 import eng_to_telugu as _legacy_eng_to_te
    _HAS_LEGACY = True
except Exception:
    try:
        from transliterator_v4_3_0 import eng_to_telugu as _legacy_eng_to_te
        _HAS_LEGACY = True
    except Exception:
        _HAS_LEGACY = False


def _roman_variants(w: str) -> List[str]:
    """
    Generate a small set of Roman phonetic alternates that often map to
    valid alternative Telugu spellings (IME-like).
    Keep simple & deterministic.
    """
    w = (w or "").strip()
    if not w:
        return []

    c = {w}

    # Vowel-length hypotheses (a↔aa, e↔ee, i↔ii, o↔oo, u↔uu)
    for v in "aeiou":
        c.add(w.replace(v, v * 2))
        c.add(w.replace(v * 2, v))

    # ch ↔ chh; also try plain 'c' once
    if "ch" in w:
        c.add(w.replace("ch", "chh"))
        c.add(w.replace("ch", "c"))
    elif "c" in w:
        c.add(w.replace("c", "ch"))

    # Retroflex L hypothesis
    if "l" in w:
        c.add(w.replace("l", "L"))

    # 'ri' kept (C+ri → ṛ matra handled by transliterator)
    if "ri" in w:
        c.add(w)  # no-op but keeps the case in the set

    # Sanskritic clusters commonly seen
    for pat in ("str", "shna", "ksha"):
        if pat in w:
            c.add(w)  # ensure base form is considered

    # Return unique, non-empty
    return [x for x in c if x]


def _fanout(roman: str) -> List[str]:
    """Run through both engines and collect unique Telugu outputs."""
    outs = set()
    def _run(fn: Callable[[str], str]) -> None:
        try:
            s = fn(roman)
            if s:
                outs.add(s)
        except Exception:
            pass

    _run(_std_eng_to_te)
    if _HAS_LEGACY:
        _run(_legacy_eng_to_te)
    return list(outs)


def suggestions(word: str, limit: int = 8) -> List[str]:
    """
    Return multiple Telugu suggestions for a single Roman word.
    Ranking: prefer forms with retroflex/Sanskritic signs; then by shorter length.
    """
    seen = set()
    ranked: list[tuple[tuple[int, int], str]] = []

    for r in _roman_variants(word):
        for out in _fanout(r):
            if out in seen:
                continue
            seen.add(out)
            bonus = 0
            if any(ch in out for ch in "ళఋృషఠఢ"):
                bonus -= 1  # slight preference
            ranked.append(((bonus, len(out)), out))

    ranked.sort(key=lambda x: x[0])
    return [o for _, o in ranked][:limit]