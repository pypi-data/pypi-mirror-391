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
    Generate Roman phonetic alternates for Telugu words.
    ENHANCED: More comprehensive variant generation.
    """
    w = (w or "").strip()
    if not w:
        return []

    variants = {w}

    # Vowel length variants (short ↔ long)
    for v in "aeiou":
        variants.add(w.replace(v, v * 2))
        variants.add(w.replace(v * 2, v))

    # Consonant variants
    # Retroflex alternatives
    if "t" in w:
        variants.add(w.replace("t", "T"))  # dental → retroflex
    if "T" in w:
        variants.add(w.replace("T", "t"))  # retroflex → dental
    
    if "d" in w:
        variants.add(w.replace("d", "D"))
    if "D" in w:
        variants.add(w.replace("D", "d"))
    
    if "n" in w:
        variants.add(w.replace("n", "N"))  # dental → retroflex
        # Nasal variants (n → M before certain consonants)
        variants.add(w.replace("n", "M"))
    
    # Sibilant variants
    if "s" in w:
        variants.add(w.replace("s", "S"))  # s → ṣ
        variants.add(w.replace("s", "sh"))  # s → ś
    if "S" in w:
        variants.add(w.replace("S", "s"))
    if "sh" in w:
        variants.add(w.replace("sh", "s"))
        variants.add(w.replace("sh", "S"))
    
    # Palatal variants
    if "ch" in w:
        variants.add(w.replace("ch", "chh"))
        variants.add(w.replace("ch", "c"))
    if "c" in w:
        variants.add(w.replace("c", "ch"))
    
    # Liquid variants
    if "l" in w:
        variants.add(w.replace("l", "L"))  # l → ḷ
    if "L" in w:
        variants.add(w.replace("L", "l"))
    
    # Vocalic r variants
    if "ri" in w:
        variants.add(w.replace("ri", "ru"))
        variants.add(w.replace("ri", "r"))
    
    # Common clusters
    if "nk" in w:
        variants.add(w.replace("nk", "Mk"))  # nasal assimilation
    if "nt" in w:
        variants.add(w.replace("nt", "Mt"))
        variants.add(w.replace("nt", "MT"))  # retroflex variant
    if "nd" in w:
        variants.add(w.replace("nd", "Md"))
        variants.add(w.replace("nd", "MD"))
    if "mp" in w:
        variants.add(w.replace("mp", "Mp"))
    if "mb" in w:
        variants.add(w.replace("mb", "Mb"))
    
    # Return unique, non-empty variants
    return [x for x in variants if x and len(x) >= len(w) - 2]  # avoid too short variants


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