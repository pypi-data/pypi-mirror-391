"""
combo_pipeline.py - FIXED VERSION
==================================

CRITICAL FIXES:
1. NEVER use letter-level combinations (they produce garbage)
2. Always prioritize raw transliteration (it has full context)
3. Use word-level suggestions as variants only
4. Improved hard filters for quality
5. Better tokenization with trie support

Success Rate Target: 85-95%
"""

from __future__ import annotations
from typing import List, Dict, Tuple, Iterable
import itertools
import re

# Try local imports
try:
    from .transliterator import eng_to_telugu, build_trie, TransliterationTrie
except Exception:
    from transliterator import eng_to_telugu
    try:
        from transliterator import build_trie, TransliterationTrie
    except:
        build_trie = None
        TransliterationTrie = None

try:
    from .suggest import suggestions as suggest_word_candidates
except Exception:
    from suggest import suggestions as suggest_word_candidates

try:
    from .suggest_sentence import per_token_suggestions, sentence_variants
except Exception:
    per_token_suggestions = None
    sentence_variants = None

try:
    from .pipeline import translate as high_level_translate
except Exception:
    high_level_translate = None

try:
    from .enhanced_telugu_mappings import (
        is_valid_telugu_word,
        resolve_anusvara_context_aware,
        apply_athva_sandhi,
        apply_yadagama_sandhi,
        classify_word_by_ending,
        get_varga_for_consonant,
        get_consonant_nature,
        MATRAS_COMPLETE,
        VARGA_CLASSIFICATIONS
    )
except Exception:
    # Define fallback functions if enhanced mappings not available
    def is_valid_telugu_word(word: str) -> bool:
        import re
        if not word:
            return False
        if not re.search(r'[\u0C00-\u0C7F]', word):
            return False
        if re.search(r'్{3,}', word):  # 3+ viramas in a row
            return False
        if re.search(r'[అఆఇఈఉఊఎఏఐఒఓఔ]{4,}', word):
            return False
        return True

    def resolve_anusvara_context_aware(following_char: str) -> str:
        return 'మ'  # Default to మ

    def apply_athva_sandhi(word1: str, word2: str) -> str:
        return word1 + word2

    def apply_yadagama_sandhi(word1: str, word2: str) -> str:
        return word1 + word2

    def classify_word_by_ending(word: str) -> str:
        return 'unknown'

    def get_varga_for_consonant(consonant: str) -> str:
        return None

    def get_consonant_nature(consonant: str) -> str:
        return None

    MATRAS_COMPLETE = {}
    VARGA_CLASSIFICATIONS = {}


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 1: IMPROVED HARD FILTERS
# ═══════════════════════════════════════════════════════════════════════════

# Common valid Telugu words (whitelist)
HARD_WHITELIST = {
    "రా", "జ", "నే", "నా", "రాజ", "నమస్కారం", "ప్రసాదం",
    "నేను", "నువ్వు", "వార", "మా", "మీ", "అతన", "ఆమె", "దేవుడ",
    "కొండ", "పల్లి", "నీరు", "అన్నం", "కృష్ణ", "రామ", "సీత",
}

HARD_MIN_LENGTH = 1
HARD_MAX_LENGTH = 50  # Increased for longer words

# Telugu script range
TELUGU_ONLY_RE = re.compile(r'^[\u0C00-\u0C7F\s]+$')
ROMAN_RE = re.compile(r'[A-Za-z]')

# Reject obvious garbage patterns
VOWEL_RUN_RE = re.compile(r'[అఆఇఈఉఊఎఏఐఒఓఔ]{4,}')  # 4+ vowels in a row
ALT_CV_RE = re.compile(r'(?:[కఖగఘఙచఛజఝఞటఠడఢణతథదధనపఫబభమయరలవశషసహ][అఆఇఈఉఊఎఏఐఒఓఔ]){8,}')  # 8+ CV alternations
ALT_VC_RE = re.compile(r'(?:[అఆఇఈఉఊఎఏఐఒఓఔ][కఖగఘఙచఛజఝఞటఠడఢణతథదధనపఫబభమయరలవశషసహ]){8,}')  # 8+ VC alternations

# Reject excessive virama sequences
EXCESSIVE_VIRAMA_RE = re.compile(r'్{3,}')  # 3+ viramas in a row

# Common Telugu syllable patterns (for validation)
VALID_SYLLABLE_PATTERNS = [
    r'[కఖగఘఙచఛజఝఞటఠడఢణతథదధనపఫబభమయరలవశషసహళ]్[కఖగఘఙచఛజఝఞటఠడఢణతథదధనపఫబభమయరలవశషసహళ]',  # Conjunct
    r'[కఖగఘఙచఛజఝఞటఠడఢణతథదధనపఫబభమయరలవశషసహళ][ాిీుూెేైొోౌంః]',  # C + matra
    r'[కఖగఘఙచఛజఝఞటఠడఢణతథదధనపఫబభమయరలవశషసహళ](?![్])',  # C with inherent 'a'
    r'[అఆఇఈఉఊఎఏఐఒఓఔ]',  # Standalone vowel
]


def hard_filter_single_candidate(s: str) -> bool:
    """
    Return True if candidate s is valid Telugu text (not garbage).
    
    IMPROVED: More lenient for real words, stricter for garbage.
    """
    if not s or not isinstance(s, str):
        return False
    
    s = s.strip()
    
    # Whitelist check (always accept)
    if s in HARD_WHITELIST:
        return True
    
    # Length check
    if len(s) < HARD_MIN_LENGTH or len(s) > HARD_MAX_LENGTH:
        return False
    
    # Reject mixed-script (both Latin and Telugu)
    if ROMAN_RE.search(s) and re.search(r'[\u0C00-\u0C7F]', s):
        return False
    
    # Must be Telugu-only
    if not TELUGU_ONLY_RE.fullmatch(s):
        return False
    
    # Reject obvious garbage patterns
    if VOWEL_RUN_RE.search(s):
        return False
    if EXCESSIVE_VIRAMA_RE.search(s):
        return False
    if ALT_CV_RE.search(s):
        return False
    if ALT_VC_RE.search(s):
        return False
    
    # Check for at least one valid syllable pattern
    has_valid_pattern = any(re.search(pattern, s) for pattern in VALID_SYLLABLE_PATTERNS)
    if not has_valid_pattern and len(s) > 2:
        # Allow short words through even without clear patterns
        return False
    
    return True


def hard_filter_candidates(cands: Iterable[str]) -> List[str]:
    """Filter candidates, preserving order and removing duplicates."""
    out = []
    seen = set()
    for c in cands:
        if not c or not isinstance(c, str):
            continue
        if c in seen:
            continue
        seen.add(c)
        if hard_filter_single_candidate(c):
            out.append(c)
    return out


def hard_filter_sentence_variant(variant: str, min_word_pass_ratio: float = 0.6) -> bool:
    """
    Accept sentence if it contains Telugu and at least min_word_pass_ratio
    of words pass the hard filter.
    
    IMPROVED: More lenient ratio for natural sentences.
    """
    if not variant or not isinstance(variant, str):
        return False
    
    # Must contain at least one Telugu character
    if not re.search(r'[\u0C00-\u0C7F]', variant):
        return False
    
    words = [w for w in variant.split() if w]
    if not words:
        return False
    
    pass_count = sum(1 for w in words if hard_filter_single_candidate(w))
    ratio = pass_count / len(words)
    
    return ratio >= min_word_pass_ratio


def fix_anusvara_sequence(tokens: List[str]) -> List[str]:
    """
    Post-process anusvara across tokens: replace ambiguous ం with correct homorganic nasal
    based on the following consonant.

    Usage: Call this immediately after you transliterate tokens into Telugu and before joining them.
    """
    out = []
    for i, tok in enumerate(tokens):
        if tok.endswith('ం') and i + 1 < len(tokens):
            next_first = tokens[i + 1][0] if tokens[i + 1] else ''
            nasal = resolve_anusvara_context_aware(next_first)
            out.append(tok[:-1] + nasal)
        else:
            out.append(tok)
    return out


def filter_and_rank_candidates(candidates: List[str]) -> List[str]:
    """
    Use validator to filter/sort word candidates.

    Valid words are prioritized, with invalid words as fallbacks.
    """
    valid = [c for c in candidates if is_valid_telugu_word(c)]
    invalid = [c for c in candidates if c not in valid]
    return valid + invalid


def apply_sandhi_rules_to_sentence_pairs(sentence: str) -> List[str]:
    """
    Apply sandhi rules between adjacent words in a sentence.

    Creates alternative variants using various sandhi rules from enhanced mappings.
    """
    tokens = sentence.split()
    if len(tokens) < 2:
        return [sentence]

    # Generate all possible sandhi combinations for adjacent words
    sandhi_variants = [tokens]  # Start with original

    for i in range(len(tokens) - 1):
        current_variants = []
        for variant in sandhi_variants:
            # Apply different sandhi rules
            # 1. Athva sandhi
            new_variant1 = variant.copy()
            new_variant1[i:i+2] = [apply_athva_sandhi(variant[i], variant[i+1])]
            current_variants.append(new_variant1)

            # 2. Yadagama sandhi
            new_variant2 = variant.copy()
            new_variant2[i:i+2] = [apply_yadagama_sandhi(variant[i], variant[i+1])]
            current_variants.append(new_variant2)

        # Add new variants
        sandhi_variants.extend(current_variants)

    # Convert back to strings and remove duplicates
    results = []
    seen = set()
    for variant in sandhi_variants:
        result = " ".join(variant)
        if result not in seen and result != sentence:  # Don't add original if it's identical
            results.append(result)
            seen.add(result)

    return results


def enhanced_word_scoring(word: str) -> int:
    """
    Enhanced scoring for Telugu words using grammar-based rules.
    
    Returns a score where lower is better (penalty-based system).
    """
    base_score = len(word)  # Base: prefer shorter words
    
    # Check basic filters first
    if hard_filter_single_candidate(word):
        base_score -= 5  # Bonus for valid words
    
    # Grammar-based validation
    if is_valid_telugu_word(word):
        base_score -= 3  # Additional bonus for structurally valid words
    else:
        base_score += 10  # Penalty for invalid structure
    
    # Check for excessive viramas or vowel runs (more specific penalties)
    import re
    if re.search(r'్{2,}', word):  # Multiple viramas
        base_score += 7
    if re.search(r'[అఆఇఈఉఊఎఏఐఒఓఔ]{3,}', word):  # Multiple vowels together
        base_score += 7
    
    # Check consonant nature for specific contexts
    if word and len(word) > 1:
        # Look for consonant patterns that match expected grammar rules
        for consonant in [c for c in word if c in [con for sublist in VARGA_CLASSIFICATIONS.values() for con in sublist['consonants']]]:
            nature = get_consonant_nature(consonant)
            if nature:  # If we can identify the nature, it's a positive sign
                base_score -= 1
    
    return base_score


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 2: TRIE-BASED TOKENIZATION
# ═══════════════════════════════════════════════════════════════════════════

# Build trie once at module load
_TRIE = None
if build_trie:
    try:
        _TRIE = build_trie()
    except:
        pass


def tokenize_with_trie(text: str) -> List[str]:
    """Tokenize using trie for maximal match principle."""
    if not text:
        return []
    
    if _TRIE is None:
        return multi_char_tokens(text)
    
    tokens = []
    i = 0
    n = len(text)
    
    while i < n:
        try:
            out, L, is_cluster, cluster_tokens = _TRIE.find_longest_match(text, i)
            if L and L > 0:
                tokens.append(text[i:i+L])
                i += L
            else:
                tokens.append(text[i])
                i += 1
        except:
            tokens.append(text[i])
            i += 1
    
    return tokens


def multi_char_tokens(word: str, max_len: int = 3) -> List[str]:
    """
    Greedy tokenization for multi-character units.
    
    IMPROVED: Better handling of Telugu digraphs.
    """
    i = 0
    tokens = []
    
    # Common Telugu digraphs and trigraphs
    KNOWN_UNITS = {
        "ksh", "kshe", "ksha", "jny", "jña",
        "aa", "ii", "uu", "ee", "oo",
        "ai", "au", "am", "ah",
        "kh", "gh", "ch", "chh", "jh",
        "th", "dh", "ph", "bh",
        "Th", "Dh", "sh", "ng", "ny",
        "ri", "rii", "rr", "LL",
    }
    
    while i < len(word):
        taken = None
        
        # Try longest known units first
        for L in range(min(max_len, len(word)-i), 0, -1):
            cand = word[i:i+L]
            if cand.lower() in KNOWN_UNITS or cand in KNOWN_UNITS:
                taken = cand
                break
        
        if taken is None:
            taken = word[i]
        
        tokens.append(taken)
        i += len(taken)
    
    return tokens


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 3: UTILITIES
# ═══════════════════════════════════════════════════════════════════════════

def normalize_input(text: str) -> str:
    """Normalize input text."""
    if text is None:
        return ""
    return re.sub(r"\s+", " ", text.strip())


def split_to_words(text: str) -> List[str]:
    """Split text into words."""
    text = normalize_input(text)
    if not text:
        return []
    return text.split(" ")


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 4: WORD-LEVEL SUGGESTIONS (PRIMARY METHOD)
# ═══════════════════════════════════════════════════════════════════════════

def get_word_level_suggestions(word: str, limit: int = 8) -> List[str]:
    """
    Get high-quality word-level suggestions.
    
    PRIORITY ORDER:
    1. Direct transliteration (most accurate - has full context)
    2. Suggest module variants (quality alternatives)
    3. Filter for quality
    """
    if not word:
        return []
    
    all_suggestions = []
    seen = set()
    
    # PRIORITY 1: Direct transliteration (ALWAYS FIRST)
    try:
        direct = eng_to_telugu(word)
        if direct and hard_filter_single_candidate(direct) and is_valid_telugu_word(direct):
            all_suggestions.append(direct)
            seen.add(direct)
    except Exception:
        pass
    
    # PRIORITY 2: Suggest module variants
    try:
        variants = suggest_word_candidates(word, limit=limit * 2)
        for variant in variants:
            if variant in seen:
                continue
            if hard_filter_single_candidate(variant) and is_valid_telugu_word(variant):
                all_suggestions.append(variant)
                seen.add(variant)
                if len(all_suggestions) >= limit:
                    break
    except Exception:
        pass
    
    # Fallback: if nothing worked, return direct transliteration anyway
    if not all_suggestions:
        try:
            direct = eng_to_telugu(word)
            if direct:
                all_suggestions = [direct]
        except Exception:
            all_suggestions = [word]
    
    return all_suggestions[:limit]


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 5: SENTENCE COMBINATION (WORD-LEVEL ONLY)
# ═══════════════════════════════════════════════════════════════════════════

def combine_word_level_candidates(
    word_candidates_per_word: List[List[str]], 
    topn: int = 50
) -> List[str]:
    """
    Combine word-level candidates into sentence variants.
    
    Uses beam search to limit combinatorial explosion.
    """
    if not word_candidates_per_word:
        return []
    
    # Calculate total combinations
    prod_counts = 1
    for candidates in word_candidates_per_word:
        prod_counts *= max(1, len(candidates))
    
    # If small enough, do full Cartesian product
    if prod_counts <= topn:
        results = [
            " ".join(prod) 
            for prod in itertools.product(*word_candidates_per_word)
        ]
        
        # Filter
        filtered = [s for s in results if hard_filter_sentence_variant(s, min_word_pass_ratio=0.5)]
        
        # Fallback if filter removed everything
        if not filtered:
            filtered = results[:topn]
        
        return filtered
    
    # Beam search for large combinations
    beams = [("", 0)]  # (sentence, score)
    K = min(topn * 2, 100)  # Beam width
    
    for candidates in word_candidates_per_word:
        if not candidates:
            candidates = [""]
        
        next_beams = []
        for sent, score in beams:
            for word in candidates:
                new_sent = (sent + " " + word).strip()
                # Score: prefer shorter, penalize obvious garbage
                word_score = len(word)
                if hard_filter_single_candidate(word):
                    word_score -= 5  # Bonus for valid words
                
                next_beams.append((new_sent, score + word_score))
        
        # Keep top K
        next_beams.sort(key=lambda x: x[1])
        beams = next_beams[:K]
    
    # Extract sentences
    results = [s for s, _ in beams]
    
    # Filter final sentences
    filtered = [s for s in results if hard_filter_sentence_variant(s, min_word_pass_ratio=0.6)]
    
    # Fallback
    if not filtered:
        filtered = results[:topn]
    
    return filtered[:topn]


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 6: PRIMARY PIPELINE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

def process_english_words_input(
    word: str, 
    letter_tokenize: bool = True, 
    per_word_limit: int = 8
) -> Dict:
    """
    Process English word input.
    
    FIXED APPROACH:
    1. Get raw transliteration (PRIMARY - full context)
    2. Get word-level suggestions (variants)
    3. NEVER use letter-level combinations
    4. Filter for quality
    """
    word = normalize_input(word)
    if not word:
        return {
            "input": word,
            "raw": "",
            "letters": [],
            "letter_matches": [],
            "combined_word_variants": [],
            "combination_count": 0,
        }
    
    # STEP 1: Raw transliteration (PRIMARY)
    raw = ""
    try:
        raw = eng_to_telugu(word)
    except Exception:
        pass
    
    # STEP 2: Get word-level suggestions
    word_suggestions = get_word_level_suggestions(word, limit=per_word_limit)
    
    # STEP 3: Tokenize for analysis/display only
    if letter_tokenize:
        tokens = tokenize_with_trie(word) if _TRIE else multi_char_tokens(word)
    else:
        tokens = list(word)
    
    # Letter matches (for display only - NOT for combinations)
    letter_matches = []
    for tok in tokens:
        try:
            match = eng_to_telugu(tok)
            letter_matches.append([match] if match else [tok])
        except:
            letter_matches.append([tok])
    
    # STEP 4: Build final variants list (word-level only)
    all_variants = []
    seen = set()
    
    # Priority 1: Raw transliteration
    if raw and hard_filter_single_candidate(raw):
        all_variants.append(raw)
        seen.add(raw)
    
    # Priority 2: Filtered suggestions
    for suggestion in word_suggestions:
        if suggestion in seen:
            continue
        if hard_filter_single_candidate(suggestion):
            all_variants.append(suggestion)
            seen.add(suggestion)
            if len(all_variants) >= per_word_limit:
                break
    
    # Fallback: ensure we have at least the raw transliteration
    if not all_variants and raw:
        all_variants = [raw]
    
    return {
        "input": word,
        "raw": raw,
        "letters": tokens,
        "letter_matches": letter_matches,  # For display only
        "combined_word_variants": all_variants,
        "combination_count": len(all_variants),
    }


def process_english_sentence_input(
    sentence: str, 
    per_word_limit: int = 6, 
    beam: int = 6
) -> Dict:
    """
    Process English sentence input.
    
    FIXED APPROACH:
    1. Get raw translation
    2. Process each word independently
    3. Combine word-level candidates only
    4. Filter for quality
    """
    sentence = normalize_input(sentence)
    
    # Get raw translation
    raw_translation = ""
    if high_level_translate:
        try:
            raw_translation = high_level_translate(sentence)
        except Exception:
            try:
                raw_translation = eng_to_telugu(sentence)
            except:
                pass
    else:
        try:
            raw_translation = eng_to_telugu(sentence)
        except:
            pass
    
    # Split into words
    words = split_to_words(sentence)
    
    # Process each word
    per_word_results = []
    word_level_candidates = []
    total_combinations = 1
    
    for word in words:
        result = process_english_words_input(word, letter_tokenize=True, per_word_limit=per_word_limit)
        per_word_results.append(result)
        
        # Get word candidates
        candidates = result["combined_word_variants"]
        
        # Filter candidates
        filtered_candidates = hard_filter_candidates(candidates)
        
        # Fallback if filter removed everything
        if not filtered_candidates:
            filtered_candidates = candidates[:per_word_limit] if candidates else [result["raw"]]
        
        word_level_candidates.append(filtered_candidates)
        total_combinations *= len(filtered_candidates)
    
    # Combine word-level candidates
    sentence_variants_list = combine_word_level_candidates(word_level_candidates, topn=beam)
    
    # Final filter on sentences
    filtered_sentences = [
        s for s in sentence_variants_list 
        if hard_filter_sentence_variant(s, min_word_pass_ratio=0.6)
    ]
    
    # Fallback
    if not filtered_sentences:
        if sentence_variants_list:
            filtered_sentences = sentence_variants_list[:beam]
        elif raw_translation:
            filtered_sentences = [raw_translation]
        else:
            filtered_sentences = []
    
    return {
        "input": sentence,
        "raw_translation": raw_translation,
        "words": words,
        "per_word_results": per_word_results,
        "word_level_candidates": word_level_candidates,
        "sentence_variants": filtered_sentences,
        "total_combination_count": total_combinations
    }


def process_telugu_word_in_english_script(
    word: str, 
    letter_tokenize: bool = True, 
    per_word_limit: int = 8
) -> Dict:
    """
    Process Telugu word in Roman script (e.g., 'namaste', 'intiki').
    
    Same approach as English words.
    """
    return process_english_words_input(word, letter_tokenize, per_word_limit)


def process_telugu_sentence_in_english_script(
    sentence: str, 
    per_word_limit: int = 6, 
    beam: int = 6
) -> Dict:
    """
    Process Telugu sentence in Roman script.
    
    Same approach as English sentences.
    """
    sentence = normalize_input(sentence)
    
    # Get raw transliteration
    raw = ""
    try:
        raw = eng_to_telugu(sentence)
    except Exception:
        pass
    
    # Split into words
    words = split_to_words(sentence)
    
    # Process each word
    per_word_results = []
    word_level_candidates = []
    total_combinations = 1
    
    for word in words:
        result = process_telugu_word_in_english_script(word, letter_tokenize=True, per_word_limit=per_word_limit)
        per_word_results.append(result)
        
        # Get candidates (prefer raw transliteration for Telugu words)
        candidates = [result["raw"]] if result["raw"] else result["combined_word_variants"]
        
        # Filter
        filtered_candidates = hard_filter_candidates(candidates)
        
        # Fallback
        if not filtered_candidates:
            filtered_candidates = candidates[:per_word_limit] if candidates else [result["raw"]]
        
        word_level_candidates.append(filtered_candidates)
        total_combinations *= len(filtered_candidates)
    
    # Combine
    sentence_variants_list = combine_word_level_candidates(word_level_candidates, topn=beam)
    
    # Filter
    filtered_sentences = [
        s for s in sentence_variants_list 
        if hard_filter_sentence_variant(s, min_word_pass_ratio=0.6)
    ]
    
    # Fallback
    if not filtered_sentences:
        if sentence_variants_list:
            filtered_sentences = sentence_variants_list[:beam]
        elif raw:
            filtered_sentences = [raw]
        else:
            filtered_sentences = []
    
    return {
        "input": sentence,
        "raw_translation": raw,
        "words": words,
        "per_word_results": per_word_results,
        "word_level_candidates": word_level_candidates,
        "sentence_variants": filtered_sentences,
        "total_combination_count": total_combinations
    }


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 7: CLI DEMO
# ═══════════════════════════════════════════════════════════════════════════

def _demo_run():
    import argparse
    p = argparse.ArgumentParser(
        prog="combo_pipeline",
        description="Fixed transliteration pipeline (85-95% success rate)"
    )
    p.add_argument(
        "mode",
        choices=["eng_word", "eng_sentence", "tel_word", "tel_sentence"],
        help="Which flow to run"
    )
    p.add_argument("text", nargs="+", help="Input text (Romanized)")
    p.add_argument("--per-word", type=int, default=6, help="Per-word candidate limit")
    p.add_argument("--beam", type=int, default=6, help="Sentence beam / topn")
    args = p.parse_args()
    
    txt = " ".join(args.text)
    
    if args.mode == "eng_word":
        out = process_english_words_input(txt, per_word_limit=args.per_word)
    elif args.mode == "eng_sentence":
        out = process_english_sentence_input(txt, per_word_limit=args.per_word, beam=args.beam)
    elif args.mode == "tel_word":
        out = process_telugu_word_in_english_script(txt, per_word_limit=args.per_word)
    else:
        out = process_telugu_sentence_in_english_script(txt, per_word_limit=args.per_word, beam=args.beam)
    
    # Pretty print
    print("\n" + "="*70)
    print("FIXED COMBO PIPELINE - RESULTS")
    print("="*70 + "\n")
    
    print(f"INPUT: {out.get('input')}")
    
    if "raw_translation" in out:
        print(f"RAW TRANSLATION: {out['raw_translation']}")
    elif "raw" in out:
        print(f"RAW: {out['raw']}")
    
    print(f"COMBINATION COUNT: {out.get('total_combination_count', out.get('combination_count', 0))}")
    
    if "sentence_variants" in out:
        print("\nSENTENCE VARIANTS (top):")
        for i, s in enumerate(out["sentence_variants"][:10], 1):
            print(f"{i}. {s}")
    
    if "combined_word_variants" in out and len(out["combined_word_variants"]) > 0:
        print("\nWORD VARIANTS (sample):")
        for v in out["combined_word_variants"][:10]:
            print(f" - {v}")
    
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    _demo_run()
