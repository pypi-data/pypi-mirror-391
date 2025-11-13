"""
suggest.py - IMPROVED VERSION
==============================

IMPROVEMENTS:
1. More comprehensive Roman variant generation
2. Better handling of Telugu phonetic patterns
3. Improved ranking algorithm
4. Support for common Telugu words

Target: Generate 10-15 quality variants per word
"""

from __future__ import annotations
from typing import List, Callable, Set

# Load both transliterators
try:
    from .transliterator import eng_to_telugu as _std_eng_to_te
except Exception:
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


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 1: COMPREHENSIVE ROMAN VARIANT GENERATION
# ═══════════════════════════════════════════════════════════════════════════

def _roman_variants(w: str) -> List[str]:
    """
    Generate comprehensive Roman phonetic alternates for Telugu words.
    
    IMPROVED: Covers more Telugu phonetic patterns.
    """
    w = (w or "").strip()
    if not w:
        return []
    
    variants: Set[str] = {w}
    
    # ────────────────────────────────────────────────────────────────────────
    # 1. VOWEL LENGTH VARIANTS (short ↔ long)
    # ────────────────────────────────────────────────────────────────────────
    for vowel in "aeiou":
        # Short → Long
        variants.add(w.replace(vowel, vowel * 2))
        # Long → Short
        variants.add(w.replace(vowel * 2, vowel))
    
    # Special vowel patterns
    if "a" in w:
        variants.add(w.replace("a", "aa"))
        variants.add(w.replace("aa", "a"))
    if "i" in w:
        variants.add(w.replace("i", "ii"))
        variants.add(w.replace("ii", "i"))
    if "u" in w:
        variants.add(w.replace("u", "uu"))
        variants.add(w.replace("uu", "u"))
    if "e" in w:
        variants.add(w.replace("e", "ee"))
        variants.add(w.replace("ee", "e"))
    if "o" in w:
        variants.add(w.replace("o", "oo"))
        variants.add(w.replace("oo", "o"))
    
    # ────────────────────────────────────────────────────────────────────────
    # 2. RETROFLEX vs DENTAL CONSONANTS (critical for Telugu)
    # ────────────────────────────────────────────────────────────────────────
    
    # T/t variants (retroflex ↔ dental)
    if "t" in w:
        variants.add(w.replace("t", "T"))   # dental → retroflex
        variants.add(w.replace("tt", "TT"))  # geminate
    if "T" in w:
        variants.add(w.replace("T", "t"))   # retroflex → dental
        variants.add(w.replace("TT", "tt"))
    
    # D/d variants
    if "d" in w:
        variants.add(w.replace("d", "D"))
        variants.add(w.replace("dd", "DD"))
    if "D" in w:
        variants.add(w.replace("D", "d"))
        variants.add(w.replace("DD", "dd"))
    
    # N/n variants (retroflex ↔ dental nasal)
    if "n" in w:
        variants.add(w.replace("n", "N"))
        variants.add(w.replace("nn", "NN"))
    if "N" in w:
        variants.add(w.replace("N", "n"))
        variants.add(w.replace("NN", "nn"))
    
    # L/l variants (retroflex lateral)
    if "l" in w:
        variants.add(w.replace("l", "L"))
        variants.add(w.replace("ll", "LL"))
    if "L" in w:
        variants.add(w.replace("L", "l"))
        variants.add(w.replace("LL", "ll"))
    
    # ────────────────────────────────────────────────────────────────────────
    # 3. SIBILANT VARIANTS (s, sh, S)
    # ────────────────────────────────────────────────────────────────────────
    
    if "s" in w:
        variants.add(w.replace("s", "S"))   # s → ṣ (retroflex)
        variants.add(w.replace("s", "sh"))  # s → ś (palatal)
    if "S" in w:
        variants.add(w.replace("S", "s"))
        variants.add(w.replace("S", "sh"))
    if "sh" in w:
        variants.add(w.replace("sh", "s"))
        variants.add(w.replace("sh", "S"))
    
    # ────────────────────────────────────────────────────────────────────────
    # 4. PALATAL VARIANTS (c, ch)
    # ────────────────────────────────────────────────────────────────────────
    
    if "ch" in w:
        variants.add(w.replace("ch", "chh"))  # aspirated
        variants.add(w.replace("ch", "c"))
    if "chh" in w:
        variants.add(w.replace("chh", "ch"))
    if "c" in w and "ch" not in w:
        variants.add(w.replace("c", "ch"))
    
    # ────────────────────────────────────────────────────────────────────────
    # 5. ASPIRATED CONSONANTS (kh, gh, th, dh, ph, bh)
    # ────────────────────────────────────────────────────────────────────────
    
    aspirated_pairs = [
        ("k", "kh"), ("g", "gh"),
        ("t", "th"), ("d", "dh"),
        ("T", "Th"), ("D", "Dh"),
        ("p", "ph"), ("b", "bh"),
    ]
    
    for plain, aspirated in aspirated_pairs:
        if plain in w and aspirated not in w:
            variants.add(w.replace(plain, aspirated))
        if aspirated in w:
            variants.add(w.replace(aspirated, plain))
    
    # ────────────────────────────────────────────────────────────────────────
    # 6. VOCALIC R/L VARIANTS (ri, rii, ru)
    # ────────────────────────────────────────────────────────────────────────
    
    if "ri" in w:
        variants.add(w.replace("ri", "ru"))
        variants.add(w.replace("ri", "r"))
        variants.add(w.replace("ri", "rii"))
    if "rii" in w:
        variants.add(w.replace("rii", "ri"))
        variants.add(w.replace("rii", "ru"))
    if "ru" in w:
        variants.add(w.replace("ru", "ri"))
    
    # ────────────────────────────────────────────────────────────────────────
    # 7. NASAL ASSIMILATION CLUSTERS (common in Telugu)
    # ────────────────────────────────────────────────────────────────────────
    
    nasal_clusters = [
        ("nk", "Nk"), ("ng", "Ng"),
        ("nt", "Nt"), ("nT", "NT"),
        ("nd", "Nd"), ("nD", "ND"),
        ("mp", "Mp"), ("mb", "Mb"),
    ]
    
    for plain, assimilated in nasal_clusters:
        if plain in w:
            variants.add(w.replace(plain, assimilated))
            variants.add(w.replace(plain, plain[0].upper() + plain[1]))
        if assimilated in w:
            variants.add(w.replace(assimilated, plain))
    
    # ────────────────────────────────────────────────────────────────────────
    # 8. SPECIAL CLUSTERS (ksh, jny, etc.)
    # ────────────────────────────────────────────────────────────────────────
    
    special_clusters = [
        ("ksh", "kS", "kSh"),
        ("jny", "jñ", "gny"),
        ("dny", "gny"),
    ]
    
    for cluster_variants in special_clusters:
        for i, c1 in enumerate(cluster_variants):
            if c1 in w:
                for c2 in cluster_variants:
                    if c1 != c2:
                        variants.add(w.replace(c1, c2))
    
    # ────────────────────────────────────────────────────────────────────────
    # 9. COMMON WORD PATTERNS
    # ────────────────────────────────────────────────────────────────────────
    
    # Final 'a' vs no final 'a'
    if w.endswith("a") and len(w) > 2:
        variants.add(w[:-1])
    elif len(w) > 1 and not w.endswith("a"):
        variants.add(w + "a")
    
    # Initial vowel variants
    if w.startswith("a"):
        variants.add(w[1:])
    if not w.startswith("a"):
        variants.add("a" + w)
    
    # ────────────────────────────────────────────────────────────────────────
    # 10. GEMINATE VARIANTS (double consonants)
    # ────────────────────────────────────────────────────────────────────────
    
    consonants = "kgcjtdpbmyrlvs"
    for c in consonants:
        if c * 2 in w:
            variants.add(w.replace(c * 2, c))
        elif c in w:
            variants.add(w.replace(c, c * 2))
    
    # ────────────────────────────────────────────────────────────────────────
    # FILTER: Remove variants that are too different
    # ────────────────────────────────────────────────────────────────────────
    
    # Keep variants within reasonable length range
    min_len = max(1, len(w) - 3)
    max_len = len(w) + 3
    
    filtered_variants = [
        v for v in variants 
        if v and min_len <= len(v) <= max_len
    ]
    
    return filtered_variants


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 2: TRANSLITERATION ENGINE FANOUT
# ═══════════════════════════════════════════════════════════════════════════

def _fanout(roman: str) -> List[str]:
    """
    Run through both transliteration engines and collect unique Telugu outputs.
    """
    outs = set()
    
    def _run(fn: Callable[[str], str]) -> None:
        try:
            result = fn(roman)
            if result:
                outs.add(result)
        except Exception:
            pass
    
    # Run standard transliterator
    _run(_std_eng_to_te)
    
    # Run legacy transliterator if available
    if _HAS_LEGACY:
        _run(_legacy_eng_to_te)
    
    return list(outs)


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 3: RANKING ALGORITHM
# ═══════════════════════════════════════════════════════════════════════════

def _score_telugu_word(word: str) -> tuple:
    """
    Score Telugu word for ranking.
    
    Returns: (priority, length) tuple for sorting
    Lower is better.
    """
    priority = 0
    
    # ────────────────────────────────────────────────────────────────────────
    # PRIORITY 1: Prefer words with Sanskritic/literary features
    # ────────────────────────────────────────────────────────────────────────
    
    # Retroflex consonants (ट, ड, ण, ळ, ష)
    if any(ch in word for ch in "టఠడఢణళష"):
        priority -= 2
    
    # Vocalic r/l (ఋ, ౠ, ఌ, ౡ)
    if any(ch in word for ch in "ఋౠఌౡృౄౢౣ"):
        priority -= 2
    
    # Visarga/Anusvara (ః, ం)
    if any(ch in word for ch in "ఃం"):
        priority -= 1
    
    # ────────────────────────────────────────────────────────────────────────
    # PRIORITY 2: Penalize overly long words
    # ────────────────────────────────────────────────────────────────────────
    
    length_penalty = len(word)
    
    # ────────────────────────────────────────────────────────────────────────
    # PRIORITY 3: Prefer words with proper conjuncts
    # ────────────────────────────────────────────────────────────────────────
    
    # Count virama (్) - indicates conjuncts
    virama_count = word.count("్")
    if virama_count > 0 and virama_count < 4:
        priority -= 1
    
    return (priority, length_penalty)


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 4: PUBLIC API
# ═══════════════════════════════════════════════════════════════════════════

def suggestions(word: str, limit: int = 8) -> List[str]:
    """
    Return multiple Telugu suggestions for a single Roman word.
    
    IMPROVED: Better ranking and more comprehensive variants.
    
    Args:
        word: Romanized Telugu word
        limit: Maximum number of suggestions to return
    
    Returns:
        List of Telugu suggestions, ranked by quality
    """
    if not word:
        return []
    
    seen = set()
    scored_results = []
    
    # Generate Roman variants
    roman_variants = _roman_variants(word)
    
    # Transliterate each variant
    for roman_variant in roman_variants:
        # Run through transliteration engines
        telugu_outputs = _fanout(roman_variant)
        
        for output in telugu_outputs:
            if output in seen:
                continue
            seen.add(output)
            
            # Score the output
            score = _score_telugu_word(output)
            scored_results.append((score, output))
    
    # Sort by score (lower is better)
    scored_results.sort(key=lambda x: x[0])
    
    # Return top N
    return [output for _, output in scored_results[:limit]]


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 5: TESTING
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("="*70)
    print("IMPROVED SUGGEST.PY - TESTING")
    print("="*70 + "\n")
    
    test_words = [
        "krishna",
        "rama",
        "namaste",
        "intiki",
        "pustakam",
        "school",
        "going",
        "reading",
    ]
    
    for word in test_words:
        results = suggestions(word, limit=10)
        print(f"\n{word}:")
        for i, suggestion in enumerate(results, 1):
            print(f"  {i}. {suggestion}")
    
    print("\n" + "="*70)
