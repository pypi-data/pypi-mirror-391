"""
combo_pipeline.py

Implement the flowcharts: take input (English or Romanized-Telugu; word or sentence),
get raw transliteration/translation, split into words/letters, gather candidate Telugu
matches for each letter and for each word, combine into word/sentence variants and
calculate combination counts.

Depends on:
- transliterator.eng_to_telugu
- suggest.suggestions
- suggest_sentence.per_token_suggestions (optional)
- pipeline.translate (optional)
"""

from __future__ import annotations
from typing import List, Dict, Tuple, Iterable
import itertools
import re

# Try local imports (adjust if package layout differs)
try:
    from .transliterator import eng_to_telugu
except Exception:
    # fallback if running at top-level
    from transliterator import eng_to_telugu

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

# --- HARD FILTER HELPERS (paste once) ---
# Config (tune as needed)
HARD_WHITELIST = {"రా", "జు", "నే", "నా", "రాజు", "నమస్కారం", "ప్రసాదం"}
HARD_WHITELIST.update({"నేను", "నువ్వు", "వారు", "మా", "మీ", "అతను", "ఆమె", "దేవుడు"})
HARD_MIN_LENGTH = 1
HARD_MAX_LENGTH = 48

TELUGU_ONLY_RE = re.compile(r'^[\u0C00-\u0C7F\s]+$')
ROMAN_RE = re.compile(r'[A-Za-z]')
VOWEL_RUN_RE = re.compile(r'[అఆఇఈఉఊఎఏఐఒఓఔ]{3,}')
# increase threshold so normal words aren't accidentally rejected
ALT_CV_RE = re.compile(r'(?:[కఖగఘఙచఛజఝఞటఠడఢణతథదధనపఫబభమయరలవశషసహ][అఆఇఈఉఊఎఏఐఒఓఔ]){6,}')
ALT_VC_RE = re.compile(r'(?:[అఆఇఈఉఊఎఏఐఒఓఔ][కఖగఘఙచఛజఝఞటఠడఢణతథదధనపఫబభమయరలవశషసహ]){6,}')

def hard_filter_single_candidate(s: str) -> bool:
    """Return True iff candidate s is accepted (not junk)."""
    if not s or not isinstance(s, str):
        return False
    s = s.strip()
    if s in HARD_WHITELIST:
        return True
    if len(s) < HARD_MIN_LENGTH or len(s) > HARD_MAX_LENGTH:
        return False
    # Reject mixed-script (contains both Latin letters and Telugu glyphs)
    if ROMAN_RE.search(s) and re.search(r'[\u0C00-\u0C7F]', s):
        return False

    # Require Telugu-only for primary candidates
    if not TELUGU_ONLY_RE.fullmatch(s):
        return False
    # Reject vowel runs or alternating vowel/consonant sequences
    if VOWEL_RUN_RE.search(s):
        return False
    if ALT_CV_RE.search(s) or ALT_VC_RE.search(s):
        return False
    # Passed basic checks
    return True

def hard_filter_candidates(cands: Iterable[str]) -> List[str]:
    """Filter an iterable of candidates and return list preserving order."""
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

def hard_filter_sentence_variant(variant: str, min_word_pass_ratio: float = 0.7) -> bool:
    """
    Accept a sentence variant if it contains Telugu and at least
    `min_word_pass_ratio` fraction of its words individually pass the hard filter.
    This prevents rejecting sentences that include occasional valid short tokens.
    """
    if not variant or not isinstance(variant, str):
        return False
    # require at least one Telugu glyph
    if not re.search(r'[\u0C00-\u0C7F]', variant):
        return False
    words = [w for w in variant.split() if w]
    if not words:
        return False
    pass_count = 0
    for w in words:
        if hard_filter_single_candidate(w):
            pass_count += 1
    ratio = pass_count / len(words)
    return ratio >= min_word_pass_ratio
# --- end helpers ---

# prefer trie-based tokenization when available
try:
    from .transliterator import build_trie, TransliterationTrie, eng_to_telugu as _eng_to_telugu
    _TRIE = build_trie() if callable(build_trie) else None
except Exception:
    _TRIE = None
    _eng_to_telugu = eng_to_telugu

def tokenize_with_trie(text: str) -> List[str]:
    if not text:
        return []
    if _TRIE is None:
        return multi_char_tokens(text)
    toks = []
    i = 0; n = len(text)
    while i < n:
        out, L, is_cluster, cluster_tokens = _TRIE.find_longest_match(text, i)
        if L and L > 0:
            toks.append(text[i:i+L]); i += L
        else:
            toks.append(text[i]); i += 1
    return toks


# -------------------------
# Utilities
# -------------------------
def normalize_input(text: str) -> str:
    """Basic normalization (trim + collapse spaces)."""
    if text is None:
        return ""
    return re.sub(r"\s+", " ", text.strip())


def split_to_words(text: str) -> List[str]:
    """Split on whitespace; keep punctuation tokens intact (simple heuristic)."""
    text = normalize_input(text)
    if not text:
        return []
    return text.split(" ")


def split_word_to_letters(word: str) -> List[str]:
    """
    Naive split into characters for Roman input.
    NOTE: this is a simple character split — if you want orthographic units
    (e.g., 'ch', 'sh', 'aa') you can pre-tokenize or use transliterator trie.
    For flowchart parity we keep single-character decomposition but preserve
    an option to use heuristic multi-char units below.
    """
    return list(word)


def multi_char_tokens(word: str, max_len: int = 3) -> List[str]:
    """
    Produce a simple greedy tokenization of word into multi-char tokens (max_len).
    This helps when letters like 'ch', 'sh', 'th', 'aa' should be grouped.
    Greedy left-to-right longest-match of ASCII sequences (not based on trie).
    """
    i = 0
    toks = []
    while i < len(word):
        taken = None
        for L in range(min(max_len, len(word)-i), 0, -1):
            cand = word[i:i+L]
            # treat vowel doubles as single tokens (aa, ii, uu, ee, oo)
            if re.fullmatch(r"(aa|ii|uu|ee|oo|ai|au|kh|gh|chh|sh|th|dh|ph|bh|ng|ny|rr|LL|RR|TT|DD|Sh|Shh|shh)", cand, flags=re.IGNORECASE):
                taken = cand
                break
            # common digraphs
            if cand.lower() in {"kh","gh","ch","jh","th","dh","sh","ph","bh","ng","ny","ai","au","aa","ee","ii","oo","uu","ri","rii","rr"}:
                taken = cand
                break
        if taken is None:
            # default to single char
            taken = word[i]
        toks.append(taken)
        i += len(taken)
    return toks


# -------------------------
# Match gathering
# -------------------------
def get_word_level_suggestions(word: str, limit: int = 8) -> List[str]:
    """
    High-quality word-level suggestions (IME-like).
    Uses suggest.suggestions which runs multiple transliterator variants and roman variants.
    """
    try:
        outs = suggest_word_candidates(word, limit=limit)
        if outs:
            return outs
    except Exception:
        pass

    # Fallback: direct transliterator single output
    try:
        return [eng_to_telugu(word)]
    except Exception:
        return [word]


def get_letter_level_matches(letter_token: str, max_per_letter: int = 3) -> List[str]:
    """
    For a given Roman token (single char or multi-char unit), return plausible Telugu glyphs.
    Heuristic approach:
      - Try transliterating the token alone
      - Try transliterating token + 'a' (to capture inherent vowel)
      - Try suggestions() on the token
      - Deduplicate and return
    """
    outs = []
    tried = set()
    # try canonical transliteration first
    try:
        t = eng_to_telugu(letter_token)
        if t and t not in tried:
            outs.append(t); tried.add(t)
    except Exception:
        pass
    try:
        t2 = eng_to_telugu(letter_token + "a")
        if t2 and t2 not in tried:
            outs.append(t2); tried.add(t2)
    except Exception:
        pass

    # suggestions fallback
    try:
        for s in suggest_word_candidates(letter_token, limit=6):
            if s not in tried:
                outs.append(s); tried.add(s)
                if len(outs) >= max_per_letter:
                    break
    except Exception:
        pass

    if not outs:
        outs = [letter_token]
    return outs[:max_per_letter]


# -------------------------
# Combination helpers
# -------------------------
def combine_letter_matches_to_words(letter_matches: List[List[str]], cap: int = 2000) -> List[str]:
    """
    Combine letter-level matches (cartesian product) into word variants.
    cap: safety limit on number of combinations returned. If exceeded, we return
         the top lexicographically-first results up to cap.
    """
    # count combos
    total = 1
    for lst in letter_matches:
        total *= max(1, len(lst))

    if total > cap:
        # beam: keep top-K partials; heuristic: prefer parts that contain Telugu glyphs
        K = min(cap, 400)
        beams = [("", 0)]
        for lst in letter_matches:
            next_beams = []
            for partial, _ in beams:
                for choice in lst:
                    candidate = partial + choice
                    # score: prefer parts that contain Telugu glyphs
                    score = 0 if re.search(r'[\u0C00-\u0C7F]', candidate) else 1
                    score = (score, len(candidate))
                    next_beams.append((candidate, score))
            # keep best K deterministic
            next_beams.sort(key=lambda x: x[1])
            beams = next_beams[:K]
        results = [s for s, _ in beams]
        filtered_results = hard_filter_candidates(results)
        if not filtered_results:
            fallback = ["".join(lst[0] for lst in letter_matches if lst)]
            return fallback[:cap]
        return filtered_results[:cap]

    # existing code builds 'results' (list of candidate strings)
    # just before return, apply hard filter:
    results = ["".join(prod) for prod in itertools.product(*letter_matches)]
    filtered_results = hard_filter_candidates(results)
    # if filter removed everything, fall back to deterministic join-first N results (avoid empty)
    if not filtered_results:
        # return some conservative deterministic options built from first options per letter
        fallback = ["".join(lst[0] for lst in letter_matches if lst)]
        return fallback[:cap]
    return filtered_results[:cap]


def combine_word_level_candidates(word_candidates_per_word: List[List[str]], topn: int = 50) -> List[str]:
    """
    Combine word-level candidates across words into sentence variants using beam-like truncated product.
    """
    # naive Cartesian product but truncated
    # estimate total combos
    prod_counts = 1
    for c in word_candidates_per_word:
        prod_counts *= max(1, len(c))

    if prod_counts <= topn:
        results = [" ".join(prod) for prod in itertools.product(*word_candidates_per_word)]
        # Apply hard filter to sentence variants
        filtered_results = [s for s in results if hard_filter_sentence_variant(s, min_word_pass_ratio=0.5)]
        # fallback: if none left, keep original top-N variants
        if not filtered_results:
            filtered_results = results[:topn]
        return filtered_results

    # truncated beam: at each step keep up to K best by simple length heuristic
    beams = [("", 0)]
    K = topn
    for cands in word_candidates_per_word:
        next_beams = []
        for sent, score in beams:
            for w in cands:
                new_sent = (sent + " " + w).strip()
                # score: shorter total length preferred (arbitrary heuristic)
                next_beams.append((new_sent, len(new_sent)))
        next_beams.sort(key=lambda x: x[1])
        beams = next_beams[:K]
    results = [s for s, _ in beams]
    
    # Apply hard filter to sentence variants
    filtered_results = [s for s in results if hard_filter_sentence_variant(s, min_word_pass_ratio=0.5)]
    # fallback: if none left, keep original results
    if not filtered_results:
        filtered_results = results[:topn]
    return filtered_results


# -------------------------
# Primary pipeline functions (map to flowchart blocks)
# -------------------------
def process_english_words_input(word: str, letter_tokenize: bool = True, per_word_limit: int = 8) -> Dict:
    """
    Flowchart path: English Words -> Input: English Word -> Get Raw Translation -> Break into components
                   -> Split to individual letters -> Get Telugu character matches for each letter
                   -> Combine All Telugu matches -> Calculate Number of Combinations -> Show results + count
    Returns a dict:
      {
        "input": original word,
        "raw": raw_transliteration,
        "letters": [list of letter tokens],
        "letter_matches": [[telugu options per letter]],
        "combined_word_variants": [ ... ],
        "combination_count": int
      }
    """
    word = normalize_input(word)
    raw = eng_to_telugu(word) if word else ""

    # tokenization at letter/grapheme-level
    if letter_tokenize:
        tokens = tokenize_with_trie(word) if _TRIE else multi_char_tokens(word)
    else:
        tokens = split_word_to_letters(word)

    letter_matches = [get_letter_level_matches(tok, max_per_letter=3) for tok in tokens]
    combined = combine_letter_matches_to_words(letter_matches)
    # if none left, keep canonical raw transliteration as fallback
    if not combined:
        combined = [raw] if raw else [letter_matches[0][0]] if letter_matches and letter_matches[0] else []
    combo_count = len(combined)

    return {
        "input": word,
        "raw": raw,
        "letters": tokens,
        "letter_matches": letter_matches,
        "combined_word_variants": combined,
        "combination_count": combo_count,
    }


def process_english_sentence_input(sentence: str, per_word_limit: int = 6, beam: int = 6) -> Dict:
    """
    Flowchart path: English Sentences -> Input -> Get Raw Translation -> Break into words -> For each word: split to letters,
    get per-letter matches and combine per-word -> combine words into Telugu sentence variants -> calculate total combos.
    Returns dictionary with detailed data.
    """
    sentence = normalize_input(sentence)
    # Decide: use high-level translator if it seems like a grammatical sentence
    raw_translation = ""
    if high_level_translate:
        try:
            raw_translation = high_level_translate(sentence)
        except Exception:
            raw_translation = eng_to_telugu(sentence)
    else:
        raw_translation = eng_to_telugu(sentence)

    words = split_to_words(sentence)
    per_word_results = []
    total_combinations = 1

    for w in words:
        res = process_english_words_input(w, letter_tokenize=True, per_word_limit=per_word_limit)
        per_word_results.append(res)
        total_combinations *= res["combination_count"] if res["combination_count"] > 0 else 1

    # Combine per-word candidates (use word-suggestions if available to get IME-like words)
    word_level_candidates = []
    for i, w in enumerate(words):
        # prefer suggestions (word-level) as candidates; fallback to combined letter variants
        wl = get_word_level_suggestions(w, limit=per_word_limit)
        # apply hard filter to per-word candidates
        wl_filtered = hard_filter_candidates(wl)
        # fallback to the original wl (or raw transliteration) if filter removed all
        if not wl_filtered:
            # choose safe fallback: raw transliteration for that word or first few combos
            wl_filtered = wl if wl else [per_word_results[i]["raw"]]
        # replace the candidate list
        word_level_candidates.append(wl_filtered)

    sentence_variants_list = combine_word_level_candidates(word_level_candidates, topn=beam)
    # Apply hard filter on final sentence variants
    sentence_variants_filtered = [s for s in sentence_variants_list if hard_filter_sentence_variant(s, min_word_pass_ratio=0.5)]
    # fallback: if none left, keep original top-N variants or use raw_translation
    if not sentence_variants_filtered:
        sentence_variants_filtered = sentence_variants_list[:beam] if sentence_variants_list else ([raw_translation] if raw_translation else [])
    sentence_variants_list = sentence_variants_filtered

    return {
        "input": sentence,
        "raw_translation": raw_translation,
        "words": words,
        "per_word_results": per_word_results,
        "word_level_candidates": word_level_candidates,
        "sentence_variants": sentence_variants_list,
        "total_combination_count": total_combinations
    }


def process_telugu_word_in_english_script(word: str, letter_tokenize: bool = True, per_word_limit: int = 8) -> Dict:
    """
    Flowchart path for 'Telugu Words in English' (Roman-script Telugu):
    - Input: roman-ized Telugu (e.g., 'namaste')
    - Get raw translation meaning in Telugu (i.e., transliteration to Telugu script)
    - Break into components & letters
    - Get Telugu character matches for each letter (this is often 1:1 for romanized Telugu)
    """
    # For roman-telugu, the transliterator should already map tokens more accurately
    raw = eng_to_telugu(word)
    # tokenization should use trie-based tokens because romanized telugu often uses digraphs
    tokens = tokenize_with_trie(word) if letter_tokenize else split_word_to_letters(word)
    letter_matches = [get_letter_level_matches(tok, max_per_letter=3) for tok in tokens]
    combined = combine_letter_matches_to_words(letter_matches)
    # if none left, keep canonical raw transliteration as fallback
    if not combined:
        combined = [raw] if raw else [letter_matches[0][0]] if letter_matches and letter_matches[0] else []
    combo_count = len(combined)

    return {
        "input": word,
        "raw": raw,
        "letters": tokens,
        "letter_matches": letter_matches,
        "combined_word_variants": combined,
        "combination_count": combo_count
    }


def process_telugu_sentence_in_english_script(sentence: str, per_word_limit: int = 6, beam: int = 6) -> Dict:
    """
    Flowchart path: Telugu sentences in English script -> Input -> Get Raw Translation Meaning in Telugu
    -> Break sentence into words -> For each word split to letters -> Get Telugu character matches -> Combine -> Count
    """
    sentence = normalize_input(sentence)
    raw = eng_to_telugu(sentence)
    words = split_to_words(sentence)

    per_word_results = []
    total_combinations = 1
    word_level_candidates = []

    for i, w in enumerate(words):
        r = process_telugu_word_in_english_script(w, letter_tokenize=True, per_word_limit=per_word_limit)
        per_word_results.append(r)
        total_combinations *= r["combination_count"] if r["combination_count"] > 0 else 1
        # for roman-telugu, direct transliteration often suffices as candidate
        wl = [r["raw"]] if r["raw"] else r["combined_word_variants"][:per_word_limit]
        # apply hard filter to per-word candidates
        wl_filtered = hard_filter_candidates(wl)
        # fallback to the original wl (or raw transliteration) if filter removed all
        if not wl_filtered:
            # choose safe fallback: raw transliteration for that word
            wl_filtered = wl if wl else [r["raw"]]
        # replace the candidate list
        word_level_candidates.append(wl_filtered)

    sentence_variants_list = combine_word_level_candidates(word_level_candidates, topn=beam)
    # Apply hard filter on final sentence variants
    sentence_variants_filtered = [s for s in sentence_variants_list if hard_filter_sentence_variant(s, min_word_pass_ratio=0.5)]
    # fallback: if none left, keep original top-N variants or use raw_translation
    if not sentence_variants_filtered:
        sentence_variants_filtered = sentence_variants_list[:beam] if sentence_variants_list else ([raw] if raw else [])
    sentence_variants_list = sentence_variants_filtered

    return {
        "input": sentence,
        "raw_translation": raw,
        "words": words,
        "per_word_results": per_word_results,
        "word_level_candidates": word_level_candidates,
        "sentence_variants": sentence_variants_list,
        "total_combination_count": total_combinations
    }


# -------------------------
# Simple CLI helper if run as script
# -------------------------
def _demo_run():
    import argparse
    p = argparse.ArgumentParser(prog="combo_pipeline", description="Run the transliteration/transformation pipeline (flowchart)")
    p.add_argument("mode", choices=["eng_word","eng_sentence","tel_word","tel_sentence"], help="Which flow to run")
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

    # Pretty print summary
    print("INPUT:", out.get("input"))
    if "raw_translation" in out:
        print("RAW TRANSLATION:", out["raw_translation"])
    elif "raw" in out:
        print("RAW:", out["raw"])
    print("COMBINATION COUNT:", out.get("total_combination_count", out.get("combination_count", 0)))
    if "sentence_variants" in out:
        print("\nSENTENCE VARIANTS (top):")
        for i, s in enumerate(out["sentence_variants"][:10], 1):
            print(f"{i}. {s}")
    if "combined_word_variants" in out and len(out["combined_word_variants"]) > 0:
        print("\nSOME WORD VARIANTS (sample):")
        for v in out["combined_word_variants"][:10]:
            print(" -", v)


if __name__ == "__main__":
    _demo_run()