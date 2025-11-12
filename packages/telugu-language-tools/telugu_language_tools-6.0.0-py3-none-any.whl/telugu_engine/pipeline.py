# telugu_engine/pipeline.py
from __future__ import annotations
from typing import Literal
import re

# Transliteration (standard)
try:
    from .transliterator import eng_to_telugu as _std_eng_to_te
except Exception:
    from transliterator import eng_to_telugu as _std_eng_to_te

# Transliteration (legacy)
try:
    from .transliterator_v4_3_0 import eng_to_telugu as _legacy_eng_to_te
    _HAS_LEGACY = True
except Exception:
    try:
        from transliterator_v4_3_0 import eng_to_telugu as _legacy_eng_to_te
        _HAS_LEGACY = True
    except Exception:
        _HAS_LEGACY = False

# Translator (English → Telugu grammar)
try:
    from .enhanced_tense import translate_sentence as _translate_sentence
except Exception:
    from enhanced_tense import translate_sentence as _translate_sentence

from .suggest import suggestions as suggest_word
from .suggest_sentence import sentence_variants as suggest_sentence

def eng_to_telugu(text: str, variant: Literal["standard","legacy"]="standard") -> str:
    fn = _legacy_eng_to_te if (variant == "legacy" and _HAS_LEGACY) else _std_eng_to_te
    return fn(text)

def translate(text: str, transliterator_variant: Literal["standard","legacy"]="standard") -> str:
    # very light English detector; feel free to improve
    if re.search(r"\b(i|you|he|she|it|we|they|am|is|are|will|did|have|go|came|read|eat|to)\b", text.lower()):
        return _translate_sentence(text)
    return eng_to_telugu(text, variant=transliterator_variant)

def suggest_word_variants(word: str, limit: int = 8):
    return suggest_word(word, limit=limit)

def suggest_sentence_variants(text: str, topn: int = 5, per_word: int = 4, beam: int = 6):
    return suggest_sentence(text, topn=topn, per_word=per_word, beam=beam)