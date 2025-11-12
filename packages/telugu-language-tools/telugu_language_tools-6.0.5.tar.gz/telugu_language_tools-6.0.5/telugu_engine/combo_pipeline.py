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
from typing import List, Dict, Tuple
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


def get_letter_level_matches(letter_token: str) -> List[str]:
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

    candidates = [letter_token, letter_token + "a", letter_token + "aa"]
    candidates += [letter_token.lower(), letter_token.upper()]

    for c in candidates:
        try:
            t = eng_to_telugu(c)
            if t and t not in tried:
                outs.append(t)
                tried.add(t)
        except Exception:
            pass

    # also try suggest-based small list for this token
    try:
        for s in suggest_word_candidates(letter_token, limit=6):
            if s not in tried:
                outs.append(s)
                tried.add(s)
    except Exception:
        pass

    # final fallback: the token itself (keeps pipeline robust)
    if not outs:
        outs = [letter_token]

    return outs


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
        # to avoid explosion, we produce deterministic partial combinations:
        # take the first candidate from the first N-1 letters and iterate last
        results = []
        # build iterators that are truncated to small sizes
        truncated = [lst if len(lst) <= 4 else lst[:4] for lst in letter_matches]
        for prod in itertools.islice(itertools.product(*truncated), cap):
            results.append("".join(prod))
        return results

    return ["".join(prod) for prod in itertools.product(*letter_matches)]


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
        return [" ".join(prod) for prod in itertools.product(*word_candidates_per_word)]

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
    return [s for s, _ in beams]


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
        tokens = multi_char_tokens(word)
    else:
        tokens = split_word_to_letters(word)

    letter_matches = [get_letter_level_matches(tok) for tok in tokens]
    combined = combine_letter_matches_to_words(letter_matches)
    combo_count = 1
    for lst in letter_matches:
        combo_count *= max(1, len(lst))

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
    for w in words:
        # prefer suggestions (word-level) as candidates; fallback to combined letter variants
        wl = get_word_level_suggestions(w, limit=per_word_limit)
        if not wl:
            # fall back to letter-based combos (but trim)
            pw = process_english_words_input(w, letter_tokenize=True, per_word_limit=per_word_limit)
            wl = pw["combined_word_variants"][:per_word_limit]
        word_level_candidates.append(wl)

    sentence_variants_list = combine_word_level_candidates(word_level_candidates, topn=beam)

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
    # tokenization should use multi-char tokens because romanized telugu often uses digraphs
    tokens = multi_char_tokens(word)
    letter_matches = [get_letter_level_matches(tok) for tok in tokens]
    combined = combine_letter_matches_to_words(letter_matches)
    combo_count = 1
    for lst in letter_matches:
        combo_count *= max(1, len(lst))

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

    for w in words:
        r = process_telugu_word_in_english_script(w, letter_tokenize=True, per_word_limit=per_word_limit)
        per_word_results.append(r)
        total_combinations *= r["combination_count"] if r["combination_count"] > 0 else 1
        # for roman-telugu, direct transliteration often suffices as candidate
        wl = [r["raw"]] if r["raw"] else r["combined_word_variants"][:per_word_limit]
        word_level_candidates.append(wl)

    sentence_variants_list = combine_word_level_candidates(word_level_candidates, topn=beam)

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